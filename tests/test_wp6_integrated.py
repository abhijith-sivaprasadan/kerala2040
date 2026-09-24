"""Integrated WP6 site: service, energy, peak and provenance regression."""
import pytest

from kerala2040.flexibility_integrated import CLASSIFICATION, build_integrated


@pytest.fixture(scope="module")
def product():
    return build_integrated()


def test_four_synchronized_cases(product):
    assert product["classification"] == CLASSIFICATION
    assert set(product["cases"]) == {"unmanaged", "flexibility_only", "bess_only", "combined"}
    assert all(len(case["hourly"]) == 24 for case in product["cases"].values())
    assert all(flag is False for flag in product["release"].values())
    assert product["renewable_profile"] is None
    assert product["observed_kerala_interval_demand"] is None


def test_hourly_conservation_and_joint_peak(product):
    for case in product["cases"].values():
        rows, summary = case["hourly"], case["summary"]
        for row in rows:
            expected = (row["background_kw"] + row["ev_kw"] + row["industrial_kw"]
                        + row["cooling_kw"] + row["battery_charge_kw"]
                        + row["battery_auxiliary_kw"] - row["battery_discharge_kw"])
            assert row["net_site_kw"] == pytest.approx(expected, abs=3e-6)
            assert not (row["battery_charge_kw"] and row["battery_discharge_kw"])
        assert summary["daily_grid_kwh"] == pytest.approx(sum(r["net_site_kw"] for r in rows), abs=1e-5)
        assert summary["whole_day_peak_kw"] == max(r["net_site_kw"] for r in rows)
        assert summary["evening_peak_kw"] == max(rows[h]["net_site_kw"] for h in range(17, 22))


def test_service_preserved_and_battery_losses(product):
    base = product["cases"]["unmanaged"]["summary"]
    for case in product["cases"].values():
        s = case["summary"]
        assert s["ev_service_kwh"] == base["ev_service_kwh"]
        assert s["industry_service_kwh"] == base["industry_service_kwh"]
        assert s["cooling_comfort_violation_hours"] == 0
        assert s["battery_terminal_kwh"] == 0
    assert product["cases"]["bess_only"]["summary"]["daily_grid_kwh"] > base["daily_grid_kwh"]
