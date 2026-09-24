"""WP6 electrical-storage demonstration: BESS vs tiny hydraulic PSP analogue.

Fixed 24h synthetic electrical-service requirement, separate charge/discharge,
standing and auxiliary loss accounting, 0 -> 0 terminal state. Not Kerala data.
"""
from __future__ import annotations

import copy
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / "configs/wp6_bess_psp_illustrative.yaml"
CLASSIFICATION = "WP6_SYNTHETIC_ELECTRICAL_STORAGE_NOT_KERALA_SITES"
OUTPUT_CLASS = "WP6_SYNTHETIC_BESS_PSP_FIXED_SERVICE_NOT_KERALA_FEASIBILITY"


def load_spec(path: Path = CONFIG) -> dict:
    cfg = yaml.safe_load(path.read_text(encoding="utf-8"))
    validate_spec(cfg)
    return cfg


def validate_spec(cfg: dict) -> None:
    if cfg.get("version") != 1 or cfg.get("classification") != CLASSIFICATION:
        raise ValueError("BESS/PSP source was promoted from a synthetic example")
    load = cfg["hourly_background_site_kw"]
    if len(load) != 24 or any(not 0 < x < 1000 for x in load):
        raise ValueError("Need 24 non-negative valid synthetic site hours")
    if cfg["charge_hours"] != list(range(7)) or cfg["discharge_hours"] != list(range(17, 22)):
        raise ValueError("Synthetic service horizon changed")
    if not 0 < cfg["discharge_service_kw"] < min(load[h] for h in cfg["discharge_hours"]):
        raise ValueError("Storage must not export or invent demand")
    if set(cfg["storage"]) != {"bess", "psp"}:
        raise ValueError("Both technologies required")
    for kind, store in cfg["storage"].items():
        for key in ("capacity_kwh_stored", "charge_max_kw", "discharge_max_kw"):
            if store[key] <= 0:
                raise ValueError("Storage size and converter limits must be positive")
        for key in ("charge_efficiency", "discharge_efficiency"):
            if not 0 < store[key] <= 1:
                raise ValueError("Charge/discharge efficiencies outside physics")
        if not 0 <= store["standing_loss_per_hour"] < 1:
            raise ValueError("Invalid standing storage loss")
        if not 0 <= store["auxiliary_kwh_per_kwh_delivered"] < 1:
            raise ValueError("Invalid storage auxiliary")
        if len(store["sensitivity_capacity_kwh"]) != 3 or len(store["sensitivity_charge_efficiency"]) != 3:
            raise ValueError("Nine sensitivity cells per technology are required")
        if kind == "psp" and any(store[k] <= 0 for k in (
            "hypothetical_net_head_m", "reference_water_density_kg_per_m3",
            "gravity_m_per_s2"
        )):
            raise ValueError("Hydraulic analogue requires positive head, density, gravity")
    if any(value is not False for value in cfg["release"].values()):
        raise ValueError("Unsupported Kerala capacity, project or financial claim")


def _r(value: float) -> float:
    return round(value, 6)


def hydraulic_kwh_per_m3(store: dict) -> float:
    """Potential energy per cubic metre, no site-specific topology implied."""
    return (
        store["reference_water_density_kg_per_m3"] *
        store["gravity_m_per_s2"] *
        store["hypothetical_net_head_m"] / 3_600_000.0
    )


def simulate(cfg: dict, kind: str) -> dict:
    validate_spec(cfg)
    if kind not in ("bess", "psp"):
        raise ValueError("Unsupported storage technology")
    p = cfg["storage"][kind]
    load = cfg["hourly_background_site_kw"]
    loss = p["standing_loss_per_hour"]
    eta_c, eta_d = p["charge_efficiency"], p["discharge_efficiency"]
    service = cfg["discharge_service_kw"]
    discharge = {
        hour: min(service, p["discharge_max_kw"], load[hour])
        for hour in cfg["discharge_hours"]
    }

    # Back-solve the stock needed at end hour 6 to serve exactly the subsequent
    # discharge schedule after all intervening standing losses.
    required = 0.0
    for hour in range(23, 6, -1):
        required = (required + discharge.get(hour, 0.0) / eta_d) / (1.0 - loss)
    max_stored = required
    if max_stored > p["capacity_kwh_stored"] + 1e-8:
        raise ValueError("Infeasible storage energy capacity for full service")

    # Back-solve latest-first charging through hour 6; no free initial energy.
    charging = {}
    need = required
    for hour in reversed(cfg["charge_hours"]):
        electric = min(p["charge_max_kw"], need / eta_c)
        charging[hour] = electric
        need = max(0.0, (need - electric * eta_c) / (1.0 - loss))
    if need > 1e-7:
        raise ValueError("Infeasible pre-discharge charging power or time")
    stock = 0.0
    rows = []
    for hour, bg in enumerate(load):
        old = stock
        standing = stock * loss
        stock -= standing
        charge = charging.get(hour, 0.0)
        supplied = discharge.get(hour, 0.0)
        withdrawn = supplied / eta_d
        stock += charge * eta_c - withdrawn
        if stock < -1e-7 or stock > p["capacity_kwh_stored"] + 1e-7:
            raise AssertionError("Store violates SOC energy bounds")
        if charge > 0 and supplied > 0:
            raise AssertionError("Charge and discharge overlap")
        if (hour not in cfg["charge_hours"] and charge > 0 or
                hour not in cfg["discharge_hours"] and supplied > 0):
            raise AssertionError("Out-of-window dispatch")
        if abs(stock - (old - standing + charge * eta_c - withdrawn)) > 1e-8:
            raise AssertionError("Electrical storage energy balance broken")
        auxiliary = supplied * p["auxiliary_kwh_per_kwh_delivered"]
        grid = bg + charge + auxiliary - supplied
        if grid < 0:
            raise AssertionError("Unexpected electricity export")
        row = {
            "hour": hour, "background_kw": _r(bg),
            "grid_charge_kwh": _r(charge),
            "grid_discharge_kwh": _r(supplied),
            "auxiliary_grid_kwh": _r(auxiliary),
            "standing_loss_kwh_stored": _r(standing),
            "storage_conversion_loss_kwh": _r(charge * (1 - eta_c)
                                              + withdrawn - supplied),
            "stock_kwh_stored": _r(stock),
            "grid_site_kw": _r(grid),
            "evening_window": hour in cfg["discharge_hours"],
        }
        if kind == "psp":
            row["upper_water_m3_analogue"] = _r(max(0.0, stock) / hydraulic_kwh_per_m3(p))
        rows.append(row)
    if abs(stock) > 1e-7:
        raise ValueError("Terminal storage not empty: free energy leak")
    charged = sum(charging.values())
    supplied_total = sum(discharge.values())
    standing_total = sum(r["standing_loss_kwh_stored"] for r in rows)
    aux_total = supplied_total * p["auxiliary_kwh_per_kwh_delivered"]
    total_site = sum(r["grid_site_kw"] for r in rows)
    base_total = sum(load)
    if abs(total_site - (base_total + charged + aux_total - supplied_total)) > 2e-5:
        raise AssertionError("Net site energy versus storage input does not close")
    net_added = charged + aux_total - supplied_total
    if net_added < -1e-8:
        raise AssertionError("Storage falsely produces daily energy")
    out = {
        "kind": kind,
        "summary": {
            "charge_grid_kwh": _r(charged),
            "discharge_to_site_kwh": _r(supplied_total),
            "auxiliary_grid_kwh": _r(aux_total),
            "standing_loss_kwh_stored": _r(standing_total),
            "daily_site_grid_kwh": _r(total_site),
            "daily_grid_energy_change_kwh": _r(net_added),
            "whole_day_site_peak_kw": _r(max(r["grid_site_kw"] for r in rows)),
            "evening_site_peak_kw": _r(max(rows[h]["grid_site_kw"] for h in cfg["discharge_hours"])),
            "evening_grid_kwh": _r(sum(rows[h]["grid_site_kw"] for h in cfg["discharge_hours"])),
            "round_trip_net_energy_ratio": _r(supplied_total / (charged + aux_total)),
            "max_stored_kwh": _r(max_stored),
            "terminal_stored_kwh": _r(stock),
            "max_upper_water_m3_analogue": (
                _r(max_stored / hydraulic_kwh_per_m3(p)) if kind == "psp" else None
            ),
        },
        "hourly": rows,
    }
    return out


def build_screen(cfg: dict | None = None) -> dict:
    if cfg is None:
        cfg = load_spec()
    validate_spec(cfg)
    bg = cfg["hourly_background_site_kw"]
    window = cfg["discharge_hours"]
    baseline = {
        "daily_site_grid_kwh": _r(sum(bg)),
        "whole_day_site_peak_kw": _r(max(bg)),
        "evening_site_peak_kw": _r(max(bg[h] for h in window)),
        "evening_grid_kwh": _r(sum(bg[h] for h in window)),
    }
    cases = {kind: simulate(cfg, kind) for kind in ("bess", "psp")}
    sensitivities = {}
    for kind in cases:
        entries = []
        for cap in cfg["storage"][kind]["sensitivity_capacity_kwh"]:
            for efficiency in cfg["storage"][kind]["sensitivity_charge_efficiency"]:
                candidate = copy.deepcopy(cfg)
                candidate["storage"][kind]["capacity_kwh_stored"] = cap
                candidate["storage"][kind]["charge_efficiency"] = efficiency
                try:
                    run = simulate(candidate, kind)
                except ValueError as error:
                    if not str(error).startswith("Infeasible"):
                        raise
                    entries.append({
                        "capacity_kwh_stored": cap, "charge_efficiency": efficiency,
                        "feasible": False, "reason": str(error),
                        "daily_site_grid_kwh": None,
                        "evening_site_peak_kw": None,
                        "whole_day_site_peak_kw": None,
                    })
                else:
                    entries.append({
                        "capacity_kwh_stored": cap, "charge_efficiency": efficiency,
                        "feasible": True, "reason": None,
                        "daily_site_grid_kwh": run["summary"]["daily_site_grid_kwh"],
                        "evening_site_peak_kw": run["summary"]["evening_site_peak_kw"],
                        "whole_day_site_peak_kw": run["summary"]["whole_day_site_peak_kw"],
                    })
        sensitivities[kind] = entries
    return {
        "classification": OUTPUT_CLASS,
        "input": cfg, "baseline": baseline, "cases": cases,
        "sensitivities": sensitivities,
        "comparison": {
            k: {
                "evening_site_peak_change_kw": _r(v["summary"]["evening_site_peak_kw"]
                                                   - baseline["evening_site_peak_kw"]),
                "whole_day_site_peak_change_kw": _r(v["summary"]["whole_day_site_peak_kw"]
                                                     - baseline["whole_day_site_peak_kw"]),
                "daily_site_energy_change_kwh": v["summary"]["daily_grid_energy_change_kwh"],
            }
            for k, v in cases.items()
        },
        "release": {
            "measured_kerala_data": False,
            "site_or_project_feasibility": False,
            "grid_services_or_reliability": False,
            "hydro_cascade_water_rights_environmental_clearance": False,
            "real_financial_or_carbon_benefit": False,
            "calibrated_2040_capacity": False,
        },
    }
