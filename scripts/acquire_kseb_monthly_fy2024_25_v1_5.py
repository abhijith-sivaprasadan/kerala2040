"""CLI for acquiring the official KSEB FY2024-25 monthly workbooks."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from kerala2040.kseb_monthly_acquire_v1_5 import DEFAULT_INVENTORY, acquire


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--inventory", type=Path, default=Path(DEFAULT_INVENTORY))
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--report", type=Path)
    parser.add_argument("--attempts", type=int, default=3)
    parser.add_argument("--connect-timeout", type=float, default=15.0)
    parser.add_argument("--read-timeout", type=float, default=120.0)
    args = parser.parse_args()

    result = acquire(
        args.inventory,
        args.out_dir,
        attempts=args.attempts,
        connect_timeout=args.connect_timeout,
        read_timeout=args.read_timeout,
    )
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    if not result["ready_for_content_schema_audit"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
