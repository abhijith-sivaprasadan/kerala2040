"""Build a machine-readable Kerala 110/220/320/400 kV graph from KSEBL public layers.

Input is the output of scripts/acquire_public_network_sources.py. The builder:
- keeps only public, in-service 110 kV and above feeder layers;
- snaps feeder endpoints to public substation/generating-station points;
- assigns districts from KSEBL's public district polygons;
- preserves source feeder length and independently derives geodesic geometry length;
- fails closed on unresolved 220 kV+ endpoints;
- reports rather than hides 110 kV endpoint gaps/ambiguities.

This is a physical-site topology graph. Transformer/busbar separation is added
later from public SLDs; this file must not be treated as an AC load-flow model.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import re
from collections import Counter, defaultdict, deque
from pathlib import Path
from typing import Any

from shapely.geometry import Point, shape

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ACQ = ROOT / "results/acquisition/network_public_v0_1"
DEFAULT_OUT = ROOT / "results/network/public_grid_graph_v0_1"

FEEDER_FILES = {
    110: "110kVFeederInservice_11.geojson",
    220: "220kVFeederInservice_13.geojson",
    320: "320kVFeederInservice_14.geojson",
    400: "400kVFeederInservice_16.geojson",
}
NODE_FILES = {
    "substation": "Substations_18.geojson",
    "generation": "GeneratingStations_17.geojson",
}
DISTRICT_FILE = "Districts_5.geojson"

CLASSIFICATION = "KSEBL_PUBLIC_GRID_GRAPH_V0_1_PHYSICAL_SITE_TOPOLOGY_NOT_POWER_FLOW_READY"


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _norm(value: Any) -> str:
    text = str(value or "").lower()
    text = text.replace("&", " and ")
    text = re.sub(r"\b(?:no\.?|number)\b", " ", text)
    text = re.sub(r"\b(?:i|ii|iii|iv|v)\b", " ", text)
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return " ".join(text.split())


def _tokens(value: Any) -> set[str]:
    stop = {
        "to", "kv", "kV", "sub", "station", "gs", "hep", "shep", "no",
        "pgcil", "ksebl", "line", "feeder",
    }
    return {token for token in _norm(value).split() if token not in stop and len(token) > 2}


def _name_overlap(a: Any, b: Any) -> float:
    aa, bb = _tokens(a), _tokens(b)
    if not aa or not bb:
        return 0.0
    return len(aa & bb) / len(aa | bb)


def _haversine_km(a: tuple[float, float], b: tuple[float, float]) -> float:
    lon1, lat1 = a
    lon2, lat2 = b
    radius = 6371.0088
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    h = (
        math.sin(dp / 2) ** 2
        + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    )
    return 2 * radius * math.atan2(math.sqrt(h), math.sqrt(1 - h))


def _line_parts(geometry: Any) -> list[list[tuple[float, float]]]:
    if geometry.is_empty:
        return []
    if geometry.geom_type == "LineString":
        return [list(geometry.coords)]
    if geometry.geom_type == "MultiLineString":
        return [list(part.coords) for part in geometry.geoms if not part.is_empty]
    return []


def _endpoints(geometry: Any) -> list[tuple[float, float]]:
    parts = _line_parts(geometry)
    if not parts or not parts[0] or not parts[-1]:
        return []
    return [tuple(parts[0][0]), tuple(parts[-1][-1])]


def _geometry_length_km(geometry: Any) -> float:
    total = 0.0
    for coords in _line_parts(geometry):
        for a, b in zip(coords, coords[1:], strict=False):
            total += _haversine_km(tuple(a), tuple(b))
    return total


def _node_id(kind: str, props: dict[str, Any], index: int) -> str:
    code = re.sub(r"[^A-Za-z0-9_-]+", "", str(props.get("Code") or ""))
    klass = re.sub(r"[^A-Za-z0-9_-]+", "", str(props.get("Class") or "NA"))
    prefix = "SS" if kind == "substation" else "GS"
    return f"{prefix}:{code or index}:{klass}"


def _district(point: Point, districts: list[tuple[str, Any]]) -> str | None:
    for name, polygon in districts:
        if polygon.contains(point) or polygon.touches(point):
            return name
    return None


def _build_nodes(geojson_dir: Path) -> list[dict[str, Any]]:
    district_obj = _load(geojson_dir / DISTRICT_FILE)
    districts: list[tuple[str, Any]] = []
    for feature in district_obj["features"]:
        props = feature.get("properties") or {}
        name = (
            props.get("DISTRICT")
            or props.get("District")
            or props.get("district")
            or props.get("Name")
            or props.get("NAME")
            or props.get("name")
        )
        districts.append((str(name or ""), shape(feature["geometry"])))

    nodes: list[dict[str, Any]] = []
    for kind, filename in NODE_FILES.items():
        obj = _load(geojson_dir / filename)
        for index, feature in enumerate(obj["features"]):
            props = feature.get("properties") or {}
            geom = shape(feature["geometry"])
            if geom.is_empty or geom.geom_type != "Point":
                continue
            node = {
                "node_id": _node_id(kind, props, index),
                "kind": kind,
                "location": str(props.get("Location") or ""),
                "code": str(props.get("Code") or ""),
                "voltage_class_kv": (
                    int(float(props["Class"]))
                    if str(props.get("Class") or "").replace(".", "", 1).isdigit()
                    else None
                ),
                "status": str(props.get("Status") or ""),
                "owner": str(props.get("Owner") or ""),
                "type": str(props.get("Type") or ""),
                "group": str(props.get("Group") or ""),
                "sld_html": str(props.get("SLD") or ""),
                "lon": float(geom.x),
                "lat": float(geom.y),
                "district": _district(geom, districts),
            }
            nodes.append(node)
    return nodes


def _match_endpoint(
    endpoint: tuple[float, float],
    feeder_name: str,
    feeder_voltage: int,
    nodes: list[dict[str, Any]],
) -> dict[str, Any]:
    ranked: list[tuple[float, float, int, dict[str, Any]]] = []
    for node in nodes:
        distance = _haversine_km(endpoint, (node["lon"], node["lat"]))
        overlap = _name_overlap(feeder_name, node["location"])
        class_bonus = int(node["voltage_class_kv"] == feeder_voltage)
        ranked.append((distance, -overlap, -class_bonus, node))
    ranked.sort(key=lambda row: (round(row[0], 6), row[1], row[2], row[3]["node_id"]))

    best_distance = ranked[0][0]
    near = [row for row in ranked if row[0] <= best_distance + 0.20]
    if len(near) > 1:
        near.sort(
            key=lambda row: (
                -_name_overlap(feeder_name, row[3]["location"]),
                -(row[3]["voltage_class_kv"] == feeder_voltage),
                row[0],
                row[3]["node_id"],
            )
        )
        chosen = near[0]
    else:
        chosen = ranked[0]

    node = chosen[3]
    threshold = 0.25 if feeder_voltage >= 220 else 1.0
    return {
        "node_id": node["node_id"] if chosen[0] <= threshold else None,
        "distance_km": float(chosen[0]),
        "threshold_km": threshold,
        "candidate_count_within_200m_of_best": len(near),
        "name_overlap": _name_overlap(feeder_name, node["location"]),
        "nearest_node_id": node["node_id"],
        "nearest_location": node["location"],
        "nearest_kind": node["kind"],
        "nearest_voltage_class_kv": node["voltage_class_kv"],
        "resolved": chosen[0] <= threshold,
    }


def _components(node_ids: set[str], edges: list[dict[str, Any]]) -> list[list[str]]:
    adjacency: dict[str, set[str]] = defaultdict(set)
    for edge in edges:
        a, b = edge["from_node_id"], edge["to_node_id"]
        if not a or not b:
            continue
        adjacency[a].add(b)
        adjacency[b].add(a)

    seen: set[str] = set()
    components: list[list[str]] = []
    for node_id in sorted(node_ids):
        if node_id in seen or node_id not in adjacency:
            continue
        component: list[str] = []
        queue = deque([node_id])
        seen.add(node_id)
        while queue:
            current = queue.popleft()
            component.append(current)
            for neighbour in adjacency[current]:
                if neighbour not in seen:
                    seen.add(neighbour)
                    queue.append(neighbour)
        components.append(sorted(component))
    components.sort(key=len, reverse=True)
    return components


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames: list[str] = []
    for row in rows:
        for key in row:
            if key not in fieldnames:
                fieldnames.append(key)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--acquisition", type=Path, default=DEFAULT_ACQ)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()

    geojson_dir = args.acquisition / "geojson"
    if not geojson_dir.is_dir():
        raise SystemExit(f"missing acquisition GeoJSON directory: {geojson_dir}")

    nodes = _build_nodes(geojson_dir)
    edges: list[dict[str, Any]] = []
    empty_geometry: list[dict[str, Any]] = []

    for voltage, filename in FEEDER_FILES.items():
        obj = _load(geojson_dir / filename)
        for index, feature in enumerate(obj["features"]):
            props = feature.get("properties") or {}
            geometry = shape(feature["geometry"])
            endpoints = _endpoints(geometry)
            edge_id = f"{voltage}:{str(props.get('Feeder') or index).strip()}"
            if len(endpoints) != 2:
                empty_geometry.append(
                    {
                        "edge_id": edge_id,
                        "voltage_kv": voltage,
                        "name": str(props.get("Name") or ""),
                        "source_file": filename,
                    }
                )
                continue

            feeder_name = str(props.get("Name") or "")
            a = _match_endpoint(endpoints[0], feeder_name, voltage, nodes)
            b = _match_endpoint(endpoints[1], feeder_name, voltage, nodes)
            source_length = props.get("Length_km")
            source_length = float(source_length) if source_length not in (None, "") else None
            geometry_length = _geometry_length_km(geometry)
            edges.append(
                {
                    "edge_id": edge_id,
                    "name": feeder_name,
                    "feeder_code": str(props.get("Feeder") or ""),
                    "voltage_kv": voltage,
                    "status": str(props.get("Status") or ""),
                    "owner": str(props.get("Owner") or ""),
                    "station_code": str(props.get("Station") or ""),
                    "source_file": filename,
                    "source_length_km": source_length,
                    "geometry_length_km": geometry_length,
                    "length_difference_km": (
                        geometry_length - source_length
                        if source_length is not None
                        else None
                    ),
                    "from_node_id": a["node_id"],
                    "to_node_id": b["node_id"],
                    "from_distance_km": a["distance_km"],
                    "to_distance_km": b["distance_km"],
                    "from_nearest_location": a["nearest_location"],
                    "to_nearest_location": b["nearest_location"],
                    "from_name_overlap": a["name_overlap"],
                    "to_name_overlap": b["name_overlap"],
                    "from_candidate_count": a["candidate_count_within_200m_of_best"],
                    "to_candidate_count": b["candidate_count_within_200m_of_best"],
                    "endpoint_resolution": (
                        "RESOLVED"
                        if a["resolved"] and b["resolved"]
                        else "UNRESOLVED"
                    ),
                }
            )

    edge_nodes = {
        node_id
        for edge in edges
        for node_id in (edge["from_node_id"], edge["to_node_id"])
        if node_id
    }
    active_nodes = [node for node in nodes if node["node_id"] in edge_nodes]

    unresolved_by_voltage = Counter(
        edge["voltage_kv"]
        for edge in edges
        if edge["endpoint_resolution"] != "RESOLVED"
    )
    resolved_by_voltage = Counter(
        edge["voltage_kv"]
        for edge in edges
        if edge["endpoint_resolution"] == "RESOLVED"
    )
    total_by_voltage = Counter(edge["voltage_kv"] for edge in edges)

    # The higher-voltage backbone must be exact enough for automatic admission.
    if any(unresolved_by_voltage.get(kv, 0) for kv in (220, 320, 400)):
        bad = {
            kv: unresolved_by_voltage.get(kv, 0)
            for kv in (220, 320, 400)
            if unresolved_by_voltage.get(kv, 0)
        }
        raise RuntimeError(f"unresolved 220 kV+ public feeder endpoints: {bad}")

    components = _components(edge_nodes, edges)
    degree = Counter()
    for edge in edges:
        if edge["from_node_id"] and edge["to_node_id"]:
            degree[edge["from_node_id"]] += 1
            degree[edge["to_node_id"]] += 1
    for node in active_nodes:
        node["degree"] = degree[node["node_id"]]

    district_counts = Counter(node["district"] or "UNASSIGNED" for node in active_nodes)
    graph = {
        "classification": CLASSIFICATION,
        "prepared_date": "2026-09-27",
        "source": {
            "publisher": "KSEBL Power System Engineering",
            "public_grid_version": "3.2",
            "as_of": "2026-03-31",
            "acquisition_directory": str(args.acquisition),
        },
        "scope": {
            "minimum_voltage_kv": 110,
            "in_service_only": True,
            "physical_site_graph": True,
            "transformer_busbar_model": False,
            "power_flow_ready": False,
        },
        "counts": {
            "all_public_nodes_loaded": len(nodes),
            "active_graph_nodes": len(active_nodes),
            "edges": len(edges),
            "empty_geometry_features": len(empty_geometry),
            "edges_by_voltage": dict(sorted(total_by_voltage.items())),
            "resolved_edges_by_voltage": dict(sorted(resolved_by_voltage.items())),
            "unresolved_edges_by_voltage": dict(sorted(unresolved_by_voltage.items())),
            "connected_components_with_edges": len(components),
            "largest_component_nodes": len(components[0]) if components else 0,
            "district_counts": dict(sorted(district_counts.items())),
        },
        "endpoint_policy": {
            "220_320_400_snap_threshold_km": 0.25,
            "110_snap_threshold_km": 1.0,
            "co_located_candidate_window_km": 0.20,
            "rule": "geometry distance first; co-located candidates are tie-broken by feeder-name token overlap and voltage class",
        },
        "warnings": [
            "A physical-site edge does not imply a same-voltage bus connection through a transformer.",
            "SLD-derived transformer and busbar structure must be added before AC/DC load-flow use.",
            "110 kV unresolved endpoints are retained as QA findings rather than guessed.",
            "Source Length_km is preserved separately from geometry-derived geodesic length.",
        ],
        "nodes": active_nodes,
        "edges": edges,
        "empty_geometry_features": empty_geometry,
        "components": components,
    }

    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "network_graph_110plus.json").write_text(
        json.dumps(graph, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    _write_csv(args.out / "network_nodes_110plus.csv", active_nodes)
    _write_csv(args.out / "network_edges_110plus.csv", edges)
    qa = {
        "classification": "KSEBL_PUBLIC_GRID_GRAPH_V0_1_QA",
        "all_220plus_edges_resolved": all(
            unresolved_by_voltage.get(kv, 0) == 0 for kv in (220, 320, 400)
        ),
        "edge_counts_by_voltage": dict(sorted(total_by_voltage.items())),
        "unresolved_edges_by_voltage": dict(sorted(unresolved_by_voltage.items())),
        "empty_geometry_features": empty_geometry,
        "active_graph_nodes": len(active_nodes),
        "connected_components_with_edges": len(components),
        "largest_component_nodes": len(components[0]) if components else 0,
        "max_endpoint_distance_km_by_voltage": {
            str(kv): max(
                max(edge["from_distance_km"], edge["to_distance_km"])
                for edge in edges
                if edge["voltage_kv"] == kv
            )
            for kv in sorted(total_by_voltage)
        },
        "power_flow_ready": False,
    }
    (args.out / "network_graph_qa.json").write_text(
        json.dumps(qa, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(qa, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
