"""Audit source-derived Idukki daily inflow recoveries from monthly cumulative rows.

This does not alter the strict v1.4 source-reported inflow gate. It identifies
only values that are uniquely determined by consecutive source cumulative
monthly inflow observations plus directly reported daily inflows.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from itertools import pairwise
from pathlib import Path

import pandas as pd

EXPECTED_SHA256 = (
    "b7d4439135edbe02d9e577892e090aafaf92f58606cdc04ee9b6d39e608036c9"
)
START = pd.Timestamp("2024-04-01")
END = pd.Timestamp("2025-03-30")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def audit(path: Path) -> dict:
    actual = sha256(path)
    if actual != EXPECTED_SHA256:
        raise ValueError(f"Unexpected reservoir_rows.csv SHA256: {actual}")

    rows = pd.read_csv(path, parse_dates=["date"], low_memory=False)
    required = {"date", "reservoir", "inflow_mcm_day", "month_inflow_mu"}
    if not required.issubset(rows):
        raise ValueError(f"Missing columns: {sorted(required - set(rows))}")

    idukki = rows.loc[
        rows["reservoir"].astype(str).str.upper().eq("IDUKKI")
    ].copy()
    if idukki["date"].duplicated().any():
        raise ValueError("Duplicate Idukki dates")
    idukki = idukki.set_index("date").sort_index()

    days = pd.date_range(START, END, freq="D")
    direct = {}
    cumulative = {}
    present = {}
    for day in days:
        present[day] = day in idukki.index
        direct[day] = (
            float(idukki.loc[day, "inflow_mcm_day"])
            if present[day] and pd.notna(idukki.loc[day, "inflow_mcm_day"])
            else None
        )
        cumulative[day] = (
            float(idukki.loc[day, "month_inflow_mu"])
            if present[day] and pd.notna(idukki.loc[day, "month_inflow_mu"])
            else None
        )

    recovered = {}
    intervals = {}
    for month in sorted(set(days.to_period("M"))):
        month_days = [d for d in days if d.to_period("M") == month]
        observed_cumulative = [d for d in month_days if cumulative[d] is not None]
        for left, right in pairwise(observed_cumulative):
            interval = [d for d in month_days if left < d <= right]
            unknown = [d for d in interval if direct[d] is None]
            if len(unknown) != 1:
                continue
            rhs = cumulative[right] - cumulative[left] - sum(
                direct[d] for d in interval if direct[d] is not None
            )
            if rhs < -1e-9:
                continue
            day = unknown[0]
            value = max(0.0, float(rhs))
            recovered[day] = value
            intervals[day] = {
                "left_cumulative_date": left.strftime("%Y-%m-%d"),
                "right_cumulative_date": right.strftime("%Y-%m-%d"),
                "derived_inflow_mcm_day": value,
                "source_row_present_on_target_date": present[day],
            }

    missing = [d for d in days if direct[d] is None]
    unresolved = [d for d in missing if d not in recovered]

    return {
        "classification": (
            "SOURCE_DERIVED_CUMULATIVE_ACCOUNTING_RECOVERY_"
            "NOT_DIRECTLY_REPORTED_DAILY_INFLOW"
        ),
        "source_sha256": actual,
        "pilot_days": len(days),
        "direct_reported_days": sum(direct[d] is not None for d in days),
        "missing_direct_daily_inflow_days": len(missing),
        "uniquely_recovered_days": len(recovered),
        "coverage_after_source_derived_recovery_days": (
            sum(direct[d] is not None for d in days) + len(recovered)
        ),
        "coverage_after_source_derived_recovery_percent": 100.0
        * (sum(direct[d] is not None for d in days) + len(recovered))
        / len(days),
        "recovered_sum_mcm": sum(recovered.values()),
        "recovered": {
            day.strftime("%Y-%m-%d"): intervals[day] for day in sorted(recovered)
        },
        "unresolved_days": [d.strftime("%Y-%m-%d") for d in unresolved],
        "strict_v1_4_gate_changed": False,
        "admit_as_observed_daily_inflow": False,
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("reservoir_rows", type=Path)
    p.add_argument("--out", type=Path)
    args = p.parse_args()
    result = audit(args.reservoir_rows)
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text, encoding="utf-8")
    print(text, end="")


if __name__ == "__main__":
    main()
