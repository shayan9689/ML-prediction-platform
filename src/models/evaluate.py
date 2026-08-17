"""Evaluation plots and markdown reports for a saved model."""

from __future__ import annotations

import json
from pathlib import Path

import joblib
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import ConfusionMatrixDisplay, RocCurveDisplay

from src.config import ARTIFACTS, FIGURES, REPORTS, get_task
from src.models.train import evaluate_estimator
from src.preprocessing import prepare_task


def _load_model(task_id: str):
    path = ARTIFACTS / f"{task_id}_model.joblib"
    if not path.exists():
        raise FileNotFoundError(f"Train first: missing {path}")
    return joblib.load(path)


def evaluate_task(task_id: str) -> dict:
    task = get_task(task_id)
    model = _load_model(task_id)
    bundle = prepare_task(task_id, persist=False)
    x_test, y_test = bundle["x_test"], bundle["y_test"]
    x_train, y_train = bundle["x_train"], bundle["y_train"]
    FIGURES.mkdir(parents=True, exist_ok=True)

    test_metrics = evaluate_estimator(task["type"], model, x_test, y_test)
    train_metrics = evaluate_estimator(task["type"], model, x_train, y_train)

    if task["type"] == "regression":
        pred = model.predict(x_test)
        _regression_plots(task_id, y_test.to_numpy(), pred)
    else:
        proba = model.predict_proba(x_test)[:, 1]
        pred = (proba >= 0.5).astype(int)
        _classification_plots(task_id, y_test.to_numpy(), pred, proba)

    _importance_plot(task_id)
    report = _write_report(task_id, task, train_metrics, test_metrics)
    print(json.dumps({"task": task_id, "test": test_metrics}, indent=2))
    return {"train": train_metrics, "test": test_metrics, "report": str(report)}


def _regression_plots(task_id: str, y_true, y_pred) -> None:
    resid = y_true - y_pred
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.scatter(y_pred, y_true, alpha=0.35, s=12)
    lo, hi = min(y_pred.min(), y_true.min()), max(y_pred.max(), y_true.max())
    ax.plot([lo, hi], [lo, hi], color="black", linewidth=1)
    ax.set_xlabel("Predicted")
    ax.set_ylabel("Actual")
    ax.set_title(f"{task_id}: predicted vs actual")
    fig.tight_layout()
    fig.savefig(FIGURES / f"{task_id}_pred_vs_actual.png", dpi=120)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.hist(resid, bins=40, color="#2563eb")
    ax.set_title(f"{task_id}: residuals")
    ax.set_xlabel("Actual - predicted")
    fig.tight_layout()
    fig.savefig(FIGURES / f"{task_id}_residuals.png", dpi=120)
    plt.close(fig)


def _classification_plots(task_id: str, y_true, y_pred, y_proba) -> None:
    fig, ax = plt.subplots(figsize=(5, 4))
    ConfusionMatrixDisplay.from_predictions(y_true, y_pred, ax=ax, colorbar=False)
    ax.set_title(f"{task_id}: confusion matrix")
    fig.tight_layout()
    fig.savefig(FIGURES / f"{task_id}_confusion_matrix.png", dpi=120)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(5, 4))
    RocCurveDisplay.from_predictions(y_true, y_proba, ax=ax)
    ax.set_title(f"{task_id}: ROC curve")
    fig.tight_layout()
    fig.savefig(FIGURES / f"{task_id}_roc.png", dpi=120)
    plt.close(fig)


def _importance_plot(task_id: str) -> None:
    meta_path = ARTIFACTS / f"{task_id}_metrics.json"
    if not meta_path.exists():
        return
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    items = meta.get("feature_importance") or []
    if not items:
        return
    labels = [i["feature"] for i in items][::-1]
    values = [i["importance"] for i in items][::-1]
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.barh(labels, values, color="#0f766e")
    ax.set_title(f"{task_id}: feature importance")
    ax.set_xlabel("Relative importance")
    fig.tight_layout()
    fig.savefig(FIGURES / f"{task_id}_feature_importance.png", dpi=120)
    plt.close(fig)


def _write_report(task_id: str, task: dict, train_m: dict, test_m: dict) -> Path:
    meta_path = ARTIFACTS / f"{task_id}_metrics.json"
    meta = json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.exists() else {}
    lines = [
        f"# Evaluation report — {task['name']} (`{task_id}`)",
        "",
        f"- Type: **{task['type']}**",
        f"- Best model: **{meta.get('best_model', 'unknown')}**",
        f"- Selection metric: `{task['select_metric']}`",
        "",
        "## Test metrics",
        "",
        "| Metric | Train | Test |",
        "|---|---:|---:|",
    ]
    for key in test_m:
        tr = train_m.get(key)
        te = test_m.get(key)
        lines.append(f"| {key} | {_fmt(tr)} | {_fmt(te)} |")
    gap_notes = []
    if task["type"] == "regression" and train_m.get("r2") and test_m.get("r2"):
        if train_m["r2"] - test_m["r2"] > 0.1:
            gap_notes.append("Train R2 is materially higher than test R2 — possible overfitting.")
    if task["type"] != "regression" and train_m.get("roc_auc") and test_m.get("roc_auc"):
        if train_m["roc_auc"] - test_m["roc_auc"] > 0.08:
            gap_notes.append("Train ROC-AUC is much higher than test — possible overfitting.")
    lines += ["", "## Caveats", ""]
    if gap_notes:
        lines.extend(f"- {n}" for n in gap_notes)
    else:
        lines.append("- Train vs test gap looks acceptable for a v1 demo model.")
    if task_id == "house_price":
        lines.append("- Target is capped at $500,001, which compresses residuals at the top end.")
        lines.append("- `total_bedrooms` has missing values; median impute is used at train and serve time.")
    if task_id == "churn":
        lines.append("- Churn is imbalanced (~27% Yes). Class weights / scale_pos_weight were used.")
        lines.append("- `customerID` is dropped to avoid identifier leakage.")
    if task_id == "loan_default":
        lines.append("- Positive class is `Loan_Status=N` (reject / high risk), so the score is P(reject).")
        lines.append("- Only 614 rows; metrics will move around if the split changes.")
    lines += ["", f"Plots: `reports/figures/{task_id}_*.png`", ""]
    REPORTS.mkdir(parents=True, exist_ok=True)
    path = REPORTS / f"evaluation_{task_id}.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def _fmt(value) -> str:
    if value is None:
        return "-"
    return f"{value:.4f}"


def evaluate_all() -> None:
    for task_id in ("house_price", "churn", "loan_default"):
        evaluate_task(task_id)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--task",
        choices=["house_price", "churn", "loan_default", "all"],
        default="all",
    )
    args = parser.parse_args()
    if args.task == "all":
        evaluate_all()
    else:
        evaluate_task(args.task)
