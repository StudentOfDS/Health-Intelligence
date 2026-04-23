from __future__ import annotations

import warnings
from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy.stats import chi2_contingency, ttest_ind, zscore
from sklearn.preprocessing import PolynomialFeatures
from statsmodels.stats.diagnostic import het_breuschpagan
from statsmodels.stats.outliers_influence import variance_inflation_factor
from statsmodels.stats.stattools import durbin_watson

SLOW_CHANGING_COLS = ["weight_kg", "body_fat_pct", "heart_rate", "blood_sugar"]
BEHAVIOR_COLS = [
    "calories",
    "protein_g",
    "carbs_g",
    "fats_g",
    "sleep_hours",
    "sleep_quality",
    "steps",
    "exercise_minutes",
    "sedentary_minutes",
    "water_liters",
    "stress_level",
    "alcohol_units",
]
ORDINAL_COLS = {"stress_level", "sleep_quality"}


@dataclass
class ColdStartThresholds:
    descriptive_min_days: int = 3
    inference_min_days: int = 10
    hypothesis_min_days: int = 14
    comparison_min_days: int = 21
    regression_min_days: int = 30
    polynomial_min_days: int = 45


class StatisticalDecisionEngine:
    def __init__(self, thresholds: ColdStartThresholds | None = None) -> None:
        self.thresholds = thresholds or ColdStartThresholds()

    def run_pipeline(self, records: list[dict[str, Any]]) -> dict[str, Any]:
        if not records:
            return {"status": "insufficient_data", "message": "No records available."}

        frame = pd.DataFrame(records).sort_values("log_date")
        frame = self._impute_missing(frame)
        sanitized, anomalies = self._detect_outliers(frame)
        transformed = self._normalize_numeric(sanitized)

        days = len(sanitized)
        stage = self._resolve_stage(days)
        result: dict[str, Any] = {
            "status": "ok",
            "stage": stage,
            "n_days": days,
            "anomaly_count": len(anomalies),
            "anomalies": anomalies[:20],
            "encoding_strategy": self._encoding_plan(sanitized),
            "descriptive": self._descriptive_stats(sanitized),
            "decay": self._decay_weighting_preview(sanitized),
            "bayesian_updates": self._bayesian_updates(sanitized),
        }

        if days >= self.thresholds.inference_min_days:
            result["inference"] = self._inference_summary(sanitized)

        if days >= self.thresholds.hypothesis_min_days:
            result["hypothesis"] = self._hypothesis_tests(sanitized)

        if days >= self.thresholds.comparison_min_days:
            result["comparison"] = self._comparison_tests(sanitized)

        if days >= self.thresholds.regression_min_days:
            result["regression"] = self._regression_suite(transformed)

        if days >= self.thresholds.polynomial_min_days:
            result["polynomial"] = self._polynomial_suite(transformed)

        result["insights"] = self._explainable_insights(result)
        return result

    def _impute_missing(self, df: pd.DataFrame) -> pd.DataFrame:
        out = df.copy()
        out["log_date"] = pd.to_datetime(out["log_date"]) if "log_date" in out.columns else pd.NaT
        for col in [c for c in SLOW_CHANGING_COLS if c in out.columns]:
            out[col] = out[col].ffill()
        for col in [c for c in BEHAVIOR_COLS if c in out.columns]:
            med = out[col].median(skipna=True)
            if pd.notna(med):
                out[col] = out[col].fillna(med)
        for col in [c for c in out.columns if out[c].dtype == "object"]:
            mode = out[col].mode(dropna=True)
            if not mode.empty:
                out[col] = out[col].fillna(mode.iloc[0])
        return out

    def _detect_outliers(self, df: pd.DataFrame) -> tuple[pd.DataFrame, list[dict[str, Any]]]:
        out = df.copy()
        anomalies: list[dict[str, Any]] = []
        numeric_cols = [c for c in out.columns if pd.api.types.is_numeric_dtype(out[c])]

        for col in numeric_cols:
            s = out[col].dropna()
            if len(s) < 8:
                continue
            z_index = pd.Index([])
            if float(s.std(ddof=0)) > 1e-9:
                z = np.abs(zscore(s, nan_policy="omit"))
                z_index = s.index[z > 3]

            q1, q3 = s.quantile([0.25, 0.75])
            iqr = q3 - q1
            iqr_index = pd.Index([])
            if iqr > 0:
                lo, hi = q1 - 1.5 * iqr, q3 + 1.5 * iqr
                iqr_index = s.index[(s < lo) | (s > hi)]

            flagged = z_index.union(iqr_index)
            for idx in flagged:
                anomalies.append({"index": int(idx), "feature": col, "value": float(out.at[idx, col])})
            out.loc[flagged, col] = np.nan

        return out, anomalies

    def _normalize_numeric(self, df: pd.DataFrame) -> pd.DataFrame:
        out = df.copy()
        for col in [c for c in out.columns if pd.api.types.is_numeric_dtype(out[c])]:
            std = out[col].std(ddof=0)
            if pd.notna(std) and std > 0:
                out[col] = (out[col] - out[col].mean()) / std
        return out

    def _resolve_stage(self, row_count: int) -> str:
        if row_count < self.thresholds.inference_min_days:
            return "descriptive"
        if row_count < self.thresholds.hypothesis_min_days:
            return "inference"
        if row_count < self.thresholds.comparison_min_days:
            return "hypothesis"
        if row_count < self.thresholds.regression_min_days:
            return "comparison"
        if row_count < self.thresholds.polynomial_min_days:
            return "regression"
        return "polynomial"

    def _descriptive_stats(self, df: pd.DataFrame) -> dict[str, dict[str, float]]:
        numeric = df.select_dtypes(include=[np.number])
        return {
            col: {
                "mean": float(numeric[col].mean()),
                "median": float(numeric[col].median()),
                "min": float(numeric[col].min()),
                "max": float(numeric[col].max()),
            }
            for col in numeric.columns
        }

    def _decay_weighting_preview(self, df: pd.DataFrame) -> dict[str, float]:
        n = len(df)
        if n == 0:
            return {"window_size": 0, "latest_weight": 0}
        half_life = max(7, n // 4)
        weights = np.exp(np.log(0.5) * np.arange(n - 1, -1, -1) / half_life)
        weights = weights / weights.sum()
        return {"window_size": float(min(30, n)), "latest_weight": float(weights[-1]), "oldest_weight": float(weights[0])}

    def _bayesian_updates(self, df: pd.DataFrame) -> dict[str, float]:
        if "calories" not in df.columns:
            return {}
        s = df["calories"].dropna()
        if len(s) == 0:
            return {}
        prior_mean, prior_var = 2200.0, 400.0**2
        obs_var = float(np.var(s) if np.var(s) > 1 else 200.0**2)
        n = len(s)
        posterior_var = 1 / ((1 / prior_var) + (n / obs_var))
        posterior_mean = posterior_var * ((prior_mean / prior_var) + (n * float(s.mean()) / obs_var))
        return {"calories_posterior_mean": float(posterior_mean), "calories_posterior_sd": float(np.sqrt(posterior_var))}

    def _inference_summary(self, df: pd.DataFrame) -> dict[str, dict[str, float]]:
        numeric = df.select_dtypes(include=[np.number])
        response = {}
        for col in [c for c in ["calories", "sleep_hours", "weight_kg", "steps"] if c in numeric.columns]:
            s = numeric[col].dropna()
            if len(s) < 2:
                continue
            mean = s.mean()
            se = s.std(ddof=1) / np.sqrt(len(s)) if s.std(ddof=1) > 0 else 0
            response[col] = {"mean": float(mean), "ci95_low": float(mean - 1.96 * se), "ci95_high": float(mean + 1.96 * se)}
        return response

    def _hypothesis_tests(self, df: pd.DataFrame) -> dict[str, Any]:
        out: dict[str, Any] = {}
        if {"diet_type", "weight_kg"}.issubset(df.columns):
            groups = [g["weight_kg"].dropna().values for _, g in df.groupby("diet_type") if len(g) >= 3]
            if len(groups) >= 2:
                t_stat, p_val = ttest_ind(groups[0], groups[1], equal_var=False)
                out["diet_weight_ttest"] = {
                    "t_stat": float(t_stat),
                    "p_value": float(p_val),
                    "decision": "reject_h0" if p_val < 0.05 else "fail_to_reject_h0",
                }
        return out

    def _comparison_tests(self, df: pd.DataFrame) -> dict[str, Any]:
        out: dict[str, Any] = {}
        if {"diet_type", "stress_level"}.issubset(df.columns):
            tbl = pd.crosstab(df["diet_type"], df["stress_level"])
            if tbl.shape[0] > 1 and tbl.shape[1] > 1:
                chi2, p_val, _, _ = chi2_contingency(tbl)
                out["diet_stress_chi_square"] = {
                    "chi2": float(chi2),
                    "p_value": float(p_val),
                    "decision": "associated" if p_val < 0.05 else "not_associated",
                }
        return out

    def _weighted_regression(self, data: pd.DataFrame) -> dict[str, Any]:
        n = len(data)
        half_life = max(7, n // 4)
        w = np.exp(np.log(0.5) * np.arange(n - 1, -1, -1) / half_life)
        y = data["weight_kg"]
        X = sm.add_constant(data[["calories", "sleep_hours", "steps"]])
        model = sm.WLS(y, X, weights=w).fit()
        return {"weighted_r_squared": float(model.rsquared), "weighted_coefficients": {k: float(v) for k, v in model.params.to_dict().items()}}

    def _regression_suite(self, df: pd.DataFrame) -> dict[str, Any]:
        needed = ["calories", "sleep_hours", "steps", "weight_kg"]
        if not set(needed).issubset(df.columns):
            return {"message": "Required variables unavailable for regression."}
        data = df[needed].dropna()
        if len(data) < 20:
            return {"message": "Not enough complete rows for regression diagnostics."}

        y = data["weight_kg"]
        X = sm.add_constant(data[["calories", "sleep_hours", "steps"]])
        model = sm.OLS(y, X).fit()

        vif = {}
        for i in range(1, X.shape[1]):
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", RuntimeWarning)
                raw_vif = float(variance_inflation_factor(X.values, i))
            vif[X.columns[i]] = raw_vif if np.isfinite(raw_vif) else 999.0

        _, bp_p, _, _ = het_breuschpagan(model.resid, X)
        dw = durbin_watson(model.resid)

        result = {
            "r_squared": float(model.rsquared),
            "adj_r_squared": float(model.rsquared_adj),
            "coefficients": {k: float(v) for k, v in model.params.to_dict().items()},
            "p_values": {k: float(v) for k, v in model.pvalues.to_dict().items()},
            "vif": vif,
            "diagnostics": {
                "heteroscedasticity_bp_p": float(bp_p),
                "autocorrelation_dw": float(dw),
                "multicollinearity_warning": any(v > 5 for v in vif.values()),
            },
        }
        result["weighted"] = self._weighted_regression(data)
        return result

    def _polynomial_suite(self, df: pd.DataFrame) -> dict[str, Any]:
        needed = ["calories", "sleep_hours", "steps", "weight_kg"]
        data = df[[c for c in needed if c in df.columns]].dropna()
        if not set(needed).issubset(data.columns) or len(data) < 25:
            return {"message": "Insufficient data for polynomial modeling."}

        X_base = data[["calories", "sleep_hours", "steps"]]
        y = data["weight_kg"]
        poly = PolynomialFeatures(degree=2, include_bias=False)
        X_poly_df = pd.DataFrame(poly.fit_transform(X_base), columns=poly.get_feature_names_out(X_base.columns), index=data.index)
        X = sm.add_constant(X_poly_df)
        model = sm.OLS(y, X).fit()

        vif_values = {}
        for i, col in enumerate(X.columns[1:], start=1):
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", RuntimeWarning)
                raw_vif = float(variance_inflation_factor(X.values, i))
            vif_values[col] = raw_vif if np.isfinite(raw_vif) else 999.0

        top_terms = sorted(model.params.items(), key=lambda kv: abs(kv[1]), reverse=True)[:8]
        return {
            "r_squared": float(model.rsquared),
            "adj_r_squared": float(model.rsquared_adj),
            "top_terms": [{"term": k, "coef": float(v)} for k, v in top_terms],
            "max_vif": float(max(vif_values.values())) if vif_values else 0.0,
            "vif_warning": any(v > 10 for v in vif_values.values()),
        }

    def _encoding_plan(self, df: pd.DataFrame) -> dict[str, str]:
        plan = {}
        for col in [c for c in df.columns if df[c].dtype == "object"]:
            card = df[col].nunique(dropna=True)
            if col in ORDINAL_COLS:
                plan[col] = "label_encoding"
            elif card <= 6:
                plan[col] = "one_hot_drop_first"
            elif card <= 20:
                plan[col] = "binary_encoding"
            else:
                plan[col] = "target_encoding_with_cv"
        return plan

    def _explainable_insights(self, result: dict[str, Any]) -> list[str]:
        insights: list[str] = []
        stage = result.get("stage")
        insights.append(f"Current analysis stage: {stage}.")

        inf = result.get("inference", {})
        if isinstance(inf, dict) and "sleep_hours" in inf:
            sleep_mean = inf["sleep_hours"].get("mean", 0)
            insights.append(
                "Average sleep is below 7 hours; prioritize consistent sleep timing."
                if sleep_mean < 7
                else "Sleep duration is in a healthy range."
            )

        reg = result.get("regression", {})
        if isinstance(reg, dict):
            diag = reg.get("diagnostics", {})
            if isinstance(diag, dict) and diag.get("multicollinearity_warning"):
                insights.append("Regression detected multicollinearity risk (high VIF); treat coefficients cautiously.")

        poly = result.get("polynomial", {})
        if isinstance(poly, dict) and poly.get("vif_warning"):
            insights.append("Polynomial model indicates high collinearity; consider feature pruning or regularization.")

        if result.get("anomaly_count", 0) > 0:
            insights.append("Anomalies were detected and excluded before model fitting.")

        return insights
