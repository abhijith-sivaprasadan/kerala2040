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
    assert hydro["total"]["station_seed_mw"] == pytest.approx(2186.961)
    assert hydro["total"]["residual_unresolved_mw"] == pytest.approx(97.709)
    assert hydro["large_hydro"]["station_seed_mw"] == pytest.approx(2003.35)
    assert hydro["large_hydro"]["residual_unresolved_mw"] == pytest.approx(4.80)
    assert hydro["small_hydro"]["station_seed_mw"] == pytest.approx(183.611)
    assert hydro["small_hydro"]["residual_unresolved_mw"] == pytest.approx(92.909)


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


def test_portal_unit_errors_are_replaced_by_kseb_values(fleet):
    small = {row["id"]: row for row in fleet["hydro_station_seed"]}
    assert small["poringalkuthu_micro"]["capacity_mw"] == pytest.approx(0.011)
    assert small["perumthenaruvi_shep"]["capacity_mw"] == pytest.approx(6.0)
    corrections = fleet["source_corrections"]
    assert any("11 MW" in row["issue"] for row in corrections)
    assert any("capacity null" in row["issue"] for row in corrections)


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


def test_surviving_thermal_units_are_explicit(fleet):
    thermal = {row["id"]: row for row in fleet["thermal"]}
    assert sum(x["capacity_mw"] for x in thermal["ntpc_kayamkulam_rgccpp"]["units"]) == pytest.approx(359.58)
    assert [x["unit"] for x in thermal["ksebl_brahmapuram_bdpp"]["units"]] == ["1", "4", "5"]
    assert sum(x["capacity_mw"] for x in thermal["ksebl_brahmapuram_bdpp"]["units"]) == pytest.approx(63.96)
    assert [x["unit"] for x in thermal["ksebl_kozhikode_kdpp"]["units"]] == ["2", "3", "5", "6", "7", "8"]
    assert sum(x["capacity_mw"] for x in thermal["ksebl_kozhikode_kdpp"]["units"]) == pytest.approx(96.0)


def test_private_thermal_cpp_stays_unresolved_despite_candidates(fleet):
    row = next(x for x in fleet["thermal"] if x["id"] == "unresolved_private_thermal_cpp")
    assert row["capacity_mw"] == pytest.approx(17.0)
    assert all(x["admitted_to_17mw_bucket"] is False for x in row["candidate_evidence"])
