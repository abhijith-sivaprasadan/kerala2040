"""Regression tests for geometry-resolved KSEBL network topology helpers."""

from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _load_graph_module():
    path = ROOT / "scripts/build_kseb_public_network_graph_v0_2.py"
    spec = importlib.util.spec_from_file_location("kseb_graph_v02", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


GRAPH = _load_graph_module()


def test_false_110kv_self_loop_releases_far_endpoint() -> None:
    base = {
        "voltage_kv": 110,
        "from_node_id": "SS:TVLA:110",
        "to_node_id": "SS:TVLA:110",
        "from_resolution_method": "PUBLIC_NODE_SNAP",
        "to_resolution_method": "PUBLIC_NODE_SNAP",
        "endpoint_resolution": "RESOLVED",
    }
    a = {"node_id": "SS:TVLA:110", "distance_km": 0.0}
    b = {"node_id": "SS:TVLA:110", "distance_km": 0.255}

    side = GRAPH._release_false_110kv_self_loop_endpoint(
        base, a, b, degenerate=False
    )
    assert side == "to"
    assert base["from_node_id"] == "SS:TVLA:110"
    assert base["to_node_id"] is None
    assert base["endpoint_resolution"] == "UNRESOLVED_SELF_LOOP_ENDPOINT"


def test_short_true_coincident_110kv_feature_is_not_rewritten() -> None:
    base = {
        "voltage_kv": 110,
        "from_node_id": "SS:X:110",
        "to_node_id": "SS:X:110",
        "endpoint_resolution": "RESOLVED",
    }
    a = {"node_id": "SS:X:110", "distance_km": 0.005}
    b = {"node_id": "SS:X:110", "distance_km": 0.010}

    side = GRAPH._release_false_110kv_self_loop_endpoint(
        base, a, b, degenerate=False
    )
    assert side is None
    assert base["from_node_id"] == "SS:X:110"
    assert base["to_node_id"] == "SS:X:110"


def test_220kv_endpoint_is_not_changed_by_110kv_rule() -> None:
    base = {
        "voltage_kv": 220,
        "from_node_id": "SS:X:220",
        "to_node_id": "SS:X:220",
        "endpoint_resolution": "RESOLVED",
    }
    a = {"node_id": "SS:X:220", "distance_km": 0.0}
    b = {"node_id": "SS:X:220", "distance_km": 0.2}

    side = GRAPH._release_false_110kv_self_loop_endpoint(
        base, a, b, degenerate=False
    )
    assert side is None
