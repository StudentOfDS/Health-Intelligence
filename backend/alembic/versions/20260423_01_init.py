"""init pii/phi schemas and core tables

Revision ID: 20260423_01
Revises:
Create Date: 2026-04-23
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '20260423_01'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS pii")
    op.execute("CREATE SCHEMA IF NOT EXISTS phi")

    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('anonymized_id', sa.String(length=64), nullable=False, unique=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        schema='phi',
    )

    op.create_table(
        'user_pii',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('phi.users.id'), nullable=False, unique=True),
        sa.Column('email_hash', sa.String(length=64), nullable=False, unique=True),
        sa.Column('email_encrypted', sa.Text(), nullable=False),
        sa.Column('password_hash', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        schema='pii',
    )

    op.create_table(
        'baseline_profiles',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('phi.users.id'), nullable=False, unique=True),
        sa.Column('age', sa.Integer(), nullable=False),
        sa.Column('sex', sa.String(length=32), nullable=False),
        sa.Column('height_cm', sa.Float(), nullable=False),
        sa.Column('weight_kg', sa.Float(), nullable=False),
        sa.Column('body_fat_pct', sa.Float(), nullable=True),
        sa.Column('occupation_type', sa.String(length=64), nullable=True),
        sa.Column('medical_conditions', sa.Text(), nullable=True),
        sa.Column('primary_goal', sa.String(length=128), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        schema='phi',
    )

    op.create_table(
        'daily_logs',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('phi.users.id'), nullable=False),
        sa.Column('log_date', sa.Date(), nullable=False),
        sa.Column('calories', sa.Float(), nullable=True),
        sa.Column('protein_g', sa.Float(), nullable=True),
        sa.Column('carbs_g', sa.Float(), nullable=True),
        sa.Column('fats_g', sa.Float(), nullable=True),
        sa.Column('meal_timing', sa.String(length=64), nullable=True),
        sa.Column('sleep_hours', sa.Float(), nullable=True),
        sa.Column('sleep_quality', sa.Integer(), nullable=True),
        sa.Column('steps', sa.Integer(), nullable=True),
        sa.Column('exercise_minutes', sa.Integer(), nullable=True),
        sa.Column('exercise_type', sa.String(length=64), nullable=True),
        sa.Column('sedentary_minutes', sa.Integer(), nullable=True),
        sa.Column('water_liters', sa.Float(), nullable=True),
        sa.Column('stress_level', sa.Integer(), nullable=True),
        sa.Column('alcohol_units', sa.Float(), nullable=True),
        sa.Column('smoking_status', sa.String(length=32), nullable=True),
        sa.Column('diet_type', sa.String(length=64), nullable=True),
        sa.Column('heart_rate', sa.Integer(), nullable=True),
        sa.Column('blood_sugar', sa.Float(), nullable=True),
        sa.Column('weight_kg', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.UniqueConstraint('user_id', 'log_date', name='uq_user_log_date'),
        schema='phi',
    )


def downgrade() -> None:
    op.drop_table('daily_logs', schema='phi')
    op.drop_table('baseline_profiles', schema='phi')
    op.drop_table('user_pii', schema='pii')
    op.drop_table('users', schema='phi')
