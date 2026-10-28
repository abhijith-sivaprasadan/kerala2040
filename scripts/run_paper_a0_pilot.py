#!/usr/bin/env python3
"""Paper A0 preliminary FY2024-25 source-completeness/accounting audit.

This re-audits a *public processed* Kerala SLDC daily CSV, not original HTML.
It never fills missing source dates or reconciles distinct annual boundaries.
No external Python dependencies.

Usage:
    python scripts/run_paper_a0_pilot.py

Optional:
    python scripts/run_paper_a0_pilot.py --daily /path/to/daily_balance.csv \
      --ledger /path/to/TABLE_A0_01_reporting_boundary_ledger.csv \
      --output /path/to/outputs
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import defaultdict
from datetime import date, timedelta
from decimal import Decimal, InvalidOperation
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ROOT = REPO / "studies" / "paper-a-2027" / "a0-pilot"
INPUT = REPO / "data" / "external" / "sldc_fy2024_25" / "daily_balance.csv"
LEDGER = ROOT / "TABLE_A0_01_reporting_boundary_ledger.csv"
DEST = ROOT / "reproduced"
NUMERIC = ("hydro_mu", "internal_generation_mu", "net_import_mu", "consumption_mu")
COLUMNS = ("date", "status", "classification", *NUMERIC,
           "balance_residual_mu", "source_sha256")
START, END = date(2024, 4, 1), date(2025, 3, 31)
TOLERANCE = Decimal("0.00011")  # source values displayed to ~4 decimals


def read_rows(file: Path) -> list[dict[str, str]]:
    with file.open(encoding="utf-8-sig", newline="") as stream:
        table = csv.DictReader(stream)
        if table.fieldnames is None:
            raise ValueError("Missing CSV header")
        if len(set(table.fieldnames)) != len(table.fieldnames):
            raise ValueError("Duplicate input headers")
        if not set(COLUMNS) <= set(table.fieldnames):
            raise ValueError("Required columns absent: " +
                             ", ".join(sorted(set(COLUMNS) - set(table.fieldnames))))
        rows = list(table)
    if not rows:
        raise ValueError("Empty input CSV")
    return rows


def decimal_field(row: dict[str, str], field: str) -> Decimal:
    raw = row[field].strip()
    if not raw:
        raise ValueError(f"{row['date']}: blank observed {field}")
    try:
        value = Decimal(raw)
    except InvalidOperation as exc:
        raise ValueError(f"{row['date']}: nonnumeric {field}") from exc
    if not value.is_finite():
        raise ValueError(f"{row['date']}: non-finite {field}")
    return value


def audit_daily(rows: list[dict[str, str]]) -> dict:
    """Validate calendar and accounting, return reproducible observed-only summaries."""
    seen: set[date] = set()
    totals: dict[str, Decimal] = {n: Decimal(0) for n in NUMERIC}
    months = defaultdict(lambda: {
        "calendar_days": 0, "observed_days": 0, "missing_days": 0,
        "observed_consumption_mu": Decimal(0)
    })
    observed, missing = 0, 0
    abs_residual_max = Decimal(0)
    displayed_residual_nonzero_days = 0
    dates_missing: list[str] = []
    max_reported_vs_recomputed_residual = Decimal(0)

    for row in rows:
        label = row["date"].strip()
        try:
            day = date.fromisoformat(label)
        except ValueError as exc:
            raise ValueError(f"Invalid ISO date {label!r}") from exc
        if day < START or day > END:
            raise ValueError(f"Out-of-FY date {day}")
        if day in seen:
            raise ValueError(f"Duplicate date {day}")
        seen.add(day)
        month_key = day.strftime("%Y-%m")
        period = months[month_key]
        period["calendar_days"] += 1

        status = row["status"].strip()
        if status == "observed":
            observed += 1
            period["observed_days"] += 1
            if not row["source_sha256"].strip():
                raise ValueError(f"{day}: missing source hash in processed record")
            numbers = {n: decimal_field(row, n) for n in NUMERIC}
            stored_residual = decimal_field(row, "balance_residual_mu")
            recomputed_residual = (
                numbers["internal_generation_mu"] +
                numbers["net_import_mu"] -
                numbers["consumption_mu"]
            )
            error = abs(recomputed_residual - stored_residual)
            max_reported_vs_recomputed_residual = max(
                max_reported_vs_recomputed_residual, error
            )
            if error > TOLERANCE:
                raise ValueError(f"{day}: stored residual disagrees with arithmetic")
            if abs(recomputed_residual) > TOLERANCE:
                raise ValueError(f"{day}: daily energy-balance residual too large")
            abs_residual_max = max(abs_residual_max, abs(recomputed_residual))
            if stored_residual != 0:
                displayed_residual_nonzero_days += 1
            for k, v in numbers.items():
                totals[k] += v
            period["observed_consumption_mu"] += numbers["consumption_mu"]
        elif status == "missing":
            missing += 1
            period["missing_days"] += 1
            dates_missing.append(label)
            for k in (*NUMERIC, "balance_residual_mu"):
                if row[k].strip():
                    raise ValueError(f"{day}: missing-date record contains {k}")
        else:
            raise ValueError(f"{day}: unsupported status {status!r}")

    all_days = set()
    cursor = START
    while cursor <= END:
        all_days.add(cursor)
        cursor += timedelta(days=1)
    if seen != all_days:
        examples = sorted(all_days - seen)[:5]
        raise ValueError(f"Missing calendar rows (not just missing reports): {examples}")

    months_ordered = []
    for key in sorted(months):
        m = months[key]
        m["coverage_pct"] = str(
            (Decimal(100) * m["observed_days"] / m["calendar_days"]).quantize(
                Decimal("0.0001")
            )
        )
        months_ordered.append({
            "month": key,
            "expected_calendar_days": m["calendar_days"],
            "observed_report_days": m["observed_days"],
            "missing_report_days": m["missing_days"],
            "coverage_pct": m["coverage_pct"],
            "observed_day_consumption_sum_mu": str(
                m["observed_consumption_mu"].quantize(Decimal("0.0001"))
            ),
        })

    total_residual = (
        totals["internal_generation_mu"] + totals["net_import_mu"] -
        totals["consumption_mu"]
    )
    return {
        "calendar_start": START.isoformat(), "calendar_end": END.isoformat(),
        "calendar_rows": len(rows), "observed_days": observed,
        "missing_report_days": missing,
        "coverage_pct": str(
            (Decimal(100) * observed / len(rows)).quantize(Decimal("0.0001"))
        ),
        "missing_dates": dates_missing,
        "observed_day_totals_mu": {
            k: str(v.quantize(Decimal("0.0001"))) for k, v in totals.items()
        },
        "aggregate_of_rounded_daily_balance_residual_mu":
            str(total_residual.quantize(Decimal("0.0001"))),
        "max_abs_recomputed_daily_balance_residual_mu": str(abs_residual_max),
        "max_stored_vs_recomputed_daily_residual_diff_mu":
            str(max_reported_vs_recomputed_residual),
        "stored_nonzero_residual_days": displayed_residual_nonzero_days,
        "monthly": months_ordered,
        "measurement_status": "secondary_recomputation_from_public_processed_daily_csv",
    }


def validate_ledger(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    """Keep source accounting ontology explicit; disallow silent comparisons."""
    fields = ("record_id", "period", "exact_variable_key", "reporting_boundary",
              "calendar_days_represented", "published_or_processed_value",
              "unit", "evidence_class", "original_source_url")
    if len(rows) != 6:
        raise ValueError("Source-boundary ledger should hold exactly 6 cases")
    seen = set()
    for row in rows:
        if not all(row.get(f, "").strip() for f in fields):
            raise ValueError(f"Incomplete source-boundary ledger row: {row}")
        if row["record_id"] in seen:
            raise ValueError("Duplicate source ledger ID")
        seen.add(row["record_id"])
        if row["unit"] != "MU":
            raise ValueError("Unexpected source unit; no unit coercion allowed")
        if row["period"] != "FY2024-25":
            raise ValueError("Mismatched year in annual source ledger")
        decimal_field({"date": row["record_id"],
                       "published_or_processed_value":
                            row["published_or_processed_value"]},
                      "published_or_processed_value")
    return rows


def crosswalk(ledger: list[dict[str, str]]) -> list[dict[str, str]]:
    """For a pilot, classify demonstrably *ineligible* comparisons only.

    We do not assert equivalence for any two independent publishers merely
    because they share units and financial-year names.
    """
    by_id = {r["record_id"]: r for r in ledger}
    comparisons = [
        ("A0-FY25-01", "A0-FY25-06",
         "Full-year consumer-side quantity versus 354-day SLDC operational reports; distinct boundary and coverage"),
        ("A0-FY25-02", "A0-FY25-03",
         "KSEBL category-table sales including outside-state sale/trading versus adjusted within-state sales"),
        ("A0-FY25-01", "A0-FY25-05",
         "Consumer-side energy versus supply/input at state periphery"),
        ("A0-FY25-03", "A0-FY25-04",
         "Within-state electricity sales versus utility generation and purchases; not a valid unadjusted loss proxy"),
    ]
    result = []
    for lhs, rhs, why in comparisons:
        a, b = by_id[lhs], by_id[rhs]
        result.append({
            "left_record": lhs,
            "right_record": rhs,
            "left_boundary": a["reporting_boundary"],
            "right_boundary": b["reporting_boundary"],
            "admissibility": "BLOCKED_AS_DIRECT_SUBTRACTION",
            "reason": why,
            "difference_mu": "",  # intentional: an unearned arithmetic residual
        })
    return result


def write_csv(path: Path, fields: tuple[str, ...], rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8", newline="") as stream:
        out = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        out.writeheader()
        out.writerows(rows)


def run(daily_path: Path = INPUT, ledger_path: Path = LEDGER,
        output_dir: Path = DEST) -> dict:
    daily = daily_path.read_bytes()
    summary = audit_daily(read_rows(daily_path))
    ledger = validate_ledger(read_rows(ledger_path))
    official = {r["record_id"]: r for r in ledger}
    # Fail loudly if the processed sample changes; this is an *internal*
    # consistency check, NOT independent access to the original HTML.
    if summary["observed_days"] != 354 or summary["missing_report_days"] != 11:
        raise ValueError("FY2024-25 source-count regression; investigate new file revision")
    if (summary["observed_day_totals_mu"]["consumption_mu"] !=
            official["A0-FY25-06"]["published_or_processed_value"]):
        raise ValueError("Ledger SLDC number conflicts with processed daily input")

    summary["processed_daily_csv_sha256"] = hashlib.sha256(daily).hexdigest()
    summary["source_ledger_sha256"] = hashlib.sha256(ledger_path.read_bytes()).hexdigest()
    summary["comparability"] = "distinct_scope_annual_values_not_subtracted"
    summary["original_html_bytes_reverified_by_this_script"] = False
    summary["original_economic_review_pdf_reinspected_by_this_script"] = False
    summary["figure_summary"] = (
        "An incomplete 354/365 source-day sum cannot be treated as a "
        "full-FY state electricity-consumption estimate."
    )

    output_dir.mkdir(parents=True, exist_ok=True)
    write_csv(output_dir / "TABLE_A0_02_monthly_source_coverage.csv",
              ("month", "expected_calendar_days", "observed_report_days",
               "missing_report_days", "coverage_pct",
               "observed_day_consumption_sum_mu"), summary["monthly"])
    write_csv(output_dir / "TABLE_A0_03_comparison_admissibility.csv",
              ("left_record", "right_record", "left_boundary",
               "right_boundary", "admissibility", "reason", "difference_mu"),
              crosswalk(ledger))
    (output_dir / "PILOT_SUMMARY.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8"
    )
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--daily", type=Path, default=INPUT)
    parser.add_argument("--ledger", type=Path, default=LEDGER)
    parser.add_argument("--output", type=Path, default=DEST)
    args = parser.parse_args()
    result = run(args.daily, args.ledger, args.output)
    print(json.dumps({
        "calendar_rows": result["calendar_rows"],
        "observed_days": result["observed_days"],
        "missing_report_days": result["missing_report_days"],
        "observed_day_totals_mu": result["observed_day_totals_mu"],
        "original_html_independently_verified": False,
        "output_dir": str(args.output),
    }, indent=2))


if __name__ == "__main__":
    main()
