import pandas as pd

from kerala2040.hydro import build_hydro_daily, summarise_hydro


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
