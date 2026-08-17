# Evaluation report — Loan Risk (`loan_default`)

- Type: **probability**
- Best model: **random_forest**
- Selection metric: `roc_auc`

## Test metrics

| Metric | Train | Test |
|---|---:|---:|
| accuracy | 0.9604 | 0.7312 |
| precision | 0.9466 | 0.5714 |
| recall | 0.9254 | 0.5517 |
| f1 | 0.9358 | 0.5614 |
| roc_auc | 0.9933 | 0.7155 |
| brier | 0.0870 | 0.1872 |

## Caveats

- Train ROC-AUC is much higher than test — possible overfitting.
- Positive class is `Loan_Status=N` (reject / high risk), so the score is P(reject).
- Only 614 rows; metrics will move around if the split changes.

Plots: `reports/figures/loan_default_*.png`
