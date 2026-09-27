"""Build an auditable Kerala 110/220/320/400 kV topology from KSEBL public layers.

v0.2 keeps raw KSEBL feeder features separate from the graph topology. It:
- gives every public feeder feature a unique deterministic source-edge id;
- snaps feeder endpoints to published substation/generating-station points;
- resolves 110-kV tap/LILO endpoints only when another published 110-kV feeder
  geometry is directly coincident (<=20 m);
- inserts synthetic feeder-junction nodes and splits the parent feeder logically;
- excludes degenerate zero-length source geometries from topology while preserving
  them in the QA/anomaly register;
- still fails closed on unresolved 220 kV+ endpoints.

This remains a physical topology/evidence graph, not an AC/DC load-flow model.
Transformer/bus voltage structure is promoted separately from public SLDs.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
from collections import Counter, defaultdict, deque
from itertools import pairwise
from pathlib import Path
from typing import Any

from pyproj import Transformer
from shapely.geometry import Point, shape
from shapely.ops import linemerge, transform

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ACQ = ROOT / "results/acquisition/network_public_v0_1"
DEFAULT_OUT = ROOT / "results/network/public_grid_graph_v0_2"

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

CLASSIFICATION = "KSEBL_PUBLIC_GRID_GRAPH_V0_2_GEOMETRY_RESOLVED_NOT_POWER_FLOW_READY"
PROJECT = Transformer.from_crs("EPSG:4326", "EPSG:32643", always_xy=True).transform
UNPROJECT = Transformer.from_crs("EPSG:32643", "EPSG:4326", always_xy=True).transform
HIGH_VOLTAGE_SNAP_KM = 0.25
LOW_VOLTAGE_SNAP_KM = 1.0
JUNCTION_PARENT_MAX_KM = 0.020
JUNCTION_CLUSTER_MAX_KM = 0.050
DEGENERATE_GEOMETRY_KM = 0.010


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _norm(value: Any) -> str:
    text = str(value or "").lower().replace("&", " and ")
    text = re.sub(r"\b(?:no\.?|number)\b", " ", text)
    text = re.sub(r"\b(?:i|ii|iii|iv|v)\b", " ", text)
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return " ".join(text.split())


def _tokens(value: Any) -> set[str]:
    stop = {"to", "kv", "sub", "station", "gs", "hep", "shep", "no", "pgcil", "ksebl", "line", "feeder"}
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
    h = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
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
        for a, b in pairwise(coords):
            total += _haversine_km(tuple(a), tuple(b))
    return total


def _node_id(kind: str, props: dict[str, Any], index: int) -> str:
    code = re.sub(r"[^A-Za-z0-9_-]+", "", str(props.get("Code") or ""))
    klass = re.sub(r"[^A-Za-z0-9_-]+", "", str(props.get("Class") or "NA"))
    prefix = "SS" if kind == "substation" else "GS"
    return f"{prefix}:{code or index}:{klass}"


def _load_districts(geojson_dir: Path) -> list[tuple[str, Any]]:
    obj = _load(geojson_dir / DISTRICT_FILE)
    districts: list[tuple[str, Any]] = []
    for feature in obj["features"]:
        props = feature.get("properties") or {}
        name = props.get("DISTRICT") or props.get("District") or props.get("district") or props.get("Name") or props.get("NAME") or props.get("name")
        districts.append((str(name or ""), shape(feature["geometry"])))
    return districts


def _district(point: Point, districts: list[tuple[str, Any]]) -> str | None:
    for name, polygon in districts:
        if polygon.contains(point) or polygon.touches(point):
            return name
    return None


def _build_nodes(geojson_dir: Path, districts: list[tuple[str, Any]]) -> list[dict[str, Any]]:
    raw_nodes: list[dict[str, Any]] = []
    for kind, filename in NODE_FILES.items():
        obj = _load(geojson_dir / filename)
        for index, feature in enumerate(obj["features"]):
            props = feature.get("properties") or {}
            geom = shape(feature["geometry"])
            if geom.is_empty or geom.geom_type != "Point":
                continue
            raw_nodes.append({
                "node_id": _node_id(kind, props, index),
                "kind": kind,
                "location": str(props.get("Location") or ""),
                "code": str(props.get("Code") or ""),
                "voltage_class_kv": int(float(props["Class"])) if str(props.get("Class") or "").replace(".", "", 1).isdigit() else None,
                "status": str(props.get("Status") or ""),
                "owner": str(props.get("Owner") or ""),
                "type": str(props.get("Type") or ""),
                "group": str(props.get("Group") or ""),
                "sld_html": str(props.get("SLD") or ""),
                "lon": float(geom.x),
                "lat": float(geom.y),
                "district": _district(geom, districts),
                "synthetic": False,
                "source_feature_index": index,
                "source_feature_count": 1,
                "source_locations": str(props.get("Location") or ""),
            })

    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for node in raw_nodes:
        grouped[node["node_id"]].append(node)

    nodes: list[dict[str, Any]] = []
    for node_id, group in grouped.items():
        if len(group) == 1:
            nodes.append(group[0])
            continue

        anchor = group[0]
        max_separation_km = max(
            _haversine_km(
                (anchor["lon"], anchor["lat"]),
                (other["lon"], other["lat"]),
            )
            for other in group[1:]
        )
        if max_separation_km > 0.10:
            raise RuntimeError(
                f"non-coincident public node identity collision for {node_id}: "
                f"{max_separation_km:.3f} km"
            )

        anchor["lon"] = sum(float(row["lon"]) for row in group) / len(group)
        anchor["lat"] = sum(float(row["lat"]) for row in group) / len(group)
        anchor["source_feature_count"] = len(group)
        anchor["source_feature_indices"] = ";".join(
            str(row["source_feature_index"]) for row in group
        )
        anchor["source_locations"] = " | ".join(
            dict.fromkeys(str(row["location"]) for row in group)
        )
        nodes.append(anchor)

    return nodes


def _match_endpoint(endpoint: tuple[float, float], feeder_name: str, feeder_voltage: int, nodes: list[dict[str, Any]]) -> dict[str, Any]:
    ranked: list[tuple[float, float, int, dict[str, Any]]] = []
    for node in nodes:
        distance = _haversine_km(endpoint, (node["lon"], node["lat"]))
        overlap = _name_overlap(feeder_name, node["location"])
        class_bonus = int(node["voltage_class_kv"] == feeder_voltage)
        ranked.append((distance, -overlap, -class_bonus, node))
    ranked.sort(key=lambda row: (round(row[0], 6), row[1], row[2], row[3]["node_id"]))
    chosen = ranked[0]
    best_distance = chosen[0]
    near = [row for row in ranked if row[0] <= best_distance + 0.20]
    if len(near) > 1:
        near.sort(key=lambda row: (-_name_overlap(feeder_name, row[3]["location"]), -(row[3]["voltage_class_kv"] == feeder_voltage), row[0], row[3]["node_id"]))
        chosen = near[0]
    node = chosen[3]
    threshold = HIGH_VOLTAGE_SNAP_KM if feeder_voltage >= 220 else LOW_VOLTAGE_SNAP_KM
    resolved = chosen[0] <= threshold
    return {
        "node_id": node["node_id"] if resolved else None,
        "distance_km": float(chosen[0]),
        "nearest_node_id": node["node_id"],
        "nearest_location": node["location"],
        "name_overlap": _name_overlap(feeder_name, node["location"]),
        "candidate_count_within_200m_of_best": len(near),
        "resolved": resolved,
        "resolution_method": "PUBLIC_NODE_SNAP" if resolved else "UNRESOLVED",
    }


def _components(node_ids: set[str], edges: list[dict[str, Any]]) -> list[list[str]]:
    adjacency: dict[str, set[str]] = defaultdict(set)
    for edge in edges:
        a, b = edge.get("from_node_id"), edge.get("to_node_id")
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


def _cluster(points: list[Any], max_m: float) -> list[list[int]]:
    parent = list(range(len(points)))
    def find(i: int) -> int:
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i
    def union(a: int, b: int) -> None:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra
    for i in range(len(points)):
        for j in range(i + 1, len(points)):
            if points[i].distance(points[j]) <= max_m:
                union(i, j)
    groups: dict[int, list[int]] = defaultdict(list)
    for i in range(len(points)):
        groups[find(i)].append(i)
    return list(groups.values())


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--acquisition", type=Path, default=DEFAULT_ACQ)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    geojson_dir = args.acquisition / "geojson"
    if not geojson_dir.is_dir():
        raise SystemExit(f"missing acquisition GeoJSON directory: {geojson_dir}")

    districts = _load_districts(geojson_dir)
    public_nodes = _build_nodes(geojson_dir, districts)
    nodes = list(public_nodes)
    source_edges: list[dict[str, Any]] = []
    runtime: dict[str, dict[str, Any]] = {}
    anomalies: list[dict[str, Any]] = []
    feeder_code_counts: Counter[tuple[int, str]] = Counter()

    for voltage, filename in FEEDER_FILES.items():
        obj = _load(geojson_dir / filename)
        for feature_index, feature in enumerate(obj["features"]):
            props = feature.get("properties") or {}
            feeder_code = str(props.get("Feeder") or "").strip()
            feeder_code_counts[(voltage, feeder_code)] += 1
            source_edge_id = f"{voltage}:{feeder_code or 'NOFEEDER'}:{feature_index:04d}"
            geometry = shape(feature["geometry"]) if feature.get("geometry") else None
            endpoints = _endpoints(geometry) if geometry is not None else []
            name = str(props.get("Name") or "")
            source_length = props.get("Length_km")
            source_length = float(source_length) if source_length not in (None, "") else None
            geometry_length = _geometry_length_km(geometry) if geometry is not None else 0.0
            base = {
                "source_edge_id": source_edge_id,
                "source_feature_index": feature_index,
                "name": name,
                "feeder_code": feeder_code,
                "voltage_kv": voltage,
                "status": str(props.get("Status") or ""),
                "owner": str(props.get("Owner") or ""),
                "station_code": str(props.get("Station") or ""),
                "source_file": filename,
                "source_length_km": source_length,
                "geometry_length_km": geometry_length,
            }
            if len(endpoints) != 2:
                base.update({"from_node_id": None, "to_node_id": None, "endpoint_resolution": "INVALID_GEOMETRY", "topology_admitted": False})
                source_edges.append(base)
                anomalies.append({"source_edge_id": source_edge_id, "anomaly": "INVALID_OR_EMPTY_GEOMETRY", "name": name, "voltage_kv": voltage})
                continue
            a = _match_endpoint(endpoints[0], name, voltage, public_nodes)
            b = _match_endpoint(endpoints[1], name, voltage, public_nodes)
            degenerate = geometry_length < DEGENERATE_GEOMETRY_KM
            base.update({
                "from_node_id": a["node_id"], "to_node_id": b["node_id"],
                "from_distance_km": a["distance_km"], "to_distance_km": b["distance_km"],
                "from_nearest_location": a["nearest_location"], "to_nearest_location": b["nearest_location"],
                "from_name_overlap": a["name_overlap"], "to_name_overlap": b["name_overlap"],
                "from_resolution_method": a["resolution_method"], "to_resolution_method": b["resolution_method"],
                "endpoint_resolution": "DEGENERATE_GEOMETRY" if degenerate else ("RESOLVED" if a["resolved"] and b["resolved"] else "UNRESOLVED"),
                "topology_admitted": not degenerate,
            })
            source_edges.append(base)
            runtime[source_edge_id] = {
                "geometry": geometry,
                "geometry_m": transform(PROJECT, geometry),
                "endpoints": endpoints,
                "record": base,
            }
            if degenerate:
                anomalies.append({"source_edge_id": source_edge_id, "anomaly": "DEGENERATE_GEOMETRY", "name": name, "voltage_kv": voltage, "geometry_length_km": geometry_length})

    # Resolve only previously unresolved 110-kV endpoints from direct coincidence
    # with another published 110-kV feeder geometry. No broad nearest-line snapping.
    unresolved: list[dict[str, Any]] = []
    admitted_110 = [e for e in source_edges if e["voltage_kv"] == 110 and e.get("topology_admitted") and e["source_edge_id"] in runtime]
    for edge in admitted_110:
        rt = runtime[edge["source_edge_id"]]
        for side, endpoint in (("from", rt["endpoints"][0]), ("to", rt["endpoints"][1])):
            if edge[f"{side}_node_id"]:
                continue
            point_m = transform(PROJECT, Point(endpoint))
            candidates: list[tuple[float, str]] = []
            for other in admitted_110:
                if other["source_edge_id"] == edge["source_edge_id"]:
                    continue
                d_km = point_m.distance(runtime[other["source_edge_id"]]["geometry_m"]) / 1000.0
                candidates.append((d_km, other["source_edge_id"]))
            candidates.sort(key=lambda x: (x[0], x[1]))
            best_distance, parent_id = candidates[0]
            if best_distance <= JUNCTION_PARENT_MAX_KM:
                unresolved.append({"edge_id": edge["source_edge_id"], "side": side, "point_m": point_m, "endpoint": endpoint, "parent_edge_id": parent_id, "distance_to_parent_km": best_distance})

    groups = _cluster([u["point_m"] for u in unresolved], JUNCTION_CLUSTER_MAX_KM * 1000.0) if unresolved else []
    parent_junctions: dict[str, set[str]] = defaultdict(set)
    junction_runtime: dict[str, Any] = {}
    for group in groups:
        xs = [unresolved[i]["point_m"].x for i in group]
        ys = [unresolved[i]["point_m"].y for i in group]
        mean_m = Point(sum(xs) / len(xs), sum(ys) / len(ys))
        mean_ll = transform(UNPROJECT, mean_m)
        digest = hashlib.sha1(f"110:{mean_ll.x:.6f}:{mean_ll.y:.6f}".encode()).hexdigest()[:10]
        junction_id = f"J110:{digest}"
        junction_runtime[junction_id] = mean_m
        nodes.append({
            "node_id": junction_id, "kind": "junction", "location": "110 kV feeder geometry junction",
            "code": "", "voltage_class_kv": 110, "status": "derived from in-service feeder geometry", "owner": "KSEBL",
            "type": "geometry junction", "group": "110 kV topology", "sld_html": "",
            "lon": float(mean_ll.x), "lat": float(mean_ll.y), "district": _district(mean_ll, districts),
            "synthetic": True, "junction_evidence_endpoint_count": len(group),
        })
        for i in group:
            u = unresolved[i]
            edge = runtime[u["edge_id"]]["record"]
            edge[f"{u['side']}_node_id"] = junction_id
            edge[f"{u['side']}_resolution_method"] = "FEEDER_GEOMETRY_JUNCTION"
            edge[f"{u['side']}_junction_parent_edge_id"] = u["parent_edge_id"]
            edge[f"{u['side']}_junction_distance_to_parent_km"] = u["distance_to_parent_km"]
            parent_junctions[u["parent_edge_id"]].add(junction_id)

    for edge in source_edges:
        if not edge.get("topology_admitted"):
            continue
        if edge.get("from_node_id") and edge.get("to_node_id"):
            edge["endpoint_resolution"] = "RESOLVED"

    unresolved_by_voltage = Counter(e["voltage_kv"] for e in source_edges if e.get("topology_admitted") and e.get("endpoint_resolution") != "RESOLVED")
    if any(unresolved_by_voltage.get(kv, 0) for kv in (220, 320, 400)):
        bad = {kv: unresolved_by_voltage.get(kv, 0) for kv in (220, 320, 400) if unresolved_by_voltage.get(kv, 0)}
        raise RuntimeError(f"unresolved 220 kV+ public feeder endpoints: {bad}")

    topology_edges: list[dict[str, Any]] = []
    split_failures: list[dict[str, Any]] = []
    for edge in source_edges:
        if not edge.get("topology_admitted") or not edge.get("from_node_id") or not edge.get("to_node_id"):
            continue
        rt = runtime[edge["source_edge_id"]]
        merged = linemerge(rt["geometry"]) if rt["geometry"].geom_type == "MultiLineString" else rt["geometry"]
        junction_ids = sorted(parent_junctions.get(edge["source_edge_id"], set()))
        if junction_ids and merged.geom_type != "LineString":
            split_failures.append({"source_edge_id": edge["source_edge_id"], "anomaly": "PARENT_GEOMETRY_NOT_MERGEABLE", "geometry_type": merged.geom_type})
            junction_ids = []
        line_m = transform(PROJECT, merged) if merged.geom_type == "LineString" else None
        points: list[tuple[float, str, str]] = [(0.0, edge["from_node_id"], "source_endpoint")]
        if line_m is not None:
            for jid in junction_ids:
                pos = float(line_m.project(junction_runtime[jid]))
                if 5.0 < pos < max(5.0, line_m.length - 5.0):
                    points.append((pos, jid, "geometry_junction"))
        end_pos = float(line_m.length) if line_m is not None else max(edge["geometry_length_km"] * 1000.0, 1.0)
        points.append((end_pos, edge["to_node_id"], "source_endpoint"))
        points.sort(key=lambda x: (x[0], x[1]))
        # Remove accidental duplicate locations/nodes at the same linear position.
        cleaned: list[tuple[float, str, str]] = []
        for item in points:
            if cleaned and abs(item[0] - cleaned[-1][0]) < 1.0 and item[1] == cleaned[-1][1]:
                continue
            cleaned.append(item)
        for seg_index, (left, right) in enumerate(pairwise(cleaned), start=1):
            seg_m = max(0.0, right[0] - left[0])
            if seg_m < 1.0:
                continue
            fraction = seg_m / end_pos if end_pos > 0 else None
            topology_edges.append({
                "topology_edge_id": f"{edge['source_edge_id']}:seg{seg_index:02d}",
                "source_edge_id": edge["source_edge_id"], "segment_index": seg_index,
                "name": edge["name"], "feeder_code": edge["feeder_code"], "voltage_kv": edge["voltage_kv"],
                "status": edge["status"], "owner": edge["owner"], "from_node_id": left[1], "to_node_id": right[1],
                "geometry_length_km": seg_m / 1000.0,
                "source_length_km_allocated": (edge["source_length_km"] * fraction if edge.get("source_length_km") is not None and fraction is not None else None),
                "segment_fraction": fraction,
                "split_by_geometry_junction": bool(junction_ids),
            })

    edge_nodes = {n for e in topology_edges for n in (e["from_node_id"], e["to_node_id"]) if n}
    active_nodes = [n for n in nodes if n["node_id"] in edge_nodes]
    degree = Counter()
    for e in topology_edges:
        degree[e["from_node_id"]] += 1
        degree[e["to_node_id"]] += 1
    for node in active_nodes:
        node["degree"] = degree[node["node_id"]]
    components = _components(edge_nodes, topology_edges)

    feeder_reuse = [
        {"voltage_kv": kv, "feeder_code": code, "feature_count": count}
        for (kv, code), count in sorted(feeder_code_counts.items()) if code and count > 1
    ]
    total_by_voltage = Counter(e["voltage_kv"] for e in source_edges if e.get("topology_admitted"))
    junction_count = sum(n.get("synthetic", False) for n in active_nodes)
    source_ids = [e["source_edge_id"] for e in source_edges]
    public_node_ids = [n["node_id"] for n in public_nodes]
    duplicate_public_node_features_collapsed = sum(
        max(0, int(n.get("source_feature_count") or 1) - 1)
        for n in public_nodes
    )

    graph = {
        "classification": CLASSIFICATION,
        "prepared_date": "2026-09-27",
        "source": {"publisher": "KSEBL Power System Engineering", "public_grid_version": "3.2", "as_of": "2026-03-31", "acquisition_directory": str(args.acquisition)},
        "scope": {"minimum_voltage_kv": 110, "in_service_only": True, "physical_topology_graph": True, "transformer_busbar_model": False, "power_flow_ready": False},
        "counts": {
            "public_nodes_loaded": len(public_nodes), "active_graph_nodes": len(active_nodes), "synthetic_junction_nodes": junction_count,
            "source_features": len(source_edges), "source_features_admitted": sum(bool(e.get("topology_admitted")) for e in source_edges),
            "topology_segments": len(topology_edges), "source_edges_by_voltage": dict(sorted(total_by_voltage.items())),
            "unresolved_admitted_source_edges_by_voltage": dict(sorted(unresolved_by_voltage.items())),
            "connected_components_with_edges": len(components), "largest_component_nodes": len(components[0]) if components else 0,
            "source_anomalies": len(anomalies) + len(split_failures), "feeder_code_reuse_groups": len(feeder_reuse),
        },
        "endpoint_policy": {
            "220_320_400_public_node_snap_threshold_km": HIGH_VOLTAGE_SNAP_KM,
            "110_public_node_snap_threshold_km": LOW_VOLTAGE_SNAP_KM,
            "110_geometry_junction_parent_max_km": JUNCTION_PARENT_MAX_KM,
            "110_geometry_junction_cluster_max_km": JUNCTION_CLUSTER_MAX_KM,
            "rule": "public node snap first; unresolved 110-kV endpoints may join only directly coincident published 110-kV feeder geometry; degenerate features are not admitted",
        },
        "warnings": [
            "Synthetic junctions express public feeder-geometry connectivity only; they are not assumed substations or switchgear buses.",
            "A source feeder feature may become multiple topology segments when a tap/LILO junction lies on its interior.",
            "Transformer/busbar structure and electrical parameters remain separate gates before load-flow use.",
        ],
        "nodes": active_nodes, "source_edges": source_edges, "topology_edges": topology_edges,
        "source_anomalies": anomalies + split_failures, "feeder_code_reuse": feeder_reuse, "components": components,
    }

    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "network_graph_110plus.json").write_text(json.dumps(graph, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    _write_csv(args.out / "network_nodes_110plus.csv", active_nodes)
    _write_csv(args.out / "network_source_edges_110plus.csv", source_edges)
    _write_csv(args.out / "network_topology_edges_110plus.csv", topology_edges)
    _write_csv(args.out / "network_source_anomalies.csv", anomalies + split_failures)
    qa = {
        "classification": "KSEBL_PUBLIC_GRID_GRAPH_V0_2_QA",
        "source_edge_ids_unique": len(source_ids) == len(set(source_ids)),
        "public_node_ids_unique": len(public_node_ids) == len(set(public_node_ids)),
        "duplicate_public_node_features_collapsed": duplicate_public_node_features_collapsed,
        "all_220plus_edges_resolved": all(unresolved_by_voltage.get(kv, 0) == 0 for kv in (220, 320, 400)),
        "unresolved_admitted_source_edges_by_voltage": dict(sorted(unresolved_by_voltage.items())),
        "synthetic_junction_nodes": junction_count,
        "degenerate_geometry_features": sum(a.get("anomaly") == "DEGENERATE_GEOMETRY" for a in anomalies),
        "invalid_or_empty_geometry_features": sum(a.get("anomaly") == "INVALID_OR_EMPTY_GEOMETRY" for a in anomalies),
        "topology_segments": len(topology_edges),
        "active_graph_nodes": len(active_nodes),
        "connected_components_with_edges": len(components),
        "largest_component_nodes": len(components[0]) if components else 0,
        "feeder_code_reuse_groups": len(feeder_reuse),
        "split_failures": split_failures,
        "power_flow_ready": False,
    }
    (args.out / "network_graph_qa.json").write_text(json.dumps(qa, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(qa, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
