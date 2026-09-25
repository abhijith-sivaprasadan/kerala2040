"""QA for the reconciled March-2026 existing generation fleet."""
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def fleet():
    return json.loads(
        (ROOT / "data/evidence/assets/kerala_existing_fleet_2026_03_31.json")
        .read_text(encoding="utf-8")
    )


def test_state_hydro_reconciles_to_official_boundary(fleet):
    rows = fleet["state_hydro"]["stations"]
    arithmetic = sum(float(row["capacity_mw"]) for row in rows)
    target = float(fleet["state_hydro"]["reconciled_march_2026_total_mw"])
    tolerance = float(fleet["qa"]["state_hydro_reconciliation_tolerance_mw"])
    assert arithmetic == pytest.approx(2196.361)
    assert abs(arithmetic - target) <= tolerance
    assert target == pytest.approx(2196.36)


def test_state_hydro_bridge_from_2023_is_exact_at_published_precision(fleet):
    base = float(fleet["state_hydro"]["source_2023_total_mw"])
    additions = sum(
        float(row["capacity_mw"]) for row in fleet["state_hydro"]["additions_after_2023"]
    )
    assert base == pytest.approx(2090.36)
    assert additions == pytest.approx(106.0)
    assert base + additions == pytest.approx(2196.36)


def test_thermal_boundary_and_ntpc_units_reconcile(fleet):
    thermal = fleet["thermal"]
    assert sum(float(row["capacity_mw"]) for row in thermal["stations"]) == pytest.approx(
        thermal["reconciled_total_mw"]
    )
    ntpc = next(
        row for row in thermal["stations"] if row["name"] == "Rajiv Gandhi CCPP Kayamkulam"
    )
    assert sum(ntpc["units_mw"]) == pytest.approx(359.58)
    assert ntpc["units_mw"] == pytest.approx([115.2, 115.2, 129.18])


def test_bses_is_not_admitted_to_march_2026_base(fleet):
    bses = fleet["historical_location_based_crosschecks"]["cea_2025_bses_kochi"]
    assert bses["physical_location_capacity_mw"] == pytest.approx(174.0)
    assert bses["admitted_to_march_2026_base"] is False


def test_private_hydro_decomposition_reconciles(fleet):
    hydro = fleet["hydro_non_state"]
    assert hydro["march_2026_total_mw"] == pytest.approx(88.06)
    cpp = sum(row["capacity_mw"] for row in hydro["stations"] if row["category"] == "CPP")
    ipp = sum(row["capacity_mw"] for row in hydro["stations"] if row["category"] == "IPP")
    assert cpp == pytest.approx(33.50)
    assert ipp == pytest.approx(54.56)
    assert cpp + ipp == pytest.approx(88.06)
    assert hydro["status"].startswith("asset_level_capacity_decomposition_reconciled")


def test_distributed_solar_is_not_explicit_generator(fleet):
    distributed = fleet["distributed_solar_lt_1mw"]
    assert distributed["capacity_mw"] == pytest.approx(1912.33)
    assert distributed["pypsa_default"] == "embedded_in_net_grid_demand"
    assert distributed["explicit_generator"] is False


def test_storage_not_promoted_without_cod(fleet):
    storage = fleet["storage"]
    assert storage["operational_bess_mw"] is None
    assert storage["operational_bess_mwh"] is None
    assert storage["operational_psp_mw"] is None


def test_fleet_is_not_dispatch_ready(fleet):
    qa = fleet["qa"]
    assert qa["fleet_complete"] is False
    assert qa["dispatch_ready"] is False


def test_private_thermal_identity_reconciles(fleet):
    private = next(row for row in fleet["thermal"]["stations"] if row["sector"] == "private")
    assert private["name"] == "PCBL captive co-generation plant"
    assert private["capacity_mw"] == pytest.approx(17.0)


def test_private_wind_decomposition_reconciles_fy2024_25(fleet):
    wind = fleet["wind"]
    private = sum(row["capacity_mw"] for row in wind["stations"])
    assert private == pytest.approx(69.50)
    assert private + wind["state_ksebl"]["capacity_mw"] == pytest.approx(71.525)
    assert wind["qa"]["official_rounded_total_mw"] == pytest.approx(71.53)
