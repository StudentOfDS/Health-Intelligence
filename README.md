# Health Intelligence Platform

A production-grade, backend-first Health Intelligence Platform where structured lifestyle + physiological data is collected over time and processed by a centralized Statistical Decision Intelligence (SSDI) engine.

## ✅ Requested capabilities now included

### 1) Alembic migrations + separate PII/PHI schemas
- Added Alembic config and initial migration in `backend/alembic`.
- Added Postgres schema separation:
  - `pii` schema: identity/security fields (`user_pii`)
  - `phi` schema: health analytics data (`users`, `baseline_profiles`, `daily_logs`)
- Startup bootstraps `CREATE SCHEMA IF NOT EXISTS pii/phi`.

### 2) AuthN/AuthZ + encrypted fields + secrets management
- Added JWT authentication (`/api/v1/auth/login`).
- Added route-level authorization enforcing user ownership of profile/log/analysis data.
- Added encrypted PII storage (`email_encrypted`) with Fernet; lookup by `email_hash`.
- Added password hashing with bcrypt.
- Added secrets in config (JWT secret, field encryption key, token TTL) and env-driven settings.

### 3) Robust regression + diagnostics
- OLS multivariable regression.
- Polynomial regression with interaction/squared terms.
- VIF-based multicollinearity checks.
- Breusch-Pagan heteroscedasticity test.
- Durbin-Watson autocorrelation statistic.

### 4) Sliding-window/exponential data decay weighting
- Added exponential decay weighting preview.
- Added weighted regression (WLS) so recent records influence estimates more.

### 5) Bayesian online updates + explainable insights
- Added Bayesian posterior update for calories (normal-normal update).
- Added plain-language explainable insights generated from stage/diagnostics/outliers.

### 6) Test suite (backend unit + integration + frontend E2E)
- Backend unit test for SSDI progression and output integrity.
- Backend integration smoke test for app health + platform capabilities endpoint.
- Frontend E2E scaffold using Playwright.

---

## Architecture
- **Backend core (“brain”)**: FastAPI + PostgreSQL + SSDI statistical engine.
- **Web client (“face”)**: Next.js.
- **Future client**: React Native consuming same APIs.

## API endpoints
`/api/v1`
- `GET /platform/capabilities`
- `POST /users`
- `POST /auth/login`
- `POST /baseline` (auth required)
- `POST /logs` (auth required)
- `GET /users/{user_id}/logs` (auth required)
- `GET /users/{user_id}/analysis` (auth required)

## Run with Docker
```bash
docker compose up --build
```

## Local backend setup
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

## Run tests
### Backend
```bash
cd backend
pytest
```

### Frontend E2E
```bash
cd frontend
npm install
npx playwright install
npm run test:e2e
```
