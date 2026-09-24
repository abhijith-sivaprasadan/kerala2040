"""Synthetic battery/pumped-storage screen: energy, deadlines and honest limits."""
import copy
import json
from pathlib import Path

import pytest

from kerala2040.flexibility_storage import (
    build_screen,
    hydraulic_kwh_per_m3,
    load_spec,
    simulate,
    validate_spec,
)

ROOT = Path(__file__).resolve().parents[1]


def test_fixed_storage_service_energy_balance_zero_terminal_and_peak_labels():
    result = build_screen()
    assert result["classification"] == (
        "WP6_SYNTHETIC_BESS_PSP_FIXED_SERVICE_NOT_KERALA_FEASIBILITY"
    )
    baseline = result["baseline"]
    assert len(result["cases"]) == 2
    assert all(value is False for value in result["release"].values())
    for kind in ("bess", "psp"):
        trial = result["cases"][kind]
        s = trial["summary"]
        assert len(trial["hourly"]) == 24
        assert abs(s["terminal_stored_kwh"]) < 1e-6
        assert s["discharge_to_site_kwh"] == pytest.approx(10, abs=1e-5)
        assert s["charge_grid_kwh"] > 10
        assert s["daily_grid_energy_change_kwh"] > 0
        assert s["daily_site_grid_kwh"] > baseline["daily_site_grid_kwh"]
        assert s["whole_day_site_peak_kw"] >= s["evening_site_peak_kw"]
        assert s["evening_site_peak_kw"] < baseline["evening_site_peak_kw"]
        assert s["round_trip_net_energy_ratio"] < 1
        assert len(result["sensitivities"][kind]) == 9
        assert any(not r["feasible"] for r in result["sensitivities"][kind])
        assert any(r["feasible"] for r in result["sensitivities"][kind])
        for r in trial["hourly"]:
            assert r["stock_kwh_stored"] >= -1e-6
            assert r["grid_site_kw"] >= 0
            assert not (r["grid_charge_kwh"] > 0
                        and r["grid_discharge_kwh"] > 0)
            assert r["grid_charge_kwh"] <= 4 + 1e-6
            assert r["grid_discharge_kwh"] <= 3 + 1e-6
        for r in result["sensitivities"][kind]:
            if not r["feasible"]:
                assert r["reason"].startswith("Infeasible")
                assert r["daily_site_grid_kwh"] is None
    assert result["cases"]["bess"]["summary"]["max_upper_water_m3_analogue"] is None
    assert result["cases"]["psp"]["summary"]["max_upper_water_m3_analogue"] > 0


def test_psp_hydraulic_accounting_is_synthetic_not_existing_reservoir():
    cfg = load_spec()
    psp = cfg["storage"]["psp"]
    assert hydraulic_kwh_per_m3(psp) == pytest.approx(
        1000 * 9.81 * 300 / 3_600_000
    )
    trial = simulate(cfg, "psp")
    factor = hydraulic_kwh_per_m3(psp)
    for r in trial["hourly"]:
        assert r["upper_water_m3_analogue"] == pytest.approx(
            r["stock_kwh_stored"] / factor, abs=2e-6
        )
    assert trial["hourly"][-1]["upper_water_m3_analogue"] == 0


@pytest.mark.parametrize(
    ("path", "value"),
    [
        (("release", "calibrated_2040_capacity"), True),
        (("release", "verified_pumped_reservoir_pair"), True),
        (("storage", "psp", "hypothetical_net_head_m"), 0),
        (("storage", "bess", "charge_efficiency"), 1.01),
        (("storage", "psp", "discharge_efficiency"), -1),
        (("hourly_background_site_kw",), [5, 6]),
        (("storage", "bess", "capacity_kwh_stored"), 0),
    ],
)
def test_wrong_source_or_unphysical_input_rejected(path, value):
    cfg = copy.deepcopy(load_spec())
    node = cfg
    for key in path[:-1]:
        node = node[key]
    node[path[-1]] = value
    with pytest.raises(ValueError):
        validate_spec(cfg)


def test_charging_window_infeasible_is_not_hidden_as_partial_service():
    cfg = load_spec()
    cfg["storage"]["bess"]["capacity_kwh_stored"] = 2
    with pytest.raises(ValueError, match="Infeasible"):
        simulate(cfg, "bess")
    cfg = load_spec()
    cfg["storage"]["psp"]["charge_max_kw"] = 0.01
    with pytest.raises(ValueError, match="Infeasible"):
        simulate(cfg, "psp")


def test_site_discloses_not_real_hydro_project():
    html = (ROOT / "docs/index.html").read_text(encoding="utf-8")
    methods = (
        ROOT / "docs/WP6_BESS_PUMPED_STORAGE_SCREEN_2026_09_24.md"
    ).read_text(encoding="utf-8")
    for name in ("wp6StorageStatus", "wp6StorageCards", "wp6StorageChart",
                 "wp6StorageStock", "wp6StorageSensitivity"):
        assert f'id="{name}"' in html
    assert "not a pumped-storage site design" in methods.lower()
    assert "not verified kerala" in methods.lower()
    assert "CEA" in methods
    assert json.dumps(build_screen(), allow_nan=False)
