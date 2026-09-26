#!/usr/bin/env python
"""Run the Full-PyPSA Idukki stateful reservoir pilot v1.3."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from kerala2040.full_pypsa_idukki_reservoir_v1_3 import (
    run_idukki_reservoir_v13_suite,
)

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PROFILE = (
    ROOT
    / "results/models/full_pypsa/era5_renewables_v0_6/"
    "statewide_equal_weight_profile.parquet"
)
DEFAULT_OUTPUT = (
    ROOT
    / "results/models/full_pypsa/idukki_reservoir_v1_3/summary.json"
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--profile",
        type=Path,
        default=DEFAULT_PROFILE,
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
    )
    parser.add_argument(
        "--acknowledge-net-water-balance-not-catchment-inflow",
        action="store_true",
    )
    args = parser.parse_args()

    if not args.acknowledge_net_water_balance_not_catchment_inflow:
        raise SystemExit(
            "Refusing v1.3 run without explicit acknowledgement that the "
            "reconstructed water term is a net balance residual, not observed "
            "catchment inflow."
        )

    summary = run_idukki_reservoir_v13_suite(
        ROOT,
        profile_path=args.profile,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "classification": summary["classification"],
        "pilot_days": summary["pilot_days"],
        "cases_solved": summary["cases_solved"],
        "comparison_solves": summary["comparison_solves"],
        "source_qa": summary["source_qa"],
    }, indent=2))


if __name__ == "__main__":
    main()
