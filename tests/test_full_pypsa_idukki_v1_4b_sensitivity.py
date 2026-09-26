"""Tests for the Full-PyPSA Idukki v1.4b sensitivity runner."""
from pathlib import Path

import pandas as pd
import pytest

from kerala2040.full_pypsa_idukki_v1_4b_sensitivity import (
    RUNNER_CLASS,
    load_private_inflow_scenario,
    load_v14b_runner_suite,
    summarize_sensitivity,
)

ROOT = Path(__file__).resolve().parents[1]


def test_runner_config_is_fail_closed():
    suite = load_v14b_runner_suite(
        ROOT / "configs/full_pypsa_idukki_v1_4b_sensitivity_runner.yaml"
    )
    assert suite["classification"] == RUNNER_CLASS
    assert suite["matrix"]["expected_cases"] == 60
    assert suite["release"]["real_60_case_matrix_executed"] is False
    assert suite["release"]["strict_v1_4_source_reported_model_ready"] is False


def test_private_scenario_loader_requires_exact_dates(tmp_path: Path):
    path = tmp_path / "scenario.csv"
    pd.DataFrame({
        "date": ["2024-01-01", "2024-01-02"],
        "inflow_mcm_day": [0.0, 2.5],
        "input_class": ["source", "derived"],
    }).to_csv(path, index=False)
    expected = pd.date_range("2024-01-01", periods=2, freq="D")
    series = load_private_inflow_scenario(path, expected_days=expected)
    assert list(series) == [0.0, 2.5]

    expected_three = pd.date_range("2024-01-01", periods=3, freq="D")
    with pytest.raises(ValueError, match="every pilot day"):
        load_private_inflow_scenario(path, expected_days=expected_three)


def _fake_case(scenario: str, unserved: float, release: float) -> dict:
    return {
        "inflow_scenario": scenario,
        "demand_case": "reference",
        "transfer_case": "atc",
        "idukki_availability_case": "full",
        "physical": {
            "stage3_unserved_mwh": unserved,
            "idukki_non_turbine_release_mcm": release,
            "idukki_generation_mwh": 1000.0 + unserved,
            "built": {
                "solar_combined_mw": 10.0 + unserved,
                "wind_onshore_mw": 20.0,
                "bess_4h_power_mw": 5.0,
            },
        },
    }


def test_sensitivity_summary_ranges():
    names = [
        "nov30_zero_lower",
        "nov30_same_month_median",
        "nov30_same_month_p95",
        "nov30_same_month_max",
        "nov30_pilot_max_stress",
    ]
    cases = [
        _fake_case(name, float(i), float(10 - i))
        for i, name in enumerate(names)
    ]
    summary = summarize_sensitivity(cases)
    assert len(summary) == 1
    row = summary[0]
    assert row["unserved_mwh_range"] == pytest.approx(4.0)
    assert row["idukki_non_turbine_release_mcm_range"] == pytest.approx(4.0)
    assert row["idukki_generation_mwh_range"] == pytest.approx(4.0)
    assert row["solar_mw_range"] == pytest.approx(4.0)


def test_summary_requires_all_five_scenarios():
    with pytest.raises(ValueError, match="five inflow scenarios"):
        summarize_sensitivity([
            _fake_case("a", 1.0, 1.0),
            _fake_case("b", 2.0, 2.0),
        ])
