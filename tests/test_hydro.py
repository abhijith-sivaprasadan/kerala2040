import pandas as pd

from kerala2040.hydro import (
    build_hydro_daily,
    build_reservoir_level_diagnostics,
    summarise_hydro,
)


def test_hydro_diagnostics_keep_observed_days_only():
    daily = pd.DataFrame(
        {
            "date": pd.to_datetime(["2024-05-01", "2024-06-01", "2024-10-01"]),
            "hydel_total_mu": [10.0, 20.0, 15.0],
            "net_import_interface_mu": [80.0, 60.0, 70.0],
            "consumption_mu": [90.0, 80.0, 85.0],
        }
    )
    storage = pd.DataFrame(
        {
            "date": daily["date"],
            "generation_capability_gross_mu": [1000.0, 1200.0, 1400.0],
            "storage_pct_energy_weighted": [30.0, 50.0, 70.0],
            "inflow_mu": [2.0, 30.0, 10.0],
        }
    )
    result = build_hydro_daily(daily, storage)
    summary = summarise_hydro(result)

    assert len(result) == 3
    assert set(result["season"]) == {
        "dry_intermonsoon",
        "southwest_monsoon",
        "post_monsoon",
    }
    assert summary["classification"].startswith("derived_from_observed")
    assert summary["days"] == 3
    assert summary["correlations"]["imports_vs_hydro"] < 0



def test_reservoir_level_diagnostics_are_contextual():
    hydro = pd.DataFrame(
        {
            "date": pd.to_datetime(["2024-06-01", "2024-06-02", "2024-06-03"]),
            "hydel_total_mu": [20.0, 22.0, 24.0],
        }
    )
    reservoirs = pd.DataFrame(
        {
            "date": hydro["date"],
            "reservoir": ["R1", "R1", "R1"],
            "level_m": [90.0, 92.0, 94.0],
            "min_drawdown_level_m": [80.0, 80.0, 80.0],
            "full_level_m": [100.0, 100.0, 100.0],
            "full_storage_mu": [500.0, 500.0, 500.0],
        }
    )
    levels, summary = build_reservoir_level_diagnostics(hydro, reservoirs)

    assert levels["normalised_level"].tolist() == [0.5, 0.6, 0.7]
    assert summary[0]["reservoir"] == "R1"
    assert "not plant-specific" in summary[0]["interpretation"]
