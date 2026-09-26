#!/usr/bin/env python
"""Assess or run Full-PyPSA Idukki reported-inflow checkpoint v1.4."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from kerala2040.full_pypsa_idukki_inflow_release_v1_4 import (
    assess_private_inflow_gate,
    load_idukki_inflow_v14_suite,
    run_idukki_inflow_v14_suite,
)

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs/full_pypsa_idukki_inflow_release_v1_4.yaml"
DEFAULT_PROFILE = (
    ROOT
    / "results/models/full_pypsa/era5_renewables_v0_6/"
    "statewide_equal_weight_profile.parquet"
)
DEFAULT_GATE = (
    ROOT
    / "results/models/full_pypsa/idukki_inflow_release_v1_4/"
    "source_gate.json"
)
DEFAULT_OUTPUT = (
    ROOT
    / "results/models/full_pypsa/idukki_inflow_release_v1_4/"
    "summary.json"
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--private-reservoir-rows", type=Path)
    parser.add_argument("--profile", type=Path, default=DEFAULT_PROFILE)
    parser.add_argument("--gate-output", type=Path, default=DEFAULT_GATE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--gate-only", action="store_true")
    args = parser.parse_args()

    suite = load_idukki_inflow_v14_suite(CONFIG)
    gate = assess_private_inflow_gate(args.private_reservoir_rows, suite)
    args.gate_output.parent.mkdir(parents=True, exist_ok=True)
    args.gate_output.write_text(
        json.dumps(gate, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(gate, indent=2, sort_keys=True))

    if args.gate_only:
        return
    if not gate["physical_run_ready"]:
        raise SystemExit(
            "v1.4 physical run blocked by private source gate. "
            "Supply the exact Phase-4-audited reservoir_rows.csv with all "
            "364 pilot-day Idukki inflow values."
        )

    summary = run_idukki_inflow_v14_suite(
        ROOT,
        private_source=args.private_reservoir_rows,
        profile_path=args.profile,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "classification": summary["classification"],
                "pilot_days": summary["pilot_days"],
                "cases_solved": summary["cases_solved"],
                "source_qa": summary["source_qa"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
