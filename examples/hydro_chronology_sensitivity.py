"""Rerun the historical reconstruction-only hydro timing robustness experiment."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from kerala2040.hydro_chronology_uncertainty import run

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "results/examples/hydro_chronology_sensitivity.json")
    args = parser.parse_args()
    result = run(ROOT)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Completed {len(result['results'])} source-derived test cases for {result['selected_observed_high_consumption_dates'][0]} through {result['selected_observed_high_consumption_dates'][-1]}.")
    print("RECONSTRUCTED NOT MEASURED; historical sensitivity NOT a check of 2030-31 model headline.")


if __name__ == "__main__":
    main()
