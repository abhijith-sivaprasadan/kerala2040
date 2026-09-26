"""Fingerprint locally acquired official KSEB monthly reservoir files.

No source file format is assumed from the KSEB index. This gate identifies the
container from byte signatures, hashes the exact bytes, and binds each file to
the official FY2024-25 monthly inventory before any content parser is selected.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import zipfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INVENTORY = (
    ROOT
    / "data/evidence/hydro/"
    "kseb_monthly_reservoir_inventory_fy2024_25_2026_09_26.json"
)
MONTH_RE = re.compile(r"^20\d{2}-(?:0[1-9]|1[0-2])$")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def detect_file_type(path: Path) -> dict[str, Any]:
    head = path.read_bytes()[:8192]
    if head.startswith(b"%PDF-"):
        return {"family": "pdf", "confidence": "magic"}

    if head.startswith(bytes.fromhex("D0CF11E0A1B11AE1")):
        return {
            "family": "ole_compound",
            "confidence": "magic",
            "possible_formats": ["xls", "doc", "ppt", "other_ole"],
        }

    if head.startswith(b"PK\x03\x04"):
        try:
            with zipfile.ZipFile(path) as archive:
                names = set(archive.namelist())
        except zipfile.BadZipFile:
            return {"family": "corrupt_zip_signature", "confidence": "magic"}

        if "[Content_Types].xml" in names and any(
            name.startswith("xl/") for name in names
        ):
            return {"family": "xlsx", "confidence": "container_structure"}
        if "mimetype" in names:
            try:
                with zipfile.ZipFile(path) as archive:
                    mimetype = archive.read("mimetype").decode(
                        "ascii",
                        errors="replace",
                    )
            except (KeyError, OSError, zipfile.BadZipFile):
                mimetype = ""
            if "opendocument.spreadsheet" in mimetype:
                return {"family": "ods", "confidence": "container_structure"}
        return {"family": "zip", "confidence": "magic"}

    lowered = head.lstrip().lower()
    if lowered.startswith(b"<!doctype html") or lowered.startswith(b"<html"):
        return {"family": "html", "confidence": "content"}

    if b"\x00" not in head:
        try:
            text = head.decode("utf-8")
        except UnicodeDecodeError:
            text = ""
        if text:
            lines = [line for line in text.splitlines() if line.strip()]
            if len(lines) >= 2:
                if all("," in line for line in lines[: min(5, len(lines))]):
                    return {"family": "csv", "confidence": "content"}
                if all("\t" in line for line in lines[: min(5, len(lines))]):
                    return {"family": "tsv", "confidence": "content"}
            return {"family": "text", "confidence": "content"}

    return {"family": "unknown_binary", "confidence": "none"}


def parse_listed_size(value: str) -> float:
    match = re.fullmatch(r"\s*(\d+(?:\.\d+)?)\s*(KB|MB)\s*", value)
    if not match:
        raise ValueError(f"Unsupported listed size: {value!r}")
    amount = float(match.group(1))
    multiplier = 1024 if match.group(2) == "KB" else 1024 * 1024
    return amount * multiplier


def load_inventory(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("classification") != (
        "OFFICIAL_KSEB_MONTHLY_RESERVOIR_SOURCE_INVENTORY_"
        "FY2024_25_BYTES_NOT_YET_ACQUIRED"
    ):
        raise ValueError("Unexpected KSEB monthly inventory classification")
    months = data.get("months", [])
    if len(months) != 12:
        raise ValueError("KSEB FY2024-25 inventory must contain exactly 12 months")
    ids = [item["month"] for item in months]
    expected = [
        f"{year:04d}-{month:02d}"
        for year, month in (
            [(2024, m) for m in range(4, 13)]
            + [(2025, m) for m in range(1, 4)]
        )
    ]
    if ids != expected:
        raise ValueError("KSEB monthly inventory is not continuous FY2024-25")
    return data


def audit_file(month: str, path: Path, inventory_row: dict[str, Any]) -> dict[str, Any]:
    if not MONTH_RE.fullmatch(month):
        raise ValueError(f"Invalid YYYY-MM month: {month!r}")
    if not path.is_file():
        raise FileNotFoundError(path)

    observed_bytes = path.stat().st_size
    listed_bytes = parse_listed_size(inventory_row["listed_size"])
    return {
        "month": month,
        "source_inventory": inventory_row,
        "local_file": {
            "filename": path.name,
            "suffix": path.suffix.lower() or null_suffix(),
            "bytes": observed_bytes,
            "sha256": sha256(path),
            "detected_type": detect_file_type(path),
        },
        "listed_size_comparison": {
            "listed_size_text": inventory_row["listed_size"],
            "listed_size_binary_bytes_if_kib": listed_bytes,
            "observed_to_listed_ratio": (
                observed_bytes / listed_bytes if listed_bytes else None
            ),
            "binding_check": false_value(),
            "interpretation": (
                "KSEB's displayed size is rounded metadata only; it is not used "
                "as an identity or authenticity check."
            ),
        },
    }


def null_suffix() -> None:
    return None


def false_value() -> bool:
    return False


def parse_month_file(value: str) -> tuple[str, Path]:
    if "=" not in value:
        raise argparse.ArgumentTypeError("Expected YYYY-MM=/path/to/file")
    month, raw_path = value.split("=", 1)
    if not MONTH_RE.fullmatch(month):
        raise argparse.ArgumentTypeError(f"Invalid month: {month}")
    return month, Path(raw_path)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--month-file",
        action="append",
        type=parse_month_file,
        default=[],
        help="Repeatable YYYY-MM=/path/to/downloaded_file",
    )
    parser.add_argument("--inventory", type=Path, default=DEFAULT_INVENTORY)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()

    inventory = load_inventory(args.inventory)
    lookup = {item["month"]: item for item in inventory["months"]}

    seen: set[str] = set()
    records = []
    for month, path in args.month_file:
        if month in seen:
            raise SystemExit(f"Duplicate --month-file for {month}")
        seen.add(month)
        if month not in lookup:
            raise SystemExit(f"Month {month} is not in the official FY2024-25 inventory")
        records.append(audit_file(month, path, lookup[month]))

    result = {
        "classification": "KSEB_MONTHLY_LOCAL_FILE_FINGERPRINT_AUDIT_V1_5",
        "inventory_source": str(args.inventory),
        "files_supplied": len(records),
        "months_supplied": sorted(seen),
        "months_missing": [
            item["month"] for item in inventory["months"] if item["month"] not in seen
        ],
        "complete_12_month_byte_set": len(records) == 12,
        "records": records,
        "content_parser_selected": False,
        "reason_content_parser_not_selected": (
            "This stage fingerprints and identifies source containers only."
        ),
    }

    output = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(output, encoding="utf-8")
    print(output, end="")


if __name__ == "__main__":
    main()
