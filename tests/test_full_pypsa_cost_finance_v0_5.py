"""QA for Full-PyPSA v0.5 cost/finance harmonisation."""
from math import sqrt
from pathlib import Path

import pytest

from kerala2040.full_pypsa_cost_finance import (
    annualised_cost_inr_per_kw_year,
    annuity,
    build_cost_finance_summary,
    load_cost_finance_suite,
)

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs/full_pypsa_cost_finance_v0_5.yaml"


@pytest.fixture
def suite():
    return load_cost_finance_suite(CONFIG)


def test_annuity_zero_and_positive_rate():
    assert annuity(0.0, 20) == pytest.approx(0.05)
    assert annuity(0.0908, 25) > 0.09


def test_annualised_cost_adds_fom():
    value = annualised_cost_inr_per_kw_year(
        41000,
        discount_rate=0.0908,
        lifetime_years=25,
        fixed_om_fraction_capex_per_year=0.01,
    )
    assert value > 41000 * annuity(0.0908, 25)


def test_v05_uses_single_real_price_basis(suite):
    assert suite["price_basis"]["basis"] == "real_2021_22_INR"
    assert suite["price_basis"]["inflation_applied"] is False


def test_current_cerc_finance_benchmark_is_explicit(suite):
    finance = suite["finance"]
    assert finance["discount_rate_real_fraction"] == pytest.approx(0.0908)
    assert finance["normative_debt_fraction"] == pytest.approx(0.70)
    assert finance["normative_equity_fraction"] == pytest.approx(0.30)
    assert finance["normative_loan_interest_fraction"] == pytest.approx(0.1071)
    assert finance["normative_loan_tenure_years"] == 15


def test_2030_solar_and_wind_benchmarks(suite):
    tech = suite["research_2030"]
    assert tech["solar_pv"]["capex_inr_per_kw"] == 41000
    assert tech["wind_onshore"]["capex_inr_per_kw"] == 60000
    assert tech["solar_pv"]["lifetime_years"] == 25
    assert tech["wind_onshore"]["lifetime_years"] == 25


def test_bess_is_four_hour_bracket_not_invented_midpoint(suite):
    bess = suite["research_2030"]["bess_4h"]
    assert bess["duration_hours"] == 4
    assert bess["capex_inr_per_kw_bracket"] == [47200, 82200]
    assert bess["round_trip_efficiency"] == pytest.approx(0.88)
    assert bess["charge_efficiency_symmetric"] == pytest.approx(sqrt(0.88))
    assert bess["charge_efficiency_symmetric"] * bess[
        "discharge_efficiency_symmetric"
    ] == pytest.approx(0.88)


def test_psp_and_post_2030_extrapolation_remain_blocked(suite):
    assert suite["research_2030"]["pumped_storage"]["capex_inr_per_kw"] is None
    assert (
        suite["research_2030"]["pumped_storage"][
            "expansion_cost_admitted_for_research"
        ]
        is False
    )
    assert suite["model_year_admission"][2035][
        "cost_finance_harmonised_for_research"
    ] is False
    assert suite["model_year_admission"][2040][
        "cost_finance_harmonised_for_research"
    ] is False


def test_summary_does_not_release_capacity_expansion(suite):
    summary = build_cost_finance_summary(suite)
    costs = summary["annualised_2030_inr_per_kw_year"]
    assert costs["solar_pv"] > 0
    assert costs["wind_onshore"] > costs["solar_pv"]
    assert costs["bess_4h_high"] > costs["bess_4h_low"]
    assert summary["capacity_expansion_research_2030_ready"] is False
    assert summary["validated_costs"] is False
