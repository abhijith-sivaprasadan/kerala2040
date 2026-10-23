"""A source-anchored, constrained seven-day supply/chronology stress test.

Observed: daily SLDC energy, source completeness.
Reconstructed: every hourly MW demand in this experiment.
Hypothetical: hourly import availability and hydro ramp; NOT historical operation.

This model adds constraints that break the artificial permutation invariance of v0.1.
It cannot validate a specific shortage, event, hydro fleet, or FY2030-31 projection.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import linprog
from scipy.sparse import lil_matrix

from kerala2040.chronological_screen import prepare_inputs
from kerala2040.hydro_chronology_uncertainty import (
    SHAPES,
    choose_observed_peak_energy_week,
    perturb_day,
)

# Explicitly hypothetical stress designs, not measured import constraints.
TRANSFER_CAPS_MW = (4455.0, 3564.0)
SUPPLY_SHAPES = ("uniform_import_capacity", "illustrative_18_22_import_20pct_derate")
HYDRO_RAMP_CASES_MW_PER_H = (None, 400.0)
HYDRO_AGGREGATE_POWER_MW = 2284.42
ENERGY_TOLERANCE_MWH = 1e-3


def import_capacity_series(days: int, ceiling_mw: float, kind: str) -> np.ndarray:
    """A deliberately stylised, predeclared four-hour import restriction."""
    if not isinstance(days, int) or days < 1 or not np.isfinite(ceiling_mw) or ceiling_mw <= 0:
        raise ValueError("Need positive complete days and import ceiling")
    capacity = np.full(24 * days, ceiling_mw)
    if kind == "uniform_import_capacity":
        return capacity
    if kind == "illustrative_18_22_import_20pct_derate":
        for day in range(days):
            capacity[day * 24 + 18:day * 24 + 22] *= 0.8
        return capacity
    raise ValueError(f"Unknown hypothetical availability profile: {kind}")


def solve_seven_day_hydro(
    load_mw: np.ndarray,
    nonhydro_mw: np.ndarray,
    daily_hydro_mwh: np.ndarray,
    import_cap_by_hour_mw: np.ndarray,
    *,
    hydro_power_mw: float,
    ramp_mw_per_h: float | None,
) -> dict:
    """Minimise unserved MWh with exact daily hydro MWh and optionally coupled ramps.

    Hourly identity: hydro + import + unserved - spill = demand - nonhydro.
    No interday hydro MWh transfer, reservoir state, AC network, physical fleet ramp,
    or empirically estimated hourly imports. Ramp is a *hypothesis*, not measured.
    """
    load = np.asarray(load_mw, dtype=float)
    other = np.asarray(nonhydro_mw, dtype=float)
    daily_energy = np.asarray(daily_hydro_mwh, dtype=float)
    hourly_import_cap = np.asarray(import_cap_by_hour_mw, dtype=float)
    n = len(load)
    days = n // 24
    if n < 24 or n % 24 or daily_energy.shape != (days,):
        raise ValueError("Require at least one complete day and matching daily hydro energy")
    if any(x.shape != (n,) for x in (load, other, hourly_import_cap)):
        raise ValueError("Hourly input arrays must have exactly the same length")
    if any(not np.isfinite(x).all() for x in (load, other, daily_energy, hourly_import_cap)):
        raise ValueError("Nonfinite numerical input")
    if min(float(load.min()), float(other.min()), float(hourly_import_cap.min()),
           float(daily_energy.min()), float(hydro_power_mw)) < 0 or hydro_power_mw <= 0:
        raise ValueError("Energy, capacity and output must be nonnegative")
    if (daily_energy > 24 * hydro_power_mw + ENERGY_TOLERANCE_MWH).any():
        raise ValueError("Hydro daily target exceeds aggregate power availability")
    if ramp_mw_per_h is not None and (not np.isfinite(ramp_mw_per_h) or ramp_mw_per_h <= 0):
        raise ValueError("Hypothetical hourly hydro ramp must be positive and finite")

    # n hydro, n import, n unserved, n explicit spill decision variables.
    eq = lil_matrix((n + days, 4 * n), dtype=float)
    for t in range(n):
        eq[t, t] = 1.0
        eq[t, n + t] = 1.0
        eq[t, 2*n + t] = 1.0
        eq[t, 3*n + t] = -1.0
    for day in range(days):
        eq[n + day, day*24:(day+1)*24] = 1.0
    rhs = np.r_[load - other, daily_energy]

    inequality = None
    upper_rhs = None
    if ramp_mw_per_h is not None:
        # Importantly: ramp constraints span *midnight*, not just each calendar day.
        inequality = lil_matrix((2*(n-1), 4*n), dtype=float)
        for t in range(1, n):
            inequality[2*(t-1), t] = 1.0
            inequality[2*(t-1), t-1] = -1.0
            inequality[2*(t-1)+1, t] = -1.0
            inequality[2*(t-1)+1, t-1] = 1.0
        inequality = inequality.tocsr()
        upper_rhs = np.full(2*(n-1), ramp_mw_per_h)

    objective = np.zeros(4*n)
    objective[2*n:3*n] = 1.0
    bounds = (
        [(0.0, hydro_power_mw)]*n
        + [(0.0, float(cap)) for cap in hourly_import_cap]
        + [(0.0, None)]*(2*n)
    )
    result = linprog(objective, A_eq=eq.tocsr(), b_eq=rhs, A_ub=inequality,
                     b_ub=upper_rhs, bounds=bounds, method="highs")
    if not result.success:
        raise RuntimeError(f"Constrained seven-day hydro programme unsuccessful: {result.message}")

    hydro, imported, unserved, spill = np.split(result.x, 4)
    deviation = float(np.max(np.abs(eq.tocsr() @ result.x - rhs)))
    daily_residual = float(np.max(np.abs(hydro.reshape(days, 24).sum(axis=1) - daily_energy)))
    actual_ramp = float(np.max(np.abs(np.diff(hydro)))) if n > 1 else 0.0
    if deviation > ENERGY_TOLERANCE_MWH or daily_residual > ENERGY_TOLERANCE_MWH:
        raise RuntimeError("Unserved result rejected: energy balance or hydro equality failed")
    if ramp_mw_per_h is not None and actual_ramp > ramp_mw_per_h + 1e-4:
        raise RuntimeError("Hydro ramp constraint violated")
    return {
        "modelled_unserved_mwh": float(unserved.sum()),
        "hydro_generation_mwh": float(hydro.sum()),
        "import_mwh": float(imported.sum()),
        "spill_mwh": float(spill.sum()),
        "peak_hydro_mw": float(hydro.max()),
        "observed_solver_max_hydro_ramp_mw_per_h": actual_ramp,
        "max_hourly_balance_residual_mw": deviation,
        "max_daily_hydro_energy_residual_mwh": daily_residual,
        "solver": "SciPy/HiGHS sparse linear programme",
    }


def run(root: Path) -> dict:
    root = Path(root)
    sources = (
        "data/external/sldc_fy2024_25/daily_balance.csv",
        "data/external/sldc_fy2024_25/qa_report.json",
        "public/hourly-load-proxy.json",
    )
    source_sha = {p: hashlib.sha256((root / p).read_bytes()).hexdigest() for p in sources}
    daily = pd.read_csv(root / sources[0])
    qa = json.loads((root / sources[1]).read_text(encoding="utf-8"))
    proxy = json.loads((root / sources[2]).read_text(encoding="utf-8"))
    hourly, metadata = prepare_inputs(proxy, daily, expected_missing_dates=qa["missing_dates"])
    days = choose_observed_peak_energy_week(daily)
    selected = hourly.loc[hourly["date"].isin(days)].copy()
    if len(selected) != 168 or selected["date"].tolist() != [d for d in days for _ in range(24)]:
        raise RuntimeError("Observed selected week is not exactly seven contiguous complete days")
    hydro_targets = selected["hydro_fixed_mw"].to_numpy().reshape(7, 24).sum(axis=1)
    other = selected["nonhydro_fixed_mw"].to_numpy().astype(float)
    daily_average_hydro = np.repeat(hydro_targets / 24., 24)
    # 400 MW/h is large enough to make this window's day-flat replay feasible
    # even across midnight; therefore constraining hydro cannot outperform
    # the unconstrained run or make the fixed baseline infeasible.
    max_fixed_ramp = float(np.max(np.abs(np.diff(daily_average_hydro))))
    if max_fixed_ramp > 400.0 + 1e-6:
        raise RuntimeError("Fixed-hydro replay now violates declared 400 MW/h ramp bracket")
    variants = {}
    for shape in SHAPES:
        shaped = np.concatenate([
            perturb_day(g["load_mw"].to_numpy(dtype=float), shape)
            for _, g in selected.groupby("date", sort=True)
        ])
        for day in range(7):
            prior = float(selected["load_mw"].iloc[day*24:(day+1)*24].sum())
            if abs(shaped[day*24:(day+1)*24].sum()-prior) > 1e-4:
                raise RuntimeError("Scenario changed source-tied daily consumption")
        variants[shape] = shaped

    cases = []
    for transfer in TRANSFER_CAPS_MW:
        for supply_shape in SUPPLY_SHAPES:
            hourly_cap = import_capacity_series(7, transfer, supply_shape)
            for demand_shape, shaped in variants.items():
                # Exact objective for a fixed-hydro replay, independently of the LP.
                fixed_unserved = float(
                    np.maximum(0., shaped-other-daily_average_hydro-hourly_cap).sum()
                )
                previous = None
                for ramp in HYDRO_RAMP_CASES_MW_PER_H:
                    solved = solve_seven_day_hydro(
                        shaped, other, hydro_targets, hourly_cap,
                        hydro_power_mw=HYDRO_AGGREGATE_POWER_MW, ramp_mw_per_h=ramp,
                    )
                    # Here the fixed baseline satisfies either possible ramp restriction.
                    if solved["modelled_unserved_mwh"] > fixed_unserved + 1e-3:
                        raise RuntimeError("Flexible hydro is worse than a feasible fixed-hydro replay")
                    if previous is not None and solved["modelled_unserved_mwh"] + 1e-3 < previous:
                        raise RuntimeError("Imposing a ramp constraint paradoxically improved shortage")
                    previous = solved["modelled_unserved_mwh"]
                    cases.append({
                        "import_ceiling_mw": transfer,
                        "hypothetical_import_hourly_schedule": supply_shape,
                        "demand_shape": demand_shape,
                        "hydro_ramp_cap_mw_per_h": ramp,
                        "fixed_hydro_unserved_mwh": fixed_unserved,
                        "optimised_hydro_unserved_mwh": solved["modelled_unserved_mwh"],
                        "avoided_unserved_mwh": fixed_unserved-solved["modelled_unserved_mwh"],
                        "daily_energy_preserved": True,
                        "solver_checks": {
                            "max_hourly_balance_residual_mw": solved["max_hourly_balance_residual_mw"],
                            "max_daily_hydro_energy_residual_mwh": solved["max_daily_hydro_energy_residual_mwh"],
                            "actual_hydro_ramp_mw_per_h": solved["observed_solver_max_hydro_ramp_mw_per_h"],
                        },
                    })
    # Controlled falsification: permutation invariance MUST hold with time-invariant
    # imports and no ramp, and MUST NOT be used to imply realistic hourly alignment.
    for transfer in TRANSFER_CAPS_MW:
        const = {(x["demand_shape"], x["hydro_ramp_cap_mw_per_h"]): x
                 for x in cases if x["import_ceiling_mw"] == transfer
                 and x["hypothetical_import_hourly_schedule"] == "uniform_import_capacity"}
        for shift in ("shift_earlier_2h", "shift_later_2h"):
            for metric in ("fixed_hydro_unserved_mwh", "optimised_hydro_unserved_mwh"):
                if abs(const[(shift, None)][metric]-const[("baseline", None)][metric]) > 1e-3:
                    raise RuntimeError("Unexpected clock-time asymmetry in the control case")

    return {
        "experiment": "historic_proxy_time_varying_supply_ramp_stress_v0_2",
        "source_sha256": source_sha,
        "selected_observed_week": days,
        "daily_source_consumption_mu": float(daily.set_index("date").loc[days, "consumption_mu"].sum()),
        "window_hours": 168,
        "observed_source_days": metadata["observed_days"],
        "hourly_demand_evidence": "RECONSTRUCTED_NOT_MEASURED",
        "supply_availability": "ILLUSTRATIVE_HOURLY_DERATES_NOT_OBSERVED_IMPORT_CONSTRAINTS",
        "ramp_source": "HYPOTHETICAL_400_MW_PER_H_NOT_A_VALIDATED_FLEET_RAMP",
        "max_fixed_hourly_hydro_jump_mw": max_fixed_ramp,
        "study_scope": "single-node historical screening: exact source-day hydro energy; static daily nonhydro; 2026 aggregate hydro capacity; no station, reservoir, AC, future projection or event attribution",
        "separate_main_study": "NOT a replay or validation of FY2030-31 hydro-flex 375.03-to-11.75 GWh result",
        "cases": cases,
    }
