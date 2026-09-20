"""Research progress is source-reconciled, not a release-gate override."""
from __future__ import annotations

from pathlib import Path

import pytest

from kerala2040.audit_readiness import build_audit
from kerala2040.research_ledger import build_ledger

ROOT = Path(__file__).resolve().parents[1]


def test_workbench_ledger_is_a_fail_closed_index():
    ledger = build_ledger(ROOT)
    assert ledger["classification"] == (
        "dated_repository_research_progress_NOT_geospatial_or_model_readiness"
    )
    assert len(ledger["workstreams"]) == 6
    assert ledger["ecological_capacity_ceiling_ready"] is False
    assert ledger["eligible_area_sq_km"] is None
    assert ledger["potential_mw"] is None
    assert ledger["release_gates"]["ecological_capacity_ceiling"]["passed"] is False
    assert ledger["release_gates"]["techno_economic_2040"]["passed"] is False
    assert ledger["audit_open_findings"] == ledger["audit_finding_count"]
    ids = {row["id"] for row in ledger["workstreams"]}
    assert ids == {"electricity", "boundary", "landslide", "forest", "wetlands",
                   "modelling"}
    assert all(row["evidence"] and row["blocked"] for row in ledger["workstreams"])


def test_terrain_coverage_is_not_promoted_to_suitability():
    rows = {x["id"]: x for x in build_ledger(ROOT)["workstreams"]}
    assert rows["boundary"]["metric"] == "4,624,362"
    assert rows["boundary"]["phase"] == "validated_source"
    assert "2,596" in rows["boundary"]["blocked"]
    assert rows["landslide"]["metric"] == "39"
    assert "Alappuzha" in rows["landslide"]["blocked"]
    assert rows["forest"]["metric"] == "0 / 25"
    assert rows["wetlands"]["metric"] == "0"
    assert "not a" in rows["boundary"]["summary"]


def test_ledger_rejects_false_model_readiness():
    audit = build_audit(ROOT)
    audit["release_gates"]["techno_economic_2040"]["passed"] = True
    audit["release_gates"]["techno_economic_2040"]["blocking_checks"] = []
    with pytest.raises(AssertionError):
        build_ledger(ROOT, audit)
