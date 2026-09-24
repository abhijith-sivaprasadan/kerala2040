"""WP6: constrained synthetic managed EV charging and optional industrial job shifting.

Identical service, availability, shared charger/process limit and terminal
deadlines for unmanaged and managed. Greedy schedules are feasible examples,
NOT an optimal algorithm and NOT Kerala fleet/KMML operations.
"""
from __future__ import annotations

import copy
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
SPECS = {
    "ev": (
        "configs/wp6_ev_charging_illustrative.yaml",
        "WP6_SYNTHETIC_EV_CHARGING_NOT_KERALA_FLEET",
        "WP6_SYNTHETIC_EV_DEADLINE_DISPATCH_NOT_KERALA_FLEET",
    ),
    "industry": (
        "configs/wp6_industrial_illustrative.yaml",
        "WP6_SYNTHETIC_NONCRITICAL_INDUSTRIAL_JOBS_NOT_KMML_OPERATIONS",
        "WP6_SYNTHETIC_INDUSTRIAL_DEADLINE_DISPATCH_NOT_KMML_OPERATIONS",
    ),
}


def load_spec(kind: str, root: Path = ROOT) -> dict:
    if kind not in SPECS:
        raise ValueError("Unknown WP6 demonstration type")
    path, tag, _ = SPECS[kind]
    data = yaml.safe_load((root / path).read_text(encoding="utf-8"))
    validate_spec(data, kind)
    return data


def validate_spec(data: dict, kind: str) -> None:
    if kind not in SPECS or data.get("classification") != SPECS[kind][1]:
        raise ValueError("WP6 synthetic provenance not established")
    if data.get("version") != 1 or any(x is not False for x in data["release"].values()):
        raise ValueError("WP6 original research source or unvalidated release promoted")
    other = data["hourly_other_site_load_kw"] if kind == "ev" else data[
        "hourly_nonshiftable_site_load_kw"
    ]
    if len(other) != 24 or any(not 0 <= power < 200 for power in other):
        raise ValueError("24 hours of valid synthetic site load required")
    if data["evening_window"] != [17, 18, 19, 20, 21]:
        raise ValueError("WP6 illustrative five-hour window changed")
    cap_key = ("managed_shared_charger_limit_kw" if kind == "ev"
               else "managed_shared_flexible_limit_kw")
    if not 0 < data[cap_key] < 200:
        raise ValueError("Invalid shared flexible electrical capacity")
    if kind == "industry" and data[
        "nonshiftable_safety_and_critical_duty_always_on"
    ] is not True:
        raise ValueError("Safety-critical load cannot be treated as shiftable")
    jobs = data["vehicles"] if kind == "ev" else data["jobs"]
    if len(jobs) != 3 or len({item["id"] for item in jobs}) != len(jobs):
        raise ValueError("Pilot requires three distinct, explicitly authored jobs")
    for job in jobs:
        start = job["arrival_hour"]
        end = job["departure_hour"] if kind == "ev" else job["deadline_hour"]
        needed = (job["required_battery_kwh"] if kind == "ev"
                  else job["electricity_service_kwh"])
        power = job["charging_limit_kw"] if kind == "ev" else job[
            "flexible_power_limit_kw"
        ]
        eta = job["charging_efficiency"] if kind == "ev" else job[
            "conversion_efficiency"
        ]
        if (not 0 <= start < end <= 24 or needed <= 0 or power <= 0 or
                not 0 < eta <= 1):
            raise ValueError("Invalid service, charging power or arrival/deadline")
        if kind == "ev" and (
            job["initial_battery_kwh"] < 0 or
            job["initial_battery_kwh"] + needed > job["battery_capacity_kwh"]
        ):
            raise ValueError("EV destination battery capacity would be exceeded")
    if kind == "industry" and (
        data["industry_scope"]["critical_load_curtailment_allowed"] is not False
        or data["industry_scope"]["utility_or_residual_recovery_claim"] is not False
    ):
        raise ValueError("Unverified industrial process, safety or recovery promotion")


def _r(value: float) -> float:
    return round(value, 6)


def _params(job: dict, kind: str) -> tuple[int, int, float, float, float]:
    return (
        job["arrival_hour"],
        job["departure_hour"] if kind == "ev" else job["deadline_hour"],
        job["required_battery_kwh"] if kind == "ev" else job["electricity_service_kwh"],
        job["charging_limit_kw"] if kind == "ev" else job["flexible_power_limit_kw"],
        job["charging_efficiency"] if kind == "ev" else job["conversion_efficiency"],
    )


def dispatch(spec: dict, kind: str, policy: str) -> dict:
    """Schedule all jobs; greedy 'managed' is feasible but not claimed optimal."""
    validate_spec(spec, kind)
    if policy not in ("arrival_order", "managed"):
        raise ValueError("Unknown dispatch policy")
    background = (spec["hourly_other_site_load_kw"] if kind == "ev"
                  else spec["hourly_nonshiftable_site_load_kw"])
    cap = (spec["managed_shared_charger_limit_kw"] if kind == "ev"
           else spec["managed_shared_flexible_limit_kw"])
    jobs = spec["vehicles"] if kind == "ev" else spec["jobs"]
    window = set(spec["evening_window"])
    grid = [0.0] * 24
    by_job = {item["id"]: [0.0] * 24 for item in jobs}
    delivered = {}
    if policy == "arrival_order":
        order = sorted(jobs, key=lambda j: (_params(j, kind)[0],
                                           _params(j, kind)[1], j["id"]))
    else:
        # Give less off-peak-slack workloads first claim on limited windows.
        def offpeak_slack(item: dict) -> tuple[float, int, str]:
            a, b, energy, max_kw, eta = _params(item, kind)
            nonpeak_slots = sum(h not in window for h in range(a, b))
            return (nonpeak_slots * min(max_kw, cap) - energy / eta,
                    b, item["id"])

        order = sorted(jobs, key=offpeak_slack)

    for item in order:
        a, b, energy, power, eta = _params(item, kind)
        remaining = energy / eta
        slots = list(range(a, b))
        if policy == "managed":
            slots.sort(key=lambda h: (h in window, background[h] + grid[h], h))
        for h in slots:
            amount = min(remaining, power, max(0.0, cap - grid[h]))
            if amount < 0:
                raise AssertionError("Negative electricity allocation")
            if amount <= 1e-10:
                continue
            grid[h] += amount
            by_job[item["id"]][h] += amount
            remaining -= amount
            if remaining <= 1e-8:
                break
        if remaining > 1e-8:
            raise ValueError("Infeasible deadline: requested service cannot be charged")
        delivered[item["id"]] = energy

    rows = []
    for h in range(24):
        electric = sum(by_job[j["id"]][h] for j in jobs)
        if abs(grid[h] - electric) > 1e-8 or grid[h] > cap + 1e-8:
            raise AssertionError("Shared flexible-site power boundary violated")
        rows.append({
            "hour": h, "background_kw": _r(background[h]),
            "flexible_kw": _r(grid[h]),
            "site_total_kw": _r(background[h] + grid[h]),
            "in_evening_window": h in window,
            "job_grid_kw": {j["id"]: _r(by_job[j["id"]][h]) for j in jobs},
        })
    final_service = []
    for item in jobs:
        a, b, energy, power, eta = _params(item, kind)
        profile = by_job[item["id"]]
        if any(profile[h] > 1e-9 for h in list(range(a)) + list(range(b, 24))):
            raise AssertionError("Charging occurred outside authorised arrival/departure")
        if any(amount > power + 1e-9 for amount in profile):
            raise AssertionError("Device or process job power was exceeded")
        received = sum(profile) * eta
        if abs(received - energy) > 1e-7:
            raise AssertionError("Departing vehicle or due process has unmet service")
        final_service.append({
            "id": item["id"], "required_service_kwh": _r(energy),
            "delivered_service_kwh": _r(received),
            "grid_electricity_kwh": _r(sum(profile)),
            "arrival_hour": a, "deadline_hour": b,
            "power_limit_kw": power,
            "departure_battery_kwh": (
                _r(item["initial_battery_kwh"] + received)
                if kind == "ev" else None
            ),
            "met_deadline": True,
        })
    base_grid = sum(grid)
    base_service = sum(j["required_service_kwh"] for j in final_service)
    metric = {
        "electricity_kwh": _r(base_grid),
        "delivered_service_kwh": _r(base_service),
        "total_site_kwh": _r(sum(background) + base_grid),
        "whole_day_site_peak_kw": _r(max(background[h] + grid[h] for h in range(24))),
        "evening_site_peak_kw": _r(max(background[h] + grid[h] for h in window)),
        "evening_flexible_kwh": _r(sum(grid[h] for h in window)),
        "evening_site_kwh": _r(sum(background[h] + grid[h] for h in window)),
        "missed_deadlines": 0,
        "shared_flexible_limit_kw": cap,
    }
    return {"policy": policy, "hourly": rows, "jobs": final_service, "summary": metric}


def build_demonstration(kind: str, spec: dict | None = None) -> dict:
    if spec is None:
        spec = load_spec(kind)
    validate_spec(spec, kind)
    original = dispatch(spec, kind, "arrival_order")
    managed = dispatch(spec, kind, "managed")
    original_s, managed_s = original["summary"], managed["summary"]
    if (abs(original_s["electricity_kwh"] - managed_s["electricity_kwh"]) > 1e-6 or
            abs(original_s["delivered_service_kwh"] -
                managed_s["delivered_service_kwh"]) > 1e-6):
        raise AssertionError("Load shifting manufactured or removed delivered service")

    runs = []
    if kind == "ev":
        combinations = [
            (cap, eta)
            for cap in spec["sensitivity"]["shared_charger_limit_kw"]
            for eta in spec["sensitivity"]["charging_efficiency"]
        ]
    else:
        combinations = [
            (cap, scale)
            for cap in spec["sensitivity"]["shared_flexible_limit_kw"]
            for scale in spec["sensitivity"]["optional_job_service_multiplier"]
        ]
    for cap, variant in combinations:
        revised = copy.deepcopy(spec)
        if kind == "ev":
            revised["managed_shared_charger_limit_kw"] = cap
            for job in revised["vehicles"]:
                job["charging_efficiency"] = variant
        else:
            revised["managed_shared_flexible_limit_kw"] = cap
            for job in revised["jobs"]:
                job["electricity_service_kwh"] *= variant
        initial = dispatch(revised, kind, "arrival_order")
        altered = dispatch(revised, kind, "managed")
        if abs(initial["summary"]["electricity_kwh"] -
               altered["summary"]["electricity_kwh"]) > 1e-6:
            raise AssertionError("Sensitivity comparison broke service equivalence")
        runs.append({
            "shared_limit_kw": cap,
            "charging_efficiency" if kind == "ev" else "service_multiplier": variant,
            "baseline_evening_site_peak_kw": initial["summary"]["evening_site_peak_kw"],
            "managed_evening_site_peak_kw": altered["summary"]["evening_site_peak_kw"],
            "baseline_whole_day_site_peak_kw": initial["summary"]["whole_day_site_peak_kw"],
            "managed_whole_day_site_peak_kw": altered["summary"]["whole_day_site_peak_kw"],
            "service_kwh": altered["summary"]["delivered_service_kwh"],
            "site_total_kwh": altered["summary"]["total_site_kwh"],
            "missed_deadlines": altered["summary"]["missed_deadlines"],
        })
    return {
        "classification": SPECS[kind][2],
        "kind": kind,
        "scope": ("One explicitly illustrative three-vehicle depot, not Kerala fleet"
                  if kind == "ev" else
                  "Three hypothetical noncritical auxiliary jobs, NOT KMML operations"),
        "input": spec,
        "baseline": original,
        "managed": managed,
        "comparison": {
            "evening_site_peak_change_kw": _r(
                managed_s["evening_site_peak_kw"] -
                original_s["evening_site_peak_kw"]),
            "whole_day_site_peak_change_kw": _r(
                managed_s["whole_day_site_peak_kw"] -
                original_s["whole_day_site_peak_kw"]),
            "evening_flexible_energy_change_kwh": _r(
                managed_s["evening_flexible_kwh"] -
                original_s["evening_flexible_kwh"]),
            "total_electricity_change_kwh": _r(
                managed_s["electricity_kwh"] -
                original_s["electricity_kwh"]),
        },
        "sensitivity": runs,
        "science_gates": {
            "real_kerala_data_admitted": False,
            "actual_kmml_or_fleet_dispatch_admitted": False,
            "statewide_mw_mwh_or_avoided_co2_admitted": False,
            "tariff_or_project_finance_admitted": False,
            "optimal_control_proved": False,
            "year_2040_model_input_ready": False,
        },
    }
