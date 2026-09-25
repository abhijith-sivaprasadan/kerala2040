#!/usr/bin/env python3
"""Validate and export the canonical Kerala2040 March-2026 base system."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from kerala2040.base_system import load_base_system, summarize_base_system


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("results/models/full_pypsa/base_system_2026_03_31.json"),
    )
    args = parser.parse_args()
    cfg = load_base_system(args.root / "configs/base_system_2026_03_31.yaml")
    summary = summarize_base_system(cfg)
    payload = {
        "classification": "reconciled_structural_base_not_dispatch_ready",
        "summary": summary.to_dict(),
        "base_release": cfg["base_release"],
        "blocking_inputs": cfg["blocking_inputs"],
        "distributed_solar_boundary": cfg["distributed_solar_boundary"],
        "later_august_2026_renewable_overlay": cfg["later_august_2026_renewable_overlay"],
    }
    out = args.root / args.output
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(
        "BASE",
        summary.base_date,
        "main",
        summary.cea_main_capacity_mw,
        "MW + sub1MW solar",
        summary.solar_lt_1mw_mw,
        "MW =",
        summary.physical_arithmetic_capacity_mw,
        "MW;",
        summary.blocker_count,
        "blockers; dispatch_ready=",
        summary.dispatch_ready,
    )


if __name__ == "__main__":
    main()
