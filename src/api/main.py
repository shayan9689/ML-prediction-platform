"""FastAPI app: health, task schemas, predict, metrics."""

from __future__ import annotations

import json
import os
import time
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.api.logging_config import log_event, persist_prediction, setup_logging
from src.api.supabase_sync import sync_model_metrics_to_supabase
from src.api.schemas import (
    HealthResponse,
    MetricsResponse,
    PredictRequest,
    PredictResponse,
    TaskInfo,
    TasksResponse,
)
from src.config import ARTIFACTS, TASKS, feature_columns, get_task

load_dotenv()

MODELS: dict[str, object] = {}
METRICS: dict[str, dict] = {}


def _models_dir() -> Path:
    return Path(os.getenv("MODELS_DIR", ARTIFACTS))


def load_artifacts() -> None:
    MODELS.clear()
    METRICS.clear()
    folder = _models_dir()
    for task_id in TASKS:
        model_path = folder / f"{task_id}_model.joblib"
        meta_path = folder / f"{task_id}_metrics.json"
        if model_path.exists():
            MODELS[task_id] = joblib.load(model_path)
        if meta_path.exists():
            METRICS[task_id] = json.loads(meta_path.read_text(encoding="utf-8"))


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    load_artifacts()
    sync_result = sync_model_metrics_to_supabase(_models_dir())
    log_event({"event": "startup", "models": list(MODELS), "supabase_metrics": sync_result})
    yield


app = FastAPI(
    title="ML Prediction Platform",
    version="1.0.0",
    description="Train-compare-serve API for house price, churn, and loan risk.",
    lifespan=lifespan,
)

origins = [o.strip() for o in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def limit_payload(request: Request, call_next):
    length = request.headers.get("content-length")
    if length and int(length) > 50_000:
        return JSONResponse(status_code=413, content={"detail": "Payload too large"})
    return await call_next(request)


@app.exception_handler(HTTPException)
async def http_error(request: Request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.get("/health", response_model=HealthResponse)
def health():
    return {"status": "ok", "models_loaded": sorted(MODELS)}


@app.get("/tasks", response_model=TasksResponse)
def list_tasks():
    tasks = []
    for task in TASKS.values():
        tasks.append(
            TaskInfo(
                id=task["id"],
                name=task["name"],
                type=task["type"],
                description=task["description"],
                features=task["feature_schema"],
            )
        )
    return {"tasks": tasks}


def _require_task(task: str) -> dict:
    try:
        return get_task(task)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.get("/models/{task}/metrics", response_model=MetricsResponse)
def model_metrics(task: str):
    _require_task(task)
    meta = METRICS.get(task)
    if not meta:
        raise HTTPException(status_code=503, detail=f"Metrics not loaded for '{task}'. Train the model first.")
    return {
        "task": task,
        "best_model": meta.get("best_model"),
        "metrics": meta.get("metrics", {}),
        "comparison": meta.get("comparison", []),
        "feature_importance": meta.get("feature_importance", []),
        "trained_at": meta.get("trained_at"),
    }


@app.post("/predict/{task}", response_model=PredictResponse)
def predict(task: str, body: PredictRequest):
    spec = _require_task(task)
    model = MODELS.get(task)
    if model is None:
        raise HTTPException(status_code=503, detail=f"Model not loaded for '{task}'. Train it first.")

    features = body.features
    required = feature_columns(spec)
    missing = [c for c in required if c not in features or features[c] in (None, "")]
    if missing:
        raise HTTPException(status_code=422, detail=f"Missing required fields: {missing}")

    row = {col: features[col] for col in required}
    yes_no = {"yes": 1, "true": 1, "1": 1, "no": 0, "false": 0, "0": 0}
    for col in spec["numeric_cols"]:
        raw = row[col]
        if isinstance(raw, str) and raw.strip().lower() in yes_no:
            row[col] = yes_no[raw.strip().lower()]
            continue
        try:
            row[col] = float(raw)
        except (TypeError, ValueError) as exc:
            raise HTTPException(status_code=422, detail=f"Field '{col}' must be numeric") from exc

    x = pd.DataFrame([row])
    started = time.perf_counter()
    try:
        result = _infer(spec, model, x)
    except Exception as exc:  # noqa: BLE001
        latency = int((time.perf_counter() - started) * 1000)
        persist_prediction(
            {"task": task, "input": row, "prediction": None, "latency_ms": latency, "error": str(exc)}
        )
        log_event({"event": "predict_error", "task": task, "error": str(exc), "latency_ms": latency})
        raise HTTPException(status_code=400, detail=f"Inference failed: {exc}") from exc

    latency = int((time.perf_counter() - started) * 1000)
    meta = METRICS.get(task, {})
    response = {
        "prediction": result["prediction"],
        "prediction_label": result["prediction_label"],
        "confidence": result["confidence"],
        "model_used": meta.get("best_model", "unknown"),
        "task": task,
        "timestamp": datetime.now(timezone.utc),
    }
    persist_prediction(
        {
            "task": task,
            "model_used": response["model_used"],
            "input": row,
            "prediction": {k: response[k] for k in ("prediction", "prediction_label", "confidence")},
            "latency_ms": latency,
            "error": None,
        }
    )
    log_event(
        {
            "event": "predict",
            "task": task,
            "model_used": response["model_used"],
            "prediction": response["prediction"],
            "latency_ms": latency,
        }
    )
    return response


def _infer(spec: dict, model, x: pd.DataFrame) -> dict:
    if spec["type"] == "regression":
        pred = float(model.predict(x)[0])
        mae = float(METRICS.get(spec["id"], {}).get("metrics", {}).get("mae", abs(pred) * 0.2))
        confidence = float(np.clip(1 - mae / (abs(pred) + mae + 1e-9), 0.05, 0.99))
        return {"prediction": pred, "prediction_label": None, "confidence": confidence}

    proba = float(model.predict_proba(x)[0, 1])
    if spec["id"] == "churn":
        label = "Yes" if proba >= 0.5 else "No"
        confidence = proba if label == "Yes" else 1 - proba
        return {"prediction": proba, "prediction_label": label, "confidence": float(confidence)}

    label = "high_risk" if proba >= 0.5 else "low_risk"
    return {"prediction": proba, "prediction_label": label, "confidence": float(proba)}
