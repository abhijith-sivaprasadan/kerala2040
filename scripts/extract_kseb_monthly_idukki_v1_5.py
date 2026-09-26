"""Extract the FY2024-25 Idukki daily series from KSEB monthly workbooks."""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from kerala2040.kseb_monthly_workbook_v1_5 import extract_fy2024_25


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bundle-dir", type=Path, required=True)
    parser.add_argument("--out-json", type=Path, required=True)
    parser.add_argument("--out-csv", type=Path)
    args = parser.parse_args()

    result = extract_fy2024_25(args.bundle_dir)
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    if args.out_csv:
        rows = []
        for record in result["records"]:
            row = {"date": record["date"], "sheet": record["sheet"]}
            row.update(record["metrics"])
            rows.append(row)
        keys = sorted({key for row in rows for key in row})
        args.out_csv.parent.mkdir(parents=True, exist_ok=True)
        with args.out_csv.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=keys)
            writer.writeheader()
            writer.writerows(rows)

    print(
        json.dumps(
            {
                "status": result["status"],
                "record_count": result["record_count"],
                "missing_dates": result["missing_dates"],
                "duplicate_dates": result["duplicate_dates"],
            },
            indent=2,
        )
    )
    if not result["ready_for_water_balance_qa"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
