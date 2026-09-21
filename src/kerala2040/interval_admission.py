"""Fail-closed structural intake for source-supplied Kerala FY2024-25 interval data.

Passing these checks is NOT an independent source-authentication, publication
licence, metering-boundary reconciliation or chronological-model release gate.
No synthetic/proxy input can be promoted by this module.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

IST = timezone(timedelta(hours=5, minutes=30))
START = datetime(2024, 4, 1, tzinfo=IST)
END = datetime(2025, 4, 1, tzinfo=IST)
COLUMNS = ("timestamp_ist", "demand_mw", "actual_net_import_mw")
SOURCE_TYPES = {"kerala_sldc", "ksebl"}


class IntervalAdmissionError(ValueError):
    """A candidate failed mandatory provenance, chronology or values checks."""


def _require(ok: bool, message: str) -> None:
    if not ok:
        raise IntervalAdmissionError(message)


def _source_meta(metadata: dict[str, Any], actual_hash: str) -> int:
    mandatory = (
        "classification", "source_type", "source_url", "source_sha256",
        "obtained_at_utc", "original_filename", "revision_id",
        "interval_minutes", "timestamp_semantics", "timezone",
        "demand_scope", "interchange_scope", "interchange_sign_convention",
        "reuse_terms",
    )
    _require(all(metadata.get(key) not in (None, "") for key in mandatory),
             "source manifest lacks a required provenance or boundary field")
    _require(metadata["classification"] == "observed",
             "source input must be declared observed, never proxy or synthetic")
    _require(metadata["source_type"] in SOURCE_TYPES,
             "composite SRPC DSM, figure digitisation and unknown publishers are not a state-load export")
    uri = urlsplit(str(metadata["source_url"]))
    _require(uri.scheme == "https" and bool(uri.hostname) and not uri.username,
             "original source URL must be an HTTPS resource")
    _require(metadata["source_sha256"] == actual_hash,
             "source_sha256 does not match the exact input CSV bytes")
    _require(metadata["timezone"] == "Asia/Kolkata" and
             metadata["timestamp_semantics"] == "interval_start",
             "explicit IST interval-start timestamps are required")
    _require(metadata["interchange_sign_convention"] ==
             "positive_import_negative_export",
             "actual interchange import/export signs must be explicit")
    interval = metadata["interval_minutes"]
    _require(type(interval) is int and interval in (15, 60),
             "only 15-minute or hourly interval-average MW is accepted")
    _require(metadata["demand_scope"] == "kerala_state_demand_met_mw",
             "demand must be actual met Kerala state MW, not unrestricted or scheduled drawal")
    _require(metadata["interchange_scope"] == "kerala_actual_net_interchange_mw",
             "interchange must be actual metered net MW, not scheduled MW, prices or limits")
    _require(isinstance(metadata["reuse_terms"], str) and
             metadata["reuse_terms"].strip().lower() not in {"unknown", "none", "na"},
             "explicit reuse terms are required; data stay private by default")
    try:
        observed_time = datetime.fromisoformat(str(metadata["obtained_at_utc"]).replace("Z", "+00:00"))
    except ValueError as exc:
        raise IntervalAdmissionError("obtained_at_utc must be ISO 8601") from exc
    _require(observed_time.tzinfo is not None and
             observed_time.utcoffset() == timedelta(0),
             "obtained_at_utc must have UTC timezone")
    return interval


def _quantity(value: str, column: str, line: int) -> float:
    _require(value is not None and value.strip() != "",
             f"blank {column} at input line {line} cannot become zero")
    try:
        amount = float(value)
    except ValueError as exc:
        raise IntervalAdmissionError(
            f"non-numeric {column} at input line {line}"
        ) from exc
    _require(math.isfinite(amount), f"nonfinite {column} at input line {line}")
    if column == "demand_mw":
        _require(amount > 0, f"nonpositive actual demand at input line {line}")
    return amount


def inspect_interval_candidate(csv_file: Path, manifest_file: Path) -> dict[str, Any]:
    """Validate complete IST chronology, exact source hash, units and values.

    Returns a private, structurally-qualified report; never upgrades a scientific gate.
    """
    raw = csv_file.read_bytes()
    source_hash = hashlib.sha256(raw).hexdigest()
    metadata = json.loads(manifest_file.read_text(encoding="utf-8"))
    _require(isinstance(metadata, dict), "source manifest must be a JSON object")
    minutes = _source_meta(metadata, source_hash)
    expected = int((END - START) / timedelta(minutes=minutes))
    last: datetime | None = None
    first: datetime | None = None
    rows = 0
    demand_mwh = 0.0
    imports_mwh = 0.0
    by_date: dict[str, dict[str, float | int]] = {}
    with csv_file.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        _require(reader.fieldnames == list(COLUMNS),
                 f"input CSV must have exact headers: {', '.join(COLUMNS)}")
        for line, record in enumerate(reader, start=2):
            if None in record:
                raise IntervalAdmissionError(f"extra unheaded CSV field on input line {line}")
            try:
                stamp = datetime.fromisoformat(record["timestamp_ist"])
            except (ValueError, TypeError) as exc:
                raise IntervalAdmissionError(
                    f"invalid ISO 8601 timestamp at input line {line}"
                ) from exc
            _require(stamp.tzinfo is not None and stamp.utcoffset() == timedelta(hours=5, minutes=30),
                     f"timestamp must explicitly include +05:30 at input line {line}")
            _require(START <= stamp < END,
                     f"timestamp outside FY2024-25 at input line {line}")
            if last is None:
                _require(stamp == START, "first interval does not start on 2024-04-01 00:00 IST")
                first = stamp
            else:
                _require(stamp - last == timedelta(minutes=minutes),
                         f"duplicate, missing, unsorted or misaligned interval at input line {line}")
            demand = _quantity(record["demand_mw"], "demand_mw", line)
            imports = _quantity(record["actual_net_import_mw"], "actual_net_import_mw", line)
            energy_factor = minutes / 60
            demand_mwh += demand * energy_factor
            imports_mwh += imports * energy_factor
            key = stamp.date().isoformat()
            day = by_date.setdefault(key, {"intervals": 0, "demand_mu": 0.0,
                                            "actual_net_import_mu": 0.0})
            day["intervals"] += 1
            day["demand_mu"] += demand * energy_factor / 1000
            day["actual_net_import_mu"] += imports * energy_factor / 1000
            last = stamp
            rows += 1
    _require(rows == expected and last == END - timedelta(minutes=minutes),
             f"incomplete FY interval series: {rows}/{expected} source intervals")
    _require(len(by_date) == 365 and
             all(day["intervals"] == 1440 // minutes for day in by_date.values()),
             "missing or overfull local-IST day")
    return {
        "classification": "source_supplied_observed_candidate_structurally_checked",
        "scientific_gate_passed": False,
        "model_ready": False,
        "republication_approved": False,
        "report_scope": "private_source_admission_not_a_published_measured_baseline",
        "source_sha256": source_hash,
        "source_type": metadata["source_type"],
        "source_url": metadata["source_url"],
        "source_revision_id": metadata["revision_id"],
        "interval_minutes": minutes,
        "expected_intervals": expected,
        "observed_intervals": rows,
        "days_present": len(by_date),
        "first_timestamp_ist": first.isoformat() if first else None,
        "last_timestamp_ist": last.isoformat() if last else None,
        "demand_energy_twh": round(demand_mwh / 1_000_000, 7),
        "actual_net_import_energy_twh": round(imports_mwh / 1_000_000, 7),
        "reconciliation_required": [
            "verify agency data authenticity and source revisions independently",
            "reconcile metering/accounting boundaries with SLDC daily observations",
            "reconcile official annual energy and coincident peaks",
            "verify research-use and redistribution permission",
            "complete release-gate review using committed admissible evidence",
        ],
        "daily_aggregates": [
            {"date": key, **{
                field: round(value, 6) if isinstance(value, float) else value
                for field, value in day.items()
            }}
            for key, day in by_date.items()
        ],
    }
