import pandas as pd

from kerala2040.historical_model import (
    build_daily_observed_replay,
    replay_energy_summary,
)


def test_daily_replay_uses_no_synthetic_hourly_load():
    daily = pd.DataFrame(
        {
            "date": pd.to_datetime(["2024-04-01", "2024-04-02"]),
            "consumption_mu": [50.0, 52.0],
            "internal_generation_mu": [20.0, 22.0],
            "net_import_interface_mu": [30.0, 30.0],
            "hydel_total_mu": [15.0, 16.0],
        }
    )
    observed = {
        "period": "FY2024-25",
        "electricity": {
            "installed_capacity_mw": 4412.14,
            "capacity_mix_mw": {
                "hydel": 2284.42,
                "thermal": 536.54,
                "solar": 1519.66,
                "wind": 71.53,
            },
        },
    }
    network = build_daily_observed_replay(daily, observed)
    summary = replay_energy_summary(network)

    assert network.meta["synthetic_hourly_load_used"] is False
    assert network.meta["hourly_telemetry_used"] is False
    assert len(network.snapshots) == 2
    assert abs(summary["load_mwh"] - 102000.0) < 1e-6
    assert abs(summary["balance_error_mwh"]) < 1e-6
