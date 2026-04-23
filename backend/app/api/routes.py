from __future__ import annotations

import hashlib
import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.health import BaselineProfile, DailyLog, User, UserPII
from app.schemas.health import (
    BaselineCreate,
    BaselineRead,
    DailyLogCreate,
    DailyLogRead,
    UserCreate,
    UserRead,
)
from app.services.statistical_engine import StatisticalDecisionEngine

router = APIRouter()
engine = StatisticalDecisionEngine()


@router.get("/platform/capabilities")
def platform_capabilities():
    return {
        "backend_role": "central statistical decision engine",
        "supported_clients": ["nextjs-web"],
        "planned_clients": ["react-native-mobile"],
        "pipeline": [
            "collection",
            "imputation",
            "anomaly_detection",
            "hybrid_encoding",
            "feature_engineering",
            "cold_start_gating",
            "inference",
            "hypothesis_testing",
            "comparison",
            "regression_and_polynomial",
            "diagnostics_and_vif",
            "data_decay",
            "insight_generation",
        ],
    }


@router.post("/users", response_model=UserRead)
def create_user(payload: UserCreate, db: Session = Depends(get_db)):
    exists = db.scalar(select(UserPII).where(UserPII.email == payload.email))
    if exists:
        raise HTTPException(status_code=409, detail="Email already exists")

    anonymized = hashlib.sha256(f"{payload.email}:{uuid.uuid4()}".encode()).hexdigest()
    user = User(anonymized_id=anonymized)
    db.add(user)
    db.flush()
    db.add(UserPII(user_id=user.id, email=payload.email))
    db.commit()
    db.refresh(user)
    return user


@router.post("/baseline", response_model=BaselineRead)
def upsert_baseline(payload: BaselineCreate, db: Session = Depends(get_db)):
    user = db.get(User, payload.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    profile = db.scalar(select(BaselineProfile).where(BaselineProfile.user_id == payload.user_id))
    if profile:
        for k, v in payload.model_dump().items():
            setattr(profile, k, v)
    else:
        profile = BaselineProfile(**payload.model_dump())
        db.add(profile)

    db.commit()
    db.refresh(profile)
    return profile


@router.post("/logs", response_model=DailyLogRead)
def create_or_replace_daily_log(payload: DailyLogCreate, db: Session = Depends(get_db)):
    user = db.get(User, payload.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    existing = db.scalar(
        select(DailyLog).where(DailyLog.user_id == payload.user_id, DailyLog.log_date == payload.log_date)
    )
    if existing:
        for k, v in payload.model_dump().items():
            setattr(existing, k, v)
        log = existing
    else:
        log = DailyLog(**payload.model_dump())
        db.add(log)

    db.commit()
    db.refresh(log)
    return log


@router.get("/users/{user_id}/logs", response_model=list[DailyLogRead])
def list_logs(user_id: int, db: Session = Depends(get_db)):
    return list(db.scalars(select(DailyLog).where(DailyLog.user_id == user_id).order_by(DailyLog.log_date)).all())


@router.get("/users/{user_id}/analysis")
def analyze_user(user_id: int, db: Session = Depends(get_db)):
    logs = db.scalars(select(DailyLog).where(DailyLog.user_id == user_id).order_by(DailyLog.log_date)).all()
    records = [
        {
            "log_date": log.log_date.isoformat(),
            "calories": log.calories,
            "protein_g": log.protein_g,
            "carbs_g": log.carbs_g,
            "fats_g": log.fats_g,
            "meal_timing": log.meal_timing,
            "sleep_hours": log.sleep_hours,
            "sleep_quality": log.sleep_quality,
            "steps": log.steps,
            "exercise_minutes": log.exercise_minutes,
            "exercise_type": log.exercise_type,
            "sedentary_minutes": log.sedentary_minutes,
            "water_liters": log.water_liters,
            "stress_level": log.stress_level,
            "alcohol_units": log.alcohol_units,
            "smoking_status": log.smoking_status,
            "diet_type": log.diet_type,
            "heart_rate": log.heart_rate,
            "blood_sugar": log.blood_sugar,
            "weight_kg": log.weight_kg,
        }
        for log in logs
    ]
    return engine.run_pipeline(records)
