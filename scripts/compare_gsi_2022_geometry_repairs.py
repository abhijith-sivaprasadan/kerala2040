"""Compare explicit repairs for invalid GSI 2022 landslide polygons.

This is a topology-repair sensitivity study. It does not convert susceptibility
into a legal exclusion and does not infer Alappuzha as hazard-free.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import tempfile
import zipfile
from pathlib import Path
from typing import Any

import geopandas as gpd
import pandas as pd
import requests
from shapely import make_valid

from kerala2040.gsi_repair import compare_feature, polygonal

ACQ = Path("data/evidence/gis/official_gis_public_acquisition_2026_09_20.json")
SOURCE_QA = Path("data/evidence/gis/gsi_2022_geometry_validation_2026_09_20.json")
TARGET_CRS = "EPSG:32643"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def download(session: requests.Session, url: str, dest: Path, expected_sha: str) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    part = dest.with_suffix(dest.suffix + ".part")
    with session.get(url, timeout=(15, 120), stream=True) as response:
        response.raise_for_status()
        with part.open("wb") as out:
            for chunk in response.iter_content(1024 * 1024):
                if chunk:
                    out.write(chunk)
    if sha256(part) != expected_sha:
        part.unlink(missing_ok=True)
        raise ValueError(f"SHA256 mismatch: {url}")
    part.replace(dest)


def safe_extract(archive: Path, out: Path) -> None:
    with zipfile.ZipFile(archive) as zf:
        for member in zf.infolist():
            target = (out / member.filename).resolve()
            if not str(target).startswith(str(out.resolve()) + "/"):
                raise ValueError(f"unsafe zip member: {member.filename}")
            if member.file_size > 500_000_000:
                raise ValueError(f"oversized member: {member.filename}")
        zf.extractall(out)


def read_frame(archive: Path, group: str) -> gpd.GeoDataFrame:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        safe_extract(archive, root)
        shp = root / f"{group}.shp"
        if not shp.exists():
            candidates = list(root.rglob("*.shp"))
            if len(candidates) != 1:
                raise ValueError(f"expected one shapefile; got {len(candidates)}")
            shp = candidates[0]
        return gpd.read_file(shp)


def aggregate_class(frame: gpd.GeoDataFrame) -> list[dict[str, Any]]:
    rows = []
    for cls, part in frame.groupby("Susceptibi", dropna=False):
        rows.append({
            "susceptibility": None if pd.isna(cls) else str(cls),
            "features": len(part),
            "make_valid_area_km2": float(part.geometry.area.sum() / 1e6),
        })
    return sorted(rows, key=lambda x: str(x["susceptibility"]))


def run(root: Path, output: Path, gpkg: Path, raw_dir: Path) -> dict[str, Any]:
    acquisition = json.loads((root / ACQ).read_text())
    prior = json.loads((root / SOURCE_QA).read_text())
    if (
        prior["published_packages_decoded"] != 13
        or prior["invalid_geometry_count_total"] != 39
        or prior["susceptibility_semantics_verified"] is not True
        or prior["raw_source_geometries_all_valid"] is not False
    ):
        raise ValueError("repair study requires the committed invalid-source QA baseline")

    entries = acquisition["gsi_2022"]["per_district"]
    if len(entries) != 13:
        raise ValueError("expected 13 source archives")

    session = requests.Session()
    session.headers.update({"User-Agent": "Kerala2040Research/1.0"})
    repaired_frames = []
    feature_rows = []
    try:
        for entry in entries:
            district = entry["district"]
            archive = raw_dir / f"{district}.zip"
            download(session, entry["source_url"], archive, entry["sha256"])
            source = read_frame(archive, entry["complete_shapefile_groups"][0])
            if source.crs is None:
                raise ValueError(f"{district}: CRS missing")
            source = source.to_crs(TARGET_CRS)
            if "Susceptibi" not in source.columns:
                raise ValueError(f"{district}: susceptibility field missing")
            mv_geoms = []
            for idx, geom in enumerate(source.geometry):
                if geom is None or geom.is_empty:
                    raise ValueError(f"{district} feature {idx}: empty source geometry")
                mv = polygonal(make_valid(geom, method="structure", keep_collapsed=True))
                b0 = polygonal(geom.buffer(0))
                metrics = compare_feature(geom, mv, b0)
                if metrics["make_valid_empty"] or not metrics["make_valid_valid"]:
                    raise ValueError(f"{district} feature {idx}: make_valid did not yield valid areal geometry")
                if metrics["buffer0_empty"] or not metrics["buffer0_valid"]:
                    raise ValueError(f"{district} feature {idx}: buffer(0) did not yield valid areal geometry")
                print(f"repair {district} feature {idx}", flush=True)
                feature_rows.append({
                    "district": district,
                    "source_index": int(idx),
                    "susceptibility": str(source.iloc[idx]["Susceptibi"]),
                    **metrics,
                })
                mv_geoms.append(mv)
            repaired = source.copy()
            repaired["district"] = district
            repaired["source_zip_sha256"] = entry["sha256"]
            repaired.geometry = mv_geoms
            repaired_frames.append(repaired)
    finally:
        session.close()

    merged = gpd.GeoDataFrame(pd.concat(repaired_frames, ignore_index=True), crs=TARGET_CRS)
    if len(merged) != 39 or not bool(merged.geometry.is_valid.all()):
        raise ValueError("repaired derivative does not contain 39 valid features")
    if set(merged["Susceptibi"]) != {"Low", "Moderate", "High"}:
        raise ValueError("susceptibility classes changed during repair")

    area_disagreements = [r["repair_relative_area_disagreement"] for r in feature_rows]
    centroid_shifts = [r["repair_centroid_shift_m"] for r in feature_rows]
    bounds_deltas = [r["repair_bounds_max_abs_delta_m"] for r in feature_rows]
    part_differences = [abs(r["part_count_difference"]) for r in feature_rows]
    max_area_disagreement = max(area_disagreements)
    mean_area_disagreement = sum(area_disagreements) / len(area_disagreements)
    mv_src_ratios = [r["make_valid_vs_source_area_ratio"] for r in feature_rows if r["make_valid_vs_source_area_ratio"] is not None]
    b0_src_ratios = [r["buffer0_vs_source_area_ratio"] for r in feature_rows if r["buffer0_vs_source_area_ratio"] is not None]

    # Detect overlaps only within each district. Cross-district overlaps require an
    # authoritative district boundary to distinguish edge mismatch from true overlap.
    district_overlap_records = []
    for district, district_frame in merged.groupby("district"):
        overlap_area = 0.0
        pairs = 0
        geoms = list(district_frame.geometry)
        for i, left in enumerate(geoms):
            for right in geoms[i + 1:]:
                area = float(left.intersection(right).area)
                if area > 0:
                    overlap_area += area
                    pairs += 1
        district_overlap_records.append({
            "district": str(district),
            "positive_area_overlap_pairs_between_susceptibility_features": pairs,
            "positive_overlap_area_m2": overlap_area,
        })

    gpkg.parent.mkdir(parents=True, exist_ok=True)
    merged.to_file(gpkg, layer="gsi_2022_make_valid", driver="GPKG")
    derivative_sha = sha256(gpkg)
    result = {
        "classification": "documented_make_valid_derivative_with_repair_sensitivity_NOT_legal_exclusion",
        "source_geometry_validation": str(SOURCE_QA),
        "source_archives": 13,
        "source_features": 39,
        "source_crs": TARGET_CRS,
        "repair_methods_compared": ["shapely.make_valid_structure_polygonal_only", "shapely.buffer_0_polygonal_only"],
        "selected_derivative_method": "shapely.make_valid_structure_polygonal_only",
        "selection_reason": (
            "GEOS make_valid structure mode repairs rings from shell/hole structure while preserving "
            "polygonal output. buffer(0) is retained only as an independent sensitivity comparison."
        ),
        "all_make_valid_features_valid": True,
        "all_buffer0_features_valid": True,
        "all_39_features_retained": True,
        "susceptibility_classes_preserved": ["High", "Low", "Moderate"],
        "max_repair_method_relative_area_disagreement": max_area_disagreement,
        "mean_repair_method_relative_area_disagreement": mean_area_disagreement,
        "max_repair_method_centroid_shift_m": max(centroid_shifts),
        "max_repair_method_bounds_delta_m": max(bounds_deltas),
        "features_with_different_part_counts": sum(value > 0 for value in part_differences),
        "max_absolute_part_count_difference": max(part_differences),
        "make_valid_vs_invalid_source_area_ratio_min": min(mv_src_ratios),
        "make_valid_vs_invalid_source_area_ratio_max": max(mv_src_ratios),
        "buffer0_vs_invalid_source_area_ratio_min": min(b0_src_ratios),
        "buffer0_vs_invalid_source_area_ratio_max": max(b0_src_ratios),
        "feature_comparison": feature_rows,
        "district_internal_overlap_qa": district_overlap_records,
        "class_area_summary": aggregate_class(merged),
        "derivative": {
            "path": str(gpkg),
            "sha256": derivative_sha,
            "feature_count": len(merged),
            "crs": merged.crs.to_string(),
            "geometry_types": sorted(set(merged.geometry.geom_type)),
            "all_valid": bool(merged.geometry.is_valid.all()),
            "redistribution_status": "workflow_artifact_only_pending_source_redistribution_review",
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
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--output", type=Path, default=Path("results/gis/gsi_2022_repair_comparison.json"))
    parser.add_argument("--gpkg", type=Path, default=Path("results/gis/gsi_2022_repaired.gpkg"))
    parser.add_argument("--raw-dir", type=Path, default=Path("results/gis/gsi_2022_repair_zips"))
    args = parser.parse_args()
    report = run(args.root, args.output, args.gpkg, args.raw_dir)
    print(json.dumps(report, indent=2, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
