"""Tests for the partial-exact March-2026 Kerala fleet reconciliation."""
import copy
from pathlib import Path

import pytest

from kerala2040.fleet_reconciliation import load_fleet, summarize_fleet, validate_fleet

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def fleet():
    return load_fleet(
        ROOT / "data/evidence/assets/kerala_fleet_reconciliation_2026_03_31.json"
    )


def test_exact_aggregate_fleet_reconciles(fleet):
    s = summarize_fleet(fleet)
    assert s.base_date == "2026-03-31"
    assert s.physical_capacity_mw == pytest.approx(5110.82)
    assert s.thermal_mw == pytest.approx(536.54)
    assert s.hydro_mw == pytest.approx(2284.67)
    assert s.wind_mw == pytest.approx(71.52)
    assert s.solar_grid_and_rooftop_mw == pytest.approx(2215.59)
    assert s.bio_power_mw == pytest.approx(2.50)


def test_hydro_residual_is_explicit_not_invented(fleet):
    hydro = fleet["hydro_reconciliation"]
    assert hydro["total"]["station_seed_mw"] == pytest.approx(2180.95)
    assert hydro["total"]["residual_unresolved_mw"] == pytest.approx(103.72)
    assert hydro["large_hydro"]["station_seed_mw"] == pytest.approx(2003.35)
    assert hydro["large_hydro"]["residual_unresolved_mw"] == pytest.approx(4.80)
    assert hydro["small_hydro"]["station_seed_mw"] == pytest.approx(177.60)
    assert hydro["small_hydro"]["residual_unresolved_mw"] == pytest.approx(98.92)


def test_wind_and_ground_solar_keep_residuals(fleet):
    assert fleet["wind"]["named_seed_mw"] == pytest.approx(29.03)
    assert fleet["wind"]["residual_unresolved_mw"] == pytest.approx(42.49)
    ground = fleet["solar"]["ground_mounted"]
    assert ground["named_seed_mw"] == pytest.approx(192.0)
    assert ground["residual_unresolved_mw"] == pytest.approx(148.26)


def test_historical_thermal_is_not_current_fleet(fleet):
    ids = {row["id"] for row in fleet["thermal"]}
    assert "bses_kochi" not in ids
    assert "kasaragod_power_thermal" not in ids
    excluded = {row["id"] for row in fleet["excluded_or_historical"]}
    assert {"bses_kochi", "kasaragod_power_thermal"} <= excluded


def test_rooftop_and_offgrid_are_not_double_counted(fleet):
    solar = fleet["solar"]
    assert solar["rooftop"]["representation"] == "embedded_in_net_grid_demand"
    assert solar["rooftop"]["explicit_dispatch_generator"] is False
    assert solar["off_grid_or_kusum_b"]["representation"] == "excluded_from_grid_dispatch"


def test_kasaragod_component_is_not_double_counted(fleet):
    named = fleet["solar"]["ground_mounted"]["named_seed"]
    parks = [row for row in named if row["id"] == "kasaragod_solar_park"]
    assert len(parks) == 1
    assert parks[0]["capacity_mw"] == pytest.approx(100.0)


def test_bad_micro_screw_portal_row_is_excluded(fleet):
    bad = next(
        row
        for row in fleet["excluded_or_historical"]
        if row["id"] == "poringalkuthu_micro_screw_bad_unit"
    )
    assert "11kW" in bad["reason"]
    assert "11 MW" in bad["reason"]


def test_fleet_remains_not_dispatch_ready(fleet):
    release = fleet["release"]
    assert release["exact_aggregate_fleet_reconciled"] is True
    assert release["station_level_fleet_complete"] is False
    assert release["unit_level_fleet_complete"] is False
    assert release["dispatch_ready"] is False
    assert release["capacity_expansion_ready"] is False


def test_erasing_residual_without_evidence_fails_closed(fleet):
    bad = copy.deepcopy(fleet)
    bad["hydro_reconciliation"]["total"]["residual_unresolved_mw"] = 0
    with pytest.raises(ValueError, match="total station seed and residual"):
        validate_fleet(bad)


def test_adding_bses_to_current_thermal_fails_closed(fleet):
    bad = copy.deepcopy(fleet)
    bad["thermal"].append(
        {
            "id": "bses_kochi",
            "capacity_mw": 157,
            "dispatch_admitted": False,
        }
    )
    with pytest.raises(ValueError, match="thermal rows"):
        validate_fleet(bad)
