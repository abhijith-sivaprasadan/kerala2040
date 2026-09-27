"""Integrity and conservation checks for the ERA5-sensitive hourly load proxy."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from kerala2040.chronological_screen import prepare_inputs
from kerala2040.weather_load_proxy import load_hourly_proxy

ROOT = Path(__file__).resolve().parents[1]
PROXY = (
    ROOT
    / "data/evidence/demand/hourly_load_proxy_era5_weather_sensitive_v2/manifest.json"
)


def test_weather_sensitive_proxy_loads_and_keeps_provenance():
    proxy = load_hourly_proxy(PROXY)
    assert proxy["classification"] == "proxy_reconstruction_not_measured_telemetry"
    assert proxy["profile_variant"] == "era5_weather_sensitive_sparse_extrema_v2"
    assert len(proxy["records"]) == 8760
    assert proxy["records"][0]["timestamp"].startswith("2024-04-01T00:00:00+05:30")
    assert proxy["records"][-1]["timestamp"].startswith("2025-03-31T23:00:00+05:30")
    values = [row["load_mw"] for row in proxy["records"]]
    assert abs(max(values) - 5923.326) < 0.001
    assert min(values) > 0
    assert {row["classification"] for row in proxy["records"]} == {
        "proxy_reconstruction"
    }


def test_weather_sensitive_proxy_conserves_observed_daily_energy():
    proxy = load_hourly_proxy(PROXY)
    qa = json.loads(
        (ROOT / "data/external/sldc_fy2024_25/qa_report.json").read_text(
            encoding="utf-8"
        )
    )
    daily = pd.read_csv(ROOT / "data/external/sldc_fy2024_25/daily_balance.csv")
    hourly, meta = prepare_inputs(
        proxy, daily, expected_missing_dates=qa["missing_dates"]
    )
    assert len(hourly) == 8760
    assert meta["observed_days"] == 354
    assert meta["imputed_days"] == 11
    assert int(hourly.groupby("date").daily_energy_imputed.first().sum()) == 11
    assert (
        hourly.loc[hourly.daily_energy_imputed, "date"].drop_duplicates().tolist()
        == qa["missing_dates"]
    )
    assert meta["observed_proxy_max_daily_residual_mu"] <= 1e-4
