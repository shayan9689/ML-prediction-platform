# EDA findings

Generated in Phase 4 from `data/raw/` CSVs. Charts are in `reports/figures/eda_*.png`.

## House price (regression)

- 20,640 census-block rows. Target `median_house_value` is right-skewed and **capped at 500,001**.
- `total_bedrooms` is the only modeled column with missing values (~1%).
- `median_income` is the strongest numeric correlate of price; `ocean_proximity=INLAND` is typically cheaper.
- No ID leakage. Latitude/longitude are location features, not IDs — keep them.
- Modeling: log-transform is optional; tree models handle skew. Median impute + one-hot `ocean_proximity`.

## Customer churn (classification)

- 7,043 customers. Churn is **imbalanced** (No ~73% / Yes ~27%).
- `TotalCharges` has blank strings for tenure=0; coerced to NaN then median-imputed.
- Drop `customerID` (pure identifier).
- Contract type, tenure, and internet service are the usual drivers. Use class weights / `scale_pos_weight`.
- Metric to optimize: ROC-AUC, then F1 on the Yes class.

## Loan risk (probability)

- Only 614 rows — treat metrics as noisy.
- Target `Loan_Status` is imbalanced (Y ~69% / N ~31%). Positive class for scoring is **N** (reject).
- Missing: Credit_History, Self_Employed, LoanAmount, Dependents, Gender, term.
- Drop `Loan_ID`. Credit_History is the classic high-signal field; do not leak future outcomes.
- Metric: ROC-AUC + Brier score (probability quality).

## Leakage checklist

- Dropped: `customerID`, `Loan_ID`.
- Housing has no post-sale features in this CSV.
- Telco `TotalCharges` is historical billed amount, acceptable as a feature.
