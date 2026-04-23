# Health Intelligence Platform

A **production-grade backend-first Health Intelligence Platform** where structured lifestyle and physiological data is continuously collected, stored as longitudinal time-series data, and processed through a full statistical decision engine (SSDI) to produce uncertainty-aware, interpretable insights.

## Platform architecture (core principle)
- **Core product (brain):** FastAPI + PostgreSQL + Statistical Engine.
- **Current face:** Next.js web app.
- **Future face:** React Native mobile app (same backend APIs).

This is a **single platform with multiple clients**, not separate products per device.

## What is implemented

### Backend (central engine)
- FastAPI API layer with structured validation.
- SQLAlchemy data model with **PII separation**:
  - `users` table stores anonymized identity.
  - `user_pii` table stores email separately.
  - `baseline_profiles` and `daily_logs` store health/statistical inputs.
- Daily logs persisted as clean timestamped rows with one-log-per-user-per-day uniqueness.

### Statistical Decision Engine (SSDI)
Pipeline includes:
1. **Imputation layer**
   - Forward-fill for slow-changing bio metrics.
   - Median fill for behavior metrics.
2. **Outlier/anomaly layer**
   - Z-score and IQR detection.
   - Flagged values excluded from modeling inputs.
3. **Transformation layer**
   - Numeric standardization.
   - Hybrid categorical encoding plan:
     - low-cardinality → one-hot (drop first)
     - medium-cardinality → binary encoding
     - high-cardinality → target encoding with CV safeguards
     - ordinal → label encoding
4. **Cold-start stage gates**
   - descriptive → inference → hypothesis → comparison → regression → polynomial
5. **Inference layer**
   - means + 95% confidence intervals.
6. **Hypothesis layer**
   - diet-vs-weight t-test with decision logic.
7. **Comparison layer**
   - chi-square test for categorical associations.
8. **Modeling layer**
   - multivariable OLS regression.
   - polynomial feature expansion and polynomial OLS.
9. **Diagnostics layer**
   - VIF for multicollinearity.
   - Breusch-Pagan (heteroscedasticity).
   - Durbin-Watson (autocorrelation).
10. **Data decay preview**
    - exponential weighting to prioritize recency.

### Frontend (Next.js)
- Structured workflow for:
  - Identity creation
  - Baseline onboarding
  - Daily structured logging
  - SSDI analysis output visualization
- Pulls platform capability metadata from backend to reinforce multi-client backend-first design.

## API endpoints
`/api/v1`
- `GET /platform/capabilities`
- `POST /users`
- `POST /baseline`
- `POST /logs`
- `GET /users/{user_id}/logs`
- `GET /users/{user_id}/analysis`

## Run with Docker
```bash
docker compose up --build
```

- Frontend: http://localhost:3000
- Backend docs: http://localhost:8000/docs
- Backend health: http://localhost:8000/health

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

## Next production steps
1. Alembic migrations and schema versioning.
2. AuthN/AuthZ, encryption-at-rest, audit logs, and key management.
3. Bayesian online updates and MANOVA support.
4. Model monitoring, retraining schedules, and drift detection.
5. Dedicated React Native client implementation.
6. End-to-end automated tests and CI/CD gates.
