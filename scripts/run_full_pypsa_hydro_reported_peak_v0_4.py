"""Run the v0.4 three-way hydro timing/capability research bracket."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from kerala2040.full_pypsa_hydro_reported_peak import run_reported_peak_envelope


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--acknowledge-proxy",
        action="store_true",
        help="Required: the station-max envelope is not simultaneous capability.",
    )
    parser.add_argument("--hours", type=int, default=8760)
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(
            "results/models/full_pypsa/hydro_reported_peak_v0_4/summary.json"
        ),
    )
    args = parser.parse_args()
    if not args.acknowledge_proxy:
        parser.error(
            "Pass --acknowledge-proxy; this is a research hydro envelope"
        )

    result = run_reported_peak_envelope(args.root, hours=args.hours)
    output = args.root / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(result, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )

    flat = {case["id"]: case for case in result["flat_daily_average"]}
    middle = {
        case["id"]: case for case in result["reported_station_peak_envelope"]
    }
    upper = {
        case["id"]: case
        for case in result["installed_capacity_redispatch_upper_bound"]
    }
    compact = []
    for case_id in flat:
        compact.append(
            {
                "id": case_id,
                "limit_mw": flat[case_id]["import_limit_mw"],
                "flat_unserved_mwh": flat[case_id]["unserved_energy_mwh"],
                "reported_peak_unserved_mwh": middle[case_id][
                    "unserved_energy_mwh"
                ],
                "installed_upper_unserved_mwh": upper[case_id][
                    "unserved_energy_mwh"
                ],
                "reported_peak_hours_unserved": middle[case_id][
                    "hours_with_unserved"
                ],
                "reported_peak_hydro_peak_mw": middle[case_id][
                    "hydro_peak_mw_modelled"
                ],
            }
        )
    print(
        json.dumps(
            {
                "classification": result["classification"],
                "hours": result["hours"],
                "station_envelope_summary": result["station_envelope_summary"],
                "cases": compact,
                "output": str(output),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
