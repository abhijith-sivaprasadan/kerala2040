"""Header-driven parser for official KSEB Dam Safety daily reservoir pages.

The historical KSEB table schema has changed over time. This parser therefore
does not use fixed column positions. Critical hydro fields are identified from
their header meaning and unit, and ambiguous or visibly shifted rows fail
closed.

The module is intentionally limited to source extraction/QA. It does not infer
missing days or convert one reported unit into another.
"""
from __future__ import annotations

import hashlib
import re
import unicodedata
from dataclasses import dataclass
from datetime import date, datetime
from typing import Any
from urllib.parse import urljoin

from bs4 import BeautifulSoup

OFFICIAL_HOST = "dams.kseb.in"
DATE_RE = re.compile(r"(?<!\d)(\d{1,2})[./-](\d{1,2})[./-](\d{4})(?!\d)")


class KSEBSourceError(ValueError):
    """Raised when an official KSEB page cannot be parsed unambiguously."""


@dataclass(frozen=True)
class HeaderField:
    key: str
    unit: str | None
    raw: str


def _clean_text(value: str) -> str:
    return " ".join(value.replace("\xa0", " ").split())


def _ascii(value: str) -> str:
    return unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode()


def normalize_header(value: str) -> str:
    value = _ascii(_clean_text(value)).lower()
    value = value.replace("w.r.t", "wrt").replace("w r t", "wrt")
    value = re.sub(r"[^a-z0-9%/]+", " ", value)
    return " ".join(value.split())


def _unit_from_header(raw: str) -> str | None:
    text = normalize_header(raw)
    if "mcm" in text or "million cubic" in text:
        return "MCM"
    if "cumec" in text or "m3/s" in text or "m 3 / s" in text:
        return "cumecs"
    if "rain" in text and "mm" in text:
        return "mm"
    if "metre" in text or "meter" in text:
        return "metre"
    if " ft" in f" {text}" or "feet" in text:
        return "ft"
    if "%" in text or "percent" in text:
        return "percent"
    return None


def classify_header(raw: str) -> HeaderField:
    text = normalize_header(raw)
    unit = _unit_from_header(raw)

    if "name of dam" in text or "name of reservoir" in text:
        return HeaderField("dam_name", None, raw)
    if text == "district":
        return HeaderField("district", None, raw)
    if text.startswith("sl no") or text in {"sl no", "serial no"}:
        return HeaderField("serial", None, raw)
    if "today" in text and "live storage" in text:
        return HeaderField("live_storage", unit, raw)
    if "today" in text and "water level" in text:
        return HeaderField("water_level", unit, raw)
    if "storage wrt live storage at frl" in text:
        return HeaderField("storage_percent", "percent", raw)
    if "same day previous year" in text and "live storage" in text:
        return HeaderField("previous_year_live_storage", unit, raw)
    if "same day previous year" in text and "water level" in text:
        return HeaderField("previous_year_water_level", unit, raw)
    if "average inflow" in text:
        return HeaderField("average_inflow", unit, raw)
    if re.search(r"(^| )inflow( |$)", text):
        return HeaderField("inflow", unit, raw)
    if "power house discharge" in text or "powerhouse discharge" in text:
        return HeaderField("power_house_discharge", unit, raw)
    if "spillway release" in text or "spill way release" in text:
        return HeaderField("spillway_release", unit, raw)
    if "total outflow" in text:
        return HeaderField("total_outflow", unit, raw)
    if "rainfall" in text or "rain fall" in text:
        return HeaderField("rainfall", unit or "mm", raw)
    if text == "remarks":
        return HeaderField("remarks", None, raw)
    if text.startswith("mwl"):
        return HeaderField("mwl", unit, raw)
    if text.startswith("frl"):
        return HeaderField("frl", unit, raw)
    if "live storage at frl" in text:
        return HeaderField("live_storage_at_frl", unit, raw)
    if "rule level" in text:
        return HeaderField("rule_level", unit, raw)
    if "blue level" in text:
        return HeaderField("blue_level", unit, raw)
    if "orange level" in text:
        return HeaderField("orange_level", unit, raw)
    if "red level" in text:
        return HeaderField("red_level", unit, raw)
    if "spillway crest level" in text:
        return HeaderField("spillway_crest_level", unit, raw)
    return HeaderField("other", unit, raw)


def _metric_key(field: HeaderField) -> str:
    if field.key in {
        "inflow",
        "average_inflow",
        "power_house_discharge",
        "spillway_release",
        "total_outflow",
    }:
        if field.unit == "MCM":
            return f"{field.key}_mcm"
        if field.unit == "cumecs":
            return f"{field.key}_cumecs"
        raise KSEBSourceError(
            f"Critical flow field has no supported unit: {field.raw!r}"
        )
    if field.key in {
        "live_storage",
        "previous_year_live_storage",
        "live_storage_at_frl",
    }:
        if field.unit != "MCM":
            raise KSEBSourceError(
                f"Storage field is not explicitly MCM: {field.raw!r}"
            )
        return f"{field.key}_mcm"
    if field.key in {"water_level", "previous_year_water_level"}:
        return f"{field.key}_{(field.unit or 'unspecified').lower()}"
    if field.key == "rainfall":
        return "rainfall_mm"
    if field.key == "storage_percent":
        return "storage_percent"
    return field.key


def parse_numeric(raw: str, *, unit: str | None, field: str) -> float | None:
    text = _clean_text(raw)
    if text in {"", "-", "–", "—", "NA", "N/A", "nil", "Nil"}:
        return None

    lowered = text.lower()
    if unit != "percent" and "%" in text:
        raise KSEBSourceError(
            f"{field} contains a percentage under unit {unit}: {raw!r}"
        )
    if unit not in {"ft", None} and re.search(r"\bft\b", lowered):
        raise KSEBSourceError(f"{field} contains feet under unit {unit}: {raw!r}")

    cleaned = text.replace(",", "")
    if unit == "percent":
        cleaned = cleaned.replace("%", "").strip()
    if unit == "ft":
        cleaned = re.sub(r"\s*ft\.?\s*$", "", cleaned, flags=re.IGNORECASE)

    if not re.fullmatch(r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)", cleaned):
        raise KSEBSourceError(f"{field} is not a clean numeric source value: {raw!r}")
    return float(cleaned)


def parse_page_date(text: str) -> date:
    match = DATE_RE.search(text)
    if not match:
        raise KSEBSourceError(f"No DD.MM.YYYY-style date found in {text!r}")
    day, month, year = map(int, match.groups())
    return date(year, month, day)


def _table_headers(table: Any) -> tuple[list[str], int]:
    rows = table.find_all("tr")
    for idx, row in enumerate(rows):
        cells = row.find_all(["th", "td"])
        raw = [_clean_text(cell.get_text(" ", strip=True)) for cell in cells]
        normalized = [normalize_header(x) for x in raw]
        has_name = any("name of dam" in x or "name of reservoir" in x for x in normalized)
        has_hydro = any(
            "inflow" in x or "power house discharge" in x or "powerhouse discharge" in x
            for x in normalized
        )
        if has_name and has_hydro:
            return raw, idx
    raise KSEBSourceError("No semantic KSEB reservoir header row found")


def _schema_fingerprint(headers: list[HeaderField]) -> str:
    signature = "|".join(
        f"{h.key}:{h.unit or '-'}:{normalize_header(h.raw)}" for h in headers
    )
    return hashlib.sha256(signature.encode("utf-8")).hexdigest()


def parse_kseb_reservoir_page(
    html: str,
    *,
    source_url: str,
    target_dam: str = "IDUKKI",
) -> dict[str, Any]:
    if OFFICIAL_HOST not in source_url.lower():
        raise KSEBSourceError(f"Not an official KSEB Dam Safety URL: {source_url}")

    soup = BeautifulSoup(html, "html.parser")
    title_node = soup.select_one("h1.entry-title") or soup.find("h1")
    title = _clean_text(title_node.get_text(" ", strip=True)) if title_node else ""
    page_date = parse_page_date(title or soup.get_text(" ", strip=True)[:500])

    parsed_tables: list[tuple[Any, list[str], int]] = []
    for table in soup.find_all("table"):
        try:
            raw_headers, header_idx = _table_headers(table)
        except KSEBSourceError:
            continue
        parsed_tables.append((table, raw_headers, header_idx))

    if len(parsed_tables) != 1:
        raise KSEBSourceError(
            f"Expected exactly one reservoir table, found {len(parsed_tables)}"
        )

    table, raw_headers, header_idx = parsed_tables[0]
    headers = [classify_header(x) for x in raw_headers]
    name_indexes = [i for i, h in enumerate(headers) if h.key == "dam_name"]
    if len(name_indexes) != 1:
        raise KSEBSourceError("Dam-name column is missing or ambiguous")
    name_idx = name_indexes[0]

    critical = {"live_storage", "inflow", "power_house_discharge", "spillway_release"}
    keys = {h.key for h in headers}
    missing = sorted(critical - keys)
    if missing:
        raise KSEBSourceError(f"Critical KSEB headers missing: {missing}")

    data_rows: list[list[str]] = []
    rows = table.find_all("tr")
    for row in rows[header_idx + 1 :]:
        cells = row.find_all(["td", "th"])
        values = [_clean_text(cell.get_text(" ", strip=True)) for cell in cells]
        if len(values) != len(raw_headers):
            continue
        if values[name_idx].strip().upper() == target_dam.upper():
            data_rows.append(values)

    if len(data_rows) != 1:
        raise KSEBSourceError(
            f"Expected exactly one {target_dam} row, found {len(data_rows)}"
        )

    values = data_rows[0]
    raw_by_header: dict[str, str] = {}
    metrics: dict[str, float | None] = {}
    units: dict[str, str | None] = {}
    duplicate_metric_keys: set[str] = set()
    unit_overrides: list[dict[str, str]] = []

    mwl_raw = next(
        (raw for header, raw in zip(headers, values) if header.key == "mwl"),
        "",
    )
    idukki_levels_in_feet = bool(re.search(r"\bft\b", mwl_raw, flags=re.IGNORECASE))

    skipped_static_levels = {
        "mwl",
        "frl",
        "rule_level",
        "blue_level",
        "orange_level",
        "red_level",
        "spillway_crest_level",
    }

    for header, raw in zip(headers, values):
        if header.key in {
            "other",
            "serial",
            "district",
            "dam_name",
            "remarks",
            *skipped_static_levels,
        }:
            continue
        effective = header
        if (
            idukki_levels_in_feet
            and header.key in {"water_level", "previous_year_water_level"}
            and header.unit == "metre"
        ):
            effective = HeaderField(header.key, "ft", header.raw)
            unit_overrides.append(
                {
                    "field": header.key,
                    "header_unit": "metre",
                    "effective_row_unit": "ft",
                    "reason": "Idukki MWL source cell is explicitly marked ft",
                }
            )
        metric = _metric_key(effective)
        if metric in raw_by_header:
            duplicate_metric_keys.add(metric)
            continue
        raw_by_header[metric] = raw
        units[metric] = effective.unit
        metrics[metric] = parse_numeric(
            raw,
            unit=effective.unit,
            field=metric,
        )

    if duplicate_metric_keys:
        raise KSEBSourceError(
            f"Duplicate semantic metrics in schema: {sorted(duplicate_metric_keys)}"
        )

    has_inflow = any(
        key in metrics for key in ("inflow_mcm", "inflow_cumecs", "average_inflow_cumecs")
    )
    has_powerhouse = any(
        key in metrics
        for key in ("power_house_discharge_mcm", "power_house_discharge_cumecs")
    )
    has_spill = any(
        key in metrics for key in ("spillway_release_mcm", "spillway_release_cumecs")
    )
    if not (has_inflow and has_powerhouse and has_spill):
        raise KSEBSourceError(
            "Idukki row lacks an unambiguous inflow/powerhouse/spill metric set"
        )

    return {
        "classification": "OFFICIAL_KSEB_HEADER_DRIVEN_RESERVOIR_ROW_V1_5",
        "date": page_date.isoformat(),
        "dam": target_dam.upper(),
        "source_url": source_url,
        "schema": {
            "column_count": len(raw_headers),
            "fingerprint_sha256": _schema_fingerprint(headers),
            "raw_headers": raw_headers,
            "semantic_headers": [
                {"key": h.key, "unit": h.unit, "raw": h.raw} for h in headers
            ],
        },
        "metrics": metrics,
        "raw_values": raw_by_header,
        "units": units,
        "unit_overrides": unit_overrides,
    }


def discover_dated_post_links(html: str, *, base_url: str) -> list[dict[str, str]]:
    soup = BeautifulSoup(html, "html.parser")
    found: dict[tuple[str, str], dict[str, str]] = {}
    for anchor in soup.find_all("a", href=True):
        text = _clean_text(anchor.get_text(" ", strip=True))
        match = DATE_RE.search(text)
        if not match:
            continue
        try:
            parsed = parse_page_date(text)
        except KSEBSourceError:
            continue
        url = urljoin(base_url, anchor["href"])
        if OFFICIAL_HOST not in url.lower():
            continue
        item = {
            "date": parsed.isoformat(),
            "url": url,
            "link_text": text,
        }
        found[(item["date"], item["url"])] = item
    return sorted(found.values(), key=lambda x: (x["date"], x["url"]))


def utc_now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")
