"""Pydantic schemas for FastAPI."""

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field

TaskId = Literal["house_price", "churn", "loan_default"]


class HealthResponse(BaseModel):
    status: str
    models_loaded: list[str]


class FeatureField(BaseModel):
    name: str
    type: str
    required: bool = True
    options: list[Any] | None = None
    example: Any | None = None


class TaskInfo(BaseModel):
    id: str
    name: str
    type: str
    description: str
    features: list[FeatureField]


class TasksResponse(BaseModel):
    tasks: list[TaskInfo]


class PredictRequest(BaseModel):
    features: dict[str, Any] = Field(..., description="Feature name -> value")


class PredictResponse(BaseModel):
    prediction: float
    prediction_label: str | None
    confidence: float
    model_used: str
    task: str
    timestamp: datetime


class MetricsResponse(BaseModel):
    task: str
    best_model: str
    metrics: dict[str, Any]
    comparison: list[dict[str, Any]]
    feature_importance: list[dict[str, Any]]
    trained_at: str | None = None


class ErrorResponse(BaseModel):
    detail: str
