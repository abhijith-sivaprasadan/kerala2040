"""Tests for the Full-PyPSA Idukki stateful reservoir pilot v1.3."""
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from kerala2040.full_pypsa_idukki_reservoir_v1_3 import (
    load_idukki_reservoir_v13_suite,
    load_idukki_water_balance_inputs,
    solve_idukki_reservoir_case,
)

ROOT = Path(__file__).resolve().parents[1]


def test_v13_release_is_fail_closed():
    suite = load_idukki_reservoir_v13_suite(
        ROOT / "configs/full_pypsa_idukki_reservoir_v1_3.yaml"
    )
    release = suite["release"]
    assert release["idukki_stateful_reservoir_pilot_ready"] is True
    assert release["reconstructed_net_water_balance_ready"] is True
    assert release["catchment_inflow_model_ready"] is False
    assert release["head_dependent_efficiency_ready"] is False
    assert release["cascade_model_ready"] is False
    assert release["full_reservoir_model_validated"] is False
    assert release["validated_capacity_plan"] is False


def test_v13_repository_water_balance_closes():
    suite = load_idukki_reservoir_v13_suite(
        ROOT / "configs/full_pypsa_idukki_reservoir_v1_3.yaml"
    )
    source = load_idukki_water_balance_inputs(ROOT, suite)
    assert source["observed_storage_days"] >= 350
    assert source["observed_generation_days"] >= 350
    assert source["interpolated_storage_days"] > 0
    assert source["interpolated_generation_days"] > 0
    assert source["derived_energy_equivalent_mwh_per_mcm"] == pytest.approx(
        1470.0,
        abs=2.0,
    )
    assert source["initial_storage_mcm"] == pytest.approx(649.727, abs=1e-6)
    assert source["terminal_storage_mcm"] == pytest.approx(689.054, abs=1e-6)
    assert abs(source["historical_replay_terminal_residual_mcm"]) < 1e-6
    assert len(source["net_water_balance_mcm_day"]) == 364


def test_v13_synthetic_stateful_reservoir_hits_terminal_stock():
    pytest.importorskip("pypsa")
    pytest.importorskip("highspy")

    snapshots = pd.date_range("2025-01-01", periods=48, freq="h")
    daily_index = pd.to_datetime(["2025-01-01", "2025-01-02"])
    result = solve_idukki_reservoir_case(
        residual_after_nonhydro_mw=np.full(48, 20.0),
        snapshots=snapshots,
        other_hydro_daily_mwh=pd.Series(
            [0.0, 0.0],
            index=["2025-01-01", "2025-01-02"],
        ),
        other_hydro_power_mw=10.0,
        idukki_power_mw=20.0,
        idukki_full_storage_mcm=10.0,
        idukki_initial_storage_mcm=5.0,
        idukki_terminal_storage_mcm=5.0,
        idukki_energy_equivalent_mwh_per_mcm=100.0,
        idukki_net_water_balance_mcm_day=pd.Series(
            [2.0, 2.0],
            index=daily_index,
        ),
        solar_profile=np.zeros(48),
        wind_profile=np.zeros(48),
        import_limit_mw=20.0,
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
    assert result["idukki_storage_terminal_mcm"] == pytest.approx(5.0, abs=1e-5)
    assert result["idukki_storage_min_mcm"] >= -1e-6
    assert result["idukki_storage_max_mcm"] <= 10.0 + 1e-6
    assert result["idukki_generation_peak_mw"] <= 20.0 + 1e-6
