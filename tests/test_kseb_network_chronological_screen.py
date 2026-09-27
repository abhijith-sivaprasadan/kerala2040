from __future__ import annotations

import numpy as np
import pandas as pd

from kerala2040.kseb_network_chronological_screen import (
    connected_components,
    identify_boundary_interfaces,
    spatialize_generation,
    transformer_capacity_for_dc_base,
)


def test_boundary_interface_requires_explicit_cross_district_edge() -> None:
    buses = [
        {
            "bus_id": "outside@400",
            "node_id": "outside",
            "location": "To external grid",
            "district": "",
            "voltage_kv": 400,
            "synthetic_junction": False,
        },
        {
            "bus_id": "inside@400",
            "node_id": "inside",
            "location": "Kerala station",
            "district": "Palakkad",
            "voltage_kv": 400,
            "synthetic_junction": False,
        },
        {
            "bus_id": "blank@110",
            "node_id": "blank",
            "location": "Unknown",
            "district": "",
            "voltage_kv": 110,
            "synthetic_junction": False,
        },
    ]
    lines = [
        {
            "line_id": "L1",
            "bus0": "outside@400",
            "bus1": "inside@400",
            "screening_s_nom_mva": 1000,
        },
        {
            "line_id": "L2",
            "bus0": "blank@110",
            "bus1": "inside@400",
            "screening_s_nom_mva": 100,
        },
    ]
    found = identify_boundary_interfaces(
        buses, lines, minimum_voltage_kv=220
    )
    assert len(found) == 1
    assert found[0]["bus_id"] == "outside@400"
    assert found[0]["allocation_weight"] == 1.0


def test_connected_components_include_isolated_bus() -> None:
    buses = {"a", "b", "c", "d"}
    lines = [{"bus0": "a", "bus1": "b"}]
    transformers = [{"bus0": "b", "bus1": "c"}]
    components, lookup = connected_components(buses, lines, transformers)
    assert components[0] == ["a", "b", "c"]
    assert components[1] == ["d"]
    assert lookup["a"] == lookup["c"]
    assert lookup["d"] != lookup["a"]


def test_generation_spatialization_keeps_unmapped_share_unlocated() -> None:
    hourly = pd.DataFrame(
        {
            "hydro_fixed_mw": [50.0, 100.0],
            "nonhydro_fixed_mw": [20.0, 40.0],
        }
    )
    generators = [
        {
            "asset_id": "h1",
            "technology": "hydro",
            "p_nom_mw": 50.0,
            "bus_id": "a",
        },
        {
            "asset_id": "n1",
            "technology": "thermal",
            "p_nom_mw": 25.0,
            "bus_id": "b",
        },
    ]
    dispatch, unlocated, stats = spatialize_generation(
        hourly,
        generators,
        official_hydro_mw=100.0,
        official_nonhydro_mw=100.0,
    )
    np.testing.assert_allclose(dispatch["h1"], [25.0, 50.0])
    np.testing.assert_allclose(dispatch["n1"], [5.0, 10.0])
    np.testing.assert_allclose(unlocated, [40.0, 80.0])
    assert stats["mapped_hydro_capacity_fraction"] == 0.5
    assert stats["mapped_nonhydro_capacity_fraction"] == 0.25


def test_transformer_capacity_prefers_source_then_incident_line_proxy() -> None:
    source = {
        "bus0": "a",
        "bus1": "b",
        "screening_s_nom_mva": "160",
        "screening_capacity_basis": "PSS",
    }
    cap, basis, backed = transformer_capacity_for_dc_base(
        source, {"a": [100.0], "b": [200.0]}, floor_mva=50.0
    )
    assert cap == 160.0
    assert basis == "PSS"
    assert backed is True

    missing = {
        "bus0": "a",
        "bus1": "b",
        "screening_s_nom_mva": "",
    }
    cap, basis, backed = transformer_capacity_for_dc_base(
        missing, {"a": [100.0], "b": [200.0]}, floor_mva=50.0
    )
    assert cap == 200.0
    assert "NOT_OPERATOR_RATING" in basis
    assert backed is False
