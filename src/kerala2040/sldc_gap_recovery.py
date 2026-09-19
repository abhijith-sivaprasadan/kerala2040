"""Recheck the exact missing SLDC Generation dates without fabricating observations.

This collects *candidates*, not an update to the 354-day validated archive. Dates must
match the response heading, required system-balance metrics must parse, and MU
accounting must agree. A complete daily-source recovery additionally requires the
other four report sections and reintegration against the retained original archive.
"""

from __future__ import annotations

import hashlib
import json
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from requests import Session

from kerala2040.sources.sldc import SYSTEM_STATS_URL, parse_system_statistics

FORM_ACTION_URL = "https://sldckerala.com/index.php"
BALANCE_TOLERANCE_MU = 0.001


def _date_payload(iso_date: str) -> dict[str, str]:
    yyyy, mm, dd = iso_date.split("-")
    return {
        "date1_day": dd,
        "date1_month": mm,
        "date1_year": yyyy,
        "sbtstat": "SHOW",
    }


def probe_missing_dates(
    missing_dates: list[str],
    output: Path,
    session: Session,
    *,
    pause_seconds: float = 0.8,
    timeout: float = 30,
) -> dict[str, Any]:
    """Attempt the adapter endpoint and the live form's canonical action.

    Never save a wrong-date or absent report as a validated observation.
    The form action is a fallback because the live date selector submits to
    /index.php while the historical adapter uses /index.php?id=1.
    """
    if len(set(missing_dates)) != len(missing_dates):
        raise ValueError("Duplicate dates in source QA")
    output.mkdir(parents=True, exist_ok=True)
    candidate_dir = output / "verified_generation_candidates"
    candidate_dir.mkdir(exist_ok=True)
    records = []

    for iso_date in missing_dates:
        attempts = []
        accepted = None
        for endpoint in (SYSTEM_STATS_URL, FORM_ACTION_URL):
            try:
                response = session.post(
                    endpoint, data=_date_payload(iso_date), timeout=timeout
                )
                detail: dict[str, Any] = {
                    "endpoint": endpoint,
                    "http_status": response.status_code,
                    "final_url": response.url,
                    "retrieved_at_utc": datetime.now(UTC).isoformat(),
                    "response_sha256": hashlib.sha256(response.content).hexdigest(),
                    "response_bytes": len(response.content),
                }
                if response.status_code != 200:
                    detail["result"] = "http_error"
                else:
                    parsed = parse_system_statistics(response.text)
                    detail["returned_report_date"] = parsed["report_date"]
                    detail["balance_error_mu"] = parsed["balance_error_mu"]
                    if parsed["report_date"] != iso_date:
                        detail["result"] = "wrong_report_date"
                    elif abs(parsed["balance_error_mu"]) > BALANCE_TOLERANCE_MU:
                        detail["result"] = "balance_failure"
                    else:
                        detail["result"] = "verified_generation_candidate"
                        candidate = candidate_dir / f"{iso_date}.html"
                        candidate.write_bytes(response.content)
                        detail["candidate_path"] = str(candidate)
                        detail["metrics_mu"] = parsed["metrics"]
                        accepted = detail
                attempts.append(detail)
                if accepted:
                    break
            except (ValueError, OSError, RuntimeError) as exc:
                attempts.append({
                    "endpoint": endpoint,
                    "result": "unverified_response",
                    "exception_type": type(exc).__name__,
                    "detail": str(exc)[:350],
                })
            except Exception as exc:
                # Transport and TLS failures are evidence of a failed request,
                # never proof that no dated report exists in the agency records.
                attempts.append({
                    "endpoint": endpoint,
                    "result": "request_failed",
                    "exception_type": type(exc).__name__,
                    "detail": str(exc)[:350],
                })
            if pause_seconds:
                time.sleep(pause_seconds)
        records.append({
            "requested_date": iso_date,
            "status": "generation_candidate_only" if accepted else "not_recovered",
            "accepted_attempt": accepted,
            "attempts": attempts,
        })
        if pause_seconds:
            time.sleep(pause_seconds)

    found = sum(record["status"] == "generation_candidate_only" for record in records)
    report = {
        "classification": "primary_source_retrieval_attempt_not_validated_dataset",
        "source": "Kerala SLDC public historical date form",
        "source_url": SYSTEM_STATS_URL,
        "source_scope": (
            "Generation section only. Other original sections: Imports, "
            "Storage, Availability, Others; not recovered or validated here."
        ),
        "requested_missing_dates": missing_dates,
        "recovered_generation_candidates": found,
        "not_recovered": len(records) - found,
        "original_archive_updated": False,
        "official_observed_day_coverage_changed": False,
        "audit_gate_closed": False,
        "records": records,
    }
    (output / "attempts.json").write_text(
        json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )
    return report


def probe_from_committed_qa(
    root: Path,
    output: Path,
    session: Session,
    *,
    pause_seconds: float = 0.8,
    timeout: float = 30,
) -> dict[str, Any]:
    qa = json.loads(
        (root / "data/external/sldc_fy2024_25/qa_report.json").read_text(
            encoding="utf-8"
        )
    )
    if qa["expected_days"] != 365 or qa["observed_days"] != 354:
        raise ValueError("Committed source coverage has changed; review before retry")
    dates = qa["missing_dates"]
    if len(dates) != 11:
        raise ValueError("Expected the exact 11 source-identified missing dates")
    return probe_missing_dates(
        dates, output, session, pause_seconds=pause_seconds, timeout=timeout
    )
