"""Validate and summarise the Full-PyPSA v0.5 research cost/finance package."""
from __future__ import annotations

import json
from pathlib import Path

from kerala2040.full_pypsa_cost_finance import (
    build_cost_finance_summary,
    load_cost_finance_suite,
)

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs/full_pypsa_cost_finance_v0_5.yaml"
OUT = ROOT / "results/models/full_pypsa/cost_finance_v0_5/summary.json"


def main() -> None:
    data = load_cost_finance_suite(CONFIG)
    summary = build_cost_finance_summary(data)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
