"""Acquire the twelve official KSEB FY2024-25 monthly reservoir workbooks."""
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

import requests

from kerala2040.kseb_monthly_bundle_v1_5 import audit_bundle, detect_format, sha256

UA = "Mozilla/5.0 (compatible; Kerala2040-research/1.5)"
DEFAULT_INVENTORY = (
    "data/evidence/hydro/"
    "kseb_monthly_inventory_fy2024_25_v1_5_2026_09_26.json"
)
DEFAULT_REFERER = "https://dams.kseb.in/?p=329"


def _load_inventory(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    months = data.get("required_months")
    if not isinstance(months, list) or len(months) != 12:
        raise ValueError("KSEB monthly inventory must contain exactly 12 months")
    return data


def _download_one(
    item: dict[str, Any],
    *,
    dest: Path,
    timeout: tuple[float, float],
    attempts: int,
) -> dict[str, Any]:
    expected = str(item["format"]).lower()
    urls = [
        str(item["derived_short_download_url"]),
        str(item["official_package_url"]),
    ]
    errors: list[str] = []

    session = requests.Session()
    session.headers.update(
        {
            "User-Agent": UA,
            "Referer": DEFAULT_REFERER,
            "Accept": "*/*",
        }
    )

    for attempt in range(1, attempts + 1):
        for url in urls:
            part = dest.with_suffix(dest.suffix + ".part")
            try:
                with session.get(
                    url,
                    timeout=timeout,
                    allow_redirects=True,
                    stream=True,
                ) as response:
                    response.raise_for_status()
                    part.parent.mkdir(parents=True, exist_ok=True)
                    with part.open("wb") as handle:
                        for chunk in response.iter_content(chunk_size=1024 * 1024):
                            if chunk:
                                handle.write(chunk)

                    if part.stat().st_size == 0:
                        raise ValueError("empty response body")
                    detected = detect_format(part)
                    if detected != expected:
                        prefix = part.read_bytes()[:120]
                        raise ValueError(
                            "download is not the expected workbook format: "
                            f"expected={expected} detected={detected} "
                            f"content_type={response.headers.get('Content-Type')} "
                            f"prefix={prefix!r}"
                        )

                    part.replace(dest)
                    listed_bytes = float(item["listed_size_kb"]) * 1024.0
                    size_ratio = dest.stat().st_size / listed_bytes
                    return {
                        "month": item["month"],
                        "status": "downloaded",
                        "wpdmdl": int(item["wpdmdl"]),
                        "source_url": url,
                        "final_url": response.url,
                        "path": dest.name,
                        "expected_format": expected,
                        "detected_format": detected,
                        "size_bytes": dest.stat().st_size,
                        "listed_size_kb": float(item["listed_size_kb"]),
                        "listed_size_ratio": size_ratio,
                        "sha256": sha256(dest),
                        "content_type": response.headers.get("Content-Type"),
                        "content_disposition": response.headers.get(
                            "Content-Disposition"
                        ),
                        "attempt": attempt,
                    }
            except (requests.RequestException, OSError, ValueError) as exc:
                part.unlink(missing_ok=True)
                errors.append(
                    f"attempt={attempt} url={url}: "
                    f"{type(exc).__name__}: {exc}"
                )
        if attempt < attempts:
            time.sleep(min(2 ** (attempt - 1), 8))

    return {
        "month": item["month"],
        "status": "failed",
        "wpdmdl": int(item["wpdmdl"]),
        "expected_format": expected,
        "errors": errors,
    }


def acquire(
    inventory_path: Path,
    out_dir: Path,
    *,
    attempts: int = 3,
    connect_timeout: float = 15.0,
    read_timeout: float = 120.0,
) -> dict[str, Any]:
    inventory = _load_inventory(inventory_path)
    results = []

    for item in inventory["required_months"]:
        month = str(item["month"])
        fmt = str(item["format"]).lower()
        dest = out_dir / f"{month}.{fmt}"

        if dest.is_file():
            detected = detect_format(dest)
            if detected == fmt:
                results.append(
                    {
                        "month": month,
                        "status": "already_present",
                        "wpdmdl": int(item["wpdmdl"]),
                        "path": dest.name,
                        "expected_format": fmt,
                        "detected_format": detected,
                        "size_bytes": dest.stat().st_size,
                        "sha256": sha256(dest),
                    }
                )
                continue

        results.append(
            _download_one(
                item,
                dest=dest,
                timeout=(connect_timeout, read_timeout),
                attempts=attempts,
            )
        )

    out_dir.mkdir(parents=True, exist_ok=True)
    gate = audit_bundle(out_dir)
    return {
        "classification": "KSEB_MONTHLY_OFFICIAL_ACQUISITION_V1_5",
        "inventory_path": str(inventory_path),
        "results": results,
        "downloaded_or_present": sum(
            item["status"] in {"downloaded", "already_present"} for item in results
        ),
        "failed": sum(item["status"] == "failed" for item in results),
        "bundle_gate": gate,
        "ready_for_content_schema_audit": gate["ready_for_content_schema_audit"],
    }
