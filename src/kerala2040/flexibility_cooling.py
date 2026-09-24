"""Reproducible WP6 cooling-flexibility thought experiment.

Synthetic 1R1C zone. No ERA5, SLDC, Kerala AC fleet, tariff or weather claims.
One-hour Euler balance; cold storage is an independent charging chiller.
"""
from __future__ import annotations

import copy
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / "configs/wp6_cooling_tes_illustrative.yaml"
CLASSIFICATION = "synthetic_illustrative_1R1C_24_hour_cooling_only_NOT_Kerala_observations"
CASES = ("conventional", "precooling", "chilled_water_storage")


def read_config(path: Path = CONFIG) -> dict:
    cfg = yaml.safe_load(path.read_text(encoding="utf-8"))
    if cfg.get("classification") != CLASSIFICATION or cfg.get("version") != 1:
        raise ValueError("WP6 synthetic-only provenance gate failed")
    temp = cfg["hourly_outdoor_C"]
    zone, store = cfg["zone"], cfg["storage"]
    if len(temp) != 24 or any(not 20 <= x <= 46 for x in temp):
        raise ValueError("Expected 24 explicitly illustrative ambient inputs")
    if (cfg["peak_window"]["start_hour_inclusive"],
            cfg["peak_window"]["end_hour_inclusive"]) != (17, 21):
        raise ValueError("Peak window no longer matches the scoped demonstration")
    if not 0 < zone["min_comfort_C"] < zone["baseline_setpoint_C"] < zone["max_comfort_C"]:
        raise ValueError("Comfort and setpoint inputs invalid")
    for key in ("heat_capacity_kWh_per_K", "envelope_UA_kW_per_K",
                "internal_gain_kW", "ac_max_thermal_kW", "cop_at_28C"):
        if zone[key] <= 0:
            raise ValueError("Non-positive building or chiller input")
    if not 0 < zone["cop_lower_bound"] <= zone["cop_upper_bound"]:
        raise ValueError("Invalid COP bounds")
    for key in ("charging_efficiency", "discharging_efficiency",
                "charging_COP_multiplier"):
        if not 0 < store[key] <= 1:
            raise ValueError("Invalid storage efficiency or charging COP")
    if not 0 <= store["self_discharge_fraction_per_hour"] < 1:
        raise ValueError("Invalid storage self-discharge")
    for key in ("thermal_energy_capacity_kWh", "charging_limit_kW_th",
                "discharging_limit_kW_th"):
        if store[key] <= 0:
            raise ValueError("Invalid storage size or thermal rate")
    if (store["initial_stored_kWh_th"] != 0
            or sorted(store["charging_hours"]) != list(range(7))
            or sorted(store["discharge_hours"]) != list(range(17, 22))):
        raise ValueError("Boundary requires empty initial storage and fixed charging window")
    if any(v is not False for v in cfg["release"].values()):
        raise ValueError("An unverified Kerala result has been promoted")
    return cfg


def _round(number: float) -> float:
    return round(number, 6)


def _cop(ambient_c: float, zone: dict) -> float:
    rated = zone["cop_at_28C"] - zone["cop_drop_per_outdoor_K"] * (ambient_c - 28)
    return max(zone["cop_lower_bound"], min(zone["cop_upper_bound"], rated))


def simulate(cfg: dict, case: str) -> dict:
    """Return a 24h physically balanced trace and technical outcomes."""
    if case not in CASES:
        raise ValueError("Unknown WP6 control case")
    zone, store = cfg["zone"], cfg["storage"]
    peak = cfg["peak_window"]
    indoor = float(zone["starting_indoor_C"])
    stock = float(store["initial_stored_kWh_th"])
    rows = []
    for hour, ambient in enumerate(cfg["hourly_outdoor_C"]):
        setpoint = float(zone["baseline_setpoint_C"])
        if case == "precooling" and cfg["precool"]["first_hour"] <= hour <= cfg["precool"]["last_hour"]:
            setpoint = float(cfg["precool"]["early_setpoint_C"])

        # Zone: C*(T_next-T_now) = UA*(T_out-T_now) + Q_internal - Q_room.
        heat = zone["envelope_UA_kW_per_K"] * (ambient - indoor) + zone["internal_gain_kW"]
        desired_cold = max(0.0, zone["heat_capacity_kWh_per_K"] * (indoor - setpoint) + heat)
        room_cold = min(zone["ac_max_thermal_kW"], desired_cold)
        new_indoor = indoor + (heat - room_cold) / zone["heat_capacity_kWh_per_K"]
        target_shortfall = desired_cold - room_cold

        old_stock = stock
        standing_loss = stock * store["self_discharge_fraction_per_hour"] if case == "chilled_water_storage" else 0.0
        stock -= standing_loss
        charged = discharged = 0.0
        direct_room = room_cold
        if case == "chilled_water_storage":
            if hour in store["discharge_hours"]:
                discharged = min(room_cold, store["discharging_limit_kW_th"],
                                 stock * store["discharging_efficiency"])
                stock -= discharged / store["discharging_efficiency"]
                direct_room -= discharged
            if hour in store["charging_hours"]:
                charged = min(store["charging_limit_kW_th"],
                              (store["thermal_energy_capacity_kWh"] - stock)
                              / store["charging_efficiency"])
                stock += charged * store["charging_efficiency"]

        cop = _cop(ambient, zone)
        direct_electricity = direct_room / cop
        charge_electricity = charged / (cop * store["charging_COP_multiplier"])
        discharge_electricity = discharged * store["discharge_pump_kWh_e_per_kWh_th"]
        grid_kw = direct_electricity + charge_electricity + discharge_electricity
        comfort_violation_c = max(zone["min_comfort_C"] - new_indoor,
                                  new_indoor - zone["max_comfort_C"], 0.0)
        # Independent conservation checks on unrounded values.
        if abs(zone["heat_capacity_kWh_per_K"] * (new_indoor - indoor)
               - (heat - room_cold)) > 1e-9:
            raise AssertionError("Building thermal energy balance violated")
        if abs(stock - (old_stock - standing_loss
                        + charged * store["charging_efficiency"]
                        - discharged / store["discharging_efficiency"])) > 1e-9:
            raise AssertionError("Cold-storage state balance violated")
        if stock < -1e-9 or stock > store["thermal_energy_capacity_kWh"] + 1e-9:
            raise AssertionError("Cold storage energy capacity violated")
        if abs(direct_room + discharged - room_cold) > 1e-9:
            raise AssertionError("Room cold supply counted twice")
        if charged > 0 and discharged > 0:
            raise AssertionError("Charge and discharge cannot occur simultaneously")

        rows.append({
            "hour": hour, "ambient_C": ambient,
            "target_C": _round(setpoint), "room_C": _round(new_indoor),
            "room_heat_gain_kWh_th": _round(heat),
            "room_cooling_requested_kWh_th": _round(desired_cold),
            "room_cooling_delivered_kWh_th": _round(room_cold),
            "target_shortfall_kWh_th": _round(target_shortfall),
            "comfort_violation_C": _round(comfort_violation_c),
            "direct_cooling_kWh_th": _round(direct_room),
            "thermal_charge_input_kWh_th": _round(charged),
            "thermal_discharge_to_room_kWh_th": _round(discharged),
            "standing_loss_kWh_th": _round(standing_loss),
            "store_kWh_th": _round(stock),
            "cop_direct": _round(cop),
            "grid_kWh_e": _round(grid_kw),
            "grid_direct_kWh_e": _round(direct_electricity),
            "grid_charge_kWh_e": _round(charge_electricity),
            "grid_pump_kWh_e": _round(discharge_electricity),
            "evening_window": peak["start_hour_inclusive"] <= hour <= peak["end_hour_inclusive"],
        })
        indoor = new_indoor

    energy = sum(r["grid_kWh_e"] for r in rows)
    evening = [r for r in rows if r["evening_window"]]
    summary = {
        "total_grid_kWh_e": _round(energy),
        "whole_day_peak_kW_e": _round(max(r["grid_kWh_e"] for r in rows)),
        "evening_peak_kW_e": _round(max(r["grid_kWh_e"] for r in evening)),
        "evening_grid_kWh_e": _round(sum(r["grid_kWh_e"] for r in evening)),
        "room_cooling_delivered_kWh_th": _round(sum(r["room_cooling_delivered_kWh_th"] for r in rows)),
        "room_cooling_target_shortfall_kWh_th": _round(sum(r["target_shortfall_kWh_th"] for r in rows)),
        "comfort_violation_hours": sum(r["comfort_violation_C"] > 1e-6 for r in rows),
        "maximum_comfort_violation_C": _round(max(r["comfort_violation_C"] for r in rows)),
        "minimum_room_C": _round(min(r["room_C"] for r in rows)),
        "maximum_room_C": _round(max(r["room_C"] for r in rows)),
        "end_room_C": _round(indoor),
        "end_store_kWh_th": _round(stock),
        "charged_kWh_th": _round(sum(r["thermal_charge_input_kWh_th"] for r in rows)),
        "discharged_to_room_kWh_th": _round(sum(r["thermal_discharge_to_room_kWh_th"] for r in rows)),
        "standing_loss_kWh_th": _round(sum(r["standing_loss_kWh_th"] for r in rows)),
    }
    if summary["comfort_violation_hours"] != 0:
        raise ValueError("Cooling case leaves the common comfort envelope")
    if abs(stock - store["initial_stored_kWh_th"]) > 1e-7:
        raise ValueError("Storage must end empty: no end-of-horizon free energy")
    if abs(indoor - zone["starting_indoor_C"]) > 1e-7:
        raise ValueError("Zone must end at starting temperature: no unpaid pre-cooling")
    return {"case": case, "summary": summary, "hourly": rows}


def build_pilot(cfg: dict | None = None) -> dict:
    if cfg is None:
        cfg = read_config()
    outcomes = {key: simulate(cfg, key) for key in CASES}
    baseline = outcomes["conventional"]["summary"]
    differences = {}
    for key in CASES[1:]:
        trial = outcomes[key]["summary"]
        differences[key] = {
            "change_total_grid_kWh_e": _round(trial["total_grid_kWh_e"] - baseline["total_grid_kWh_e"]),
            "change_whole_day_peak_kW_e": _round(trial["whole_day_peak_kW_e"] - baseline["whole_day_peak_kW_e"]),
            "change_evening_peak_kW_e": _round(trial["evening_peak_kW_e"] - baseline["evening_peak_kW_e"]),
            "change_evening_grid_kWh_e": _round(trial["evening_grid_kWh_e"] - baseline["evening_grid_kWh_e"]),
        }
    sensitivity = []
    for cap in cfg["sensitivity"]["storage_capacity_kWh_th"]:
        for derate in cfg["sensitivity"]["charge_COP_multiplier"]:
            altered = copy.deepcopy(cfg)
            altered["storage"]["thermal_energy_capacity_kWh"] = cap
            altered["storage"]["charging_COP_multiplier"] = derate
            result = simulate(altered, "chilled_water_storage")
            sensitivity.append({
                "storage_kWh_th": cap, "charging_cop_multiplier": derate,
                "total_grid_kWh_e": result["summary"]["total_grid_kWh_e"],
                "evening_peak_kW_e": result["summary"]["evening_peak_kW_e"],
                "whole_day_peak_kW_e": result["summary"]["whole_day_peak_kW_e"],
                "end_store_kWh_th": result["summary"]["end_store_kWh_th"],
                "comfort_violation_hours": result["summary"]["comfort_violation_hours"],
            })
    return {
        "classification": "WP6_SYNTHETIC_24H_1R1C_COOLING_COMPARISON_NOT_KERALA_GRID_RESULT",
        "source": cfg["source"], "time_basis": cfg["time_basis"],
        "spatial_scope": cfg["spatial_scope"],
        "inputs": cfg,
        "cases": outcomes, "differences_vs_conventional": differences,
        "sensitivity": sensitivity,
        "science_gates": {
            "real_Kerala_weather": False,
            "measured_building_cooling_load": False,
            "validated_operative_temperature_or_humidity": False,
            "statewide_MW_or_MWh_claim": False,
            "annual_electricity_saving_claim": False,
            "optimized_or_calibrated_2040_pathway": False,
            "financial_or_emissions_benefit_claim": False,
        },
        "interpretation": (
            "Synthetic engineering counterfactual: same zone and 24-26 C comfort bounds; "
            "pre-cooling intentionally changes delivered thermal cooling, not a claim "
            "of equal thermal kWh. Cooling capacity shortfall to early setpoint differs "
            "from a true comfort-limit violation. Evaluate evening peak separately "
            "from the full-day maximum and electricity energy."
        ),
    }
