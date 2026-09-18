from datetime import date

import pandas as pd

from kerala2040.sources.grid_india import (
    extract_state_row,
    fiscal_year_label,
    legacy_report_entries,
    legacy_report_url,
    select_report_files,
)


def test_extract_state_row() -> None:
    sheet = pd.DataFrame(
        [
            ["Region", "State", "Max Demand Met", "Peak Shortage", "Energy Met", "Schedule", "OD", "Max OD", "Energy Shortage"],
            ["SR", "Tamil Nadu", 17000, 0, 350.0, 300.0, 0, 0, 0],
            ["SR", "Kerala", 5800, 10, 92.5, 70.0, 1.0, 200.0, 0.2],
        ]
    )
    row = extract_state_row(sheet, "Kerala")
    assert row["peak_demand_met_mw"] == 5800.0
    assert row["energy_met_mu"] == 92.5
    assert row["peak_shortage_mw"] == 10.0
    assert row["drawal_schedule_mu"] == 70.0


def test_select_report_files() -> None:
    entries = [
        {"report_date": "2025-03-30", "FilePath": "a.xls"},
        {"report_date": "2025-04-01", "FilePath": "b.xls"},
    ]
    result = select_report_files(
        entries,
        start=pd.Timestamp("2025-03-30").date(),
        end=pd.Timestamp("2025-03-31").date(),
    )
    assert [item["FilePath"] for item in result] == ["a.xls"]


def test_fiscal_year_label() -> None:
    assert fiscal_year_label(date(2024, 4, 1)) == "2024-2025"
    assert fiscal_year_label(date(2025, 3, 31)) == "2024-2025"
    assert fiscal_year_label(date(2025, 4, 1)) == "2025-2026"


def test_legacy_url_and_entries() -> None:
    report_date = pd.Timestamp("2025-03-31").date()
    url = legacy_report_url(report_date)
    assert "2024-2025/March%202025/31.03.25_NLDC_PSP.xls" in url
    entries = legacy_report_entries(report_date, report_date)
    assert entries[0]["report_date"] == "2025-03-31"
    assert entries[0]["legacy_url"] == url
