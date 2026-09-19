"""Build provisional weather-derived solar and wind availability profiles."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from kerala2040.renewables import build_renewable_profiles


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--weather", type=Path, default=Path("data/processed/weather_points.parquet")
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/processed/renewable_availability_proxy.parquet"),
    )
    parser.add_argument(
        "--summary",
        type=Path,
        default=Path("results/resources/renewable_availability_summary.json"),
    )
    args = parser.parse_args()

    profiles, summary = build_renewable_profiles(pd.read_parquet(args.weather))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    profiles.to_parquet(args.output, index=False)
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
