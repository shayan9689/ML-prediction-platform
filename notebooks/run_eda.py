"""Generate EDA figures and a findings summary for all tasks."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from src.config import FIGURES, REPORTS, TASKS, feature_columns
from src.preprocessing import DataLoader

sns.set_theme(style="whitegrid")


def run_eda(task_id: str) -> dict:
    loader = DataLoader(task_id)
    df = loader.load()
    task = loader.task
    FIGURES.mkdir(parents=True, exist_ok=True)
    numeric = [c for c in task["numeric_cols"] if c in df.columns]
    categorical = [c for c in task["categorical_cols"] if c in df.columns]
    target = task["target"]

    missing = df[feature_columns(task) + [target]].isna().mean().sort_values(ascending=False)
    missing = missing[missing > 0]

    fig, ax = plt.subplots(figsize=(8, 4))
    if missing.empty:
        ax.text(0.5, 0.5, "No missing values in modeled columns", ha="center", va="center")
        ax.axis("off")
    else:
        missing.plot(kind="barh", ax=ax, color="#b45309")
        ax.set_xlabel("Fraction missing")
    ax.set_title(f"{task_id}: missing values")
    fig.tight_layout()
    fig.savefig(FIGURES / f"eda_{task_id}_missing.png", dpi=120)
    plt.close(fig)

    show_num = numeric[:6]
    if show_num:
        fig, axes = plt.subplots(2, 3, figsize=(10, 6))
        axes = axes.ravel()
        for i, col in enumerate(show_num):
            sns.histplot(df[col].dropna(), ax=axes[i], kde=True, color="#2563eb")
            axes[i].set_title(col)
        for j in range(len(show_num), 6):
            axes[j].axis("off")
        fig.suptitle(f"{task_id}: numeric distributions")
        fig.tight_layout()
        fig.savefig(FIGURES / f"eda_{task_id}_numeric.png", dpi=120)
        plt.close(fig)

        corr = df[show_num + ([target] if pd.api.types.is_numeric_dtype(df[target]) else [])].corr(
            numeric_only=True
        )
        fig, ax = plt.subplots(figsize=(7, 5))
        sns.heatmap(corr, annot=True, fmt=".2f", cmap="RdBu_r", center=0, ax=ax)
        ax.set_title(f"{task_id}: correlation")
        fig.tight_layout()
        fig.savefig(FIGURES / f"eda_{task_id}_corr.png", dpi=120)
        plt.close(fig)

    if task["type"] == "regression":
        fig, ax = plt.subplots(figsize=(6, 4))
        sns.histplot(df[target], ax=ax, kde=True, color="#0f766e")
        ax.set_title(f"{task_id}: target distribution")
        fig.tight_layout()
        fig.savefig(FIGURES / f"eda_{task_id}_target.png", dpi=120)
        plt.close(fig)
        balance = {"min": float(df[target].min()), "max": float(df[target].max()), "mean": float(df[target].mean())}
    else:
        fig, ax = plt.subplots(figsize=(5, 4))
        df[target].astype(str).value_counts().plot(kind="bar", ax=ax, color="#7c3aed")
        ax.set_title(f"{task_id}: target balance")
        fig.tight_layout()
        fig.savefig(FIGURES / f"eda_{task_id}_target.png", dpi=120)
        plt.close(fig)
        balance = df[target].astype(str).value_counts(normalize=True).to_dict()

    if categorical:
        col = categorical[0]
        fig, ax = plt.subplots(figsize=(6, 4))
        df[col].astype(str).value_counts().head(8).plot(kind="barh", ax=ax, color="#0369a1")
        ax.set_title(f"{task_id}: {col} counts")
        fig.tight_layout()
        fig.savefig(FIGURES / f"eda_{task_id}_categorical.png", dpi=120)
        plt.close(fig)

    return {
        "rows": int(len(df)),
        "missing": missing.to_dict() if not missing.empty else {},
        "target": balance,
        "id_cols": task["id_cols"],
    }


def write_findings(summaries: dict) -> Path:
    lines = [
        "# EDA findings",
        "",
        "Generated in Phase 4 from `data/raw/` CSVs. Charts are in `reports/figures/eda_*.png`.",
        "",
    ]
    hp = summaries["house_price"]
    lines += [
        "## House price (regression)",
        "",
        f"- {hp['rows']:,} census-block rows. Target `median_house_value` is right-skewed and **capped at 500,001**.",
        "- `total_bedrooms` is the only modeled column with missing values (~1%).",
        "- `median_income` is the strongest numeric correlate of price; `ocean_proximity=INLAND` is typically cheaper.",
        "- No ID leakage. Latitude/longitude are location features, not IDs — keep them.",
        "- Modeling: log-transform is optional; tree models handle skew. Median impute + one-hot `ocean_proximity`.",
        "",
        "## Customer churn (classification)",
        "",
    ]
    ch = summaries["churn"]
    lines += [
        f"- {ch['rows']:,} customers. Churn is **imbalanced** ({ch['target']}).",
        "- `TotalCharges` has blank strings for tenure=0; coerced to NaN then median-imputed.",
        "- Drop `customerID` (pure identifier).",
        "- Contract type, tenure, and internet service are the usual drivers. Use class weights / `scale_pos_weight`.",
        "- Metric to optimize: ROC-AUC, then F1 on the Yes class.",
        "",
        "## Loan risk (probability)",
        "",
    ]
    ln = summaries["loan_default"]
    lines += [
        f"- Only {ln['rows']:,} rows — treat metrics as noisy.",
        f"- Target `Loan_Status` is imbalanced ({ln['target']}). Positive class for scoring is **N** (reject).",
        "- Missing: Credit_History, Self_Employed, LoanAmount, Dependents, Gender, term.",
        "- Drop `Loan_ID`. Credit_History is the classic high-signal field; do not leak future outcomes.",
        "- Metric: ROC-AUC + Brier score (probability quality).",
        "",
        "## Leakage checklist",
        "",
        "- Dropped: `customerID`, `Loan_ID`.",
        "- Housing has no post-sale features in this CSV.",
        "- Telco `TotalCharges` is historical billed amount, acceptable as a feature.",
        "",
    ]
    REPORTS.mkdir(parents=True, exist_ok=True)
    path = REPORTS / "findings.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def main() -> None:
    summaries = {task_id: run_eda(task_id) for task_id in TASKS}
    path = write_findings(summaries)
    print(json.dumps({k: v for k, v in summaries.items()}, indent=2, default=str))
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
