"""Reusable tabular preprocessing: impute, encode, scale, split, persist."""

from __future__ import annotations

from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from src.config import ARTIFACTS, PROCESSED, feature_columns, get_task


class DataLoader:
    """Read a task CSV and validate required columns."""

    def __init__(self, task_id: str):
        self.task_id = task_id
        self.task = get_task(task_id)

    def load(self, path: str | Path | None = None) -> pd.DataFrame:
        csv_path = Path(path) if path else Path(self.task["data_path"])
        if not csv_path.exists():
            raise FileNotFoundError(f"Dataset not found: {csv_path}")
        df = pd.read_csv(csv_path)
        df = self._coerce_types(df)
        self.validate(df)
        return df

    def _coerce_types(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        if "TotalCharges" in df.columns:
            df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce")
        if "Dependents" in df.columns and self.task_id == "loan_default":
            df["Dependents"] = df["Dependents"].astype(str).replace({"nan": np.nan})
        for col in self.task["numeric_cols"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")
        return df

    def validate(self, df: pd.DataFrame, require_target: bool = True) -> None:
        required = feature_columns(self.task)
        if require_target:
            required = required + [self.task["target"]]
        missing = [c for c in required if c not in df.columns]
        if missing:
            raise ValueError(f"Missing required columns for {self.task_id}: {missing}")

    def xy(self, df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series | None]:
        cols = feature_columns(self.task)
        drop = list(self.task["id_cols"])
        frame = df.drop(columns=[c for c in drop if c in df.columns], errors="ignore")
        x = frame[cols].copy()
        target = self.task["target"]
        y = None
        if target in frame.columns:
            y = frame[target].copy()
            if self.task["type"] != "regression":
                positive = self.task["positive_label"]
                y = (y.astype(str) == str(positive)).astype(int)
        return x, y


def build_preprocess_pipeline(numeric_cols: list[str], categorical_cols: list[str]) -> ColumnTransformer:
    transformers = []
    if numeric_cols:
        transformers.append(
            (
                "num",
                Pipeline(
                    [
                        ("imputer", SimpleImputer(strategy="median")),
                        ("scaler", StandardScaler()),
                    ]
                ),
                numeric_cols,
            )
        )
    if categorical_cols:
        transformers.append(
            (
                "cat",
                Pipeline(
                    [
                        ("imputer", SimpleImputer(strategy="most_frequent")),
                        (
                            "encoder",
                            OneHotEncoder(handle_unknown="ignore", sparse_output=False),
                        ),
                    ]
                ),
                categorical_cols,
            )
        )
    if not transformers:
        raise ValueError("Need at least one numeric or categorical column")
    return ColumnTransformer(transformers, remainder="drop")


def split_xy(
    x: pd.DataFrame,
    y: pd.Series,
    task_type: str,
    test_size: float = 0.15,
    val_size: float = 0.15,
    random_state: int = 42,
) -> tuple:
    stratify = y if task_type != "regression" else None
    x_train, x_test, y_train, y_test = train_test_split(
        x, y, test_size=test_size, random_state=random_state, stratify=stratify
    )
    val_ratio = val_size / (1 - test_size)
    stratify_train = y_train if task_type != "regression" else None
    x_train, x_val, y_train, y_val = train_test_split(
        x_train,
        y_train,
        test_size=val_ratio,
        random_state=random_state,
        stratify=stratify_train,
    )
    return x_train, x_val, x_test, y_train, y_val, y_test


def save_pipeline(pipeline: Pipeline | ColumnTransformer, task_id: str, name: str = "preprocess") -> Path:
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    path = ARTIFACTS / f"{task_id}_{name}.joblib"
    joblib.dump(pipeline, path)
    return path


def load_pipeline(task_id: str, name: str = "preprocess"):
    path = ARTIFACTS / f"{task_id}_{name}.joblib"
    if not path.exists():
        raise FileNotFoundError(f"Pipeline not found: {path}")
    return joblib.load(path)


def prepare_task(task_id: str, persist: bool = True) -> dict:
    loader = DataLoader(task_id)
    task = loader.task
    df = loader.load()
    x, y = loader.xy(df)
    x_train, x_val, x_test, y_train, y_val, y_test = split_xy(x, y, task["type"])
    preprocess = build_preprocess_pipeline(task["numeric_cols"], task["categorical_cols"])
    preprocess.fit(x_train)
    if persist:
        PROCESSED.mkdir(parents=True, exist_ok=True)
        # Full preprocess+model pipeline is saved in train.py; no separate artifact needed here.
    return {
        "task": task,
        "preprocess": preprocess,
        "x_train": x_train,
        "x_val": x_val,
        "x_test": x_test,
        "y_train": y_train,
        "y_val": y_val,
        "y_test": y_test,
    }
