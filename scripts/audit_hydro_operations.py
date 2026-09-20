"""Fail-closed hydro evidence audit, not a reservoir dispatch model."""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path
from typing import Any

import yaml

ROOT_QA = "data/external/sldc_fy2024_25/qa_report.json"
RESERVOIRS = "data/external/sldc_fy2024_25/reservoir_daily.csv"
STATIONS = "data/external/sldc_fy2024_25/hydro_station_daily.csv"
DAILY = "data/external/sldc_fy2024_25/daily_balance.csv"
TOPOLOGY = "configs/hydro_topology_evidence_2024_25.yaml"
SHA = re.compile(r"[0-9a-f]{64}")


def _csv(root: Path, path: str) -> list[dict[str, str]]:
    with (root / path).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _numeric(row: dict[str, str], key: str) -> float | None:
    value = row[key]
    if value == "":
        return None
    n = float(value)
    if not (-1e20 < n < 1e20):
        raise ValueError(f"Nonfinite hydro metric {key}")
    return n


def _validate_graph(topology: dict[str, Any],
                    reservoir_names: set[str],
                    station_names: set[str]) -> dict[str, Any]:
    if topology.get("classification") != (
        "partial_official_hydro_topology_not_dispatch_constraints"
    ):
        raise ValueError("Hydro topology classification cannot claim complete operations")
    sources = topology["sources"]
    for key, entry in sources.items():
        if not entry.get("url", "").startswith("https://"):
            raise ValueError(f"Hydro source URL missing: {key}")
    mapped = topology["observed_reservoirs"]
    if set(mapped) - reservoir_names:
        raise ValueError(f"Unknown SLDC reservoir label {sorted(set(mapped) - reservoir_names)}")
    all_nodes = reservoir_names | station_names | set(topology["non_observed_nodes"])
    referenced_stations: set[str] = set()
    for name, entry in mapped.items():
        if not entry.get("source_ids") or not set(entry["source_ids"]) <= set(sources):
            raise ValueError(f"Unreferenced reservoir-source mapping: {name}")
        if "sldc_reservoir" not in entry["source_ids"]:
            raise ValueError(f"Missing observed reservoir provenance: {name}")
        if not entry.get("storage_complex") or not entry.get("correspondence"):
            raise ValueError(f"Reservoir relationship unqualified: {name}")
        for station in entry["source_station_labels"]:
            if station not in station_names:
                raise ValueError(f"Unmatched observed station name: {station}")
            referenced_stations.add(station)
    complexes = topology["storage_complexes"]
    for complex_id, complex_data in complexes.items():
        if not complex_data["unique_waterbody"]:
            raise ValueError(f"Multiple dams double-counted as stores: {complex_id}")
        if len(set(complex_data["structures"])) != len(complex_data["structures"]):
            raise ValueError(f"Repeated structures in {complex_id}")
        if not set(complex_data["source_ids"]) <= set(sources):
            raise ValueError(f"Unknown complex source {complex_id}")
    for name, entry in mapped.items():
        if entry["storage_complex"] not in complexes and name not in {
            "PAMBA", "PORINGAL", "KAKKAD"
        }:
            raise ValueError(f"Unqualified storage complex: {name}")
    edges: dict[str, set[str]] = defaultdict(set)
    pairs: set[tuple[str, str]] = set()
    for link in topology["documented_links"]:
        u, v = link["from"], link["to"]
        if u not in all_nodes or v not in all_nodes or u == v:
            raise ValueError(f"Unknown/self-linked hydro node: {u} -> {v}")
        if (u, v) in pairs:
            raise ValueError(f"Duplicate hydro link {u}->{v}")
        pairs.add((u, v))
        if not link.get("relation") or not link.get("source_ids"):
            raise ValueError(f"Unqualified link {u}->{v}")
        if not set(link["source_ids"]) <= set(sources):
            raise ValueError(f"Unknown link evidence {u}->{v}")
        edges[u].add(v)
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(u: str) -> None:
        if u in visiting:
            raise ValueError("Hydro directed topology contains a cycle")
        if u in visited:
            return
        visiting.add(u)
        for v in edges[u]:
            visit(v)
        visiting.remove(u)
        visited.add(u)

    for u in all_nodes:
        visit(u)
    return {
        "mapped_reservoir_labels": len(mapped),
        "mapped_station_labels": len(referenced_stations),
        "documented_qualitative_links": len(pairs),
        "documented_shared_waterbody_complexes": len(complexes),
        "unmapped_reservoir_labels": sorted(reservoir_names - set(mapped)),
        "unmapped_station_labels": sorted(station_names - referenced_stations),
    }


def audit_hydro_evidence(root: Path) -> dict[str, Any]:
    """Verify reported rows and exact source topology; never infer water flows."""
    qa = json.loads((root / ROOT_QA).read_text(encoding="utf-8"))
    topology = yaml.safe_load((root / TOPOLOGY).read_text(encoding="utf-8"))
    reservoir = _csv(root, RESERVOIRS)
    stations = _csv(root, STATIONS)
    daily = _csv(root, DAILY)
    if len(reservoir) != qa["normalized_row_counts"]["reservoir"]:
        raise ValueError("SLDC reservoir row count differs from source QA")
    if len(stations) != qa["normalized_row_counts"]["hydro_station"]:
        raise ValueError("SLDC station row count differs from source QA")
    if len(daily) != qa["normalized_row_counts"]["daily_balance"]:
        raise ValueError("SLDC daily row count differs from source QA")
    observed = {r["date"] for r in daily if r["status"] == "observed"}
    missing = {r["date"] for r in daily if r["status"] == "missing"}
    if (len(observed) != qa["observed_days"] or missing != set(qa["missing_dates"])
            or observed & missing or len(daily) != qa["expected_days"]):
        raise ValueError("Hydro observed-day coverage does not match SLDC QA")
    daily_dates = [r["date"] for r in daily]
    if len(daily_dates) != len(set(daily_dates)):
        raise ValueError("Duplicate SLDC daily dates")
    if qa.get("source_archive_sha256") == "" or qa["bad_raw_sha256_count"]:
        raise ValueError("Source archive integrity not established")
    if len(reservoir) % len(observed):
        raise ValueError("Unequal reservoir row count per observed day")
    expected_per_day = len(reservoir) // len(observed)
    reservoir_day: dict[str, set[str]] = defaultdict(set)
    station_day: dict[str, set[str]] = defaultdict(set)
    reservoir_hash: dict[str, set[str]] = defaultdict(set)
    station_hash: dict[str, set[str]] = defaultdict(set)
    anomalous_storage_pct: list[dict[str, Any]] = []
    gross_station_not_interchangeable = 0
    for row in reservoir:
        day, name, digest = (
            row["date"], row["reservoir_name_as_reported"], row["source_sha256"]
        )
        if day not in observed or not SHA.fullmatch(digest):
            raise ValueError("Hydro reservoir row lacks an observed date or SHA")
        if name in reservoir_day[day]:
            raise ValueError(f"Duplicate reservoir on {day}: {name}")
        reservoir_day[day].add(name)
        reservoir_hash[day].add(digest)
        for key in (
            "level_m", "effective_storage_mcm", "storage_percent",
            "generation_capability_gross_mu", "generation_capability_station_mu"
        ):
            _numeric(row, key)
        effective = _numeric(row, "effective_storage_mcm")
        pct = _numeric(row, "storage_percent")
        if effective is not None and effective > 0 and pct == 0:
            anomalous_storage_pct.append({
                "date": day, "reservoir": name,
                "effective_storage_mcm": effective,
                "reported_storage_percent": pct,
                "interpretation": "Unreconciled source field; do not replace with a computed percentage.",
            })
        gross = _numeric(row, "generation_capability_gross_mu")
        station = _numeric(row, "generation_capability_station_mu")
        if gross is not None and station is not None and abs(gross - station) > 0.001:
            gross_station_not_interchangeable += 1
    for row in stations:
        day, name, digest = (
            row["date"], row["station_name_as_reported"], row["source_sha256"]
        )
        if day not in observed or not SHA.fullmatch(digest):
            raise ValueError("Hydro station row lacks an observed date or SHA")
        if name in station_day[day]:
            raise ValueError(f"Duplicate station on {day}: {name}")
        station_day[day].add(name)
        station_hash[day].add(digest)
        _numeric(row, "generation_mu")
    if any(len(v) != 1 for v in reservoir_hash.values()):
        raise ValueError("Reservoir source SHA differs within a daily source section")
    if any(len(v) != 1 for v in station_hash.values()):
        raise ValueError("Station source SHA differs within a daily source section")
    if set(reservoir_day) != observed or set(station_day) != observed:
        raise ValueError("Reservoir/station reports missing for an observed SLDC day")
    reservoir_names = set.union(*reservoir_day.values())
    if any(v != reservoir_names for v in reservoir_day.values()):
        raise ValueError("SLDC reservoir names change across days; inspect before mapping")
    if any(len(v) != expected_per_day for v in reservoir_day.values()):
        raise ValueError("SLDC reservoir rows missing for one or more dates")
    station_names = set.union(*station_day.values())
    graph = _validate_graph(topology, reservoir_names, station_names)
    return {
        "classification": "verified_retained_daily_rows_and_partial_official_topology_NOT_hydro_dispatch_model",
        "source_archive_sha256": qa["source_archive_sha256"],
        "source_evidence": [QA for QA in (ROOT_QA, RESERVOIRS, STATIONS, DAILY, TOPOLOGY)],
        "observed_dates": len(observed),
        "expected_dates": qa["expected_days"],
        "missing_dates": sorted(missing),
        "reservoir_rows": len(reservoir),
        "reservoir_rows_per_observed_date": expected_per_day,
        "unique_reservoir_names": len(reservoir_names),
        "hydro_station_rows": len(stations),
        "unique_hydro_station_names": len(station_names),
        "gross_vs_station_capability_distinct_rows": gross_station_not_interchangeable,
        "positive_effective_storage_with_zero_reported_pct": len(
            anomalous_storage_pct
        ),
        "storage_pct_conflict_examples": anomalous_storage_pct[:10],
        "qualitative_topology": graph,
        "source_derived_dated_hydrology_verified": False,
        "water_balance_reconciled": False,
        "head_efficiency_and_release_rules_verified": False,
        "cascade_energy_allocation_allowed": False,
        "pypsa_connected_hydro_stores_allowed": False,
        "audit_gate_closed": False,
        "interpretation": (
            "Observed SLDC water-level/storage and station-generation rows have "
            "dated source hashes; documented selected directional links are "
            "qualitative. Source MU and percent fields are not transferable "
            "independent energy stores or water-volume inflows."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument(
        "--output", type=Path, default=Path("results/hydro/operations_evidence.json")
    )
    args = parser.parse_args()
    report = audit_hydro_evidence(args.root)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n",
                           encoding="utf-8")
    print(json.dumps(report, indent=2, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
