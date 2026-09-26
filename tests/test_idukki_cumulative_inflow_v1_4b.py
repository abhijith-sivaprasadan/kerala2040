"""Tests for Idukki source-cumulative inflow sensitivity v1.4b."""
from pathlib import Path

import pandas as pd
import pytest

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


def test_build_source_informed_scenario(tmp_path: Path):
    extra = []
    for month in range(2, 12):
        for day in range(1, 12):
            extra.append({
                "date": pd.Timestamp(2023, month, day),
                "reservoir": "IDUKKI",
                "inflow_mcm_day": None,
                "month_inflow_mu": 0.0,
                "source_sha256": "x",
            })

    # Pilot Jan 1-5:
    # Jan 2 blank -> zero by convention.
    # Jan 3 source row absent -> cumulative-derived as 3 MCM from Jan 2/4.
    # Jan 5 source row absent -> unresolved because no following pilot day.
    pilot = [
        {
            "date": pd.Timestamp("2024-01-01"),
            "reservoir": "IDUKKI",
            "inflow_mcm_day": 1.0,
            "month_inflow_mu": 1.0,
            "source_sha256": "a",
        },
        {
            "date": pd.Timestamp("2024-01-02"),
            "reservoir": "IDUKKI",
            "inflow_mcm_day": None,
            "month_inflow_mu": 1.0,
            "source_sha256": "b",
        },
        {
            "date": pd.Timestamp("2024-01-04"),
            "reservoir": "IDUKKI",
            "inflow_mcm_day": 2.0,
            "month_inflow_mu": 6.0,
            "source_sha256": "c",
        },
    ]
    rows = pd.DataFrame([*extra, *pilot])
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
            "dispatch_end": "2024-01-05",
        },
    }
    private = tmp_path / "private"
    result = build_source_informed_inflow_scenarios(
        source,
        suite,
        private_output_dir=private,
    )

    assert result["pilot"]["source_reported_daily_inflow_days"] == 2
    assert result["pilot"]["accepted_blank_zero_convention_days"] == 1
    assert result["pilot"]["rejected_source_rows"] == 2
    assert result["pilot"]["rejected_dates_recovered_by_adjacent_cumulative"] == 1
    assert result["pilot"]["rejected_cumulative_derived_sum_mcm"] == pytest.approx(3.0)
    assert result["pilot"]["source_unconstrained_dates_after_recovery"] == [
        "2024-01-05"
    ]
    assert set(result["scenarios"]) == {
        "nov30_zero_lower",
        "nov30_same_month_median",
        "nov30_same_month_p95",
        "nov30_same_month_max",
        "nov30_pilot_max_stress",
    }
    for scenario_id in result["scenarios"]:
        assert (private / f"{scenario_id}.csv").is_file()


def test_suite_class_constant():
    assert "source_informed_sensitivity" in SUITE_CLASS
