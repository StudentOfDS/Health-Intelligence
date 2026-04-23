from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd

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


@dataclass
class ColdStartThresholds:
    descriptive_min_days: int = 3
    inference_min_days: int = 10
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
        frame, anomalies = self._detect_outliers(frame)

        row_count = len(frame)
        stage = self._resolve_stage(row_count)
        result: dict[str, Any] = {
            "status": "ok",
            "stage": stage,
            "n_days": row_count,
            "anomaly_count": len(anomalies),
            "anomalies": anomalies[:15],
            "encoding_strategy": self._encoding_plan(frame),
            "descriptive": self._descriptive_stats(frame),
        }

        if row_count >= self.thresholds.inference_min_days:
            result["inference"] = self._inference_summary(frame)

        if row_count >= self.thresholds.regression_min_days:
            result["regression"] = self._linear_relationships(frame)

        if row_count >= self.thresholds.polynomial_min_days:
            result["polynomial"] = self._polynomial_readiness(frame)

        return result

    def _impute_missing(self, df: pd.DataFrame) -> pd.DataFrame:
        out = df.copy()
        existing_slow = [c for c in SLOW_CHANGING_COLS if c in out.columns]
        existing_behavior = [c for c in BEHAVIOR_COLS if c in out.columns]

        if existing_slow:
            out[existing_slow] = out[existing_slow].ffill()

        for col in existing_behavior:
            median_val = out[col].median(skipna=True)
            if pd.notna(median_val):
                out[col] = out[col].fillna(median_val)

        return out

    def _detect_outliers(self, df: pd.DataFrame) -> tuple[pd.DataFrame, list[dict[str, Any]]]:
        out = df.copy()
        numeric_cols = [c for c in out.columns if pd.api.types.is_numeric_dtype(out[c])]
        anomalies: list[dict[str, Any]] = []

        for col in numeric_cols:
            series = out[col].dropna()
            if len(series) < 8:
                continue
            q1, q3 = series.quantile([0.25, 0.75])
            iqr = q3 - q1
            if iqr == 0:
                continue
            lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
            idx = out.index[(out[col] < lower) | (out[col] > upper)]
            for i in idx:
                anomalies.append({"index": int(i), "feature": col, "value": float(out.at[i, col])})
            out.loc[idx, col] = np.nan

        return out, anomalies

    def _resolve_stage(self, row_count: int) -> str:
        if row_count < self.thresholds.inference_min_days:
            return "descriptive"
        if row_count < self.thresholds.regression_min_days:
            return "inference"
        if row_count < self.thresholds.polynomial_min_days:
            return "regression"
        return "polynomial"

    def _descriptive_stats(self, df: pd.DataFrame) -> dict[str, dict[str, float]]:
        numeric = df.select_dtypes(include=[np.number])
        summary = {}
        for col in numeric.columns:
            summary[col] = {
                "mean": float(numeric[col].mean()),
                "min": float(numeric[col].min()),
                "max": float(numeric[col].max()),
            }
        return summary

    def _inference_summary(self, df: pd.DataFrame) -> dict[str, dict[str, float]]:
        numeric = df.select_dtypes(include=[np.number])
        inference = {}
        for col in [c for c in ["calories", "sleep_hours", "weight_kg"] if c in numeric.columns]:
            series = numeric[col].dropna()
            if len(series) < 2:
                continue
            std = series.std(ddof=1)
            se = std / np.sqrt(len(series)) if std > 0 else 0
            mean = series.mean()
            inference[col] = {
                "mean": float(mean),
                "ci95_low": float(mean - 1.96 * se),
                "ci95_high": float(mean + 1.96 * se),
            }
        return inference

    def _linear_relationships(self, df: pd.DataFrame) -> dict[str, Any]:
        numeric = df.select_dtypes(include=[np.number]).dropna(axis=1, how="all")
        if {"calories", "weight_kg"}.issubset(numeric.columns):
            corr = numeric[["calories", "weight_kg"]].corr().iloc[0, 1]
            return {"calories_vs_weight_corr": float(corr)}
        return {"message": "Not enough numeric columns for relationship checks."}

    def _polynomial_readiness(self, df: pd.DataFrame) -> dict[str, Any]:
        feature_count = max(df.select_dtypes(include=[np.number]).shape[1], 1)
        n = len(df)
        approx_vif_risk = round((feature_count**2) / n, 3)
        return {
            "feature_count": feature_count,
            "approx_vif_risk": approx_vif_risk,
            "warning": "High risk of multicollinearity" if approx_vif_risk > 1.0 else "Acceptable",
        }

    def _encoding_plan(self, df: pd.DataFrame) -> dict[str, str]:
        plan = {}
        categorical = [c for c in df.columns if df[c].dtype == "object"]
        for col in categorical:
            cardinality = df[col].nunique(dropna=True)
            if col in {"sleep_quality", "stress_level"}:
                plan[col] = "label_encoding"
            elif cardinality <= 6:
                plan[col] = "one_hot_drop_first"
            elif cardinality <= 20:
                plan[col] = "binary_encoding"
            else:
                plan[col] = "target_encoding_with_cv"
        return plan
