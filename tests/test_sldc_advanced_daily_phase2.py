"""Synthetic-only tests for public SLDC advanced daily analysis helpers.

Original third-party source files belong in the private archive, not in CI.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path


MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "analysis"
    / "analyze_sldc_2019_2026.py"
)
SPEC = importlib.util.spec_from_file_location("sldc_advanced_daily", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
ANALYSIS = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ANALYSIS)


def test_none_and_ratio_denominator_guard():
    assert ANALYSIS.f("") is None
    assert ANALYSIS.f(None) is None
    assert ANALYSIS.mean([]) is None
    assert ANALYSIS.ratio(10, 0) is None
    assert ANALYSIS.ratio(20, 100) == 20.0


def test_interpolated_quantiles():
    assert ANALYSIS.percentile([4, 2, 3, 1], 0.5) == 2.5
    assert ANALYSIS.percentile([2, 2, 7], 0.9) == 6.0


def test_fiscal_year_month_day_matching_is_calendar_not_position():
    assert ANALYSIS.md("2020-04-01") == ANALYSIS.md("2025-04-01")
    assert ANALYSIS.md("2020-02-29") != ANALYSIS.md("2026-02-28")


def test_season_boundaries():
    assert ANALYSIS.season(3) == "summer_MarMay"
    assert ANALYSIS.season(5) == "summer_MarMay"
    assert ANALYSIS.season(6) == "monsoon_JunSep"
    assert ANALYSIS.season(9) == "monsoon_JunSep"
    assert ANALYSIS.season(10) == "other_OctFeb"
    assert ANALYSIS.season(2) == "other_OctFeb"
