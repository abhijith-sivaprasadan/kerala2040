"""Kerala SLDC public system-statistics adapter.

The public SLDC page is HTML, not a documented API. This module therefore keeps
the extraction deliberately narrow and preserves the raw labels. Historical
dates are requested through the date form exposed on the official page.
"""

from __future__ import annotations

import re
import time
from collections.abc import Iterator
from datetime import date, timedelta
from typing import Any

import pandas as pd
from bs4 import BeautifulSoup
from requests import Session

from kerala2040.provenance import sha256_bytes, utc_now_iso
from kerala2040.sources.http import build_session, checked

BASE_URL = "https://sldckerala.com/index.php"
SYSTEM_STATS_URL = f"{BASE_URL}?id=1"
STORAGE_URL = f"{BASE_URL}?id=7"

_DATE_RE = re.compile(
    r"SYSTEM\s+STATISTICS\s*-\s*FOR\s+(\d{1,2}/\d{1,2}/\d{4})",
    re.IGNORECASE,
)
_FLOAT_RE = re.compile(r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)")

# These are separate accounting concepts on the source page. Do not collapse them.
_METRIC_LABELS = {
    "hydel total": "hydel_total_mu",
    "thermal total": "thermal_total_mu",
    "ipp total": "ipp_total_mu",
    "internal generation": "internal_generation_mu",
    "net import": "net_import_interface_mu",
    "consumption": "consumption_mu",
    "import (mu)": "ui_import_mu",
    "export (mu)": "ui_export_mu",
    "net import (on ui) (mu)": "ui_net_import_mu",
    "cgs availability": "cgs_availability_mu",
    "adl share(+) / surrender(-)": "additional_share_surrender_mu",
    "sr / er loss": "sr_er_loss_mu",
    "interstate purch/sale(+/-ve)": "interstate_purchase_sale_mu",
    "net schedule": "net_schedule_mu",
}


def _clean(value: str) -> str:
    return " ".join(value.replace("\xa0", " ").split()).strip()


def _normalise_label(value: str) -> str:
    return _clean(value).lower()


def _first_number(cells: list[str]) -> float | None:
    for cell in cells:
        match = _FLOAT_RE.search(cell.replace(",", ""))
        if match:
            return float(match.group(0))
    return None


def parse_system_statistics(html: str) -> dict[str, Any]:
    """Parse a public SLDC system-statistics HTML response."""
    soup = BeautifulSoup(html, "lxml")
    page_text = _clean(soup.get_text(" ", strip=True))
    date_match = _DATE_RE.search(page_text)
    if not date_match:
        raise ValueError("SLDC response did not contain a system-statistics date")
    day, month, year = (int(part) for part in date_match.group(1).split("/"))
    report_date = date(year, month, day)

    metrics: dict[str, float] = {}
    raw_rows: list[dict[str, Any]] = []

    for tr in soup.find_all("tr"):
        cells = [_clean(cell.get_text(" ", strip=True)) for cell in tr.find_all(["td", "th"])]
        if not cells or not cells[0]:
            continue
        label = cells[0]
        value = _first_number(cells[1:])
        raw_rows.append({"label": label, "value_first_numeric": value})

        key = _METRIC_LABELS.get(_normalise_label(label))
        if key is not None and value is not None:
            metrics[key] = value

    required = {"internal_generation_mu", "net_import_interface_mu", "consumption_mu"}
    missing = sorted(required - metrics.keys())
    if missing:
        raise ValueError(f"SLDC response missing required metrics: {missing}")

    balance_error_mu = (
        metrics["internal_generation_mu"]
        + metrics["net_import_interface_mu"]
        - metrics["consumption_mu"]
    )

    return {
        "report_date": report_date.isoformat(),
        "metrics": metrics,
        "balance_error_mu": balance_error_mu,
        "rows": raw_rows,
    }


def fetch_system_statistics(
    report_date: date | None = None,
    *,
    session: Session | None = None,
    timeout: float = 45.0,
) -> dict[str, Any]:
    """Fetch latest or one historical daily SLDC system-statistics page."""
    own_session = session is None
    session = session or build_session()
    try:
        if report_date is None:
            response = checked(session.get(SYSTEM_STATS_URL, timeout=timeout))
        else:
            payload = {
                "date1_day": report_date.strftime("%d"),
                "date1_month": report_date.strftime("%m"),
                "date1_year": report_date.strftime("%Y"),
                "sbtstat": "SHOW",
            }
            response = checked(session.post(SYSTEM_STATS_URL, data=payload, timeout=timeout))

        parsed = parse_system_statistics(response.text)
        if report_date is not None and parsed["report_date"] != report_date.isoformat():
            raise ValueError(
                "SLDC returned a different report date "
                f"({parsed['report_date']}) than requested ({report_date.isoformat()})"
            )
        parsed["provenance"] = {
            "source_id": "kerala_sldc_system_statistics",
            "source_url": response.url,
            "retrieved_at_utc": utc_now_iso(),
            "http_status": response.status_code,
            "sha256": sha256_bytes(response.content),
            "content_type": response.headers.get("Content-Type"),
        }
        return parsed
    finally:
        if own_session:
            session.close()


def iter_daily(
    start: date,
    end: date,
    *,
    delay_seconds: float = 0.8,
    session: Session | None = None,
) -> Iterator[dict[str, Any]]:
    """Yield requested SLDC dates inclusively, rate-limited by default."""
    if end < start:
        raise ValueError("end must be on or after start")
    own_session = session is None
    session = session or build_session()
    current = start
    try:
        while current <= end:
            yield fetch_system_statistics(current, session=session)
            current += timedelta(days=1)
            if current <= end and delay_seconds > 0:
                time.sleep(delay_seconds)
    finally:
        if own_session:
            session.close()


def daily_frame(records: list[dict[str, Any]]) -> pd.DataFrame:
    """Flatten parsed daily records into one analysis table."""
    rows: list[dict[str, Any]] = []
    for record in records:
        row = {
            "date": pd.Timestamp(record["report_date"]),
            **record["metrics"],
            "balance_error_mu": record["balance_error_mu"],
            "source_sha256": record["provenance"]["sha256"],
            "retrieved_at_utc": record["provenance"]["retrieved_at_utc"],
        }
        rows.append(row)
    frame = pd.DataFrame(rows)
    if not frame.empty:
        frame = frame.sort_values("date").reset_index(drop=True)
    return frame
