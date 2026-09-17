"""NASA POWER hourly point-data adapter."""

from __future__ import annotations

from collections.abc import Iterable
from datetime import date
from typing import Any

import numpy as np
import pandas as pd
from requests import Session

from kerala2040.provenance import sha256_bytes, utc_now_iso
from kerala2040.sources.http import build_session, checked

ENDPOINT = "https://power.larc.nasa.gov/api/temporal/hourly/point"
DEFAULT_PARAMETERS = (
    "T2M",
    "RH2M",
    "ALLSKY_SFC_SW_DWN",
    "WS10M",
    "PRECTOTCORR",
)
COLUMN_MAP = {
    "T2M": "temp_c",
    "RH2M": "rh_pct",
    "ALLSKY_SFC_SW_DWN": "ghi_wh_m2",
    "WS10M": "wind10_m_s",
    "PRECTOTCORR": "precip_mm_h",
}


def parse_hourly_payload(payload: dict[str, Any]) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Convert a POWER JSON payload to UTC and Asia/Kolkata timestamps."""
    header = payload.get("header", {})
    fill_value = header.get("fill_value", -999.0)
    parameters = payload.get("properties", {}).get("parameter", {})
    if not parameters:
        raise ValueError("NASA POWER response contained no parameter data")

    timestamps = sorted({stamp for series in parameters.values() for stamp in series})
    index = pd.to_datetime(timestamps, format="%Y%m%d%H", utc=True)
    frame = pd.DataFrame({"timestamp_utc": index})
    frame["timestamp_ist"] = frame["timestamp_utc"].dt.tz_convert("Asia/Kolkata")

    for source_name, series in parameters.items():
        target_name = COLUMN_MAP.get(source_name, source_name.lower())
        values = pd.Series([series.get(stamp, np.nan) for stamp in timestamps], dtype="float64")
        frame[target_name] = values.replace(float(fill_value), np.nan)

    metadata = {
        "title": header.get("title"),
        "api": header.get("api"),
        "sources": header.get("sources", []),
        "fill_value": fill_value,
        "time_standard": header.get("time_standard"),
        "start": header.get("start"),
        "end": header.get("end"),
        "parameters": payload.get("parameters", {}),
    }
    return frame, metadata


def fetch_hourly_point(
    *,
    latitude: float,
    longitude: float,
    start: date,
    end: date,
    parameters: Iterable[str] = DEFAULT_PARAMETERS,
    community: str = "RE",
    session: Session | None = None,
    timeout: float = 60.0,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Fetch hourly NASA POWER data with explicit UTC timestamps."""
    selected = tuple(dict.fromkeys(parameters))
    if not 1 <= len(selected) <= 15:
        raise ValueError("NASA POWER hourly requests support 1 to 15 parameters")
    if end < start:
        raise ValueError("end must be on or after start")

    own_session = session is None
    session = session or build_session()
    query = {
        "parameters": ",".join(selected),
        "community": community,
        "longitude": longitude,
        "latitude": latitude,
        "start": start.strftime("%Y%m%d"),
        "end": end.strftime("%Y%m%d"),
        "format": "JSON",
        "time-standard": "UTC",
    }
    try:
        response = checked(session.get(ENDPOINT, params=query, timeout=timeout))
        payload = response.json()
        frame, metadata = parse_hourly_payload(payload)
        metadata["provenance"] = {
            "source_id": "nasa_power_hourly",
            "source_url": response.url,
            "retrieved_at_utc": utc_now_iso(),
            "http_status": response.status_code,
            "sha256": sha256_bytes(response.content),
            "content_type": response.headers.get("Content-Type"),
            "latitude": latitude,
            "longitude": longitude,
        }
        return frame, metadata
    finally:
        if own_session:
            session.close()
