"""Build an explicit FY2024-25 energy-accounting reconciliation table."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd
import yaml

from kerala2040.reconciliation import build_energy_reconciliation


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--observed", type=Path, default=Path("configs/observed_2024_25.yaml")
    )
    parser.add_argument(
        "--cea", type=Path, default=Path("configs/cea_resource_adequacy_2025.yaml")
    )
    parser.add_argument(
        "--baseline-summary", type=Path, default=Path("results/baseline/summary.json")
    )
    parser.add_argument(
        "--proxy-summary", type=Path, default=Path("public/hourly-load-proxy-summary.json")
    )
    parser.add_argument("--output-dir", type=Path, default=Path("results/reconciliation"))
    args = parser.parse_args()

    observed = yaml.safe_load(args.observed.read_text(encoding="utf-8"))
    cea = yaml.safe_load(args.cea.read_text(encoding="utf-8"))
    observed["cea_actual_2024_25"] = {
        **cea["actual_2024_25"],
        "source": "Central Electricity Authority Resource Adequacy Plan for Kerala",
    }
    baseline = json.loads(args.baseline_summary.read_text(encoding="utf-8"))
    proxy = (
        json.loads(args.proxy_summary.read_text(encoding="utf-8"))
        if args.proxy_summary.exists()
        else None
    )

    result = build_energy_reconciliation(observed, baseline, proxy_summary=proxy)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "energy_reconciliation.json").write_text(
        json.dumps(result, indent=2), encoding="utf-8"
    )
    pd.DataFrame(result["rows"]).to_csv(
        args.output_dir / "energy_reconciliation.csv", index=False
    )
    print(json.dumps(result["checks"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
