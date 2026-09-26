from pathlib import Path

import pytest
from openpyxl import Workbook

from kerala2040.kseb_monthly_workbook_v1_5 import (
    KSEBWorkbookParseError,
    expected_dates_for_month,
    extract_month,
    parse_daily_sheet,
)

HEADERS = [
    "Sl. No.",
    "Name of Reservoir",
    "District",
    "FRL (metre)",
    "Rule level (metre)",
    "Water level on date (metre)",
    "MWL (metre)",
    "Spillway Crest Level (metre)",
    "Blue Alert level (metre)",
    "Orange Alert level (metre)",
    "Red Alert Level (metre)",
    "Live Storage at FRL (MCM)",
    "Live Storage (MCM)",
    "% Storage",
    "% Storage wrt Live Storage at FRL",
    "Inflow (MCM)",
    "Average Inflow (Cumecs)",
    "Power House Discharge (MCM)",
    "Spill (MCM)",
    "Current Spillway release (Cumecs)",
    "Total Outflow (MCM)",
    "Rain fall (mm)",
    "Remarks",
    "Generation (MU)",
]


def idukki_row():
    return [
        1,
        "IDUKKI",
        "IDK",
        2403,
        2375.33,
        2321,
        "2408.5 ft",
        "2373 ft",
        2367.33,
        2373.33,
        2374.33,
        1459.49,
        343.54,
        23.54,
        "#REF!",
        3.911,
        45.27,
        0.9804,
        0,
        0,
        0.9804,
        23,
        None,
        1.42,
    ]


def test_parse_modern_daily_sheet():
    rows = [
        ["KERALA STATE ELECTRICITY BOARD LIMITED"],
        ["DAILY REPORT - WATER LEVELS OF MAJOR RESERVOIRS (As on 01.07.2026) 7.00 AM."],
        HEADERS,
        list(range(1, len(HEADERS) + 1)),
        idukki_row(),
    ]
    result = parse_daily_sheet(rows, sheet_name="01.07.2026")
    assert result["date"] == "2026-07-01"
    assert result["metrics"]["live_storage_mcm"] == pytest.approx(343.54)
    assert result["metrics"]["inflow_mcm"] == pytest.approx(3.911)
    assert result["metrics"]["average_inflow_cumecs"] == pytest.approx(45.27)
    assert result["metrics"]["power_house_discharge_mcm"] == pytest.approx(0.9804)
    assert result["metrics"]["spill_mcm"] == pytest.approx(0)
    assert result["metrics"]["total_outflow_mcm"] == pytest.approx(0.9804)
    assert result["metrics"]["generation_mu"] == pytest.approx(1.42)
    assert result["units"]["water_level"] == "ft"
    assert result["metrics"]["outflow_component_residual_mcm"] == pytest.approx(0)


def test_percentage_in_inflow_fails():
    row = idukki_row()
    row[15] = "44.85%"
    rows = [["title 01.07.2026"], HEADERS, row]
    with pytest.raises(KSEBWorkbookParseError, match="percentage"):
        parse_daily_sheet(rows, sheet_name="01.07.2026")


def test_expected_dates_leap_safe():
    assert len(expected_dates_for_month("2024-04")) == 30
    assert len(expected_dates_for_month("2025-02")) == 28


def test_extract_month_reports_missing_dates(tmp_path: Path):
    path = tmp_path / "2024-04.xlsx"
    wb = Workbook()
    ws = wb.active
    ws.title = "01.04.2024"
    ws.append(["KERALA STATE ELECTRICITY BOARD LIMITED"])
    ws.append(["DAILY REPORT (As on 01.04.2024)"])
    ws.append(HEADERS)
    ws.append(list(range(1, len(HEADERS) + 1)))
    ws.append(idukki_row())
    wb.save(path)

    result = extract_month(path, month="2024-04")
    assert result["record_count"] == 1
    assert result["status"] == "blocked_incomplete_or_ambiguous"
    assert len(result["missing_dates"]) == 29


def test_parse_legacy_cumecs_schema():
    headers = [
        "Sl. No.",
        "Name of Dam / Reservoir",
        "District",
        "MWL (metre)",
        "FRL (metre)",
        "Spillway Crest Level (metre)",
        "Gross Storage (Million cubic metre)",
        "Dead Storage (MCM)",
        "Live Storage at FRL (MCM)",
        "Rule level (metre)",
        "Blue level (metre)",
        "Orange level (metre)",
        "Red Level (metre)",
        "Today's Water level (metre)",
        "Today's Gross Storage (MCM)",
        "Percentage Storage respect to Gross Storage",
        "Today's Live Storage (MCM)",
        "% Storage wrt Live Storage at FRL",
        "Same day previous year Water level (metre)",
        "Same day previous year Gross Storage (MCM)",
        "Same day previous year Live Storage (MCM)",
        "% Storage wrt Live Storage at FRL",
        "Inflow (cumecs)",
        "Power House Discharge(cumecs)",
        "Spillway release (cumecs)",
        "Total Outflow (cumecs)",
        "Rain fall (mm)",
        "Remarks",
    ]
    row = [
        1,
        "IDUKKI",
        "IDK",
        "2408.5 ft",
        "2403 ft",
        "2373.6 ft",
        1996.3,
        536.81,
        1459.49,
        2399.79,
        2391.79,
        2397.79,
        2398.79,
        "2393.84ft",
        1842.053,
        0.9227,
        1305.243,
        0.8943,
        "2381.62ft",
        1639.797,
        1102.987,
        0.7557,
        41.5162,
        53.0093,
        0.0,
        53.0093,
        0.4,
        None,
    ]
    rows = [
        ["KERALA STATE ELECTRICITY BOARD LIMITED"],
        ["WATER LEVELS OF MAIN RESERVOIRS (as on 01.11.2020) 7.00 AM."],
        headers,
        list(range(1, len(headers) + 1)),
        row,
    ]
    result = parse_daily_sheet(rows, sheet_name="01.11.2020")
    assert result["metrics"]["live_storage_mcm"] == pytest.approx(1305.243)
    assert result["metrics"]["inflow_cumecs"] == pytest.approx(41.5162)
    assert result["metrics"]["power_house_discharge_cumecs"] == pytest.approx(53.0093)
    assert result["metrics"]["spill_cumecs"] == pytest.approx(0.0)
    assert result["metrics"]["total_outflow_cumecs"] == pytest.approx(53.0093)
    assert result["metrics"]["outflow_component_residual_cumecs"] == pytest.approx(0)
    assert result["units"]["water_level"] == "ft"
