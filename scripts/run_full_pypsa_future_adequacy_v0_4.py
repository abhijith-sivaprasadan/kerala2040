"""Run the Full-PyPSA v0.4 future-demand adequacy counterfactual."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from kerala2040.full_pypsa_future_adequacy import run_future_adequacy_suite


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--acknowledge-counterfactual",
        action="store_true",
        help=(
            "Required: future hours are morphed proxy chronology with frozen "
            "generation."
        ),
    )
    parser.add_argument("--hours", type=int, default=8760)
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("results/models/full_pypsa/future_adequacy_v0_4/summary.json"),
    )
    args = parser.parse_args()
    if not args.acknowledge_counterfactual:
        parser.error(
            "Pass --acknowledge-counterfactual; this is NOT a future hourly forecast"
        )

    result = run_future_adequacy_suite(args.root, hours=args.hours)
    output = args.root / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(result, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "classification": result["classification"],
                "hours": result["hours"],
                "cases": [
                    {
                        "demand_case": case["demand_case"],
                        "transfer_case": case["transfer_case"],
                        "unserved_energy_mwh": case["unserved_energy_mwh"],
                        "hours_with_unserved": case["hours_with_unserved"],
                    }
                    for case in result["cases"]
                ],
                "output": str(output),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
