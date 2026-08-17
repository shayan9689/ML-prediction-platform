# Evaluation report — House Price (`house_price`)

- Type: **regression**
- Best model: **xgboost**
- Selection metric: `r2`

## Test metrics

| Metric | Train | Test |
|---|---:|---:|
| rmse | 37474.5748 | 47420.3890 |
| mae | 25989.9477 | 31786.0720 |
| r2 | 0.8948 | 0.8284 |

## Caveats

- Train vs test gap looks acceptable for a v1 demo model.
- Target is capped at $500,001, which compresses residuals at the top end.
- `total_bedrooms` has missing values; median impute is used at train and serve time.

Plots: `reports/figures/house_price_*.png`
