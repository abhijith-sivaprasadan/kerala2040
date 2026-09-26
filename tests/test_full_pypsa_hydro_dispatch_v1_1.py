"""Tests for daily-energy-constrained hydro dispatch v1.1."""
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from kerala2040.full_pypsa_hydro_dispatch import (
    load_hydro_dispatch_suite,
    solve_flexible_hydro_economic_case,
    validate_hydro_evidence,
)

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs/full_pypsa_hydro_dispatch_v1_1.yaml"


def test_v11_hydro_evidence_and_release_are_fail_closed():
    suite = load_hydro_dispatch_suite(CONFIG)
    evidence = validate_hydro_evidence(ROOT, suite)
    assert evidence["aggregate_capacity"]["march_2026_hydro_mw"] == 2284.42
    assert (
        evidence["station_unit_anchor"]["largest_verified_single_unit_mw"] == 130
    )
    assert suite["release"]["daily_energy_constrained_hydro_dispatch_ready"] is True
    assert suite["release"]["reservoir_model_ready"] is False
    assert suite["release"]["outage_chronology_validated"] is False


def test_v11_daily_hydro_energy_is_conserved_on_synthetic_day():
    pytest.importorskip("pypsa")
    pytest.importorskip("highspy")
    timestamps = pd.date_range("2025-04-01", periods=24, freq="h")
    target = pd.Series([1200.0], index=["2025-04-01"])
    result = solve_flexible_hydro_economic_case(
        timestamps=timestamps,
        demand_mw=np.full(24, 100.0),
        nonhydro_fixed_mw=np.full(24, 10.0),
        daily_hydro_targets_mwh=target,
        hydro_group_caps_mw={"test_hydro": 80.0},
        solar_profile=np.r_[np.zeros(6), np.ones(12) * 0.5, np.zeros(6)],
        wind_profile=np.full(24, 0.2),
        import_limit_mw=100.0,
        import_price_real_inr_per_mwh=4500.0,
        caps={
            "ground_solar_headroom_mw": 100.0,
            "floating_solar_headroom_mw": 50.0,
            "solar_total_headroom_mw": 150.0,
            "wind_headroom_mw": 100.0,
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
    assert result["hydro_generation_mwh"] == pytest.approx(1200.0, abs=1e-5)
    assert result["hydro_peak_mw"] <= 80.0 + 1e-6
    assert result["max_daily_hydro_energy_residual_mwh"] <= 1e-5


def test_v11_rejects_availability_below_daily_energy_feasibility():
    pytest.importorskip("pypsa")
    pytest.importorskip("highspy")
    timestamps = pd.date_range("2025-04-01", periods=24, freq="h")
    with pytest.raises(ValueError, match="daily energy exceeds"):
        solve_flexible_hydro_economic_case(
            timestamps=timestamps,
            demand_mw=np.full(24, 100.0),
            nonhydro_fixed_mw=np.full(24, 10.0),
            daily_hydro_targets_mwh=pd.Series([1200.0], index=["2025-04-01"]),
            hydro_group_caps_mw={"test_hydro": 40.0},
            solar_profile=np.zeros(24),
            wind_profile=np.zeros(24),
            import_limit_mw=100.0,
            import_price_real_inr_per_mwh=4500.0,
            caps={
                "ground_solar_headroom_mw": 0.0,
                "floating_solar_headroom_mw": 0.0,
                "solar_total_headroom_mw": 0.0,
                "wind_headroom_mw": 0.0,
                "bess_power_headroom_mw": 0.0,
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
