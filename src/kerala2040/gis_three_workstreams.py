"""Validate GIS source workstreams without promoting catalogues to siting capacity."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import zipfile
from pathlib import Path
from typing import Any

import yaml

REGISTRY = "configs/gis_forest_dem_wetlands_hazards_2026.yaml"
ACQUISITION = "data/evidence/gis/official_gis_public_acquisition_2026_09_20.json"
GSI_VALIDATION = "data/evidence/gis/gsi_2022_geometry_validation_2026_09_20.json"
DEM_ENVELOPE = "data/evidence/gis/copernicus_glo90_envelope_2026_09_20.json"
EXPECTED = {"forest_protected_areas", "elevation_dem", "wetlands_waterbodies_landslide"}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def check_raster(path: Path) -> dict[str, Any]:
    """First-pass physical raster QA only; NOT area coverage, terrain truth or siting."""
    import rasterio
    from rasterio.warp import transform_bounds

    if path.suffix.lower() not in {".tif", ".tiff"}:
        raise ValueError("DEM is not an original TIFF")
    with rasterio.open(path) as src:
        if src.count != 1 or not src.crs or src.width < 2 or src.height < 2:
            raise ValueError("DEM raster band/CRS/dimensions missing")
        if any(not math.isfinite(n) or n <= 0 for n in src.res):
            raise ValueError("DEM has invalid source resolution")
        west, south, east, north = transform_bounds(
            src.crs, "EPSG:4326", *src.bounds
        )
        if east <= 74.5 or west >= 78.0 or north <= 8.0 or south >= 12.9:
            raise ValueError("DEM sample does not overlap Kerala bounding envelope")
        if src.count != 1:
            raise ValueError("DEM sample must be single-band")
        valid = sum(
            src.read(1, window=window, masked=True).count()
            for _, window in src.block_windows(1)
        )
        if valid == 0:
            raise ValueError("DEM sample contains no valid height pixels")
        return {
            "status": "single_raster_file_structure_verified_NOT_statewide_DTM",
            "sha256": sha256(path),
            "driver": src.driver,
            "crs": src.crs.to_string(),
            "nodata": src.nodata,
            "source_nodata_defined": src.nodata is not None,
            "width": src.width,
            "height": src.height,
            "source_resolution_crs_units": list(src.res),
            "bounds_wgs84": [west, south, east, north],
            "valid_pixels_in_this_file": valid,
            "vertical_datum": "not_verified_by_raster_structure",
            "surface_type": "not_established_by_raster_structure",
            "statewide_coverage_verified": False,
            "slope_threshold_validated": False,
        }


def check_shapefile_zip(path: Path) -> dict[str, Any]:
    """Inspect safe ZIP structure; members alone do not certify mapped polygons."""
    if path.suffix.lower() != ".zip":
        raise ValueError("Expected a downloaded original GSI shapefile ZIP")
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        if not names or len(names) > 10000 or any(
            item.startswith(("/", "\\")) or ".." in Path(item).parts for item in names
        ):
            raise ValueError("Malformed or unsafe geometry ZIP")
        groups: dict[str, set[str]] = {}
        for item in names:
            p = Path(item)
            groups.setdefault(str(p.with_suffix("")).casefold(), set()).add(p.suffix.lower())
        complete = [
            key for key, suffixes in groups.items()
            if {".shp", ".shx", ".dbf", ".prj"} <= suffixes
        ]
        if not complete:
            raise ValueError("GSI shapefile archive missing shp/shx/dbf/prj")
        if sum(info.file_size for info in archive.infolist()) > 2_000_000_000:
            raise ValueError("Geometry ZIP exceeds safe decompressed size")
        return {
            "status": "zip_components_qa_only_NOT_geometry_or_hazard_validated",
            "sha256": sha256(path),
            "bytes": path.stat().st_size,
            "complete_shapefile_groups": complete,
            "geometry_count_verified": False,
            "gsi_2022_class_attributes_verified": False,
            "kerala_coverage_verified": False,
        }


def audit_gis(root: Path) -> dict[str, Any]:
    registry = yaml.safe_load((root / REGISTRY).read_text(encoding="utf-8"))
    if registry.get("classification") != (
        "source_scoped_three_workstream_gis_review_not_validated_geometry"
    ):
        raise ValueError("GIS register cannot claim validated geometry")
    workstreams = registry["workstreams"]
    if set(workstreams) != EXPECTED:
        raise ValueError("Unexpected/missing GIS workstream")
    sources = registry["source_registry"]
    for name, value in sources.items():
        if not value.get("url", "").startswith("https://"):
            raise ValueError(f"GIS source URL missing or not HTTPS: {name}")
    for name, entry in workstreams.items():
        ids = entry.get("source_ids", [])
        if not ids or len(ids) != len(set(ids)) or not set(ids) <= set(sources):
            raise ValueError(f"GIS source citations absent/unknown: {name}")
    districts = workstreams["wetlands_waterbodies_landslide"]["published_gsi_district_labels"]
    if len(districts) != 13 or len(set(districts)) != 13 or "Alappuzha" in districts:
        raise ValueError("KSDMA published GSI district list must retain scope")
    allowed_false = (
        "authoritative_forest_exclusions_verified",
        "full_kerala_height_and_slope_verified",
        "wetland_waterbody_land_hazard_overlay_verified",
        "ecological_capacity_ceiling_ready",
    )
    if any(registry["model_use"][key] is not False for key in allowed_false):
        raise ValueError("GIS source catalogue cannot self-certify siting")
    if any(registry["model_use"][key] is not None for key in (
        "eligible_area_sq_km", "potential_mw"
    )):
        raise ValueError("GIS source catalogue cannot invent eligible area or MW")
    if workstreams["forest_protected_areas"]["confirmed_geometry_acquired"] is not False:
        raise ValueError("Forest data cannot be declared acquired without actual official file")
    if workstreams["elevation_dem"]["geospatial_mosaic_coverage_verified"] is not False:
        raise ValueError("DEM tile reference cannot establish statewide mosaic")
    if workstreams["wetlands_waterbodies_landslide"]["final_notifications_mapped"] is not False:
        raise ValueError("Draft wetland brief cannot turn into notified polygon")
    for name in EXPECTED:
        if workstreams[name].get("original_file_sha256") is not None:
            raise ValueError("Claimed original GIS file without committed source QA")
    acquired = json.loads((root / ACQUISITION).read_text(encoding="utf-8"))
    if acquired.get("classification") != (
        "verified_workflow_download_hashes_and_shapefile_archive_components_NOT_geospatial_or_legal_validation"
    ):
        raise ValueError("GIS acquisition manifest wrongly claims legal or spatial QA")
    pilot = acquired["public_kerala_dsm_pilot"]
    if (
        len(pilot["sha256"]) != 64
        or pilot["bytes"] <= 0
        or pilot["original_crs"] != "EPSG:4326"
        or not pilot["source_url"].startswith("https://copernicus-dem-90m.s3.amazonaws.com/")
        or pilot["classification"] != "one_2021_GLO90_DSM_tile_not_Kerala_terrain_mosaic"
    ):
        raise ValueError("Public Copernicus pilot source identity inconsistent")
    gsi = acquired["gsi_2022"]
    archives = gsi["per_district"]
    if (
        gsi["published_district_links_retrieved"] != 13
        or gsi["archives_with_shp_shx_dbf_prj"] != 13
        or {item["district"] for item in archives} != set(districts)
        or len(archives) != 13
        or gsi["geometries_crs_and_classes_independently_validated"] is not False
    ):
        raise ValueError("GSI acquired archive count or limitations inconsistent")
    if any(
        len(item["sha256"]) != 64
        or not item["source_url"].startswith(
            "https://sdma.kerala.gov.in/wp-content/uploads/2025/08/"
        )
        or not item["complete_shapefile_groups"]
        or item["structural_status"] != (
            "zip_components_qa_only_NOT_geometry_or_hazard_validated"
        )
        for item in archives
    ):
        raise ValueError("GSI official archive hashes or structural status invalid")
    gsi_validation = json.loads((root / GSI_VALIDATION).read_text(encoding="utf-8"))
    if gsi_validation.get("classification") != (
        "decoded_official_GSI_2022_geometry_validation_NOT_model_ready_overlay"
    ):
        raise ValueError("GSI geometry evidence classification mismatch")
    if (
        gsi_validation["published_packages_decoded"] != 13
        or gsi_validation["total_features"] != 39
        or gsi_validation["invalid_geometry_count_total"] != 39
        or gsi_validation["null_geometry_count_total"] != 0
        or gsi_validation["empty_geometry_count_total"] != 0
        or gsi_validation["source_crs_all_districts"] != "EPSG:32643"
        or gsi_validation["susceptibility_field"] != "Susceptibi"
        or set(gsi_validation["susceptibility_classes"]) != {"High", "Low", "Moderate"}
        or gsi_validation["susceptibility_semantics_verified"] is not True
        or gsi_validation["invalidity_reason_all_features"] != "Ring Self-intersection"
        or gsi_validation["merged_derivative_written"] is not False
        or gsi_validation["repaired_geometry_admitted_for_model_use"] is not False
        or gsi_validation["alappuzha_hazard_status_inferred"] is not False
    ):
        raise ValueError("GSI decoded geometry findings inconsistent")
    if (
        gsi_validation["eligible_area_sq_km"] is not None
        or gsi_validation["capacity_ceiling_mw"] is not None
        or gsi_validation["ecological_capacity_ceiling_ready"] is not False
    ):
        raise ValueError("Invalid GSI geometry cannot certify ecological capacity")
    if (
        acquired["original_files_committed_to_repository"] is not False
        or acquired["forest_official_boundary_geometries_acquired"] is not False
        or acquired["swak_final_wetland_polygons_acquired"] is not False
        or acquired["eligible_area_sq_km"] is not None
        or acquired["capacity_ceiling_mw"] is not None
    ):
        raise ValueError("Source acquisition cannot create legal area or capacity")
    dem_envelope = json.loads((root / DEM_ENVELOPE).read_text(encoding="utf-8"))
    if dem_envelope.get("classification") != (
        "downloaded_public_Copernicus_GLO90_DSM_partial_envelope_not_eligible_terrain"
    ):
        raise ValueError("DEM source acquisition cannot self-certify model terrain")
    tile_rows = dem_envelope["original_tiles_and_hashes"]
    acquired_tiles = [row for row in tile_rows if row["status"] == "original_tif_downloaded"]
    absent_tiles = [row for row in tile_rows if row["status"] == "tile_not_published_http_404"]
    if (
        dem_envelope["requested_envelope_tiles"] != 20
        or len(tile_rows) != 20
        or len(acquired_tiles) != 14
        or len(absent_tiles) != 6
        or len({(row["latitude"], row["longitude"]) for row in tile_rows}) != 20
        or not all(row["url"].startswith(
            "https://copernicus-dem-90m.s3.amazonaws.com/"
        ) and len(row["sha256"]) == 64 and row["bytes"] > 0
            for row in acquired_tiles)
        or dem_envelope["adjacent_seam_checks"] != 19
    ):
        raise ValueError("DEM source tile hashes or envelope scope inconsistent")
    mosaic = dem_envelope["mosaic"]
    if (
        mosaic["status"] != (
            "partial_public_tile_mosaic_with_unknown_uncovered_cells_NOT_Kerala_mask"
        )
        or mosaic["source_tiles"] != 14
        or mosaic["404_or_failed_envelope_tiles"] != 6
        or mosaic["source_uncovered_output_pixels"] <= 0
        or mosaic["complete_rectangular_envelope_source_coverage"] is not False
        or len(mosaic["sha256"]) != 64
        or mosaic["crs"] != "EPSG:4326"
        or dem_envelope["official_kerala_boundary_coverage_verified"] is not False
        or dem_envelope["source_dsm_not_bare_earth_dtm"] is not True
        or dem_envelope["ecological_capacity_ceiling_ready"] is not False
        or dem_envelope["eligible_area_sq_km"] is not None
        or dem_envelope["capacity_ceiling_mw"] is not None
    ):
        raise ValueError("DEM mosaic cannot establish Kerala terrain or eligibility")
    return {
        "classification": "verified_official_source_routes_not_acquired_model_ready_geometry",
        "registry": REGISTRY,
        "acquisition_manifest": ACQUISITION,
        "gsi_geometry_validation": GSI_VALIDATION,
        "dem_envelope_acquisition": DEM_ENVELOPE,
        "workstreams": {
            "forest_protected_areas": {
                "official_boundary_layers_reported": True,
                "source_geometry_verified_in_committed_repo": False,
                "notification_status_verified_spatially": False,
            },
            "elevation_dem": {
                "cartodem_login_route_documented": True,
                "public_copernicus_dsm_route_documented": True,
                "statewide_dem_raster_verified_in_committed_repo": False,
                "glo90_sample_tile_retrieved_in_workflow_artifact": True,
                "glo90_original_tiles_retrieved": len(acquired_tiles),
                "glo90_unpublished_offshore_or_unknown_tiles": len(absent_tiles),
                "glo90_partial_mosaic_sha256": mosaic["sha256"],
                "glo90_partial_mosaic_source_uncovered_pixels": mosaic["source_uncovered_output_pixels"],
                "glo90_sample_original_sha256": pilot["sha256"],
                "dsm_is_not_bare_earth": True,
            },
            "wetlands_waterbodies_landslide": {
                "published_gsi_2022_district_download_labels": len(districts),
                "gsi_original_zips_downloaded_to_workflow_artifact": len(archives),
                "gsi_shapefile_bundles_decoded": 13,
                "gsi_features_decoded": 39,
                "gsi_source_crs": "EPSG:32643",
                "gsi_susceptibility_classes_verified": ["High", "Low", "Moderate"],
                "gsi_invalid_source_features": 39,
                "gsi_invalidity_reason": "Ring Self-intersection",
                "gsi_model_overlay_admitted": False,
                "gsi_shapefile_bundles_verified_in_committed_repo": 0,
                "notified_wetland_polygons_verified": 0,
                "older_ncess_landslide_not_current_reference": True,
            },
        },
        "ecological_eligibility_established": False,
        "eligible_area_sq_km": None,
        "capacity_ceiling_mw": None,
        "audit_gate_closed": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument(
        "--output", type=Path, default=Path("results/gis/three_workstreams_source_audit.json")
    )
    parser.add_argument("--dem-sample", type=Path)
    parser.add_argument("--gsi-zip-sample", type=Path)
    args = parser.parse_args()
    report = audit_gis(args.root)
    if args.dem_sample:
        report["dem_sample"] = check_raster(args.dem_sample)
    if args.gsi_zip_sample:
        report["gsi_zip_sample"] = check_shapefile_zip(args.gsi_zip_sample)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
    print(json.dumps(report, indent=2, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
