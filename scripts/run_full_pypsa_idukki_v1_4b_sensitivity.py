"""Run the private Full-PyPSA Idukki v1.4b 60-case sensitivity matrix."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from kerala2040.full_pypsa_idukki_v1_4b_sensitivity import (
    run_v14b_sensitivity_suite,
)

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PROFILE = (
    ROOT
    / "results/models/full_pypsa/era5_renewables_v0_6/"
    "statewide_equal_weight_profile.parquet"
)
DEFAULT_OUTPUT = (
    ROOT
    / "results/models/full_pypsa/idukki_v1_4b_sensitivity/"
    "summary.json"
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--private-reservoir-rows", type=Path, required=True)
    parser.add_argument("--private-work-dir", type=Path, required=True)
    parser.add_argument("--profile", type=Path, default=DEFAULT_PROFILE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--acknowledge-source-informed-not-observed",
        action="store_true",
        required=True,
    )
    args = parser.parse_args()

    summary = run_v14b_sensitivity_suite(
        ROOT,
        private_reservoir_rows=args.private_reservoir_rows,
        private_work_dir=args.private_work_dir,
        profile_path=args.profile,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(summary, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    print("classification:", summary["classification"])
    print("cases_solved:", summary["cases_solved"])
    for row in summary["sensitivity_summary"]:
        print(
            row["demand_case"],
            row["transfer_case"],
            row["idukki_availability_case"],
            "unserved_range_MWh=",
            round(row["unserved_mwh_range"], 6),
            "release_range_MCM=",
            round(row["idukki_non_turbine_release_mcm_range"], 6),
        )


if __name__ == "__main__":
    main()
