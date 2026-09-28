"""Planning bridge for robust KSEBL network-screening evidence."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

DEFAULT_EVIDENCE_RELATIVE = (
    "data/evidence/network/"
    "kseb_network_robust_bottlenecks_v1_0_2026_09_28.json"
)

EVIDENCE_CLASS = (
    "KSEBL_NETWORK_ROBUST_BOTTLENECK_EVIDENCE_V1_0_"
    "SCREENING_NOT_OPERATIONAL_VALIDATION"
)


def load_network_planning_evidence(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("classification") != EVIDENCE_CLASS:
        raise ValueError("network planning evidence classification mismatch")
    summary = data["summary"]
    if int(summary["robust_source_backed_line_bottlenecks"]) != 21:
        raise ValueError("robust line-bottleneck count changed without review")
    if int(summary["robust_independent_pss_backed_transformer_bottlenecks"]) != 1:
        raise ValueError("robust transformer-bottleneck count changed without review")
    if int(summary["source_backed_primary_lines_tested"]) != 233:
        raise ValueError("source-backed line population changed without review")
    if len(data.get("robust_line_bottlenecks") or []) != 21:
        raise ValueError("robust line register must contain 21 rows")
    if len(data.get("robust_transformer_bottlenecks") or []) != 1:
        raise ValueError("robust transformer register must contain one row")
    if data["source"].get("boundary_allocation_cases") != 8:
        raise ValueError("network robustness envelope must retain eight cases")
    if data["source"].get("admitted_interface_count") != 6:
        raise ValueError("network robustness interface count changed")
    if summary.get("all_cases_topology_closed_without_gap_supply") is not True:
        raise ValueError("network robustness evidence contains topology-gap supply")
    corridors = data.get("robust_corridors") or []
    if len(corridors) != 12:
        raise ValueError("robust corridor register must contain 12 connected groups")
    corridor_line_ids = [
        line_id
        for corridor in corridors
        for line_id in corridor.get("line_ids", [])
    ]
    robust_line_ids = [
        row["line_id"] for row in data.get("robust_line_bottlenecks") or []
    ]
    if sorted(corridor_line_ids) != sorted(robust_line_ids):
        raise ValueError("robust corridor groups must partition all 21 robust lines")
    if data.get("system_pattern", {}).get("strongest_hub") != "Shornur":
        raise ValueError("strongest multi-voltage screening hub changed without review")
    treatment = data["planning_model_treatment"]
    if "EVIDENCE_GATE_ONLY" not in treatment["full_pypsa_capacity_expansion"]:
        raise ValueError("Full-PyPSA must not silently internalize screening constraints")
    if "EVIDENCE_GATE_ONLY" not in treatment["osemosys_capacity_benchmark"]:
        raise ValueError("OSeMOSYS must not silently internalize screening constraints")
    return data


def planning_network_summary(data: dict[str, Any]) -> dict[str, Any]:
    summary = data["summary"]
    tx = data["robust_transformer_bottlenecks"][0]
    return {
        "classification": data["classification"],
        "source_pr": data["source"]["pr_number"],
        "source_commit": data["source"]["merged_commit"],
        "hours_per_case": data["source"]["hours_per_case"],
        "boundary_allocation_cases": data["source"]["boundary_allocation_cases"],
        "robust_source_backed_line_bottlenecks": summary[
            "robust_source_backed_line_bottlenecks"
        ],
        "robust_connected_subgraphs": summary["robust_connected_subgraphs"],
        "robust_corridor_groups": len(data["robust_corridors"]),
        "strongest_multi_voltage_screening_hub": data["system_pattern"][
            "strongest_hub"
        ],
        "robust_independent_pss_backed_transformer_bottlenecks": summary[
            "robust_independent_pss_backed_transformer_bottlenecks"
        ],
        "robust_transformer_location": tx["location"],
        "spatial_constraints_internalized_in_planning_optimizers": False,
        "interpretation": (
            "Public-network screening evidence is carried as a planning gate. "
            "It is not converted into investment constraints until future corridor "
            "capacities, upgrade options/costs and a validated spatial aggregation "
            "are admitted."
        ),
    }


def planning_network_summary_from_root(root: Path) -> dict[str, Any]:
    """Load the canonical robust-network planning gate from a repository root."""
    return planning_network_summary(
        load_network_planning_evidence(root / DEFAULT_EVIDENCE_RELATIVE)
    )
