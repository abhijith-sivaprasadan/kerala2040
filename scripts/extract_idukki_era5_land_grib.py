#!/usr/bin/env python3
"""Offline original GRIB -> private ERA5-Land hourly pixel CSV and source grid.

This extracts original ERA5-Land forecast accumulations (tp, metres) WITHOUT
turning them into rainfall yet. Phase 5's separate hourly processor validates
deaccumulation, local IST dates, complete days and grid weights.

Install in user's authenticated/local environment: pip install cfgrib eccodes
The tp and t2m monthly files can be the SAME GRIB if the CDS request contains
both variables; otherwise supply corresponding separate monthly paths.
Example:
 python scripts/extract_idukki_era5_land_grib.py \
 --tp-grib PRIVATE/2018_01.grib PRIVATE/2018_02.grib \
 --t2m-grib PRIVATE/2018_01.grib PRIVATE/2018_02.grib \
 --out PRIVATE/era5_hourly.csv --grid-out PRIVATE/era5_grid.csv

Use --weights-csv after externally reviewing geometry to output selected
pixels only. Never upload output CSV or source GRIB without a reuse decision.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import pandas as pd


def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024*1024), b""):
            h.update(block)
    return h.hexdigest()


def open_variable(path: Path, short_name: str, expected_unit: str) -> pd.DataFrame:
    try:
        import xarray as xr
        import cfgrib  # noqa: F401
    except ImportError as exc:
        raise RuntimeError("Install cfgrib + eccodes in local environment") from exc
    with xr.open_dataset(path, engine="cfgrib", backend_kwargs={
        "filter_by_keys": {"shortName": short_name}, "indexpath": ""
    }) as dataset:
        if len(dataset.data_vars) != 1:
            raise ValueError(f"{path}: expected exactly one {short_name} variable")
        variable = next(iter(dataset.data_vars))
        data = dataset[variable]
        if str(data.attrs.get("units", "")) != expected_unit:
            raise ValueError(f"{path}: expected {short_name} in {expected_unit}")
        if short_name == "tp" and data.attrs.get("GRIB_stepType") != "accum":
            raise ValueError(f"{path}: tp must be ORIGINAL accumulated forecast data")
        frame = data.to_dataframe(name="value").reset_index()
        needed = {"valid_time", "latitude", "longitude", "value"}
        if not needed.issubset(frame):
            raise ValueError(f"{path}: original latitude/longitude/valid_time unavailable")
        frame = frame[["valid_time", "latitude", "longitude", "value"]]
        frame["valid_time_utc"] = pd.to_datetime(frame.valid_time, utc=True).dt.strftime(
            "%Y-%m-%dT%H:%M:%SZ")
        frame = frame[["valid_time_utc", "latitude", "longitude", "value"]]
        if frame.duplicated(["valid_time_utc", "latitude", "longitude"]).any():
            raise ValueError(f"{path}: multiple source records for same validity/pixel")
        if frame.empty:
            raise ValueError(f"{path}: no original {short_name} records")
        return frame


def extract(tp_files: list[Path], temp_files: list[Path], out: Path,
            grid_out: Path, weights_file: Path | None) -> dict:
    if not tp_files or len(tp_files) != len(temp_files):
        raise ValueError("Supply 1:1 original tp and t2m GRIB paths in month order")
    out.parent.mkdir(parents=True, exist_ok=True)
    grid_out.parent.mkdir(parents=True, exist_ok=True)
    select = None
    if weights_file:
        select = pd.read_csv(weights_file)[["latitude", "longitude"]].drop_duplicates()
        if select.empty:
            raise ValueError("Selected geometry has no pixels")
    seen_times: set[str] = set()
    grid_keys = None
    records = []
    for i, (tp_path, temp_path) in enumerate(zip(tp_files, temp_files)):
        rain = open_variable(tp_path, "tp", "m").rename(columns={"value": "tp_accum_m"})
        temp = open_variable(temp_path, "2t", "K").rename(columns={"value": "t2m_k"})
        joined = rain.merge(temp, on=["valid_time_utc", "latitude", "longitude"],
                            how="outer", indicator=True, validate="one_to_one")
        if not joined._merge.eq("both").all():
            raise ValueError("tp/t2m GRIB pixel-hour coverage differs")
        joined = joined.drop(columns="_merge")
        grid = joined[["latitude", "longitude"]].drop_duplicates().sort_values(
            ["latitude", "longitude"]).reset_index(drop=True)
        keys = set(map(tuple, grid.itertuples(index=False, name=None)))
        if grid_keys is not None and keys != grid_keys:
            raise ValueError("ERA5 grid changed across months; do not silently regrid")
        grid_keys = keys
        if i == 0:
            grid.to_csv(grid_out, index=False)
        if select is not None:
            joined = joined.merge(select, on=["latitude", "longitude"],
                                  how="inner", validate="many_to_one")
            if joined.empty:
                raise ValueError("No selected pixels in this source GRIB")
            if len(joined[["latitude", "longitude"]].drop_duplicates()]) != len(select):
                raise ValueError("GRIB omits at least one reviewed catchment pixel")
        times = set(joined.valid_time_utc.unique())
        if times & seen_times:
            raise ValueError("Overlapping original GRIB validity dates between files")
        seen_times.update(times)
        joined[["valid_time_utc", "latitude", "longitude",
                "tp_accum_m", "t2m_k"]].to_csv(
                    out, mode="w" if i == 0 else "a", header=i == 0, index=False)
        records.append({"tp_grib": str(tp_path), "tp_sha256": sha(tp_path),
                        "t2m_grib": str(temp_path), "t2m_sha256": sha(temp_path),
                        "validity_hours": len(times), "pixel_hours_written": len(joined)})
    manifest = {"classification": "SOURCE_GRIB_EXTRACT_NOT_IST_DAILY_WEATHER",
                "hourly_csv": str(out), "hourly_csv_sha256": sha(out),
                "grid_csv": str(grid_out), "grid_sha256": sha(grid_out),
                "selected_weights_sha256": sha(weights_file) if weights_file else None,
                "originals": records}
    out.with_suffix(".source_manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--tp-grib", nargs="+", type=Path, required=True)
    p.add_argument("--t2m-grib", nargs="+", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--grid-out", type=Path, required=True)
    p.add_argument("--weights-csv", type=Path)
    a = p.parse_args()
    result = extract(a.tp_grib, a.t2m_grib, a.out, a.grid_out, a.weights_csv)
    print(json.dumps({"months_extracted": len(result["originals"]),
                      "status": result["classification"],
                      "hourly_csv": result["hourly_csv"]}, indent=2))


if __name__ == "__main__":
    main()
