"""Acquire and QA source Copernicus GLO-90 DSM tiles over Kerala's envelope.

An envelope is not an authenticated Kerala boundary. No claim of bare-earth
elevation, source vintage FY2024-25, slope eligibility, or legal exclusions.
Original COGs and optional mosaic are CI artifacts, not committed model inputs.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
import rasterio
import requests
from rasterio.merge import merge

SOURCE = "https://copernicus-dem-90m.s3.amazonaws.com"
LATITUDES = tuple(range(8, 13))
LONGITUDES = tuple(range(74, 78))
SOURCE_CRS = "EPSG:4326"
EXPECTED_RES = 1 / 1200


def tile_name(latitude: int, longitude: int) -> str:
    return f"Copernicus_DSM_COG_30_N{latitude:02}_00_E{longitude:03}_00_DEM"


def tile_url(latitude: int, longitude: int) -> str:
    name = tile_name(latitude, longitude)
    return f"{SOURCE}/{name}/{name}.tif"


def sha256(path: Path) -> str:
    sha = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            sha.update(chunk)
    return sha.hexdigest()


def download(session: requests.Session, url: str, target: Path,
             max_size: int = 32_000_000) -> dict:
    target.parent.mkdir(parents=True, exist_ok=True)
    partial = target.with_suffix(".tif.part")
    total = 0
    try:
        with session.get(url, timeout=(20, 90), stream=True) as response:
            if response.status_code == 404:
                return {"status": "tile_not_published_http_404", "url": url}
            response.raise_for_status()
            declared = int(response.headers.get("Content-Length") or 0)
            if declared > max_size:
                raise ValueError("Tile exceeds per-file download cap")
            with partial.open("wb") as dest:
                for fragment in response.iter_content(1024 * 1024):
                    if not fragment:
                        continue
                    total += len(fragment)
                    if total > max_size:
                        raise ValueError("Tile exceeds streamed download cap")
                    dest.write(fragment)
        partial.replace(target)
    except Exception:
        partial.unlink(missing_ok=True)
        raise
    return {"status": "original_tif_downloaded", "url": url,
            "bytes": total, "sha256": sha256(target)}


def inspect_tile(path: Path, latitude: int, longitude: int) -> dict:
    with rasterio.open(path) as dataset:
        if dataset.count != 1 or dataset.driver != "GTiff":
            raise ValueError(f"{path.name}: not a single-band GeoTIFF")
        if dataset.crs is None or dataset.crs.to_string() != SOURCE_CRS:
            raise ValueError(f"{path.name}: unexpected CRS")
        if dataset.width != 1200 or dataset.height != 1200:
            raise ValueError(f"{path.name}: unexpected tile dimensions")
        if any(abs(value - EXPECTED_RES) > 1e-10 for value in dataset.res):
            raise ValueError(f"{path.name}: unexpected 3-arcsecond pixel spacing")
        west, south, east, north = dataset.bounds
        if not all(abs(a - b) <= 0.001 for a, b in (
            (west, longitude), (east, longitude + 1),
            (south, latitude), (north, latitude + 1),
        )):
            raise ValueError(f"{path.name}: tile geolocation does not match URL")
        if dataset.dtypes[0] not in ("float32", "float64"):
            raise ValueError(f"{path.name}: unexpected height datatype")
        data = dataset.read(1, masked=True)
        values = data.compressed()
        if not len(values):
            raise ValueError(f"{path.name}: no decoded height samples")
        finite = np.isfinite(values)
        finite_values = values[finite]
        if not len(finite_values):
            raise ValueError(f"{path.name}: no finite samples")
        return {
            "source_crs": SOURCE_CRS, "width": dataset.width,
            "height": dataset.height, "dtype": dataset.dtypes[0],
            "resolution_degrees": list(dataset.res),
            "source_nodata_metadata": dataset.nodata,
            "has_source_mask": bool(np.ma.getmaskarray(data).any()),
            "bounds_wgs84": [west, south, east, north],
            "finite_sample_count": len(finite_values),
            "nonfinite_sample_count": len(values) - len(finite_values),
            "min_sample_source_height_units": float(finite_values.min()),
            "max_sample_source_height_units": float(finite_values.max()),
            "zero_sample_count_ambiguous_sea_or_terrain": int(
                np.count_nonzero(finite_values == 0)
            ),
            "vertical_datum_independently_verified": False,
            "bare_earth_elevation": False,
        }


def measure_seam(a: Path, b: Path, axis: str) -> dict:
    """Adjacent pixel-center differences are only a diagnostic, not seam truth."""
    with rasterio.open(a) as left, rasterio.open(b) as right:
        if axis == "east":
            x = left.read(1, window=((0, 1200), (1199, 1200))).reshape(-1)
            y = right.read(1, window=((0, 1200), (0, 1))).reshape(-1)
        else:
            x = left.read(1, window=((0, 1), (0, 1200))).reshape(-1)
            y = right.read(1, window=((1199, 1200), (0, 1200))).reshape(-1)
        finite = np.isfinite(x) & np.isfinite(y)
        values = np.abs(x[finite] - y[finite])
        return {
            "adjacent_finite_pairs": len(values),
            "absolute_height_step_median_source_units": (
                float(np.median(values)) if len(values) else None
            ),
            "absolute_height_step_p95_source_units": (
                float(np.percentile(values, 95)) if len(values) else None
            ),
            "absolute_height_step_max_source_units": (
                float(values.max()) if len(values) else None
            ),
            "note": "Natural terrain/coastal edge gradients are not systematic seams; no arbitrary pass threshold.",
        }


def run(output: Path, tile_dir: Path, mosaic_path: Path, *,
        max_download_mb: int = 32) -> dict:
    output.parent.mkdir(parents=True, exist_ok=True)
    tile_dir.mkdir(parents=True, exist_ok=True)
    records = []
    available = {}
    session = requests.Session()
    session.headers.update({"User-Agent": "Kerala2040Research/1.0 (+https://github.com/abhijith-sivaprasadan/kerala2040)"})
    try:
        for lat in LATITUDES:
            for lon in LONGITUDES:
                target = tile_dir / (tile_name(lat, lon) + ".tif")
                url = tile_url(lat, lon)
                try:
                    if target.exists():
                        downloaded = {
                            "status": "local_original_rechecked", "url": url,
                            "bytes": target.stat().st_size, "sha256": sha256(target),
                        }
                    else:
                        downloaded = download(
                            session, url, target, max_download_mb * 1_000_000
                        )
                    if downloaded["status"] == "tile_not_published_http_404":
                        row = {"latitude": lat, "longitude": lon, **downloaded}
                    else:
                        row = {"latitude": lat, "longitude": lon, **downloaded,
                               "structure_qa": inspect_tile(target, lat, lon)}
                        available[(lat, lon)] = target
                except Exception as exc:  # noqa: BLE001 - keep every failed source tile as audit evidence
                    row = {"latitude": lat, "longitude": lon, "url": url,
                           "status": "tile_download_or_qa_failed",
                           "error": f"{type(exc).__name__}: {exc}"}
                print(json.dumps({k: row[k] for k in (
                    "latitude", "longitude", "status", "error"
                ) if k in row}), flush=True)
                records.append(row)
    finally:
        session.close()
    seams = []
    for (lat, lon), path in available.items():
        for axis, neighbor in (("east", (lat, lon + 1)),
                               ("north", (lat + 1, lon))):
            if neighbor in available:
                seams.append({
                    "first": [lat, lon], "second": list(neighbor),
                    "direction": axis,
                    **measure_seam(path, available[neighbor], axis),
                })
    mosaic = {"status": "not_created_coverage_or_alignment_unverified"}
    if len(available) == len(LATITUDES) * len(LONGITUDES):
        sources = [rasterio.open(available[lat, lon])
                   for lat in LATITUDES for lon in LONGITUDES]
        try:
            arrays, transform = merge(sources, method="first", nodata=np.nan)
            # Source has no nodata declaration; this mosaic is a DSM diagnostic,
            # not land-versus-sea or valid Kerala pixel mask.
            profile = sources[0].profile.copy()
            profile.update(
                driver="GTiff", width=arrays.shape[2], height=arrays.shape[1],
                transform=transform, count=1, dtype="float32",
                nodata=np.nan, tiled=True, compress="deflate",
                predictor=3, blockxsize=256, blockysize=256,
            )
            mosaic_path.parent.mkdir(parents=True, exist_ok=True)
            with rasterio.open(mosaic_path, "w", **profile) as dest:
                dest.write(arrays[0].astype("float32"), 1)
            mosaic = {
                "status": "complete_envelope_grid_mosaic_NOT_statewide_GIS_suitability",
                "sha256": sha256(mosaic_path),
                "bytes": mosaic_path.stat().st_size,
                "width": arrays.shape[2], "height": arrays.shape[1],
                "crs": SOURCE_CRS,
                "nodata_derived_not_original": "NaN",
                "bounds_wgs84": list(rasterio.transform.array_bounds(
                    arrays.shape[1], arrays.shape[2], transform,
                )),
                "source_tiles": len(available),
                "vertical_datum_independently_verified": False,
                "kerala_official_boundary_clip_verified": False,
            }
        finally:
            for source in sources:
                source.close()
    result = {
        "classification": "official_public_GLO90_DSM_Kerala_envelope_tile_acquisition_NOT_validated_terrain_or_siting",
        "run_utc": datetime.now(UTC).replace(microsecond=0).isoformat(),
        "source": SOURCE,
        "scope": "unclipped approximate bounding envelope lat 8-13N, lon 74-78E; not a Kerala administrative polygon",
        "requested_tiles": len(LATITUDES) * len(LONGITUDES),
        "original_tiles_acquired_and_structurally_checked": len(available),
        "missing_or_failed_tiles": len(records) - len(available),
        "tiles": records,
        "adjacent_tile_seam_diagnostics": seams,
        "mosaic": mosaic,
        "source_product_type": "digital_surface_model_NOT_bare_earth_DTM",
        "coastal_zero_height_is_not_land_mask": True,
        "source_vertical_datum_independently_verified": False,
        "kerala_official_boundary_clip_verified": False,
        "technological_slope_constraint_validated": False,
        "legal_exclusion_layer_ready": False,
        "ecological_capacity_ceiling_ready": False,
        "eligible_area_sq_km": None,
        "capacity_ceiling_mw": None,
    }
    output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    print(json.dumps({
        "classification": result["classification"],
        "acquired": len(available), "requested": len(records),
        "mosaic": mosaic["status"], "seams": len(seams),
        "evidence_json": str(output),
    }, indent=2))
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output", type=Path,
        default=Path("results/gis/copernicus_glo90_envelope_qa.json"),
    )
    parser.add_argument(
        "--tile-dir", type=Path,
        default=Path("results/gis/copernicus_glo90_originals"),
    )
    parser.add_argument(
        "--mosaic", type=Path,
        default=Path("results/gis/copernicus_glo90_envelope_DSM.tif"),
    )
    args = parser.parse_args()
    run(args.output, args.tile_dir, args.mosaic)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
