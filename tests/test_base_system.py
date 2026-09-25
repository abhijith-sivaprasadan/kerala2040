"""Regression tests for the canonical March-2026 Kerala base system."""
import copy
from pathlib import Path

import pytest

from kerala2040.base_system import load_base_system, summarize_base_system, validate_base_system

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def base():
    return load_base_system(ROOT / "configs/base_system_2026_03_31.yaml")


def test_same_date_location_based_capacity_reconciles(base):
    s = summarize_base_system(base)
    assert s.base_date == "2026-03-31"
    assert s.thermal_mw == pytest.approx(536.54)
    assert s.large_hydro_mw == pytest.approx(2008.15)
    assert s.small_hydro_mw == pytest.approx(276.52)
    assert s.hydro_total_mw == pytest.approx(2284.67)
    assert s.wind_mw == pytest.approx(71.52)
    assert s.bio_power_mw == pytest.approx(2.50)
    assert s.solar_total_mw == pytest.approx(2215.59)
    assert s.renewable_total_mw == pytest.approx(4574.28)
    assert s.physical_capacity_total_mw == pytest.approx(5110.82)


def test_mnre_solar_categories_reconcile(base):
    solar = base["capacity_boundary_mw"]["renewable_location_based"]["solar"]
    assert solar["ground_mounted"] == pytest.approx(340.26)
    assert solar["rooftop_including_pm_surya_ghar"] == pytest.approx(1850.40)
    assert solar["off_grid_or_kusum_component_b"] == pytest.approx(24.93)
    assert (
        solar["ground_mounted"]
        + solar["rooftop_including_pm_surya_ghar"]
        + solar["hybrid_component"]
        + solar["off_grid_or_kusum_component_b"]
    ) == pytest.approx(solar["total"])


def test_thermal_named_and_residual_rows_reconcile(base):
    thermal = base["named_asset_crosschecks"]["thermal"]
    assert sum(x["accounting_mw"] for x in thermal) == pytest.approx(536.54)


def test_rooftop_solar_cannot_be_double_counted(base):
    distributed = base["distributed_solar_boundary"]
    assert distributed["rooftop_capacity_mw"] == pytest.approx(1850.40)
    assert distributed["rooftop_pypsa_treatment_default"] == "embedded_in_net_grid_demand"
    assert distributed["rooftop_explicit_generator_allowed"] is False
    assert distributed["off_grid_pypsa_treatment_default"] == "excluded_from_grid_dispatch"


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
    assert release["same_date_technology_capacity_reconciled"] is True
    assert release["asset_level_fleet_reconciled"] is False
    assert release["chronological_dispatch_ready"] is False
    assert release["capacity_expansion_ready"] is False
    assert release["research_assumption_run_ready"] is False
    assert release["validated_run_ready"] is False


def test_wrong_re_total_fails_closed(base):
    bad = copy.deepcopy(base)
    bad["capacity_boundary_mw"]["renewable_location_based"]["total"] += 1
    with pytest.raises(ValueError, match="renewable total"):
        validate_base_system(bad)


def test_silent_august_merge_fails_closed(base):
    bad = copy.deepcopy(base)
    bad["later_august_2026_renewable_overlay"]["applied_to_base"] = True
    with pytest.raises(ValueError, match="August 2026 overlay"):
        validate_base_system(bad)


def test_explicit_rooftop_with_net_demand_fails_closed(base):
    bad = copy.deepcopy(base)
    bad["distributed_solar_boundary"]["rooftop_explicit_generator_allowed"] = True
    with pytest.raises(ValueError, match="rooftop solar"):
        validate_base_system(bad)
