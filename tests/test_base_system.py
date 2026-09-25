"""Regression tests for the canonical March-2026 Kerala base system."""
from pathlib import Path

import copy
import pytest

from kerala2040.base_system import load_base_system, summarize_base_system, validate_base_system

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def base():
    return load_base_system(ROOT / "configs/base_system_2026_03_31.yaml")


def test_base_capacity_reconciles_exactly(base):
    s = summarize_base_system(base)
    assert s.base_date == "2026-03-31"
    assert s.thermal_mw == pytest.approx(536.54)
    assert s.hydro_mw == pytest.approx(2284.42)
    assert s.renewable_ge_1mw_mw == pytest.approx(400.34)
    assert s.cea_main_capacity_mw == pytest.approx(3221.30)
    assert s.solar_lt_1mw_mw == pytest.approx(1912.33)
    assert s.physical_arithmetic_capacity_mw == pytest.approx(5133.63)


def test_ownership_and_named_assets_reconcile(base):
    own = base["ownership_boundary_mw"]
    assert sum(x["main_table_total"] for x in own.values()) == pytest.approx(3221.30)
    assert sum(x["solar_lt_1mw"] for x in own.values()) == pytest.approx(1912.33)
    thermal = base["named_asset_crosschecks"]["thermal"]
    assert sum(x["accounting_mw"] for x in thermal) == pytest.approx(536.54)
    renew = base["named_asset_crosschecks"]["renewable_ge_1mw"]
    assert sum(x["accounting_mw"] for x in renew) == pytest.approx(400.34)


def test_rooftop_solar_cannot_be_double_counted(base):
    distributed = base["distributed_solar_boundary"]
    assert distributed["reported_capacity_mw"] == pytest.approx(1912.33)
    assert distributed["pypsa_treatment_default"] == "embedded_in_net_grid_demand"
    assert distributed["explicit_generator_allowed"] is False


def test_august_overlay_is_not_the_march_base(base):
    overlay = base["later_august_2026_renewable_overlay"]
    assert overlay["as_of"] == "2026-08-31"
    assert overlay["applied_to_base"] is False
    assert overlay["solar_mw"]["rooftop_including_pm_surya_ghar"] == pytest.approx(2259.50)


def test_unverified_storage_stays_null(base):
    storage = base["storage_boundary"]
    assert storage["operational_bess_power_mw"] is None
    assert storage["operational_bess_energy_mwh"] is None
    assert storage["operational_psp_power_mw"] is None


def test_base_cannot_self_promote(base):
    release = base["base_release"]
    assert release["structural_capacity_reconciled"] is True
    assert release["asset_level_fleet_reconciled"] is False
    assert release["chronological_dispatch_ready"] is False
    assert release["capacity_expansion_ready"] is False
    assert release["research_assumption_run_ready"] is False
    assert release["validated_run_ready"] is False


def test_wrong_arithmetic_fails_closed(base):
    bad = copy.deepcopy(base)
    bad["capacity_boundary_mw"]["cea_main_table"]["total"] += 1
    with pytest.raises(ValueError, match="main capacity"):
        validate_base_system(bad)


def test_silent_august_merge_fails_closed(base):
    bad = copy.deepcopy(base)
    bad["later_august_2026_renewable_overlay"]["applied_to_base"] = True
    with pytest.raises(ValueError, match="August 2026 overlay"):
        validate_base_system(bad)


def test_explicit_rooftop_with_net_demand_fails_closed(base):
    bad = copy.deepcopy(base)
    bad["distributed_solar_boundary"]["explicit_generator_allowed"] = True
    with pytest.raises(ValueError, match="sub-1-MW solar"):
        validate_base_system(bad)
