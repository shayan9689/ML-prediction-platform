"""Task configs: column lists, metrics, and file paths."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_RAW = ROOT / "data" / "raw"
ARTIFACTS = ROOT / "data" / "artifacts"
PROCESSED = ROOT / "data" / "processed"
FIGURES = ROOT / "reports" / "figures"
REPORTS = ROOT / "reports"

TASKS = {
    "house_price": {
        "id": "house_price",
        "name": "House Price",
        "type": "regression",
        "description": "Predict median house value in California census blocks.",
        "data_path": DATA_RAW / "housing.csv",
        "target": "median_house_value",
        "id_cols": [],
        "numeric_cols": [
            "longitude",
            "latitude",
            "housing_median_age",
            "total_rooms",
            "total_bedrooms",
            "population",
            "households",
            "median_income",
        ],
        "categorical_cols": ["ocean_proximity"],
        "positive_label": None,
        "select_metric": "r2",
        "select_greater_is_better": True,
        "feature_schema": [
            {"name": "longitude", "type": "number", "required": True, "example": -122.23},
            {"name": "latitude", "type": "number", "required": True, "example": 37.88},
            {"name": "housing_median_age", "type": "number", "required": True, "example": 41},
            {"name": "total_rooms", "type": "number", "required": True, "example": 880},
            {"name": "total_bedrooms", "type": "number", "required": True, "example": 129},
            {"name": "population", "type": "number", "required": True, "example": 322},
            {"name": "households", "type": "number", "required": True, "example": 126},
            {"name": "median_income", "type": "number", "required": True, "example": 8.3252},
            {
                "name": "ocean_proximity",
                "type": "select",
                "required": True,
                "options": ["<1H OCEAN", "INLAND", "NEAR OCEAN", "NEAR BAY", "ISLAND"],
                "example": "NEAR BAY",
            },
        ],
    },
    "churn": {
        "id": "churn",
        "name": "Customer Churn",
        "type": "classification",
        "description": "Predict whether a telco customer will leave.",
        "data_path": DATA_RAW / "telco_churn.csv",
        "target": "Churn",
        "id_cols": ["customerID"],
        "numeric_cols": ["tenure", "MonthlyCharges", "TotalCharges", "SeniorCitizen"],
        "categorical_cols": [
            "gender",
            "Partner",
            "Dependents",
            "PhoneService",
            "MultipleLines",
            "InternetService",
            "OnlineSecurity",
            "OnlineBackup",
            "DeviceProtection",
            "TechSupport",
            "StreamingTV",
            "StreamingMovies",
            "Contract",
            "PaperlessBilling",
            "PaymentMethod",
        ],
        "positive_label": "Yes",
        "select_metric": "roc_auc",
        "select_greater_is_better": True,
        "feature_schema": [
            {"name": "gender", "type": "select", "required": True, "options": ["Female", "Male"], "example": "Female"},
            {"name": "SeniorCitizen", "type": "select", "required": True, "options": [0, 1], "example": 0},
            {"name": "Partner", "type": "select", "required": True, "options": ["Yes", "No"], "example": "Yes"},
            {"name": "Dependents", "type": "select", "required": True, "options": ["Yes", "No"], "example": "No"},
            {"name": "tenure", "type": "number", "required": True, "example": 1},
            {"name": "PhoneService", "type": "select", "required": True, "options": ["Yes", "No"], "example": "No"},
            {
                "name": "MultipleLines",
                "type": "select",
                "required": True,
                "options": ["No phone service", "No", "Yes"],
                "example": "No phone service",
            },
            {
                "name": "InternetService",
                "type": "select",
                "required": True,
                "options": ["DSL", "Fiber optic", "No"],
                "example": "DSL",
            },
            {
                "name": "OnlineSecurity",
                "type": "select",
                "required": True,
                "options": ["No", "Yes", "No internet service"],
                "example": "No",
            },
            {
                "name": "OnlineBackup",
                "type": "select",
                "required": True,
                "options": ["Yes", "No", "No internet service"],
                "example": "Yes",
            },
            {
                "name": "DeviceProtection",
                "type": "select",
                "required": True,
                "options": ["No", "Yes", "No internet service"],
                "example": "No",
            },
            {
                "name": "TechSupport",
                "type": "select",
                "required": True,
                "options": ["No", "Yes", "No internet service"],
                "example": "No",
            },
            {
                "name": "StreamingTV",
                "type": "select",
                "required": True,
                "options": ["No", "Yes", "No internet service"],
                "example": "No",
            },
            {
                "name": "StreamingMovies",
                "type": "select",
                "required": True,
                "options": ["No", "Yes", "No internet service"],
                "example": "No",
            },
            {
                "name": "Contract",
                "type": "select",
                "required": True,
                "options": ["Month-to-month", "One year", "Two year"],
                "example": "Month-to-month",
            },
            {"name": "PaperlessBilling", "type": "select", "required": True, "options": ["Yes", "No"], "example": "Yes"},
            {
                "name": "PaymentMethod",
                "type": "select",
                "required": True,
                "options": [
                    "Electronic check",
                    "Mailed check",
                    "Bank transfer (automatic)",
                    "Credit card (automatic)",
                ],
                "example": "Electronic check",
            },
            {"name": "MonthlyCharges", "type": "number", "required": True, "example": 29.85},
            {"name": "TotalCharges", "type": "number", "required": True, "example": 29.85},
        ],
    },
    "loan_default": {
        "id": "loan_default",
        "name": "Loan Risk",
        "type": "probability",
        "description": "Score the probability that a loan is rejected / high risk.",
        "data_path": DATA_RAW / "loan_prediction.csv",
        "target": "Loan_Status",
        "id_cols": ["Loan_ID"],
        "numeric_cols": [
            "ApplicantIncome",
            "CoapplicantIncome",
            "LoanAmount",
            "Loan_Amount_Term",
            "Credit_History",
        ],
        "categorical_cols": [
            "Gender",
            "Married",
            "Dependents",
            "Education",
            "Self_Employed",
            "Property_Area",
        ],
        "positive_label": "N",
        "select_metric": "roc_auc",
        "select_greater_is_better": True,
        "feature_schema": [
            {"name": "Gender", "type": "select", "required": True, "options": ["Male", "Female"], "example": "Male"},
            {"name": "Married", "type": "select", "required": True, "options": ["Yes", "No"], "example": "Yes"},
            {"name": "Dependents", "type": "select", "required": True, "options": ["0", "1", "2", "3+"], "example": "0"},
            {
                "name": "Education",
                "type": "select",
                "required": True,
                "options": ["Graduate", "Not Graduate"],
                "example": "Graduate",
            },
            {"name": "Self_Employed", "type": "select", "required": True, "options": ["Yes", "No"], "example": "No"},
            {"name": "ApplicantIncome", "type": "number", "required": True, "example": 5849},
            {"name": "CoapplicantIncome", "type": "number", "required": True, "example": 0},
            {"name": "LoanAmount", "type": "number", "required": True, "example": 128},
            {"name": "Loan_Amount_Term", "type": "number", "required": True, "example": 360},
            {"name": "Credit_History", "type": "select", "required": True, "options": [1.0, 0.0], "example": 1.0},
            {
                "name": "Property_Area",
                "type": "select",
                "required": True,
                "options": ["Urban", "Semiurban", "Rural"],
                "example": "Urban",
            },
        ],
    },
}


def get_task(task_id: str) -> dict:
    if task_id not in TASKS:
        raise KeyError(f"Unknown task '{task_id}'. Choose from: {list(TASKS)}")
    return TASKS[task_id]


def feature_columns(task: dict) -> list[str]:
    return list(task["numeric_cols"]) + list(task["categorical_cols"])
