#!/usr/bin/env python
"""Fetch hourly NASA POWER data for one configured point."""

from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path

from kerala2040.provenance import build_manifest, write_manifest
from kerala2040.sources.nasa_power import fetch_hourly_point


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", required=True, type=date.fromisoformat)
    parser.add_argument("--end", required=True, type=date.fromisoformat)
    parser.add_argument("--lat", required=True, type=float)
    parser.add_argument("--lon", required=True, type=float)
    parser.add_argument("--name", default="point")
    parser.add_argument("--output-dir", type=Path, default=Path("data/processed/weather"))
    args = parser.parse_args()

    frame, metadata = fetch_hourly_point(
        latitude=args.lat,
        longitude=args.lon,
        start=args.start,
        end=args.end,
    )
    args.output_dir.mkdir(parents=True, exist_ok=True)
    output = args.output_dir / f"nasa_power_{args.name}.parquet"
    frame.to_parquet(output, index=False)

    manifest = build_manifest(
        command="scripts/ingest_weather.py",
        parameters={
            "name": args.name,
            "start": args.start.isoformat(),
            "end": args.end.isoformat(),
            "lat": args.lat,
            "lon": args.lon,
        },
        sources=[metadata["provenance"]],
        outputs=[str(output)],
    )
    manifest["nasa_power_metadata"] = {
        key: value for key, value in metadata.items() if key != "provenance"
    }
    manifest_path = output.with_suffix(".manifest.json")
    write_manifest(manifest_path, manifest)
    print(f"wrote {len(frame)} rows -> {output}")
    print(f"manifest -> {manifest_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
