"""Rebuild the exact NWIC-clipped Kerala NIWE 150 m CSV from pinned originals.

Private derived output; do not redistribute raw NIWE rows publicly until terms
are checked. The gzip is deterministic (mtime=0, no source filename).
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd
from pyproj import Transformer
from shapely import contains_xy, prepare
from shapely.geometry import shape
from shapely.ops import transform

INNER_SHA256 = "f166450c3ea591b5b346f9cd27899b10b6f18ce9cf441c98388c6f0e98d44b38"
NWIC_SHA256 = "a932ea29e7afd0fea1e1068f3beeeadb760e6b2baae9783f5822bbefd4224ebd"
NATIONAL_ROWS = 19_475_568
KERALA_ROWS = 200_692
SOURCE_COLUMNS = (
    "Longitude (E)", "Latitude (N)", "Wind Speed (m/s)",
    "Weibull A (m/s)", "Weibull k", "Air Density (kg/m3)",
    "Wind Power Density (W/sq.m)",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(4 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def rebuild(inner_zip: Path, nwic_artifact: Path, out_dir: Path) -> dict:
    if sha256(inner_zip) != INNER_SHA256:
        raise ValueError("Wrong NIWE original national 150 m nested ZIP SHA256")
    with zipfile.ZipFile(nwic_artifact) as artifact:
        raw = artifact.read("nwic_original/nwic_original_state_boundary_download")
    if hashlib.sha256(raw).hexdigest() != NWIC_SHA256:
        raise ValueError("Wrong NWIC original state-boundary ZIP SHA256")
    with zipfile.ZipFile(io.BytesIO(raw)) as artifact:
        source = json.loads(artifact.read("state_NWIC.GeoJSON"))
    if "7755" not in json.dumps(source.get("crs")):
        raise ValueError("NWIC GeoJSON original CRS must identify EPSG:7755")
    selected = [
        feature for feature in source["features"]
        if feature["properties"].get("state_name") == "Kerala"
    ]
    if len(selected) != 1:
        raise ValueError("Expected exactly one Kerala state-boundary feature")
    geom = transform(
        Transformer.from_crs(7755, 4326, always_xy=True).transform,
        shape(selected[0]["geometry"]),
    )
    if not geom.is_valid:
        raise ValueError("Invalid original Kerala polygon")
    prepare(geom)
    rows: list[pd.DataFrame] = []
    national_count = 0
    with zipfile.ZipFile(inner_zip) as archive, archive.open(
        "150m_Map_Data_A_to_G.csv"
    ) as data:
        for chunk in pd.read_csv(data, chunksize=250_000):
            if tuple(chunk.columns) != SOURCE_COLUMNS:
                raise ValueError("Unexpected national NIWE columns/order")
            national_count += len(chunk)
            lon = chunk[SOURCE_COLUMNS[0]].to_numpy(dtype="float64")
            lat = chunk[SOURCE_COLUMNS[1]].to_numpy(dtype="float64")
            west, south, east, north = geom.bounds
            in_envelope = (
                (lon >= west) & (lon <= east)
                & (lat >= south) & (lat <= north)
            )
            if in_envelope.any():
                subset = np.flatnonzero(in_envelope)
                in_polygon = contains_xy(geom, lon[subset], lat[subset])
                if in_polygon.any():
                    rows.append(chunk.iloc[subset[in_polygon]])
    if national_count != NATIONAL_ROWS:
        raise ValueError(f"Unexpected national rows: {national_count}")
    wind = pd.concat(rows, ignore_index=True)
    if len(wind) != KERALA_ROWS:
        raise ValueError(f"Unexpected exact Kerala point count: {len(wind)}")
    if wind.duplicated(subset=list(SOURCE_COLUMNS[:2])).any():
        raise ValueError("Duplicate NIWE coordinates")
    if not np.isfinite(wind[list(SOURCE_COLUMNS)].to_numpy()).all():
        raise ValueError("Nonfinite NIWE coordinates or resource values")
    if not contains_xy(
        geom,
        wind[SOURCE_COLUMNS[0]].to_numpy(dtype="float64"),
        wind[SOURCE_COLUMNS[1]].to_numpy(dtype="float64"),
    ).all():
        raise ValueError("Point outside original NWIC Kerala polygon")
    out_dir.mkdir(parents=True, exist_ok=True)
    target = out_dir / "NIWE_150m_Kerala_NWIC_point_centres.csv.gz"
    with target.open("wb") as raw_file, gzip.GzipFile(
        fileobj=raw_file, filename="", mode="wb", compresslevel=7, mtime=0
    ) as compressor, io.TextIOWrapper(
        compressor, encoding="utf-8", newline=""
    ) as text_file:
        wind.to_csv(text_file, index=False, float_format="%.8g")
    evidence = {
        "classification": "exact_NWIC_Kerala_NIWE_150m_derived_clip_NOT_capacity",
        "NIWE_inner_original_SHA256": INNER_SHA256,
        "NWIC_original_boundary_SHA256": NWIC_SHA256,
        "original_NWIC_CRS": "EPSG:7755",
        "transformed_coordinates": "EPSG:4326 (lon/lat)",
        "NIWE_CSV_CRS_independently_certified": False,
        "national_rows": national_count,
        "Kerala_point_centres": len(wind),
        "clip_compression": "gzip compresslevel=7 mtime=0 filename=''",
        "clip_sha256": sha256(target),
        "previous_nondeterministic_gzip_sha256": (
            "364808dd40751bd5f3e131e86127dbdab73168d1830a682002de5a4c6fdd0dee"
        ),
        "compressed_bytes_expected_to_match_prior_gzip": False,
        "median_wind_speed_m_s": float(wind["Wind Speed (m/s)"].median()),
        "eligible_area_km2": None,
        "capacity_MW": None,
        "model_ready": False,
    }
    (out_dir / "NIWE_150m_Kerala_clip_rebuild_QA.json").write_text(
        json.dumps(evidence, indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )
    return evidence


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-inner-zip", type=Path, required=True)
    parser.add_argument("--nwic-artifact", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(rebuild(
        args.source_inner_zip, args.nwic_artifact, args.out_dir,
    ), indent=2))


if __name__ == "__main__":
    main()
