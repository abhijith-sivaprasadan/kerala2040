#!/usr/bin/env python
"""Fetch full-period NASA POWER weather for configured Kerala sample points."""

from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path

import pandas as pd

from kerala2040.config import load_yaml
from kerala2040.sources.nasa_power import fetch_hourly_point


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", required=True, type=date.fromisoformat)
    parser.add_argument("--end", required=True, type=date.fromisoformat)
    parser.add_argument("--config", type=Path, default=Path("configs/sources.yaml"))
    parser.add_argument("--output", type=Path, default=Path("data/processed/weather_points.parquet"))
    args = parser.parse_args()

    config = load_yaml(args.config)
    points = config["sources"]["nasa_power"]["representative_points"]
    frames = []
    failures = []
    for name, coordinates in points.items():
        try:
            frame, metadata = fetch_hourly_point(
                latitude=float(coordinates["lat"]),
                longitude=float(coordinates["lon"]),
                start=args.start,
                end=args.end,
            )
            frame["point"] = name
            frame["latitude"] = float(coordinates["lat"])
            frame["longitude"] = float(coordinates["lon"])
            frame["source_sha256"] = metadata["provenance"]["sha256"]
            frames.append(frame)
        except Exception as exc:  # noqa: BLE001 - keep successful weather points
            failures.append({"point": name, "error": str(exc)})

    combined = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    combined.to_parquet(args.output, index=False)
    args.output.with_suffix(".failures.json").write_text(
        json.dumps(failures, indent=2), encoding="utf-8"
    )
    print(f"weather rows: {len(combined)}; point failures: {len(failures)}")
    return 0 if frames else 2


if __name__ == "__main__":
    raise SystemExit(main())
