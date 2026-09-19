import pandas as pd

from kerala2040.observed_daily_network import (
    build_observed_detail_network,
    observed_detail_summary,
)


def _frames():
    daily = pd.DataFrame(
        {
            "date": ["2024-04-01", "2024-04-02", "2024-04-03"],
            "status": ["observed", "observed", "missing"],
            "hydro_mu": [10.0, 12.0, None],
            "internal_generation_mu": [14.0, 16.0, None],
            "net_import_mu": [26.0, 24.0, None],
            "consumption_mu": [40.0, 40.0, None],
        }
    )
    hydro = pd.DataFrame(
        {
            "date": ["2024-04-01", "2024-04-01", "2024-04-02"],
            "station_name_as_reported": ["A", "B", "A"],
            "generation_mu": [6.0, 2.0, 7.0],
        }
    )
    imports = pd.DataFrame(
        {
            "date": [
                "2024-04-01",
                "2024-04-01",
                "2024-04-02",
                "2024-04-02",
            ],
            "interface_name_as_reported": ["North", "South", "North", "South"],
            "import_mu": [15.0, 11.0, 14.0, 10.0],
        }
    )
    return daily, hydro, imports


def test_observed_detail_replay_preserves_missing_station_as_unallocated_hydro():
    daily, hydro, imports = _frames()
    network = build_observed_detail_network(
        daily,
        hydro,
        imports,
        qa={
            "source_archive_sha256": "x" * 64,
            "missing_dates": ["2024-04-03"],
        },
    )
    summary = observed_detail_summary(network)

    assert len(network.snapshots) == 2
    assert network.meta["hourly_telemetry_used"] is False
    assert network.meta["missing_day_interpolation_used"] is False
    assert network.meta["reservoir_constraints_used"] is False
    assert network.meta["hydro_station_missing_cells"]["B"] == 1

    # Day 1: 2 MU unallocated; day 2: B missing and 5 MU is retained
    # in the residual rather than silently attributed to station B.
    residual_mwh = summary["generator_energy_mwh"]["hydro_unallocated"]
    assert abs(residual_mwh - 7000.0) < 1e-6
    assert abs(summary["balance_error_mwh"]) < 1e-6


def test_observed_detail_replay_keeps_import_interfaces_separate():
    daily, hydro, imports = _frames()
    network = build_observed_detail_network(daily, hydro, imports)

    assert "import_interface__north" in network.generators.index
    assert "import_interface__south" in network.generators.index
    assert (
        network.generators.loc[
            ["import_interface__north", "import_interface__south"], "carrier"
        ]
        == "interstate_import"
    ).all()


def test_observed_detail_replay_rejects_incomplete_import_interface_coverage():
    daily, hydro, imports = _frames()
    imports = imports.loc[
        ~(
            imports["date"].eq("2024-04-02")
            & imports["interface_name_as_reported"].eq("South")
        )
    ]

    try:
        build_observed_detail_network(daily, hydro, imports)
    except ValueError as exc:
        assert "missing observed-day cells" in str(exc)
    else:
        raise AssertionError("incomplete interface coverage should fail")
