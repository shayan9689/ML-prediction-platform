# Evaluation report — Customer Churn (`churn`)

- Type: **classification**
- Best model: **xgboost**
- Selection metric: `roc_auc`

## Test metrics

| Metric | Train | Test |
|---|---:|---:|
| accuracy | 0.7638 | 0.7559 |
| precision | 0.5356 | 0.5249 |
| recall | 0.8272 | 0.8286 |
| f1 | 0.6502 | 0.6427 |
| roc_auc | 0.8693 | 0.8555 |
| brier | 0.1529 | 0.1607 |

## Caveats

- Train vs test gap looks acceptable for a v1 demo model.
- Churn is imbalanced (~27% Yes). Class weights / scale_pos_weight were used.
- `customerID` is dropped to avoid identifier leakage.

Plots: `reports/figures/churn_*.png`
