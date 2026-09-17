"""Kerala SLDC reservoir-storage adapter."""

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
from kerala2040.sources.sldc import BASE_URL, STORAGE_URL

_DATE_RE = re.compile(r"STORAGE\s+AS\s+ON\s+(\d{1,2}\.\d{1,2}\.\d{4})", re.IGNORECASE)


def _clean(value: str) -> str:
    return " ".join(value.replace("\xa0", " ").split()).strip()


def _number(value: str) -> float | None:
    match = re.search(r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)", value.replace(",", ""))
    return float(match.group(0)) if match else None


def parse_storage(html: str) -> dict[str, Any]:
    """Parse reservoir rows from the public SLDC storage table."""
    soup = BeautifulSoup(html, "lxml")
    title = soup.find("h1", class_="title")
    title_text = _clean(title.get_text(" ", strip=True)) if title else ""
    match = _DATE_RE.search(title_text)
    if not match:
        raise ValueError("SLDC storage response did not contain a report date")
    day, month, year = (int(part) for part in match.group(1).split("."))
    report_date = date(year, month, day)

    reservoirs: list[dict[str, Any]] = []
    table = soup.find("table", class_="display")
    if table is None:
        raise ValueError("SLDC storage response did not contain the storage table")

    for tr in table.find_all("tr"):
        cells = [_clean(td.get_text(" ", strip=True)) for td in tr.find_all("td")]
        if len(cells) < 16:
            continue
        reservoir = cells[4]
        if not reservoir or reservoir.upper() == "RESERVOIR" or "TOTAL" in reservoir.upper():
            continue
        if _number(cells[0]) is None or _number(cells[3]) is None:
            continue
        reservoirs.append(
            {
                "reservoir": reservoir,
                "min_drawdown_level_m": _number(cells[0]),
                "full_level_m": _number(cells[1]),
                "full_storage_mcm": _number(cells[2]),
                "full_storage_mu": _number(cells[3]),
                "level_m": _number(cells[5]),
                "effective_storage_mcm": _number(cells[6]),
                "storage_pct": _number(cells[7]),
                "generation_capability_gross_mu": _number(cells[8]),
                "generation_capability_station_mu": _number(cells[9]),
                "rainfall_mm": _number(cells[10]),
                "spill_mcm_day": _number(cells[11]),
                "inflow_mu": _number(cells[12]),
                "cumulative_inflow_month_mu": _number(cells[13]),
                "previous_day_storage_pct": _number(cells[14]),
                "remarks": cells[15],
            }
        )

    if not reservoirs:
        raise ValueError("SLDC storage response contained no reservoir rows")

    full_mu = sum(row["full_storage_mu"] or 0.0 for row in reservoirs)
    gross_mu = sum(row["generation_capability_gross_mu"] or 0.0 for row in reservoirs)
    inflow_mu = sum(row["inflow_mu"] or 0.0 for row in reservoirs)
    return {
        "report_date": report_date.isoformat(),
        "reservoirs": reservoirs,
        "system": {
            "full_storage_mu": full_mu,
            "generation_capability_gross_mu": gross_mu,
            "storage_pct_energy_weighted": 100.0 * gross_mu / full_mu if full_mu else None,
            "inflow_mu": inflow_mu,
            "reservoir_count": len(reservoirs),
        },
    }


def fetch_storage(
    report_date: date | None = None,
    *,
    session: Session | None = None,
    timeout: float = 45.0,
) -> dict[str, Any]:
    """Fetch latest or a historical SLDC storage report."""
    own_session = session is None
    session = session or build_session()
    try:
        if report_date is None:
            response = checked(session.get(STORAGE_URL, timeout=timeout))
        else:
            payload = {
                "date1_day": report_date.strftime("%d"),
                "date1_month": report_date.strftime("%m"),
                "date1_year": report_date.strftime("%Y"),
                "sbtstore": "SHOW",
            }
            response = checked(session.post(BASE_URL, data=payload, timeout=timeout))
        parsed = parse_storage(response.text)
        if report_date is not None and parsed["report_date"] != report_date.isoformat():
            raise ValueError(
                "SLDC storage returned a different report date "
                f"({parsed['report_date']}) than requested ({report_date.isoformat()})"
            )
        parsed["provenance"] = {
            "source_id": "kerala_sldc_storage",
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


def iter_daily_storage(
    start: date,
    end: date,
    *,
    delay_seconds: float = 0.8,
    session: Session | None = None,
) -> Iterator[dict[str, Any]]:
    if end < start:
        raise ValueError("end must be on or after start")
    own_session = session is None
    session = session or build_session()
    current = start
    try:
        while current <= end:
            yield fetch_storage(current, session=session)
            current += timedelta(days=1)
            if current <= end and delay_seconds > 0:
                time.sleep(delay_seconds)
    finally:
        if own_session:
            session.close()


def storage_frames(records: list[dict[str, Any]]) -> tuple[pd.DataFrame, pd.DataFrame]:
    daily_rows: list[dict[str, Any]] = []
    reservoir_rows: list[dict[str, Any]] = []
    for record in records:
        day = pd.Timestamp(record["report_date"])
        daily_rows.append(
            {
                "date": day,
                **record["system"],
                "source_sha256": record["provenance"]["sha256"],
                "retrieved_at_utc": record["provenance"]["retrieved_at_utc"],
            }
        )
        for reservoir in record["reservoirs"]:
            reservoir_rows.append({"date": day, **reservoir})
    daily = pd.DataFrame(daily_rows)
    reservoir = pd.DataFrame(reservoir_rows)
    if not daily.empty:
        daily = daily.sort_values("date").reset_index(drop=True)
    if not reservoir.empty:
        reservoir = reservoir.sort_values(["date", "reservoir"]).reset_index(drop=True)
    return daily, reservoir
