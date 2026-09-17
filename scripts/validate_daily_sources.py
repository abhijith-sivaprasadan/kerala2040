#!/usr/bin/env python
"""Cross-check overlapping Kerala daily electricity datasets."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from kerala2040.validation import compare_daily_energy, monthly_energy_balance


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sldc", type=Path, default=Path("data/processed/sldc_daily.parquet"))
    parser.add_argument(
        "--grid-india", type=Path, default=Path("data/processed/grid_india_psp.parquet")
    )
    parser.add_argument("--output-dir", type=Path, default=Path("results/validation"))
    args = parser.parse_args()

    sldc = pd.read_parquet(args.sldc)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    monthly = monthly_energy_balance(sldc)
    monthly.to_parquet(args.output_dir / "sldc_monthly_balance.parquet", index=False)
    monthly.to_csv(args.output_dir / "sldc_monthly_balance.csv", index=False)

    if not args.grid_india.exists():
        summary = {
            "grid_india_comparison": "not_run",
            "reason": f"{args.grid_india} does not exist",
        }
        (args.output_dir / "cross_source_summary.json").write_text(
            json.dumps(summary, indent=2), encoding="utf-8"
        )
        print(json.dumps(summary, indent=2))
        return 0

    grid_india = pd.read_parquet(args.grid_india)
    comparison, summary = compare_daily_energy(sldc, grid_india)
    comparison.to_parquet(args.output_dir / "sldc_vs_grid_india_daily.parquet", index=False)
    comparison.to_csv(args.output_dir / "sldc_vs_grid_india_daily.csv", index=False)
    (args.output_dir / "cross_source_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8"
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
