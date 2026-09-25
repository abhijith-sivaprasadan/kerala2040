"""Tests for direct PyPSA equivalence checkpoint v0.9."""
from pathlib import Path

import numpy as np
import pytest

from kerala2040.full_pypsa_proxy_expansion import solve_proxy_expansion_case
from kerala2040.full_pypsa_pypsa_equivalence import (
    _compare_case,
    load_pypsa_equivalence_suite,
    solve_pypsa_equivalence_case,
)

ROOT = Path(__file__).resolve().parents[1]


def test_v09_suite_is_equivalence_only():
    suite = load_pypsa_equivalence_suite(
        ROOT / "configs/full_pypsa_pypsa_equivalence_v0_9.yaml"
    )
    assert suite["solver"]["engine"] == "PyPSA_Network_optimize"
    assert suite["release"]["direct_pypsa_equivalence_checkpoint"] is True
    assert suite["release"]["validated_capacity_plan"] is False
    assert suite["release"]["scenario_recommendation"] is False


def test_v09_direct_pypsa_matches_v08_on_synthetic_day():
    pytest.importorskip("pypsa")
    pytest.importorskip("highspy")

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
        "annualized_costs": costs,
        "bess_duration_h": 4.0,
        "charge_efficiency": 0.94,
        "discharge_efficiency": 0.94,
        "unserved_tolerance_mwh": 1e-6,
    }
    reference = solve_proxy_expansion_case(**kwargs)
    direct = solve_pypsa_equivalence_case(**kwargs)
    comparison = _compare_case(
        reference,
        direct,
        {
            "stage1_unserved_mwh_abs": 1e-4,
            "stage2_unserved_mwh_abs": 1e-4,
            "stage3_unserved_mwh_abs": 1e-4,
            "candidate_capacity_mw_abs": 1e-4,
            "annualized_investment_million_inr_per_year_abs": 1e-3,
            "stage3_imports_mwh_abs": 1e-3,
        },
    )
    assert comparison["passed"] is True


def test_v09_comparison_fails_outside_tolerance():
    reference = {
        "stage1_minimum_unserved_mwh": 0.0,
        "stage2_unserved_mwh": 0.0,
        "stage3_reporting_unserved_mwh": 0.0,
        "annualized_candidate_investment_million_inr_per_year": 100.0,
        "stage3_minimum_imports_mwh": 1000.0,
        "built": {
            "solar_combined_mw": 10.0,
            "wind_onshore_mw": 20.0,
            "bess_4h_power_mw": 30.0,
        },
    }
    direct = {
        **reference,
        "built": {**reference["built"], "solar_combined_mw": 11.0},
    }
    result = _compare_case(
        reference,
        direct,
        {
            "stage1_unserved_mwh_abs": 0.05,
            "stage2_unserved_mwh_abs": 0.05,
            "stage3_unserved_mwh_abs": 0.05,
            "candidate_capacity_mw_abs": 0.05,
            "annualized_investment_million_inr_per_year_abs": 0.5,
            "stage3_imports_mwh_abs": 2.0,
        },
    )
    assert result["passed"] is False
    assert result["checks"]["built.solar_combined_mw"]["passed"] is False
