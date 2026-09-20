"""Auditable, opt-in diagnostic of GSI ring self-intersection repairs.

Never replace the original agency ZIP, overwrite source geometry, or silently
declare repaired layers authoritative or legally eligible.
"""

from __future__ import annotations

import argparse
import json
import tempfile
import zipfile
from datetime import UTC, datetime
from itertools import combinations
from pathlib import Path

import shapely
from shapely.geometry import MultiPolygon, Polygon

from kerala2040.gis_three_workstreams import check_shapefile_zip, sha256
from kerala2040.gsi_2022_geometry import _extract_one, _read_manifest


def _polygons(value) -> list[Polygon]:
    if value.is_empty:
        return []
    if isinstance(value, Polygon):
        return [value]
    return [polygon for part in shapely.get_parts(value) for polygon in _polygons(part)]


def assess_archive(path: Path, row: dict) -> tuple[dict, list[dict]]:
    import geopandas as gpd

    if path.stat().st_size != row["bytes"] or sha256(path) != row["sha256"]:
        raise ValueError("Original archive SHA256/bytes differ from committed manifest")
    groups = check_shapefile_zip(path)["complete_shapefile_groups"]
    if len(groups) != 1:
        raise ValueError("District has ambiguous original shapefile group count")
    with tempfile.TemporaryDirectory(prefix="gsi-repair-review-") as temp:
        with zipfile.ZipFile(path) as archive:
            shp = _extract_one(archive, groups[0], Path(temp))
        frame = gpd.read_file(shp, engine="pyogrio")
    if frame.crs is None or frame.crs.to_string() != "EPSG:32643":
        raise ValueError("Unreviewed source CRS: expected documented EPSG:32643")
    if "Susceptibi" not in frame or sorted(frame["Susceptibi"].tolist()) != [
        "High", "Low", "Moderate"
    ]:
        raise ValueError("Original raw susceptibility classes are not exactly 3 documented labels")
    features: list[dict] = []
    candidates: list[dict] = []
    for raw_class, geometry in zip(frame["Susceptibi"], frame.geometry, strict=True):
        if geometry is None or geometry.is_empty:
            raise ValueError("Source contains missing original polygon")
        if geometry.geom_type != "MultiPolygon":
            raise ValueError("Unexpected original type for reviewed GSI source")
        repaired = shapely.make_valid(geometry, method="linework")
        polygons = _polygons(repaired)
        if not polygons:
            raise ValueError("make_valid yielded no polygonal shape")
        polygon = polygons[0] if len(polygons) == 1 else MultiPolygon(polygons)
        original_area = geometry.area
        revised_area = polygon.area
        effect = abs(revised_area - original_area) / original_area if original_area else None
        remaining = not bool(shapely.is_valid(polygon))
        report = {
            "raw_source_class": raw_class,
            "source_geometry_type": geometry.geom_type,
            "source_is_valid": bool(shapely.is_valid(geometry)),
            "original_invalid_reason": shapely.is_valid_reason(geometry),
            "make_valid_method": "GEOS_linework",
            "make_valid_return_type": repaired.geom_type,
            "polygon_component_count": len(polygons),
            "polygonal_geometry_is_valid_after_repair": not remaining,
            "original_invalid_geometry_area_km2": original_area / 1e6,
            "repaired_polygon_area_km2": revised_area / 1e6,
            "absolute_area_difference_km2": abs(revised_area - original_area) / 1e6,
            "absolute_area_change_fraction_vs_invalid_geometry_area": effect,
            "nonpolygonal_collapsed_parts_may_be_discarded": repaired.geom_type == "GeometryCollection",
            "authoritative_repair_approval": False,
        }
        features.append(report)
        candidates.append({"raw_source_class": raw_class, "geometry": polygon})
    overlaps = []
    for left, right in combinations(candidates, 2):
        area = left["geometry"].intersection(right["geometry"]).area / 1e6
        overlaps.append({
            "source_classes": [left["raw_source_class"], right["raw_source_class"]],
            "pairwise_overlap_area_km2": area,
        })
    result = {
        "district": row["district"],
        "source_zip_sha256": row["sha256"],
        "original_crs": "EPSG:32643",
        "features": features,
        "class_overlap_diagnostics": overlaps,
        "maximum_relative_area_change": max(
            v["absolute_area_change_fraction_vs_invalid_geometry_area"]
            for v in features
        ),
        "all_repaired_polygons_valid": all(
            f["polygonal_geometry_is_valid_after_repair"] for f in features
        ),
        "derivative_is_official_GSI_geometry": False,
        "legal_site_suitability_validated": False,
    }
    return result, candidates


def run(
    root: Path,
    archive_dir: Path,
    output: Path,
    *,
    provisional_gpkg: Path | None = None,
) -> dict:
    rows = _read_manifest(root)
    results = []
    harmonized = []
    for row in rows:
        path = archive_dir / Path(row["source_url"]).name
        try:
            info, candidates = assess_archive(path, row)
            for candidate in candidates:
                harmonized.append({
                    "source_district": row["district"],
                    "source_raw_class_field": "Susceptibi",
                    "raw_susceptibility": candidate["raw_source_class"],
                    "original_zip_sha256": row["sha256"],
                    "repair_method": "GEOS make_valid linework; polygonal parts",
                    "geometry": candidate["geometry"],
                })
            info["status"] = "repair_preview_measured_not_source_replacement"
            print(
                f"REPAIR {row['district']}: valid_after={info['all_repaired_polygons_valid']} "
                f"max_area_change={info['maximum_relative_area_change']:.6f} "
                f"overlaps={info['class_overlap_diagnostics']}",
                flush=True,
            )
        except Exception as exc:  # noqa: BLE001 - preserve which originals remain unresolved
            info = {
                "district": row["district"],
                "status": "repair_qa_failed",
                "error": f"{type(exc).__name__}: {exc}",
            }
            print(f"REPAIR {row['district']}: {info['error']}", flush=True)
        results.append(info)
    safe_derivative = (
        len(harmonized) == 39
        and len(results) == 13
        and all(
            d.get("all_repaired_polygons_valid") is True
            and d.get("maximum_relative_area_change", 1.0) <= 1e-8
            and all(
                pair["pairwise_overlap_area_km2"] <= 1e-6
                for pair in d.get("class_overlap_diagnostics", [])
            )
            for d in results
        )
    )
    output_file = None
    if provisional_gpkg is not None:
        if not safe_derivative:
            raise ValueError("Refusing GPKG: incomplete, overlapping or area-changing repair QA")
        import geopandas as gpd
        import pyogrio

        provisional_gpkg.parent.mkdir(parents=True, exist_ok=True)
        provisional_gpkg.unlink(missing_ok=True)
        layer = "GSI2022_REPAIRED_PROVISIONAL_NOT_LEGAL"
        frame = gpd.GeoDataFrame(harmonized, geometry="geometry", crs="EPSG:32643")
        frame.to_file(provisional_gpkg, layer=layer, driver="GPKG", engine="pyogrio")
        independent = pyogrio.read_info(str(provisional_gpkg), layer=layer)
        if independent["features"] != 39 or independent["crs"] != "EPSG:32643":
            raise ValueError("Saved GPKG failed feature-count/source-CRS reread")
        output_file = {
            "path": str(provisional_gpkg),
            "sha256": sha256(provisional_gpkg),
            "bytes": provisional_gpkg.stat().st_size,
            "layer_name": layer,
            "feature_count": int(independent["features"]),
            "source_crs": independent["crs"],
            "original_zip_identities_preserved_in_attributes": True,
            "source_raw_class_labels_preserved": True,
            "official_source_geometry": False,
            "legal_exclusion_mask": False,
            "statewide_coverage": False,
            "model_eligible_area_or_mw": None,
        }
        print("GSI_PROVISIONAL_GPKG=" + json.dumps(output_file), flush=True)
    report = {
        "classification": "original_invalid_GSI_ring_geometries_make_valid_DIAGNOSTIC_only",
        "reviewed_at_utc": datetime.now(UTC).replace(microsecond=0).isoformat(),
        "number_of_original_district_archives": 13,
        "districts_repair_qa_completed": sum(
            d.get("status") == "repair_preview_measured_not_source_replacement"
            for d in results
        ),
        "repair_approval_from_source_agency": False,
        "cross_district_overlap_qa_completed": False,
        "original_source_geometry_replaced": False,
        "repaired_geopackage_published": False,
        "provisional_gpkg": output_file,
        "independent_district_coverage_qa_completed": False,
        "alappuzha_source_coverage": "unassessed",
        "legal_siting_status": "blocked",
        "area_sq_km_available_for_siting": None,
        "renewable_capacity_mw": None,
        "districts": results,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
    print("GSI_REPAIR_QA_SUMMARY=" + json.dumps({
        "districts_repair_qa_completed": report["districts_repair_qa_completed"],
        "maximum_relative_area_change": max(
            (d.get("maximum_relative_area_change", 0) for d in results),
            default=0,
        ),
        "all_valid_after": all(
            d.get("all_repaired_polygons_valid") is True for d in results
        ),
        "interclass_positive_area_overlap_pairs": sum(
            pair["pairwise_overlap_area_km2"] > 0.000001
            for district in results
            for pair in district.get("class_overlap_diagnostics", [])
        ),
    }, allow_nan=False))
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--raw-dir", type=Path, default=Path("results/gis/pilot_raw/ksdma"))
    parser.add_argument("--output", type=Path, default=Path("results/gis/gsi_2022_repair_review.json"))
    parser.add_argument("--provisional-gpkg", type=Path)
    args = parser.parse_args()
    result = run(
        args.root, args.raw_dir, args.output, provisional_gpkg=args.provisional_gpkg
    )
    return 0 if result["districts_repair_qa_completed"] == 13 else 2


if __name__ == "__main__":
    raise SystemExit(main())
