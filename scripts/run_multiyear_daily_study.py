"""Private local multi-year SLDC study; outputs aggregate metrics only."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import pandas as pd

from kerala2040.multiyear_daily_study import (
    evaluate_multiyear_daily_weather,
    read_private_daily_source,
)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--private-daily-gzip", type=Path, required=True)
    p.add_argument("--private-manifest", type=Path, required=True)
    p.add_argument("--weather-parquet", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    if args.output.exists():
        raise FileExistsError("Do not overwrite prior scientific outputs")
    observed, provenance = read_private_daily_source(
        args.private_daily_gzip, args.private_manifest
    )
    weather = pd.read_parquet(args.weather_parquet)
    report = evaluate_multiyear_daily_weather(observed, weather)
    report["daily_source_provenance"] = provenance
    # This pins the normalized table bytes, not the upstream CDS source archive.
    digest = hashlib.sha256()
    with args.weather_parquet.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    report["normalized_weather_parquet_sha256"] = digest.hexdigest()
    report["original_era5_source_archive_verified_by_this_runner"] = False
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")


if __name__ == "__main__":
    main()
