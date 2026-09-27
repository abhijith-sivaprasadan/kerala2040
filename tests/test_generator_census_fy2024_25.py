"""Tests for the FY2024-25 installed-generation capacity census."""
from pathlib import Path

import pytest

from kerala2040.generator_census import (
    build_generator_census,
    load_generator_census,
    reconcile_generator_census,
)

ROOT = Path(__file__).resolve().parents[1]
SOURCE = (
    ROOT
    / "data/evidence/generation/fy2024_25_generator_capacity_census.json"
)


def test_census_closes_capacity_accounting_without_fudge_row():
    frame, summary = build_generator_census(SOURCE)

    assert len(frame) == 112
    assert summary["station_or_farm_rows"] == 98
    assert summary["aggregate_or_distributed_rows"] == 14
    assert summary["historical_exclusion_rows"] == 2

    assert summary["official_reported_total_mw"] == pytest.approx(4412.14)
    assert summary["official_category_anchor_sum_mw"] == pytest.approx(4412.15)
    assert summary["bottom_up_detailed_total_mw"] == pytest.approx(4412.156)
    assert summary["bottom_up_minus_reported_total_mw"] == pytest.approx(0.016)

    # The 0.01 MW source inconsistency is preserved, never hidden by a
    # balancing asset.
    assert summary["official_category_sum_minus_reported_total_mw"] == pytest.approx(
        0.01
    )
    assert not frame["plant"].str.contains("balanc|fudge", case=False, regex=True).any()


def test_detailed_technology_and_sector_reconciliation_is_source_bounded():
    _, summary = build_generator_census(SOURCE)

    assert summary["technology_capacity_mw"]["hydro"] == pytest.approx(2284.421)
    assert summary["technology_capacity_mw"]["thermal"] == pytest.approx(536.54)
    assert summary["technology_capacity_mw"]["wind"] == pytest.approx(71.525)
    assert summary["technology_capacity_mw"]["solar"] == pytest.approx(1519.67)

    assert summary["technology_residual_mw"]["hydro"] == pytest.approx(0.001)
    assert summary["technology_residual_mw"]["thermal"] == pytest.approx(0.0)
    assert summary["technology_residual_mw"]["wind"] == pytest.approx(-0.005)
    assert summary["technology_residual_mw"]["solar"] == pytest.approx(0.01)

    assert summary["sector_capacity_mw"]["state"] == pytest.approx(2409.776)
    assert summary["sector_capacity_mw"]["central"] == pytest.approx(359.58)
    assert summary["sector_capacity_mw"]["private"] == pytest.approx(1642.80)


def test_44_ksebl_hydro_stations_reconcile_to_official_rounding():
    frame, summary = build_generator_census(SOURCE)

    hydro = frame.loc[frame["official_category"].eq("Hydel: KSEB")]
    assert len(hydro) == 44
    assert hydro["capacity_mw"].sum() == pytest.approx(2196.361)
    assert summary["official_category_anchor_mw"]["Hydel: KSEB"] == pytest.approx(
        2196.36
    )
    assert set(["Thottiyar HEP", "Pallivasal Extension Scheme"]).issubset(
        set(hydro["plant"])
    )
    micro = hydro.loc[hydro["plant"].eq("Poringalkuthu Micro")].iloc[0]
    assert micro["capacity_mw"] == pytest.approx(0.011)


def test_private_hydro_and_wind_match_official_ipp_cpp_buckets():
    frame, _ = build_generator_census(SOURCE)

    def total(category: str) -> float:
        return float(
            frame.loc[frame["official_category"].eq(category), "capacity_mw"].sum()
        )

    assert total("Hydel: CPP") == pytest.approx(33.50)
    assert total("Hydel: IPP") == pytest.approx(54.56)
    assert total("Wind:CPP") == pytest.approx(11.00)
    assert total("Wind: IPP") == pytest.approx(58.50)
    assert total("Solar :IPP") == pytest.approx(204.00)


def test_distributed_solar_remains_aggregate_and_visible():
    frame, summary = build_generator_census(SOURCE)

    lt = frame.loc[frame["asset_id"].eq("solar-other-lt-lr-prosumers")].iloc[0]
    assert lt["capacity_mw"] == pytest.approx(1081.87)
    assert lt["capacity_basis"] == "distributed_aggregate"
    assert lt["model_admission"] == "aggregate_capacity_not_individual_asset"

    assert summary["official_category_anchor_mw"]["Solar other than KSEBL"] == pytest.approx(
        1264.23
    )
    assert summary["category_capacity_mw"]["Solar other than KSEBL"] == pytest.approx(
        1264.24
    )


def test_bses_and_kpcl_are_preserved_as_historical_exclusions_not_capacity():
    data = load_generator_census(SOURCE)
    frame, summary = reconcile_generator_census(data)

    excluded = {
        item["plant"]: item["stale_portal_capacity_mw"]
        for item in summary["historical_exclusions"]
    }
    assert excluded["BSES Kochi"] == pytest.approx(157.0)
    assert excluded["Kasaragod Power / KPCL"] == pytest.approx(20.44)
    assert "BSES Kochi" not in set(frame["plant"])
    assert "Kasaragod Power / KPCL" not in set(frame["plant"])


def test_release_gate_closes_capacity_accounting_only():
    _, summary = build_generator_census(SOURCE)
    gate = summary["release_gate"]

    assert gate["capacity_accounting_reconciled"] is True
    assert gate["every_physical_rooftop_asset_individually_enumerated"] is False
    assert gate["plant_level_hourly_availability_verified"] is False
    assert gate["unit_outage_derating_verified"] is False
    assert gate["station_generation_reconciled"] is False
    assert gate["dispatch_model_ready_from_installed_capacity_alone"] is False
