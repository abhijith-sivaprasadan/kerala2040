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
    assert len(ledger["workstreams"]) == 13
    assert ledger["ecological_capacity_ceiling_ready"] is False
    assert ledger["eligible_area_sq_km"] is None
    assert ledger["potential_mw"] is None
    assert ledger["release_gates"]["ecological_capacity_ceiling"]["passed"] is False
    assert ledger["release_gates"]["techno_economic_2040"]["passed"] is False
    assert ledger["audit_open_findings"] == ledger["audit_finding_count"]
    ids = {row["id"] for row in ledger["workstreams"]}
    assert ids == {"electricity", "generators", "hydro", "grid", "wind", "lris", "lulc",
                   "boundary", "landslide", "forest", "wetlands", "industry", "modelling"}
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


def test_executed_wind_and_lris_are_descriptive_not_eligible_capacity():
    ledger = build_ledger(ROOT)
    w = ledger["wind_terrain"]
    assert w["point_centres"] == 200_692
    assert w["slope"]["finite_point_centres"] == 199_853
    assert w["slope"]["missing_point_centres"] == 839
    assert w["speed_m_s"]["median"] == 3.91
    assert w["wind_power_density_w_m2"]["median"] == 78.9255
    matrix = w["sensitivity"]["matching_point_centre_counts_in_row_column_order"]
    assert matrix[2][1] == 8_637
    assert w["sensitivity"]["denominator_for_percentages"] == 199_853
    assert w["candidate_area_km2"] is None
    assert w["feasible_capacity_MW"] is None
    assert w["model_admitted"] is False
    assert ledger["lris"]["district_count"] == 14
    assert ledger["lris"]["wfs_result"] == "Service WFS is disabled"
    assert ledger["lris"]["native_land_use_geometry_acquired"] is False
    assert ledger["lris"]["legal_exclusion_verified"] is False
    assert ledger["lris"]["model_admitted"] is False


def test_incomplete_district_partition_cannot_look_like_complete_gis():
    ledger = build_ledger(ROOT)
    d = ledger["district_qa"]
    assert d["original_point_centres"] == 200_692
    assert d["unique_district_point_centres"] == 200_362
    assert d["unassigned_point_centres"] == 330
    assert d["ambiguous_point_centres"] == 0
    assert d["unique_district_point_centres"] + d["unassigned_point_centres"] == d["original_point_centres"]
    assert d["matched_slope_finite"] + d["unassigned_slope_finite"] == 199_853
    assert d["unassigned_slope_missing"] == 236
    assert d["statewide_population_reconciles_with_unassigned"] is True
    assert d["complete_district_partition"] is False
    assert d["district_publication_ready"] is False
    assert d["eligible_area_km2"] is None and d["feasible_capacity_MW"] is None
    assert d["model_admitted"] is False


def test_nwic_partition_reconciles_all_districts_without_admitting_wind_capacity():
    ledger = build_ledger(ROOT)
    record = ledger["nwic_district"]
    population = record["point_assignment"]
    districts = record["districts"]
    assert len(districts) == 14
    assert population["source_points"] == population["uniquely_assigned"] == 200_692
    assert population["unassigned"] == population["ambiguous"] == 0
    assert population["slope_finite"] == 199_853
    assert population["slope_missing"] == 839
    assert sum(d["point_centres"] for d in districts) == 200_692
    assert sum(d["slope_finite"] for d in districts) == 199_853
    assert sum(d["slope_missing"] for d in districts) == 839
    assert sum(d["delta_point_centres_vs_LRIS"] for d in districts) == 330
    assert sum(d["threshold_matrix"][2][1] for d in districts) == 8_637
    assert record["source"]["source_reuse_rights_verified"] is False
    assert record["legal_ecology_screens_verified"] is False
    assert record["eligible_area_km2"] is None
    assert record["feasible_capacity_MW"] is None
    assert record["model_admitted"] is False
    # Retain old LRIS QA as historic comparison, not a live NWIC partition blocker.
    assert ledger["district_qa"]["unassigned_point_centres"] == 330


def test_wind_phase1_is_closed_only_as_descriptive_analysis():
    ledger = build_ledger(ROOT)
    phase = ledger["wind_phase1"]
    normalized = phase["normalized"]
    assert phase["descriptive_wind_phase1_complete"] is True
    assert ledger["reviewed_date"] >= "2026-09-23"
    assert normalized["statewide"]["source_point_centres"] == 200_692
    assert normalized["statewide"]["finite_DSM_slope_point_centres"] == 199_853
    assert normalized["statewide"]["missing_DSM_slope_point_centres"] == 839
    assert normalized["qa"]["all_16_threshold_cell_counts_reconciled"]
    assert len(normalized["districts"]) == 14
    case = normalized["spotlight_descriptive_example"]
    assert case["statewide_matching_point_centres"] == 8637
    assert case["palakkad_matching_point_centres"] == 6330
    assert case["idukki_matching_point_centres"] == 1804
    assert phase["site_eligibility_verified"] is False
    assert phase["source_reuse_rights_verified"] is False
    assert phase["eligible_area_km2"] is None
    assert phase["feasible_capacity_MW"] is None
    assert phase["model_admitted"] is False
    rows = {row["id"]: row for row in ledger["workstreams"]}
    assert rows["wind"]["phase"] == "validated_source"
    assert "model gate closed" in rows["wind"]["label"]
