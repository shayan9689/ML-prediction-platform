# ML Prediction Platform

**Train → compare → serve tabular ML models through a FastAPI backend and a React dashboard.**

Three real-world use cases: neighborhood home value, customer retention, and loan risk. No OpenAI — classical ML only (scikit-learn + XGBoost).

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/API-FastAPI-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/UI-React-61DAFB?logo=react&logoColor=black)](https://react.dev/)
[![Tests](https://img.shields.io/badge/tests-13%20passing-success)](tests/)

---

## Live demo

| Service | URL |
|---|---|
| Frontend (Vercel) | _Coming soon — add your deploy URL_ |
| API + docs (Railway) | _Coming soon — add your deploy URL_ (`/docs`) |

> Works fully **locally** today. See [Quick start](#-quick-start) below.

---

## What it does

1. **Pick a task** — Housing, telecom churn, or loan risk
2. **Fill a short form** — client-friendly fields (regions, not GPS coordinates)
3. **Get a score** — prediction + confidence + model name
4. **Check accuracy** — how reliable the model is on test data (not a repeat of your form)

```
Home  →  Predict  →  Result card
              ↓
         Accuracy (model quality report)
```

---

## Three prediction tasks

| | Task | What you get | Best model | Test score |
|---|---|---|---|---|
| 🏠 | **Neighborhood value** | Estimated home price (USD) | XGBoost | R² **0.83** |
| 📱 | **Customer retention** | Stay vs leave + probability | XGBoost | ROC-AUC **0.86** |
| 💳 | **Loan risk score** | High / low reject risk (0–1) | Random Forest | ROC-AUC **0.72** |

Each task compares **Ridge/Logistic**, **Random Forest**, and **XGBoost**, then saves the winner as a joblib pipeline.

---

## Screenshots

_Add 2–3 screenshots here before your LinkedIn post:_

| Home | Predict | Accuracy |
|---|---|---|
| _screenshot_ | _screenshot_ | _screenshot_ |

Evaluation charts: [`reports/figures/`](reports/figures/)

---

## Tech stack

| Layer | Tools |
|---|---|
| ML | Python, pandas, scikit-learn, XGBoost, joblib |
| API | FastAPI, uvicorn, Pydantic |
| UI | React 18, Vite, Tailwind, Recharts |
| Database | Supabase Postgres _(prod)_ · SQLite _(local fallback)_ |
| Deploy | Railway (API) · Vercel (frontend) · Docker |

---

## Architecture

```
┌─────────────────────────────────────────┐
│  React dashboard (Vercel / localhost)   │
│  Home · Predict · Accuracy              │
└──────────────────┬──────────────────────┘
                   │  REST
                   ▼
┌─────────────────────────────────────────┐
│  FastAPI (Railway / localhost:8000)     │
│  preprocess + model (joblib)            │
└──────────────────┬──────────────────────┘
                   │
                   ▼
        Supabase or SQLite
        (prediction logs)
```

Model files live in `data/artifacts/` on the API server — never in the browser.

---

## Features

- ✅ Dynamic forms driven by `GET /tasks`
- ✅ Preprocess + model saved as one sklearn **Pipeline** (no train/serve drift)
- ✅ Confidence score and model name on every prediction
- ✅ **Accuracy** page with plain-English metrics + charts
- ✅ Structured logging (`logs/app.log`) + SQLite/Supabase
- ✅ 13 pytest tests (preprocessing + API)
- ✅ OpenAPI docs at `/docs`

---

## Quick start

**Requirements:** Python 3.11+, Node 18+

### 1. Backend (terminal 1)

```bash
git clone https://github.com/shayan9689/ML-prediction-platform.git
cd ML-prediction-platform

python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
# source .venv/bin/activate

pip install -r requirements.txt
copy .env.example .env          # Windows
# cp .env.example .env          # macOS / Linux

# Skip if data/artifacts/ already exists
python -m src.models.train --task all

uvicorn src.api.main:app --reload --port 8000
```

Open **http://localhost:8000/docs**

### 2. Frontend (terminal 2)

```bash
cd src/frontend
copy .env.example .env          # Windows
# cp .env.example .env          # macOS / Linux
npm install
npm run dev
```

Open **http://localhost:5173**

### 3. Docker (API only, optional)

```bash
docker compose -f docker/docker-compose.yml up --build
```

---

## API at a glance

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | API status + loaded models |
| `GET` | `/tasks` | Task list + form schema |
| `POST` | `/predict/{task}` | Run prediction |
| `GET` | `/models/{task}/metrics` | Model accuracy report |

**Tasks:** `house_price` · `churn` · `loan_default`

<details>
<summary><b>Example: house price prediction</b></summary>

```bash
curl -X POST http://localhost:8000/predict/house_price \
  -H "Content-Type: application/json" \
  -d "{\"features\":{\"longitude\":-122.23,\"latitude\":37.88,\"housing_median_age\":41,\"total_rooms\":880,\"total_bedrooms\":129,\"population\":322,\"households\":126,\"median_income\":8.3252,\"ocean_proximity\":\"NEAR BAY\"}}"
```

</details>

---

## Model performance (hold-out test set)

These numbers come from data the model **never saw during training**.

### 🏠 Neighborhood value

| Metric | Value | Plain English |
|---|---:|---|
| Typical miss (RMSE) | $47,420 | Big errors count extra |
| Average miss (MAE) | $31,786 | Average dollar error |
| Fit quality (R²) | 0.83 / 1.00 | Explains ~83% of price variation |

### 📱 Customer retention

| Metric | Value |
|---|---:|
| Accuracy | 75.6% |
| F1 | 0.64 |
| ROC-AUC | **0.86** |

### 💳 Loan risk score

| Metric | Value |
|---|---:|
| Accuracy | 73.1% |
| F1 | 0.56 |
| ROC-AUC | **0.72** |

Full reports: [`reports/evaluation_*.md`](reports/) · Retrain: `python -m src.models.train --task all`

---

## Project structure

```
ML-prediction-platform/
├── data/
│   ├── raw/              # Training CSVs
│   └── artifacts/        # Saved models + metrics JSON
├── src/
│   ├── api/              # FastAPI app
│   ├── models/           # train.py, evaluate.py
│   ├── frontend/         # React (Vite) dashboard
│   ├── config.py         # Task definitions
│   └── preprocessing.py
├── tests/                # pytest
├── reports/              # EDA + evaluation + charts
├── docs/                 # Deploy guide, wireframes, Supabase SQL
└── docker/               # Dockerfile + compose
```

---

## Deploy to production

| Step | Service | What you need |
|---|---|---|
| 1 | **Supabase** | Run [`docs/supabase.sql`](docs/supabase.sql) · service role key |
| 2 | **Railway** | Deploy API · set `CORS_ORIGINS`, `SUPABASE_*` |
| 3 | **Vercel** | Deploy `src/frontend` · set `VITE_API_BASE_URL` |

Full guide: [`docs/deploy-supabase-railway.md`](docs/deploy-supabase-railway.md)

---

## What I learned

- 🔗 Save **preprocess + model together** — inference must match training encodings
- ⚖️ **Class imbalance** (churn, loans) — accuracy alone is misleading; use ROC-AUC and F1
- 🏘️ **Client UX ≠ raw CSV columns** — map regions instead of lat/long for demos
- 🔒 **Frontend → API only** — secrets and DB writes stay on the server

---

## Docs

| File | Contents |
|---|---|
| [`spec.md`](spec.md) | Product spec + API contract |
| [`docs/wireframes.md`](docs/wireframes.md) | UI wireframes |
| [`reports/findings.md`](reports/findings.md) | EDA summary |

---

## License

MIT

---

**Built for portfolio / interview demos.** Star ⭐ the repo if you find it useful.
