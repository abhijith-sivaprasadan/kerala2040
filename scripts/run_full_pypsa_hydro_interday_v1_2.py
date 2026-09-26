"""Run Full-PyPSA interday hydro-flexibility bracket v1.2."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from kerala2040.full_pypsa_hydro_interday_v1_2 import (
    run_hydro_interday_v12_suite,
)

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--profile",
        type=Path,
        default=(
            ROOT
            / "results/models/full_pypsa/era5_renewables_v0_6/"
            "statewide_equal_weight_profile.parquet"
        ),
    )
    parser.add_argument("--hours", type=int, default=8760)
    parser.add_argument(
        "--output",
        type=Path,
        default=(
            ROOT
            / "results/models/full_pypsa/hydro_interday_v1_2/summary.json"
        ),
    )
    parser.add_argument(
        "--acknowledge-interday-bracket-not-reservoir-model",
        action="store_true",
    )
    args = parser.parse_args()
    if not args.acknowledge_interday_bracket_not_reservoir_model:
        raise SystemExit(
            "Refusing v1.2 without "
            "--acknowledge-interday-bracket-not-reservoir-model"
        )

    result = run_hydro_interday_v12_suite(
        ROOT,
        profile_path=args.profile,
        hours=args.hours,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, indent=2) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "classification": result["classification"],
                "hours": result["hours"],
                "cases_solved": result["cases_solved"],
                "installed_hydro_mw": result["installed_hydro_mw"],
                "daily_hydro_energy_mwh": result[
                    "daily_hydro_energy_mwh"
                ],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
