"""Download the official KSEB FY2024-25 monthly reservoir workbooks."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from kerala2040.kseb_monthly_acquisition_v1_5 import acquire_bundle


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("PRIVATE/kseb_monthly_fy2024_25"),
    )
    parser.add_argument(
        "--month",
        action="append",
        help="Optional YYYY-MM month; repeat to fetch a subset.",
    )
    args = parser.parse_args()

    result = acquire_bundle(args.out_dir, months=args.month)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
