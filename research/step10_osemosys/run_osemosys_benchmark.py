#!/usr/bin/env python3
"""Run Kerala2040 Step 10 independent TZ-OSeMOSYS capacity benchmark."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from kerala2040.osemosys_capacity_benchmark import (
    BenchmarkCase,
    run_benchmark,
)

ROOT = Path(__file__).resolve().parents[2]


def _parse_case(text: str) -> BenchmarkCase:
    parts = [part.strip() for part in text.split(",")]
    if len(parts) != 4 or any(not part for part in parts):
        raise argparse.ArgumentTypeError(
            "--case must be DEMAND,TRANSFER,ENVELOPE,BESS_COST"
        )
    return BenchmarkCase(*parts)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--profile",
        type=Path,
        default=ROOT
        / "results/models/full_pypsa/era5_renewables_v0_6/statewide_equal_weight_profile.parquet",
    )
    parser.add_argument("--hours", type=int, default=168)
    parser.add_argument(
        "--case",
        type=_parse_case,
        action="append",
        default=[],
        help="DEMAND,TRANSFER,ENVELOPE,BESS_COST; may be repeated",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=ROOT / "configs/osemosys_capacity_benchmark_v0_1.yaml",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "results/models/osemosys_step10/benchmark.json",
    )
    args = parser.parse_args()
    cases = args.case or [
        BenchmarkCase("reference_FY2030_31", "atc_snapshot_reference", "high", "low")
    ]
    report = run_benchmark(
        ROOT,
        profile_path=args.profile,
        cases=cases,
        hours=args.hours,
        suite_path=args.config,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if not report["all_cases_pass_numeric_equivalence"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
