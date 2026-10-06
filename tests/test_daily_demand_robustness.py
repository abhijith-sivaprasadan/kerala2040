"""Tests for rolling daily-demand ML robustness v0.2."""
from __future__ import annotations

import numpy as np
import pandas as pd

from kerala2040.daily_demand_robustness import (
    FEATURE_GROUPS,
    _pct_reduction,
    monthly_rolling_folds,
)


def _table() -> pd.DataFrame:
    dates = pd.date_range("2024-04-02", "2025-03-31", freq="D")
    return pd.DataFrame(
        {
            "date": dates,
            "consumption_mu": 95.0 + np.linspace(0.0, 12.0, len(dates)),
        }
    )


def test_monthly_rolling_folds_are_nonoverlapping_and_past_only():
    folds = monthly_rolling_folds(_table())
    assert [fold.label for fold in folds] == [
        "2024-09",
        "2024-10",
        "2024-11",
        "2024-12",
        "2025-01",
        "2025-02",
        "2025-03",
    ]
    for fold in folds:
        assert fold.train_end < fold.holdout_start
        assert fold.train_rows >= 120
        assert fold.holdout_rows >= 28


def test_weather_reduction_sign_is_interpretable():
    assert _pct_reduction(10.0, 6.0) == 40.0
    assert _pct_reduction(10.0, 12.0) == -20.0


def test_feature_groups_preserve_calendar_and_separate_weather_families():
    calendar = set(FEATURE_GROUPS["calendar_only"])
    for name, features in FEATURE_GROUPS.items():
        assert calendar.issubset(features), name

    assert "temp_mean_c" in FEATURE_GROUPS["temperature"]
    assert "precip_mm_day" in FEATURE_GROUPS["precipitation"]
    assert "ghi_kwh_m2_day" in FEATURE_GROUPS["radiation"]
    assert "wind_mean_m_s" in FEATURE_GROUPS["wind"]
    assert "temp_mean_c" not in FEATURE_GROUPS["all_except_temperature"]
    assert "temp_mean_c" in FEATURE_GROUPS["all_weather"]
