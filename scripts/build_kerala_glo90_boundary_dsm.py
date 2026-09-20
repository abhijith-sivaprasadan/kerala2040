"""Build a Kerala-boundary Copernicus GLO-90 DSM and descriptive slope QA.

This uses hash-verified public GLO-90 source tiles plus the hash-verified NWIC
Kerala administrative polygon. It proves raster coverage only for that boundary
version. It does NOT turn a DSM into bare-earth terrain, a legal exclusion, or
renewable-siting eligibility.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import tempfile
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
import rasterio
import requests
from pyproj import Transformer
from rasterio.features import geometry_mask
from rasterio.merge import merge
from rasterio.transform import array_bounds
from rasterio.warp import Resampling, calculate_default_transform, reproject
from shapely.geometry import mapping
from shapely.ops import transform as shapely_transform

from acquire_copernicus_glo90_envelope import inspect_tile, sha256
from audit_official_kerala_boundary_dem import _kerala_feature, _parse_geojson

DEM_MANIFEST = Path("data/evidence/gis/copernicus_glo90_envelope_2026_09_20.json")
BOUNDARY_EVIDENCE = Path(
    "data/evidence/gis/nwic_kerala_boundary_dem_tile_intersections_2026_09_20.json"
)
TARGET_CRS = "EPSG:32643"
TARGET_RESOLUTION_M = 90.0


def download_verified(
    session: requests.Session, url: str, path: Path, expected_sha256: str,
    max_bytes: int = 40_000_000,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    partial = path.with_suffix(path.suffix + ".part")
    digest = hashlib.sha256()
    total = 0
    try:
        with session.get(url, stream=True, timeout=(20, 120)) as response:
            response.raise_for_status()
            declared = int(response.headers.get("Content-Length", "0") or "0")
            if declared > max_bytes:
                raise ValueError("source file exceeds cap")
            with partial.open("wb") as output:
                for chunk in response.iter_content(1024 * 1024):
                    if not chunk:
                        continue
                    total += len(chunk)
                    if total > max_bytes:
                        raise ValueError("streamed source file exceeds cap")
                    digest.update(chunk)
                    output.write(chunk)
        if digest.hexdigest() != expected_sha256:
            raise ValueError("source SHA256 differs from committed evidence")
        partial.replace(path)
    except Exception:
        partial.unlink(missing_ok=True)
        raise


def _download_bytes(
    session: requests.Session, url: str, expected_sha256: str,
    max_bytes: int = 30_000_000,
) -> bytes:
    chunks = []
    total = 0
    digest = hashlib.sha256()
    with session.get(url, stream=True, timeout=(20, 120)) as response:
        response.raise_for_status()
        for chunk in response.iter_content(1024 * 1024):
            if not chunk:
                continue
            total += len(chunk)
            if total > max_bytes:
                raise ValueError("boundary archive exceeds size cap")
            digest.update(chunk)
            chunks.append(chunk)
    if digest.hexdigest() != expected_sha256:
        raise ValueError("boundary source SHA256 differs from committed evidence")
    return b"".join(chunks)


def _source_tiles(root: Path) -> list[dict]:
    evidence = json.loads((root / DEM_MANIFEST).read_text())
    rows = [
        row for row in evidence["original_tiles_and_hashes"]
        if row["status"] == "original_tif_downloaded"
    ]
    if len(rows) != 14:
        raise ValueError("Expected 14 published original GLO-90 tiles")
    if any(not row.get("sha256") for row in rows):
        raise ValueError("Published source tile missing committed hash")
    return rows


def _load_boundary(root: Path, session: requests.Session):
    evidence = json.loads((root / BOUNDARY_EVIDENCE).read_text())
    if evidence["missing_source_tile_intersection_with_official_kerala"]["count"] != 0:
        raise ValueError("Committed boundary evidence intersects an unpublished tile")
    raw = _download_bytes(
        session,
        evidence["original_source_url"],
        evidence["original_sha256"],
    )
    collection = _parse_geojson(raw)
    geometry, properties, area_sq_km = _kerala_feature(collection)
    if evidence["source_crs"] != "EPSG:7755 / India NSF LCC":
        raise ValueError("Boundary evidence CRS changed")
    return geometry, properties, area_sq_km, hashlib.sha256(raw).hexdigest()


def _write_raster(path: Path, data: np.ndarray, profile: dict) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    with rasterio.open(path, "w", **profile) as dst:
        dst.write(data.astype("float32"), 1)
    return sha256(path)


def _slope_from_projected_dsm(
    data: np.ndarray, resolution_m: float,
) -> tuple[np.ndarray, np.ndarray]:
    """Central-difference slope; edge/invalid-neighbour cells are NaN."""
    if data.ndim != 2:
        raise ValueError("DSM must be a 2D array")
    slope = np.full(data.shape, np.nan, dtype="float32")
    valid = np.isfinite(data)
    neighborhood = (
        valid[1:-1, 1:-1]
        & valid[1:-1, :-2]
        & valid[1:-1, 2:]
        & valid[:-2, 1:-1]
        & valid[2:, 1:-1]
    )
    center = data[1:-1, 1:-1]
    dzdx = (data[1:-1, 2:] - data[1:-1, :-2]) / (2 * resolution_m)
    dzdy = (data[2:, 1:-1] - data[:-2, 1:-1]) / (2 * resolution_m)
    gradient = np.sqrt(dzdx * dzdx + dzdy * dzdy)
    local = np.degrees(np.arctan(gradient)).astype("float32")
    out = slope[1:-1, 1:-1]
    out[neighborhood] = local[neighborhood]
    slope[1:-1, 1:-1] = out
    return slope, neighborhood


def _summary(values: np.ndarray) -> dict:
    finite = values[np.isfinite(values)]
    if finite.size == 0:
        raise ValueError("No finite values in derived raster")
    return {
        "finite_pixels": int(finite.size),
        "min": float(np.min(finite)),
        "p05": float(np.percentile(finite, 5)),
        "p50": float(np.percentile(finite, 50)),
        "p95": float(np.percentile(finite, 95)),
        "p99": float(np.percentile(finite, 99)),
        "max": float(np.max(finite)),
        "mean": float(np.mean(finite)),
    }


def build(
    root: Path,
    raw_dir: Path,
    output_dir: Path,
    output_json: Path,
) -> dict:
    rows = _source_tiles(root)
    session = requests.Session()
    session.headers.update({
        "User-Agent": (
            "Kerala2040Research/1.0 "
            "(+https://github.com/abhijith-sivaprasadan/kerala2040)"
        )
    })
    tile_paths = []
    source_records = []
    try:
        boundary_wgs84, boundary_props, boundary_area_sq_km, boundary_sha = (
            _load_boundary(root, session)
        )
        for row in rows:
            target = raw_dir / Path(row["url"]).name
            if not target.is_file() or sha256(target) != row["sha256"]:
                download_verified(session, row["url"], target, row["sha256"])
            info = inspect_tile(target, row["latitude"], row["longitude"])
            tile_paths.append(target)
            source_records.append({
                "latitude": row["latitude"],
                "longitude": row["longitude"],
                "source_sha256": row["sha256"],
                "bytes": target.stat().st_size,
                "structure_qa": info,
            })
    finally:
        session.close()

    datasets = [rasterio.open(path) for path in tile_paths]
    try:
        mosaic, transform = merge(datasets, method="first", nodata=np.nan)
        source = mosaic[0].astype("float32")
        height, width = source.shape
        inside = ~geometry_mask(
            [mapping(boundary_wgs84)],
            out_shape=(height, width),
            transform=transform,
            invert=False,
            all_touched=False,
        )
        # geometry_mask(invert=False): False inside geometries, hence ~ mask.
        inside_pixels = int(np.count_nonzero(inside))
        finite_inside = np.isfinite(source) & inside
        missing_inside = inside & ~np.isfinite(source)
        if inside_pixels == 0:
            raise ValueError("Official Kerala boundary rasterizes to zero source pixels")

        clipped_source = np.where(inside, source, np.nan).astype("float32")
        source_profile = datasets[0].profile.copy()
        source_profile.update(
            driver="GTiff", width=width, height=height, transform=transform,
            count=1, dtype="float32", nodata=np.nan, tiled=True,
            compress="deflate", predictor=3, blockxsize=256, blockysize=256,
        )
        source_path = output_dir / "kerala_boundary_GLO90_DSM_native_grid.tif"
        source_sha = _write_raster(source_path, clipped_source, source_profile)

        west, south, east, north = boundary_wgs84.bounds
        dst_transform, dst_width, dst_height = calculate_default_transform(
            "EPSG:4326", TARGET_CRS, width, height,
            *array_bounds(height, width, transform),
            resolution=TARGET_RESOLUTION_M,
        )
        projected = np.full((dst_height, dst_width), np.nan, dtype="float32")
        reproject(
            source=clipped_source,
            destination=projected,
            src_transform=transform,
            src_crs="EPSG:4326",
            src_nodata=np.nan,
            dst_transform=dst_transform,
            dst_crs=TARGET_CRS,
            dst_nodata=np.nan,
            resampling=Resampling.bilinear,
        )
        boundary_projected = shapely_transform(
            Transformer.from_crs(
                "EPSG:4326", TARGET_CRS, always_xy=True
            ).transform,
            boundary_wgs84,
        )
        projected_inside = ~geometry_mask(
            [mapping(boundary_projected)],
            out_shape=projected.shape,
            transform=dst_transform,
            invert=False,
            all_touched=False,
        )
        projected[~projected_inside] = np.nan
        projected_missing_inside = projected_inside & ~np.isfinite(projected)

        projected_profile = source_profile.copy()
        projected_profile.update(
            crs=TARGET_CRS, transform=dst_transform,
            width=dst_width, height=dst_height,
        )
        projected_path = output_dir / "kerala_boundary_GLO90_DSM_EPSG32643_90m.tif"
        projected_sha = _write_raster(
            projected_path, projected, projected_profile
        )

        slope, _ = _slope_from_projected_dsm(projected, TARGET_RESOLUTION_M)
        slope[~projected_inside] = np.nan
        slope_path = output_dir / "kerala_boundary_GLO90_slope_degrees_90m.tif"
        slope_sha = _write_raster(slope_path, slope, projected_profile)

        result = {
            "classification": (
                "hash_verified_official_boundary_clipped_GLO90_DSM_and_"
                "descriptive_slope_NOT_bare_earth_NOT_siting_eligibility"
            ),
            "built_at_utc": datetime.now(UTC).replace(microsecond=0).isoformat(),
            "source_dem_manifest": str(DEM_MANIFEST),
            "source_boundary_evidence": str(BOUNDARY_EVIDENCE),
            "source_product": "Copernicus DEM GLO-90 Digital Surface Model",
            "source_product_release": "2021",
            "source_horizontal_crs": "EPSG:4326",
            "source_vertical_crs_documented": "EPSG:3855 EGM2008",
            "source_vertical_unit_documented": "metres",
            "source_vertical_datum_independently_verified_from_current_official_documentation": True,
            "source_is_bare_earth_dtm": False,
            "source_original_tiles": len(source_records),
            "source_original_tile_hashes_reverified": True,
            "source_records": source_records,
            "official_boundary": {
                "source_sha256": boundary_sha,
                "state_name": boundary_props.get("state_name", "Kerala"),
                "source_agency_property": boundary_props.get("src_agency"),
                "analysis_bounds_wgs84": [west, south, east, north],
                "approx_area_sq_km_NOT_land_eligibility": boundary_area_sq_km,
                "boundary_version_pixel_coverage_tested": True,
            },
            "native_grid_boundary_clip": {
                "path": str(source_path),
                "sha256": source_sha,
                "width": width,
                "height": height,
                "source_resolution_degrees": list(datasets[0].res),
                "boundary_pixel_centres": inside_pixels,
                "finite_boundary_pixel_centres": int(
                    np.count_nonzero(finite_inside)
                ),
                "nonfinite_boundary_pixel_centres": int(
                    np.count_nonzero(missing_inside)
                ),
                "pixel_center_coverage_fraction": (
                    float(np.count_nonzero(finite_inside) / inside_pixels)
                ),
                "all_boundary_pixel_centres_have_source_height": (
                    not bool(np.any(missing_inside))
                ),
                "coverage_rule": (
                    "pixel centres inside this NWIC Kerala polygon; coastline "
                    "subpixel coverage is not inferred"
                ),
            },
            "projected_dsm": {
                "path": str(projected_path),
                "sha256": projected_sha,
                "crs": TARGET_CRS,
                "resolution_m": TARGET_RESOLUTION_M,
                "width": dst_width,
                "height": dst_height,
                "boundary_pixel_centres": int(
                    np.count_nonzero(projected_inside)
                ),
                "nonfinite_boundary_pixel_centres_after_bilinear_reprojection": int(
                    np.count_nonzero(projected_missing_inside)
                ),
                "height_m_summary": _summary(projected),
                "resampling": "bilinear",
                "status": "derived_analysis_DSM_not_original_source",
            },
            "descriptive_slope": {
                "path": str(slope_path),
                "sha256": slope_sha,
                "units": "degrees",
                "algorithm": (
                    "central difference on bilinear-reprojected 90 m DSM; "
                    "requires finite N/S/E/W neighbours"
                ),
                "slope_summary_degrees": _summary(slope),
                "technology_threshold_selected": False,
                "land_eligibility_interpretation": False,
                "status": (
                    "descriptive_DSM_surface_slope_not_validated_"
                    "technology_constraint"
                ),
            },
            "seam_acceptance_threshold_defined": False,
            "technology_specific_slope_rules_verified": False,
            "legal_exclusion_applied": False,
            "ecological_capacity_ceiling_ready": False,
            "eligible_area_sq_km": None,
            "capacity_ceiling_mw": None,
        }
    finally:
        for dataset in datasets:
            dataset.close()

    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    compact = {
        "built_at_utc": result["built_at_utc"],
        "classification": result["classification"],
        "source_product_release": result["source_product_release"],
        "source_vertical_crs_documented": result["source_vertical_crs_documented"],
        "source_original_tiles": result["source_original_tiles"],
        "official_boundary": result["official_boundary"],
        "native_grid_boundary_clip": result["native_grid_boundary_clip"],
        "projected_dsm": result["projected_dsm"],
        "descriptive_slope": result["descriptive_slope"],
        "technology_specific_slope_rules_verified": False,
        "legal_exclusion_applied": False,
        "ecological_capacity_ceiling_ready": False,
        "eligible_area_sq_km": None,
        "capacity_ceiling_mw": None,
    }
    print("KERALA_DSM_QA_COMPACT=" + json.dumps(
        compact, separators=(",", ":"), allow_nan=False
    ), flush=True)
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument(
        "--raw-dir", type=Path,
        default=Path("results/gis/kerala_glo90_original_tiles"),
    )
    parser.add_argument(
        "--output-dir", type=Path,
        default=Path("results/gis/kerala_glo90_boundary"),
    )
    parser.add_argument(
        "--output-json", type=Path,
        default=Path("results/gis/kerala_glo90_boundary_slope_qa.json"),
    )
    args = parser.parse_args()
    report = build(
        args.root, args.raw_dir, args.output_dir, args.output_json
    )
    print(json.dumps({
        "classification": report["classification"],
        "native_coverage_fraction": report[
            "native_grid_boundary_clip"
        ]["pixel_center_coverage_fraction"],
        "native_missing_inside": report[
            "native_grid_boundary_clip"
        ]["nonfinite_boundary_pixel_centres"],
        "projected_missing_inside": report[
            "projected_dsm"
        ]["nonfinite_boundary_pixel_centres_after_bilinear_reprojection"],
        "slope_finite_pixels": report[
            "descriptive_slope"
        ]["slope_summary_degrees"]["finite_pixels"],
        "output": str(args.output_json),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
