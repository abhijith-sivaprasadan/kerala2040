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
    wind = _json(
        root, "data/evidence/gis/niwe_150m_kerala_real_wind_DSM_slope_2026_09_22.json"
    )
    lris = _json(
        root, "data/evidence/gis/lris_public_services_discovery_2026_09_22.json"
    )
    district_qa = _json(
        root, "data/evidence/gis/niwe_lris_district_partition_qa_2026_09_22.json"
    )
    nwic_district = _json(
        root, "data/evidence/gis/niwe_nwic_district_wind_terrain_2026_09_22.json"
    )
    wind_normalized = _json(
        root, "data/evidence/gis/niwe_nwic_district_normalized_wind_terrain_2026_09_23.json"
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

    assert wind["classification"] == "NIWE_150M_KERALA_DESCRIPTIVE_RESOURCE_TERRAIN_NOT_CAPACITY"
    assert wind["Kerala_point_centres"] == 200_692
    assert wind["slope"]["finite_point_centres"] + wind["slope"]["missing_point_centres"] == wind["Kerala_point_centres"]
    assert sum(wind["wind_speed_at_150m_m_s"]["bin_counts"]) == wind["Kerala_point_centres"]
    assert sum(wind["slope"]["bin_counts"]) == wind["slope"]["finite_point_centres"]
    sensitivity = wind["physical_threshold_sensitivity"]
    assert len(sensitivity["minimum_150m_speed_m_s_inclusive"]) == 4
    assert len(sensitivity["maximum_DSM_slope_degrees_inclusive"]) == 4
    assert len(sensitivity["matching_point_centre_counts_in_row_column_order"]) == 4
    assert all(
        len(row) == 4 and all(0 <= value <= wind["slope"]["finite_point_centres"] for value in row)
        for row in sensitivity["matching_point_centre_counts_in_row_column_order"]
    )
    assert sensitivity["denominator_for_percentages"] == wind["slope"]["finite_point_centres"]
    assert (wind["candidate_area_km2"] is None and wind["feasible_capacity_MW"] is None
            and wind["model_admitted"] is False and wind["site_eligibility_verified"] is False)
    assert lris["classification"] == "LRIS_PUBLIC_PORTAL_DISCOVERY_NOT_STATUTORY_GIS_OR_SITE_ELIGIBILITY"
    assert lris["wfs"]["verified_vector_export"] is False
    assert lris["rights_and_data_limits"]["vector_land_use_exclusions_acquired"] is False
    assert lris["model_admitted"] is False
    assert district_qa["classification"] == (
        "NIWE_NWIC_KERALA_LRIS_DISTRICT_PARTITION_INCOMPLETE_DESCRIPTIVE_QA_NOT_GIS_ADMISSION"
    )
    part = district_qa["point_assignment"]
    terrain_partition = district_qa["terrain_samples"]
    assert part["original_nwic_kerala_niwe_centres"] == wind["Kerala_point_centres"]
    assert part["uniquely_matched_to_LRIS_district"] == 200_362
    assert part["not_in_any_LRIS_district"] == 330 and part["multi_district"] == 0
    assert part["uniquely_matched_to_LRIS_district"] + part["not_in_any_LRIS_district"] == wind["Kerala_point_centres"]
    assert terrain_partition["LRIS_district_assigned_finite"] + terrain_partition["outside_LRIS_finite"] == wind["slope"]["finite_point_centres"]
    assert terrain_partition["LRIS_district_assigned_missing"] + terrain_partition["outside_LRIS_missing"] == wind["slope"]["missing_point_centres"]
    assert district_qa["checks"]["all_source_points_reconciled_with_explicit_unassigned_bucket"]
    assert district_qa["checks"]["all_16_threshold_counts_reconcile_with_unassigned"]
    assert district_qa["checks"]["all_200692_centres_placed_in_LRIS_district"] is False
    assert district_qa["ready_for_complete_district_publication"] is False
    assert district_qa["eligible_area_km2"] is None and district_qa["feasible_capacity_MW"] is None
    assert district_qa["model_admitted"] is False

    assert nwic_district["classification"] == (
        "NIWE_NWIC_14_DISTRICT_DESCRIPTIVE_POINT_PARTITION_NOT_CAPACITY"
    )
    nd = nwic_district["point_assignment"]
    nr = nwic_district["districts"]
    assert len(nr) == 14 and len({row["district"] for row in nr}) == 14
    assert nd["source_points"] == nd["uniquely_assigned"] == wind["Kerala_point_centres"]
    assert nd["unassigned"] == nd["ambiguous"] == 0
    assert nd["complete_descriptive_partition"] is True
    assert nd["slope_finite"] == wind["slope"]["finite_point_centres"]
    assert nd["slope_missing"] == wind["slope"]["missing_point_centres"]
    assert sum(row["point_centres"] for row in nr) == nd["source_points"]
    assert sum(row["slope_finite"] for row in nr) == nd["slope_finite"]
    assert sum(row["slope_missing"] for row in nr) == nd["slope_missing"]
    assert sum(row["delta_point_centres_vs_LRIS"] for row in nr) == 330
    assert all(
        len(row["threshold_matrix"]) == 4
        and all(len(t) == 4 for t in row["threshold_matrix"])
        and row["slope_finite"] + row["slope_missing"] == row["point_centres"]
        for row in nr
    )
    assert all(
        sum(row["threshold_matrix"][i][j] for row in nr)
        == wind["physical_threshold_sensitivity"][
            "matching_point_centre_counts_in_row_column_order"
        ][i][j]
        for i in range(4) for j in range(4)
    )
    assert nwic_district["source"]["source_reuse_rights_verified"] is False
    assert nwic_district["legal_ecology_screens_verified"] is False
    assert nwic_district["eligible_area_km2"] is None
    assert nwic_district["feasible_capacity_MW"] is None
    assert nwic_district["model_admitted"] is False

    assert wind_normalized["classification"] == (
        "NIWE_NWIC_DISTRICT_NORMALIZED_DESCRIPTIVE_WIND_TERRAIN_SENSITIVITY_NOT_SUITABILITY"
    )
    normal_rows = wind_normalized["districts"]
    assert len(normal_rows) == len(nr) == 14
    assert [r["district"] for r in normal_rows] == [r["district"] for r in nr]
    assert wind_normalized["statewide"]["source_point_centres"] == 200_692
    assert wind_normalized["statewide"]["finite_DSM_slope_point_centres"] == 199_853
    assert wind_normalized["statewide"]["missing_DSM_slope_point_centres"] == 839
    assert wind_normalized["statewide"]["threshold_count_matrix"] == (
        wind["physical_threshold_sensitivity"]["matching_point_centre_counts_in_row_column_order"]
    )
    assert all(
        r["valid_slope_point_centres"] == raw["slope_finite"]
        and r["niwe_point_centres"] == raw["point_centres"]
        and r["counts"] == raw["threshold_matrix"]
        and all(
            abs(r["percent_of_district_valid_slope_centres"][i][j]
                - 100 * r["counts"][i][j] / raw["slope_finite"]) < 0.000051
            for i in range(4) for j in range(4)
        )
        for r, raw in zip(normal_rows, nr, strict=True)
    )
    assert wind_normalized["qa"]["all_16_threshold_cell_counts_reconciled"] is True
    assert wind_normalized["eligible_area_km2"] is None
    assert wind_normalized["feasible_capacity_MW"] is None
    assert wind_normalized["model_admitted"] is False

    workstreams = [
        {
            "id": "electricity", "title": "Electricity & historical balance",
            "phase": "partial", "label": "Observed days, incomplete year",
            "metric": f'{qa["observed_days"]} / {qa["expected_days"]}',
            "unit": "SLDC days verified",
            "summary": "Source-hashed daily accounting and station-level exports; no measured full-year interval load or interchange series.",
            "completed": "Daily balance source QA, import/hydro tables and official comparison. All 11 missing dates retried 2026-09-20: zero recovery, known-day control confirmed.",
            "blocked": "11 missing daily reports, interval chronology and final historical calibration.",
            "action": "Recover original SLDC reports and authenticated interval exports.",
            "route": "electricity",
            "evidence": [
                {"label": "SLDC source QA", "href": ROOT + "data/external/sldc_fy2024_25/qa_report.json"},
                {"label": "Historical daily replay method", "href": ROOT + "docs/OBSERVED_DAILY_PYPSA.md"},
                {"label": "Missing-11 public source retry", "href": "https://github.com/abhijith-sivaprasadan/kerala2040/actions/runs/35539424582"},
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
            "id": "wind", "title": "Onshore wind resource × terrain",
            "phase": "validated_source", "label": "Descriptive wind phase 1 complete; model gate closed",
            "metric": f'{wind["Kerala_point_centres"]:,}',
            "unit": "NIWE 150 m Kerala resource point centres",
            "summary": (
                f'Median modelled 150 m wind speed {wind["wind_speed_at_150m_m_s"]["median"]:.2f} m/s; '
                f'{wind["slope"]["finite_point_centres"]:,} points have sampled GLO-90 DSM slope.'
            ),
            "completed": (
                "Pinned-original NIWE and NWIC polygon clip; actual DSM slope join, "
                "16 descriptive wind/slope threshold combinations and aggregate source QA; "
                "NWIC original 14-district partition assigns all 200,692 points exactly once; "
                "district-normalized 16-cell sensitivity and original vector poster figures complete."
            ),
            "blocked": (
                "No notified land/ESZ/wetland polygons, turbine layout/production calibration, "
                "access rights or verified grid hosting. Historic LRIS geometry left "
                "330 points unassigned, but original NWIC districts close the descriptive "
                "partition. Point counts are not km² or MW."
            ),
            "action": "Join authorised, source-dated land geometry and verified connection corridors.",
            "route": "atlas",
            "evidence": [
                {"label": "Executed wind × terrain report", "href": ROOT + "docs/NIWE_150M_KERALA_TERRAIN_REAL_DATA_RESULT_2026_09_22.md"},
                {"label": "Aggregate source QA", "href": ROOT + "data/evidence/gis/niwe_150m_kerala_real_wind_DSM_slope_2026_09_22.json"},
                {"label": "NWIC district real-data analysis", "href": ROOT + "docs/NIWE_NWIC_DISTRICT_WIND_TERRAIN_RESULT_2026_09_22.md"},
                {"label": "NWIC district aggregate", "href": ROOT + "data/evidence/gis/niwe_nwic_district_wind_terrain_2026_09_22.json"},
                {"label": "Wind phase 1 closeout", "href": ROOT + "docs/WIND_PHASE1_DISTRICT_NORMALIZED_CLOSEOUT_2026_09_23.md"},
                {"label": "Normalized district sensitivity QA", "href": ROOT + "data/evidence/gis/niwe_nwic_district_normalized_wind_terrain_2026_09_23.json"},
                {"label": "Historic LRIS boundary mismatch", "href": ROOT + "docs/NIWE_LRIS_DISTRICT_PARTITION_QA_2026_09_22.md"},
            ],
        },
        {
            "id": "lris", "title": "LRIS 2.0 land-use service discovery",
            "phase": "partial", "label": "Public portal categories; no source vectors",
            "metric": "14",
            "unit": "districts advertising land use, roads, slope and water",
            "summary": (
                "Observed administrative GeoJSON, category-area summaries and WMS imagery; "
                "the tested public WFS explicitly reports disabled."
            ),
            "completed": "Public service discovery and historic LRIS 330-point geometry mismatch audited; a separate original NWIC district source now closes the descriptive partition.",
            "blocked": "Underlying class-coded land-use polygons, source vintage/CRS/rights and statutory land boundaries not acquired.",
            "action": "Seek authorised native class-coded land-use vectors and independently notified legal layers; review NWIC source-vintage and use terms.",
            "route": "atlas",
            "evidence": [
                {"label": "LRIS source/service evidence", "href": ROOT + "data/evidence/gis/lris_public_services_discovery_2026_09_22.json"},
                {"label": "District geometry mismatch QA", "href": ROOT + "data/evidence/gis/niwe_lris_district_partition_qa_2026_09_22.json"},
            ],
        },
        {
            "id": "lulc", "title": "Land use & land cover",
            "phase": "blocked", "label": "Native class-coded raster not acquired",
            "metric": "0",
            "unit": "verified current native Kerala rasters",
            "summary": "The FY2024–25 Bhuvan visual theme is not a native categorical layer or legal forest map.",
            "completed": "NRSC/Bhuvan source paths and LRIS public service discovery; no native class-coded GIS admitted.",
            "blocked": "No hash-verified native raster/vector, full class legend, CRS, coverage QA or use rights; LRIS WFS tested disabled.",
            "action": "Acquire authorised original LULC and validate class codes before land screening.",
            "route": "atlas",
            "evidence": [
                {"label": "LRIS service inventory", "href": ROOT + "data/evidence/gis/lris_public_services_discovery_2026_09_22.json"},
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
            "id": "industry", "title": "Circular industry & KMML",
            "phase": "blocked", "label": "Measured process boundary required",
            "metric": "KMML",
            "unit": "selected case; no validated numerical recovery result",
            "summary": "Recovery proposals need chemistry, measured mass/energy flows, costs and offtake.",
            "completed": "Primary industrial case and the measurement requirements identified.",
            "blocked": "No validated residue throughput, yields, heat, water or financing boundary.",
            "action": "Acquire metered data and close mass, energy and cost balances.",
            "route": "industry",
            "evidence": [
                {"label": "KMML case plan", "href": ROOT + "docs/KMML_CASE_PLAN.md"},
                {"label": "Release-gate rules", "href": ROOT + "docs/AUDIT_RELEASE_GATES.md"},
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
        "reviewed_date": max(gis["review_date"], wind["reviewed_date"], lris["reviewed_date"], wind_normalized["reviewed_date"]),
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
        "nwic_district": nwic_district,
        "wind_phase1": {
            "classification": wind_normalized["classification"],
            "descriptive_wind_phase1_complete": True,
            "normalized": wind_normalized,
            "site_eligibility_verified": False,
            "source_reuse_rights_verified": False,
            "eligible_area_km2": None,
            "feasible_capacity_MW": None,
            "hourly_generation_validated": False,
            "model_admitted": False,
        },
        "district_qa": {
            "classification": district_qa["classification"],
            "original_point_centres": part["original_nwic_kerala_niwe_centres"],
            "unique_district_point_centres": part["uniquely_matched_to_LRIS_district"],
            "unassigned_point_centres": part["not_in_any_LRIS_district"],
            "ambiguous_point_centres": part["multi_district"],
            "matched_slope_finite": terrain_partition["LRIS_district_assigned_finite"],
            "unassigned_slope_finite": terrain_partition["outside_LRIS_finite"],
            "unassigned_slope_missing": terrain_partition["outside_LRIS_missing"],
            "statewide_population_reconciles_with_unassigned": True,
            "complete_district_partition": False,
            "district_publication_ready": False,
            "eligible_area_km2": None,
            "feasible_capacity_MW": None,
            "model_admitted": False,
        },
        "wind_terrain": {
            "classification": wind["classification"],
            "reviewed_date": wind["reviewed_date"],
            "point_centres": wind["Kerala_point_centres"],
            "source_height_m": 150,
            "source_nominal_grid_m": 500,
            "speed_m_s": wind["wind_speed_at_150m_m_s"],
            "wind_power_density_w_m2": wind["wind_power_density_W_per_m2"],
            "slope": wind["slope"],
            "sensitivity": sensitivity,
            "candidate_area_km2": wind["candidate_area_km2"],
            "feasible_capacity_MW": wind["feasible_capacity_MW"],
            "model_admitted": wind["model_admitted"],
        },
        "lris": {
            "classification": lris["classification"],
            "district_count": 14,
            "wfs_result": lris["wfs"]["exception_text_user_observed"],
            "native_land_use_geometry_acquired": False,
            "legal_exclusion_verified": False,
            "model_admitted": False,
        },
        "caution": (
            "An acquired file, successful workflow or candidate repaired shape is "
            "not an independently accepted legal boundary, measured chronology "
            "or viable MW potential."
        ),
    }
