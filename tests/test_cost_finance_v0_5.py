"""Regression tests for the v0.5 research cost/finance admission."""

from pathlib import Path

import pytest

from kerala2040.cost_finance import annuity, load_cost_finance

ROOT = Path(__file__).resolve().parents[1]


def test_annuity_matches_selected_cerc_finance_anchor():
    assert annuity(0.0908, 25) == pytest.approx(0.1024668966722117)


def test_v05_cost_finance_is_narrow_and_fail_closed():
    cfg = load_cost_finance(ROOT / "configs/research_cost_finance_v0_5.yaml")
    assert cfg["selection"]["model_year"] == 2030
    assert cfg["selection"]["price_basis"] == "real_2021_22_INR"
    assert cfg["release"]["research_2030_cost_finance_benchmark"] is True
    assert cfg["release"]["capacity_expansion_2030"] is False
    assert cfg["release"]["capacity_expansion_2035_2040"] is False
    assert cfg["release"]["economic_dispatch_with_import_prices"] is False


def test_procurement_average_is_not_promoted_to_import_marginal_price():
    cfg = load_cost_finance(ROOT / "configs/research_cost_finance_v0_5.yaml")
    rec = cfg["sources"]["rec_regulatory_parameters_kerala"]
    assert rec["kerala_fy2024_25_approved_power_procurement_cost_inr_per_kwh"] == 4.70
    assert rec["transmission_charges_included"] is False
    assert "accounting_crosscheck" in rec["role"]
    assert "marginal_import_price" in cfg["blocked"]
