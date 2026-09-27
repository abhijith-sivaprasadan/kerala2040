"""Tests for the ERA5-sensitive hourly demand reconstruction."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

from kerala2040.weather_sensitive_load import (
    ANCHOR_ORDER,
    create_proxy_and_summary,
    interval_midpoint_hours,
)

ROOT = Path(__file__).resolve().parents[1]


def inputs():
    daily = pd.read_csv(ROOT / "data/external/sldc_fy2024_25/daily_balance.csv")
    extrema = pd.read_csv(
        ROOT / "data/external/sldc_fy2024_25/selected_intraday_extrema.csv"
    )
    weather = pd.read_csv(
        ROOT / "data/evidence/weather/era5_kerala_state_daily_all24_fy2024_25.csv"
    )
    cea = yaml.safe_load(
        (ROOT / "configs/cea_resource_adequacy_2025.yaml").read_text(encoding="utf-8")
    )
    return daily, extrema, weather, cea


def test_interval_midpoint():
    assert interval_midpoint_hours("22:30", "23:00") == 22.75
    assert interval_midpoint_hours("23:30", "00:00") == 23.75


def test_weather_sensitive_proxy_is_full_year_and_conserves_daily_energy():
    daily, extrema, weather, cea = inputs()
    proxy, hourly, summary = create_proxy_and_summary(
        daily,
        weather,
        extrema,
        bins=cea["hourly_demand_2024_25"]["frequency_bins"],
        cea_peak_mw=float(cea["actual_2024_25"]["peak_demand_mw"]),
    )
    assert proxy["classification"] == "proxy_reconstruction_not_measured_telemetry"
    assert len(proxy["records"]) == len(hourly) == 8760
    assert summary["daily_observations_measured"] == 354
    assert summary["daily_observations_interpolated"] == 11
    assert summary["daily_energy_conservation_max_abs_residual_mu"] < 1e-8
    assert set(summary["canonical_anchor_hours_from_training"]) == set(ANCHOR_ORDER)
    validation = summary["validation_against_selected_intraday_consumption_extrema"]
    assert validation["population"]["test_days"] >= 80
    assert validation["population"]["test_rows"] >= 300
    for label in ("old_fixed_curve", "calendar_anchor_model", "era5_anchor_model", "era5_hourly_curve"):
        assert np.isfinite(validation["overall"][label]["rmse_mw"])
        assert validation["overall"][label]["rmse_mw"] > 0


def test_proxy_keeps_missing_days_flagged():
    daily, extrema, weather, cea = inputs()
    proxy, hourly, summary = create_proxy_and_summary(
        daily,
        weather,
        extrema,
        bins=cea["hourly_demand_2024_25"]["frequency_bins"],
        cea_peak_mw=float(cea["actual_2024_25"]["peak_demand_mw"]),
    )
    flags = hourly.daily_energy_imputed.to_numpy(dtype=bool)
    assert flags.sum() == 11 * 24
    assert len(summary["interpolated_dates"]) == 11
    records = proxy["records"]
    assert sum(bool(r["daily_energy_imputed"]) for r in records) == 11 * 24
