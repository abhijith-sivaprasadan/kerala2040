"""Build descriptive onshore Kerala NIWE/GSA resource clips from exact originals.

Example:
  python scripts/build_kerala_renewable_resource_clips.py \
      --sources "E:/Kerala2040/Solar" --wind "E:/Kerala2040/Wind.zip" \
      --boundary-artifact "E:/Kerala2040/nwic_boundary_2026_09_20.zip" \
      --output results/gis/kerala_renewables

Use original NWIC Actions artifact from run 35517474497; original source
checksum is pinned. This script does not publish raw files or certify siting.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import tempfile
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

BOUNDARY_SHA = "a932ea29e7afd0fea1e1068f3beeeadb760e6b2baae9783f5822bbefd4224ebd"
NIWE_ZIP_SHA = "f166450c3ea591b5b346f9cd27899b10b6f18ce9cf441c98388c6f0e98d44b38"
ROOT = Path(__file__).resolve().parents[1]
SOURCE_MANIFEST = ROOT / "data/evidence/solar/solar_batch_2026_09_21_originals_manifest.json"
RASTERS = {
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
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(4 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def original_boundary(artifact: Path):
    with zipfile.ZipFile(artifact) as wrapper:
        raw = wrapper.read("nwic_original/nwic_original_state_boundary_download")
    if hashlib.sha256(raw).hexdigest() != BOUNDARY_SHA:
        raise ValueError("NWIC official original boundary hash mismatch")
    with zipfile.ZipFile(io.BytesIO(raw)) as original:
        collection = json.loads(original.read("state_NWIC.GeoJSON"))
    if "7755" not in json.dumps(collection.get("crs")):
        raise ValueError("NWIC projected EPSG:7755 source CRS missing")
    matches = [
        item for item in collection["features"]
        if item.get("properties", {}).get("state_name") == "Kerala"
    ]
    if len(matches) != 1:
        raise ValueError("Expected one original Kerala feature")
    geometry = transform(
        Transformer.from_crs(7755, 4326, always_xy=True).transform,
        shape(matches[0]["geometry"]),
    )
    if not geometry.is_valid or not (74 < geometry.bounds[0] < 76):
        raise ValueError("Kerala geometry failed basic source QA")
    return geometry


def clipped_raster(
    archive: Path, member_basename: str, boundary, destination: Path,
) -> dict:
    with zipfile.ZipFile(archive) as z:
        matches = [
            name for name in z.namelist()
            if Path(name).name == member_basename
        ]
    if len(matches) != 1:
        raise ValueError(f"Expected one {member_basename} in {archive.name}")
    vsi = "/vsizip/" + archive.resolve().as_posix() + "/" + matches[0]
    with rasterio.open(vsi) as source:
        if source.crs.to_epsg() != 4326:
            raise ValueError("Original GSA raster CRS changed")
        cropped, grid = mask(
            source, [mapping(boundary)], crop=True, filled=False,
            all_touched=False,
        )
        data = cropped[0].filled(np.nan).astype("float32")
        profile = source.profile.copy()
    finite = data[np.isfinite(data)]
    if not finite.size:
        raise ValueError("Original raster has no valid Kerala cells")
    profile.update(
        driver="GTiff", width=data.shape[1], height=data.shape[0],
        transform=grid, crs="EPSG:4326", count=1, dtype="float32",
        nodata=np.nan, compress="deflate", predictor=3, tiled=True,
        blockxsize=256, blockysize=256,
    )
    with rasterio.open(destination, "w", **profile) as output:
        output.write(data, 1)
    return {
        "source_zip": archive.name, "original_member": matches[0],
        "native_resolution_degrees": list(source.res),
        "valid_pixel_centres": int(finite.size), "median": float(np.median(finite)),
        "sha256": sha256(destination),
    }


def niwe_original_bytes(wind: Path) -> bytes:
    with zipfile.ZipFile(wind) as z:
        if "150m_Map_Data_A_to_G.csv" in z.namelist():
            original = wind.read_bytes()
        else:
            original = z.read("Wind/150m_Map_Data_A_to_G.zip")
    if hashlib.sha256(original).hexdigest() != NIWE_ZIP_SHA:
        raise ValueError("Original NIWE 150m ZIP SHA256 mismatch")
    return original


def niwe_clip(wind: Path, boundary, output: Path) -> dict:
    west, south, east, north = boundary.bounds
    prepare(boundary)
    points: list[np.ndarray] = []
    buffer: list[list[float]] = []
    examined = 0
    bounding_candidates = 0
    last_lon = -float("inf")

    def flush() -> None:
        if buffer:
            xy = np.asarray(buffer, dtype="float64")
            inside = contains_xy(boundary, xy[:, 0], xy[:, 1])
            points.extend(xy[inside])
            buffer.clear()

    with tempfile.TemporaryDirectory() as tmp:
        original = Path(tmp) / "original.zip"
        original.write_bytes(niwe_original_bytes(wind))
        with zipfile.ZipFile(original) as z:
            with z.open("150m_Map_Data_A_to_G.csv") as rows:
                columns = rows.readline().decode().strip().split(",")
                for line in rows:
                    examined += 1
                    parts = line.split(b",", 2)
                    lon = float(parts[0])
                    if lon < last_lon:
                        raise ValueError("NIWE longitude sequence not sorted")
                    last_lon = lon
                    if lon > east:
                        break  # Verified sorted prefix covers the state longitude.
                    if west <= lon <= east:
                        lat = float(parts[1])
                        if south <= lat <= north:
                            bounding_candidates += 1
                            buffer.append([float(part) for part in line.strip().split(b",")])
                            if len(buffer) == 50_000:
                                flush()
                flush()

    clipped = pd.DataFrame(np.asarray(points), columns=columns)
    if len(clipped) < 1000 or len(columns) != 7:
        raise ValueError("No credible original NIWE Kerala point coverage")
    clipped.to_csv(
        output, index=False,
        compression={"method": "gzip", "compresslevel": 4},
        float_format="%.7g",
    )
    return {
        "source_original_zip_sha256": NIWE_ZIP_SHA,
        "monotone_prefix_rows_examined": examined,
        "bounding_candidates": bounding_candidates,
        "inside_Kerala_source_point_centres": len(clipped),
        "wind_m_s_median": float(clipped.iloc[:, 2].median()),
        "wind_m_s_p95": float(clipped.iloc[:, 2].quantile(.95)),
        "sha256": sha256(output),
        "public_redistribution_permission_verified": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sources", type=Path, required=True)
    parser.add_argument("--wind", type=Path, required=True)
    parser.add_argument("--boundary-artifact", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path("results/gis/kerala_renewables"))
    args = parser.parse_args()
    manifest = json.loads(SOURCE_MANIFEST.read_text(encoding="utf-8"))
    originals = {item["name"]: item for item in manifest["assets"]}
    boundary = original_boundary(args.boundary_artifact)
    args.output.mkdir(parents=True, exist_ok=True)
    report = {
        "classification": "verified_native_source_Kerala_onshore_descriptive_only",
        "boundary_original_sha256": BOUNDARY_SHA,
        "raster_pixel_rule": "pixel centre in NWIC polygon",
        "wind_point_rule": "point centre in NWIC polygon",
        "raster_outputs": {},
        "model_ready": False,
        "capacity_mw": None,
        "offshore_assessed": False,
    }
    for label, (archive_name, member) in RASTERS.items():
        archive = args.sources / archive_name
        if sha256(archive) != originals[archive_name]["sha256"]:
            raise ValueError(f"Original GSA ZIP hash changed: {archive.name}")
        target = args.output / f"{label}_Kerala_NWIC.tif"
        report["raster_outputs"][label] = clipped_raster(
            archive, member, boundary, target,
        )
        print(f"VERIFIED raster: {label}", flush=True)
    yearly = args.output / "PVOUT_yearly_total_kWh_kWp_Kerala_NWIC.tif"
    daily = args.output / "PVOUT_daily_mean_kWh_kWp_Kerala_NWIC.tif"
    with rasterio.open(yearly) as x, rasterio.open(daily) as y:
        if x.transform != y.transform or x.shape != y.shape:
            raise ValueError("PVOUT source grids differ")
        a, b = x.read(1), y.read(1)
    valid = np.isfinite(a) & np.isfinite(b) & (b > 0)
    error = abs(a[valid] / b[valid] - 365.25)
    if not valid.any() or error.max() > .02:
        raise ValueError("FY/average-day PVOUT source unit reconciliation failed")
    report["annual_over_daily_QA"] = {
        "matched_cells": int(valid.sum()),
        "expected_ratio": 365.25,
        "maximum_absolute_error": float(error.max()),
    }
    report["niwe"] = niwe_clip(
        args.wind, boundary,
        args.output / "NIWE_150m_Kerala_NWIC_point_centres.csv.gz",
    )
    (args.output / "source_qa.json").write_text(
        json.dumps(report, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "kerala_wind_points": report["niwe"]["inside_Kerala_source_point_centres"],
        "pvout_raster_centres": report["annual_over_daily_QA"]["matched_cells"],
        "output": str(args.output),
        "classification": report["classification"],
    }, indent=2))


if __name__ == "__main__":
    main()
