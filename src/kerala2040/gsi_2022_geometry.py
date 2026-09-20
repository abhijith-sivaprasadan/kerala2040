"""Decode official KSDMA GSI district shapefiles; report raw classes, not legal siting.

Network operation requires an explicit --download flag and verifies previously
recorded *source* SHA256 before reading. No geometry correction, inferred
district boundary, class re-labelling, or capacity calculation is performed.
"""

from __future__ import annotations

import argparse
from collections import Counter
from datetime import UTC, datetime
import hashlib
import json
from pathlib import Path
import shutil
import tempfile
from urllib.parse import urlparse
import zipfile

import requests

from kerala2040.gis_three_workstreams import ACQUISITION, check_shapefile_zip, sha256

ENVELOPE = (74.0, 7.5, 78.5, 13.5)
DOWNLOAD_LIMIT = 70 * 1024 * 1024
SUSCEPTIBILITY_FIELDS = (
    "suscept", "hazard", "risk", "zone", "class", "category",
    "level", "lsz", "lss", "landslide",
)


def _read_manifest(root: Path) -> list[dict]:
    manifest = json.loads((root / ACQUISITION).read_text(encoding="utf-8"))
    rows = manifest["gsi_2022"]["per_district"]
    if (
        len(rows) != 13
        or len({r["district"] for r in rows}) != 13
        or any(len(r["sha256"]) != 64 for r in rows)
    ):
        raise ValueError("Expected 13 individually hashed official district archives")
    return rows


def _download_checked(session: requests.Session, row: dict, dest: Path) -> None:
    url = row["source_url"]
    parsed = urlparse(url)
    if (
        parsed.scheme != "https"
        or parsed.hostname != "sdma.kerala.gov.in"
        or not parsed.path.startswith("/wp-content/uploads/2025/08/")
        or not parsed.path.endswith(".zip")
    ):
        raise ValueError(f"Non-official or unexpected GSI ZIP URL: {url}")
    dest.parent.mkdir(parents=True, exist_ok=True)
    part = dest.with_suffix(".zip.part")
    digest = hashlib.sha256()
    count = 0
    try:
        with session.get(url, stream=True, timeout=(20, 120)) as response:
            response.raise_for_status()
            size = int(response.headers.get("Content-Length", "0") or "0")
            if size > DOWNLOAD_LIMIT:
                raise ValueError("GSI ZIP exceeds source size limit")
            with part.open("wb") as handle:
                for chunk in response.iter_content(1024 * 1024):
                    count += len(chunk)
                    if count > DOWNLOAD_LIMIT:
                        raise ValueError("GSI ZIP exceeded streamed size limit")
                    digest.update(chunk)
                    handle.write(chunk)
        if digest.hexdigest() != row["sha256"] or count != row["bytes"]:
            raise ValueError("Downloaded GSI ZIP does not match committed original SHA/size")
        part.replace(dest)
    finally:
        part.unlink(missing_ok=True)


def _extract_one(archive: zipfile.ZipFile, stem: str, directory: Path) -> Path:
    """Extract only matching shapefile components without zip-slip paths."""
    candidate = None
    total = 0
    for member in archive.infolist():
        path = Path(member.filename)
        if (
            member.is_dir()
            or str(path.with_suffix("")).casefold() != stem.casefold()
            or path.suffix.lower() not in {
                ".shp", ".shx", ".dbf", ".prj", ".cpg", ".qix", ".sbn", ".sbx",
            }
        ):
            continue
        if path.is_absolute() or ".." in path.parts or len(path.parts) > 5:
            raise ValueError("Unsafe GSI source ZIP member")
        total += member.file_size
        if total > 1_000_000_000:
            raise ValueError("GSI extracted district group too large")
        out = directory / path
        out.parent.mkdir(parents=True, exist_ok=True)
        with archive.open(member) as source, out.open("wb") as target:
            shutil.copyfileobj(source, target)
        if path.suffix.lower() == ".shp":
            candidate = out
    if candidate is None:
        raise ValueError("Source ZIP contained no extracted .shp member")
    return candidate


def _small_field_profile(frame, field: str) -> dict:
    """Summarise low-cardinality RAW labels; no source code interpretation."""
    values = frame[field].astype("string").fillna("<NULL>").str.strip()
    counts = values.value_counts(dropna=False)
    return {
        "field": field,
        "unique_raw_values": int(len(counts)),
        "complete_values_recorded": len(counts) <= 25,
        "raw_value_counts": {
            str(name)[:110]: int(n) for name, n in counts.iloc[:25].items()
        },
    }


def inspect_archive(path: Path, row: dict) -> dict:
    """Full row/geometry reads, original CRS/fields and class candidates."""
    import geopandas as gpd
    import pyogrio
    from pyproj import CRS, Transformer
    import shapely

    if not path.is_file() or sha256(path) != row["sha256"]:
        raise ValueError("Original GSI source checksum missing or changed")
    if path.stat().st_size != row["bytes"]:
        raise ValueError("GSI original file size changed")
    structural = check_shapefile_zip(path)
    groups = structural["complete_shapefile_groups"]
    if len(groups) != 1:
        raise ValueError("More than one complete shapefile group: manual layer choice needed")
    with tempfile.TemporaryDirectory(prefix="kerala-gsi-") as tmp:
        with zipfile.ZipFile(path) as archive:
            shp = _extract_one(archive, groups[0], Path(tmp))
        info = pyogrio.read_info(str(shp))
        frame = gpd.read_file(shp, engine="pyogrio")
        if not len(frame):
            raise ValueError("GSI shapefile has zero features")
        if frame.crs is None or info.get("crs") is None:
            raise ValueError("GSI shapefile lacks a valid original source CRS")
        source_crs = CRS.from_user_input(frame.crs)
        if not source_crs.is_projected and not source_crs.is_geographic:
            raise ValueError("GSI shapefile's CRS is not interpretable as horizontal geography")
        transform = Transformer.from_crs(source_crs, "EPSG:4326", always_xy=True)
        bbox = shapely.transform(
            shapely.box(*[float(v) for v in frame.total_bounds]),
            transform.transform,
            interleaved=False,
        ).bounds
        w, s, e, n = bbox
        kw, ks, ke, kn = ENVELOPE
        if (
            not all(abs(v) < 10000 for v in bbox)
            or e < kw or w > ke or n < ks or s > kn
        ):
            raise ValueError("GSI original geometries lie outside Kerala test envelope")
        geometry = frame.geometry
        null_count = int(geometry.isna().sum())
        empty_count = int(geometry.is_empty.sum())
        valid = shapely.is_valid(geometry.array)
        invalid_count = int((~valid).sum()) - null_count
        invalid_count = max(0, invalid_count)
        reasons = Counter(
            str(value) for value in shapely.is_valid_reason(geometry[~valid].array)[:12]
        )
        geom_types = {
            str(k): int(v) for k, v in geometry.geom_type.value_counts().items()
        }
        columns = [
            {"name": name, "dtype": str(frame[name].dtype)}
            for name in frame.columns if name != frame.geometry.name
        ]
        priority = [
            name for name in frame.columns
            if name != frame.geometry.name and any(
                word in name.lower() for word in SUSCEPTIBILITY_FIELDS
            )
        ]
        raw_profiles = [_small_field_profile(frame, name) for name in priority]
        return {
            "district_source_label": row["district"],
            "source_url": row["source_url"],
            "original_zip_sha256": row["sha256"],
            "original_zip_bytes": row["bytes"],
            "internal_shapefile_group": groups[0],
            "feature_count": len(frame),
            "original_crs": source_crs.to_string(),
            "source_bounds_raw_crs": [float(v) for v in frame.total_bounds],
            "source_extent_wgs84": [float(v) for v in bbox],
            "source_fields": columns,
            "geometry_types": geom_types,
            "null_geometries": null_count,
            "empty_geometries": empty_count,
            "invalid_geometries": invalid_count,
            "sample_invalid_geometry_reasons": dict(reasons),
            "source_category_candidate_fields": priority,
            "source_raw_category_profiles": raw_profiles,
            "all_features_read": int(info["features"]) == len(frame),
            "has_polygonal_geometry_only": all(
                typ in {"Polygon", "MultiPolygon"} for typ in geom_types
            ),
            "district_membership_against_official_boundary_verified": False,
            "cross_district_overlap_verified": False,
            "legal_buildability_verified": False,
            "siting_area_sq_km": None,
            "siting_capacity_mw": None,
        }


def run(
    root: Path,
    raw_dir: Path,
    output: Path,
    *,
    download: bool = False,
) -> dict:
    rows = _read_manifest(root)
    record = {
        "classification": "original_gsi_2022_archives_geometry_and_raw_attribute_QA_NOT_legal_siting",
        "generated_at_utc": datetime.now(UTC).replace(microsecond=0).isoformat(),
        "source_manifest": ACQUISITION,
        "source_archive_count_expected": 13,
        "source_archive_count_verified": 0,
        "districts_decoded": 0,
        "districts": [],
        "alappuzha": "not_in_KSDMA_published_13_ZIP_set_NOT_a_zero_hazard_class",
        "official_district_boundary_overlay_complete": False,
        "whole_Kerala_coverage_certified": False,
        "class_legend_harmonization_certified": False,
        "per_district_source_labels_preserved": True,
        "provisional_nonlegal_layer_only": True,
        "model_eligible_land_sq_km": None,
        "model_capacity_mw": None,
        "audit_gate_closed": False,
    }
    session = requests.Session()
    session.headers["User-Agent"] = "Kerala2040Research/1.0"
    try:
        for row in rows:
            path = raw_dir / Path(urlparse(row["source_url"]).path).name
            try:
                if download:
                    _download_checked(session, row, path)
                if not path.is_file():
                    raise FileNotFoundError("Original ZIP unavailable; enable --download")
                record["source_archive_count_verified"] += int(
                    sha256(path) == row["sha256"] and path.stat().st_size == row["bytes"]
                )
                result = inspect_archive(path, row)
                record["districts_decoded"] += 1
                result["inspection_status"] = "original_geometry_and_raw_attribute_inspected"
            except Exception as exc:  # noqa: BLE001 - don't misstate partial success
                result = {
                    "district_source_label": row["district"],
                    "source_url": row["source_url"],
                    "original_zip_sha256": row["sha256"],
                    "inspection_status": "blocked_source_or_decode_failed",
                    "error": f"{type(exc).__name__}: {exc}",
                }
            record["districts"].append(result)
            print(
                f"GSI {row['district']}: {result['inspection_status']} "
                f"features={result.get('feature_count', 'NA')} "
                f"CRS={result.get('original_crs', 'NA')} "
                f"fields={result.get('source_category_candidate_fields', [])} "
                f"error={result.get('error', '')}",
                flush=True,
            )
    finally:
        session.close()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(record, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print("GSI_GEO_QA_SUMMARY=" + json.dumps({
        "verified_original_archives": record["source_archive_count_verified"],
        "districts_decoded": record["districts_decoded"],
        "feature_total": sum(d.get("feature_count", 0) for d in record["districts"]),
        "invalid_geometries_total": sum(
            d.get("invalid_geometries", 0) for d in record["districts"]
        ),
        "raw_category_candidate_fields_by_district": {
            d["district_source_label"]: d.get("source_category_candidate_fields", [])
            for d in record["districts"]
        },
    }, allow_nan=False))
    return record


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument(
        "--raw-dir", type=Path, default=Path("results/gis/pilot_raw/ksdma")
    )
    parser.add_argument(
        "--output", type=Path, default=Path("results/gis/gsi_2022_geometry_audit.json")
    )
    parser.add_argument("--download", action="store_true")
    args = parser.parse_args()
    report = run(args.root, args.raw_dir, args.output, download=args.download)
    return 0 if report["districts_decoded"] == 13 else 2


if __name__ == "__main__":
    raise SystemExit(main())
