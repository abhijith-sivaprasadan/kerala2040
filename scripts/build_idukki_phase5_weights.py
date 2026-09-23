#!/usr/bin/env python3
"""Build weighted ERA5-Land pixels from an independently checked reservoir catchment.

No default polygon, invented watershed, district proxy, or Periyar-wide substitute.
A reviewer must select a single WGS84 GeoJSON feature that genuinely represents
the intercepted Idukki RESERVOIR catchment (not the whole Periyar river basin).
Grid cell overlaps are computed in equal-area EPSG:6933, not by centre counting.

pip install geopandas pyproj shapely
python scripts/build_idukki_phase5_weights.py --geometry PRIVATE/catchment.geojson \
 --grid-csv PRIVATE/era5_grid.csv --grid-spacing-deg 0.1 \
 --source-id REVIEWED_SOURCE_ID --source-url https://... \
 --reviewer YOUR_NAME --expected-area-km2 SOURCE_DECLARED_AREA \
 --out PRIVATE/idukki_weights.csv
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import pandas as pd

SUPPORT = "IDUKKI_RESERVOIR_INTERCEPTED_CATCHMENT"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def make_weights(geometry_path: Path, grid_path: Path, out: Path,
                 spacing: float, source_id: str, source_url: str,
                 reviewer: str, expected_area_km2: float,
                 max_area_error_pct: float = 5.) -> dict:
    try:
        from pyproj import Transformer
        from shapely.geometry import box, shape
        from shapely.ops import transform
    except ImportError as exc:
        raise RuntimeError("Install geo extras: shapely + pyproj") from exc
    if not (0.01 <= spacing <= 0.25) or not (0 < expected_area_km2 < 20000):
        raise ValueError("Supply checked grid resolution and catchment area")
    if not (0 < max_area_error_pct <= 10):
        raise ValueError("Area tolerance must be (0,10] percent")
    if not source_id.strip() or not source_url.startswith("https://") or not reviewer.strip():
        raise ValueError("Reviewer and HTTPS source documentation are mandatory")
    obj = json.loads(geometry_path.read_text(encoding="utf-8"))
    if obj.get("type") == "FeatureCollection":
        if len(obj.get("features", [])) != 1:
            raise ValueError("Select exactly one reviewed catchment feature, never auto-union")
        feature = obj["features"][0]
    elif obj.get("type") == "Feature":
        feature = obj
    else:
        raise ValueError("Input must be a single GeoJSON Feature or one-feature collection")
    crs = obj.get("crs")
    if crs and "4326" not in json.dumps(crs) and "CRS84" not in json.dumps(crs).upper():
        raise ValueError("Supply WGS84 GeoJSON coordinates, do not assume arbitrary CRS")
    geom = shape(feature["geometry"])
    if geom.geom_type not in ("Polygon", "MultiPolygon") or not geom.is_valid or geom.is_empty:
        raise ValueError("A valid single polygonal reservoir catchment is required")
    west, south, east, north = geom.bounds
    if not (60 < west < east < 100 and 0 < south < north < 40):
        raise ValueError("Catchment lies outside reasonable India coordinate bounds")
    project = Transformer.from_crs("EPSG:4326", "EPSG:6933", always_xy=True).transform
    catchment = transform(project, geom)
    actual_area = catchment.area / 1e6
    relative = 100 * abs(actual_area - expected_area_km2) / expected_area_km2
    if relative > max_area_error_pct:
        raise ValueError(f"Geometry area {actual_area:.2f} km² differs from source "
                         f"{expected_area_km2:.2f} km² by {relative:.2f}%")
    grid = pd.read_csv(grid_path)
    if not {"latitude", "longitude"}.issubset(grid):
        raise ValueError("Grid needs original ERA5 latitude,longitude centres")
    if grid[["latitude", "longitude"]].isna().any().any() or grid.duplicated(
            ["latitude", "longitude"]).any():
        raise ValueError("Grid coordinates missing or duplicated")
    results = []
    half = spacing / 2
    for p in grid.itertuples():
        cell = transform(project, box(float(p.longitude)-half, float(p.latitude)-half,
                                      float(p.longitude)+half, float(p.latitude)+half))
        shared = catchment.intersection(cell).area
        if shared > 0:
            results.append({"latitude": float(p.latitude),
                            "longitude": float(p.longitude), "area_m2": shared})
    if not results:
        raise ValueError("No gridded cell overlaps catchment; verify bbox and CRS")
    rows = pd.DataFrame(results)
    area_sum = float(rows.area_m2.sum())
    # A sparse or clipped grid is NOT an area-weighted catchment sample.
    overlap_error = 100 * abs(area_sum - catchment.area) / catchment.area
    if overlap_error > 0.5:
        raise ValueError(f"ERA5 grid covers only {100-overlap_error:.2f}% of catchment area")
    rows["weight"] = rows.area_m2 / area_sum
    rows["source_id"] = source_id
    rows["spatial_support"] = SUPPORT
    rows["geometry_sha256"] = digest(geometry_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    rows[["latitude", "longitude", "weight", "source_id",
          "spatial_support", "geometry_sha256"]].to_csv(out, index=False)
    metadata = {"classification": "reviewed_geometry_provenance_NOT_field_verified_by_script",
                "source_id": source_id, "source_url": source_url,
                "reviewer": reviewer, "geometry_sha256": digest(geometry_path),
                "grid_sha256": digest(grid_path),
                "expected_source_area_km2": expected_area_km2,
                "computed_polygon_area_km2": actual_area,
                "area_difference_percent": relative,
                "cell_overlap_coverage_percent": 100 - overlap_error,
                "selected_cells": len(rows), "grid_spacing_deg": spacing,
                "weight_file_sha256": digest(out),
                "caution": "Check that geometry represents the *reservoir intercepted* catchment "
                           "and includes upstream diversion treatment, not the full river basin."}
    out.with_suffix(".qa.json").write_text(json.dumps(metadata, indent=2)+"\n", encoding="utf-8")
    return metadata


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--geometry", type=Path, required=True)
    p.add_argument("--grid-csv", type=Path, required=True)
    p.add_argument("--grid-spacing-deg", type=float, required=True)
    p.add_argument("--source-id", required=True)
    p.add_argument("--source-url", required=True)
    p.add_argument("--reviewer", required=True)
    p.add_argument("--expected-area-km2", type=float, required=True)
    p.add_argument("--max-area-error-pct", type=float, default=5.)
    p.add_argument("--out", type=Path, required=True)
    a = p.parse_args()
    print(json.dumps(make_weights(a.geometry, a.grid_csv, a.out, a.grid_spacing_deg,
                                  a.source_id, a.source_url, a.reviewer,
                                  a.expected_area_km2, a.max_area_error_pct), indent=2))


if __name__ == "__main__":
    main()
