"""Build the canonical generator/capacity inventory seed."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import yaml

from kerala2040.generators import generator_database


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--projects", type=Path, default=Path("public/kseb-projects.json")
    )
    parser.add_argument(
        "--observed", type=Path, default=Path("configs/observed_2024_25.yaml")
    )
    parser.add_argument(
        "--reconciliation",
        type=Path,
        default=Path("configs/generator_reconciliation_2024_25.yaml"),
    )
    parser.add_argument("--output-dir", type=Path, default=Path("results/inventory"))
    args = parser.parse_args()

    projects = json.loads(args.projects.read_text(encoding="utf-8"))
    observed = yaml.safe_load(args.observed.read_text(encoding="utf-8"))
    reconciliation = yaml.safe_load(args.reconciliation.read_text(encoding="utf-8"))
    frame, summary = generator_database(projects, observed, reconciliation)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    frame.to_csv(args.output_dir / "generator_capacity_database.csv", index=False)
    frame.to_parquet(args.output_dir / "generator_capacity_database.parquet", index=False)
    (args.output_dir / "generator_capacity_summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
