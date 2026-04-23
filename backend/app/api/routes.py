from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.security import create_access_token, encrypt_field, hash_lookup, hash_password, verify_password
from app.db.session import get_db
from app.models.health import BaselineProfile, DailyLog, User, UserPII
from app.schemas.health import (
    BaselineCreate,
    BaselineRead,
    DailyLogCreate,
    DailyLogRead,
    LoginRequest,
    Token,
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
        "security": ["jwt_authn", "row_level_authz", "encrypted_pii_fields", "env_secrets_management"],
    }


@router.post("/users", response_model=UserRead)
def create_user(payload: UserCreate, db: Session = Depends(get_db)):
    email_hash = hash_lookup(payload.email)
    exists = db.scalar(select(UserPII).where(UserPII.email_hash == email_hash))
    if exists:
        raise HTTPException(status_code=409, detail="Email already exists")

    anonymized = uuid.uuid4().hex + uuid.uuid4().hex
    user = User(anonymized_id=anonymized)
    db.add(user)
    db.flush()
    db.add(
        UserPII(
            user_id=user.id,
            email_hash=email_hash,
            email_encrypted=encrypt_field(payload.email),
            password_hash=hash_password(payload.password),
        )
    )
    db.commit()
    db.refresh(user)
    return user


@router.post("/auth/login", response_model=Token)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    email_hash = hash_lookup(payload.email)
    pii = db.scalar(select(UserPII).where(UserPII.email_hash == email_hash))
    if not pii or not verify_password(payload.password, pii.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")

    token = create_access_token(str(pii.user_id))
    return Token(access_token=token)


@router.post("/baseline", response_model=BaselineRead)
def upsert_baseline(
    payload: BaselineCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if payload.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

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
def create_or_replace_daily_log(
    payload: DailyLogCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if payload.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

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
def list_logs(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")
    return list(db.scalars(select(DailyLog).where(DailyLog.user_id == user_id).order_by(DailyLog.log_date)).all())


@router.get("/users/{user_id}/analysis")
def analyze_user(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

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
