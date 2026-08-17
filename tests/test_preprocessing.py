"""Unit tests for the generic preprocessing pipeline."""

import numpy as np
import pandas as pd
import pytest
from sklearn.pipeline import Pipeline

from src.config import TASKS
from src.preprocessing import (
    DataLoader,
    build_preprocess_pipeline,
    prepare_task,
    split_xy,
)


def test_loader_rejects_missing_columns(tmp_path):
    path = tmp_path / "bad.csv"
    pd.DataFrame({"longitude": [1]}).to_csv(path, index=False)
    loader = DataLoader("house_price")
    with pytest.raises(ValueError, match="Missing required columns"):
        loader.load(path)


def test_pipeline_imputes_missing_and_encodes_unseen():
    numeric = ["a"]
    categorical = ["b"]
    pipe = build_preprocess_pipeline(numeric, categorical)
    train = pd.DataFrame({"a": [1.0, np.nan, 3.0], "b": ["x", "y", "x"]})
    pipe.fit(train)
    test = pd.DataFrame({"a": [np.nan], "b": ["unseen_label"]})
    out = pipe.transform(test)
    assert out.shape[0] == 1
    assert np.isfinite(out).all()


def test_split_stratifies_classification():
    x = pd.DataFrame({"f": range(100)})
    y = pd.Series([0] * 70 + [1] * 30)
    _, _, _, y_train, y_val, y_test = split_xy(x, y, "classification", random_state=0)
    for part in (y_train, y_val, y_test):
        rate = part.mean()
        assert 0.2 < rate < 0.4


def test_prepare_house_price_roundtrip():
    bundle = prepare_task("house_price", persist=False)
    assert len(bundle["x_train"]) > 0
    xt = bundle["preprocess"].transform(bundle["x_test"][:5])
    assert xt.shape[0] == 5
    assert np.isfinite(xt).all()


@pytest.mark.parametrize("task_id", list(TASKS))
def test_each_task_loads(task_id):
    loader = DataLoader(task_id)
    df = loader.load()
    x, y = loader.xy(df)
    assert y is not None
    assert len(x) == len(y)
    assert not x.empty
