"""Download and decode the 13 official KSDMA/GSI landslide shapefiles.

The output is a reproducible geometry/attribute QA manifest. It does not convert
landslide susceptibility into a legal exclusion or renewable-capacity ceiling.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import tempfile
import zipfile
from pathlib import Path
from typing import Any

import geopandas as gpd
import pandas as pd
import requests
from shapely.geometry import box

ACQ = Path("data/evidence/gis/official_gis_public_acquisition_2026_09_20.json")
KERALA_ENVELOPE = box(74.5, 8.0, 78.0, 12.9)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def download(session: requests.Session, url: str, dest: Path, expected_sha: str) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(dest.suffix + ".part")
    with session.get(url, stream=True, timeout=(15, 120)) as r:
        r.raise_for_status()
        with tmp.open("wb") as f:
            for chunk in r.iter_content(1024 * 1024):
                if chunk:
                    f.write(chunk)
    if sha256(tmp) != expected_sha:
        tmp.unlink(missing_ok=True)
        raise ValueError(f"SHA256 mismatch for {url}")
    tmp.replace(dest)


def safe_extract(archive: Path, out: Path) -> None:
    with zipfile.ZipFile(archive) as z:
        for member in z.infolist():
            target = (out / member.filename).resolve()
            if not str(target).startswith(str(out.resolve()) + "/"):
                raise ValueError(f"Unsafe ZIP member: {member.filename}")
            if member.file_size > 500_000_000:
                raise ValueError(f"Unreasonably large ZIP member: {member.filename}")
        z.extractall(out)


def json_value(value: Any) -> Any:
    if pd.isna(value):
        return None
    if hasattr(value, "item"):
        value = value.item()
    if isinstance(value, float) and not math.isfinite(value):
        return None
    return value


def candidate_class_fields(frame: gpd.GeoDataFrame) -> dict[str, list[Any]]:
    """Return low-cardinality attributes without guessing which is susceptibility."""
    result: dict[str, list[Any]] = {}
    for name in frame.columns:
        if name == frame.geometry.name:
            continue
        series = frame[name].dropna()
        if series.empty:
            continue
        unique = series.drop_duplicates()
        if 1 < len(unique) <= 30:
            values = sorted((json_value(v) for v in unique), key=lambda x: str(x))
            result[str(name)] = values
    return result


def validate_archive(
    district: str,
    archive: Path,
    expected_group: str,
    target_crs: str = "EPSG:32643",
) -> tuple[dict[str, Any], gpd.GeoDataFrame]:
    with tempfile.TemporaryDirectory() as tmp:
        extracted = Path(tmp)
        safe_extract(archive, extracted)
        shp = extracted / (expected_group + ".shp")
        if not shp.exists():
            matches = list(extracted.rglob("*.shp"))
            if len(matches) != 1:
                raise ValueError(
                    f"{district}: expected one shapefile, found {len(matches)}"
                )
            shp = matches[0]
        frame = gpd.read_file(shp)
        if frame.empty:
            raise ValueError(f"{district}: empty shapefile")
        if frame.crs is None:
            raise ValueError(f"{district}: shapefile has no CRS")
        geom = frame.geometry
        null_count = int(geom.isna().sum())
        empty_count = int(geom.is_empty.sum())
        valid = geom.is_valid.fillna(False)
        invalid_count = int((~valid & ~geom.isna()).sum())
        original_types = sorted(set(geom.dropna().geom_type))
        if not set(original_types) <= {"Polygon", "MultiPolygon"}:
            raise ValueError(f"{district}: unexpected geometry types {original_types}")
        bounds_original = [float(x) for x in frame.total_bounds]
        wgs = frame.to_crs(4326)
        bounds_wgs84 = [float(x) for x in wgs.total_bounds]
        envelope = box(*bounds_wgs84)
        overlaps_kerala_envelope = bool(envelope.intersects(KERALA_ENVELOPE))
        if not overlaps_kerala_envelope:
            raise ValueError(f"{district}: extent does not overlap Kerala envelope")
        projected = frame.to_crs(target_crs)
        positive_area = projected.geometry.area > 0
        if not bool(positive_area.any()):
            raise ValueError(f"{district}: no positive-area polygons")
        non_geom = frame.drop(columns=frame.geometry.name)
        duplicate_attribute_rows = int(non_geom.duplicated().sum())
        exact_duplicate_geometries = int(
            frame.geometry.to_wkb().duplicated().sum()
        )
        fields = {
            str(name): str(dtype)
            for name, dtype in frame.drop(columns=frame.geometry.name).dtypes.items()
        }
        record = {
            "district": district,
            "source_zip_sha256": sha256(archive),
            "source_crs": frame.crs.to_string(),
            "feature_count": len(frame),
            "geometry_types": original_types,
            "null_geometry_count": null_count,
            "empty_geometry_count": empty_count,
            "invalid_geometry_count": invalid_count,
            "all_non_null_geometries_valid": invalid_count == 0,
            "bounds_original": bounds_original,
            "bounds_wgs84": bounds_wgs84,
            "overlaps_kerala_approximate_envelope": overlaps_kerala_envelope,
            "attribute_fields": fields,
            "candidate_low_cardinality_fields": candidate_class_fields(frame),
            "exact_duplicate_geometry_count": exact_duplicate_geometries,
            "duplicate_non_geometry_attribute_row_count": duplicate_attribute_rows,
            "target_crs_for_merged_derivative": target_crs,
            "positive_area_feature_count": int(positive_area.sum()),
            "source_geometry_repaired": False,
            "legal_exclusion_interpretation_applied": False,
        }
        merged = projected.copy()
        merged.insert(0, "source_district", district)
        return record, merged


def run(root: Path, output: Path, gpkg: Path, raw_dir: Path) -> dict[str, Any]:
    source = json.loads((root / ACQ).read_text(encoding="utf-8"))
    entries = source["gsi_2022"]["per_district"]
    if len(entries) != 13:
        raise ValueError("Expected exactly 13 published GSI district packages")
    session = requests.Session()
    session.headers.update(
        {"User-Agent": "Kerala2040Research/1.0 (+https://github.com/abhijith-sivaprasadan/kerala2040)"}
    )
    records = []
    merged = []
    try:
        for entry in entries:
            district = entry["district"]
            url = entry["source_url"]
            dest = raw_dir / f"{district}.zip"
            download(session, url, dest, entry["sha256"])
            expected_group = entry["complete_shapefile_groups"][0]
            record, frame = validate_archive(district, dest, expected_group)
            records.append(record)
            merged.append(frame)
    finally:
        session.close()
    fields_by_district = {
        row["district"]: sorted(row["attribute_fields"]) for row in records
    }
    common_fields = sorted(set.intersection(*(set(v) for v in fields_by_district.values())))
    class_candidates = {
        field: {
            row["district"]: row["candidate_low_cardinality_fields"].get(field)
            for row in records
        }
        for field in common_fields
        if any(field in row["candidate_low_cardinality_fields"] for row in records)
    }
    combined = gpd.GeoDataFrame(
        pd.concat(merged, ignore_index=True),
        crs=merged[0].crs,
    )
    gpkg.parent.mkdir(parents=True, exist_ok=True)
    combined.to_file(gpkg, layer="gsi_2022_landslide_susceptibility", driver="GPKG")
    result = {
        "classification": (
            "decoded_official_GSI_2022_district_geometries_and_attributes_"
            "NOT_legal_exclusion_NOT_statewide_14_district_coverage"
        ),
        "source_manifest": str(ACQ),
        "published_packages_expected": 13,
        "published_packages_decoded": len(records),
        "districts_decoded": [r["district"] for r in records],
        "alappuzha_published_package_present": False,
        "total_features": sum(r["feature_count"] for r in records),
        "invalid_geometry_count_total": sum(r["invalid_geometry_count"] for r in records),
        "empty_geometry_count_total": sum(r["empty_geometry_count"] for r in records),
        "null_geometry_count_total": sum(r["null_geometry_count"] for r in records),
        "exact_duplicate_geometry_count_total": sum(
            r["exact_duplicate_geometry_count"] for r in records
        ),
        "all_district_extents_overlap_kerala_envelope": all(
            r["overlaps_kerala_approximate_envelope"] for r in records
        ),
        "common_attribute_fields": common_fields,
        "candidate_common_class_fields": class_candidates,
        "per_district": records,
        "merged_derivative": {
            "path": str(gpkg),
            "layer": "gsi_2022_landslide_susceptibility",
            "target_crs": combined.crs.to_string(),
            "feature_count": len(combined),
            "sha256": sha256(gpkg),
            "source_geometry_repaired": False,
        },
        "susceptibility_semantics_verified": False,
        "district_boundary_completeness_verified": False,
        "alappuzha_hazard_status_inferred": False,
        "legal_exclusion_interpretation_applied": False,
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
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("results/gis/gsi_2022_geometry_validation.json"),
    )
    parser.add_argument(
        "--gpkg",
        type=Path,
        default=Path("results/gis/gsi_2022_landslide_susceptibility.gpkg"),
    )
    parser.add_argument(
        "--raw-dir",
        type=Path,
        default=Path("results/gis/gsi_2022_original_zips"),
    )
    args = parser.parse_args()
    report = run(args.root, args.output, args.gpkg, args.raw_dir)
    print(json.dumps(report, indent=2, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
