"""Tests for daily observed-demand ML v0.1 feature and evidence contract."""
from __future__ import annotations

import numpy as np
import pandas as pd

from kerala2040.daily_demand_ml import (
    FEATURES,
    aggregate_daily_weather,
    build_daily_feature_table,
    chronological_split,
    regression_metrics,
)


def _weather(days: int = 220) -> pd.DataFrame:
    times = pd.date_range("2024-04-01", periods=days * 24, freq="h", tz="UTC")
    rows = []
    points = ["a", "b", "c", "d", "e"]
    for p_i, point in enumerate(points):
        for hour, ts in enumerate(times):
            local_hour = ts.tz_convert("Asia/Kolkata").hour
            rows.append(
                {
                    "point": point,
                    "timestamp_utc": ts,
                    "temp_c": 27.0
                    + 2.0 * np.sin(2 * np.pi * local_hour / 24)
                    + p_i * 0.1,
                    "wind10_m_s": 3.0 + p_i * 0.05,
                    "ghi_wh_m2": 600.0 if 7 <= local_hour <= 17 else 0.0,
                    "precip_mm_h": 0.2 if hour % 97 == 0 else 0.0,
                }
            )
    return pd.DataFrame(rows)


def test_daily_weather_uses_exact_ist_days_and_expected_features():
    daily = aggregate_daily_weather(_weather(days=3))
    assert len(daily) >= 2
    assert {
        "temp_mean_c",
        "temp_max_c",
        "temp_min_c",
        "cooling_degree_hours_24c",
        "ghi_kwh_m2_day",
        "precip_mm_day",
    }.issubset(daily.columns)
    assert (daily["temp_max_c"] >= daily["temp_min_c"]).all()


def test_feature_table_joins_observed_target_without_reconstructing_target():
    weather = _weather(days=220)
    dates = pd.date_range("2024-04-02", periods=200, freq="D")
    observed = pd.DataFrame(
        {
            "date": dates,
            "consumption_mu": 95.0 + np.linspace(0, 8, len(dates)),
        }
    )
    table = build_daily_feature_table(observed, weather)
    assert len(table) == len(observed)
    assert table["consumption_mu"].equals(observed["consumption_mu"])
    assert not table[FEATURES].isna().any().any()


def test_chronological_split_never_leaks_holdout_backwards():
    dates = pd.date_range("2024-04-01", "2025-03-31", freq="D")
    frame = pd.DataFrame({"date": dates, "consumption_mu": 100.0})
    train, holdout = chronological_split(frame)
    assert train["date"].max() < pd.Timestamp("2025-01-01")
    assert holdout["date"].min() >= pd.Timestamp("2025-01-01")
    assert train["date"].max() < holdout["date"].min()


def test_regression_metrics_are_zero_for_perfect_prediction():
    y = np.array([1.0, 2.0, 4.0])
    metrics = regression_metrics(y, y)
    assert metrics["mae_mu"] == 0.0
    assert metrics["rmse_mu"] == 0.0
    assert metrics["correlation"] == 1.0
