"""No realistic-looking fake telemetry is ever committed as observed data.

The generated 1 MW/hour-like fixtures exist only in tests and are synthetic.
"""
from __future__ import annotations

import csv
import hashlib
import json
from datetime import datetime, timedelta, timezone

import pytest

from kerala2040.interval_admission import (
    IntervalAdmissionError,
    inspect_interval_candidate,
)

IST = timezone(timedelta(hours=5, minutes=30))


def candidate(tmp_path, minutes=60, mutate=None, meta_change=None):
    """Produce a synthetic test-only full-FY fixture with a source-bound hash."""
    csv_path = tmp_path / "synthetic_interval_test_only.csv"
    metadata_path = tmp_path / "synthetic_manifest_test_only.json"
    first = datetime(2024, 4, 1, tzinfo=IST)
    count = 365 * 1440 // minutes
    rows = [
        [(first + timedelta(minutes=i * minutes)).isoformat(), "3500", "-125"]
        for i in range(count)
    ]
    if mutate:
        mutate(rows)
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(("timestamp_ist", "demand_mw", "actual_net_import_mw"))
        writer.writerows(rows)
    metadata = {
        "classification": "observed",
        "source_type": "kerala_sldc",
        "source_url": "https://sldckerala.com/example-export.csv",
        "source_sha256": hashlib.sha256(csv_path.read_bytes()).hexdigest(),
        "obtained_at_utc": "2026-09-21T00:00:00Z",
        "original_filename": "example-export.csv",
        "revision_id": "test_source_v1",
        "interval_minutes": minutes,
        "timestamp_semantics": "interval_start",
        "timezone": "Asia/Kolkata",
        "demand_scope": "kerala_state_demand_met_mw",
        "interchange_scope": "kerala_actual_net_interchange_mw",
        "interchange_sign_convention": "positive_import_negative_export",
        "reuse_terms": "test fixture only, not operational data",
    }
    if meta_change:
        meta_change(metadata)
    metadata_path.write_text(json.dumps(metadata), encoding="utf-8")
    return csv_path, metadata_path


@pytest.mark.parametrize("minutes, count", [(60, 8760), (15, 35040)])
def test_exact_ist_fy_and_energy_integration_are_structurally_checked(tmp_path, minutes, count):
    csv_path, manifest = candidate(tmp_path, minutes=minutes)
    report = inspect_interval_candidate(csv_path, manifest)
    assert report["observed_intervals"] == count
    assert report["expected_intervals"] == count
    assert report["days_present"] == 365
    assert report["daily_aggregates"][0]["date"] == "2024-04-01"
    assert report["daily_aggregates"][-1]["date"] == "2025-03-31"
    assert report["daily_aggregates"][0]["intervals"] == 1440 // minutes
    assert report["demand_energy_twh"] == 30.66
    assert report["actual_net_import_energy_twh"] == -1.095
    assert report["scientific_gate_passed"] is False
    assert report["model_ready"] is False
    assert report["republication_approved"] is False
    assert "candidate" in report["classification"]


@pytest.mark.parametrize("mutate, reason", [
    (lambda r: r.pop(100), "missing, unsorted or misaligned"),
    (lambda r: r.insert(100, r[99].copy()), "duplicate, missing, unsorted"),
    (lambda r: r[50].__setitem__(0, "2024-04-03T00:00:00+00:00"), "include \\+05:30"),
    (lambda r: r[30].__setitem__(1, ""), "blank demand"),
    (lambda r: r[30].__setitem__(1, "nan"), "nonfinite demand"),
    (lambda r: r[30].__setitem__(1, "-1"), "nonpositive actual demand"),
    (lambda r: r[31].__setitem__(2, "inf"), "nonfinite actual_net_import"),
])
def test_bad_chronology_and_non_measurements_fail_closed(tmp_path, mutate, reason):
    csv_path, manifest = candidate(tmp_path, mutate=mutate)
    with pytest.raises(IntervalAdmissionError, match=reason):
        inspect_interval_candidate(csv_path, manifest)


@pytest.mark.parametrize("change, reason", [
    (lambda m: m.update(classification="proxy"), "must be declared observed"),
    (lambda m: m.update(source_type="srpc_dsm"), "not a state-load export"),
    (lambda m: m.update(demand_scope="scheduled_import_mw"), "actual met Kerala"),
    (lambda m: m.update(interchange_scope="scheduled_drawal_mw"), "actual metered net MW"),
    (lambda m: m.update(interchange_sign_convention="unknown"), "signs must be explicit"),
    (lambda m: m.update(timestamp_semantics="interval_end"), "interval-start"),
    (lambda m: m.update(timezone="UTC"), "interval-start"),
    (lambda m: m.update(interval_minutes=30), "15-minute or hourly"),
    (lambda m: m.update(reuse_terms="unknown"), "explicit reuse terms"),
    (lambda m: m.update(source_url="http://example.test"), "HTTPS"),
    (lambda m: m.update(source_sha256="0" * 64), "does not match"),
])
def test_source_metadata_cannot_self_promote_proxy_or_schedules(
    tmp_path, change, reason
):
    csv_path, manifest = candidate(tmp_path, meta_change=change)
    with pytest.raises(IntervalAdmissionError, match=reason):
        inspect_interval_candidate(csv_path, manifest)


def test_tamper_after_manifest_creation_fails_source_hash(tmp_path):
    csv_path, manifest = candidate(tmp_path)
    with csv_path.open("a", encoding="utf-8") as handle:
        handle.write("tampered after hashing\\n")
    with pytest.raises(IntervalAdmissionError, match="does not match"):
        inspect_interval_candidate(csv_path, manifest)


def test_empty_source_does_not_become_zero(tmp_path):
    csv_path, manifest = candidate(tmp_path, mutate=lambda r: r.clear())
    with pytest.raises(IntervalAdmissionError, match="first interval|incomplete FY"):
        inspect_interval_candidate(csv_path, manifest)
