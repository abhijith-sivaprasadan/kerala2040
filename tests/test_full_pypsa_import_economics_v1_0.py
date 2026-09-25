"""Tests for Full-PyPSA import economics v1.0."""
from pathlib import Path

import numpy as np
import pytest

from kerala2040.full_pypsa_import_economics import (
    load_import_economics_suite,
    solve_import_economic_case,
    validate_import_evidence,
)

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs/full_pypsa_import_economics_v1_0.yaml"


def test_v10_price_and_forward_transfer_gates_are_fail_closed():
    suite = load_import_economics_suite(CONFIG)
    evidence = validate_import_evidence(ROOT, suite)
    assert suite["release"]["import_economic_sensitivity_ready"] is True
    assert suite["release"]["total_system_cost_optimization"] is False
    assert suite["forward_transfer_benchmarks"]["future_ATC_mw"] is None
    assert evidence["transfer_evidence"]["future_atc_mw"] is None


def test_v10_real_price_deflator_matches_source_arithmetic():
    suite = load_import_economics_suite(CONFIG)
    evidence = validate_import_evidence(ROOT, suite)
    ratio = evidence["price_basis"]["deflator"][
        "nominal_2023_24_to_real_2021_22_ratio"
    ]
    nominal = evidence["import_price_benchmarks"][
        "ksebl_weighted_average_purchase_fy2023_24"
    ]["nominal_inr_per_mwh"]
    real = suite["import_price_cases"][0]["real_2021_22_inr_per_mwh"]
    assert real == pytest.approx(nominal * ratio, abs=1e-9)


def test_v10_higher_import_price_cannot_raise_imports_in_simple_case():
    pytest.importorskip("pypsa")
    pytest.importorskip("highspy")
    hours = 24
    common = {
        "residual_load_mw": np.full(hours, 100.0),
        "solar_profile": np.r_[np.zeros(6), np.ones(12), np.zeros(6)],
        "wind_profile": np.full(hours, 0.4),
        "import_limit_mw": 100.0,
        "caps": {
            "ground_solar_headroom_mw": 200.0,
            "floating_solar_headroom_mw": 100.0,
            "solar_total_headroom_mw": 300.0,
            "wind_headroom_mw": 200.0,
            "bess_power_headroom_mw": 50.0,
        },
        "annualized_costs": {
            "solar_million_inr_per_mw_year": 4.0,
            "wind_million_inr_per_mw_year": 6.0,
            "bess_million_inr_per_mw_year": 8.0,
        },
        "bess_duration_h": 4.0,
        "charge_efficiency": 0.94,
        "discharge_efficiency": 0.94,
        "unserved_tolerance_mwh": 1e-6,
    }
    low = solve_import_economic_case(
        **common,
        import_price_real_inr_per_mwh=1000.0,
    )
    high = solve_import_economic_case(
        **common,
        import_price_real_inr_per_mwh=10000.0,
    )
    assert low["stage1_minimum_unserved_mwh"] == pytest.approx(
        high["stage1_minimum_unserved_mwh"], abs=1e-6
    )
    assert high["imports_mwh"] <= low["imports_mwh"] + 1e-5
