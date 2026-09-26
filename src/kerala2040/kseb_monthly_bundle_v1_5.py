"""Fail-closed audit for the official KSEB FY2024-25 monthly reservoir bundle.

This module does not parse reservoir values. It proves that the twelve monthly
files required for the next v1.5 schema audit are present, uniquely mapped to
months, and byte-fingerprinted. Content admission happens only after a separate
header/schema audit of the actual files.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

EXPECTED_MONTHS = tuple(
    [f"2024-{month:02d}" for month in range(4, 13)]
    + [f"2025-{month:02d}" for month in range(1, 4)]
)

MONTH_NAMES = {
    1: "january",
    2: "february",
    3: "march",
    4: "april",
    5: "may",
    6: "june",
    7: "july",
    8: "august",
    9: "september",
    10: "october",
    11: "november",
    12: "december",
}
MONTH_LOOKUP = {name: number for number, name in MONTH_NAMES.items()}

SUPPORTED_FORMATS = {"pdf", "xlsx", "xls", "csv", "text", "zip"}
EXPECTED_FORMATS = {
    "2024-04": "xlsx",
    "2024-05": "xlsx",
    "2024-06": "xls",
    "2024-07": "xls",
    "2024-08": "xlsx",
    "2024-09": "xls",
    "2024-10": "xls",
    "2024-11": "xlsx",
    "2024-12": "xlsx",
    "2025-01": "xls",
    "2025-02": "xls",
    "2025-03": "xlsx",
}


class KSEBMonthlyBundleError(ValueError):
    """Raised when the monthly file bundle is ambiguous or incomplete."""


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def detect_format(path: Path) -> str:
    with path.open("rb") as handle:
        head = handle.read(16)

    if head.startswith(b"%PDF-"):
        return "pdf"
    if head.startswith(b"PK\x03\x04"):
        if path.suffix.lower() == ".xlsx":
            return "xlsx"
        return "zip"
    if head.startswith(bytes.fromhex("D0CF11E0A1B11AE1")):
        return "xls"

    if path.suffix.lower() == ".csv":
        return "csv"

    try:
        sample = path.read_text(encoding="utf-8")[:4096]
    except UnicodeDecodeError:
        return "unknown"
    if sample:
        return "text"
    return "unknown"


def month_from_filename(path: Path) -> str | None:
    name = re.sub(r"[^a-z0-9]+", " ", path.name.lower())
    year_match = re.search(r"\b(2024|2025)\b", name)
    if not year_match:
        return None
    year = int(year_match.group(1))

    month_hits = [
        number
        for month_name, number in MONTH_LOOKUP.items()
        if re.search(rf"\b{month_name}\b", name)
    ]
    if len(month_hits) != 1:
        return None
    value = f"{year}-{month_hits[0]:02d}"
    return value if value in EXPECTED_MONTHS else None


def load_explicit_manifest(path: Path, root: Path) -> dict[str, Path]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    entries = raw.get("files", raw) if isinstance(raw, dict) else raw
    if not isinstance(entries, list):
        raise KSEBMonthlyBundleError("Manifest must contain a list of files")

    mapped: dict[str, Path] = {}
    for entry in entries:
        if not isinstance(entry, dict):
            raise KSEBMonthlyBundleError("Every manifest entry must be an object")
        month = str(entry.get("month", ""))
        rel = entry.get("path")
        if month not in EXPECTED_MONTHS or not isinstance(rel, str) or not rel:
            raise KSEBMonthlyBundleError(f"Invalid manifest entry: {entry!r}")
        if month in mapped:
            raise KSEBMonthlyBundleError(f"Duplicate manifest month: {month}")
        candidate = (root / rel).resolve()
        try:
            candidate.relative_to(root.resolve())
        except ValueError as exc:
            raise KSEBMonthlyBundleError(
                f"Manifest path escapes bundle root: {rel}"
            ) from exc
        mapped[month] = candidate
    return mapped


def discover_bundle(root: Path) -> tuple[dict[str, Path], dict[str, list[str]]]:
    candidates: dict[str, list[Path]] = {month: [] for month in EXPECTED_MONTHS}
    ignored: list[str] = []

    for path in sorted(p for p in root.rglob("*") if p.is_file()):
        month = month_from_filename(path)
        if month is None:
            ignored.append(str(path.relative_to(root)))
            continue
        candidates[month].append(path)

    duplicates = {
        month: [str(path.relative_to(root)) for path in paths]
        for month, paths in candidates.items()
        if len(paths) > 1
    }
    mapped = {
        month: paths[0]
        for month, paths in candidates.items()
        if len(paths) == 1
    }
    return mapped, {"duplicates": duplicates, "ignored": ignored}


def audit_bundle(
    root: Path,
    *,
    manifest: Path | None = None,
) -> dict[str, Any]:
    root = root.resolve()
    if not root.is_dir():
        raise KSEBMonthlyBundleError(f"Bundle directory does not exist: {root}")

    if manifest:
        mapped = load_explicit_manifest(manifest.resolve(), root)
        discovery = {"duplicates": {}, "ignored": []}
        mapping_mode = "explicit_manifest"
    else:
        mapped, discovery = discover_bundle(root)
        mapping_mode = "filename_month_discovery"

    records = []
    missing = []
    invalid = []

    for month in EXPECTED_MONTHS:
        path = mapped.get(month)
        if path is None:
            missing.append(month)
            continue
        if not path.is_file():
            invalid.append({"month": month, "reason": "file_missing", "path": str(path)})
            continue

        fmt = detect_format(path)
        record = {
            "month": month,
            "path": str(path.relative_to(root)),
            "size_bytes": path.stat().st_size,
            "sha256": sha256(path),
            "detected_format": fmt,
        }
        records.append(record)
        if fmt not in SUPPORTED_FORMATS:
            invalid.append(
                {
                    "month": month,
                    "reason": "unsupported_or_unknown_format",
                    "path": record["path"],
                    "detected_format": fmt,
                }
            )
        expected = EXPECTED_FORMATS[month]
        if fmt != expected:
            invalid.append(
                {
                    "month": month,
                    "reason": "format_mismatch_against_official_listing",
                    "path": record["path"],
                    "detected_format": fmt,
                    "expected_format": expected,
                }
            )

    duplicates = discovery["duplicates"]
    ready = not missing and not duplicates and not invalid and len(records) == 12

    return {
        "classification": "KSEB_MONTHLY_RESERVOIR_BUNDLE_GATE_V1_5",
        "mapping_mode": mapping_mode,
        "required_months": list(EXPECTED_MONTHS),
        "required_count": len(EXPECTED_MONTHS),
        "found_count": len(records),
        "records": records,
        "missing_months": missing,
        "duplicate_month_candidates": duplicates,
        "invalid_files": invalid,
        "ignored_files": discovery["ignored"],
        "ready_for_content_schema_audit": ready,
        "status": (
            "ready_for_content_schema_audit"
            if ready
            else "blocked_monthly_files_missing_ambiguous_or_invalid"
        ),
        "content_values_admitted": False,
        "model_input_ready": False,
    }
