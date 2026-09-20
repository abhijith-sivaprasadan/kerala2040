"""Compare repairs on original hash-verified KSDMA/GSI 2022 source polygons.

No repair is admitted as scientific truth, legal exclusion or model-ready overlay.
All area calculations are in original source EPSG:32643 square metres. An
invalid polygon's raw algebraic area is a diagnostic, NOT ground-truth area.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import tempfile
from datetime import UTC, datetime
from itertools import combinations
from pathlib import Path
from typing import Any

import geopandas as gpd
import requests
import shapely
from shapely.geometry import MultiPolygon, Polygon
from shapely.ops import unary_union

from validate_gsi_2022_landslide import ACQ, download, safe_extract, sha256

VALIDATED = Path("data/evidence/gis/gsi_2022_geometry_validation_2026_09_20.json")
METHODS = ("linework", "structure", "buffer0")
CLASSES = {"Low", "Moderate", "High"}


def polygonal(geometry: Any) -> tuple[Any, int]:
    """Return polygonal parts separately; quantify rejected non-polygon parts."""
    parts: list[Polygon] = []
    nonpolygon = 0

    def walk(value: Any) -> None:
        nonlocal nonpolygon
        if value is None or value.is_empty:
            return
        if isinstance(value, Polygon):
            parts.append(value)
        elif isinstance(value, MultiPolygon):
            parts.extend(value.geoms)
        elif hasattr(value, "geoms"):
            for sub in value.geoms:
                walk(sub)
        else:
            nonpolygon += 1

    walk(geometry)
    result = MultiPolygon(parts) if parts else MultiPolygon()
    return result, nonpolygon


def safe_div(numerator: float, denominator: float) -> float | None:
    return float(numerator / denominator) if denominator > 0 else None


def repair_variants(geometry: Any) -> dict[str, tuple[Any, int]]:
    variants = {
        "linework": shapely.make_valid(geometry, method="linework"),
        "structure": shapely.make_valid(geometry, method="structure"),
        "buffer0": geometry.buffer(0),
    }
    return {key: polygonal(value) for key, value in variants.items()}


def compare_feature(geometry: Any, district: str, cls: str, source_sha: str,
                    source_row: int) -> tuple[dict[str, Any], dict[str, Any]]:
    """Calculate raw/candidate area and valid-to-valid geometric disagreement."""
    if geometry is None or geometry.is_empty:
        raise ValueError(f"{district}/{cls}: null or empty original")
    if geometry.is_valid:
        raise ValueError(f"{district}/{cls}: unexpected valid original; source changed")
    source_area = float(geometry.area)
    source_wkb_sha = hashlib.sha256(geometry.wkb).hexdigest()
    variant_geoms = repair_variants(geometry)
    raw = {}
    for method, (geom, collapsed) in variant_geoms.items():
        raw[method] = {
            "polygonal": geom,
            "discarded_nonpolygon_parts": collapsed,
            "geometry_is_valid": bool(geom.is_valid),
            "geometry_is_empty": bool(geom.is_empty),
            "area_m2": float(geom.area),
            "polygon_components": len(geom.geoms),
            "relative_area_change_vs_invalid_source_pct": (
                100 * (float(geom.area) - source_area) / source_area
                if source_area > 0 else None
            ),
        }
    if any(v["geometry_is_empty"] or not v["geometry_is_valid"] for v in raw.values()):
        raise ValueError(f"{district}/{cls}: one candidate is not valid and nonempty")
    comparisons = {}
    for left, right in combinations(METHODS, 2):
        a, b = raw[left]["polygonal"], raw[right]["polygonal"]
        difference = float(a.symmetric_difference(b).area)
        union = float(a.union(b).area)
        comparisons[f"{left}_vs_{right}"] = {
            "symmetric_difference_m2": difference,
            "symmetric_difference_fraction_of_union": safe_div(difference, union),
            "area_change_m2": float(a.area - b.area),
            "hausdorff_distance_m_source_crs": float(a.boundary.hausdorff_distance(b.boundary)),
            "topologically_equal": bool(a.equals(b)),
        }
    entry = {
        "district": district,
        "susceptibility_class": cls,
        "original_row_index": source_row,
        "source_archive_sha256": source_sha,
        "original_feature_wkb_sha256": source_wkb_sha,
        "source_invalid_algebraic_area_m2_NOT_ground_truth": source_area,
        "source_geometry_is_valid": False,
        "candidates": {
            key: {k: v for k, v in data.items() if k != "polygonal"}
            for key, data in raw.items()
        },
        "pairwise_comparison": comparisons,
        "candidate_automatically_admitted": False,
    }
    return entry, {key: item["polygonal"] for key, item in raw.items()}


def class_overlap(candidate: dict[str, Any]) -> dict[str, Any]:
    overlaps = {}
    for left, right in combinations(sorted(CLASSES), 2):
        a, b = candidate[left], candidate[right]
        area = float(a.intersection(b).area)
        overlaps[f"{left}_and_{right}"] = {
            "overlap_m2": area,
            "relative_to_smaller_class_area": safe_div(area, min(a.area, b.area)),
        }
    return overlaps


def compare_archives(root: Path, raw_dir: Path, output: Path) -> dict[str, Any]:
    evidence = json.loads((root / ACQ).read_text())
    baseline = json.loads((root / VALIDATED).read_text())
    sources = evidence["gsi_2022"]["per_district"]
    if len(sources) != 13 or baseline["invalid_geometry_count_total"] != 39:
        raise ValueError("Changed source/archive baseline; validate originals again")
    if baseline["published_packages_decoded"] != 13 or baseline["total_features"] != 39:
        raise ValueError("Invalid or different source cohort")
    raw_dir.mkdir(parents=True, exist_ok=True)
    records: list[dict[str, Any]] = []
    district_records: list[dict[str, Any]] = []
    source_hashes: dict[str, str] = {}
    session = requests.Session()
    session.headers.update({
        "User-Agent": (
            "Kerala2040Research/1.0 "
            "(+https://github.com/abhijith-sivaprasadan/kerala2040)"
        )
    })
    try:
        for source in sources:
            district = source["district"]
            dest = raw_dir / f"{district}.zip"
            if not dest.is_file() or sha256(dest) != source["sha256"]:
                download(session, source["source_url"], dest, source["sha256"])
            source_hashes[district] = sha256(dest)
            with tempfile.TemporaryDirectory() as temporary:
                extracted = Path(temporary)
                safe_extract(dest, extracted)
                shp_path = extracted / (source["complete_shapefile_groups"][0] + ".shp")
                if not shp_path.exists():
                    raise ValueError(f"{district}: exact original shapefile missing")
                frame = gpd.read_file(shp_path)
                if frame.crs is None or frame.crs.to_epsg() != 32643:
                    raise ValueError(f"{district}: original projected CRS changed")
                if len(frame) != 3 or set(frame["Susceptibi"]) != CLASSES:
                    raise ValueError(f"{district}: source classes/count changed")
                if not set(frame.geometry.geom_type) <= {"MultiPolygon", "Polygon"}:
                    raise ValueError(f"{district}: source geometry type changed")
                by_method: dict[str, dict[str, Any]] = {key: {} for key in METHODS}
                district_rows = []
                for index, row in frame.iterrows():
                    cls = str(row["Susceptibi"])
                    measured, variants = compare_feature(
                        row.geometry, district, cls, source["sha256"], int(index),
                    )
                    records.append(measured)
                    district_rows.append(measured)
                    for method, polygon in variants.items():
                        by_method[method][cls] = polygon
                overlaps = {method: class_overlap(classes)
                            for method, classes in by_method.items()}
                total_candidate_class_area = {
                    method: float(sum(poly.area for poly in classes.values()))
                    for method, classes in by_method.items()
                }
                union_area = {
                    method: float(unary_union(list(classes.values())).area)
                    for method, classes in by_method.items()
                }
                district_records.append({
                    "district": district,
                    "source_archive_sha256": source["sha256"],
                    "source_feature_count": len(frame),
                    "susceptibility_classes": sorted(CLASSES),
                    "candidate_class_area_sums_m2": total_candidate_class_area,
                    "candidate_union_area_m2": union_area,
                    "candidate_cross_class_overlap": overlaps,
                    "candidate_total_area_change_vs_linework_pct": {
                        method: (
                            100 * (area - total_candidate_class_area["linework"])
                            / total_candidate_class_area["linework"]
                            if total_candidate_class_area["linework"] > 0 else None
                        )
                        for method, area in total_candidate_class_area.items()
                    },
                    "all_repaired_candidate_features_valid": all(
                        row["candidates"][method]["geometry_is_valid"]
                        for row in district_rows for method in METHODS
                    ),
                    "surveyed_district_boundary_completeness_verified": False,
                })
    finally:
        session.close()
    if len(records) != 39 or len(district_records) != 13:
        raise ValueError("Incomplete GSI comparison cohort")
    result = {
        "classification": "original_hash_verified_GSI_repair_sensitivity_NOT_authoritative_geometry",
        "comparison_timestamp_utc": datetime.now(UTC).replace(microsecond=0).isoformat(),
        "source_acquisition_manifest": str(ACQ),
        "source_decoded_evidence": str(VALIDATED),
        "geos_version": shapely.geos_version_string,
        "shapely_version": shapely.__version__,
        "source_crs": "EPSG:32643",
        "source_invalid_features": 39,
        "source_invalid_area_caveat": (
            "Area of a self-intersecting polygon is an algebraic GEOS calculation "
            "and NOT authoritative observed land area."
        ),
        "methods": {
            "linework": "shapely.make_valid(method=linework), polygon parts only",
            "structure": "shapely.make_valid(method=structure), polygon parts only",
            "buffer0": "source.buffer(0), polygon parts only, potential geometry loss",
        },
        "district_count": 13,
        "feature_count": 39,
        "districts": district_records,
        "feature_comparison": records,
        "per_district_original_zip_sha256": source_hashes,
        "alappuzha_published_package_present": False,
        "alappuzha_hazard_status_inferred": False,
        "fully_notified_district_boundaries_compared": False,
        "geometry_repair_proven_correct_against_reference": False,
        "automatic_method_selection": None,
        "model_ready_repaired_geopackage_written": False,
        "legal_exclusion_applied": False,
        "eligible_area_sq_km": None,
        "capacity_ceiling_mw": None,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument(
        "--raw-dir", type=Path, default=Path("results/gis/gsi_2022_repair_original_zips")
    )
    parser.add_argument(
        "--output", type=Path,
        default=Path("results/gis/gsi_2022_repair_method_comparison.json"),
    )
    args = parser.parse_args()
    report = compare_archives(args.root, args.raw_dir, args.output)
    pair = [r["pairwise_comparison"] for r in report["feature_comparison"]]
    summary = {
        "classification": report["classification"],
        "original_features": report["source_invalid_features"],
        "methods": list(report["methods"]),
        "districts": report["district_count"],
        "compared_features": report["feature_count"],
        "max_pairwise_symmetric_difference_fraction": {
            name: max((v[name]["symmetric_difference_fraction_of_union"] or 0.0)
                      for v in pair)
            for name in pair[0]
        },
        "all_candidate_features_valid": all(
            f["candidates"][m]["geometry_is_valid"]
            for f in report["feature_comparison"] for m in METHODS
        ),
        "model_ready_repaired_geopackage_written": False,
        "full_report": str(args.output),
    }
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
