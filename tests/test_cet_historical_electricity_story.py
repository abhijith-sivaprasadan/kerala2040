"""CET 2026 historical story: protect source population and release boundaries."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/evidence/sldc/sldc_daily_advanced_aggregate_2026_09_23.json"
STORY = ROOT / "data/evidence/sldc/cet_historical_electricity_story_2026_09_24.json"
FIGURES = [
    "cet-historical-official-consumption-20260924.svg",
    "cet-historical-matched-month-demand-20260924.svg",
    "cet-historical-import-hydro-shares-20260924.svg",
    "cet-historical-evening-peaks-20260924.svg",
]


def test_historical_story_source_reconciles_without_filling_missing_dates():
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    story = json.loads(STORY.read_text(encoding="utf-8"))
    official = story["official_economic_review_2025_kerala_consumption_mu"]
    assert list(official) == ["2020-21", "2021-22", "2022-23", "2023-24", "2024-25"]
    assert official == {
        "2020-21": 22540.32,
        "2021-22": 23983.42,
        "2022-23": 25383.77,
        "2023-24": 28360.25,
        "2024-25": 29311.76,
    }
    assert len(story["sldc_observed_fy"]) == 6
    for year, row in story["sldc_observed_fy"].items():
        src = source["fy"][year]
        assert row["qualified_days"] == src["n"]
        assert row["calendar_days"] == src["calendar_days_in_scope"]
        assert row["observed_sum_mu"] == src["observed_consumption_mu"]
        assert row["observed_daily_mean_mu"] == src["daily_consumption_mean_mu"]
        assert row["net_import_energy_share_pct"] == src["net_import_share_weighted_pct"]
        assert row["hydel_energy_share_pct"] == src["hydel_share_weighted_pct"]
        assert row["peak_evening_p95_mw"] == src["evening_peak_p95_mw"]
        assert row["peak_evening_max_mw"] == src["max_evening_peak_mw"]
        assert row["qualified_days"] <= row["calendar_days"]
    assert story["paired_fy_2020_21_2025_26"] == source["matched_2020_21_vs_2025_26"]
    assert story["paired_recent_comparisons"] == source["matched_other_fys"]
    assert story["paired_months"] == source["matched_months"]
    assert sum(r["n"] for r in story["paired_months"].values()) == 356
    assert story["qa"]["missing_fy2024_25"] == 11
    assert story["qa"]["no_imputation"] is True
    assert story["qa"]["interval_telemetry_present"] is False
    assert story["sldc_observed_fy"]["2020-21"]["qualified_days"] == 365
    assert story["sldc_observed_fy"]["2020-21"]["observed_sum_mu"] != official["2020-21"]
    assert story["sldc_observed_fy"]["2024-25"]["observed_sum_mu"] != official["2024-25"]
    assert story["qa"]["peak_fields_non_interchangeable"]["paired_days"] == 2574
    assert story["qa"]["peak_fields_non_interchangeable"]["exact_equal_days"] == 15
    assert story["qa"]["sldc_source_qualified_days"] == source["qa"]["qualified_days"]
    assert story["source"]["sldc_archive_sha256"] == source["qa"]["source_archive_sha256"]


def test_historical_story_figures_are_scoped_and_source_qualified():
    for name in FIGURES:
        text = (ROOT / "docs/assets" / name).read_text(encoding="utf-8")
        assert text.startswith("<svg ")
        assert "Kerala2040 · CET 2026" in text
        assert "Source:" in text
        assert "<script" not in text
