"""Tests use authored synthetic dates, never private observations."""
import numpy as np
import pandas as pd
import pytest

from kerala2040.multiyear_daily_study import fixed_fiscal_year_design


def authored():
    dates = pd.date_range("2020-04-01", "2025-03-31", freq="D")
    return pd.DataFrame({
        "date": dates,
        "consumption_mu": 60 + 2 * np.sin(np.arange(len(dates)) / 10),
    })


def test_each_holdout_follows_its_training_dates():
    folds = fixed_fiscal_year_design(authored())
    assert len(folds) == 3
    assert [f["fiscal_year"] for f in folds] == ["2022-23", "2023-24", "2024-25"]
    for f in folds:
        assert f["train"]["date"].max() < f["test"]["date"].min()


def test_duplicate_date_fails():
    frame = pd.concat([authored(), authored().head(1)])
    with pytest.raises(ValueError, match="Duplicate"):
        fixed_fiscal_year_design(frame)


def test_missing_holdout_year_fails():
    frame = authored()
    frame = frame.loc[~frame["date"].between("2023-04-01", "2024-03-31")]
    with pytest.raises(ValueError, match="Insufficient"):
        fixed_fiscal_year_design(frame)
