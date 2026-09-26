"""Regression gates for observed-daily-anchored synthetic quarter-hour load."""
import importlib.util
from datetime import date
from pathlib import Path

import pytest

MODULE = Path(__file__).resolve().parents[1] / "scripts/build_sldc_synthetic_15min.py"
SPEC = importlib.util.spec_from_file_location("sldc_synthetic", MODULE)
assert SPEC and SPEC.loader
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)


@pytest.fixture(scope="module")
def product():
    rows = mod.read_daily()
    return rows, *mod.generate(rows)


def test_source_calendar_and_observed_count(product):
    rows, daily, _, report = product
    assert len(rows) == len(daily) == 365
    assert report["observed_days"] == 354
    assert report["estimated_days"] == 11
    assert report["unavailable_days"] == 0
    assert report["observed_days_energy_mu"] == pytest.approx(30666.2569)
    assert all(d["source_sha256"] is None for d in daily if d["anchor_status"] != "observed_daily_anchor")


def test_every_scenario_reconciles_every_day(product):
    _, daily, intervals, _ = product
    assert len(intervals) == 365 * 96 * 3
    grouped = {}
    for r in intervals:
        key = (r["date_ist"], r["scenario_id"])
        grouped.setdefault(key, []).append(r)
        assert r["classification"] == mod.CLASSIFICATION
        assert r["demand_mw"] > 0
        assert r["interval_hours"] == 0.25
    for d in daily:
        for scenario in mod.METHODS:
            slots = grouped[d["date"], scenario]
            assert len(slots) == 96
            assert sum(x["demand_mw"] for x in slots) / 4000 == pytest.approx(d["daily_energy_mu"], abs=1e-9)


def test_determinism_and_missingness(product):
    rows, daily, _, report = product
    assert mod.shape(date(2024, 9, 20), "evening_stress") == mod.shape(date(2024, 9, 20), "evening_stress")
    assert mod.shape(date(2024, 9, 20), "flat") != mod.shape(date(2024, 9, 20), "evening_stress")
    assert report["benchmark"]["interpolation"]["held_out_observed_days"] > 300
    _, _, strict = mod.generate(rows, estimate_missing=False)
    assert strict["estimated_days"] == 0
    assert strict["unavailable_days"] == 11
    assert strict["reconstructed_full_period_mu"] is None
    assert sum(d["anchor_status"] == "estimated_daily_anchor" for d in daily) == 11
