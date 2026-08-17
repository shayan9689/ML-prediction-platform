# ML Prediction Platform

Reusable tabular ML pipeline: compare models for three tasks, serve the winner through FastAPI, and show predictions plus performance in a React dashboard.

**Phase status:** 1�11 complete for local v1. Live Vercel / Railway / Supabase links need your accounts (see [Your inputs](#your-inputs-required-for-live-deploy)).

## Overview

Users pick a task, enter features, and get a prediction with confidence. A second page shows which model won, its metrics, and feature importance.

v1 supports three tasks only � not generic AutoML.

| Task ID | Type | Best model | Hold-out score |
|---|---|---|---|
| `house_price` | Regression | XGBoost | R� **0.83** |
| `churn` | Classification | XGBoost | ROC-AUC **0.86** |
| `loan_default` | Probability / risk | Random Forest | ROC-AUC **0.72** |

Full spec: [`spec.md`](spec.md) � Wireframes: [`docs/wireframes.md`](docs/wireframes.md) � EDA: [`reports/findings.md`](reports/findings.md)

## Problem statement

Three common business questions on public tabular data: what is this house worth, will this customer leave, and how risky is this loan? The platform trains Ridge/Logistic, Random Forest, and XGBoost, keeps the winner, and exposes a documented API plus a small dashboard.

## Architecture

```
Browser (React on Vercel)
        |
        |  GET /tasks  POST /predict/{task}  GET /models/{task}/metrics
        v
FastAPI (Railway / localhost:8000)
        |  sklearn Pipeline (preprocess + model) loaded from joblib
        v
Supabase Postgres (optional) or local SQLite
        prediction_logs
```

Model files live on the API host (`data/artifacts/`), not in the browser.

## Tech stack

- Python 3.11, pandas, scikit-learn, XGBoost, FastAPI, uvicorn
- React 18 + Vite + Tailwind + Recharts
- Supabase Postgres (logs) with SQLite fallback
- Docker / Railway / Vercel

## Features

- Dynamic predict forms from `GET /tasks`
- Prediction + confidence + model name
- Metrics dashboard with comparison and feature importance
- Request logging to `logs/app.log` (JSON lines) and SQLite/Supabase
- OpenAPI at `/docs`

## Live demo

- Frontend: _add Vercel URL after you deploy_
- API: _add Railway URL after you deploy_ (`/docs`)

## Screenshots

EDA and evaluation plots are in [`reports/figures/`](reports/figures/). UI screens: task cards, predict form, performance charts.

## Local setup

Requires Python 3.11+ and Node 18+.

### Backend

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env

python -m src.models.train --task all   # already run once; skip if data/artifacts exists
uvicorn src.api.main:app --reload --port 8000
```

API: http://localhost:8000/docs

### Frontend

```bash
cd src/frontend
copy .env.example .env
npm install
npm run dev
```

UI: http://localhost:5173

### Docker (API only)

```bash
docker compose -f docker/docker-compose.yml up --build
```

## API usage

```bash
curl http://localhost:8000/health

curl -X POST http://localhost:8000/predict/house_price ^
  -H "Content-Type: application/json" ^
  -d "{\"features\":{\"longitude\":-122.23,\"latitude\":37.88,\"housing_median_age\":41,\"total_rooms\":880,\"total_bedrooms\":129,\"population\":322,\"households\":126,\"median_income\":8.3252,\"ocean_proximity\":\"NEAR BAY\"}}"
```

| Method | Path | Purpose |
|---|---|---|
| GET | `/health` | Liveness + loaded models |
| GET | `/tasks` | Form schema for the UI |
| POST | `/predict/{task}` | Score one row |
| GET | `/models/{task}/metrics` | Winner, comparison, importance |

`task` is `house_price` | `churn` | `loan_default`.

## Model performance summary

| Task | RMSE / Acc | MAE / F1 | R� / ROC-AUC |
|---|---:|---:|---:|
| House price | RMSE 47,420 | MAE 31,786 | R� 0.828 |
| Churn | Acc 0.756 | F1 0.643 | AUC 0.856 |
| Loan risk | Acc 0.731 | F1 0.561 | AUC 0.716 |

Reports: `reports/evaluation_*.md`. Retrain with `python -m src.models.train --task all`.

## Your inputs (required for live deploy)

The app runs locally without cloud accounts. For production you provide:

1. **GitHub** � push this repo (optional but needed for Vercel/Railway Git deploy).
2. **Supabase** � project URL + **service role** key; run [`docs/supabase.sql`](docs/supabase.sql).
3. **Railway** � deploy the API; set `CORS_ORIGINS`, `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`.
4. **Vercel** � deploy `src/frontend`; set `VITE_API_BASE_URL` to the Railway URL.

Step-by-step: [`docs/deployment.md`](docs/deployment.md).

## What I learned

- Persist **preprocess + model as one Pipeline** so inference cannot drift from training encodings.
- Class imbalance (churn, loans) needs class weights / `scale_pos_weight`; accuracy alone is misleading.
- California housing�s $500,001 cap and loan�s 614 rows both show up as evaluation caveats.
- The React app must not talk to Supabase; the API owns secrets and logging.

## License

MIT

## Project layout

```
data/raw/            training CSVs
data/artifacts/      joblib models + metrics JSON
notebooks/           EDA notebooks + run_eda.py
src/models/          train.py, evaluate.py
src/api/             FastAPI app
src/frontend/        React (Vite) app
tests/               pytest
docker/              compose + API Dockerfile
docs/                wireframes, deploy, supabase SQL
reports/             findings, evaluation, figures
```
