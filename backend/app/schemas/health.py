from datetime import date
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserRead(BaseModel):
    id: int
    anonymized_id: str

    model_config = {"from_attributes": True}


class BaselineCreate(BaseModel):
    user_id: int
    age: int = Field(ge=12, le=100)
    sex: str
    height_cm: float = Field(gt=80, lt=260)
    weight_kg: float = Field(gt=25, lt=300)
    body_fat_pct: Optional[float] = Field(default=None, ge=2, le=70)
    occupation_type: Optional[str] = None
    medical_conditions: Optional[str] = None
    primary_goal: str


class BaselineRead(BaselineCreate):
    id: int

    model_config = {"from_attributes": True}


class DailyLogCreate(BaseModel):
    user_id: int
    log_date: date
    calories: Optional[float] = Field(default=None, ge=0, le=10000)
    protein_g: Optional[float] = Field(default=None, ge=0, le=500)
    carbs_g: Optional[float] = Field(default=None, ge=0, le=1200)
    fats_g: Optional[float] = Field(default=None, ge=0, le=400)
    meal_timing: Optional[str] = None
    sleep_hours: Optional[float] = Field(default=None, ge=0, le=24)
    sleep_quality: Optional[int] = Field(default=None, ge=1, le=10)
    steps: Optional[int] = Field(default=None, ge=0, le=120000)
    exercise_minutes: Optional[int] = Field(default=None, ge=0, le=600)
    exercise_type: Optional[str] = None
    sedentary_minutes: Optional[int] = Field(default=None, ge=0, le=1440)
    water_liters: Optional[float] = Field(default=None, ge=0, le=20)
    stress_level: Optional[int] = Field(default=None, ge=1, le=10)
    alcohol_units: Optional[float] = Field(default=None, ge=0, le=30)
    smoking_status: Optional[str] = None
    diet_type: Optional[str] = None
    heart_rate: Optional[int] = Field(default=None, ge=25, le=230)
    blood_sugar: Optional[float] = Field(default=None, ge=20, le=500)
    weight_kg: Optional[float] = Field(default=None, ge=25, le=300)


class DailyLogRead(DailyLogCreate):
    id: int

    model_config = {"from_attributes": True}
