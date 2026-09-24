"""WP6 cooling/TES source and thermodynamic counterfactual contracts."""
import copy
import json
from pathlib import Path

import pytest

from kerala2040.flexibility_cooling import (
    build_pilot,
    read_config,
    simulate,
)

ROOT = Path(__file__).resolve().parents[1]


def test_synthetic_three_cases_deliver_common_comfort_and_close_end_states():
    pilot = build_pilot()
    assert pilot["classification"] == (
        "WP6_SYNTHETIC_24H_1R1C_COOLING_COMPARISON_NOT_KERALA_GRID_RESULT"
    )
    assert set(pilot["cases"]) == {
        "conventional", "precooling", "chilled_water_storage"
    }
    assert pilot["spatial_scope"].startswith("one illustrative")
    baseline = pilot["cases"]["conventional"]["summary"]
    cool = pilot["cases"]["precooling"]["summary"]
    store = pilot["cases"]["chilled_water_storage"]["summary"]
    for scenario in pilot["cases"].values():
        assert len(scenario["hourly"]) == 24
        assert scenario["summary"]["comfort_violation_hours"] == 0
        assert abs(scenario["summary"]["end_room_C"] - 25.5) < 1e-5
        assert scenario["summary"]["end_store_kWh_th"] == 0
        assert all(
            24 <= row["room_C"] <= 26
            and row["store_kWh_th"] >= 0
            and row["grid_kWh_e"] >= 0
            for row in scenario["hourly"]
        )
        assert scenario["summary"]["whole_day_peak_kW_e"] >= (
            scenario["summary"]["evening_peak_kW_e"]
        )
    assert cool["room_cooling_delivered_kWh_th"] > baseline["room_cooling_delivered_kWh_th"]
    assert cool["room_cooling_target_shortfall_kWh_th"] > 0
    assert cool["evening_grid_kWh_e"] < baseline["evening_grid_kWh_e"]
    assert store["total_grid_kWh_e"] > baseline["total_grid_kWh_e"]
    assert store["evening_grid_kWh_e"] < baseline["evening_grid_kWh_e"]
    assert store["evening_peak_kW_e"] < baseline["evening_peak_kW_e"]
    assert store["charged_kWh_th"] > store["discharged_to_room_kWh_th"]
    assert len(pilot["sensitivity"]) == 9
    assert all(s["comfort_violation_hours"] == 0 for s in pilot["sensitivity"])
    assert all(value is False for value in pilot["science_gates"].values())


def test_storage_hard_limits_and_dispatch_windows():
    cfg = read_config()
    trial = simulate(cfg, "chilled_water_storage")
    rows = trial["hourly"]
    assert all(row["thermal_charge_input_kWh_th"] == 0 for row in rows[7:])
    assert all(row["thermal_discharge_to_room_kWh_th"] == 0 for row in rows[:17])
    assert all(row["thermal_discharge_to_room_kWh_th"] == 0 for row in rows[22:])
    assert all(row["store_kWh_th"] <= 6 for row in rows)
    assert all(
        not (row["thermal_charge_input_kWh_th"] > 0
             and row["thermal_discharge_to_room_kWh_th"] > 0)
        for row in rows
    )


@pytest.mark.parametrize(
    ("path", "value"),
    [
        (("release", "numerical_kerala_2040_ready"), True),
        (("release", "actual_building_annual_savings_ready"), True),
        (("zone", "heat_capacity_kWh_per_K"), 0),
        (("storage", "charging_efficiency"), 1.1),
        (("storage", "initial_stored_kWh_th"), 3),
        (("hourly_outdoor_C",), [29, 30]),
    ],
)
def test_inputs_refuse_promoted_or_unphysical_assumptions(tmp_path, path, value):
    cfg = read_config()
    nested = copy.deepcopy(cfg)
    parent = nested
    for key in path[:-1]:
        parent = parent[key]
    parent[path[-1]] = value
    import yaml

    file = tmp_path / "invalid.yaml"
    file.write_text(yaml.safe_dump(nested), encoding="utf-8")
    with pytest.raises(ValueError):
        read_config(file)


def test_tighter_chiller_fails_if_actual_comfort_is_unmet():
    cfg = read_config()
    cfg["zone"]["ac_max_thermal_kW"] = 0.01
    with pytest.raises(ValueError, match="comfort"):
        simulate(cfg, "conventional")


def test_wp6_is_not_installed_as_a_statewide_calibrated_model():
    result = build_pilot()
    assert all(x is False for x in result["science_gates"].values())
    assert result["cases"]["conventional"]["summary"]["charged_kWh_th"] == 0
    assert result["cases"]["chilled_water_storage"]["summary"]["end_store_kWh_th"] == 0
    doc = (ROOT / "docs/WP6_COOLING_THERMAL_STORAGE_PILOT_2026_09_24.md").read_text(
        encoding="utf-8"
    )
    assert "not measured Kerala" in doc.lower()
    assert "setpoint shortfall" in doc.lower()
    assert "whole-day" in doc.lower()
    assert json.dumps(result, allow_nan=False)
