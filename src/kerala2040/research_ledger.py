"""Generate a publishable, fail-closed research-workbench ledger from committed QA.

This is a progress/evidence index, not a spatial file, source replacement,
legal exclusion map or numerical 2040 planning output.
"""
from __future__ import annotations

import json
from pathlib import Path

import yaml

from kerala2040.audit_readiness import build_audit

ROOT = "https://github.com/abhijith-sivaprasadan/kerala2040/blob/main/"


def _yaml(root: Path, path: str) -> dict:
    return yaml.safe_load((root / path).read_text(encoding="utf-8"))


def _json(root: Path, path: str) -> dict:
    return json.loads((root / path).read_text(encoding="utf-8"))


def build_ledger(root: Path, audit: dict | None = None) -> dict:
    """Reconcile indicators against underlying committed evidence, not a UI claim."""
    if audit is None:
        audit = build_audit(root)
    gis = _yaml(root, "configs/gis_forest_dem_wetlands_hazards_2026.yaml")
    forest = gis["workstreams"]["forest_protected_areas"]
    terrain = gis["workstreams"]["elevation_dem"]
    hazard = gis["workstreams"]["wetlands_waterbodies_landslide"]
    wdpa = _yaml(root, "configs/kerala_protected_area_crosswalk_2026.yaml")
    lulc = _yaml(root, "configs/lulc_native_acquisition_2024_25.yaml")
    hydro = _yaml(root, "configs/hydro_topology_evidence_2024_25.yaml")
    transfer = _yaml(root, "configs/grid_transfer_contract_evidence_2024_25.yaml")
    generator = _yaml(root, "configs/generator_reconciliation_2024_25.yaml")
    qa = _json(root, "data/external/sldc_fy2024_25/qa_report.json")
    boundary = _json(
        root, "data/evidence/gis/nwic_kerala_boundary_dem_tile_intersections_2026_09_20.json"
    )
    forest_source = _json(
        root, "data/evidence/gis/forest_protected_area_source_audit_2026_09_20.json"
    )
    model = gis["model_use"]
    gates = audit["release_gates"]

    assert audit["classification"] == "repository_evidence_audit_not_external_source_validation"
    assert qa["observed_days"] + len(qa["missing_dates"]) == qa["expected_days"] == 365
    assert boundary["missing_source_tile_intersection_with_official_kerala"]["count"] == 0
    assert forest_source["verified_geometry_archives"] == forest["verified_geometry_archives"] == 0
    assert forest["wdpa_unique_matches_to_25_kfd_designations"] == 0
    assert len(wdpa["protected_areas"]) == 25
    assert lulc["model_use"]["native_kerala_lulc_acquired"] is False
    assert transfer["model_use"]["can_apply_snapshot_as_full_year_import_limit"] is False
    assert hydro["classification"] == "partial_official_hydro_topology_not_dispatch_constraints"
    assert generator["release_gate"] == "partial_or_provisional"
    assert not gates["kmml_case"]["passed"]
    assert hazard["gsi_total_source_features"] == hazard["gsi_invalid_source_features"] == 39
    assert hazard["wetland_geometries_verified"] == 0
    assert terrain["nwic_kerala_native_grid_dsm_pixel_centres_verified"] is True
    assert terrain["geospatial_mosaic_coverage_verified"] is False
    assert model["ecological_capacity_ceiling_ready"] is False
    assert model["eligible_area_sq_km"] is None and model["potential_mw"] is None
    assert not gates["ecological_capacity_ceiling"]["passed"]
    assert not gates["techno_economic_2040"]["passed"]

    workstreams = [
        {
            "id": "electricity", "title": "Electricity & historical balance",
            "phase": "partial", "label": "Observed days, incomplete year",
            "metric": f'{qa["observed_days"]} / {qa["expected_days"]}',
            "unit": "SLDC days verified",
            "summary": "Source-hashed daily accounting and station-level exports; no measured full-year interval load or interchange series.",
            "completed": "Daily balance source QA, import/hydro tables and dated official comparison.",
            "blocked": "11 missing daily reports, interval chronology and final historical calibration.",
            "action": "Recover original SLDC reports and authenticated interval exports.",
            "route": "electricity",
            "evidence": [
                {"label": "SLDC source QA", "href": ROOT + "data/external/sldc_fy2024_25/qa_report.json"},
                {"label": "Historical daily replay method", "href": ROOT + "docs/OBSERVED_DAILY_PYPSA.md"},
            ],
        },
        {
            "id": "generators", "title": "Power plants & asset inventory",
            "phase": "partial", "label": "Crosschecked assets, incomplete fleet",
            "metric": str(len(generator["official_commissioned_during_fy"])),
            "unit": "FY2024–25 projects crosschecked",
            "summary": "KSEBL project status is not the complete operating generator fleet.",
            "completed": "CEA and Kerala Economic Review crosschecks correct Thottiyar and Pallivasal Extension commissioning.",
            "blocked": "Non-KSEBL ownership, project aliases, actual generation and availability are unreconciled.",
            "action": "Reconcile source-versioned units and actual output at the FY boundary.",
            "route": "electricity",
            "evidence": [
                {"label": "Generator audit", "href": ROOT + "docs/GENERATOR_REGISTER_FY2024_25_RECONCILIATION.md"},
                {"label": "Crosschecked records", "href": ROOT + "configs/generator_reconciliation_2024_25.yaml"},
            ],
        },
        {
            "id": "hydro", "title": "Hydro & reservoir operations",
            "phase": "partial", "label": "Topology documented, physics open",
            "metric": str(len(hydro["observed_reservoirs"])),
            "unit": "selected source-linked reservoir nodes",
            "summary": "Qualitative cascades are not a calibrated water-balance model.",
            "completed": "Observed-day station/reservoir tables and selected sourced links.",
            "blocked": "Inflow, release, spill, head, rule curves and shared-water accounting remain open.",
            "action": "Acquire operations and reconcile common reservoir complexes.",
            "route": "electricity",
            "evidence": [
                {"label": "Hydro audit", "href": ROOT + "docs/HYDRO_RESERVOIR_OPERATIONS_AUDIT.md"},
                {"label": "Hydro topology", "href": ROOT + "configs/hydro_topology_evidence_2024_25.yaml"},
            ],
        },
        {
            "id": "grid", "title": "Imports, grid & contracts",
            "phase": "partial", "label": "Dated snapshots, no FY constraint",
            "metric": str(len(transfer["transfer_snapshots"])),
            "unit": "transfer-capability reference dates",
            "summary": "Daily energy, TTC/ATC, contracted MW and delivered electricity have different boundaries.",
            "completed": "SLDC interface groups and January/March public capability references audited.",
            "blocked": "Full-year ATC revisions, actual interchange and contract-level prices unavailable.",
            "action": "Acquire dated SRPC revisions and KSEBL metered/scheduled contracts.",
            "route": "electricity",
            "evidence": [
                {"label": "Grid audit", "href": ROOT + "docs/GRID_TRANSFER_CONTRACTS_FY2024_25_AUDIT.md"},
                {"label": "Transfer register", "href": ROOT + "configs/grid_transfer_contract_evidence_2024_25.yaml"},
            ],
        },
        {
            "id": "lulc", "title": "Land use & land cover",
            "phase": "blocked", "label": "Native class-coded raster not acquired",
            "metric": "0",
            "unit": "verified current native Kerala rasters",
            "summary": "The FY2024–25 Bhuvan visual theme is not a native categorical layer or legal forest map.",
            "completed": "NRSC/Bhuvan source paths, scale and exact legend requirements documented.",
            "blocked": "No hash-verified native raster, full class legend, CRS, coverage QA or use rights.",
            "action": "Acquire authorised original LULC and validate class codes before land screening.",
            "route": "atlas",
            "evidence": [
                {"label": "NRSC LULC audit", "href": ROOT + "docs/NRSC_LULC_NATIVE_ACQUISITION_AUDIT.md"},
                {"label": "LULC register", "href": ROOT + "configs/lulc_native_acquisition_2024_25.yaml"},
            ],
        },
        {
            "id": "boundary", "title": "Kerala boundary & terrain",
            "phase": "validated_source", "label": "Native-grid source coverage verified",
            "metric": f'{terrain["nwic_kerala_native_grid_finite_boundary_pixel_centres"]:,}',
            "unit": "finite native-grid pixel centres",
            "summary": "NWIC Kerala boundary and hash-verified Copernicus GLO-90 surface raster; source-grid coverage is not a terrain-suitability map.",
            "completed": f'{terrain["downloaded_glo90_original_tiles_in_artifact"]} original tiles; none of the six unavailable envelope tiles intersects this boundary.',
            "blocked": f'{terrain["nwic_kerala_projected_nonfinite_boundary_pixel_centres"]:,} projected-grid boundary centres non-finite; DSM is not bare-earth DTM; no technology slope rules.',
            "action": "Resolve projected-grid edge cells and validate technology-specific terrain treatment.",
            "route": "atlas",
            "evidence": [
                {"label": "NWIC polygon and tile intersection QA", "href": ROOT + "data/evidence/gis/nwic_kerala_boundary_dem_tile_intersections_2026_09_20.json"},
                {"label": "Boundary-clipped DSM/slope source run", "href": terrain["nwic_kerala_dsm_slope_qa_run"]},
            ],
        },
        {
            "id": "landslide", "title": "GSI 2022 landslide susceptibility",
            "phase": "partial", "label": "Official source decoded, geometry held",
            "metric": str(hazard["gsi_total_source_features"]),
            "unit": "source features requiring admission",
            "summary": "Thirteen KSDMA-hosted district files expose Low, Moderate and High susceptibility, not statutory development exclusions.",
            "completed": "Originals decoded, source hashes and three repair methods compared.",
            "blocked": "All 39 source geometries invalid; candidate repairs not ground truth; Alappuzha absent from the source list.",
            "action": "Adjudicate repair boundaries with source custodian before overlay.",
            "route": "atlas",
            "evidence": [
                {"label": "GSI geometry and source audit", "href": ROOT + "docs/FOREST_DEM_WETLANDS_LANDSLIDE_GIS_AUDIT.md"},
                {"label": "Repair-comparison workflow", "href": "https://github.com/abhijith-sivaprasadan/kerala2040/actions/runs/35514485905"},
            ],
        },
        {
            "id": "forest", "title": "Forests & protected areas",
            "phase": "blocked", "label": "Statutory polygons not acquired",
            "metric": str(forest["wdpa_unique_matches_to_25_kfd_designations"]) + " / 25",
            "unit": "secondary polygon matches",
            "summary": "Official protected-area names and reported areas are distinct from legal geospatial boundaries.",
            "completed": "KFD source-route audit, complete-ID WDPA point/polygon query and 2025 government area reconciliation.",
            "blocked": "Eight official ZIP requests returned 403, one 404; four WDPA polygons matched none of the 25 KFD designations.",
            "action": "Acquire gazette-linked KFD/KSDI forest and protected-area polygons.",
            "route": "atlas",
            "evidence": [
                {"label": "WDPA/KFD crosswalk decision", "href": ROOT + "docs/WDPA_KFD_PROTECTED_AREA_CROSSWALK_AUDIT.md"},
                {"label": "Original KFD source audit", "href": ROOT + "data/evidence/gis/forest_protected_area_source_audit_2026_09_20.json"},
            ],
        },
        {
            "id": "wetlands", "title": "Wetlands & waterbodies",
            "phase": "blocked", "label": "No legally verified polygons",
            "metric": str(hazard["current_notified_wetland_geometries_verified"]),
            "unit": "notified wetland geometries",
            "summary": "SWAK/DoECC/WIAMS sources and final notifications must be separated from draft briefs and background maps.",
            "completed": "Reproducible official-page and candidate-document audit.",
            "blocked": "No verified final wetland or waterbody vector, zones of influence or polygon-to-notification linkage.",
            "action": "Acquire notification-linked wetland and waterbody vectors with version and use rights.",
            "route": "atlas",
            "evidence": [
                {"label": "GIS wetland source audit", "href": ROOT + "docs/FOREST_DEM_WETLANDS_LANDSLIDE_GIS_AUDIT.md"},
                {"label": "SWAK source-check workflow", "href": "https://github.com/abhijith-sivaprasadan/kerala2040/actions/runs/35533008587"},
            ],
        },
        {
            "id": "modelling", "title": "2040 model & reliability",
            "phase": "blocked", "label": "Release gate not passed",
            "metric": "Not calibrated",
            "unit": "no published Kerala 2040 optimisation",
            "summary": "Scenario choices and external CSTEP/CN50 benchmarks are not forecast outputs from this project.",
            "completed": "Observed-day replay, scenario specifications and provisional stress-test framework.",
            "blocked": "Hourly observations, costs, grid deliverability, hydro physics and ecological siting remain unresolved.",
            "action": "Close historical, resource, cost and physical gates before publishing modelled pathways.",
            "route": "pathways",
            "evidence": [
                {"label": "Release-gate method", "href": ROOT + "docs/AUDIT_RELEASE_GATES.md"},
                {"label": "Modelling roadmap", "href": ROOT + "docs/MODELLING_DATA_ROADMAP.md"},
            ],
        },
    ]
    if len({row["id"] for row in workstreams}) != len(workstreams):
        raise ValueError("Duplicate research workstream ID")
    if any(not row["evidence"] or not row["blocked"] for row in workstreams):
        raise ValueError("Research ledger lacks evidence or limit")
    return {
        "classification": "dated_repository_research_progress_NOT_geospatial_or_model_readiness",
        "reviewed_date": gis["review_date"],
        "scope": "Kerala, historical FY2024-25 and planning horizon 2040",
        "audit_finding_count": audit["finding_count"],
        "audit_open_findings": audit["open_findings"],
        "release_gates": {
            key: {"passed": bool(gate["passed"]), "blocking_checks": gate["blocking_checks"]}
            for key, gate in gates.items()
        },
        "ecological_capacity_ceiling_ready": False,
        "eligible_area_sq_km": None,
        "potential_mw": None,
        "workstreams": workstreams,
        "caution": (
            "An acquired file, successful workflow or candidate repaired shape is "
            "not an independently accepted legal boundary, measured chronology "
            "or viable MW potential."
        ),
    }
