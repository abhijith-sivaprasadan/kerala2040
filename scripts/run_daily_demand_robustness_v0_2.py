"""Run Kerala2040 daily demand ML robustness v0.2."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from kerala2040.daily_demand_ml import load_observed_daily_consumption
from kerala2040.daily_demand_robustness import run_rolling_robustness

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--weather",
        type=Path,
        required=True,
        help="Verified ERA5 hourly weather_points.parquet from the v0.6 source pipeline.",
    )
    parser.add_argument(
        "--target",
        type=Path,
        default=ROOT / "public" / "daily-balance.json",
        help="Published observed daily balance JSON.",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=ROOT / "results" / "ml" / "daily_demand_robustness_v0_2",
    )
    parser.add_argument("--trials", type=int, default=10)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--first-holdout", default="2024-09-01")
    parser.add_argument("--last-holdout", default="2025-03-01")
    args = parser.parse_args()

    observed = load_observed_daily_consumption(args.target)
    weather = pd.read_parquet(args.weather)
    summary = run_rolling_robustness(
        observed,
        weather,
        trials=args.trials,
        seed=args.seed,
        first_holdout=args.first_holdout,
        last_holdout=args.last_holdout,
        out_dir=args.out_dir,
    )
    print(json.dumps(summary, indent=2, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
