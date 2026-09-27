"""Content-level gate for the FY2024-25 official KSEB Idukki series."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

from kerala2040.kseb_monthly_bundle_v1_5 import EXPECTED_MONTHS
from kerala2040.kseb_monthly_parser_v1_5 import parse_workbook

START = pd.Timestamp("2024-04-01")
END = pd.Timestamp("2025-03-31")
DISPATCH_END = pd.Timestamp("2025-03-30")
ANCHOR_EVIDENCE = (
    "data/evidence/hydro/"
    "idukki_v1_5_official_daily_gap_anchors_2026_09_26.json"
)


def _flatten(record: dict[str, Any]) -> dict[str, Any]:
    row = {
        "date": record["date"],
        "reservoir": record["reservoir"],
        "source_month": record["source_month"],
        "source_file": record["source_file"],
        "source_sha256": record["source_sha256"],
        "source_sheet": record["source_sheet"],
    }
    row.update(record["metrics"])
    return row


def extract_official_series(bundle_dir: Path) -> dict[str, Any]:
    monthly = []
    rows = []
    for month in EXPECTED_MONTHS:
        matches = list(bundle_dir.glob(f"{month}.*"))
        if len(matches) != 1:
            raise ValueError(
                f"Expected one official KSEB workbook for {month}, found {len(matches)}"
            )
        parsed = parse_workbook(matches[0], source_month=month)
        monthly.append(
            {
                "month": month,
                "source_file": parsed["source_file"],
                "source_sha256": parsed["source_sha256"],
                "record_count": parsed["record_count"],
                "ignored_sheets": parsed["ignored_sheets"],
            }
        )
        rows.extend(_flatten(record) for record in parsed["records"])

    frame = pd.DataFrame(rows)
    if frame.empty:
        raise ValueError("No official KSEB Idukki daily rows were extracted")
    frame["date"] = pd.to_datetime(frame["date"])
    if frame["date"].duplicated().any():
        duplicates = frame.loc[frame["date"].duplicated(keep=False), "date"]
        raise ValueError(
            "Duplicate KSEB Idukki dates: "
            + ", ".join(sorted(set(duplicates.dt.strftime("%Y-%m-%d"))))
        )
    frame = frame.set_index("date").sort_index()

    required_days = pd.date_range(START, END, freq="D")
    missing_dates = required_days.difference(frame.index)
    outside = frame.index.difference(required_days)

    storage = pd.to_numeric(
        frame.get("live_storage_mcm", pd.Series(index=frame.index, dtype=float)),
        errors="coerce",
    ).reindex(required_days)
    inflow = pd.to_numeric(
        frame.get("inflow_mcm", pd.Series(index=frame.index, dtype=float)),
        errors="coerce",
    ).reindex(required_days)

    invalid_storage = required_days[
        ~(storage.notna() & storage.ge(0) & storage.le(1460.5)).to_numpy()
    ]
    invalid_inflow = required_days[
        ~(inflow.notna() & inflow.ge(0) & inflow.le(300)).to_numpy()
    ]

    return {
        "classification": "OFFICIAL_KSEB_IDUKKI_FY2024_25_CONTENT_GATE_V1_5",
        "frame": frame,
        "monthly_sources": monthly,
        "required_days": len(required_days),
        "extracted_unique_days": int(frame.index.nunique()),
        "missing_dates": [d.strftime("%Y-%m-%d") for d in missing_dates],
        "outside_required_dates": [d.strftime("%Y-%m-%d") for d in outside],
        "invalid_or_missing_storage_dates": [
            d.strftime("%Y-%m-%d") for d in invalid_storage
        ],
        "invalid_or_missing_inflow_dates": [
            d.strftime("%Y-%m-%d") for d in invalid_inflow
        ],
        "storage_mcm": storage,
        "inflow_mcm_day": inflow,
        "complete_365_day_storage_and_inflow": bool(
            not len(missing_dates)
            and not len(outside)
            and not len(invalid_storage)
            and not len(invalid_inflow)
        ),
    }


def reconcile_daily_anchors(root: Path, frame: pd.DataFrame) -> dict[str, Any]:
    evidence = json.loads((root / ANCHOR_EVIDENCE).read_text(encoding="utf-8"))
    checks = []
    for day, source in evidence["dates"].items():
        timestamp = pd.Timestamp(day)
        if timestamp not in frame.index:
            checks.append(
                {
                    "date": day,
                    "status": "missing_monthly_row",
                    "passed": False,
                }
            )
            continue

        row = frame.loc[timestamp]
        storage_actual = pd.to_numeric(row.get("live_storage_mcm"), errors="coerce")
        storage_expected = source.get("live_storage_mcm")
        storage_delta = (
            None
            if pd.isna(storage_actual) or storage_expected is None
            else float(storage_actual) - float(storage_expected)
        )

        rate_actual = pd.to_numeric(
            row.get("average_inflow_cumecs"),
            errors="coerce",
        )
        if pd.isna(rate_actual):
            rate_actual = pd.to_numeric(row.get("inflow_cumecs"), errors="coerce")
        rate_expected = source.get("inflow_cumecs")
        rate_delta = (
            None
            if pd.isna(rate_actual) or rate_expected is None
            else float(rate_actual) - float(rate_expected)
        )

        storage_pass = storage_delta is not None and abs(storage_delta) <= 0.01
        rate_pass = rate_delta is None or abs(rate_delta) <= 0.05
        checks.append(
            {
                "date": day,
                "status": "checked",
                "monthly_storage_mcm": (
                    None if pd.isna(storage_actual) else float(storage_actual)
                ),
                "daily_page_storage_mcm": storage_expected,
                "storage_delta_mcm": storage_delta,
                "monthly_average_inflow_cumecs": (
                    None if pd.isna(rate_actual) else float(rate_actual)
                ),
                "daily_page_inflow_cumecs": rate_expected,
                "inflow_rate_delta_cumecs": rate_delta,
                "passed": bool(storage_pass and rate_pass),
            }
        )
    return {
        "classification": "KSEB_MONTHLY_VS_OFFICIAL_DAILY_ANCHOR_RECONCILIATION_V1_5",
        "checks": checks,
        "all_anchors_passed": all(item["passed"] for item in checks),
    }


def build_model_input(root: Path, bundle_dir: Path) -> dict[str, Any]:
    extracted = extract_official_series(bundle_dir)
    anchors = reconcile_daily_anchors(root, extracted["frame"])

    ready = (
        extracted["complete_365_day_storage_and_inflow"]
        and anchors["all_anchors_passed"]
    )
    dispatch_days = pd.date_range(START, DISPATCH_END, freq="D")
    return {
        "classification": "KSEB_OFFICIAL_IDUKKI_MODEL_INPUT_GATE_V1_5",
        "status": "ready_official_source_complete" if ready else "blocked_source_qa",
        "physical_run_ready": bool(ready),
        "required_calendar_days": extracted["required_days"],
        "required_dispatch_days": len(dispatch_days),
        "extracted_unique_days": extracted["extracted_unique_days"],
        "missing_dates": extracted["missing_dates"],
        "invalid_or_missing_storage_dates": extracted[
            "invalid_or_missing_storage_dates"
        ],
        "invalid_or_missing_inflow_dates": extracted[
            "invalid_or_missing_inflow_dates"
        ],
        "monthly_sources": extracted["monthly_sources"],
        "anchor_reconciliation": anchors,
        "initial_storage_mcm": (
            float(extracted["storage_mcm"].loc[START])
            if ready
            else None
        ),
        "terminal_storage_mcm": (
            float(extracted["storage_mcm"].loc[END])
            if ready
            else None
        ),
        "dispatch_inflow_mcm_day": (
            extracted["inflow_mcm_day"].reindex(dispatch_days) if ready else None
        ),
        "frame": extracted["frame"],
    }
