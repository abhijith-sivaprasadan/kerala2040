"""Fail-closed recovery of missing Kerala SLDC Storage reports.

This module only collects date-verified candidate source pages. It never updates
the validated archive automatically and never substitutes a neighbouring date.
"""
from __future__ import annotations

import hashlib
import json
import re
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup
from requests import Session
from requests.exceptions import RequestException

STORAGE_URL = "https://sldckerala.com/index.php?id=7"
FORM_ACTION_URL = "https://sldckerala.com/index.php"
HEADING_RE = re.compile(
    r"SYSTEM\s+STATISTICS:\s*STORAGE\s+AS\s+ON\s+"
    r"(\d{2})\.(\d{2})\.(\d{4})",
    re.IGNORECASE,
)


def _payload(iso_date: str) -> dict[str, str]:
    yyyy, mm, dd = iso_date.split("-")
    return {
        "date1_day": dd,
        "date1_month": mm,
        "date1_year": yyyy,
        "sbtstat": "SHOW",
    }


def _parse_storage_candidate(html: str, requested_date: str) -> dict[str, Any]:
    soup = BeautifulSoup(html, "html.parser")
    text = " ".join(soup.stripped_strings)
    matches = HEADING_RE.findall(text)
    dates = [
        f"{yyyy}-{mm}-{dd}"
        for dd, mm, yyyy in matches
    ]
    unique_dates = sorted(set(dates))
    if unique_dates != [requested_date]:
        return {
            "accepted": False,
            "returned_report_dates": unique_dates,
            "reason": "requested_storage_heading_not_unique_or_exact",
        }

    idukki_rows: list[list[str]] = []
    for tr in soup.find_all("tr"):
        cells = [
            cell.get_text(" ", strip=True)
            for cell in tr.find_all(["th", "td"])
        ]
        if any(cell.strip().upper() == "IDUKKI" for cell in cells):
            idukki_rows.append(cells)
    if len(idukki_rows) != 1:
        return {
            "accepted": False,
            "returned_report_dates": unique_dates,
            "reason": "idukki_row_not_unique",
            "idukki_row_count": len(idukki_rows),
        }

    row = idukki_rows[0]
    if len(row) < 14:
        return {
            "accepted": False,
            "returned_report_dates": unique_dates,
            "reason": "idukki_row_too_short",
            "idukki_row": row,
        }

    return {
        "accepted": True,
        "returned_report_dates": unique_dates,
        "idukki_row": row,
        "idukki_inflow_cell": row[12] if len(row) > 12 else "",
        "idukki_cumulative_inflow_cell": row[13] if len(row) > 13 else "",
    }


def probe_storage_dates(
    dates: list[str],
    output: Path,
    session: Session,
    *,
    control_date: str = "2024-11-29",
    pause_seconds: float = 0.8,
    timeout: float = 30.0,
) -> dict[str, Any]:
    if len(dates) != len(set(dates)):
        raise ValueError("Duplicate requested storage dates")
    output.mkdir(parents=True, exist_ok=True)
    candidate_dir = output / "verified_storage_candidates"
    candidate_dir.mkdir(exist_ok=True)

    def attempt_one(iso_date: str) -> dict[str, Any]:
        attempts: list[dict[str, Any]] = []
        accepted: dict[str, Any] | None = None
        for endpoint in (STORAGE_URL, FORM_ACTION_URL):
            detail: dict[str, Any] = {"endpoint": endpoint}
            try:
                response = session.post(
                    endpoint,
                    data=_payload(iso_date),
                    timeout=timeout,
                    allow_redirects=True,
                )
                detail.update({
                    "http_status": response.status_code,
                    "final_url": response.url,
                    "retrieved_at_utc": datetime.now(UTC).isoformat(),
                    "response_sha256": hashlib.sha256(response.content).hexdigest(),
                    "response_bytes": len(response.content),
                })
                if response.status_code != 200:
                    detail["result"] = "http_error"
                else:
                    parsed = _parse_storage_candidate(response.text, iso_date)
                    detail.update(parsed)
                    detail["result"] = (
                        "verified_storage_candidate"
                        if parsed["accepted"]
                        else parsed["reason"]
                    )
                    if parsed["accepted"]:
                        candidate = candidate_dir / f"{iso_date}.html"
                        candidate.write_bytes(response.content)
                        detail["candidate_path"] = str(candidate)
                        accepted = detail
                attempts.append(detail)
                if accepted:
                    break
            except RequestException as exc:
                detail.update({
                    "result": "request_failed",
                    "exception_type": type(exc).__name__,
                    "detail": str(exc)[:400],
                })
                attempts.append(detail)
            if pause_seconds:
                time.sleep(pause_seconds)
        return {
            "requested_date": iso_date,
            "status": "storage_candidate_only" if accepted else "not_recovered",
            "accepted_attempt": accepted,
            "attempts": attempts,
        }

    records = []
    for date in dates:
        records.append(attempt_one(date))
        if pause_seconds:
            time.sleep(pause_seconds)

    control = attempt_one(control_date)
    report = {
        "classification": "PRIMARY_SOURCE_STORAGE_RETRIEVAL_ATTEMPT_NOT_VALIDATED_DATASET",
        "source": "Kerala SLDC public historical Storage form",
        "source_url": STORAGE_URL,
        "requested_dates": dates,
        "recovered_storage_candidates": sum(
            row["status"] == "storage_candidate_only"
            for row in records
        ),
        "not_recovered": sum(
            row["status"] == "not_recovered"
            for row in records
        ),
        "known_observed_control_date": control_date,
        "known_observed_control_status": control["status"],
        "known_observed_control_attempts": control["attempts"],
        "original_archive_updated": False,
        "v1_4_strict_gate_changed": False,
        "records": records,
    }
    (output / "attempts.json").write_text(
        json.dumps(report, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    return report
