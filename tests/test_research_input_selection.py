"""QA for the first full-PyPSA research input selection."""
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def selection():
    return yaml.safe_load(
        (ROOT / "configs/research_input_selection_v0_1.yaml").read_text(encoding="utf-8")
    )


def test_selection_uses_canonical_march_base(selection):
    assert selection["base_date"] == "2026-03-31"
    assert selection["selected"]["base_system"]["status"] == "admitted_structural_base"


def test_selected_existing_capacity_matches_reconciled_boundary(selection):
    gen = selection["selected"]["existing_generation"]["representation"]
    assert gen["ksebl_hydro"]["capacity_mw"] == pytest.approx(2196.36)
    assert gen["non_state_hydro"]["capacity_mw"] == pytest.approx(88.06)
    assert gen["ksebl_thermal"]["brahmapuram_mw"] == pytest.approx(63.96)
    assert gen["ksebl_thermal"]["kozhikode_mw"] == pytest.approx(96.0)
    assert gen["ntpc_kayamkulam"]["capacity_mw"] == pytest.approx(359.58)
    assert sum(gen["ntpc_kayamkulam"]["units_mw"]) == pytest.approx(359.58)
    assert gen["private_thermal"]["capacity_mw"] == pytest.approx(17.0)
    assert gen["central_floating_solar"]["capacity_mw"] == pytest.approx(92.0)
    assert gen["renewable_ge_1mw_residual"]["capacity_mw"] == pytest.approx(308.34)
    assert gen["distributed_solar_lt_1mw"]["capacity_mw"] == pytest.approx(1912.33)


def test_unresolved_resources_cannot_dispatch(selection):
    gen = selection["selected"]["existing_generation"]["representation"]
    assert gen["ksebl_thermal"]["dispatch_enabled"] is False
    assert gen["ntpc_kayamkulam"]["dispatch_enabled"] is False
    assert gen["private_thermal"]["dispatch_enabled"] is False
    assert gen["central_floating_solar"]["dispatch_enabled"] is False
    assert gen["renewable_ge_1mw_residual"]["dispatch_enabled"] is False


def test_rooftop_stays_embedded_in_net_demand(selection):
    rooftop = selection["selected"]["existing_generation"]["representation"]["distributed_solar_lt_1mw"]
    assert rooftop["mode"] == "embedded_in_net_grid_demand"
    assert rooftop["explicit_generator"] is False


def test_no_storage_is_invented(selection):
    storage = selection["selected"]["storage"]
    assert storage["operational_bess_power_mw"] is None
    assert storage["operational_bess_energy_mwh"] is None
    assert storage["operational_psp_power_mw"] is None


def test_only_network_skeleton_is_ready(selection):
    release = selection["release"]
    assert release["network_skeleton_smoke_ready"] is True
    assert release["chronological_dispatch_ready"] is False
    assert release["capacity_expansion_ready"] is False
    assert release["publishable_scenario_results_ready"] is False


def test_optimisation_is_explicitly_forbidden(selection):
    forbidden = set(selection["forbidden_now"])
    assert "least-cost capacity expansion" in forbidden
    assert "S0-S5 result publication" in forbidden
    assert "storage sizing recommendations" in forbidden
