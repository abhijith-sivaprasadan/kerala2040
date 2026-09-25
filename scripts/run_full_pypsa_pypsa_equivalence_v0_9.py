"""Run direct PyPSA equivalence against proxy expansion v0.8."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from kerala2040.full_pypsa_pypsa_equivalence import run_pypsa_equivalence_suite

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--profile",
        type=Path,
        default=ROOT
        / "results/models/full_pypsa/era5_renewables_v0_6/statewide_equal_weight_profile.parquet",
    )
    parser.add_argument("--hours", type=int, default=8760)
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "results/models/full_pypsa/pypsa_equivalence_v0_9/summary.json",
    )
    parser.add_argument(
        "--acknowledge-equivalence-only",
        action="store_true",
        help="Required: confirms v0.9 is formulation QA, not a validated capacity plan.",
    )
    args = parser.parse_args()
    if not args.acknowledge_equivalence_only:
        raise SystemExit("Refusing v0.9 without --acknowledge-equivalence-only")

    result = run_pypsa_equivalence_suite(
        ROOT,
        profile_path=args.profile,
        hours=args.hours,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "classification": result["classification"],
                "hours": result["hours"],
                "cases_compared": result["cases_compared"],
                "all_cases_passed": result["all_cases_passed"],
                "maximum_absolute_differences": result["maximum_absolute_differences"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
