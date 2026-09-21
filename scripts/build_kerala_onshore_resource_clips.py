"""Rebuild native-resolution Kerala-only NIWE/GSA descriptive resource clips.

Input ORIGINAL uploaded files (or checksum-verified restored equivalents).
Requires rasterio, shapely, pyproj, pandas, numpy, matplotlib.
Outputs are not licensed for public redistribution until source terms reviewed.
Never interpret source pixel centres as buildable area, capacity or FY generation.
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
import rasterio
from pyproj import Transformer
from rasterio.mask import mask
from shapely import contains_xy, prepare
from shapely.geometry import mapping, shape
from shapely.ops import transform

NWIC_SHA = "a932ea29e7afd0fea1e1068f3beeeadb760e6b2baae9783f5822bbefd4224ebd"
NIWE_SHA = "54196bfa8dfa27295db7f71f100ac63c0b4a77d1dace4da2ae5f9ee2c869d849"
INNER_SHA = "f166450c3ea591b5b346f9cd27899b10b6f18ce9cf441c98388c6f0e98d44b38"
SOURCE = {
    "PVOUT_yearly_total_kWh_kWp": ("New folder (2)(1).zip", "PVOUT.tif"),
    "PVOUT_daily_mean_kWh_kWp": (
        "India_GISdata_LTAy_AvgDailyTotals_GlobalSolarAtlas-v2_GEOTIFF.zip",
        "PVOUT.tif",
    ),
    "GHI_yearly_total_kWh_m2": ("New folder(1).zip", "GHI.tif"),
    "PVOUT_feb_avg_daily_kWh_kWp": (
        "monthlyIndia_GISdata_LTAy_AvgDailyTotals_GlobalSolarAtlas-v2_GEOTIFF(1).zip",
        "PVOUT_02.tif",
    ),
    "PVOUT_jul_avg_daily_kWh_kWp": (
        "monthlyIndia_GISdata_LTAy_AvgDailyTotals_GlobalSolarAtlas-v2_GEOTIFF(1).zip",
        "PVOUT_07.tif",
    ),
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(2 ** 20), b""):
            h.update(chunk)
    return h.hexdigest()


def boundary(original: Path):
    with zipfile.ZipFile(original) as artifact:
        raw = artifact.read("nwic_original/nwic_original_state_boundary_download")
    if hashlib.sha256(raw).hexdigest() != NWIC_SHA:
        raise ValueError("NWIC original hash mismatch")
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        features = json.loads(archive.read("state_NWIC.GeoJSON"))
    if "7755" not in json.dumps(features.get("crs")):
        raise ValueError("NWIC original CRS is not EPSG:7755")
    selected = [
        f for f in features["features"]
        if f["properties"].get("state_name") == "Kerala"
    ]
    if len(selected) != 1:
        raise ValueError("Kerala state feature missing or repeated")
    geom = transform(
        Transformer.from_crs(7755, 4326, always_xy=True).transform,
        shape(selected[0]["geometry"]),
    )
    if not geom.is_valid:
        raise ValueError("Kerala polygon invalid")
    prepare(geom)
    return geom


def process(source_dir: Path, artifact_zip: Path, output: Path) -> dict:
    output.mkdir(parents=True, exist_ok=True)
    geom = boundary(artifact_zip)
    report = {
        "classification": "NWIC_Kerala_exact_native_grid_resource_NOT_capacity",
        "source_boundary_SHA256": NWIC_SHA,
        "source_NIWE_SHA256": NIWE_SHA,
        "source_GSA": "https://globalsolaratlas.info/download/india",
        "source_NIWE": "https://niwe.res.in/Open_data_Set/open_wind_dataset/11/",
        "clipping": "native raster pixel centres and original NIWE point coordinates inside NWIC boundary",
        "capacity_MW": None,
        "offshore": False,
        "model_ready": False,
        "rasters": {},
    }
    for label, (filename, suffix) in SOURCE.items():
        path = source_dir / filename
        with zipfile.ZipFile(path) as archive:
            matches = [m for m in archive.namelist() if m.endswith("/" + suffix)]
        if len(matches) != 1:
            raise ValueError(f"not exactly one matching raster in {filename}: {matches}")
        uri = f"/vsizip/{path.resolve().as_posix()}/{matches[0]}"
        with rasterio.open(uri) as src:
            if src.crs.to_epsg() != 4326:
                raise ValueError("unexpected source CRS")
            array, affine = mask(
                src, [mapping(geom)], crop=True, filled=False, all_touched=False
            )
            v = array[0].filled(np.nan).astype("float32")
            v[~np.isfinite(v)] = np.nan
            valid = v[np.isfinite(v)]
            if valid.size == 0:
                raise ValueError("source raster has no valid Kerala cells")
            profile = src.profile.copy()
            profile.update(
                driver="GTiff", dtype="float32", count=1,
                height=v.shape[0], width=v.shape[1], transform=affine,
                nodata=np.nan, compress="deflate", predictor=3,
            )
            target = output / f"{label}_Kerala_NWIC.tif"
            with rasterio.open(target, "w", **profile) as dst:
                dst.write(v, 1)
            report["rasters"][label] = {
                "original": filename, "original_SHA256": sha256(path),
                "TIFF": target.name, "output_SHA256": sha256(target),
                "valid_cell_centres": int(valid.size),
                "source_native_resolution_degrees": list(src.res),
                "median": float(np.median(valid)),
            }
    with rasterio.open(output / "PVOUT_yearly_total_kWh_kWp_Kerala_NWIC.tif") as a, \
            rasterio.open(output / "PVOUT_daily_mean_kWh_kWp_Kerala_NWIC.tif") as b:
        x, y = a.read(1), b.read(1)
        if a.transform != b.transform or x.shape != y.shape:
            raise ValueError("GSA annual/daily grids differ")
        selected = np.isfinite(x) & np.isfinite(y) & (y > 0)
        ratio = x[selected] / y[selected]
        report["annual_over_daily_ratio"] = {
            "n": int(selected.sum()), "median": float(np.median(ratio)),
            "expected": 365.25, "max_abs_error": float(np.max(abs(ratio - 365.25))),
        }
    windpath = source_dir / "Wind.zip"
    if sha256(windpath) != NIWE_SHA:
        raise ValueError("Original Wind.zip SHA mismatch")
    with zipfile.ZipFile(windpath) as archive:
        inner = archive.read("Wind/150m_Map_Data_A_to_G.zip")
    if hashlib.sha256(inner).hexdigest() != INNER_SHA:
        raise ValueError("Original NIWE member SHA mismatch")
    rows, source_rows = [], 0
    with zipfile.ZipFile(io.BytesIO(inner)) as archive, archive.open(
        "150m_Map_Data_A_to_G.csv"
    ) as stream:
        for chunk in pd.read_csv(stream, chunksize=200_000):
            source_rows += len(chunk)
            lon = chunk["Longitude (E)"].to_numpy(dtype="float64")
            lat = chunk["Latitude (N)"].to_numpy(dtype="float64")
            in_box = (
                (lon >= geom.bounds[0]) & (lon <= geom.bounds[2]) &
                (lat >= geom.bounds[1]) & (lat <= geom.bounds[3])
            )
            if in_box.any():
                idx = np.flatnonzero(in_box)
                inside = contains_xy(geom, lon[idx], lat[idx])
                if inside.any():
                    rows.append(chunk.iloc[idx[inside]])
    if source_rows != 19_475_568:
        raise ValueError(f"NIWE source row count changed: {source_rows}")
    if not rows:
        raise ValueError("No NIWE points inside Kerala polygon")
    wind = pd.concat(rows, ignore_index=True)
    target = output / "NIWE_150m_Kerala_NWIC_point_centres.csv.gz"
    with gzip.open(target, "wt", compresslevel=7, newline="") as stream:
        wind.to_csv(stream, index=False, float_format="%.8g")
    report["NIWE"] = {
        "national_rows": source_rows, "Kerala_point_centres": len(wind),
        "output": target.name, "output_SHA256": sha256(target),
        "mean_wind_speed_m_s_median": float(wind["Wind Speed (m/s)"].median()),
        "NO_CUF_OR_BUILDABLE_MW_IN_SOURCE": True,
    }
    (output / "kerala_resource_clip_qa.json").write_text(
        json.dumps(report, indent=2, allow_nan=False) + "\n"
    )
    return report


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--sources", type=Path, required=True)
    p.add_argument("--nwic-artifact", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args()
    summary = process(args.sources, args.nwic_artifact, args.out)
    print(json.dumps(summary["NIWE"], indent=2))
