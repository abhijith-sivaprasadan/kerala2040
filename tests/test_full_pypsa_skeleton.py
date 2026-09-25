"""Tests for the non-optimising full PyPSA network skeleton."""
from pathlib import Path

import pytest

from kerala2040.full_pypsa_skeleton import (
    build_full_pypsa_skeleton,
    load_selection,
    skeleton_summary,
)

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def network():
    selection = load_selection(ROOT / "configs/research_input_selection_v0_1.yaml")
    return build_full_pypsa_skeleton(selection)


def test_skeleton_reconciles_to_cea_main_capacity(network):
    summary = skeleton_summary(network)
    assert summary["generator_capacity_mw"] == pytest.approx(3221.30)
    assert summary["import_boundary_snapshot_mw"] == pytest.approx(4455.0)


def test_skeleton_has_no_double_counted_rooftop_generator(network):
    assert "distributed_solar_lt_1mw" not in network.generators.index
    assert network.meta["distributed_solar_explicit_generator"] is False
    assert network.meta["distributed_solar_treatment"] == "embedded_in_net_grid_demand"


def test_every_resource_is_disabled_until_temporal_inputs_exist(network):
    assert (network.generators["p_max_pu"] == 0.0).all()
    assert (network.links["p_max_pu"] == 0.0).all()
    assert len(network.loads) == 0


def test_no_unverified_storage_is_inserted(network):
    assert len(network.storage_units) == 0
    assert len(network.stores) == 0
    assert network.meta["operational_bess_admitted"] is False
    assert network.meta["operational_psp_admitted"] is False


def test_capacity_expansion_is_impossible_in_skeleton(network):
    assert not network.generators["p_nom_extendable"].any()
    assert not network.links["p_nom_extendable"].any()
    assert network.meta["capacity_expansion_enabled"] is False


def test_expected_structural_components_present(network):
    assert set(network.generators.index) == {
        "ksebl_hydro",
        "non_state_hydro",
        "brahmapuram",
        "kozhikode",
        "ntpc_kayamkulam",
        "private_thermal_residual",
        "kayankulam_floating_solar",
        "renewable_ge_1mw_residual",
    }
    assert set(network.buses.index) == {"kerala_system", "external_grid"}
