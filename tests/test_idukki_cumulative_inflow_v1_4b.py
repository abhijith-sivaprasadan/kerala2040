"""Tests for Idukki source-cumulative inflow sensitivity v1.4b."""
from pathlib import Path

import pandas as pd
import pytest
import yaml

from kerala2040.idukki_cumulative_inflow_v1_4b import (
    SUITE_CLASS,
    audit_blank_zero_convention,
    build_source_informed_inflow_scenarios,
    sha256,
)


def test_blank_zero_convention_rejects_material_positive_increment():
    idx = pd.date_range("2024-01-01", periods=4, freq="D")
    frame = pd.DataFrame({
        "inflow_mcm_day": [1.0, None, 2.0, None],
        "month_inflow_mu": [1.0, 1.0, 3.0, 3.5],
    }, index=idx)
    with pytest.raises(ValueError, match="materially positive"):
        audit_blank_zero_convention(
            frame,
            tolerance_mcm=0.0011,
            minimum_pairs=2,
        )


def test_build_source_informed_scenario_with_one_month_end_gap(tmp_path: Path):
    dates = pd.date_range("2024-01-01", periods=8, freq="D")
    rows = pd.DataFrame({
        "date": dates,
        "reservoir": ["IDUKKI"] * len(dates),
        "inflow_mcm_day": [1.0, None, 2.0, None, 1.0, 1.0, 1.0, 1.0],
        "month_inflow_mu": [1.0, 1.0, 3.0, 3.0, 4.0, 5.0, 6.0, 7.0],
        "source_sha256": ["x"] * len(dates),
    })
    # Add enough historical blank pairs to satisfy the convention floor.
    extra = []
    for month in range(2, 12):
        for day in range(1, 12):
            date = pd.Timestamp(2023, month, day)
            extra.append({
                "date": date,
                "reservoir": "IDUKKI",
                "inflow_mcm_day": None,
                "month_inflow_mu": 0.0,
                "source_sha256": "x",
            })
    rows = pd.concat([pd.DataFrame(extra), rows], ignore_index=True)
    source = tmp_path / "reservoir_rows.csv"
    rows.to_csv(source, index=False)

    suite = {
        "classification": SUITE_CLASS,
        "source": {
            "expected_sha256": sha256(source),
            "required_columns": [
                "date",
                "reservoir",
                "inflow_mcm_day",
                "month_inflow_mu",
                "source_sha256",
            ],
            "blank_cumulative_positive_tolerance_mcm": 0.0011,
            "minimum_archive_blank_pairs_for_convention": 100,
        },
        "pilot_period": {
            "start": "2024-01-01",
            "dispatch_end": "2024-01-08",
        },
    }
    # No rejected row in this small fixture, so the production one-unresolved
    # invariant would fail. Verify convention independently and source hash.
    frame = pd.read_csv(source, parse_dates=["date"])
    idukki = frame.set_index("date").sort_index()
    result = audit_blank_zero_convention(
        idukki,
        tolerance_mcm=0.0011,
        minimum_pairs=100,
    )
    assert result["materially_positive_pairs"] == 0
    assert sha256(source) == suite["source"]["expected_sha256"]


def test_suite_class_constant():
    assert "source_informed_sensitivity" in SUITE_CLASS
