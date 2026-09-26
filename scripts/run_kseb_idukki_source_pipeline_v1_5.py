"""Run the complete KSEB FY2024-25 Idukki source-admission pipeline.

Stages:
1. acquire the 12 official KSEB monthly workbooks (unless --skip-download);
2. byte-level bundle gate;
3. header-driven daily Idukki extraction;
4. water-balance QA and source-anomaly screening.

This command deliberately stops before optimization. A stateful model may use
the result only after this pipeline declares the source ready.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from kerala2040.kseb_idukki_water_balance_v1_5 import water_balance_qa
from kerala2040.kseb_monthly_acquisition_v1_5 import acquire_bundle
from kerala2040.kseb_monthly_workbook_v1_5 import extract_fy2024_25


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def write_records_csv(path: Path, records: list[dict]) -> None:
    rows = []
    for record in records:
        row = {"date": record["date"], "sheet": record["sheet"]}
        row.update(record["metrics"])
        rows.append(row)
    fields = sorted({key for row in rows for key in row})
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--bundle-dir",
        type=Path,
        default=Path("PRIVATE/kseb_monthly_fy2024_25"),
    )
    parser.add_argument(
        "--results-dir",
        type=Path,
        default=Path("results/hydro/kseb_idukki_v1_5"),
    )
    parser.add_argument("--skip-download", action="store_true")
    args = parser.parse_args()

    if not args.skip_download:
        acquisition = acquire_bundle(args.bundle_dir)
        write_json(args.results_dir / "acquisition.json", acquisition)

    extraction = extract_fy2024_25(args.bundle_dir)
    write_json(args.results_dir / "extraction.json", extraction)
    write_records_csv(
        args.results_dir / "idukki_daily.csv",
        extraction["records"],
    )
    if not extraction["ready_for_water_balance_qa"]:
        raise SystemExit(2)

    qa = water_balance_qa(extraction["records"])
    write_json(args.results_dir / "water_balance_qa.json", qa)

    summary = {
        "classification": "KSEB_IDUKKI_SOURCE_ADMISSION_PIPELINE_V1_5",
        "record_count": extraction["record_count"],
        "full_year_extraction_ready": extraction[
            "ready_for_water_balance_qa"
        ],
        "water_balance_qa_ready": qa["finite"],
        "source_anomaly_count": qa["source_anomaly_count"],
        "automatic_source_corrections_applied": False,
        "ready_for_stateful_model_source_admission": (
            extraction["ready_for_water_balance_qa"]
            and qa["ready_for_model_input"]
        ),
        "validated_capacity_plan": False,
    }
    write_json(args.results_dir / "summary.json", summary)
    print(json.dumps(summary, indent=2))
    if not summary["ready_for_stateful_model_source_admission"]:
        raise SystemExit(3)


if __name__ == "__main__":
    main()
