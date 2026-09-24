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
    sldc_history = _json(
        root, "data/evidence/sldc/sldc_five_section_2019_2026_public_qa_2026_09_23.json"
    )
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
    solar_phase1 = _json(
        root, "data/evidence/solar/gsa2_nwic_district_paired_seasonality_2026_09_23.json"
    )
    kmml = _json(
        root, "data/evidence/industry/kmml_source_bounded_case_2026_09_24.json"
    )
    total_energy = _json(
        root, "data/evidence/total_energy/kerala_total_energy_source_register_2026_09_24.json"
    )
    annual_sales = _json(
        root, "data/evidence/total_energy/ppac_full_fy_kerala_source_audit_2026_09_24.json"
    )
    ghg = _json(
        root, "data/evidence/total_energy/kerala_ghg_sector_bridge_2026_09_24.json"
    )
    # Synthetic WP6 output is admitted as a bounded experiment, never as grid evidence.
    from kerala2040.flexibility_cooling import build_pilot

    flex = build_pilot()
    assert flex["classification"] == (
        "WP6_SYNTHETIC_24H_1R1C_COOLING_COMPARISON_NOT_KERALA_GRID_RESULT"
    )
    assert all(value is False for value in flex["science_gates"].values())
    assert len(flex["sensitivity"]) == 9
    model = gis["model_use"]
    gates = audit["release_gates"]

    assert audit["classification"] == "repository_evidence_audit_not_external_source_validation"
    assert qa["observed_days"] + len(qa["missing_dates"]) == qa["expected_days"] == 365
    assert sldc_history["classification"] == "SLDC_REPORTED_DAILY_OBSERVATIONS_NOT_CONTINUOUS_INTERVAL"
    assert sldc_history["calendar_days"] == 2606
    assert sldc_history["accepted_html_date_sha256_failed_count"] == 0
    assert sldc_history["sections"]["statistics"]["accepted"] == 2576
    assert sldc_history["sections"]["imports"]["accepted"] == 2576
    assert sldc_history["sections"]["storage"]["accepted"] == 2577
    assert sldc_history["sections"]["availability"]["accepted"] == 2577
    assert sldc_history["sections"]["other_extrema"]["accepted"] == 2577
    assert sldc_history["source_schema_versions"]["statistics:station_generation_without_full_energy_balance"] == 614
    assert sldc_history["source_schema_versions"]["statistics:full_energy_balance"] == 1962
    assert len(sldc_history["balance_anomalies"]) == 1
    assert sldc_history["balance_anomalies"][0]["date"] == "2019-12-05"
    assert sldc_history["model_admitted_as_hourly_chronology"] is False
    assert boundary["missing_source_tile_intersection_with_official_kerala"]["count"] == 0
    assert forest_source["verified_geometry_archives"] == forest["verified_geometry_archives"] == 0
    assert forest["wdpa_unique_matches_to_25_kfd_designations"] == 0
    assert len(wdpa["protected_areas"]) == 25
    assert lulc["model_use"]["native_kerala_lulc_acquired"] is False
    assert transfer["model_use"]["can_apply_snapshot_as_full_year_import_limit"] is False
    assert hydro["classification"] == "partial_official_hydro_topology_not_dispatch_constraints"
    assert generator["release_gate"] == "partial_or_provisional"
    assert not gates["kmml_case"]["passed"]
    assert kmml["classification"] == (
        "KMML_CHAVARA_SOURCE_BOUNDED_PROCESS_CASE_NOT_MEASURED_2024_25_NOT_RECOVERY_FORECAST"
    )
    assert len(kmml["units"]) == 9 and len(kmml["streams"]) == 10
    assert kmml["scientific_scope"]["kmml_case_release_gate_passed"] is False
    assert kmml["published_numeric_recovery_by_Kerala2040"] is None
    assert all(
        stream["annual_tonnes"] is None
        and stream["annual_mwh"] is None
        and stream["avoided_co2_t"] is None
        for stream in kmml["streams"]
    )
    assert total_energy["emc_final_energy"]["baseline_total_mtoe"] == 10.78
    assert len(total_energy["emc_final_energy"]["observed_years"]) == 6
    assert total_energy["quantities_deliberately_null"]["kerala_total_final_energy_fy2024_25_mtoe"] is None
    assert annual_sales["annual_kerala_rows"][-1]["all_pol_tier"] == (
        "secondary_transcription_unverified_at_primary"
    )
    assert annual_sales["qa"]["primary_fy2024_25_pdf_image_verified"] is False
    assert annual_sales["unsupported_current_results"]["fy2024_25_kerala_total_final_energy_mtoe"] is None
    assert ghg["classification"] == "KERALA_GHG_2023_OFFICIAL_SECTOR_EMISSIONS_NOT_FINAL_ENERGY_OR_2024_25"
    assert ghg["energy_sector_2023_mtco2e"] == 20.64
    assert ghg["period"] == "calendar_2023"
    assert ghg["no_assumed_energy_2024_25_mtoe"] is None
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

    assert solar_phase1["classification"] == (
        "GSA2_1999_2018_NWIC_KERALA_PVOUT_DISTRICT_PAIRED_SEASONALITY_DESCRIPTIVE_NOT_MW"
    )
    sp = solar_phase1["qa"]
    ss = solar_phase1["statewide"]
    sr = solar_phase1["districts"]
    assert solar_phase1["solar_phase1_descriptive_complete"] is True
    assert len(sr) == 14 and len({r["district"] for r in sr}) == 14
    assert ss["source_pixel_centres"] == sp["NWIC_Kerala_district_pixels"] == 46_241
    assert sum(r["finite_native_source_pixel_centres"] for r in sr) == 46_241
    assert sp["inside_district_missing_any_of_14_PVOUT_layers"] == 0
    assert sp["inside_district_multiple_assignments"] == 0
    assert sp["all_14_district_counts_reconcile"] is True
    assert sp["original_14_rasters_sha256_verified_against_uploaded_manifest"] is True
    assert sp["no_resampling"] is True
    assert sp["annual_source_mask_metadata_disagrees_with_actual_finite_values"] is True
    assert len(ss["monthly_marginal_pixel_median_PVOUT_kWh_kWp_day"]) == 12
    assert ss["median_paired_Feb_minus_Jul_kWh_kWp_day"] == 2.267
    assert abs(ss["median_paired_Feb_to_Jul_drop_pct"] - 43.60289) < 0.000001
    assert solar_phase1["source"]["copyright_and_reuse_rights_independently_verified"] is False
    assert solar_phase1["eligible_area_km2"] is None
    assert solar_phase1["installed_capacity_MW"] is None
    assert solar_phase1["model_admitted"] is False

    workstreams = [
        {
            "id": "electricity", "title": "Electricity & historical balance",
            "phase": "partial", "label": "2019–2026 reported daily archive audited; interval chronology missing",
            "metric": "2,575 / 2,606",
            "unit": "energy-balance-qualified reported days",
            "summary": "Five dated SLDC daily sections across 2019–2026; 2,576 Statistics and Imports days, 2,577 Storage/Availability/Extrema days. Not measured hourly telemetry.",
            "completed": "13,030 date-section statuses hash-checked; 614 early and 1,962 later Statistics layouts kept distinct. All paired import totals match; anomalous 2019-12-05 balance excluded from qualified consumption. FY2024–25 remains 354/365 days.",
            "blocked": "30 missing Statistics/Imports dates, 29 missing Storage/Availability/Extrema dates, partial reservoir subsections, and no independently measured full-year interval demand or generation.",
            "action": "Audit field coverage and obtain authenticated interval meter/SLDC exports.",
            "route": "electricity",
            "evidence": [
                {"label": "Multi-year source audit", "href": ROOT + "docs/SLDC_FIVE_SECTION_2019_2026_SOURCE_AUDIT_2026_09_23.md"},
                {"label": "Multi-year QA", "href": ROOT + "data/evidence/sldc/sldc_five_section_2019_2026_public_qa_2026_09_23.json"},
                {"label": "SLDC FY24–25 source QA", "href": ROOT + "data/external/sldc_fy2024_25/qa_report.json"},
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
            "id": "solar", "title": "Solar PV source resource × paired seasonality",
            "phase": "validated_source", "label": "Descriptive solar phase 1 complete; model gate closed",
            "metric": f'{ss["source_pixel_centres"]:,}',
            "unit": "native GSA 2.0 Kerala PVOUT pixel centres",
            "summary": (
                f'Long-term median annual PVOUT {ss["median_annual_PVOUT_kWh_kWp"]:.2f} '
                f'kWh/kWp; median paired Feb-to-Jul decline '
                f'{ss["median_paired_Feb_to_Jul_drop_pct"]:.2f}%.'
            ),
            "completed": (
                "All 14 original yearly/daily/monthly native source windows and NWIC "
                "district polygons audited. 46,241 valid pixels assigned exactly once "
                "with complete 12-month masks; paired within-pixel seasonality and "
                "three original vector poster figures are source-qualified."
            ),
            "blocked": (
                "Publisher reference-PV climatology is not FY2024-25 metered solar. "
                "No statutory rooftop/land/water eligibility, module calibration, "
                "verified hourly output, grid hosting, buildable area or installed MW; "
                "original source usage rights await review."
            ),
            "action": "Obtain monitored Kerala PV chronology and permitted technology-specific site/roof geometry.",
            "route": "atlas",
            "evidence": [
                {"label": "Solar phase 1 report", "href": ROOT + "docs/SOLAR_PHASE1_NWIC_DISTRICT_SEASONALITY_RESULT_2026_09_23.md"},
                {"label": "District paired solar aggregate", "href": ROOT + "data/evidence/solar/gsa2_nwic_district_paired_seasonality_2026_09_23.json"},
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
            "phase": "partial", "label": "Process case source-audited; measured flow gate blocked",
            "metric": "9 units / 10 streams",
            "unit": "source-qualified topology, not recovered tonnes or MWh",
            "summary": "KMML's 9 distinct production/recovery/utility units, 10 residual loops and FY2022–23 recovery trials are documented; plant-wide recovery unmeasured.",
            "completed": "Official topology and ARP acid loop sourced; historic brick commercialization distinguished from the FY2022–23 oxide-to-sponge-iron, U400 fines and backwash trials. Ten streams retain null annual benefits.",
            "blocked": "No common-period plant meters, chemistry, disposal permits, accepted buyers, energy/water allocation, FY2024–25 site balance or actual commissioning of trials. KMML numerical release gate remains closed.",
            "action": "Obtain site-approved aligned monthly/interval flow assays, treatment/reuse and purchase meters, KSPCB primary records, current trial status and capex/offtake contracts.",
            "route": "industry",
            "evidence": [
                {"label": "KMML completed process case", "href": ROOT + "docs/KMML_CIRCULAR_INDUSTRY_CASE_2026_09_24.md"},
                {"label": "KMML public-safe case data", "href": ROOT + "data/evidence/industry/kmml_source_bounded_case_2026_09_24.json"},
                {"label": "KMML case plan", "href": ROOT + "docs/KMML_CASE_PLAN.md"},
                {"label": "Release-gate rules", "href": ROOT + "docs/AUDIT_RELEASE_GATES.md"},
            ],
        },
        {
            "id": "total-energy", "title": "Total energy, oil, sector emissions",
            "phase": "partial", "label": "Three dated source boundaries; no current complete energy balance",
            "metric": "10.78 Mtoe historic / 20.64 MtCO₂e CY2023",
            "unit": "distinct TFEC and energy-emissions measures, not additive",
            "summary": "Historic EMC final energy, six-year PPAC sales and 2023 official fuel-use emissions are now source-tiered on separate year, sector and accounting boundaries.",
            "completed": "Six historical EMC FY total-final-energy values, FY2019–20 rounded oil/electricity/coal/gas shares, annual petroleum sales FY2019–20–FY2024–25, and official 2023 transport/residential/industrial emissions; heating-value method and source conflicts documented.",
            "blocked": "No original EMC fuel×sector workbook, FY2015 correction, primary PDF verification of PPAC FY2024–25, full native PPAC file, same-year NCVs, final fuel-use allocation or border import balance. GHG 2020 inventory vintages disagree.",
            "action": "Request publication-cleared EMC/DoECC source tables, original PPAC full-year state×product data and revision notes; do not derive current Kerala final-energy Mtoe or import share from sales/emissions.",
            "route": "overview",
            "evidence": [
                {"label": "Energy atlas historical baseline", "href": ROOT + "docs/KERALA_TOTAL_ENERGY_ATLAS_BASELINE_2026_09_24.md"},
                {"label": "PPAC full-year source audit", "href": ROOT + "docs/PPAC_KERALA_FULL_YEAR_SALES_SOURCE_AUDIT_2026_09_24.md"},
                {"label": "Official sector GHG and source method", "href": ROOT + "docs/KERALA_TOTAL_ENERGY_ATLAS_SECTOR_GHG_METHODS_2026_09_24.md"},
                {"label": "Dated GHG and GCV register", "href": ROOT + "data/evidence/total_energy/kerala_ghg_sector_bridge_2026_09_24.json"},
            ],
        },
        {
            "id": "flexibility", "title": "WP6 cooling, storage and demand flexibility",
            "phase": "partial", "label": "Executable synthetic physics; site and grid calibration absent",
            "metric": "3 cases / 9 sensitivities",
            "unit": "one synthetic zone / 24 illustrative hours, not Kerala MW",
            "summary": "An auditable 1R1C building model now compares conventional AC, pre-cooling and chilled-water storage under common comfort and end-state constraints.",
            "completed": "Three reproduced 24-hour cases, detailed thermal/electric balances, direct AC and independent charging COP, 24–26 C comfort checks, night charging, morning state, evening and whole-day peak metrics, nine cold-store/COP sensitivity runs and site charts.",
            "blocked": "No real Kerala weather, operative temperature/humidity validation, audited building-load measurements, actual hourly coincident grid peak, selected plant COP, tariffs, CO2, capex or annual Kerala scaling. Other WP6 EV/BESS/pumped/industrial cases are not completed.",
            "action": "Validate source-approved building and cooling plant data, add humidity/occupancy, match Kerala hourly load, and extend to managed EV/industrial flexibility without equating shift to energy saving.",
            "route": "pathways",
            "evidence": [
                {"label": "WP6 executable pilot and physical limits", "href": ROOT + "docs/WP6_COOLING_THERMAL_STORAGE_PILOT_2026_09_24.md"},
                {"label": "WP6 synthetic input file", "href": ROOT + "configs/wp6_cooling_tes_illustrative.yaml"},
                {"label": "WP6 code", "href": ROOT + "src/kerala2040/flexibility_cooling.py"},
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
        "reviewed_date": max(gis["review_date"], wind["reviewed_date"], lris["reviewed_date"], wind_normalized["reviewed_date"], solar_phase1["reviewed_date"]),
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
        "sldc_five_section": {
            "classification": sldc_history["classification"],
            "audit": sldc_history,
            "daily_source_archived": True,
            "measured_hourly_chronology": False,
            "model_admitted_as_hourly_chronology": False,
        },
        "solar_phase1": {
            "classification": solar_phase1["classification"],
            "descriptive_solar_phase1_complete": True,
            "aggregate": solar_phase1,
            "site_eligibility_verified": False,
            "source_reuse_rights_verified": False,
            "eligible_area_km2": None,
            "installed_capacity_MW": None,
            "year_specific_hourly_generation_validated": False,
            "model_admitted": False,
        },
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
