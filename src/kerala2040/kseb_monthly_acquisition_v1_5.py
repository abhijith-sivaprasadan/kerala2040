"""Acquire the twelve official KSEB FY2024-25 monthly reservoir workbooks.

The KSEB Dam Safety WordPress Download Manager package IDs are source metadata
captured from the official monthly-statistics listing. Downloads are accepted
only when their binary container matches the listing's XLS/XLSX icon and the
result is byte-fingerprinted.

This module does not parse or admit reservoir values.
"""
from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import requests

from kerala2040.kseb_monthly_bundle_v1_5 import audit_bundle

BASE_URL = "https://dams.kseb.in/"


@dataclass(frozen=True)
class MonthlyPackage:
    month: str
    package_id: int
    expected_format: str
    listed_size_kb: float
    title: str
    published_date: str

    @property
    def url(self) -> str:
        return f"{BASE_URL}?wpdmdl={self.package_id}"


PACKAGES = (
    MonthlyPackage("2024-04", 4421, "xlsx", 367.56, "Water Level of main reservoirs of KSEB Limited during April 2024", "2024-04-30"),
    MonthlyPackage("2024-05", 4488, "xlsx", 498.72, "Water level of main reservoirs of KSEB Limited during May 2024", "2024-05-31"),
    MonthlyPackage("2024-06", 4570, "xls", 419.50, "Water Level of main reservoirs of KSEB Limited during June 2024", "2024-07-02"),
    MonthlyPackage("2024-07", 4668, "xls", 528.50, "Water Level of main reservoirs of KSEB Limited during July 2024", "2024-07-31"),
    MonthlyPackage("2024-08", 4742, "xlsx", 533.27, "Water Level of main reservoirs of KSEB Limited during August 2024", "2024-08-31"),
    MonthlyPackage("2024-09", 4806, "xls", 529.50, "Water Level of main reservoirs of KSEB Limited during September 2024", "2024-09-30"),
    MonthlyPackage("2024-10", 4874, "xls", 533.00, "Water Level of main reservoirs of KSEB Limited during October 2024", "2024-11-01"),
    MonthlyPackage("2024-11", 4940, "xlsx", 516.13, "Water Level of main reservoirs of KSEB Limited during November 2024", "2024-12-02"),
    MonthlyPackage("2024-12", 5012, "xlsx", 601.74, "Water Level of main reservoirs of KSEB Limited during December 2024", "2024-12-31"),
    MonthlyPackage("2025-01", 5081, "xls", 542.50, "Water Level of main reservoirs of KSEB Ltd during January 2025", "2025-01-31"),
    MonthlyPackage("2025-02", 5143, "xls", 398.50, "Water Level of main reservoir of KSEB Limited during February 2025", "2025-03-03"),
    MonthlyPackage("2025-03", 5212, "xlsx", 451.41, "Water level of main reservoirs of KSEB Limited during March 2025", "2025-04-04"),
)

OLE_MAGIC = bytes.fromhex("D0CF11E0A1B11AE1")
ZIP_MAGIC = b"PK\x03\x04"


class KSEBMonthlyAcquisitionError(RuntimeError):
    """Raised when an official monthly workbook cannot be acquired safely."""


def sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def detect_excel_container(content: bytes) -> str:
    if content.startswith(OLE_MAGIC):
        return "xls"
    if content.startswith(ZIP_MAGIC):
        return "xlsx"
    if content.lstrip().lower().startswith((b"<!doctype html", b"<html")):
        return "html"
    return "unknown"


def content_disposition_filename(value: str | None) -> str | None:
    if not value:
        return None
    match = re.search(
        r"filename\*?=(?:UTF-8''|\")?([^\";]+)",
        value,
        flags=re.IGNORECASE,
    )
    return match.group(1).strip() if match else None


def package_by_month(month: str) -> MonthlyPackage:
    for package in PACKAGES:
        if package.month == month:
            return package
    raise KeyError(month)


def download_package(
    package: MonthlyPackage,
    *,
    session: requests.Session,
    timeout: tuple[float, float] = (20.0, 120.0),
) -> tuple[bytes, dict[str, object]]:
    response = session.get(
        package.url,
        headers={"User-Agent": "Mozilla/5.0 (kerala2040 research acquisition)"},
        allow_redirects=True,
        timeout=timeout,
    )
    response.raise_for_status()
    content = response.content
    if len(content) < 10_000:
        raise KSEBMonthlyAcquisitionError(
            f"{package.month}: implausibly small response ({len(content)} bytes)"
        )
    detected = detect_excel_container(content)
    if detected != package.expected_format:
        raise KSEBMonthlyAcquisitionError(
            f"{package.month}: expected {package.expected_format}, got {detected}"
        )
    meta = {
        "month": package.month,
        "package_id": package.package_id,
        "source_url": package.url,
        "final_url": response.url,
        "expected_format": package.expected_format,
        "detected_format": detected,
        "listed_size_kb": package.listed_size_kb,
        "downloaded_size_bytes": len(content),
        "sha256": sha256_bytes(content),
        "content_type": response.headers.get("Content-Type"),
        "content_disposition": response.headers.get("Content-Disposition"),
        "source_filename": content_disposition_filename(
            response.headers.get("Content-Disposition")
        ),
        "title": package.title,
        "published_date": package.published_date,
    }
    return content, meta


def acquire_bundle(
    output_dir: Path,
    *,
    months: Iterable[str] | None = None,
    session: requests.Session | None = None,
) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)
    wanted = set(months) if months is not None else {p.month for p in PACKAGES}
    unknown = wanted - {p.month for p in PACKAGES}
    if unknown:
        raise KSEBMonthlyAcquisitionError(
            f"Unknown requested month(s): {sorted(unknown)}"
        )

    own_session = session is None
    session = session or requests.Session()
    records: list[dict[str, object]] = []
    try:
        for package in PACKAGES:
            if package.month not in wanted:
                continue
            content, meta = download_package(package, session=session)
            path = output_dir / f"{package.month}.{package.expected_format}"
            part = path.with_suffix(path.suffix + ".part")
            part.write_bytes(content)
            part.replace(path)
            meta["path"] = path.name
            records.append(meta)
    finally:
        if own_session:
            session.close()

    acquisition = {
        "classification": "OFFICIAL_KSEB_MONTHLY_WORKBOOK_ACQUISITION_V1_5",
        "source": "KSEB Ltd Dam Safety Organisation",
        "records": records,
        "requested_months": sorted(wanted),
        "downloaded_months": [r["month"] for r in records],
        "complete_fy2024_25": len(records) == len(PACKAGES),
        "model_input_ready": False,
    }
    (output_dir / "acquisition_manifest.json").write_text(
        json.dumps(acquisition, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    if acquisition["complete_fy2024_25"]:
        bundle_gate = audit_bundle(output_dir)
        acquisition["bundle_gate"] = bundle_gate
        if not bundle_gate["ready_for_content_schema_audit"]:
            raise KSEBMonthlyAcquisitionError(
                "Downloaded all packages but bundle gate did not pass"
            )
        (output_dir / "acquisition_manifest.json").write_text(
            json.dumps(acquisition, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    return acquisition
