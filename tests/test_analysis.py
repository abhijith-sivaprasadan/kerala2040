from datetime import date

import pandas as pd
import pytest

from kerala2040.analysis import add_daily_indicators, summarise_daily_baseline


def _frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "date": pd.to_datetime(["2025-01-01", "2025-01-02"]),
            "internal_generation_mu": [25.0, 30.0],
            "net_import_interface_mu": [75.0, 70.0],
            "consumption_mu": [100.0, 100.0],
            "hydel_total_mu": [20.0, 24.0],
            "balance_error_mu": [0.0, 0.0],
        }
    )


def test_add_daily_indicators() -> None:
    result = add_daily_indicators(_frame())
    assert result.loc[0, "import_share"] == 0.75
    assert result.loc[1, "internal_share"] == 0.30


def test_summary_gate_and_units() -> None:
    summary = summarise_daily_baseline(
        _frame(), expected_start=date(2025, 1, 1), expected_end=date(2025, 1, 2)
    )
    assert summary["coverage_fraction"] == 1.0
    assert summary["consumption_twh"] == 0.2
    assert summary["aggregate_import_share"] == 0.725
    assert summary["calibration_gate_pass"] is True


def test_gate_rejects_missing_values_and_false_balance():
    data = _frame()
    data.loc[0, "consumption_mu"] = float("nan")
    assert not summarise_daily_baseline(data)["calibration_gate_pass"]
    data = _frame()
    data.loc[0, "internal_generation_mu"] = 200
    assert not summarise_daily_baseline(data)["calibration_gate_pass"]


def test_rejects_out_of_period_energy():
    with pytest.raises(ValueError, match="out-of-period"):
        summarise_daily_baseline(_frame(), expected_start="2025-01-02")
