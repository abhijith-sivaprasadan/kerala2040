#!/usr/bin/env python3
"""Build and summarize the non-optimising March-2026 full-PyPSA skeleton."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from kerala2040.full_pypsa_skeleton import (
    build_full_pypsa_skeleton,
    load_selection,
    skeleton_summary,
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("results/models/full_pypsa/network_skeleton_2026_03_31.json"),
    )
    args = parser.parse_args()
    selection = load_selection(args.root / "configs/research_input_selection_v0_1.yaml")
    network = build_full_pypsa_skeleton(selection)
    summary = skeleton_summary(network)
    output = args.root / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(
        "SKELETON",
        summary["base_date"],
        summary["generator_capacity_mw"],
        "MW generators;",
        summary["import_boundary_snapshot_mw"],
        "MW ATC snapshot;",
        summary["load_count"],
        "loads; dispatch disabled",
    )


if __name__ == "__main__":
    main()
