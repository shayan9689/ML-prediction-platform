# UI wireframes (v1)

Three screens. React + Tailwind on Vercel. Forms and charts are driven by FastAPI (`GET /tasks`, `POST /predict/{task}`, `GET /models/{task}/metrics`).

Legend: `[ button ]`  `( input )`  `{ chart }`

---

## Screen A — Task selection (`/`)

```
+------------------------------------------------------------------+
|  ML Prediction Platform                    [ Performance ]        |
+------------------------------------------------------------------+
|                                                                  |
|  Pick a prediction task                                          |
|  Train-compare-serve for three tabular problems.                 |
|                                                                  |
|  +--------------------+ +--------------------+ +----------------+|
|  | House Price        | | Customer Churn     | | Loan Risk      ||
|  | Regression         | | Classification     | | Probability    ||
|  |                    | |                    | |                ||
|  | Predict median     | | Will this customer | | P(reject /     ||
|  | California house   | | leave? Yes / No    | | default) 0–1   ||
|  | value.             | |                    | |                ||
|  |                    | |                    | |                ||
|  | [ Predict ]        | | [ Predict ]        | | [ Predict ]    ||
|  | [ View metrics ]   | | [ View metrics ]   | | [ View metrics]||
|  +--------------------+ +--------------------+ +----------------+|
|                                                                  |
+------------------------------------------------------------------+
```

Routes: Predict → `/predict/house_price` | `/predict/churn` | `/predict/loan_default`  
Metrics → `/performance?task=...`

---

## Screen B — Predict (`/predict/:task`)

```
+------------------------------------------------------------------+
|  <- Tasks     House Price                          [ Metrics ]    |
+------------------------------------------------------------------+
|                                                                  |
|  Enter features                                                  |
|  All fields come from GET /tasks for this task id.               |
|                                                                  |
|  ( median_income          )  ( housing_median_age )              |
|  ( total_rooms            )  ( total_bedrooms     )              |
|  ( population             )  ( households         )              |
|  ( latitude               )  ( longitude          )              |
|  [ ocean_proximity v ]                                           |
|                                                                  |
|  [ Get prediction ]                                              |
|                                                                  |
|  +---------------- Result card ------------------+               |
|  | Predicted value          $245,000             |               |
|  | Confidence               82%  (badge)         |               |
|  | Model used               xgboost              |               |
|  | Time                     2026-08-18 01:30 UTC |               |
|  +-----------------------------------------------+               |
|                                                                  |
|  Error examples (replace result card):                           |
|  - "MonthlyCharges is required"           (422)                  |
|  - "API unreachable — is Railway up?"     (network)              |
|  - "Unknown task"                         (404)                  |
|                                                                  |
+------------------------------------------------------------------+
```

Churn / loan use the same layout; fields change. Churn result shows Yes/No + probability. Loan result shows risk score 0–1 + high/low risk.

Loading: disable the button, show a spinner on the card.

---

## Screen C — Model performance (`/performance`)

```
+------------------------------------------------------------------+
|  <- Tasks     Model performance                                  |
+------------------------------------------------------------------+
|                                                                  |
|  Task:  ( House Price v )   Best model: xgboost                  |
|                                                                  |
|  +-----------+ +-----------+ +-----------+                       |
|  | RMSE      | | MAE       | | R2        |                       |
|  | 48,210    | | 32,104    | | 0.81      |                       |
|  +-----------+ +-----------+ +-----------+                       |
|                                                                  |
|  Model comparison                         Feature importance     |
|  +-------------------------+              +---------------------+|
|  | { bar: LR / RF / XGB }  |              | { horizontal bars } ||
|  +-------------------------+              +---------------------+|
|                                                                  |
|  Caveats: class imbalance / skew / leakage notes from EDA.       |
|                                                                  |
+------------------------------------------------------------------+
```

Churn/loan metric cards: Accuracy, F1, ROC-AUC (plus Brier for loan).

---

## Component checklist (Phase 8)

- TaskCard, PredictForm (dynamic from schema), ResultCard, MetricCards, ComparisonChart (recharts), ImportanceChart
- Loading and error states on Screens B and C
- `VITE_API_BASE_URL` for Railway
