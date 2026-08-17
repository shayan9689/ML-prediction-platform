"""Train, compare, tune, and persist the best model per task."""

from __future__ import annotations

import json
import time
from datetime import datetime, timezone

import joblib
import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.metrics import (
    accuracy_score,
    brier_score_loss,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    precision_score,
    r2_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import GridSearchCV
from sklearn.pipeline import Pipeline
from xgboost import XGBClassifier, XGBRegressor

from src.config import ARTIFACTS, ROOT, get_task
from src.preprocessing import prepare_task

COMPARISON_CSV = ROOT / "reports" / "results_comparison.csv"


def _models(task_type: str, y_train: pd.Series) -> dict:
    if task_type == "regression":
        return {
            "ridge": Ridge(),
            "random_forest": RandomForestRegressor(
                n_estimators=120, max_depth=12, random_state=42, n_jobs=-1
            ),
            "xgboost": XGBRegressor(
                n_estimators=120,
                max_depth=6,
                learning_rate=0.1,
                subsample=0.8,
                colsample_bytree=0.8,
                random_state=42,
                n_jobs=-1,
                verbosity=0,
            ),
        }
    neg, pos = int((y_train == 0).sum()), int((y_train == 1).sum())
    spw = max(neg / max(pos, 1), 1.0)
    return {
        "logistic_regression": LogisticRegression(max_iter=400, class_weight="balanced"),
        "random_forest": RandomForestClassifier(
            n_estimators=120,
            max_depth=12,
            class_weight="balanced",
            random_state=42,
            n_jobs=-1,
        ),
        "xgboost": XGBClassifier(
            n_estimators=120,
            max_depth=5,
            learning_rate=0.1,
            subsample=0.8,
            colsample_bytree=0.8,
            scale_pos_weight=spw,
            random_state=42,
            n_jobs=-1,
            eval_metric="logloss",
            verbosity=0,
        ),
    }


def _param_grids(task_type: str) -> dict:
    if task_type == "regression":
        return {
            "ridge": {"model__alpha": [0.3, 1.0, 3.0]},
            "random_forest": {"model__max_depth": [8, 14]},
            "xgboost": {"model__max_depth": [4, 6], "model__learning_rate": [0.05, 0.1]},
        }
    return {
        "logistic_regression": {"model__C": [0.2, 1.0, 5.0]},
        "random_forest": {"model__max_depth": [8, 14]},
        "xgboost": {"model__max_depth": [3, 5], "model__learning_rate": [0.05, 0.1]},
    }


def regression_metrics(y_true, y_pred) -> dict:
    rmse = float(np.sqrt(mean_squared_error(y_true, y_pred)))
    return {
        "rmse": rmse,
        "mae": float(mean_absolute_error(y_true, y_pred)),
        "r2": float(r2_score(y_true, y_pred)),
    }


def classification_metrics(y_true, y_pred, y_proba) -> dict:
    return {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision": float(precision_score(y_true, y_pred, zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, zero_division=0)),
        "f1": float(f1_score(y_true, y_pred, zero_division=0)),
        "roc_auc": float(roc_auc_score(y_true, y_proba)),
        "brier": float(brier_score_loss(y_true, y_proba)),
    }


def evaluate_estimator(task_type: str, model, x, y) -> dict:
    if task_type == "regression":
        pred = model.predict(x)
        return regression_metrics(y, pred)
    proba = model.predict_proba(x)[:, 1]
    pred = (proba >= 0.5).astype(int)
    return classification_metrics(y, pred, proba)


class ModelTrainer:
    def __init__(self, task_id: str):
        self.task_id = task_id
        self.task = get_task(task_id)

    def _wrap(self, preprocess, estimator) -> Pipeline:
        return Pipeline([("preprocess", clone(preprocess)), ("model", clone(estimator))])

    def train(self) -> dict:
        bundle = prepare_task(self.task_id, persist=True)
        preprocess = bundle["preprocess"]
        x_train, y_train = bundle["x_train"], bundle["y_train"]
        x_val, y_val = bundle["x_val"], bundle["y_val"]
        x_test, y_test = bundle["x_test"], bundle["y_test"]
        x_fit = pd.concat([x_train, x_val], axis=0)
        y_fit = pd.concat([y_train, y_val], axis=0)

        scoring = "r2" if self.task["type"] == "regression" else "roc_auc"
        candidates = _models(self.task["type"], y_train)
        grids = _param_grids(self.task["type"])
        rows = []
        fitted = {}

        for name, estimator in candidates.items():
            pipe = self._wrap(preprocess, estimator)
            t0 = time.perf_counter()
            pipe.fit(x_train, y_train)
            elapsed = time.perf_counter() - t0
            val_metrics = evaluate_estimator(self.task["type"], pipe, x_val, y_val)
            train_metrics = evaluate_estimator(self.task["type"], pipe, x_train, y_train)
            fitted[name] = pipe
            rows.append(
                {
                    "task": self.task_id,
                    "model": name,
                    "stage": "baseline",
                    "train_seconds": round(elapsed, 3),
                    **{f"val_{k}": v for k, v in val_metrics.items()},
                    **{f"train_{k}": v for k, v in train_metrics.items()},
                }
            )

        metric_key = f"val_{self.task['select_metric']}"
        ranked = sorted(
            rows,
            key=lambda r: r[metric_key],
            reverse=self.task["select_greater_is_better"],
        )
        top_names = [r["model"] for r in ranked[:2]]

        tuned = {}
        for name in top_names:
            grid = grids.get(name)
            if not grid:
                continue
            search = GridSearchCV(
                self._wrap(preprocess, candidates[name]),
                grid,
                cv=3,
                scoring=scoring,
                n_jobs=-1,
                refit=True,
            )
            t0 = time.perf_counter()
            search.fit(x_fit, y_fit)
            elapsed = time.perf_counter() - t0
            tuned[name] = search.best_estimator_
            test_metrics = evaluate_estimator(
                self.task["type"], search.best_estimator_, x_test, y_test
            )
            rows.append(
                {
                    "task": self.task_id,
                    "model": name,
                    "stage": "tuned",
                    "train_seconds": round(elapsed, 3),
                    "best_params": json.dumps(search.best_params_),
                    **{f"test_{k}": v for k, v in test_metrics.items()},
                }
            )

        finalists = tuned or {ranked[0]["model"]: fitted[ranked[0]["model"]]}
        best_name, best_pipe, best_score = None, None, None
        test_table = []
        for name, pipe in finalists.items():
            metrics = evaluate_estimator(self.task["type"], pipe, x_test, y_test)
            train_m = evaluate_estimator(self.task["type"], pipe, x_fit, y_fit)
            score = metrics[self.task["select_metric"]]
            test_table.append({"model": name, **metrics, "train_metrics": train_m})
            better = best_score is None or (
                score > best_score
                if self.task["select_greater_is_better"]
                else score < best_score
            )
            if better:
                best_score, best_name, best_pipe = score, name, pipe

        importance = _feature_importance(best_pipe, bundle["x_train"].columns)
        ARTIFACTS.mkdir(parents=True, exist_ok=True)
        joblib.dump(best_pipe, ARTIFACTS / f"{self.task_id}_model.joblib")

        winner = next(r for r in test_table if r["model"] == best_name)
        metadata = {
            "task": self.task_id,
            "task_name": self.task["name"],
            "type": self.task["type"],
            "best_model": best_name,
            "select_metric": self.task["select_metric"],
            "metrics": {k: v for k, v in winner.items() if k not in {"model", "train_metrics"}},
            "comparison": [
                {k: v for k, v in r.items() if k != "train_metrics"} for r in test_table
            ],
            "train_vs_test": {
                "train": winner["train_metrics"],
                "test": {k: v for k, v in winner.items() if k not in {"model", "train_metrics"}},
            },
            "feature_importance": importance,
            "params": {
                k: _jsonable(v)
                for k, v in best_pipe.named_steps["model"].get_params().items()
            },
            "trained_at": datetime.now(timezone.utc).isoformat(),
            "n_train": int(len(x_fit)),
            "n_test": int(len(x_test)),
        }
        (ARTIFACTS / f"{self.task_id}_metrics.json").write_text(
            json.dumps(metadata, indent=2), encoding="utf-8"
        )

        comparison_df = pd.DataFrame(rows)
        COMPARISON_CSV.parent.mkdir(parents=True, exist_ok=True)
        if COMPARISON_CSV.exists():
            prev = pd.read_csv(COMPARISON_CSV)
            prev = prev[prev["task"] != self.task_id]
            comparison_df = pd.concat([prev, comparison_df], ignore_index=True)
        comparison_df.to_csv(COMPARISON_CSV, index=False)

        print(f"[{self.task_id}] best={best_name} {self.task['select_metric']}={best_score:.4f}")
        return metadata


def _jsonable(value):
    if isinstance(value, (np.floating, np.integer)):
        return value.item()
    if isinstance(value, np.ndarray):
        return value.tolist()
    return value


def _feature_importance(pipe: Pipeline, input_cols) -> list[dict]:
    model = pipe.named_steps["model"]
    preprocess = pipe.named_steps["preprocess"]
    try:
        names = list(preprocess.get_feature_names_out())
    except Exception:
        names = [str(c) for c in input_cols]
    if hasattr(model, "feature_importances_"):
        values = model.feature_importances_
    elif hasattr(model, "coef_"):
        values = np.abs(np.ravel(model.coef_))
    else:
        return []
    if len(values) != len(names):
        names = [f"f{i}" for i in range(len(values))]
    pairs = sorted(zip(names, values), key=lambda p: p[1], reverse=True)[:15]
    total = sum(v for _, v in pairs) or 1.0
    return [
        {"feature": n.replace("num__", "").replace("cat__", ""), "importance": float(v / total)}
        for n, v in pairs
    ]


def train_all(task_ids: list[str] | None = None) -> None:
    ids = task_ids or ["house_price", "churn", "loan_default"]
    for task_id in ids:
        ModelTrainer(task_id).train()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--task",
        choices=["house_price", "churn", "loan_default", "all"],
        default="all",
    )
    args = parser.parse_args()
    train_all(None if args.task == "all" else [args.task])
