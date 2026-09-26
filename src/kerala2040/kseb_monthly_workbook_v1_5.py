"""Header-driven extraction of Idukki rows from KSEB monthly workbooks.

Supports both OOXML .xlsx and legacy BIFF .xls containers. Daily sheets are
identified by date, then parsed from the sheet's own semantic header row rather
than fixed column indexes.

The extractor is fail-closed:
- duplicate dates fail;
- missing/ambiguous Idukki rows fail;
- critical fields without source units fail;
- values with incompatible suffixes (e.g. '%' in a flow field) fail;
- full FY2024-25 extraction requires every calendar date.
"""
from __future__ import annotations

import calendar
import hashlib
import re
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
from typing import Any

import xlrd
from openpyxl import load_workbook

from kerala2040.kseb_monthly_bundle_v1_5 import (
    KSEBMonthlyBundleError,
    audit_bundle,
    detect_format,
)

DATE_RE = re.compile(r"(?<!\d)(\d{1,2})[./-](\d{1,2})[./-](\d{2,4})(?!\d)")


class KSEBWorkbookParseError(ValueError):
    """Raised when a monthly workbook cannot be interpreted unambiguously."""


@dataclass(frozen=True)
class SheetRows:
    name: str
    rows: list[list[Any]]


def _clean(value: Any) -> str:
    if value is None:
        return ""
    return " ".join(str(value).replace("\xa0", " ").split())


def _norm(value: Any) -> str:
    text = _clean(value).lower()
    text = text.replace("w.r.t", "wrt").replace("w r t", "wrt")
    return re.sub(r"[^a-z0-9%/]+", " ", text).strip()


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def parse_sheet_date(*values: Any) -> date | None:
    for value in values:
        match = DATE_RE.search(_clean(value))
        if not match:
            continue
        day, month, year = map(int, match.groups())
        if year < 100:
            year += 2000
        try:
            return date(year, month, day)
        except ValueError:
            continue
    return None


def _field_from_header(raw: Any) -> str | None:
    text = _norm(raw)
    if not text:
        return None
    if "name of reservoir" in text or "name of dam" in text:
        return "reservoir"
    if "live storage at frl" in text or "total live storage at frl" in text:
        return "live_storage_at_frl_mcm"
    if "live storage" in text and "same day previous year" not in text:
        return "live_storage_mcm"
    if "water level" in text and "previous year" not in text:
        return "water_level"
    if "spillway crest level" in text:
        return "spillway_crest_level"
    if "average inflow" in text:
        return "average_inflow"
    if re.search(r"(^| )inflow( |$)", text):
        return "inflow"
    if "power house discharge" in text or "powerhouse discharge" in text:
        return "power_house_discharge"
    if text.startswith("spill") and "current" not in text:
        return "spill"
    if "current spillway release" in text:
        return "current_spillway_release"
    if "total outflow" in text:
        return "total_outflow"
    if "rain" in text and "fall" in text:
        return "rainfall_mm"
    if text.startswith("generation"):
        return "generation_mu"
    if "storage wrt live storage at frl" in text:
        return "storage_percent_wrt_frl"
    if text in {"% storage", "storage %", "storage percent"}:
        return "storage_percent"
    if text.startswith("mwl"):
        return "mwl"
    if text.startswith("frl"):
        return "frl"
    return None


def _unit_from_header(raw: Any, field: str) -> str | None:
    text = _norm(raw)
    if "mcm" in text:
        return "MCM"
    if "cumec" in text or "m3/s" in text or "m 3 / s" in text:
        return "cumecs"
    if "mm" in text and field == "rainfall_mm":
        return "mm"
    if "mu" in text and field == "generation_mu":
        return "MU"
    if "metre" in text or "meter" in text:
        return "metre"
    if "feet" in text or re.search(r"(^| )ft( |$)", text):
        return "ft"
    if "%" in text or "percent" in text:
        return "percent"
    return None



def _metric_key(field: str, unit: str | None) -> str | None:
    flow_fields = {
        "inflow",
        "average_inflow",
        "power_house_discharge",
        "spill",
        "current_spillway_release",
        "total_outflow",
    }
    if field in flow_fields:
        if unit == "MCM":
            return f"{field}_mcm"
        if unit == "cumecs":
            return f"{field}_cumecs"
        raise KSEBWorkbookParseError(
            f"{field}: critical flow field has unsupported unit {unit!r}"
        )
    if field in {"storage_percent", "storage_percent_wrt_frl"}:
        return None
    return field


def _number(value: Any, *, field: str, unit: str | None) -> float | None:
    if value is None:
        return None
    if isinstance(value, bool):
        raise KSEBWorkbookParseError(f"{field}: boolean source value")
    if isinstance(value, (int, float)):
        return float(value)
    text = _clean(value)
    if text in {"", "-", "–", "—", "NA", "N/A", "nil", "Nil"}:
        return None
    if text.startswith("#"):
        return None
    if unit != "percent" and "%" in text:
        raise KSEBWorkbookParseError(
            f"{field}: percentage value under {unit}: {text!r}"
        )
    cleaned = text.replace(",", "")
    if unit == "percent":
        cleaned = cleaned.replace("%", "")
    if unit == "ft":
        cleaned = re.sub(r"\s*(?:ft\.?|feet)\s*$", "", cleaned, flags=re.IGNORECASE)
    if not re.fullmatch(r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)", cleaned.strip()):
        raise KSEBWorkbookParseError(
            f"{field}: non-numeric source value {text!r}"
        )
    return float(cleaned)


def _find_header(rows: list[list[Any]]) -> tuple[int, dict[int, tuple[str, str | None, str]]]:
    candidates = []
    for row_idx, row in enumerate(rows[:12]):
        mapping: dict[int, tuple[str, str | None, str]] = {}
        for col_idx, raw in enumerate(row):
            field = _field_from_header(raw)
            if field:
                mapping[col_idx] = (field, _unit_from_header(raw, field), _clean(raw))
        fields = {item[0] for item in mapping.values()}
        score = len(
            fields
            & {
                "reservoir",
                "live_storage_mcm",
                "inflow",
                "average_inflow",
                "power_house_discharge",
                "spill",
                "total_outflow",
            }
        )
        if "reservoir" in fields and score >= 3:
            candidates.append((score, row_idx, mapping))
    if not candidates:
        raise KSEBWorkbookParseError("No semantic daily reservoir header found")
    candidates.sort(key=lambda item: (-item[0], item[1]))
    return candidates[0][1], candidates[0][2]


def _is_idukki(value: Any) -> bool:
    text = _norm(value)
    return text == "idukki" or text.endswith(" idukki") or text.startswith("idukki ")


def parse_daily_sheet(rows: list[list[Any]], *, sheet_name: str) -> dict[str, Any]:
    title_candidates = [sheet_name]
    for row in rows[:4]:
        title_candidates.extend(row[:4])
    day = parse_sheet_date(*title_candidates)
    if day is None:
        raise KSEBWorkbookParseError(
            f"{sheet_name}: could not determine daily sheet date"
        )

    header_idx, mapping = _find_header(rows)
    reservoir_cols = [
        col for col, (field, _, _) in mapping.items() if field == "reservoir"
    ]
    if len(reservoir_cols) != 1:
        raise KSEBWorkbookParseError(
            f"{sheet_name}: reservoir column missing or ambiguous"
        )
    reservoir_col = reservoir_cols[0]

    matches = []
    for row in rows[header_idx + 1 :]:
        if reservoir_col < len(row) and _is_idukki(row[reservoir_col]):
            matches.append(row)
    if len(matches) != 1:
        raise KSEBWorkbookParseError(
            f"{sheet_name}: expected one Idukki row, found {len(matches)}"
        )
    source_row = matches[0]

    # KSEB's generic water-level header may say metre while Idukki uses feet.
    row_text = " ".join(_clean(value) for value in source_row)
    idukki_feet = bool(re.search(r"\b(?:ft|feet)\b", row_text, flags=re.IGNORECASE))

    metrics: dict[str, float | None] = {}
    units: dict[str, str | None] = {}
    raw_values: dict[str, str] = {}
    headers: dict[str, str] = {}

    for col, (field, unit, raw_header) in mapping.items():
        if field in {"reservoir", "mwl", "frl", "spillway_crest_level"}:
            continue
        if col >= len(source_row):
            continue
        effective_unit = unit
        if field == "water_level" and idukki_feet and unit == "metre":
            effective_unit = "ft"
        metric = _metric_key(field, effective_unit)
        if metric is None:
            continue
        raw = source_row[col]
        if metric in metrics:
            raise KSEBWorkbookParseError(
                f"{sheet_name}: duplicate semantic field {metric}"
            )
        metrics[metric] = _number(raw, field=metric, unit=effective_unit)
        units[metric] = effective_unit
        raw_values[metric] = _clean(raw)
        headers[metric] = raw_header

    if "live_storage_mcm" not in metrics:
        raise KSEBWorkbookParseError(
            f"{sheet_name}: missing critical field live_storage_mcm"
        )
    required_groups = {
        "inflow": {"inflow_mcm", "inflow_cumecs", "average_inflow_cumecs"},
        "power_house_discharge": {
            "power_house_discharge_mcm",
            "power_house_discharge_cumecs",
        },
        "spill": {"spill_mcm", "spill_cumecs"},
    }
    missing_groups = [
        name
        for name, choices in required_groups.items()
        if not any(choice in metrics for choice in choices)
    ]
    if missing_groups:
        raise KSEBWorkbookParseError(
            f"{sheet_name}: missing critical flow groups {missing_groups}"
        )

    for suffix, unit_name in (("_mcm", "MCM"), ("_cumecs", "cumecs")):
        total_key = f"total_outflow{suffix}"
        power_key = f"power_house_discharge{suffix}"
        spill_key = f"spill{suffix}"
        if (
            metrics.get(total_key) is not None
            and metrics.get(power_key) is not None
            and metrics.get(spill_key) is not None
        ):
            residual_key = f"outflow_component_residual{suffix}"
            metrics[residual_key] = (
                metrics[total_key] - metrics[power_key] - metrics[spill_key]
            )

    return {
        "date": day.isoformat(),
        "sheet": sheet_name,
        "metrics": metrics,
        "units": units,
        "raw_values": raw_values,
        "headers": headers,
        "water_level_unit_override": (
            "ft_from_idukki_row_marker"
            if idukki_feet and units.get("water_level") == "ft"
            else None
        ),
    }


def read_workbook(path: Path) -> list[SheetRows]:
    fmt = detect_format(path)
    sheets: list[SheetRows] = []
    if fmt == "xlsx":
        workbook = load_workbook(path, read_only=True, data_only=True)
        try:
            for name in workbook.sheetnames:
                ws = workbook[name]
                rows = [list(row) for row in ws.iter_rows(values_only=True)]
                sheets.append(SheetRows(name=name, rows=rows))
        finally:
            workbook.close()
        return sheets
    if fmt == "xls":
        workbook = xlrd.open_workbook(path)
        for ws in workbook.sheets():
            rows = [
                [ws.cell_value(row, col) for col in range(ws.ncols)]
                for row in range(ws.nrows)
            ]
            sheets.append(SheetRows(name=ws.name, rows=rows))
        return sheets
    raise KSEBWorkbookParseError(
        f"{path.name}: unsupported workbook container {fmt}"
    )


def expected_dates_for_month(month: str) -> set[str]:
    year, number = map(int, month.split("-"))
    last = calendar.monthrange(year, number)[1]
    return {
        date(year, number, day).isoformat()
        for day in range(1, last + 1)
    }


def extract_month(path: Path, *, month: str) -> dict[str, Any]:
    records = []
    errors = []
    seen: set[str] = set()
    for sheet in read_workbook(path):
        day = parse_sheet_date(sheet.name, *[v for row in sheet.rows[:3] for v in row[:3]])
        if day is None or day.strftime("%Y-%m") != month:
            continue
        try:
            record = parse_daily_sheet(sheet.rows, sheet_name=sheet.name)
        except KSEBWorkbookParseError as exc:
            errors.append({"sheet": sheet.name, "error": str(exc)})
            continue
        if record["date"] in seen:
            errors.append(
                {"sheet": sheet.name, "error": f"duplicate date {record['date']}"}
            )
            continue
        seen.add(record["date"])
        records.append(record)

    expected = expected_dates_for_month(month)
    found = {record["date"] for record in records}
    missing_dates = sorted(expected - found)
    extra_dates = sorted(found - expected)
    status = (
        "complete"
        if not errors and not missing_dates and not extra_dates
        else "blocked_incomplete_or_ambiguous"
    )
    return {
        "month": month,
        "workbook": path.name,
        "workbook_sha256": _sha256(path),
        "detected_format": detect_format(path),
        "record_count": len(records),
        "records": sorted(records, key=lambda item: item["date"]),
        "errors": errors,
        "missing_dates": missing_dates,
        "extra_dates": extra_dates,
        "status": status,
    }


def extract_fy2024_25(bundle_dir: Path) -> dict[str, Any]:
    gate = audit_bundle(bundle_dir)
    if not gate["ready_for_content_schema_audit"]:
        raise KSEBMonthlyBundleError(
            "Monthly bundle gate has not passed; content extraction blocked"
        )

    months = []
    all_records = []
    for gate_record in gate["records"]:
        month = gate_record["month"]
        path = bundle_dir / gate_record["path"]
        result = extract_month(path, month=month)
        months.append(result)
        all_records.extend(result["records"])

    duplicate_dates = sorted(
        day for day in {r["date"] for r in all_records}
        if sum(r["date"] == day for r in all_records) > 1
    )
    expected_start = date(2024, 4, 1)
    expected_end = date(2025, 3, 31)
    expected_dates = set()
    current = expected_start
    while current <= expected_end:
        expected_dates.add(current.isoformat())
        current += timedelta(days=1)
    found_dates = {record["date"] for record in all_records}
    missing_dates = sorted(expected_dates - found_dates)

    ready = (
        all(month["status"] == "complete" for month in months)
        and not duplicate_dates
        and not missing_dates
        and len(all_records) == 365
    )
    return {
        "classification": "OFFICIAL_KSEB_IDUKKI_MONTHLY_WORKBOOK_EXTRACTION_V1_5",
        "bundle_gate": gate,
        "months": months,
        "record_count": len(all_records),
        "records": sorted(all_records, key=lambda item: item["date"]),
        "duplicate_dates": duplicate_dates,
        "missing_dates": missing_dates,
        "ready_for_water_balance_qa": ready,
        "model_input_ready": False,
        "status": (
            "ready_for_water_balance_qa"
            if ready
            else "blocked_content_schema_or_date_gap"
        ),
    }
