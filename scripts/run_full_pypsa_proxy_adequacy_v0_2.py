"""Run the full-PyPSA v0.2 deterministic proxy adequacy suite."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from kerala2040.full_pypsa_proxy_adequacy import run_proxy_adequacy_suite


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--acknowledge-proxy",
        action="store_true",
        help="Required: the 8760-hour load shape is reconstructed, not measured telemetry.",
    )
    parser.add_argument(
        "--hours",
        type=int,
        default=8760,
        help="Whole-day chronological window; default is the full 8760-hour FY2024-25 screen.",
    )
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("results/models/full_pypsa/proxy_adequacy_v0_2/summary.json"),
    )
    args = parser.parse_args()
    if not args.acknowledge_proxy:
        parser.error("Pass --acknowledge-proxy; this chronology is NOT measured hourly telemetry")

    result = run_proxy_adequacy_suite(args.root, hours=args.hours)
    output = args.root / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "classification": result["classification"],
                "hours": result["hours"],
                "full_financial_year": result["full_financial_year"],
                "cases": [
                    {
                        "id": case["id"],
                        "import_limit_mw": case["import_limit_mw"],
                        "unserved_energy_mwh": case["unserved_energy_mwh"],
                        "deterministic_nens_pct": case["deterministic_nens_pct"],
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
