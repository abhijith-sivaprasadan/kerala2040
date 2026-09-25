"""Validate and summarize Full-PyPSA renewable capacity envelope v0.7."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from kerala2040.full_pypsa_renewable_capacity import validate_capacity_envelope

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config",
        type=Path,
        default=ROOT / "configs/full_pypsa_renewable_capacity_v0_7.yaml",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "results/models/full_pypsa/renewable_capacity_v0_7/summary.json",
    )
    args = parser.parse_args()
    summary = validate_capacity_envelope(ROOT, args.config)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
