# Health Intelligence App

Production-oriented starter for a **Health Intelligence** platform using:

- **Frontend:** Next.js (React, mobile-first UI)
- **Backend:** FastAPI (validation + statistical decision engine)
- **Database:** PostgreSQL (longitudinal time-series storage)

## What is implemented

### 1) Data collection and storage
- User identity table with anonymized identifiers.
- Baseline onboarding profile (age, sex, height, weight, body fat, occupation, conditions, goal).
- Daily structured health logs for nutrition, sleep, activity, stress, hydration, and optional physiology.
- Input validation on the API boundary via Pydantic schemas.

### 2) Statistical decision pipeline (SSDI-ready foundation)
The backend `StatisticalDecisionEngine` currently includes:
- Missing-data imputation:
  - Forward fill for slow-changing bio metrics.
  - Median fill for behavior variables.
- Outlier/anomaly handling:
  - IQR-based anomaly detection.
  - Outlier points are marked and nulled before downstream analysis.
- Stage gating (cold-start thresholds):
  - Descriptive only for very small N.
  - Inference unlocked at 10+ days.
  - Regression unlocked at 30+ days.
  - Polynomial readiness checks at 45+ days.
- Encoding strategy planner by categorical cardinality:
  - One-hot (low cardinality), binary (medium), target encoding w/ CV (high), label encoding for ordinal-like fields.

### 3) Frontend workflow
- Create user
- Add quick daily log
- Run analysis
- Render structured JSON output (stage, anomaly stats, summaries)

## API endpoints
`/api/v1`
- `POST /users`
- `POST /baseline`
- `POST /logs`
- `GET /users/{user_id}/logs`
- `GET /users/{user_id}/analysis`

## Run with Docker
```bash
docker compose up --build
```

Services:
- Frontend: http://localhost:3000
- Backend docs: http://localhost:8000/docs
- Postgres: localhost:5432

## Local development

### Backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Notes for next iteration
To fully match a production-grade SSDI engine, next steps are:
1. Alembic migrations and separate PII/PHI schemas.
2. AuthN/AuthZ + encrypted fields + secrets management.
3. Robust regression + VIF + heteroscedasticity/autocorrelation diagnostics.
4. Sliding-window/exponential decay model weighting.
5. Bayesian online updates and richer explainable insights layer.
6. Test suite (backend unit + integration + frontend E2E).
