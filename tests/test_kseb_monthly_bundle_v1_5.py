import json
from pathlib import Path

import pytest

from kerala2040.kseb_monthly_bundle_v1_5 import (
    EXPECTED_MONTHS,
    KSEBMonthlyBundleError,
    audit_bundle,
    detect_format,
    month_from_filename,
)


def test_month_from_filename():
    assert (
        month_from_filename(Path("Water Level reservoirs April 2024.pdf"))
        == "2024-04"
    )
    assert month_from_filename(Path("reservoir_March_2025.xlsx")) == "2025-03"
    assert month_from_filename(Path("March_2026.xlsx")) is None


def test_detect_formats(tmp_path: Path):
    pdf = tmp_path / "x.pdf"
    pdf.write_bytes(b"%PDF-1.7\n")
    assert detect_format(pdf) == "pdf"

    xls = tmp_path / "x.xls"
    xls.write_bytes(bytes.fromhex("D0CF11E0A1B11AE1") + b"x")
    assert detect_format(xls) == "xls"

    xlsx = tmp_path / "x.xlsx"
    xlsx.write_bytes(b"PK\x03\x04fake")
    assert detect_format(xlsx) == "xlsx"


def test_complete_auto_discovered_bundle_is_ready(tmp_path: Path):
    for month in EXPECTED_MONTHS:
        year, number = month.split("-")
        names = {
            "01": "January",
            "02": "February",
            "03": "March",
            "04": "April",
            "05": "May",
            "06": "June",
            "07": "July",
            "08": "August",
            "09": "September",
            "10": "October",
            "11": "November",
            "12": "December",
        }
        path = tmp_path / f"KSEB {names[number]} {year}.pdf"
        path.write_bytes(b"%PDF-1.7\n")
    result = audit_bundle(tmp_path)
    assert result["found_count"] == 12
    assert result["missing_months"] == []
    assert result["ready_for_content_schema_audit"] is True
    assert result["model_input_ready"] is False


def test_missing_month_fails_closed(tmp_path: Path):
    path = tmp_path / "KSEB April 2024.pdf"
    path.write_bytes(b"%PDF-1.7\n")
    result = audit_bundle(tmp_path)
    assert result["ready_for_content_schema_audit"] is False
    assert "2025-03" in result["missing_months"]


def test_explicit_manifest_rejects_escape(tmp_path: Path):
    manifest = tmp_path / "manifest.json"
    manifest.write_text(
        json.dumps([{"month": "2024-04", "path": "../outside.pdf"}]),
        encoding="utf-8",
    )
    with pytest.raises(KSEBMonthlyBundleError, match="escapes bundle root"):
        audit_bundle(tmp_path, manifest=manifest)
