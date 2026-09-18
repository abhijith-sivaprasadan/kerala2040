import csv
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "external" / "cstep_2024"


def _rows(name: str):
    with (DATA / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def test_cstep_metadata_keeps_external_classification_and_hourly_gap():
    meta = yaml.safe_load((DATA / "metadata.yaml").read_text(encoding="utf-8"))

    assert meta["classification"] == "published_external_scenario"
    assert meta["load_chronology"]["raw_fy2016_series_in_report"] is False
    assert meta["load_chronology"]["acquisition_priority"] == "critical"
    assert "Do not digitise" in meta["load_chronology"]["use_rule"]


def test_cstep_demand_projection_preserves_published_2040_values():
    rows = _rows("demand_projection_fy2023_fy2040.csv")
    assert len(rows) == 18
    final = rows[-1]

    assert final["financial_year"] == "2040"
    assert final["published_bau_demand_mu"] == "40446"
    assert final["ev_demand_mu"] == "1286"
    assert final["induction_cooktop_demand_mu"] == "415"
    assert final["published_final_demand_with_td_losses_mu"] == "45519"
    assert all(row["classification"] == "published_external_scenario" for row in rows)


def test_cstep_capacity_paths_are_external_benchmarks():
    bau = _rows("capacity_additions_bau_fy2023_fy2040.csv")[-1]
    high = _rows("capacity_additions_high_re_fy2023_fy2040.csv")[-1]

    assert bau["solar_cumulative_addition_mw"] == "8391"
    assert bau["wind_cumulative_addition_mw"] == "1794"
    assert high["solar_cumulative_addition_mw"] == "10558"
    assert high["wind_cumulative_addition_mw"] == "2754"
    assert high["nuclear_cumulative_addition_mw"] == "1056"


def test_cstep_storage_values_are_not_silently_unit_corrected():
    rows = _rows("storage_benchmarks.csv")
    assert len(rows) == 4
    assert all(
        row["interpretation_status"] == "requires_underlying_method_verification"
        for row in rows
    )
    assert max(float(row["implied_duration_hours"]) for row in rows) > 1900


def test_published_rounding_discrepancies_are_small_and_preserved():
    history = _rows("historical_category_consumption_fy2016_fy2022.csv")
    history_components = [
        "domestic_lt_mu",
        "commercial_lt_mu",
        "industrial_lt_mu",
        "ht_eht_mu",
        "public_lighting_mu",
        "agricultural_lt_mu",
        "licensees_mu",
        "railway_traction_mu",
    ]
    for row in history:
        component_sum = sum(int(row[column]) for column in history_components)
        published = int(row["published_total_mu"])
        assert abs(component_sum - published) <= 1

    projected = _rows("demand_projection_fy2023_fy2040.csv")
    projected_components = [
        "domestic_mu",
        "commercial_lt_mu",
        "industrial_lt_mu",
        "ht_eht_mu",
        "public_lighting_mu",
        "railway_traction_mu",
        "licensees_mu",
        "agricultural_lt_mu",
    ]
    for row in projected:
        component_sum = sum(int(row[column]) for column in projected_components)
        published = int(row["published_bau_demand_mu"])
        assert abs(component_sum - published) <= 2
