from datetime import date, datetime
from typing import Optional

from sqlalchemy import Date, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    anonymized_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    profile: Mapped["BaselineProfile"] = relationship(back_populates="user", uselist=False, cascade="all, delete-orphan")
    logs: Mapped[list["DailyLog"]] = relationship(back_populates="user", cascade="all, delete-orphan")


class BaselineProfile(Base):
    __tablename__ = "baseline_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True, nullable=False)
    age: Mapped[int] = mapped_column(Integer)
    sex: Mapped[str] = mapped_column(String(32))
    height_cm: Mapped[float] = mapped_column(Float)
    weight_kg: Mapped[float] = mapped_column(Float)
    body_fat_pct: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    occupation_type: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    medical_conditions: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    primary_goal: Mapped[str] = mapped_column(String(128))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped[User] = relationship(back_populates="profile")


class DailyLog(Base):
    __tablename__ = "daily_logs"
    __table_args__ = (UniqueConstraint("user_id", "log_date", name="uq_user_log_date"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    log_date: Mapped[date] = mapped_column(Date, index=True)

    calories: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    protein_g: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    carbs_g: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    fats_g: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    sleep_hours: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    sleep_quality: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    steps: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    exercise_minutes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    exercise_type: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    sedentary_minutes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    water_liters: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    stress_level: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    alcohol_units: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    smoking_status: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    diet_type: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    heart_rate: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    blood_sugar: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    weight_kg: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped[User] = relationship(back_populates="logs")
