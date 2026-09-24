"""Synchronized synthetic WP6 site dispatch; never measured Kerala telemetry."""
from __future__ import annotations

from kerala2040.flexibility_cooling import read_config
from kerala2040.flexibility_cooling import simulate as cooling_simulate
from kerala2040.flexibility_dispatch import dispatch, load_spec
from kerala2040.flexibility_storage import load_spec as storage_spec
from kerala2040.flexibility_storage import simulate as storage_simulate

CLASSIFICATION = "WP6_SYNTHETIC_SYNCHRONIZED_SITE_NOT_KERALA_GRID_DISPATCH"
EVENING = range(17, 22)


def build_integrated() -> dict:
    """Compose one-hour component traces; no statewide scaling or inferred renewables."""
    ev = load_spec("ev")
    industry = load_spec("industry")
    cool = read_config()
    store = storage_spec()
    # Original pilots use distinct fictional site backgrounds. Exclude these
    # backgrounds, use a single authored shared load, and retain only incremental
    # flexible components. This is a new fictional co-location, NOT a Kerala site.
    background = store["hourly_background_site_kw"]
    if len(background) != 24 or any(x <= 0 for x in background):
        raise ValueError("Invalid shared 24-hour synthetic background")
    ev_cases = {p: dispatch(ev, "ev", p) for p in ("arrival_order", "managed")}
    ind_cases = {p: dispatch(industry, "industry", p) for p in ("arrival_order", "managed")}
    cool_cases = {p: cooling_simulate(cool, p) for p in ("conventional", "chilled_water_storage")}
    bess = storage_simulate(store, "bess")
    scenarios = {
        "unmanaged": ("arrival_order", "arrival_order", "conventional", False),
        "flexibility_only": ("managed", "managed", "chilled_water_storage", False),
        "bess_only": ("arrival_order", "arrival_order", "conventional", True),
        "combined": ("managed", "managed", "chilled_water_storage", True),
    }
    result = {}
    for name, (ev_policy, ind_policy, cooling_policy, use_bess) in scenarios.items():
        rows = []
        for h in range(24):
            ev_kw = ev_cases[ev_policy]["hourly"][h]["flexible_kw"]
            industry_kw = ind_cases[ind_policy]["hourly"][h]["flexible_kw"]
            cooling_kw = cool_cases[cooling_policy]["hourly"][h]["grid_kWh_e"]
            battery = bess["hourly"][h] if use_bess else None
            charge = battery["grid_charge_kwh"] if battery else 0.0
            discharge = battery["grid_discharge_kwh"] if battery else 0.0
            aux = battery["auxiliary_grid_kwh"] if battery else 0.0
            total = background[h] + ev_kw + industry_kw + cooling_kw + charge + aux - discharge
            if total < -1e-8:
                raise AssertionError("Unintended site export")
            rows.append({
                "hour": h, "background_kw": background[h], "ev_kw": ev_kw,
                "industrial_kw": industry_kw, "cooling_kw": cooling_kw,
                "battery_charge_kw": charge, "battery_discharge_kw": discharge,
                "battery_auxiliary_kw": aux, "net_site_kw": round(total, 6),
            })
        total = sum(r["net_site_kw"] for r in rows)
        components = (sum(background)
                      + ev_cases[ev_policy]["summary"]["electricity_kwh"]
                      + ind_cases[ind_policy]["summary"]["electricity_kwh"]
                      + cool_cases[cooling_policy]["summary"]["total_grid_kWh_e"]
                      + (bess["summary"]["daily_grid_energy_change_kwh"] if use_bess else 0))
        if abs(total - components) > 3e-5:
            raise AssertionError("Synchronized aggregate electricity does not close")
        result[name] = {
            "hourly": rows,
            "summary": {
                "daily_grid_kwh": round(total, 6),
                "whole_day_peak_kw": max(r["net_site_kw"] for r in rows),
                "evening_peak_kw": max(rows[h]["net_site_kw"] for h in EVENING),
                "evening_grid_kwh": round(sum(rows[h]["net_site_kw"] for h in EVENING), 6),
                "ev_service_kwh": ev_cases[ev_policy]["summary"]["delivered_service_kwh"],
                "industry_service_kwh": ind_cases[ind_policy]["summary"]["delivered_service_kwh"],
                "cooling_comfort_violation_hours": cool_cases[cooling_policy]["summary"]["comfort_violation_hours"],
                "cooling_end_room_c": cool_cases[cooling_policy]["summary"]["end_room_C"],
                "battery_terminal_kwh": bess["summary"]["terminal_stored_kwh"] if use_bess else 0,
            },
        }
    for name, case in result.items():
        s = case["summary"]
        if s["cooling_comfort_violation_hours"] or abs(s["battery_terminal_kwh"]) > 1e-7:
            raise AssertionError("Integrated case violates terminal/comfort service")
        if (abs(s["ev_service_kwh"] - result["unmanaged"]["summary"]["ev_service_kwh"]) > 1e-6
                or abs(s["industry_service_kwh"] - result["unmanaged"]["summary"]["industry_service_kwh"]) > 1e-6):
            raise AssertionError("Integrated shifting changed delivered service")
    return {
        "classification": CLASSIFICATION,
        "time_basis": "24 fictional aligned one-hour slots, not Kerala timestamps",
        "background_provenance": "authored WP6 storage pilot synthetic load, counted once",
        "renewable_profile": None,
        "observed_kerala_interval_demand": None,
        "observed_kerala_generation": None,
        "observed_kerala_imports": None,
        "cases": result,
        "release": {
            "observed_kerala_hourly_dispatch": False,
            "statewide_mw_mwh_or_emissions": False,
            "measured_coincident_peak": False,
            "kerala_pumped_storage_project": False,
            "optimal_joint_dispatch": False,
        },
    }
