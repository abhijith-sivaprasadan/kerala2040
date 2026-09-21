"""Fail-closed intake of authentic Kerala demand + actual net interchange time series.

This checks candidate files, never decides their legal/scientific source admission.
Do not commit raw agency exports. The release audit deliberately remains blocked.
"""

from __future__ import annotations

import csv
import hashlib
import io
import math
import re
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from typing import Any

IST = timezone(timedelta(hours=5, minutes=30))
START = date(2024, 4, 1)
END = date(2025, 3, 31)
COLUMNS = (
    "interval_start_ist",
    "state_demand_mw",
    "actual_net_import_mw",
    "quality",
)
REQUIRED_METADATA = (
    "source_id",
    "source_document",
    "received_at_utc",
    "source_sha256",
    "rights",
    "demand_boundary",
    "actual_interchange_boundary",
    "revision_id",
    "interval_minutes",
    "timestamp_semantics",
    "timezone",
    "net_import_sign",
)
_SHA = re.compile(r"^[a-f0-9]{64}$")
_QUALITY = {"measured", "revised_measured"}


def _report(errors: list[str], metadata: dict[str, Any], actual_hash: str) -> dict[str, Any]:
    return {
        "classification": "candidate_interval_file_validation_not_source_admission",
        "source_id": metadata.get("source_id"),
        "source_sha256": actual_hash,
        "passed_candidate_checks": not errors,
        "source_authenticity_reviewed": False,
        "source_reuse_terms_reviewed": False,
        "measured_interval_release_gate_passed": False,
        "valid_for_2040_model": False,
        "errors": errors,
    }


def validate_interval_bytes(
    content: bytes,
    metadata: dict[str, Any],
    daily: dict[str, Any],
    *,
    start: date = START,
    end: date = END,
    max_daily_difference_mu: float = 0.25,
) -> dict[str, Any]:
    """Check complete source-file chronology and source-specific daily reconciliation.

    Time strings must be interval START with explicit +05:30 offset. Daily
    MU=sum(interval average MW * interval hours)/1000, NOT sum MW or
    sum instantaneous peaks. The SLDC comparisons are boundary diagnostics;
    passing them never grants source authenticity or release-gate admission.
    """
    errors: list[str] = []
    actual_hash = hashlib.sha256(content).hexdigest()
    report = _report(errors, metadata, actual_hash)
    missing = sorted(set(REQUIRED_METADATA) - set(metadata))
    if missing:
        errors.append(f"Missing source metadata: {missing}")
        return report
    for name in ("source_id", "source_document", "rights", "demand_boundary",
                 "actual_interchange_boundary", "revision_id"):
        if not isinstance(metadata[name], str) or not metadata[name].strip():
            errors.append(f"Missing non-empty source metadata: {name}")
    declared = metadata["source_sha256"]
    if not isinstance(declared, str) or not _SHA.fullmatch(declared):
        errors.append("Invalid declared source SHA-256")
    elif actual_hash != declared:
        errors.append("Raw file SHA-256 does not match source metadata")
    try:
        received = datetime.fromisoformat(metadata["received_at_utc"].replace("Z", "+00:00"))
        if received.tzinfo is None or received.utcoffset() != timedelta(0):
            raise ValueError("not UTC")
    except (AttributeError, ValueError):
        errors.append("Received-at timestamp is not explicit UTC")
    minutes = metadata["interval_minutes"]
    if isinstance(minutes, bool) or minutes not in (15, 60):
        errors.append("Interval must be 15 or 60 minutes")
    if metadata["timestamp_semantics"] != "interval_start":
        errors.append("Time labels must mark interval start")
    if metadata["timezone"] != "Asia/Kolkata":
        errors.append("Source timezone must be Asia/Kolkata")
    if metadata["net_import_sign"] != "positive_import":
        errors.append("Actual net interchange must be positive for imports")
    if max_daily_difference_mu < 0 or not math.isfinite(max_daily_difference_mu):
        errors.append("Daily comparison tolerance must be nonnegative and finite")
    if end < start:
        errors.append("End precedes start")
    if errors:
        return report

    try:
        reader = csv.DictReader(io.StringIO(content.decode("utf-8-sig"), newline=""))
        fields = reader.fieldnames or []
        if len(fields) != len(set(fields)):
            errors.append("Duplicate CSV headers")
        if not set(COLUMNS) <= set(fields):
            errors.append(f"Missing required CSV columns: {sorted(set(COLUMNS) - set(fields))}")
        if errors:
            return report
        rows = list(reader)
    except (UnicodeError, csv.Error) as exc:
        errors.append(f"Invalid UTF-8 CSV: {type(exc).__name__}")
        return report

    count_per_day: dict[date, int] = defaultdict(int)
    demand_mu: dict[date, float] = defaultdict(float)
    actual_import_mu: dict[date, float] = defaultdict(float)
    seen: set[datetime] = set()
    previous: datetime | None = None
    width = timedelta(minutes=minutes)
    expected = (end - start).days + 1
    expected *= 24 * 60 // minutes
    report["expected_intervals"] = expected
    report["observed_candidate_intervals"] = len(rows)
    if len(rows) != expected:
        errors.append(f"Expected exactly {expected} intervals; got {len(rows)}")

    for index, row in enumerate(rows, start=2):
        if None in row:
            errors.append(f"Line {index}: unexpected extra fields")
            break
        try:
            timestamp = datetime.fromisoformat(row["interval_start_ist"])
            if timestamp.utcoffset() != timedelta(hours=5, minutes=30):
                raise ValueError("timestamp missing +05:30 offset")
            if timestamp.second or timestamp.microsecond or (
                timestamp.hour * 60 + timestamp.minute
            ) % minutes:
                raise ValueError("timestamp is not aligned to interval boundary")
            day = timestamp.date()
            if day < start or day > end:
                raise ValueError("timestamp outside requested fiscal period")
            if timestamp in seen:
                raise ValueError("duplicate timestamp")
            if previous is not None and timestamp - previous != width:
                raise ValueError("gap, overlapping block or unsorted timestamp")
            seen.add(timestamp)
            previous = timestamp
            demand = float(row["state_demand_mw"])
            imported = float(row["actual_net_import_mw"])
            if not math.isfinite(demand) or demand < 0:
                raise ValueError("non-finite or negative state demand")
            if not math.isfinite(imported):
                raise ValueError("non-finite actual net interchange")
            if row["quality"] not in _QUALITY:
                raise ValueError("unverified, missing, interpolated or synthetic quality")
            if row["quality"] == "revised_measured" and metadata["revision_id"] == "original":
                raise ValueError("revised block without an identified revision")
        except (TypeError, ValueError, KeyError) as exc:
            errors.append(f"Line {index}: {exc}")
            if len(errors) >= 12:
                break
            continue
        count_per_day[day] += 1
        demand_mu[day] += demand * minutes / 60000
        actual_import_mu[day] += imported * minutes / 60000

    if rows and not errors:
        first = datetime.combine(start, datetime.min.time(), tzinfo=IST)
        final = datetime.combine(end + timedelta(days=1), datetime.min.time(),
                                 tzinfo=IST) - width
        if previous != final or first not in seen:
            errors.append("Source chronology does not span both exact FY boundary intervals")
        expected_day_count = 24 * 60 // minutes
        if len(count_per_day) != (end - start).days + 1 or any(
            count != expected_day_count for count in count_per_day.values()
        ):
            errors.append("At least one IST day lacks complete interval coverage")

    obs = daily.get("records", [])
    official: dict[date, dict[str, Any]] = {}
    try:
        for item in obs:
            day = date.fromisoformat(item["date"])
            if day in official:
                raise ValueError("Duplicate official SLDC day")
            official[day] = item
    except (TypeError, KeyError, ValueError) as exc:
        errors.append(f"Invalid reference daily source: {exc}")
    overlap = sorted(set(official) & set(count_per_day))
    if not overlap:
        errors.append("No overlap with the official SLDC daily control")
    if start == START and end == END and len(overlap) != 354:
        errors.append(f"Expected 354 separately observed SLDC control dates; got {len(overlap)}")
    comparisons = {}
    for name, measured, official_col in (
        ("demand_vs_consumption", demand_mu, "consumption_mu"),
        ("actual_import_vs_sldc_net_import", actual_import_mu, "net_import_interface_mu"),
    ):
        differences = []
        for day in overlap:
            try:
                ref = float(official[day][official_col])
                if not math.isfinite(ref):
                    raise ValueError("non-finite official reference")
                differences.append((day.isoformat(), measured[day] - ref))
            except (KeyError, TypeError, ValueError):
                errors.append(f"Official SLDC {official_col} invalid on {day}")
                break
        ranked = sorted(differences, key=lambda part: abs(part[1]), reverse=True)
        worst = ranked[:5]
        comparisons[name] = {
            "reference_source": "Kerala SLDC observed daily statistics",
            "compared_days": len(differences),
            "max_abs_difference_mu": round(abs(worst[0][1]), 6) if worst else None,
            "worst_dates_and_difference_mu": [
                {"date": day, "difference_mu": round(delta, 6)} for day, delta in worst
            ],
            "days_outside_tolerance": sum(
                abs(delta) > max_daily_difference_mu for _, delta in differences
            ),
        }
        if any(abs(delta) > max_daily_difference_mu for _, delta in differences):
            errors.append(f"{name} differs from SLDC control beyond tolerance; "
                          "verify meter/accounting boundary before calibration")

    report.update({
        "source_interval_minutes": minutes,
        "fy_start_ist": start.isoformat(),
        "fy_end_ist": end.isoformat(),
        "candidate_days": len(count_per_day),
        "sldc_observed_control_days": len(overlap),
        "unverified_sldc_dates_not_backfilled": (
            11 if start == START and end == END else None
        ),
        "daily_tolerance_mu": max_daily_difference_mu,
        "reconciliation": comparisons,
        "passed_candidate_checks": not errors,
    })
    return report
