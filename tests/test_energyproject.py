import importlib.util
from pathlib import Path

import pytest

spec = importlib.util.spec_from_file_location(
    "ingest_energyproject", Path(__file__).resolve().parents[1] / "scripts/ingest_energyproject.py"
)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def day(date, value):
    return {"date": date, "interval_min": 15,
            "series": [{"t": f"{h:02d}:{m:02d}", "demand": value}
                       for h in range(24) for m in (0, 15, 30, 45)]}


def test_average_excludes_missing_observations_without_inventing_zero():
    days = [day("2026-09-01", 100), day("2026-09-02", 200)]
    days[1]["series"][0]["demand"] = None
    result = module.average_profile(days, ("demand",))
    assert len(result) == 96
    assert result[0]["demand"] == 100
    assert result[0]["sample_counts"]["demand"] == 1
    assert result[1]["demand"] == 150
    assert result[1]["sample_counts"]["demand"] == 2


@pytest.mark.parametrize("corruption", ["duplicate_day", "missing_interval", "infinite"])
def test_rejects_invalid_interval_products(corruption):
    days = [day("2026-09-01", 100)]
    if corruption == "duplicate_day":
        days.append(day("2026-09-01", 200))
    elif corruption == "missing_interval":
        days[0]["series"].pop()
    else:
        days[0]["series"][0]["demand"] = float("inf")
    with pytest.raises(ValueError):
        module.average_profile(days, ("demand",))
