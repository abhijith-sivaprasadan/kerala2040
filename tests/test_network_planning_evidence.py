"""Tests for robust KSEBL planning-network evidence."""
from pathlib import Path

from kerala2040.network_planning_evidence import (
    EVIDENCE_CLASS,
    load_network_planning_evidence,
    planning_network_summary,
)

ROOT = Path(__file__).resolve().parents[1]


def test_network_planning_evidence_is_guarded_and_not_promoted() -> None:
    data = load_network_planning_evidence(
        ROOT
        / "data/evidence/network/"
        "kseb_network_robust_bottlenecks_v1_0_2026_09_28.json"
    )
    assert data["classification"] == EVIDENCE_CLASS
    assert len(data["robust_line_bottlenecks"]) == 21
    assert len(data["robust_transformer_bottlenecks"]) == 1
    summary = planning_network_summary(data)
    assert summary["robust_source_backed_line_bottlenecks"] == 21
    assert summary["robust_independent_pss_backed_transformer_bottlenecks"] == 1
    assert summary["robust_transformer_location"] == "Shornur"
    assert summary["robust_corridor_groups"] == 12
    assert summary["strongest_multi_voltage_screening_hub"] == "Shornur"
    assert summary["spatial_constraints_internalized_in_planning_optimizers"] is False
