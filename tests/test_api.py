"""API tests. Skips predict assertions if models are not trained yet."""

import pytest
from fastapi.testclient import TestClient

from src.api.main import app, load_artifacts
from src.config import ARTIFACTS

client = TestClient(app)


@pytest.fixture(autouse=True)
def reload_models():
    load_artifacts()


def test_health():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"


def test_tasks_schema():
    res = client.get("/tasks")
    assert res.status_code == 200
    ids = {t["id"] for t in res.json()["tasks"]}
    assert ids == {"house_price", "churn", "loan_default"}


def test_unknown_task():
    res = client.post("/predict/not_a_task", json={"features": {}})
    assert res.status_code == 404


def test_missing_fields():
    if not (ARTIFACTS / "house_price_model.joblib").exists():
        pytest.skip("model artifacts not trained")
    res = client.post("/predict/house_price", json={"features": {"median_income": 4}})
    assert res.status_code == 422
    assert "Missing required fields" in res.json()["detail"]


def test_wrong_type():
    if not (ARTIFACTS / "house_price_model.joblib").exists():
        pytest.skip("model artifacts not trained")
    payload = {
        "longitude": -122.23,
        "latitude": 37.88,
        "housing_median_age": 41,
        "total_rooms": 880,
        "total_bedrooms": 129,
        "population": 322,
        "households": 126,
        "median_income": "not-a-number",
        "ocean_proximity": "NEAR BAY",
    }
    res = client.post("/predict/house_price", json={"features": payload})
    assert res.status_code == 422


def test_valid_house_price():
    if not (ARTIFACTS / "house_price_model.joblib").exists():
        pytest.skip("model artifacts not trained")
    payload = {
        "longitude": -122.23,
        "latitude": 37.88,
        "housing_median_age": 41,
        "total_rooms": 880,
        "total_bedrooms": 129,
        "population": 322,
        "households": 126,
        "median_income": 8.3252,
        "ocean_proximity": "NEAR BAY",
    }
    res = client.post("/predict/house_price", json={"features": payload})
    assert res.status_code == 200
    body = res.json()
    assert body["task"] == "house_price"
    assert isinstance(body["prediction"], float)
    assert 0 < body["confidence"] <= 1
