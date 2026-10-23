"""A bounded, deliberately non-calibrated hydro/demand chronology sensitivity.

Uses published *daily* SLDC totals and an explicitly reconstructed hourly load.
Nothing here establishes actual hourly operation, reservoir feasibility or FY2030-31 outcomes.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import linprog

from kerala2040.chronological_screen import prepare_inputs

SHAPES = ("baseline", "shift_earlier_2h", "shift_later_2h",
          "flatten_intraday_10pct", "amplify_intraday_10pct")
TRANSFER_CASES_MW = (4455.0, 2673.0)


def perturb_day(load: np.ndarray, kind: str) -> np.ndarray:
    load = np.asarray(load, dtype=float)
    if load.shape != (24,) or not np.isfinite(load).all() or (load <= 0).any():
        raise ValueError("Expected 24 positive, finite reconstructed hourly MW values")
    mean = load.mean()
    if kind == "baseline":
        altered = load.copy()
    elif kind == "shift_earlier_2h":
        altered = np.roll(load, -2)
    elif kind == "shift_later_2h":
        altered = np.roll(load, 2)
    elif kind == "flatten_intraday_10pct":
        altered = mean + 0.9 * (load - mean)
    elif kind == "amplify_intraday_10pct":
        altered = mean + 1.1 * (load - mean)
    else:
        raise ValueError(f"Unsupported preregistered profile perturbation {kind!r}")
    if (altered <= 0).any() or abs(altered.sum() - load.sum()) > 1e-6:
        raise ValueError("Altered shape violates positive load or daily-energy conservation")
    return altered


def solve_one_day(
    load_mw: np.ndarray, *,
    nonhydro_mw: float, daily_hydro_mwh: float,
    hydro_power_mw: float, import_ceiling_mw: float,
    flexible: bool,
) -> dict:
    """Solve exact source-day hydro equality with dispatchable imports and explicit spill.

    At each of 24 hours: hydro + import + unserved - spill = load - fixed_nonhydro.
    No battery, network, unit commitment, reservoir head, ramp or interday water state.
    Optimistic flexible case relaxes only fixed hydro timing, not the daily MWh.
    """
    load = np.asarray(load_mw, dtype=float)
    if load.shape != (24,) or not np.isfinite(load).all() or (load < 0).any():
        raise ValueError("Invalid daily load")
    if not all(np.isfinite(x) for x in (nonhydro_mw, daily_hydro_mwh, hydro_power_mw, import_ceiling_mw)):
        raise ValueError("Non-finite model parameter")
    if min(nonhydro_mw, daily_hydro_mwh, hydro_power_mw, import_ceiling_mw) < 0:
        raise ValueError("Negative system parameter")
    if daily_hydro_mwh > 24 * hydro_power_mw + 1e-6:
        raise ValueError("Daily hydro MWh infeasible at stated aggregate capacity")
    fixed_mw = daily_hydro_mwh / 24.
    if not flexible and fixed_mw > hydro_power_mw + 1e-6:
        raise ValueError("Fixed average exceeds hydro power bound")

    # Variables: 24 hydro, 24 imports, 24 unserved, 24 spill.
    eq = np.zeros((25, 96))
    for hour in range(24):
        eq[hour, hour] = 1
        eq[hour, 24 + hour] = 1
        eq[hour, 48 + hour] = 1
        eq[hour, 72 + hour] = -1
    eq[24, :24] = 1
    target = np.concatenate([load - nonhydro_mw, [daily_hydro_mwh]])
    bounds = (
        [(0., hydro_power_mw) if flexible else (fixed_mw, fixed_mw)] * 24
        + [(0., import_ceiling_mw)] * 24
        + [(0., None)] * 48
    )
    objective = np.zeros(96)
    objective[48:72] = 1.0  # Pure minimization of modelled unserved MWh.
    result = linprog(objective, A_eq=eq, b_eq=target, bounds=bounds, method="highs")
    if not result.success:
        raise RuntimeError(f"Analytic day-screen LP did not solve: {result.message}")
    hydro, imports, unserved, spill = np.split(result.x, 4)
    residual = float(np.max(np.abs(eq @ result.x - target)))
    if residual > 1e-4 or abs(hydro.sum() - daily_hydro_mwh) > 1e-4:
        raise RuntimeError("Hourly or hydro-energy invariant failed")
    return {
        "modelled_unserved_mwh": float(unserved.sum()),
        "imports_mwh": float(imports.sum()),
        "spill_mwh": float(spill.sum()),
        "hydro_mwh": float(hydro.sum()),
        "hydro_peak_mw": float(hydro.max()),
        "max_equation_residual": residual,
        "solver": "SciPy/HiGHS linear program",
    }


def choose_observed_peak_energy_week(daily: pd.DataFrame) -> list[str]:
    """Highest seven-consecutive-day observed consumption; selection is NOT by model results."""
    if len(daily) != 365 or "date" not in daily or "status" not in daily:
        raise ValueError("Expected full fiscal-year daily source table")
    source = daily.sort_values("date")
    d = pd.to_datetime(source["date"])
    if not (d.diff().iloc[1:] == pd.Timedelta(days=1)).all():
        raise ValueError("Official days are not contiguous")
    valid = source["status"].to_numpy() == "observed"
    consumption = pd.to_numeric(source["consumption_mu"], errors="coerce").to_numpy()
    choices = []
    for i in range(365 - 7 + 1):
        if valid[i:i+7].all() and np.isfinite(consumption[i:i+7]).all():
            choices.append((float(consumption[i:i+7].sum()), str(source.iloc[i]["date"]),
                            source.iloc[i:i+7]["date"].tolist()))
    if not choices:
        raise ValueError("No seven-day fully observed window")
    # Earliest date wins an exact equal-energy tie. No selection using shortage outcomes.
    return min(choices, key=lambda x: (-x[0], x[1]))[2]


def run(root: Path) -> dict:
    root = Path(root)
    source_paths = (
        "data/external/sldc_fy2024_25/daily_balance.csv",
        "data/external/sldc_fy2024_25/qa_report.json",
        "public/hourly-load-proxy.json",
    )
    source_sha = {p: hashlib.sha256((root / p).read_bytes()).hexdigest() for p in source_paths}
    daily = pd.read_csv(root / source_paths[0])
    qa = json.loads((root / source_paths[1]).read_text(encoding="utf-8"))
    proxy = json.loads((root / source_paths[2]).read_text(encoding="utf-8"))
    hourly, metadata = prepare_inputs(proxy, daily, expected_missing_dates=qa["missing_dates"])
    days = choose_observed_peak_energy_week(daily)
    site = hourly[hourly["date"].isin(days)].copy()
    if len(site) != 168 or site["date"].tolist() != [day for day in days for _ in range(24)]:
        raise RuntimeError("Selected week hourly reconstruction is incomplete")
    # Configured aggregate hydro capacity is a source-backed March 2026 planning reference.
    # This is NOT an FY2024-25 generation-state observation.
    hydro_power_mw = 2284.42
    trials = []
    for import_cap in TRANSFER_CASES_MW:
        for profile in SHAPES:
            flat_shortage = 0.
            flexible_shortage = 0.
            max_balance = 0.
            for day in days:
                rows = site.loc[site["date"] == day]
                shaped = perturb_day(rows["load_mw"].to_numpy(), profile)
                hydro_target = float(rows["hydro_fixed_mw"].sum())
                fixed_nonhydro = float(rows["nonhydro_fixed_mw"].iloc[0])
                if not np.allclose(rows["nonhydro_fixed_mw"], fixed_nonhydro, atol=1e-8):
                    raise ValueError("Nonhydro daily-constant replay assumption changed")
                flat = solve_one_day(shaped, nonhydro_mw=fixed_nonhydro,
                                     daily_hydro_mwh=hydro_target, hydro_power_mw=hydro_power_mw,
                                     import_ceiling_mw=import_cap, flexible=False)
                flex = solve_one_day(shaped, nonhydro_mw=fixed_nonhydro,
                                     daily_hydro_mwh=hydro_target, hydro_power_mw=hydro_power_mw,
                                     import_ceiling_mw=import_cap, flexible=True)
                if flex["modelled_unserved_mwh"] > flat["modelled_unserved_mwh"] + 1e-3:
                    raise RuntimeError("Mathematically relaxed hydro flexibility worsened minimum shortage")
                flat_shortage += flat["modelled_unserved_mwh"]
                flexible_shortage += flex["modelled_unserved_mwh"]
                max_balance = max(max_balance, flat["max_equation_residual"],
                                  flex["max_equation_residual"])
            trials.append({
                "import_ceiling_mw": import_cap, "shape": profile,
                "fixed_hydro_unserved_mwh": flat_shortage,
                "flexible_hydro_unserved_mwh": flexible_shortage,
                "avoided_unserved_mwh": flat_shortage - flexible_shortage,
                "max_model_equation_residual_mw": max_balance,
                "reconstructed_daily_energy_preserved": True,
            })
    return {
        "experiment": "historic_proxy_seven_day_demand_chronology_sensitivity_v0_1",
        "selected_observed_high_consumption_dates": days,
        "selection_rule": "argmax total observed seven-day SLDC consumption, no missing source days, earliest tie",
        "source_sha256": source_sha,
        "shape_variants": SHAPES,
        "import_limits_mw": TRANSFER_CASES_MW,
        "hydro_aggregate_power_reference_mw": hydro_power_mw,
        "daily_hydro_energy": "observed SLDC daily totals, held fixed independently in each day",
        "hourly_demand_evidence": "RECONSTRUCTED_NOT_MEASURED",
        "model_limit": "single-node SciPy/HiGHS model, optimistic intra-day hydro power bound; no AC, hydrology, ramping, storage, forecast or reservoir validation",
        "applicability": "historical FY2024-25 reconstructed-load arithmetic only; NOT a reproduction or independent validation of FY2030-31 375.03-to-11.75 GWh claim",
        "research_status": "CONTROLLED_SENSITIVITY_NOT_CALIBRATED_UNCERTAINTY",
        "source_observed_days": metadata["observed_days"],
        "results": trials,
    }
