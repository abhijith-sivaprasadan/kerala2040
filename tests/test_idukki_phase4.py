"""Regression tests for Kerala2040 Idukki source-preserving phase-4 pilot."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

PATH = Path(__file__).resolve().parents[1] / "analysis" / "idukki_hydro_energy_phase4.py"
SPEC = importlib.util.spec_from_file_location("idukki_phase4", PATH)
assert SPEC and SPEC.loader
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)


def test_zero_2018_sldc_dates_and_source_bounds():
    assert mod.FIRST == "2019-08-06"
    assert mod.LAST == "2026-09-23"
    assert all(not (mod.FIRST <= start <= mod.LAST) for _, start, _, _ in mod.EVENTS if start.startswith("2018"))


def test_lag_1_uses_previous_calendar_day_not_previous_nonmissing_observation():
    observed = pd.Series([10, np.nan, 30], index=pd.date_range("2020-01-01", periods=3))
    lag = observed.shift(1)
    assert lag.iloc[1] == 10
    assert np.isnan(lag.iloc[2])
    assert observed.rolling(3, min_periods=3).sum().isna().all()


def test_wet_dry_water_energy_example_is_physics_only():
    r = mod.water_energy_sensitivity()
    assert r["no_verified_site_or_flood_operating_headroom"]
    assert abs(r["round_trip_efficiency_assumed"] - .765) < 1e-10
    assert r["pumping_input_gwh"] > r["generated_gwh"]
    with pytest.raises(ValueError):
        mod.water_energy_sensitivity(eta_pump=1.2)


def test_weather_requires_explicit_deaccumulation_and_ist_dates(tmp_path):
    source = pd.DataFrame({"date": ["2024-01-01"], "rainfall_mm": [5.],
                           "source_id": ["cds"], "spatial_support": ["catchment polygon"],
                           "precipitation_processing": ["naive_daily_sum"]})
    fp = tmp_path / "bad.csv"
    source.to_csv(fp, index=False)
    with pytest.raises(ValueError, match="deaccumulation"):
        mod.optional_weather(pd.DataFrame({"date": pd.to_datetime(["2024-01-01"])}), fp)


def test_blocked_model_refuses_sparse_data():
    columns = {"date": pd.date_range("2024-01-01", periods=8),
               "inflow_mcm_day_analysis": [1.] * 8,
               "inflow_lag1_mcm_day": [1.] * 8}
    columns.update({f"rain_lag{n}_mm": [1.] * 8 for n in mod.LAG_DAYS})
    r = mod.blocked_inflow_model(pd.DataFrame(columns))
    assert r["status"] == "insufficient_complete_cases"


def test_pairwise_correlation_excludes_missing_dates():
    x = pd.DataFrame({"date": pd.date_range("2021-01-01", periods=5),
                      "rain": [0, 1, None, 3, 4], "inflow": [0, 1, 2, None, 4]})
    r = mod.paired_correlation(x, "rain", "inflow", min_n=10)
    assert r["paired_days"] == 3
    assert r["pearson_r"] is None
