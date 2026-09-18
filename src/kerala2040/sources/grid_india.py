"""Grid-India daily PSP report discovery and Kerala state-row extraction."""

from __future__ import annotations

import re
from datetime import date, timedelta
from io import BytesIO
from typing import Any
from urllib.parse import quote

import pandas as pd
from requests import Session

from kerala2040.provenance import sha256_bytes, utc_now_iso
from kerala2040.sources.http import build_session, checked

API_URL = "https://webapi.grid-india.in/api/v1/file"
CDN_ROOT = "https://webcdn.grid-india.in/"
LEGACY_ROOT = "https://report.grid-india.in/ReportData/Daily Report/PSP Report"
_FILE_TYPE = "DAILY_PSP_REPORT"
_DATE_RE = re.compile(r"(?<!\d)(\d{2})\.(\d{2})\.(\d{2})(?!\d)")


def fiscal_year_label(day: date) -> str:
    """Return Grid-India fiscal-year label such as 2024-2025."""
    start = day.year if day.month >= 4 else day.year - 1
    return f"{start}-{start + 1}"


def _report_date(entry: dict[str, Any]) -> date | None:
    text = " ".join(str(entry.get(key, "")) for key in ("Title_", "FilePath", "name"))
    match = _DATE_RE.search(text)
    if not match:
        return None
    day, month, year = (int(part) for part in match.groups())
    return date(2000 + year, month, day)


def legacy_report_url(report_date: date) -> str:
    """Build the deterministic legacy Daily PSP workbook URL."""
    fiscal_year = report_date.year if report_date.month >= 4 else report_date.year - 1
    folder = f"{fiscal_year}-{fiscal_year + 1}/{report_date.strftime('%B %Y')}"
    filename = f"{report_date.strftime('%d.%m.%y')}_NLDC_PSP.xls"
    return quote(f"{LEGACY_ROOT}/{folder}/{filename}", safe=":/")


def legacy_report_entries(start: date, end: date) -> list[dict[str, Any]]:
    """Generate deterministic legacy report entries for a date range."""
    if end < start:
        raise ValueError("end must be on or after start")
    current = start
    rows: list[dict[str, Any]] = []
    while current <= end:
        rows.append(
            {
                "report_date": current.isoformat(),
                "Title_": f"{current.strftime('%d.%m.%y')}_NLDC_PSP.xls",
                "legacy_url": legacy_report_url(current),
            }
        )
        current += timedelta(days=1)
    return rows


def list_month_psp_files(
    month: date,
    *,
    session: Session | None = None,
    timeout: float = 60.0,
    verify_tls: bool = True,
) -> list[dict[str, Any]]:
    """List Daily PSP files for one Grid-India fiscal-year/month bucket.

    The current Grid-India file API requires both the fiscal year and month.
    """
    own_session = session is None
    session = session or build_session()
    try:
        response = checked(
            session.post(
                API_URL,
                json={
                    "_source": "GRDW",
                    "_type": _FILE_TYPE,
                    "_fileDate": fiscal_year_label(month),
                    "_month": month.strftime("%m"),
                },
                timeout=timeout,
                verify=verify_tls,
                headers={"Origin": "https://grid-india.in"},
            )
        )
        payload = response.json()
        if isinstance(payload, dict):
            for key in ("retData", "data", "result", "files"):
                if isinstance(payload.get(key), list):
                    payload = payload[key]
                    break
        if not isinstance(payload, list):
            raise TypeError("Grid-India file API did not return a file list")
        rows: list[dict[str, Any]] = []
        for item in payload:
            if not isinstance(item, dict) or not item.get("FilePath"):
                continue
            parsed_date = _report_date(item)
            rows.append({**item, "report_date": parsed_date.isoformat() if parsed_date else None})
        return rows
    finally:
        if own_session:
            session.close()


def discover_daily_psp_files(
    start: date,
    end: date,
    *,
    session: Session | None = None,
    timeout: float = 60.0,
    verify_tls: bool = True,
) -> list[dict[str, Any]]:
    """Discover and de-duplicate current API files over a date range."""
    if end < start:
        raise ValueError("end must be on or after start")
    own_session = session is None
    session = session or build_session()
    try:
        cursor = date(start.year, start.month, 1)
        stop = date(end.year, end.month, 1)
        by_day: dict[str, dict[str, Any]] = {}
        while cursor <= stop:
            for entry in list_month_psp_files(
                cursor,
                session=session,
                timeout=timeout,
                verify_tls=verify_tls,
            ):
                report_day = entry.get("report_date")
                if not report_day:
                    continue
                parsed = date.fromisoformat(report_day)
                if not start <= parsed <= end:
                    continue
                # Grid-India occasionally publishes corrected versions; keep the
                # last returned item for a date rather than duplicating rows.
                by_day[report_day] = entry
            if cursor.month == 12:
                cursor = date(cursor.year + 1, 1, 1)
            else:
                cursor = date(cursor.year, cursor.month + 1, 1)
        return [by_day[key] for key in sorted(by_day)]
    finally:
        if own_session:
            session.close()


def list_daily_psp_files(
    *,
    session: Session | None = None,
    timeout: float = 60.0,
    verify_tls: bool = True,
) -> list[dict[str, Any]]:
    """Compatibility helper returning files for the current calendar month."""
    today = date.today()
    return list_month_psp_files(today, session=session, timeout=timeout, verify_tls=verify_tls)


def select_report_files(
    entries: list[dict[str, Any]], *, start: date, end: date
) -> list[dict[str, Any]]:
    selected = []
    for entry in entries:
        if not entry.get("report_date"):
            continue
        report_day = date.fromisoformat(entry["report_date"])
        if start <= report_day <= end:
            selected.append(entry)
    return sorted(selected, key=lambda item: item["report_date"])


def download_report(
    entry: dict[str, Any],
    *,
    session: Session | None = None,
    timeout: float = 90.0,
    verify_tls: bool = True,
) -> tuple[bytes, dict[str, Any]]:
    """Download an API-listed or deterministic legacy PSP workbook."""
    if entry.get("legacy_url"):
        url = str(entry["legacy_url"])
        path = str(entry.get("Title_", "legacy_psp.xls"))
    else:
        path = str(entry["FilePath"]).lstrip("/")
        url = CDN_ROOT + path

    own_session = session is None
    session = session or build_session()
    try:
        response = checked(session.get(url, timeout=timeout, verify=verify_tls))
        return response.content, {
            "source_id": "grid_india_daily_psp",
            "source_url": response.url,
            "retrieved_at_utc": utc_now_iso(),
            "http_status": response.status_code,
            "sha256": sha256_bytes(response.content),
            "content_type": response.headers.get("Content-Type"),
            "report_date": entry.get("report_date"),
            "file_path": path,
        }
    finally:
        if own_session:
            session.close()


def _normalise(value: Any) -> str:
    return " ".join(str(value).replace("\n", " ").split()).strip().lower()


def _numeric(value: Any) -> float | None:
    if pd.isna(value):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    match = re.search(r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)", str(value).replace(",", ""))
    return float(match.group(0)) if match else None


def extract_state_row(sheet: pd.DataFrame, state: str = "Kerala") -> dict[str, Any]:
    """Extract a state's metrics from the standard MOP_E row layout."""
    target = state.strip().lower()
    for row_index in range(len(sheet)):
        row = sheet.iloc[row_index].tolist()
        for state_column, cell in enumerate(row):
            if _normalise(cell) != target:
                continue
            values = [_numeric(sheet.iat[row_index, column]) for column in range(sheet.shape[1])]
            if state_column + 7 >= len(values):
                raise ValueError("MOP_E state row is shorter than the expected standard layout")
            demand = values[state_column + 1]
            energy = values[state_column + 3]
            if demand is None or demand <= 0:
                raise ValueError("MOP_E Kerala peak-demand value is missing or invalid")
            if energy is None or energy <= 0:
                raise ValueError("MOP_E Kerala energy-met value is missing or invalid")
            return {
                "state": state,
                "peak_demand_met_mw": demand,
                "peak_shortage_mw": values[state_column + 2],
                "energy_met_mu": energy,
                "drawal_schedule_mu": values[state_column + 4],
                "od_ud_mu": values[state_column + 5],
                "max_od_ud_mw": values[state_column + 6],
                "energy_shortage_mu": values[state_column + 7],
            }
    raise ValueError(f"state {state!r} not found in MOP_E sheet")


def parse_mop_e_state(
    content: bytes, state: str = "Kerala", filename: str = "report.xls"
) -> dict[str, Any]:
    """Parse a legacy XLS or XLSX PSP workbook and extract the state row."""
    suffix = filename.lower().rsplit(".", maxsplit=1)[-1]
    engine = "openpyxl" if suffix == "xlsx" else "xlrd"
    sheet = pd.read_excel(BytesIO(content), sheet_name="MOP_E", header=None, engine=engine)
    return extract_state_row(sheet, state=state)
