"""Run the common PyPSA versus OSeMOSYS v1.3-frontier comparison."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from kerala2040.pypsa_osemosys_common_frontier import run_common_frontier

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PROFILE = (
    ROOT
    / "results/models/full_pypsa/era5_renewables_v0_6/"
    "statewide_equal_weight_profile.parquet"
)
DEFAULT_CONFIG = ROOT / "configs/pypsa_osemosys_common_frontier_v1_3c.yaml"
DEFAULT_OUTPUT = (
    ROOT
    / "results/models/cross_framework/common_frontier_v1_3c/summary.json"
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", type=Path, default=DEFAULT_PROFILE)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--demand-case")
    parser.add_argument("--transfer-case")
    parser.add_argument("--idukki-availability-case")
    parser.add_argument(
        "--acknowledge-net-water-balance-not-catchment-inflow",
        action="store_true",
    )
    args = parser.parse_args()

    if not args.acknowledge_net_water_balance_not_catchment_inflow:
        raise SystemExit(
            "Refusing the common-frontier run without acknowledging that the "
            "v1.3 reconstructed water term is not observed catchment inflow."
        )

    selectors = (
        args.demand_case,
        args.transfer_case,
        args.idukki_availability_case,
    )
    if any(value is not None for value in selectors) and not all(
        value is not None for value in selectors
    ):
        raise SystemExit(
            "Provide all of --demand-case, --transfer-case and "
            "--idukki-availability-case, or none of them."
        )
    only_case = selectors if all(value is not None for value in selectors) else None

    result = run_common_frontier(
        ROOT,
        profile_path=args.profile,
        suite_path=args.config,
        only_case=only_case,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "classification": result["classification"],
                "cases_compared": result["cases_compared"],
                "all_cases_pass": result["all_cases_pass"],
                "maximum_absolute_differences": result[
                    "maximum_absolute_differences"
                ],
            },
            indent=2,
        )
    )
    if not result["all_cases_pass"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
