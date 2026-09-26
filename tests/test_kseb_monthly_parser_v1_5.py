import pytest

from kerala2040.kseb_monthly_parser_v1_5 import (
    KSEBMonthlyParseError,
    parse_sheet,
    semantic_header,
)


def modern_headers():
    return [
        "Sl.No",
        "Name of Reservoir",
        "District",
        "FRL (metre)",
        "Rule level (metre)",
        "Water level on date",
        "MWL (metre)",
        "Spillway Crest Level",
        "Blue Alert level",
        "Orange Alert level",
        "Red Alert Level",
        "Live Storage at FRL (MCM)",
        "Live Storage (MCM)",
        "% Storage",
        "% Storage wrt Live Storage",
        "Inflow (MCM)",
        "Average Inflow (Cumec)",
        "Power House Discharge",
        "Spill (MCM)",
        "Current Spillway release",
    ]


def test_semantic_headers_preserve_explicit_units():
    assert semantic_header("Inflow (MCM)") == ("inflow", "MCM")
    assert semantic_header("Average Inflow (Cumec)") == (
        "average_inflow",
        "cumecs",
    )
    assert semantic_header("Spill (MCM)") == ("spill", "MCM")
    assert semantic_header("Live Storage (MCM)") == ("live_storage", "MCM")


def test_parse_modern_idukki_daily_sheet():
    rows = [
        ["KSEB Limited Dam Safety Organisation"],
        modern_headers(),
        [
            1,
            "IDUKKI",
            "Idukki",
            "2403 ft",
            2375.33,
            2321.00,
            "2408.5 ft",
            "2373 ft",
            2367.33,
            2373.33,
            2374.33,
            1459.49,
            700.125,
            47.97,
            47.97,
            4.25,
            49.19,
            31.0,
            0.2,
            0.0,
        ],
    ]
    result = parse_sheet(
        "01.07.24",
        rows,
        source_month="2024-07",
        source_sha256="abc",
        source_file="2024-07.xls",
    )
    assert result is not None
    assert result["date"] == "2024-07-01"
    assert result["metrics"]["live_storage_mcm"] == pytest.approx(700.125)
    assert result["metrics"]["inflow_mcm"] == pytest.approx(4.25)
    assert result["metrics"]["average_inflow_cumecs"] == pytest.approx(49.19)
    assert result["metrics"]["spill_mcm"] == pytest.approx(0.2)
    assert result["metrics"]["frl_ft"] == pytest.approx(2403.0)
    assert result["metrics"]["water_level_ft"] == pytest.approx(2321.0)
    assert result["idukki_elevation_unit_override"] is True


def test_sheet_outside_month_is_ignored():
    rows = [modern_headers(), [1, "IDUKKI"]]
    assert (
        parse_sheet(
            "01.08.24",
            rows,
            source_month="2024-07",
            source_sha256="abc",
            source_file="2024-07.xls",
        )
        is None
    )


def test_duplicate_semantic_field_rejected():
    headers = modern_headers() + ["Inflow (MCM)"]
    row = [
        1,
        "IDUKKI",
        "Idukki",
        "2403 ft",
        2375.33,
        2321.00,
        "2408.5 ft",
        "2373 ft",
        2367.33,
        2373.33,
        2374.33,
        1459.49,
        700.125,
        47.97,
        47.97,
        4.25,
        49.19,
        31.0,
        0.2,
        0.0,
        4.25,
    ]
    with pytest.raises(KSEBMonthlyParseError, match="duplicate semantic field"):
        parse_sheet(
            "01.07.24",
            [headers, row],
            source_month="2024-07",
            source_sha256="abc",
            source_file="2024-07.xls",
        )
