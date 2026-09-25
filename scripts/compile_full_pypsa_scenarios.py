#!/usr/bin/env python3
"""Compile the full Kerala2040 S0-S5 structural matrix without solving PyPSA."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from kerala2040.scenario_compiler import compile_matrix, load_framework


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("results/models/full_pypsa/scenario_matrix.json"),
    )
    args = parser.parse_args()
    framework = load_framework(args.root / "configs/scenario_dimensions.yaml")
    matrix = compile_matrix(framework)
    payload = {
        "classification": "scenario_structure_not_optimised_result",
        "scenario_count": len(framework["scenarios"]),
        "model_years": sorted({row.model_year for row in matrix}),
        "compiled_cases": len(matrix),
        "ready_to_build_network": sum(not row.blockers for row in matrix),
        "unsolved_specifications": sum(bool(row.blockers) for row in matrix),
        "cases": [row.to_dict() for row in matrix],
    }
    output = args.root / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(
        "COMPILED",
        payload["compiled_cases"],
        "cases;",
        payload["ready_to_build_network"],
        "ready;",
        payload["unsolved_specifications"],
        "blocked",
    )


if __name__ == "__main__":
    main()
