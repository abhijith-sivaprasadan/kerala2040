"""Cross-year analogue is source-masked and must not use target-year observations."""
import importlib.util
from datetime import date, timedelta
from pathlib import Path

import pytest

PATH = Path(__file__).resolve().parents[1] / "analysis/benchmark_sldc_cross_year_gaps.py"
SPEC = importlib.util.spec_from_file_location("cross_year", PATH)
assert SPEC and SPEC.loader
module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(module)


def fixture_data():
    first = date(2020, 1, 1)
    return {
        first + timedelta(days=i): (60 + (i // 365) * 4) * (1.05 if (first + timedelta(days=i)).day == 20 else 1)
        for i in range(365 * 5)
    }


def test_target_mask_is_mandatory():
    data = fixture_data()
    day = date(2022, 9, 20)
    with pytest.raises(ValueError, match="masked"):
        module.predict(data, day)
    actual = data.pop(day)
    assert actual > 0
    predictions = module.predict(data, day)
    assert predictions["historical_analogue_years"] >= 3
    assert predictions["historical_adjusted"] is not None


def test_no_analogue_is_null():
    day = date(2024, 2, 29)
    data = {day + timedelta(days=i): 70 for i in range(-7, 8) if i}
    result = module.predict(data, day)
    assert result["historical_adjusted"] is None
    assert result["interpolation"] == pytest.approx(70)


def test_paired_comparison_has_equal_n():
    result = module.benchmark(fixture_data())
    pair = result["paired_interpolation_vs_historical"]
    assert pair["interpolation"]["n"] == pair["historical_adjusted"]["n"]
    assert pair["interpolation"]["n"] > 100
