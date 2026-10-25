"""Recalculate the historical daily-demand ML reporting metrics from the frozen record."""

from __future__ import annotations

import json
from pathlib import Path

from kerala2040.fold_evidence import audit_frozen_ml_record


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    source = root / "data/evidence/daily_demand_ml_robustness_v0_2_2026_10_06.json"
    record = json.loads(source.read_text(encoding="utf-8"))
    result = audit_frozen_ml_record(record)
    print(json.dumps(result, indent=2, sort_keys=True, allow_nan=False))


if __name__ == "__main__":
    main()
