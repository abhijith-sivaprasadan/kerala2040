"""Aggregate 13 independent GSI repair jobs into one provenance report/artifact."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import geopandas as gpd
import pandas as pd

DISTRICTS = [
    "Thiruvananthapuram", "Kollam", "Pathanamthitta", "Kottayam", "Idukki",
    "Ernakulam", "Thrissur", "Palakkad", "Malappuram", "Kozhikode",
    "Wayanad", "Kannur", "Kasaragod",
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def aggregate(input_dir: Path, output: Path, gpkg: Path) -> dict:
    reports = []
    frames = []
    for district in DISTRICTS:
        report_path = input_dir / f"{district}.json"
        gpkg_path = input_dir / f"{district}.gpkg"
        if not report_path.is_file() or not gpkg_path.is_file():
            raise ValueError(f"missing repair artifact for {district}")
        report = json.loads(report_path.read_text())
        if (
            report["districts_processed"] != [district]
            or report["source_archives"] != 1
            or report["source_features"] != 3
            or report["all_source_features_retained"] is not True
            or report["derivative"]["feature_count"] != 3
            or report["derivative"]["all_valid"] is not True
            or report["legal_exclusion_interpretation_applied"] is not False
        ):
            raise ValueError(f"invalid district repair report: {district}")
        frame = gpd.read_file(gpkg_path, layer="gsi_2022_make_valid_structure")
        if len(frame) != 3 or frame.crs is None or frame.crs.to_string() != "EPSG:32643":
            raise ValueError(f"invalid derivative GPKG: {district}")
        if not bool(frame.geometry.is_valid.all()):
            raise ValueError(f"invalid repaired feature persisted: {district}")
        reports.append(report)
        frames.append(frame)

    merged = gpd.GeoDataFrame(pd.concat(frames, ignore_index=True), crs="EPSG:32643")
    if len(merged) != 39 or set(merged["district"]) != set(DISTRICTS):
        raise ValueError("aggregated derivative does not preserve 13 districts / 39 features")
    if set(merged["Susceptibi"]) != {"Low", "Moderate", "High"}:
        raise ValueError("susceptibility classes changed during aggregation")

    gpkg.parent.mkdir(parents=True, exist_ok=True)
    merged.to_file(gpkg, layer="gsi_2022_make_valid_structure", driver="GPKG")

    feature_rows = [
        feature
        for report in reports
        for feature in report["feature_comparison"]
    ]
    district_overlap = [
        item
        for report in reports
        for item in report["district_internal_overlap_qa"]
    ]
    class_rows = []
    for cls in ("High", "Low", "Moderate"):
        class_rows.append({
            "susceptibility": cls,
            "features": int((merged["Susceptibi"] == cls).sum()),
            "make_valid_area_km2": float(
                merged.loc[merged["Susceptibi"] == cls].geometry.area.sum() / 1e6
            ),
        })

    result = {
        "classification": (
            "documented_make_valid_structure_derivative_with_repair_sensitivity_"
            "NOT_legal_exclusion"
        ),
        "source_archives": 13,
        "source_features": 39,
        "districts_processed": DISTRICTS,
        "repair_methods_compared": [
            "shapely.make_valid_structure_polygonal_only",
            "shapely.buffer_0_polygonal_only",
        ],
        "selected_derivative_method": "shapely.make_valid_structure_polygonal_only",
        "selection_reason": (
            "GEOS structure-mode make_valid explicitly reconstructs shell/hole "
            "topology; buffer(0) is retained only as an independent sensitivity test."
        ),
        "all_source_features_retained": True,
        "susceptibility_classes_preserved": ["High", "Low", "Moderate"],
        "max_repair_method_relative_area_disagreement": max(
            row["repair_relative_area_disagreement"] for row in feature_rows
        ),
        "mean_repair_method_relative_area_disagreement": sum(
            row["repair_relative_area_disagreement"] for row in feature_rows
        ) / len(feature_rows),
        "max_repair_method_centroid_shift_m": max(
            row["repair_centroid_shift_m"] for row in feature_rows
        ),
        "max_repair_method_bounds_delta_m": max(
            row["repair_bounds_max_abs_delta_m"] for row in feature_rows
        ),
        "features_with_different_part_counts": sum(
            row["part_count_difference"] != 0 for row in feature_rows
        ),
        "max_absolute_part_count_difference": max(
            abs(row["part_count_difference"]) for row in feature_rows
        ),
        "feature_comparison": feature_rows,
        "district_internal_overlap_qa": district_overlap,
        "class_area_summary": class_rows,
        "derivative": {
            "path": str(gpkg),
            "sha256": sha256(gpkg),
            "feature_count": 39,
            "crs": "EPSG:32643",
            "geometry_types": sorted(set(merged.geometry.geom_type)),
            "all_valid": bool(merged.geometry.is_valid.all()),
            "redistribution_status": (
                "workflow_artifact_only_pending_source_redistribution_review"
            ),
        },
        "district_boundary_completeness_verified": False,
        "cross_district_edge_consistency_verified": False,
        "alappuzha_published_package_present": False,
        "alappuzha_hazard_status_inferred": False,
        "legal_exclusion_interpretation_applied": False,
        "technology_specific_hazard_rule_validated": False,
        "ecological_capacity_ceiling_ready": False,
        "eligible_area_sq_km": None,
        "capacity_ceiling_mw": None,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", type=Path, default=Path("results/gis/repair_districts"))
    parser.add_argument("--output", type=Path, default=Path("results/gis/gsi_2022_repair_comparison.json"))
    parser.add_argument("--gpkg", type=Path, default=Path("results/gis/gsi_2022_repaired.gpkg"))
    args = parser.parse_args()
    print(json.dumps(aggregate(args.input_dir, args.output, args.gpkg), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
