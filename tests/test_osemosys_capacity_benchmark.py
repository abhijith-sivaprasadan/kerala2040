"""Tests for the independent TZ-OSeMOSYS capacity-expansion benchmark."""
from pathlib import Path

import numpy as np
import pytest

from kerala2040.full_pypsa_proxy_expansion import solve_proxy_expansion_case
from kerala2040.osemosys_capacity_benchmark import (
    BENCHMARK_CLASS,
    _demand_profile,
    load_benchmark_suite,
    solve_osemosys_three_stage,
)

ROOT = Path(__file__).resolve().parents[1]


def test_benchmark_config_stays_non_recommendation():
    suite = load_benchmark_suite(ROOT / "configs/osemosys_capacity_benchmark_v0_1.yaml")
    assert suite["classification"] == BENCHMARK_CLASS
    assert suite["release"]["cross_framework_benchmark"] is True
    assert suite["release"]["validated_capacity_plan"] is False
    assert suite["release"]["scenario_recommendation"] is False


def test_residual_demand_profile_is_energy_preserving_and_rejects_negative_load():
    residual = np.array([10.0, 20.0, 30.0, 40.0])
    total, profile = _demand_profile(residual, ["a", "b", "c", "d"])
    assert total == pytest.approx(100.0)
    assert sum(profile.values()) == pytest.approx(1.0)
    assert profile["d"] == pytest.approx(0.4)
    with pytest.raises(ValueError, match="non-negative"):
        _demand_profile(np.array([10.0, -1.0]), ["a", "b"])


def test_osemosys_matches_reference_lp_on_synthetic_24h_case():
    pytest.importorskip("tz.osemosys")
    hours = 24
    residual = np.full(hours, 100.0)
    solar = np.zeros(hours)
    solar[6:18] = 1.0
    wind = np.full(hours, 0.5)
    caps = {
        "ground_solar_headroom_mw": 200.0,
        "floating_solar_headroom_mw": 100.0,
        "solar_total_headroom_mw": 300.0,
        "wind_headroom_mw": 200.0,
        "bess_power_headroom_mw": 50.0,
    }
    costs = {
        "solar_million_inr_per_mw_year": 4.0,
        "wind_million_inr_per_mw_year": 6.0,
        "bess_million_inr_per_mw_year": 8.0,
    }
    kwargs = {
        "residual_load_mw": residual,
        "solar_profile": solar,
        "wind_profile": wind,
        "import_limit_mw": 75.0,
        "caps": caps,
        "costs": costs,
        "bess_duration_h": 4.0,
        "charge_efficiency": 0.94,
        "discharge_efficiency": 0.94,
        "unserved_tolerance_mwh": 1e-6,
    }
    reference = solve_proxy_expansion_case(
        annualized_costs=kwargs["costs"],
        **{key: value for key, value in kwargs.items() if key != "costs"},
    )
    independent = solve_osemosys_three_stage(**kwargs)

    assert independent["stage1"]["unserved_mwh"] == pytest.approx(
        reference["stage1_minimum_unserved_mwh"], abs=1e-4
    )
    assert independent["stage2"]["solar_mw"] == pytest.approx(
        reference["built"]["solar_combined_mw"], abs=1e-4
    )
    assert independent["stage2"]["wind_mw"] == pytest.approx(
        reference["built"]["wind_onshore_mw"], abs=1e-4
    )
    assert independent["stage2"]["bess_mw"] == pytest.approx(
        reference["built"]["bess_4h_power_mw"], abs=1e-4
    )
    assert independent["stage2"]["bess_energy_mwh"] == pytest.approx(
        4.0 * independent["stage2"]["bess_mw"], abs=1e-5
    )
    assert independent["stage3"]["imports_mwh"] == pytest.approx(
        reference["dispatch"]["imports_mwh"], abs=1e-3
    )
