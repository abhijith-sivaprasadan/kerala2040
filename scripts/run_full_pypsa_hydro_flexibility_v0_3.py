"""Run v0.3 flat-vs-flexible intraday hydro adequacy bracket."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from kerala2040.full_pypsa_hydro_flexibility import run_hydro_flexibility_bracket


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--acknowledge-proxy",
        action="store_true",
        help="Required: reconstructed load and optimistic hydro redispatch are not telemetry.",
    )
    parser.add_argument("--hours", type=int, default=8760)
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(
            "results/models/full_pypsa/hydro_flexibility_v0_3/summary.json"
        ),
    )
    args = parser.parse_args()
    if not args.acknowledge_proxy:
        parser.error(
            "Pass --acknowledge-proxy; this is a research flexibility bracket"
        )
    result = run_hydro_flexibility_bracket(args.root, hours=args.hours)
    output = args.root / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(result, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    compact = []
    flat = {case["id"]: case for case in result["flat_daily_average"]}
    for case in result["daily_energy_redispatch_upper_bound"]:
        compact.append(
            {
                "id": case["id"],
                "limit_mw": case["import_limit_mw"],
                "flat_unserved_mwh": flat[case["id"]]["unserved_energy_mwh"],
                "redispatch_unserved_mwh": case["unserved_energy_mwh"],
                "redispatch_hours_unserved": case["hours_with_unserved"],
                "redispatch_max_gap_mw": case["max_unserved_mw"],
                "hydro_peak_mw": case["hydro_peak_mw_modelled"],
            }
        )
    print(
        json.dumps(
            {
                "classification": result["classification"],
                "hours": result["hours"],
                "cases": compact,
                "output": str(output),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
