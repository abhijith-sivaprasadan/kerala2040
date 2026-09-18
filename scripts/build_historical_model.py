"""Build the observed-day FY2024-25 Kerala PyPSA replay network."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd
import yaml

from kerala2040.historical_model import build_daily_observed_replay, replay_energy_summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--daily", type=Path, default=Path("data/processed/sldc_daily.parquet"))
    parser.add_argument(
        "--observed", type=Path, default=Path("configs/observed_2024_25.yaml")
    )
    parser.add_argument(
        "--network-output",
        type=Path,
        default=Path("results/models/kerala_fy2024_25_daily_replay.nc"),
    )
    parser.add_argument(
        "--summary-output",
        type=Path,
        default=Path("results/models/kerala_fy2024_25_daily_replay_summary.json"),
    )
    args = parser.parse_args()

    daily = pd.read_parquet(args.daily)
    observed = yaml.safe_load(args.observed.read_text(encoding="utf-8"))
    network = build_daily_observed_replay(daily, observed)
    summary = replay_energy_summary(network)
    summary["network_meta"] = network.meta

    args.network_output.parent.mkdir(parents=True, exist_ok=True)
    network.export_to_netcdf(args.network_output)
    args.summary_output.parent.mkdir(parents=True, exist_ok=True)
    args.summary_output.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
