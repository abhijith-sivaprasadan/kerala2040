"""Build the reconciled FY2024-25 Kerala installed-generation census."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from kerala2040.generator_census import build_generator_census


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--source",
        type=Path,
        default=Path(
            "data/evidence/generation/fy2024_25_generator_capacity_census.json"
        ),
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("results/inventory/fy2024_25_generator_census"),
    )
    args = parser.parse_args()

    frame, summary = build_generator_census(args.source)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    frame.to_csv(args.output_dir / "generator_census.csv", index=False)
    frame.to_parquet(args.output_dir / "generator_census.parquet", index=False)
    (args.output_dir / "generator_census_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
