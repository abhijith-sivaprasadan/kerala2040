"""Load checksummed compact hourly demand proxies without relabelling them measured.

The ERA5-sensitive FY2024-25 proxy is stored as split base64(zlib(JSON)) text so
the public repository can retain a small derived chronology without committing
raw ERA5 GRIB or detailed weather-hour rows. Every layer is SHA-256 checked
before expanding the compact 8,760-value array into the record structure used
by the chronological PyPSA screening.
"""

from __future__ import annotations

import base64
import hashlib
import json
import math
import zlib
from pathlib import Path
from typing import Any

import pandas as pd

EXPECTED_CLASS = "proxy_reconstruction_not_measured_telemetry"
PAYLOAD_ENCODING = "zlib_base64_parts_v1"
COMPACT_ENCODING = "compact_hourly_array_v1"


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _read_manifest_payload(path: Path, manifest: dict[str, Any]) -> dict[str, Any]:
    if manifest.get("classification") != EXPECTED_CLASS:
        raise ValueError("Hourly proxy classification mismatch")
    if manifest.get("encoding") != PAYLOAD_ENCODING:
        raise ValueError("Unsupported hourly proxy manifest encoding")
    parts = manifest.get("parts")
    if not isinstance(parts, list) or not parts:
        raise ValueError("Hourly proxy manifest has no payload parts")

    names: set[str] = set()
    pieces: list[str] = []
    for part in parts:
        name = str(part.get("file", ""))
        if (
            not name
            or "/" in name
            or "\\" in name
            or name in names
            or Path(name).name != name
        ):
            raise ValueError("Unsafe or duplicate hourly proxy part path")
        names.add(name)
        raw = (path.parent / name).read_bytes()
        try:
            text = raw.decode("ascii")
        except UnicodeDecodeError as exc:
            raise ValueError("Hourly proxy part is not ASCII base64") from exc
        if len(text) != int(part["chars"]) or _sha256(raw) != str(part["sha256"]):
            raise ValueError(f"Hourly proxy part integrity mismatch: {name}")
        pieces.append(text)

    payload = "".join(pieces)
    if (
        len(payload) != int(manifest["payload_chars"])
        or _sha256(payload.encode("ascii")) != str(manifest["payload_text_sha256"])
    ):
        raise ValueError("Hourly proxy payload text integrity mismatch")

    try:
        compressed = base64.b64decode(payload, validate=True)
    except ValueError as exc:
        raise ValueError("Hourly proxy payload is invalid base64") from exc
    if _sha256(compressed) != str(manifest["compressed_sha256"]):
        raise ValueError("Hourly proxy compressed payload integrity mismatch")

    try:
        raw_json = zlib.decompress(compressed)
    except zlib.error as exc:
        raise ValueError("Hourly proxy zlib payload is invalid") from exc
    if (
        len(raw_json) != int(manifest["decompressed_json_bytes"])
        or _sha256(raw_json) != str(manifest["decompressed_json_sha256"])
    ):
        raise ValueError("Hourly proxy JSON integrity mismatch")

    proxy = json.loads(raw_json)
    if proxy.get("classification") != EXPECTED_CLASS:
        raise ValueError("Decoded hourly proxy classification mismatch")
    if proxy.get("encoding") != COMPACT_ENCODING:
        raise ValueError("Decoded hourly proxy encoding mismatch")
    if proxy.get("profile_variant") != manifest.get("profile_variant"):
        raise ValueError("Hourly proxy profile variant mismatch")
    return proxy


def _expand_compact(proxy: dict[str, Any]) -> dict[str, Any]:
    values = proxy.get("load_mw")
    hours = int(proxy.get("hours", -1))
    if not isinstance(values, list) or len(values) != hours or hours != 8760:
        raise ValueError("Compact hourly proxy must contain exactly 8,760 load values")
    if any(
        not isinstance(value, (int, float))
        or not math.isfinite(float(value))
        or float(value) <= 0
        for value in values
    ):
        raise ValueError("Compact hourly proxy contains invalid load values")
    if proxy.get("timezone") != "Asia/Kolkata" or proxy.get("interval") != "1h":
        raise ValueError("Compact hourly proxy has unexpected timezone or interval")
    if proxy.get("record_classification") != "proxy_reconstruction":
        raise ValueError("Compact hourly proxy records cannot be labelled measured")

    start = pd.Timestamp(str(proxy.get("start", "")))
    if start.tzinfo is None:
        raise ValueError("Compact hourly proxy start timestamp must be timezone-aware")
    if start.tz_convert("Asia/Kolkata").strftime("%Y-%m-%d %H:%M") != "2024-04-01 00:00":
        raise ValueError("Compact hourly proxy has incorrect FY start")
    times = pd.date_range(start=start, periods=hours, freq="h")
    if times[-1].tz_convert("Asia/Kolkata").strftime("%Y-%m-%d %H:%M") != "2025-03-31 23:00":
        raise ValueError("Compact hourly proxy has incorrect FY end")

    imputed = proxy.get("daily_energy_imputed_dates")
    if not isinstance(imputed, list) or len(imputed) != 11 or len(set(imputed)) != 11:
        raise ValueError("Compact hourly proxy must retain the 11 model-only daily gaps")
    imputed_set = set(str(value) for value in imputed)

    records = []
    for timestamp, load_mw in zip(times, values, strict=True):
        date = timestamp.tz_convert("Asia/Kolkata").strftime("%Y-%m-%d")
        records.append(
            {
                "timestamp": timestamp.isoformat(),
                "load_mw": float(load_mw),
                "daily_energy_imputed": date in imputed_set,
                "classification": "proxy_reconstruction",
            }
        )
    return {**proxy, "records": records}


def load_hourly_proxy(path: Path) -> dict[str, Any]:
    """Load either the legacy record JSON or checksummed compact manifest."""
    obj = json.loads(path.read_text(encoding="utf-8"))
    if "records" in obj:
        if obj.get("classification") != EXPECTED_CLASS:
            raise ValueError("Hourly proxy must retain not-measured classification")
        return obj
    proxy = _read_manifest_payload(path, obj)
    return _expand_compact(proxy)
