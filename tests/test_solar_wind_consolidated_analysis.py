"""Protect corrected source interpretation in consolidated wind/solar analysis."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
QA = ROOT / "data/evidence/solar/solar_wind_consolidated_numeric_2026_09_22.json"
MANIFEST = ROOT / "data/evidence/solar/solar_batch_2026_09_21_originals_manifest.json"


def test_source_status_and_rejected_all_zero_irradiance() -> None:
    d = json.loads(QA.read_text(encoding="utf-8"))
    m = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert d["NWIC_FY2024_25"]["solar"]["fy_rows"] == 6007
    assert d["NWIC_FY2024_25"]["solar"]["fy_zeros"] == 6007
    assert d["NWIC_FY2024_25"]["solar"]["fy_nonzero"] == 0
    assert d["NWIC_FY2024_25"]["wind"]["fy_rows"] == 10946
    assert d["data_readiness"]["NWIC_solar_baseline_valid"] is False
    assert d["data_readiness"]["NWIC_wind_baseline_partial"] is True
    assert d["data_readiness"]["raw_17_assets_archived_in_public_GitHub_release"] is False
    assert m["release_uploaded"] is False


def test_six_city_samples_are_only_illustrations_and_unit_ratios() -> None:
    d = json.loads(QA.read_text(encoding="utf-8"))
    sites = d["six_city_illustrative"]
    assert len(sites) == 6
    assert d["solar_unit_reconciliation"]["full_raster_checked"] is False
    for site in sites:
        assert 1400 < site["pvout_kWh_per_kWp_year"] < 1700
        assert 3.5 < site["pvout_kWh_per_kWp_mean_day"] < 5.0
        assert abs(site["pvout_kWh_per_kWp_year"] /
                   site["pvout_kWh_per_kWp_mean_day"] - 365.25) < 0.05
        assert abs(site["pvout_annual_vs_month_sum_pct"]) < 0.012
        assert 0 < site["niwe_mean_wind_m_s_150m"] < 15
        assert 0 < site["niwe_nearest_point_approx_km"] < 0.3


def test_floating_pv_report_is_alternative_scenarios_not_projects() -> None:
    f = json.loads(QA.read_text(encoding="utf-8"))[
        "floating_solar_from_user_supplied_NISE_2026_report"
    ]
    assert f["Kerala_20percent_area_scenario_GWp"] == 2.22
    assert f["Kerala_feasible_scenario_GWp"] == 5.73
    assert f["Kerala_20percent_area_scenario_km2"] < f["Kerala_feasible_area_km2"]
    assert f["classification"].endswith("not_site_permit")
