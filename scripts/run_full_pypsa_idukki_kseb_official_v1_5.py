"""Assess or run Full-PyPSA official-KSEB Idukki checkpoint v1.5."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from kerala2040.full_pypsa_idukki_kseb_official_v1_5 import (
    assess_kseb_official_gate,
    load_kseb_official_v15_suite,
    run_kseb_official_v15_suite,
)

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs/full_pypsa_idukki_kseb_official_v1_5.yaml"
DEFAULT_PROFILE = (
    ROOT
    / "results/models/full_pypsa/era5_renewables_v0_6/"
    "statewide_equal_weight_profile.parquet"
)
DEFAULT_GATE = (
    ROOT
    / "results/models/full_pypsa/idukki_kseb_official_v1_5/"
    "source_gate.json"
)
DEFAULT_OUTPUT = (
    ROOT
    / "results/models/full_pypsa/idukki_kseb_official_v1_5/"
    "summary.json"
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--kseb-bundle-dir", type=Path)
    parser.add_argument("--profile", type=Path, default=DEFAULT_PROFILE)
    parser.add_argument("--gate-output", type=Path, default=DEFAULT_GATE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--gate-only", action="store_true")
    args = parser.parse_args()

    suite = load_kseb_official_v15_suite(CONFIG)
    gate = assess_kseb_official_gate(ROOT, args.kseb_bundle_dir, suite)
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
            "v1.5 physical run blocked by official KSEB source gate. "
            "Acquire all 12 FY2024-25 monthly workbooks and pass the direct "
            "365-day storage + Inflow (MCM) gate without interpolation."
        )

    summary = run_kseb_official_v15_suite(
        ROOT,
        bundle_dir=args.kseb_bundle_dir,
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
