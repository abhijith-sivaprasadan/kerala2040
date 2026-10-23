"""Run the source-anchored, explicitly hypothetical supply/chronology study."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from kerala2040.hydro_chronology_v0_2 import run

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path,
                        default=ROOT / "results/examples/hydro_supply_timing_v0_2.json")
    args = parser.parse_args()
    result = run(ROOT)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Completed {len(result['cases'])} scientifically bounded test cases")
    print("Historical reconstructed load, not measured-hour or future adequacy validation.")
    for record in result["cases"]:
        if record["demand_shape"] in ("baseline", "shift_earlier_2h", "shift_later_2h"):
            print(
                "CASE "
                f"cap={record['import_ceiling_mw']:.0f}MW "
                f"supply={record['hypothetical_import_hourly_schedule']} "
                f"demand={record['demand_shape']} "
                f"ramp={record['hydro_ramp_cap_mw_per_h']} "
                f"fixed={record['fixed_hydro_unserved_mwh']:.4f}MWh "
                f"flex={record['optimised_hydro_unserved_mwh']:.4f}MWh"
            )


if __name__ == "__main__":
    main()
