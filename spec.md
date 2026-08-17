# ML Prediction Platform - Product Spec (v1)

One-page working spec. Stack is locked to **React (Vercel) + FastAPI (Railway) + Supabase**.

**Phase status:** Phases 1�11 implemented for local v1. Live Vercel / Railway / Supabase need your accounts.

## 1. What we are building

A reusable machine learning platform that:

1. Accepts form inputs for a chosen task
2. Trains and compares multiple ML models (regression / classification / probability)
3. Selects the best-performing model
4. Serves predictions through a FastAPI backend
5. Shows results, confidence, and model performance in a React dashboard

**v1 scope is three tasks only** - not a generic "upload any CSV and train" AutoML product.

| Task ID | Type | Business example | Target |
|---|---|---|---|
| `house_price` | Regression | House price prediction | Continuous price |
| `churn` | Classification | Customer churn (Yes / No) | Class label + probability |
| `loan_default` | Probability / risk scoring | Loan reject / default risk | Probability in `[0, 1]` |

## 2. Datasets (training data)

Files live in `data/raw/`. They are **not** stored in Supabase as the primary training store in v1.

| Task | File | Dataset | Source |
|---|---|---|---|
| House price | `data/raw/housing.csv` | California Housing | ageron/handson-ml2 |
| Churn | `data/raw/telco_churn.csv` | IBM Telco Customer Churn | IBM public CSV |
| Loan risk | `data/raw/loan_prediction.csv` | Loan Prediction III | Analytics Vidhya public mirror |

## 3. User flow

```
Landing / task select
        |
        v
Dynamic input form for that task
        |
        v
POST /predict/{task}  ->  FastAPI + saved model
        |
        v
Result card: prediction + confidence + model used
        |
        v
Model Performance page: metrics, comparison, feature importance
```

Optional later: `POST /upload-dataset` to trigger retrain. **Not required for first UI.**

UI wireframes: [`docs/wireframes.md`](docs/wireframes.md).

## 4. Screens (React)

Three screens. Design against these and the API in section 7.

### Screen A - Task selection (`/`)

- Three cards: House Price, Customer Churn, Loan Risk
- Short description + Predict CTA
- Link to Model Performance for that task

### Screen B - Predict (`/predict/:task`)

- Task name in the header
- Dynamic form generated from that task's feature list
- Submit -> loading state
- Result card: prediction, confidence badge, model name, timestamp
- Error states: validation, API down, unknown task

### Screen C - Model performance (`/performance`)

- Task switcher
- Metric cards (RMSE/MAE/R2 or Accuracy/F1/ROC-AUC)
- Model comparison bar chart
- Feature-importance chart
- Short caveat text (overfit risk, class imbalance, etc.)

## 5. Tech stack (locked)

| Layer | Choice | Why |
|---|---|---|
| Frontend | React + Vite + Tailwind | Portfolio-ready UI (Phase 8) |
| Frontend host | **Vercel** | Static/SPA deploy |
| ML + API | Python 3.11, FastAPI, uvicorn | sklearn/XGBoost cannot run on Vercel |
| API host | **Railway** | Long-running Python process, model files on disk/volume |
| Training libs | pandas, scikit-learn, XGBoost, joblib | Phase 5 |
| Database | **Supabase (Postgres)** | Prediction logs, metrics JSON |
| Auth | None in v1 | Keep first demo simple |
| Local run | Docker Compose optional | Phase 10 |

**Backend is required.** Vercel hosts only the React app. Inference, preprocessing, and model files stay on Railway.

## 6. Architecture

```
Browser (React on Vercel)
        |  HTTPS
        v
FastAPI on Railway
        |  load joblib pipeline + model at startup
        |  write prediction logs / read metrics
        v
Supabase Postgres
        |
        +-- tables: prediction_logs, model_metrics

Model artifacts (joblib) live on Railway disk / volume, not in Supabase.
```

Environment variables:

| App | Variable | Purpose |
|---|---|---|
| React (Vercel) | `VITE_API_BASE_URL` | Railway API origin |
| FastAPI (Railway) | `SUPABASE_URL` | Supabase project URL |
| FastAPI (Railway) | `SUPABASE_SERVICE_ROLE_KEY` | Server-side DB writes (never expose to the browser) |
| FastAPI (Railway) | `CORS_ORIGINS` | Vercel frontend origin |
| FastAPI (Railway) | `MODELS_DIR` | Path to saved `.joblib` + metrics JSON |

The React app talks **only** to FastAPI. It does not call Supabase directly in v1.

## 7. API contract (frontend depends on this)

Base URL: Railway. OpenAPI at `/docs`.

### `GET /health`

```json
{ "status": "ok" }
```

### `GET /tasks`

Returns the three tasks and the form schema so the React form can be generated dynamically.

```json
{
  "tasks": [
    {
      "id": "house_price",
      "name": "House Price",
      "type": "regression",
      "features": [
        { "name": "median_income", "type": "number", "required": true },
        { "name": "ocean_proximity", "type": "select", "options": ["<1H OCEAN", "INLAND", "NEAR OCEAN", "NEAR BAY", "ISLAND"], "required": true }
      ]
    }
  ]
}
```

### `POST /predict/{task}`

Path `task` is one of: `house_price` | `churn` | `loan_default`.

**Response (all tasks):**

```json
{
  "prediction": 245000.12,
  "prediction_label": null,
  "confidence": 0.82,
  "model_used": "xgboost",
  "task": "house_price",
  "timestamp": "2026-08-18T01:30:00Z"
}
```

| Task | `prediction` | `prediction_label` | `confidence` |
|---|---|---|---|
| `house_price` | numeric price | `null` | 1 - normalized error band, or interval score |
| `churn` | P(churn = Yes) | `"Yes"` / `"No"` | max class probability |
| `loan_default` | P(default / reject) | `"high_risk"` / `"low_risk"` | same as probability (risk score) |

### `GET /models/{task}/metrics`

```json
{
  "task": "churn",
  "best_model": "xgboost",
  "metrics": { "accuracy": 0.81, "f1": 0.64, "roc_auc": 0.84 },
  "comparison": [
    { "model": "logistic_regression", "f1": 0.58, "roc_auc": 0.79 },
    { "model": "random_forest", "f1": 0.62, "roc_auc": 0.82 },
    { "model": "xgboost", "f1": 0.64, "roc_auc": 0.84 }
  ],
  "feature_importance": [
    { "feature": "tenure", "importance": 0.21 }
  ]
}
```

Errors: `422` invalid fields, `404` unknown task, `503` model not loaded.

## 8. Features per task (form fields)

Confirmed from the Phase 1 CSVs.

**House price (regression)** - `housing.csv`  
Numeric: `longitude`, `latitude`, `housing_median_age`, `total_rooms`, `total_bedrooms`, `population`, `households`, `median_income`  
Categorical: `ocean_proximity`  
Target: `median_house_value`  
Metrics: RMSE, MAE, R2

**Churn (classification)** - `telco_churn.csv`  
Numeric: `tenure`, `MonthlyCharges`, `TotalCharges`, `SeniorCitizen`  
Categorical: `gender`, `Partner`, `Dependents`, `PhoneService`, `MultipleLines`, `InternetService`, `OnlineSecurity`, `OnlineBackup`, `DeviceProtection`, `TechSupport`, `StreamingTV`, `StreamingMovies`, `Contract`, `PaperlessBilling`, `PaymentMethod`  
Drop at train time: `customerID` (ID, leakage)  
Target: `Churn` (`Yes`/`No`)  
Metrics: Accuracy, Precision, Recall, F1, ROC-AUC

**Loan risk (probability)** - `loan_prediction.csv`  
Numeric: `ApplicantIncome`, `CoapplicantIncome`, `LoanAmount`, `Loan_Amount_Term`, `Credit_History`  
Categorical: `Gender`, `Married`, `Dependents`, `Education`, `Self_Employed`, `Property_Area`  
Drop: `Loan_ID`  
Target: `Loan_Status` (`Y`/`N`) served as **P(default or reject)** = P(status = N)  
Metrics: ROC-AUC (primary), Brier score, F1  
Threshold for label: 0.5 unless calibration says otherwise

## 9. Models to compare (every task)

- Linear / Logistic Regression
- Random Forest
- XGBoost

Optional later: SVM, KNN.  
Select best by: R2 (regression), ROC-AUC (classification + probability).  
Persist winner with joblib + metadata JSON.

## 10. Supabase schema (v1)

```sql
create table prediction_logs (
  id uuid primary key default gen_random_uuid(),
  created_at timestamptz not null default now(),
  task text not null,
  model_used text,
  input jsonb not null,
  prediction jsonb not null,
  latency_ms integer,
  error text
);

create table model_metrics (
  task text primary key,
  best_model text not null,
  metrics jsonb not null,
  comparison jsonb,
  feature_importance jsonb,
  trained_at timestamptz not null default now()
);
```

Row Level Security: deny all from the anon key. Only the Railway service role writes/reads.

## 11. Success criteria for v1 demo

- User picks a task, fills the form, sees a prediction + confidence in the UI
- Performance page shows real metrics from the trained model (not placeholders)
- Invalid input returns a clear error in the UI
- Live links: Vercel frontend + Railway `/docs` + README

## 12. Out of scope (v1)

- User accounts / Supabase Auth
- Training from the browser / arbitrary CSV AutoML
- Real-time streaming data
- Mobile native apps
- Paying for Kaggle datasets or private data

## 13. Build order

| Phase | Focus | UI impact |
|---|---|---|
| 1 | This spec, folders, datasets, wireframes | Design against sections 4 and 7 |
| 2 | Repo, venv, CI, Cursor rules | - |
| 3-6 | Preprocess, EDA, train, evaluate | Metrics JSON that Screen C consumes |
| 7 | FastAPI on Railway shape | Frontend can be mocked until this exists |
| 8 | React app (Vite + Tailwind) | Deploy to Vercel |
| 9 | Tests, logging, QA | Error states |
| 10 | Docker, Railway + Vercel + env | CORS |
| 11 | README, demo GIF | Portfolio |

**UI note:** React can be scaffolded in Phase 8 with mocked `/tasks` and `/predict` responses, then pointed at Railway when Phase 7 is done.
