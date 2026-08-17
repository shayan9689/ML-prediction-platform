# Datasets

Raw CSVs for the three v1 tasks. Downloaded in Phase 1. Do not commit large processed artifacts.

| File | Task | Dataset | Rows | Source |
|---|---|---|---|---|
| `raw/housing.csv` | `house_price` | California Housing | 20,640 | [ageron/handson-ml2](https://github.com/ageron/handson-ml2) |
| `raw/telco_churn.csv` | `churn` | IBM Telco Customer Churn | 7,043 | [IBM/telco-customer-churn-on-icp4d](https://github.com/IBM/telco-customer-churn-on-icp4d) |
| `raw/loan_prediction.csv` | `loan_default` | Loan Prediction III | 614 | [Analytics Vidhya / public mirror](https://github.com/shrikant-temburwar/Loan-Prediction-Dataset) |

IDs to drop at train time: `customerID`, `Loan_ID`.

## Phase 1 snapshot (verified)

**housing.csv**  
Columns: `longitude`, `latitude`, `housing_median_age`, `total_rooms`, `total_bedrooms`, `population`, `households`, `median_income`, `median_house_value`, `ocean_proximity`  
Missing: `total_bedrooms` = 207  
`ocean_proximity`: `<1H OCEAN` 9136, `INLAND` 6551, `NEAR OCEAN` 2658, `NEAR BAY` 2290, `ISLAND` 5  
Target `median_house_value`: min 14,999 / mean ~206,856 / max 500,001 (capped)

**telco_churn.csv**  
21 columns including `customerID` and target `Churn`  
No pandas-nulls; `TotalCharges` has 11 blank strings (tenure = 0 customers)  
Churn: No 5174 / Yes 1869 (imbalanced)

**loan_prediction.csv**  
13 columns including `Loan_ID` and target `Loan_Status` (`Y`/`N`)  
Missing: Gender 13, Married 3, Dependents 15, Self_Employed 32, LoanAmount 22, Loan_Amount_Term 14, Credit_History 50  
Status: Y 422 / N 192 (imbalanced)

These notes feed Phase 3 imputation and Phase 4 EDA (log-skew, class weights).
