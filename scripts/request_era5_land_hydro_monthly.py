"""Kerala2040: explicit, resumable ERA5-Land monthly request manifest / opt-in CDS fetch.

Monthly source GRIB only; NO rainfall daily conversion, catchment clipping or
invented watershed polygons. A source-approved bbox is REQUIRED. With --execute
this uses the user's own local Copernicus CDS credentials and network.

Example dry run (INSERT VERIFIED WATERSHED BBOX):
 python scripts/request_era5_land_hydro_monthly.py --area NORTH WEST SOUTH EAST --out E:/ERA5Hydro
Add --execute only after checking request plan/credentials/bbox and accepting CDS
terms. The 2017-12-31 margin permits IST-day alignment from 2018-01-01.
"""
from __future__ import annotations

import argparse
import calendar
import hashlib
import json
from datetime import date
from pathlib import Path

DATASET = "reanalysis-era5-land"
VARIABLES = ("total_precipitation", "2m_temperature")
TIMES = [f"{i:02d}:00" for i in range(24)]


def months(first: date, last: date):
    if last < first:
        raise ValueError("End must be after start")
    year, month = first.year, first.month
    while (year, month) <= (last.year, last.month):
        low = first.day if (year, month) == (first.year, first.month) else 1
        high = last.day if (year, month) == (last.year, last.month) else calendar.monthrange(year, month)[1]
        yield year, month, list(range(low, high + 1))
        month += 1
        if month > 12:
            year, month = year + 1, 1


def validate_area(area):
    n, w, s, e = area
    if not (-90 <= s < n <= 90 and -180 <= w < e <= 180):
        raise ValueError("Area must be N W S E and have nonzero area")
    if n - s > 8 or e - w > 8:
        raise ValueError("Hydro pilot bbox exceeds 8 degrees: supply a verified smaller regional extent")
    return [float(x) for x in area]


def plan(area, first, last):
    bbox = validate_area(area)
    for y, m, days in months(first, last):
        req = {"variable": list(VARIABLES), "year": str(y), "month": f"{m:02d}",
               "day": [f"{x:02d}" for x in days], "time": TIMES, "area": bbox,
               "data_format": "grib", "download_format": "unarchived"}
        yield {"file": f"era5_land_hydro_{y}_{m:02d}.grib", "dataset": DATASET,
               "request": req, "timezone": "UTC", "spatial_status": "bbox_only_NOT_basin_mask"}


def magic(path: Path) -> str:
    with path.open("rb") as f:
        prefix = f.read(4)
    if prefix.startswith(b"GRIB"):
        return "grib"
    if prefix.startswith(b"PK"):
        return "zip_wrong_extension_requires_separate_inspection"
    return "unknown"


def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--area", nargs=4, type=float, required=True, metavar=("N", "W", "S", "E"))
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--start", type=date.fromisoformat, default=date(2017, 12, 31))
    parser.add_argument("--end", type=date.fromisoformat, default=date(2026, 9, 22))
    parser.add_argument("--execute", action="store_true", help="Make real CDS calls, never enabled by default")
    args = parser.parse_args()
    out = args.out
    out.mkdir(parents=True, exist_ok=True)
    jobs = list(plan(args.area, args.start, args.end))
    (out / "cds_request_plan.json").write_text(
        json.dumps({"status": "request_plan_NOT_observed_data", "jobs": jobs}, indent=2) + "\n",
        encoding="utf-8")
    if not args.execute:
        print(f"DRY_RUN: {len(jobs)} month requests; inspect {out / 'cds_request_plan.json'}")
        return
    try:
        import cdsapi
    except ImportError as exc:
        raise RuntimeError("Install cdsapi in your local authenticated environment") from exc
    client = cdsapi.Client()  # user-managed credentials, never embedded in code
    records = []
    try:
        for job in jobs:
            target = out / job["file"]
            if target.is_file() and magic(target) == "grib":
                state = "existing_grib_verified_magic"
            elif target.is_file():
                raise ValueError(f"File exists but cannot be verified GRIB: {target}")
            else:
                partial = target.with_suffix(".part")
                if partial.exists():
                    raise ValueError(f"Inspect unfinished download before resuming: {partial}")
                client.retrieve(job["dataset"], job["request"], str(partial))
                if magic(partial) != "grib":
                    raise ValueError(f"CDS returned non-GRIB payload; inspect {partial}")
                partial.rename(target)
                state = "downloaded_grib_magic_verified"
            records.append({"file": job["file"], "status": state, "sha256": sha(target),
                            "bytes": target.stat().st_size})
            (out / "cds_download_manifest.json").write_text(
                json.dumps({"dataset": DATASET, "records": records}, indent=2) + "\n",
                encoding="utf-8")
    finally:
        print(f"Months verified: {len(records)}/{len(jobs)}; originals in {out}")


if __name__ == "__main__":
    main()
