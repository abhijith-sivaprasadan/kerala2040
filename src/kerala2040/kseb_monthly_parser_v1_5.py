"""Header-driven extraction of Idukki rows from KSEB monthly XLS/XLSX workbooks.

KSEB monthly workbooks use one sheet per reporting day (with occasional
non-daily helper/status sheets). The schema changes through time, so extraction
is semantic: locate the reservoir header, identify units from header text, find
the IDUKKI row, preserve explicit source units, and reject duplicate dates.

No missing daily value is interpolated and no flow-rate/volume conversion is
performed here.
"""
from __future__ import annotations

import re
from collections.abc import Iterable
from datetime import date
from pathlib import Path
from typing import Any

import openpyxl
import xlrd

from kerala2040.kseb_monthly_bundle_v1_5 import (
    EXPECTED_MONTHS,
    detect_format,
    sha256,
)

DATE_RE = re.compile(
    r"(?<!\d)(\d{1,2})[./-](\d{1,2})[./-](\d{2}|\d{4})(?!\d)"
)


class KSEBMonthlyParseError(ValueError):
    """Raised when a KSEB workbook row cannot be interpreted safely."""


def _clean(value: Any) -> str:
    if value is None:
        return ""
    return " ".join(str(value).replace("\xa0", " ").split())


def _norm(value: Any) -> str:
    text = _clean(value).lower()
    text = text.replace("w.r.t", "wrt").replace("w r t", "wrt")
    text = re.sub(r"[^a-z0-9%/]+", " ", text)
    return " ".join(text.split())


def _unit(header: str) -> str | None:
    text = _norm(header)
    if "mcm" in text or "million cubic" in text:
        return "MCM"
    if "cumec" in text or "m3/s" in text or "m 3 / s" in text:
        return "cumecs"
    if "mm" in text and ("rain" in text or "rainfall" in text):
        return "mm"
    if "%" in text or "percent" in text:
        return "percent"
    if "metre" in text or "meter" in text:
        return "metre"
    if re.search(r"(^| )ft( |$)", text) or "feet" in text:
        return "ft"
    return None


def semantic_header(header: str) -> tuple[str, str | None]:
    text = _norm(header)
    unit = _unit(header)

    if text in {"reservoir", "name of reservoir"} or "name of reservoir" in text:
        return "reservoir", None
    if "live storage at frl" in text:
        return "live_storage_at_frl", unit
    if "live storage" in text and "previous year" not in text:
        return "live_storage", unit
    if "average inflow" in text:
        return "average_inflow", unit
    if re.search(r"(^| )inflow( |$)", text):
        return "inflow", unit
    if "power house discharge" in text or "powerhouse discharge" in text:
        return "power_house_discharge", unit
    if text.startswith("spill ") or text == "spill":
        return "spill", unit
    if "current spillway release" in text:
        return "current_spillway_release", unit
    if "spillway release" in text:
        return "spillway_release", unit
    if "total outflow" in text:
        return "total_outflow", unit
    if "rainfall" in text or "rain fall" in text:
        return "rainfall", unit or "mm"
    if "rule level" in text:
        return "rule_level", unit
    if "blue" in text and "level" in text:
        return "blue_level", unit
    if "orange" in text and "level" in text:
        return "orange_level", unit
    if "red" in text and "level" in text:
        return "red_level", unit
    if text.startswith("frl"):
        return "frl", unit
    if text.startswith("mwl"):
        return "mwl", unit
    if "spillway crest" in text or text.startswith("crest level"):
        return "spillway_crest_level", unit
    if "water level" in text and "previous year" not in text:
        return "water_level", unit
    if "storage wrt live storage" in text:
        return "storage_wrt_live_storage_percent", "percent"
    if "% storage" in text or "percentage storage" in text:
        return "storage_percent", "percent"
    return "other", unit


def _metric_name(key: str, unit: str | None) -> str:
    if key in {
        "inflow",
        "average_inflow",
        "power_house_discharge",
        "spill",
        "current_spillway_release",
        "spillway_release",
        "total_outflow",
    }:
        if unit == "MCM":
            return f"{key}_mcm"
        if unit == "cumecs":
            return f"{key}_cumecs"
        return f"{key}_raw"
    if key in {"live_storage", "live_storage_at_frl"}:
        return f"{key}_mcm" if unit == "MCM" else f"{key}_raw"
    if key == "rainfall":
        return "rainfall_mm"
    if key == "storage_percent":
        return "storage_percent"
    if key in {
        "water_level",
        "frl",
        "mwl",
        "spillway_crest_level",
        "rule_level",
        "blue_level",
        "orange_level",
        "red_level",
    }:
        return f"{key}_{(unit or 'unspecified').lower()}"
    return key


def _number(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return float(value)
    if isinstance(value, (int, float)):
        return float(value)
    text = _clean(value)
    if text in {"", "-", "–", "—", "NA", "N/A", "Nil", "nil"}:
        return None
    text = text.replace(",", "")
    text = re.sub(
        r"\s*(?:ft|m|metre|meter|cumecs?|mcm|mm|%)\.?\s*$",
        "",
        text,
        flags=re.IGNORECASE,
    )
    text = text.strip()
    if not re.fullmatch(r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)", text):
        return None
    return float(text)


def _sheet_date(title: str, rows: list[list[Any]]) -> date | None:
    candidates = [title]
    for row in rows[:8]:
        candidates.extend(_clean(cell) for cell in row[:12])
    for text in candidates:
        match = DATE_RE.search(text)
        if not match:
            continue
        day, month, year = match.groups()
        year_int = int(year)
        if year_int < 100:
            year_int += 2000
        try:
            return date(year_int, int(month), int(day))
        except ValueError:
            continue
    return None


def _header_row(rows: list[list[Any]]) -> tuple[int, list[str]] | None:
    best: tuple[int, int, list[str]] | None = None
    for idx, row in enumerate(rows[:30]):
        headers = [_clean(value) for value in row]
        semantics = [semantic_header(value)[0] for value in headers]
        score = 0
        score += 6 if "reservoir" in semantics else 0
        score += 3 if "live_storage" in semantics else 0
        score += 3 if "inflow" in semantics else 0
        score += 2 if "water_level" in semantics else 0
        score += 1 if "frl" in semantics else 0
        if (
            "reservoir" in semantics
            and score >= 8
            and (best is None or score > best[0])
        ):
            best = (score, idx, headers)
    if best is None:
        return None
    return best[1], best[2]


def parse_sheet(
    title: str,
    rows: list[list[Any]],
    *,
    source_month: str,
    source_sha256: str,
    source_file: str,
) -> dict[str, Any] | None:
    report_date = _sheet_date(title, rows)
    if report_date is None or report_date.strftime("%Y-%m") != source_month:
        return None

    detected = _header_row(rows)
    if detected is None:
        return None
    header_idx, headers = detected

    semantic = [semantic_header(header) for header in headers]
    reservoir_cols = [i for i, (key, _) in enumerate(semantic) if key == "reservoir"]
    if len(reservoir_cols) != 1:
        raise KSEBMonthlyParseError(
            f"{source_file} {title!r}: reservoir column missing or ambiguous"
        )
    reservoir_col = reservoir_cols[0]

    matches: list[list[Any]] = []
    for row in rows[header_idx + 1 :]:
        if reservoir_col >= len(row):
            continue
        if _clean(row[reservoir_col]).upper() == "IDUKKI":
            matches.append(row)
    if len(matches) != 1:
        raise KSEBMonthlyParseError(
            f"{source_file} {title!r}: expected one IDUKKI row, found {len(matches)}"
        )
    row = matches[0]

    metrics: dict[str, float | None] = {}
    units: dict[str, str | None] = {}
    raw: dict[str, str] = {}
    headers_out: dict[str, str] = {}

    for col, (key, unit) in enumerate(semantic):
        if key in {"other", "reservoir"} or col >= len(row):
            continue
        metric = _metric_name(key, unit)
        if metric in raw:
            raise KSEBMonthlyParseError(
                f"{source_file} {title!r}: duplicate semantic field {metric}"
            )
        raw[metric] = _clean(row[col])
        headers_out[metric] = headers[col]
        units[metric] = unit
        metrics[metric] = _number(row[col])

    # KSEB's Idukki row uses feet for reservoir elevations even in workbooks
    # whose generic elevation header says metre. Keep the source number but
    # move it to an explicit *_ft field when FRL/MWL establish that convention.
    row_level_feet = (
        "ft" in raw.get("frl_metre", "").lower()
        or "ft" in raw.get("mwl_metre", "").lower()
        or (metrics.get("frl_metre") or 0.0) > 1000.0
        or (metrics.get("mwl_metre") or 0.0) > 1000.0
    )
    if row_level_feet:
        for base in (
            "water_level",
            "frl",
            "mwl",
            "spillway_crest_level",
            "rule_level",
            "blue_level",
            "orange_level",
            "red_level",
        ):
            for suffix in ("metre", "unspecified"):
                old = f"{base}_{suffix}"
                if old not in metrics:
                    continue
                new = f"{base}_ft"
                if new in metrics:
                    raise KSEBMonthlyParseError(
                        f"{source_file} {title!r}: duplicate Idukki feet field {new}"
                    )
                metrics[new] = metrics.pop(old)
                raw[new] = raw.pop(old)
                headers_out[new] = headers_out.pop(old)
                units[new] = "ft"
                units.pop(old, None)

    return {
        "date": report_date.isoformat(),
        "reservoir": "IDUKKI",
        "source_month": source_month,
        "source_file": source_file,
        "source_sha256": source_sha256,
        "source_sheet": title,
        "metrics": metrics,
        "units": units,
        "raw_values": raw,
        "source_headers": headers_out,
        "idukki_elevation_unit_override": row_level_feet,
    }


def _xlsx_sheets(path: Path) -> Iterable[tuple[str, list[list[Any]]]]:
    workbook = openpyxl.load_workbook(path, read_only=True, data_only=True)
    try:
        for sheet in workbook.worksheets:
            rows = [list(row) for row in sheet.iter_rows(values_only=True)]
            yield sheet.title, rows
    finally:
        workbook.close()


def _xls_sheets(path: Path) -> Iterable[tuple[str, list[list[Any]]]]:
    workbook = xlrd.open_workbook(path, on_demand=True)
    try:
        for name in workbook.sheet_names():
            sheet = workbook.sheet_by_name(name)
            rows = [sheet.row_values(i) for i in range(sheet.nrows)]
            yield name, rows
            workbook.unload_sheet(name)
    finally:
        workbook.release_resources()


def parse_workbook(path: Path, *, source_month: str) -> dict[str, Any]:
    if source_month not in EXPECTED_MONTHS:
        raise KSEBMonthlyParseError(f"Unexpected source month: {source_month}")
    fmt = detect_format(path)
    if fmt not in {"xlsx", "xls"}:
        raise KSEBMonthlyParseError(f"Unsupported workbook format: {fmt}")

    digest = sha256(path)
    iterator = _xlsx_sheets(path) if fmt == "xlsx" else _xls_sheets(path)
    records = []
    ignored_sheets = []
    for title, rows in iterator:
        parsed = parse_sheet(
            title,
            rows,
            source_month=source_month,
            source_sha256=digest,
            source_file=path.name,
        )
        if parsed is None:
            ignored_sheets.append(title)
        else:
            records.append(parsed)

    dates = [record["date"] for record in records]
    duplicates = sorted({day for day in dates if dates.count(day) > 1})
    if duplicates:
        raise KSEBMonthlyParseError(
            f"{path.name}: duplicate Idukki reporting dates: {duplicates}"
        )

    return {
        "classification": "OFFICIAL_KSEB_MONTHLY_IDUKKI_WORKBOOK_V1_5",
        "source_month": source_month,
        "source_file": path.name,
        "source_sha256": digest,
        "detected_format": fmt,
        "records": sorted(records, key=lambda item: item["date"]),
        "record_count": len(records),
        "ignored_sheets": ignored_sheets,
    }
