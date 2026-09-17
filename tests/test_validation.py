import pandas as pd

from kerala2040.validation import compare_daily_energy, monthly_energy_balance


def test_compare_daily_energy() -> None:
    sldc = pd.DataFrame(
        {
            "date": pd.to_datetime(["2025-01-01", "2025-01-02"]),
            "consumption_mu": [100.0, 102.0],
        }
    )
    grid = pd.DataFrame(
        {
            "date": pd.to_datetime(["2025-01-01", "2025-01-02"]),
            "energy_met_mu": [99.0, 103.0],
        }
    )
    comparison, summary = compare_daily_energy(sldc, grid)
    assert comparison["difference_mu"].tolist() == [1.0, -1.0]
    assert summary["overlap_days"] == 2
    assert summary["median_absolute_difference_mu"] == 1.0


def test_monthly_energy_balance() -> None:
    daily = pd.DataFrame(
        {
            "date": pd.to_datetime(["2025-01-01", "2025-01-02"]),
            "consumption_mu": [100.0, 100.0],
            "internal_generation_mu": [25.0, 30.0],
            "net_import_interface_mu": [75.0, 70.0],
        }
    )
    result = monthly_energy_balance(daily)
    assert result.loc[0, "consumption_mu"] == 200.0
    assert result.loc[0, "import_share"] == 0.725
