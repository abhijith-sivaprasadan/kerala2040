"""Tests for Full-PyPSA hydro flexibility v1.1."""
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from kerala2040.full_pypsa_hydro_flex_v1_1 import (
    load_hydro_flex_v11_suite,
    solve_hydro_flex_case,
)

ROOT = Path(__file__).resolve().parents[1]


def test_v11_release_is_fail_closed():
    suite = load_hydro_flex_v11_suite(ROOT / "configs/full_pypsa_hydro_flex_v1_1.yaml")
    assert suite["release"]["daily_energy_constrained_hydro_expansion_sensitivity_ready"] is True
    assert suite["release"]["reservoir_model_ready"] is False
    assert suite["release"]["station_outage_model_ready"] is False
    assert suite["release"]["validated_capacity_plan"] is False


def test_v11_synthetic_day_conserves_hydro_energy():
    pytest.importorskip("pypsa")
    pytest.importorskip("highspy")
    snapshots = pd.date_range("2025-01-01", periods=24, freq="h")
    result = solve_hydro_flex_case(
        residual_after_nonhydro_mw=np.full(24, 100.0),
        snapshots=snapshots,
        daily_hydro_mwh=pd.Series([1200.0], index=["2025-01-01"]),
        solar_profile=np.r_[np.zeros(6), np.ones(12), np.zeros(6)],
        wind_profile=np.full(24, 0.4),
        installed_hydro_mw=100.0,
        hydro_available_fraction=0.7,
        import_limit_mw=80.0,
        import_price_real_inr_per_mwh=4500.0,
        caps={
            "ground_solar_headroom_mw": 200.0,
            "floating_solar_headroom_mw": 100.0,
            "solar_total_headroom_mw": 300.0,
            "wind_headroom_mw": 200.0,
            "bess_power_headroom_mw": 50.0,
        },
        annualized_costs={
            "solar_million_inr_per_mw_year": 4.0,
            "wind_million_inr_per_mw_year": 6.0,
            "bess_million_inr_per_mw_year": 8.0,
        },
        bess_duration_h=4.0,
        charge_efficiency=0.94,
        discharge_efficiency=0.94,
        unserved_tolerance_mwh=1e-6,
    )
    assert result["hydro_generation_mwh"] == pytest.approx(1200.0, abs=1e-4)
    assert result["max_daily_hydro_energy_residual_mwh"] < 1e-4
    assert result["hydro_peak_mw"] <= 70.0 + 1e-6
