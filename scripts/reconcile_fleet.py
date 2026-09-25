"""Validate and export the partial-exact March-2026 Kerala fleet."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from kerala2040.fleet_reconciliation import load_fleet, summarize_fleet


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("results/models/full_pypsa/fleet_reconciliation_2026_03_31.json"),
    )
    args = parser.parse_args()
    fleet = load_fleet(
        args.root / "data/evidence/assets/kerala_fleet_reconciliation_2026_03_31.json"
    )
    summary = summarize_fleet(fleet)
    payload = {
        "classification": fleet["classification"],
        "summary": summary.to_dict(),
        "release": fleet["release"],
        "next_blockers": fleet["next_blockers"],
    }
    out = args.root / args.output
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(
        "FLEET",
        summary.base_date,
        summary.physical_capacity_mw,
        "MW exact aggregate;",
        "hydro residual",
        summary.hydro_residual_mw,
        "MW; wind residual",
        summary.wind_residual_mw,
        "MW; ground-solar residual",
        summary.ground_solar_residual_mw,
        "MW; dispatch_ready=",
        summary.dispatch_ready,
    )


if __name__ == "__main__":
    main()
