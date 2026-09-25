"""Tests for Full-PyPSA adequacy-first proxy expansion v0.8."""
from pathlib import Path

import numpy as np
import pandas as pd

from kerala2040.full_pypsa_proxy_expansion import (
    _align_profiles,
    load_proxy_expansion_suite,
    solve_proxy_expansion_case,
)

ROOT = Path(__file__).resolve().parents[1]


def test_v08_suite_stays_proxy_and_non_recommendation():
    suite = load_proxy_expansion_suite(
        ROOT / "configs/full_pypsa_proxy_expansion_v0_8.yaml"
    )
    assert suite["release"]["research_proxy_capacity_expansion_counterfactual"] is True
    assert suite["release"]["total_system_cost_optimization"] is False
    assert suite["release"]["scenario_recommendation"] is False
    assert suite["objective"]["import_marginal_cost_inr_per_mwh"] is None


def test_v08_two_stage_builds_only_what_preserves_minimum_shortage():
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
    result = solve_proxy_expansion_case(
        residual_load_mw=residual,
        solar_profile=solar,
        wind_profile=wind,
        import_limit_mw=75.0,
        caps=caps,
        annualized_costs=costs,
        bess_duration_h=4.0,
        charge_efficiency=0.94,
        discharge_efficiency=0.94,
        unserved_tolerance_mwh=1e-6,
    )
    assert result["stage1_minimum_unserved_mwh"] < 1e-5
    assert result["stage2_unserved_mwh"] < 1e-4
    assert result["built"]["solar_combined_mw"] >= 0
    assert result["built"]["wind_onshore_mw"] >= 0
    assert result["built"]["bess_4h_power_mw"] >= 0
    assert result["built"]["solar_combined_mw"] <= 300.0 + 1e-6
    assert result["built"]["wind_onshore_mw"] <= 200.0 + 1e-6
    assert result["built"]["bess_4h_power_mw"] <= 50.0 + 1e-6


def test_v08_shortage_remains_when_candidate_caps_are_zero():
    hours = 24
    result = solve_proxy_expansion_case(
        residual_load_mw=np.full(hours, 100.0),
        solar_profile=np.zeros(hours),
        wind_profile=np.zeros(hours),
        import_limit_mw=60.0,
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
    assert abs(result["stage1_minimum_unserved_mwh"] - 960.0) < 1e-5
    assert abs(result["stage2_unserved_mwh"] - 960.0) < 1e-4
    assert result["built"]["solar_combined_mw"] == 0
    assert result["built"]["wind_onshore_mw"] == 0
    assert result["built"]["bess_4h_power_mw"] == 0


def test_v08_era5_half_hour_profile_aligns_to_all_ist_clock_hours(tmp_path):
    utc = pd.date_range("2024-04-01T00:00:00Z", periods=8760, freq="h")
    profile = pd.DataFrame(
        {
            "timestamp_ist": utc.tz_convert("Asia/Kolkata"),
            "solar_p_max_pu": np.full(8760, 0.2),
            "wind_p_max_pu_150m_niwe_anchored": np.full(8760, 0.3),
        }
    )
    path = tmp_path / "profile.parquet"
    profile.to_parquet(path, index=False)
    snapshots = pd.Series(
        pd.date_range("2024-04-01 00:00:00", periods=8760, freq="h")
    )
    solar, wind, diagnostics = _align_profiles(path, snapshots)
    assert len(solar) == 8760
    assert len(wind) == 8760
    assert np.allclose(solar, 0.2)
    assert np.allclose(wind, 0.3)
    assert diagnostics["cyclic_boundary_wrapped_local_hours"] == 6.0
    assert abs(diagnostics["solar_alignment_change_pct"]) < 1e-9
    assert abs(diagnostics["wind_alignment_change_pct"]) < 1e-9
