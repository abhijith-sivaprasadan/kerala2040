"""WP6 synthetic EV and noncritical industrial flexibility service-preservation tests."""
import copy

import pytest

from kerala2040.flexibility_dispatch import (
    build_demonstration,
    dispatch,
    load_spec,
    validate_spec,
)


@pytest.mark.parametrize("kind", ["ev", "industry"])
def test_same_terminal_service_and_fair_shared_capacity(kind):
    d = build_demonstration(kind)
    assert d["kind"] == kind
    assert len(d["baseline"]["hourly"]) == len(d["managed"]["hourly"]) == 24
    assert len(d["sensitivity"]) == 9
    assert all(v is False for v in d["science_gates"].values())
    assert d["comparison"]["total_electricity_change_kwh"] == 0
    assert d["comparison"]["evening_flexible_energy_change_kwh"] < 0
    assert d["comparison"]["evening_site_peak_change_kw"] < 0
    for scenario in ("baseline", "managed"):
        out = d[scenario]
        assert out["summary"]["missed_deadlines"] == 0
        assert all(job["met_deadline"] for job in out["jobs"])
        assert all(abs(job["required_service_kwh"] -
                       job["delivered_service_kwh"]) < 1e-5 for job in out["jobs"])
        assert all(row["flexible_kw"] <=
                   out["summary"]["shared_flexible_limit_kw"] + 1e-6
                   for row in out["hourly"])
        assert all(abs(row["site_total_kw"] - row["background_kw"] -
                       row["flexible_kw"]) < 2e-5 for row in out["hourly"])
        assert out["summary"]["whole_day_site_peak_kw"] >= (
            out["summary"]["evening_site_peak_kw"]
        )
    assert all(row["missed_deadlines"] == 0 for row in d["sensitivity"])
    assert all(row["baseline_evening_site_peak_kw"] >=
               row["managed_evening_site_peak_kw"] for row in d["sensitivity"])


def test_ev_arrivals_departures_and_energy_not_a_fake_saving():
    d = build_demonstration("ev")
    a = d["baseline"]["summary"]
    b = d["managed"]["summary"]
    assert a["electricity_kwh"] == b["electricity_kwh"]
    assert a["delivered_service_kwh"] == b["delivered_service_kwh"]
    for result in (d["baseline"], d["managed"]):
        by_id = {row["id"]: row for row in result["jobs"]}
        for vehicle in d["input"]["vehicles"]:
            record = by_id[vehicle["id"]]
            assert record["departure_battery_kwh"] == pytest.approx(
                vehicle["initial_battery_kwh"] + vehicle["required_battery_kwh"]
            )
            for hour in range(24):
                electricity = result["hourly"][hour]["job_grid_kw"][vehicle["id"]]
                if hour < vehicle["arrival_hour"] or hour >= vehicle["departure_hour"]:
                    assert electricity == 0
    assert d["comparison"]["evening_site_peak_change_kw"] < 0


def test_industrial_critical_background_never_curtailed_and_jobs_completed():
    d = build_demonstration("industry")
    expected = d["input"]["hourly_nonshiftable_site_load_kw"]
    assert d["input"]["nonshiftable_safety_and_critical_duty_always_on"]
    assert d["input"]["industry_scope"]["critical_load_curtailment_allowed"] is False
    assert d["input"]["industry_scope"]["utility_or_residual_recovery_claim"] is False
    for scenario in (d["baseline"], d["managed"]):
        assert [r["background_kw"] for r in scenario["hourly"]] == expected
        for job in scenario["jobs"]:
            assert job["departure_battery_kwh"] is None
            assert job["met_deadline"] is True
    assert sum(job["delivered_service_kwh"]
               for job in d["managed"]["jobs"]) == pytest.approx(46)


@pytest.mark.parametrize("kind", ["ev", "industry"])
def test_no_unmet_jobs_silently_accepted(kind):
    spec = load_spec(kind)
    cap = ("managed_shared_charger_limit_kw" if kind == "ev" else
           "managed_shared_flexible_limit_kw")
    spec[cap] = 0.01
    with pytest.raises(ValueError, match="Infeasible deadline"):
        dispatch(spec, kind, "managed")


@pytest.mark.parametrize("kind", ["ev", "industry"])
def test_no_real_world_reclassification(kind):
    bad = copy.deepcopy(load_spec(kind))
    first = next(iter(bad["release"]))
    bad["release"][first] = True
    with pytest.raises(ValueError, match="release"):
        validate_spec(bad, kind)


def test_ev_capacity_and_industry_safety_config_fail_closed():
    ev = load_spec("ev")
    ev["vehicles"][0]["battery_capacity_kwh"] = 20
    with pytest.raises(ValueError, match="battery capacity"):
        validate_spec(ev, "ev")
    industry = load_spec("industry")
    industry["nonshiftable_safety_and_critical_duty_always_on"] = False
    with pytest.raises(ValueError, match="Safety-critical"):
        validate_spec(industry, "industry")
    industry = load_spec("industry")
    industry["industry_scope"]["critical_load_curtailment_allowed"] = True
    with pytest.raises(ValueError, match="safety"):
        validate_spec(industry, "industry")
