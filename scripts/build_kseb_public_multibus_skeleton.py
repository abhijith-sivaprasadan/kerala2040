"""Build a fail-closed multi-voltage network skeleton from admitted KSEBL evidence.

This is a structural model handoff, not a power-flow model. It expands physical
sites into voltage-specific buses, maps feeder topology segments to those buses,
adds structural transformer connectivity only where public SLD evidence supports
it, and attaches only previously admitted generators. Ratings, impedances and
loads remain unresolved unless separately sourced.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
from collections import defaultdict, deque
from difflib import SequenceMatcher
from itertools import pairwise
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_GRAPH = ROOT / "results/network/public_grid_graph_v0_2/network_graph_110plus.json"
DEFAULT_TRANSFORMERS = ROOT / "results/network/public_sld_transformers_v0_1/transformer_evidence.json"
DEFAULT_GENERATORS = ROOT / "results/network/generator_bus_crosswalk_v0_1/generator_bus_crosswalk.json"
DEFAULT_OUT = ROOT / "results/network/public_multibus_skeleton_v0_1"

CLASSIFICATION = "KSEBL_PUBLIC_MULTIBUS_SKELETON_V0_1_NOT_POWER_FLOW_READY"


def _norm(value: Any) -> str:
    return " ".join(re.sub(r"[^a-z0-9]+", " ", str(value or "").lower()).split())


def _as_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value or "").strip().lower() in {"1", "true", "yes"}


def _as_int(value: Any) -> int | None:
    try:
        if value in (None, ""):
            return None
        return int(float(value))
    except (TypeError, ValueError):
        return None


def _write_csv(
    path: Path,
    rows: list[dict[str, Any]],
    fields: list[str] | None = None,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if fields is None:
        fields = []
        for row in rows:
            for key in row:
                if key not in fields:
                    fields.append(key)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def _map_station(
    record: dict[str, Any],
    nodes_by_code: dict[str, list[dict[str, Any]]],
) -> dict[str, Any] | None:
    code = str(record.get("code") or "")
    candidates = nodes_by_code.get(code, [])
    if not candidates:
        return None
    if len(candidates) == 1:
        return candidates[0]

    location = _norm(record.get("location"))
    klass = _as_int(record.get("class"))
    ranked: list[tuple[float, str, dict[str, Any]]] = []
    for node in candidates:
        score = SequenceMatcher(None, location, _norm(node.get("location"))).ratio()
        if klass is not None and klass == _as_int(node.get("voltage_class_kv")):
            score += 0.20
        ranked.append((score, str(node["node_id"]), node))
    ranked.sort(key=lambda item: (-item[0], item[1]))
    return ranked[0][2]


def _components(
    bus_ids: set[str],
    lines: list[dict[str, Any]],
    transformers: list[dict[str, Any]],
) -> tuple[list[list[str]], int]:
    adjacency: dict[str, set[str]] = defaultdict(set)
    for row in lines:
        a, b = row["bus0"], row["bus1"]
        adjacency[a].add(b)
        adjacency[b].add(a)
    for row in transformers:
        a, b = row["bus0"], row["bus1"]
        adjacency[a].add(b)
        adjacency[b].add(a)

    seen: set[str] = set()
    components: list[list[str]] = []
    for bus_id in sorted(bus_ids):
        if bus_id in seen or bus_id not in adjacency:
            continue
        queue = deque([bus_id])
        seen.add(bus_id)
        component: list[str] = []
        while queue:
            current = queue.popleft()
            component.append(current)
            for neighbour in adjacency[current]:
                if neighbour not in seen:
                    seen.add(neighbour)
                    queue.append(neighbour)
        components.append(sorted(component))
    components.sort(key=len, reverse=True)
    isolated = sum(bus_id not in adjacency for bus_id in bus_ids)
    return components, isolated


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--graph", type=Path, default=DEFAULT_GRAPH)
    parser.add_argument("--transformers", type=Path, default=DEFAULT_TRANSFORMERS)
    parser.add_argument("--generators", type=Path, default=DEFAULT_GENERATORS)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()

    graph = json.loads(args.graph.read_text(encoding="utf-8"))
    transformer_payload = json.loads(args.transformers.read_text(encoding="utf-8"))
    generator_payload = json.loads(args.generators.read_text(encoding="utf-8"))

    nodes = graph.get("nodes") or []
    topology_edges = graph.get("topology_edges") or []
    node_ids = [str(row["node_id"]) for row in nodes]
    if len(node_ids) != len(set(node_ids)):
        raise RuntimeError("multi-bus admission requires unique physical node IDs")

    node_by_id = {str(row["node_id"]): row for row in nodes}
    nodes_by_code: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for node in nodes:
        code = str(node.get("code") or "")
        if code:
            nodes_by_code[code].append(node)

    incident_voltages: dict[str, set[int]] = defaultdict(set)
    for edge in topology_edges:
        voltage = int(edge["voltage_kv"])
        incident_voltages[str(edge["from_node_id"])].add(voltage)
        incident_voltages[str(edge["to_node_id"])].add(voltage)

    active_transformer_records = [
        row
        for row in transformer_payload.get("transformer_evidence", [])
        if not _as_bool(row.get("proposed"))
    ]
    mapped_transformer_records: list[
        tuple[dict[str, Any], dict[str, Any], list[int]]
    ] = []
    transformer_records_outside_graph: list[dict[str, Any]] = []
    sld_voltages: dict[str, set[int]] = defaultdict(set)
    for row in active_transformer_records:
        node = _map_station(row, nodes_by_code)
        if node is None:
            transformer_records_outside_graph.append(row)
            continue
        levels = sorted(
            {
                parsed
                for value in row.get("voltage_levels_kv", [])
                if (parsed := _as_int(value)) is not None
            },
            reverse=True,
        )
        if len(levels) < 2:
            continue
        for voltage in levels:
            sld_voltages[str(node["node_id"])].add(voltage)
        mapped_transformer_records.append((row, node, levels))

    buses: list[dict[str, Any]] = []
    bus_ids: set[str] = set()
    site_bus_voltages: dict[str, set[int]] = defaultdict(set)
    for node in nodes:
        node_id = str(node["node_id"])
        voltages = set(incident_voltages.get(node_id, set()))
        voltages.update(sld_voltages.get(node_id, set()))
        station_class = _as_int(node.get("voltage_class_kv"))
        if station_class is not None:
            voltages.add(station_class)
        for voltage in sorted(voltages, reverse=True):
            bus_id = f"{node_id}@{voltage}"
            if bus_id in bus_ids:
                raise RuntimeError(f"duplicate bus id: {bus_id}")
            bus_ids.add(bus_id)
            site_bus_voltages[node_id].add(voltage)
            buses.append(
                {
                    "bus_id": bus_id,
                    "node_id": node_id,
                    "voltage_kv": voltage,
                    "location": node.get("location", ""),
                    "code": node.get("code", ""),
                    "kind": node.get("kind", ""),
                    "district": node.get("district", ""),
                    "lon": node.get("lon"),
                    "lat": node.get("lat"),
                    "synthetic_junction": _as_bool(node.get("synthetic")),
                    "topology_voltage_evidence": voltage
                    in incident_voltages.get(node_id, set()),
                    "station_class_voltage_evidence": station_class == voltage,
                    "sld_transformer_voltage_evidence": voltage
                    in sld_voltages.get(node_id, set()),
                }
            )

    lines: list[dict[str, Any]] = []
    for edge in topology_edges:
        voltage = int(edge["voltage_kv"])
        bus0 = f"{edge['from_node_id']}@{voltage}"
        bus1 = f"{edge['to_node_id']}@{voltage}"
        if bus0 not in bus_ids or bus1 not in bus_ids:
            raise RuntimeError(
                "topology edge references missing voltage bus: "
                f"{edge['topology_edge_id']}"
            )
        lines.append(
            {
                "line_id": edge["topology_edge_id"],
                "source_edge_id": edge["source_edge_id"],
                "name": edge.get("name", ""),
                "feeder_code": edge.get("feeder_code", ""),
                "voltage_kv": voltage,
                "bus0": bus0,
                "bus1": bus1,
                "geometry_length_km": edge.get("geometry_length_km"),
                "source_length_km_allocated": edge.get(
                    "source_length_km_allocated"
                ),
                "s_nom_mva": None,
                "r_pu": None,
                "x_pu": None,
                "b_pu": None,
                "electrical_parameters_admitted": False,
            }
        )

    transformer_groups: dict[tuple[str, int, int], dict[str, Any]] = {}
    for record, node, levels in mapped_transformer_records:
        node_id = str(node["node_id"])
        for high, low in pairwise(levels):
            key = (node_id, high, low)
            item = transformer_groups.setdefault(
                key,
                {
                    "transformer_link_id": f"TX:{node_id}:{high}-{low}",
                    "node_id": node_id,
                    "location": node.get("location", ""),
                    "code": node.get("code", ""),
                    "bus0": f"{node_id}@{high}",
                    "bus1": f"{node_id}@{low}",
                    "v0_kv": high,
                    "v1_kv": low,
                    "evidence_record_count": 0,
                    "labelled_evidence_record_count": 0,
                    "evidence_ids": [],
                    "rating_expressions": [],
                    "rating_values_mva": [],
                    "s_nom_mva_admitted": None,
                    "impedance_admitted": False,
                    "connectivity_only": True,
                },
            )
            item["evidence_record_count"] += 1
            item["labelled_evidence_record_count"] += int(
                _as_bool(record.get("identity_complete"))
            )
            item["evidence_ids"].append(str(record.get("evidence_id") or ""))
            item["rating_expressions"].append(
                str(record.get("rating_expression") or "")
            )
            item["rating_values_mva"].append(
                "/".join(
                    f"{float(value):g}"
                    for value in record.get("rating_values_mva", [])
                )
            )

    transformer_links: list[dict[str, Any]] = []
    for key in sorted(transformer_groups):
        row = transformer_groups[key]
        if row["bus0"] not in bus_ids or row["bus1"] not in bus_ids:
            raise RuntimeError(
                "transformer evidence references missing bus: "
                f"{row['transformer_link_id']}"
            )
        row["evidence_ids"] = ";".join(
            dict.fromkeys(row["evidence_ids"])
        )
        row["rating_expressions"] = ";".join(
            dict.fromkeys(row["rating_expressions"])
        )
        row["rating_values_mva"] = ";".join(
            dict.fromkeys(row["rating_values_mva"])
        )
        transformer_links.append(row)

    local_tx: dict[str, dict[int, set[int]]] = defaultdict(
        lambda: defaultdict(set)
    )
    for row in transformer_links:
        high, low = int(row["v0_kv"]), int(row["v1_kv"])
        local_tx[row["node_id"]][high].add(low)
        local_tx[row["node_id"]][low].add(high)

    voltage_bridge_gaps: list[dict[str, Any]] = []
    multi_voltage_sites = 0
    for node_id, voltages in sorted(site_bus_voltages.items()):
        if len(voltages) <= 1:
            continue
        multi_voltage_sites += 1
        seen: set[int] = set()
        groups: list[list[int]] = []
        for voltage in sorted(voltages, reverse=True):
            if voltage in seen:
                continue
            queue = deque([voltage])
            seen.add(voltage)
            group: list[int] = []
            while queue:
                current = queue.popleft()
                group.append(current)
                for neighbour in local_tx[node_id].get(current, set()):
                    if neighbour in voltages and neighbour not in seen:
                        seen.add(neighbour)
                        queue.append(neighbour)
            groups.append(sorted(group, reverse=True))
        if len(groups) > 1:
            node = node_by_id[node_id]
            voltage_bridge_gaps.append(
                {
                    "node_id": node_id,
                    "location": node.get("location", ""),
                    "code": node.get("code", ""),
                    "site_bus_voltages_kv": ";".join(
                        map(str, sorted(voltages, reverse=True))
                    ),
                    "transformer_connected_voltage_groups": " | ".join(
                        ";".join(map(str, group)) for group in groups
                    ),
                    "gap": "INCOMPLETE_TRANSFORMER_CONNECTIVITY_EVIDENCE",
                }
            )

    attached_generators: list[dict[str, Any]] = []
    unallocated_generators: list[dict[str, Any]] = []
    generator_voltage_inferred = 0
    for row in generator_payload.get("rows", []):
        node_id = str(row.get("network_node_id") or "")
        if not node_id:
            unallocated_generators.append(row)
            continue
        voltage = _as_int(row.get("network_node_voltage_class_kv"))
        voltage_basis = "CROSSWALK_NODE_CLASS"
        if voltage is None:
            incident = incident_voltages.get(node_id, set())
            if len(incident) == 1:
                voltage = next(iter(incident))
                voltage_basis = "UNIQUE_INCIDENT_TOPOLOGY_VOLTAGE"
                generator_voltage_inferred += 1
            else:
                unresolved = dict(row)
                unresolved["model_skeleton_gap"] = (
                    "GENERATOR_BUS_VOLTAGE_AMBIGUOUS"
                )
                unallocated_generators.append(unresolved)
                continue
        bus_id = f"{node_id}@{voltage}"
        if bus_id not in bus_ids:
            unresolved = dict(row)
            unresolved["model_skeleton_gap"] = "GENERATOR_BUS_NOT_PRESENT"
            unallocated_generators.append(unresolved)
            continue
        attached_generators.append(
            {
                "asset_id": row.get("asset_id", ""),
                "plant": row.get("plant", ""),
                "technology": row.get("technology", ""),
                "capacity_mw": float(row.get("capacity_mw") or 0),
                "bus_id": bus_id,
                "node_id": node_id,
                "voltage_kv": voltage,
                "voltage_assignment_basis": voltage_basis,
                "source_bus_attachment_status": row.get(
                    "bus_attachment_status", ""
                ),
                "p_nom_mw": float(row.get("capacity_mw") or 0),
                "hourly_availability_admitted": False,
            }
        )

    components, isolated_buses = _components(
        bus_ids, lines, transformer_links
    )

    gaps = [
        {
            "gap_id": "LOAD_CHRONOLOGY",
            "severity": "BLOCKING_FOR_DISPATCH",
            "affected_records": len(buses),
            "status": (
                "NO_SUBSTATION_OR_BUS_LOAD_MW_MVAR_CHRONOLOGY_ADMITTED"
            ),
        },
        {
            "gap_id": "LINE_RATINGS",
            "severity": "BLOCKING_FOR_NETWORK_CONSTRAINED_DISPATCH",
            "affected_records": len(lines),
            "status": "NO_BRANCH_THERMAL_MVA_LIMIT_ADMITTED",
        },
        {
            "gap_id": "LINE_IMPEDANCE",
            "severity": "BLOCKING_FOR_DC_AC_POWER_FLOW",
            "affected_records": len(lines),
            "status": "NO_R_X_B_PARAMETERS_ADMITTED",
        },
        {
            "gap_id": "TRANSFORMER_PARAMETERS",
            "severity": "BLOCKING_FOR_POWER_FLOW",
            "affected_records": len(transformer_links),
            "status": (
                "STRUCTURAL_CONNECTIVITY_ONLY; "
                "NO_AGGREGATE_S_NOM_OR_IMPEDANCE_ADMITTED"
            ),
        },
        {
            "gap_id": "LOCAL_VOLTAGE_BRIDGES",
            "severity": "TOPOLOGY_GAP",
            "affected_records": len(voltage_bridge_gaps),
            "status": (
                "MULTI_VOLTAGE_SITES_WITH_INCOMPLETE_"
                "TRANSFORMER_CONNECTIVITY_EVIDENCE"
            ),
        },
    ]

    qa = {
        "classification": "KSEBL_PUBLIC_MULTIBUS_SKELETON_V0_1_QA",
        "physical_site_nodes": len(nodes),
        "voltage_specific_buses": len(buses),
        "topology_line_segments": len(lines),
        "structural_transformer_links": len(transformer_links),
        "active_sld_transformer_evidence_records": len(
            active_transformer_records
        ),
        "active_sld_transformer_evidence_records_mapped_to_110plus_graph": len(
            mapped_transformer_records
        ),
        "active_sld_transformer_evidence_records_outside_110plus_graph": len(
            transformer_records_outside_graph
        ),
        "multi_voltage_sites": multi_voltage_sites,
        "sites_with_incomplete_transformer_connectivity": len(
            voltage_bridge_gaps
        ),
        "attached_generator_rows": len(attached_generators),
        "attached_generator_capacity_mw": round(
            sum(row["capacity_mw"] for row in attached_generators), 6
        ),
        "generator_voltage_assignments_from_unique_incident_topology": (
            generator_voltage_inferred
        ),
        "unallocated_generator_rows": len(unallocated_generators),
        "unallocated_generator_capacity_mw": round(
            sum(
                float(row.get("capacity_mw") or 0)
                for row in unallocated_generators
            ),
            6,
        ),
        "connected_components_with_edges": len(components),
        "largest_component_buses": len(components[0]) if components else 0,
        "isolated_buses": isolated_buses,
        "line_segments_with_admitted_thermal_rating": 0,
        "line_segments_with_admitted_impedance": 0,
        "transformer_links_with_admitted_capacity_constraint": 0,
        "load_rows": 0,
        "bus_ids_unique": len(bus_ids) == len(buses),
        "line_ids_unique": (
            len({row["line_id"] for row in lines}) == len(lines)
        ),
        "transformer_link_ids_unique": (
            len(
                {
                    row["transformer_link_id"]
                    for row in transformer_links
                }
            )
            == len(transformer_links)
        ),
        "all_line_bus_references_valid": all(
            row["bus0"] in bus_ids and row["bus1"] in bus_ids
            for row in lines
        ),
        "all_transformer_bus_references_valid": all(
            row["bus0"] in bus_ids and row["bus1"] in bus_ids
            for row in transformer_links
        ),
        "all_attached_generator_bus_references_valid": all(
            row["bus_id"] in bus_ids for row in attached_generators
        ),
        "topology_skeleton_ready": True,
        "transport_dispatch_ready": False,
        "dc_power_flow_ready": False,
        "ac_power_flow_ready": False,
    }

    args.out.mkdir(parents=True, exist_ok=True)
    _write_csv(args.out / "model_buses.csv", buses)
    _write_csv(args.out / "model_lines.csv", lines)
    _write_csv(
        args.out / "model_transformer_links.csv", transformer_links
    )
    _write_csv(args.out / "model_generators.csv", attached_generators)
    _write_csv(
        args.out / "unallocated_generators.csv", unallocated_generators
    )
    _write_csv(
        args.out / "load_template.csv",
        [],
        [
            "load_id",
            "bus_id",
            "timestamp",
            "p_mw",
            "q_mvar",
            "source",
            "quality_flag",
        ],
    )
    _write_csv(
        args.out / "voltage_bridge_gaps.csv", voltage_bridge_gaps
    )
    _write_csv(args.out / "model_gap_register.csv", gaps)
    payload = {
        "classification": CLASSIFICATION,
        "prepared_date": "2026-09-27",
        "scope": {
            "minimum_transmission_voltage_kv": 110,
            "lower_voltage_buses": (
                "included only when public SLD transformer evidence exposes "
                "them at an active 110-kV+ site"
            ),
            "line_parameters": "unresolved",
            "transformer_capacity_and_impedance": "unresolved",
            "load_chronology": "unresolved",
            "generator_availability": "unresolved",
        },
        "qa": qa,
        "warnings": [
            (
                "Transformer links express voltage-level connectivity supported "
                "by public SLD text; they are not a complete equipment count."
            ),
            (
                "Three-winding evidence is represented as adjacent voltage-level "
                "connectivity only, not an electrical three-winding equivalent."
            ),
            (
                "No line thermal rating, line impedance, transformer impedance "
                "or load time series is fabricated."
            ),
            (
                "This output is a model-assembly skeleton and must not be solved "
                "as a power-flow or constrained-dispatch network."
            ),
        ],
    }
    (args.out / "multibus_skeleton_summary.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (args.out / "multibus_skeleton_qa.json").write_text(
        json.dumps(qa, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(qa, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
