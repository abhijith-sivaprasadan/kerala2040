"""Windowed interday hydro-flexibility bracket for Full-PyPSA v1.2."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import xarray as xr
import yaml

from kerala2040.full_pypsa_cost_finance import load_cost_finance_suite
from kerala2040.full_pypsa_future_adequacy import (
    _load_base,
    load_future_adequacy_suite,
    morph_load_to_energy_and_peak,
)
from kerala2040.full_pypsa_hydro_flex_v1_1 import _build_network, _daily_targets
from kerala2040.full_pypsa_import_economics import load_import_economics_suite
from kerala2040.full_pypsa_proxy_expansion import (
    _align_profiles,
    _annualized_costs,
    _candidate_caps,
    _solar_allocation_range,
    load_proxy_expansion_suite,
)

SUITE_CLASS = (
    "full_pypsa_hydro_interday_v1_2_"
    "windowed_energy_bracket_not_reservoir_model"
)


def load_hydro_interday_v12_suite(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if data.get("classification") != SUITE_CLASS:
        raise ValueError("v1.2 interday-hydro classification mismatch")

    windows = data["interday_windows"]
    if [int(item["window_days"]) for item in windows] != [1, 3, 7, 30]:
        raise ValueError("v1.2 interday windows changed")

    availability = data["hydro_availability_cases"]
    if [item["id"] for item in availability] != [
        "full_available",
        "n_minus_1_idukki_130mw",
    ]:
        raise ValueError("v1.2 hydro availability cases changed")

    release = data["release"]
    if release["interday_hydro_flexibility_bracket_ready"] is not True:
        raise ValueError("v1.2 interday hydro bracket is not released")
    if release["source_anchored_idukki_n_minus_1_ready"] is not True:
        raise ValueError("v1.2 Idukki N-1 evidence is not released")
    for key in (
        "reservoir_model_ready",
        "water_balance_model_ready",
        "cascade_model_ready",
        "pumped_storage_model_ready",
        "hydro_economic_dispatch_validated",
        "total_system_cost_optimization",
        "validated_capacity_plan",
        "scenario_recommendation",
    ):
        if release[key] is not False:
            raise ValueError(f"v1.2 incorrectly enables {key}")
    return data


def validate_station_evidence(root: Path, suite: dict[str, Any]) -> dict[str, Any]:
    path = root / suite["inherits"]["station_capacity_evidence"]
    evidence = json.loads(path.read_text(encoding="utf-8"))
    if float(evidence["aggregate_capacity"]["march_2026_hydro_mw"]) != 2284.42:
        raise ValueError("v1.2 March-2026 hydro boundary changed")
    largest = float(
        evidence["station_unit_anchor"]["largest_verified_single_unit_mw"]
    )
    if largest != 130.0:
        raise ValueError("v1.2 largest verified hydro unit changed")
    n1 = float(
        evidence["availability_cases"]["n_minus_1_idukki_130mw"][
            "available_hydro_mw"
        ]
    )
    if abs(n1 - (2284.42 - 130.0)) > 1e-9:
        raise ValueError("v1.2 Idukki N-1 arithmetic mismatch")
    return evidence


def _window_constraint_data(
    snapshots: pd.DatetimeIndex,
    daily_hydro_mwh: pd.Series,
    window_days: int,
) -> tuple[xr.DataArray, np.ndarray]:
    if window_days < 1:
        raise ValueError("window_days must be >= 1")
    days = pd.DatetimeIndex(snapshots).normalize()
    day_codes, unique_days = pd.factorize(days, sort=False)
    if len(unique_days) == 0:
        raise ValueError("v1.2 requires at least one complete model day")

    daily = daily_hydro_mwh.reindex(
        pd.DatetimeIndex(unique_days).strftime("%Y-%m-%d")
    )
    if daily.isna().any():
        raise ValueError("v1.2 hydro targets do not align with model snapshots")

    window_codes = day_codes // int(window_days)
    window_count = int(window_codes.max()) + 1
    targets = np.zeros(window_count, dtype=float)
    daily_values = daily.to_numpy(dtype=float)
    day_window_codes = np.arange(len(unique_days)) // int(window_days)
    for window_id in range(window_count):
        targets[window_id] = float(
            daily_values[day_window_codes == window_id].sum()
        )

    grouper = xr.DataArray(
        window_codes,
        coords={"snapshot": np.asarray(snapshots)},
        dims="snapshot",
        name="hydro_window",
    )
    return grouper, targets


def _add_window_hydro_constraints(
    model,
    snapshots: pd.DatetimeIndex,
    daily_hydro_mwh: pd.Series,
    window_days: int,
) -> np.ndarray:
    grouper, targets = _window_constraint_data(
        snapshots,
        daily_hydro_mwh,
        window_days,
    )
    hydro = model.variables["Generator-p"].sel(name="daily_energy_hydro")
    lhs = hydro.groupby(grouper).sum()
    rhs = xr.DataArray(
        targets,
        coords={"hydro_window": np.arange(len(targets))},
        dims="hydro_window",
    )
    model.add_constraints(
        lhs=lhs,
        sign="=",
        rhs=rhs,
        name="v12-window-hydro-energy",
    )
    return targets


def solve_hydro_interday_case(
    *,
    residual_after_nonhydro_mw: np.ndarray,
    snapshots: pd.DatetimeIndex,
    daily_hydro_mwh: pd.Series,
    window_days: int,
    solar_profile: np.ndarray,
    wind_profile: np.ndarray,
    installed_hydro_mw: float,
    available_hydro_mw: float,
    import_limit_mw: float,
    import_price_real_inr_per_mwh: float,
    caps: dict[str, float],
    annualized_costs: dict[str, float],
    bess_duration_h: float,
    charge_efficiency: float,
    discharge_efficiency: float,
    unserved_tolerance_mwh: float,
) -> dict[str, Any]:
    available_fraction = float(available_hydro_mw) / float(installed_hydro_mw)
    network, active_hydro_mw = _build_network(
        residual_after_nonhydro_mw,
        solar_profile,
        wind_profile,
        snapshots=snapshots,
        daily_hydro_mwh=daily_hydro_mwh,
        installed_hydro_mw=installed_hydro_mw,
        hydro_available_fraction=available_fraction,
        import_limit_mw=import_limit_mw,
        import_price_real_inr_per_mwh=import_price_real_inr_per_mwh,
        caps=caps,
        annualized_costs=annualized_costs,
        bess_duration_h=bess_duration_h,
        charge_efficiency=charge_efficiency,
        discharge_efficiency=discharge_efficiency,
    )
    model = network.optimize.create_model(include_objective_constant=False)
    window_targets = _add_window_hydro_constraints(
        model,
        snapshots,
        daily_hydro_mwh,
        window_days,
    )

    gen_p = model.variables["Generator-p"]
    unserved = gen_p.sel(name="unserved_load")
    model.add_objective(unserved.sum(), overwrite=True)
    status1, condition1 = network.optimize.solve_model(solver_name="highs")
    if status1 != "ok" or condition1 != "optimal":
        raise RuntimeError(f"v1.2 stage 1 failed: {status1} / {condition1}")
    minimum_unserved = float(
        np.asarray(
            model.variables["Generator-p"].solution.sel(name="unserved_load")
        ).sum()
    )

    model.add_constraints(
        unserved.sum() <= minimum_unserved + float(unserved_tolerance_mwh),
        name="v12-minimum-shortage-cap",
    )
    gen_nom = model.variables["Generator-p_nom"]
    storage_nom = model.variables["StorageUnit-p_nom"]
    solar_nom = gen_nom.sel(name="candidate_solar")
    wind_nom = gen_nom.sel(name="candidate_wind")
    bess_nom = storage_nom.sel(name="candidate_bess")
    imports = gen_p.sel(name="screened_import")
    import_cost = float(import_price_real_inr_per_mwh) / 1_000_000.0
    objective = (
        solar_nom * float(annualized_costs["solar_million_inr_per_mw_year"])
        + wind_nom * float(annualized_costs["wind_million_inr_per_mw_year"])
        + bess_nom * float(annualized_costs["bess_million_inr_per_mw_year"])
        + imports.sum() * import_cost
    )
    model.add_objective(objective, overwrite=True)
    status2, condition2 = network.optimize.solve_model(solver_name="highs")
    if status2 != "ok" or condition2 != "optimal":
        raise RuntimeError(f"v1.2 stage 2 failed: {status2} / {condition2}")

    solution = model.variables
    p = solution["Generator-p"].solution
    hydro = np.asarray(p.sel(name="daily_energy_hydro"), dtype=float)
    stage2_unserved = float(np.asarray(p.sel(name="unserved_load")).sum())
    solved_gen_nom = solution["Generator-p_nom"].solution
    solved_storage_nom = solution["StorageUnit-p_nom"].solution
    solar_mw = float(
        np.asarray(solved_gen_nom.sel(name="candidate_solar")).item()
    )
    wind_mw = float(
        np.asarray(solved_gen_nom.sel(name="candidate_wind")).item()
    )
    bess_mw = float(
        np.asarray(solved_storage_nom.sel(name="candidate_bess")).item()
    )
    imports_mwh = float(np.asarray(p.sel(name="screened_import")).sum())

    grouper, _ = _window_constraint_data(
        snapshots,
        daily_hydro_mwh,
        window_days,
    )
    window_codes = np.asarray(grouper, dtype=int)
    solved_window = (
        pd.Series(hydro, index=np.arange(len(hydro)))
        .groupby(window_codes)
        .sum()
        .to_numpy(dtype=float)
    )
    max_window_residual = float(
        np.max(np.abs(solved_window - window_targets))
    )
    annual_residual = float(hydro.sum() - daily_hydro_mwh.sum())
    if max_window_residual > 1e-3 or abs(annual_residual) > 1e-3:
        raise RuntimeError("v1.2 hydro-energy conservation failed")

    return {
        "stage1_minimum_unserved_mwh": minimum_unserved,
        "stage2_unserved_mwh": stage2_unserved,
        "built": {
            "solar_combined_mw": solar_mw,
            "wind_onshore_mw": wind_mw,
            "bess_4h_power_mw": bess_mw,
            "bess_4h_energy_mwh": bess_mw * float(bess_duration_h),
            "solar_subtype_allocation_range": _solar_allocation_range(
                solar_mw,
                caps,
            ),
        },
        "imports_mwh": imports_mwh,
        "hydro_generation_mwh": float(hydro.sum()),
        "hydro_peak_mw": float(hydro.max()),
        "hydro_available_power_mw": float(active_hydro_mw),
        "window_days": int(window_days),
        "window_count": len(window_targets),
        "max_window_hydro_energy_residual_mwh": max_window_residual,
        "annual_hydro_energy_residual_mwh": annual_residual,
        "solver": {
            "engine": "PyPSA/Linopy",
            "backend": "HiGHS",
            "stage1": [status1, condition1],
            "stage2": [status2, condition2],
        },
    }


def run_hydro_interday_v12_suite(
    root: Path,
    *,
    profile_path: Path,
    hours: int = 8760,
) -> dict[str, Any]:
    if not 24 <= hours <= 8760 or hours % 24:
        raise ValueError("hours must be whole days between 24 and 8760")

    suite = load_hydro_interday_v12_suite(
        root / "configs/full_pypsa_hydro_interday_v1_2.yaml"
    )
    evidence = validate_station_evidence(root, suite)
    import_suite = load_import_economics_suite(
        root / suite["inherits"]["import_economics"]
    )
    proxy = load_proxy_expansion_suite(
        root / suite["inherits"]["proxy_expansion"]
    )
    future = load_future_adequacy_suite(
        root / suite["inherits"]["future_demand"]
    )
    hourly_base, _, observed = _load_base(root, future)
    daily_hydro = _daily_targets(hourly_base, hours)
    installed_hydro_mw = float(
        observed["electricity"]["capacity_mix_mw"]["hydel"]
    )

    solar_full, wind_full, alignment = _align_profiles(
        profile_path,
        hourly_base["snapshot_ist_naive"],
    )
    cost_data = load_cost_finance_suite(
        root / suite["inherits"]["cost_finance"]
    )
    bess = cost_data["research_2030"]["bess_4h"]
    focus = suite["focus_case"]
    caps = _candidate_caps(root, focus["capacity_envelope_case"], proxy)
    costs = _annualized_costs(root, focus["bess_cost_case"])

    price_lookup = {
        item["id"]: item for item in import_suite["import_price_cases"]
    }
    price = price_lookup[focus["import_price_case"]]
    demand_lookup = {item["id"]: item for item in future["demand_cases"]}
    transfer_lookup = {
        item["id"]: item for item in future["transfer_cases"]
    }

    snapshots = pd.DatetimeIndex(
        hourly_base["snapshot_ist_naive"].iloc[:hours].to_numpy(),
        name="snapshot",
    )
    cases: list[dict[str, Any]] = []
    for demand_id in suite["demand_cases"]:
        demand = demand_lookup[demand_id]
        morphed, _ = morph_load_to_energy_and_peak(
            hourly_base["load_mw"],
            annual_energy_mu=float(demand["annual_energy_mu"]),
            peak_mw=float(demand["peak_mw"]),
        )
        residual = (
            morphed.to_numpy(dtype=float)
            - hourly_base["nonhydro_fixed_mw"].to_numpy(dtype=float)
        )[:hours]
        for transfer_id in suite["transfer_cases"]:
            transfer = transfer_lookup[transfer_id]
            for hydro_case in suite["hydro_availability_cases"]:
                for window_case in suite["interday_windows"]:
                    solved = solve_hydro_interday_case(
                        residual_after_nonhydro_mw=residual,
                        snapshots=snapshots,
                        daily_hydro_mwh=daily_hydro,
                        window_days=int(window_case["window_days"]),
                        solar_profile=solar_full[:hours],
                        wind_profile=wind_full[:hours],
                        installed_hydro_mw=installed_hydro_mw,
                        available_hydro_mw=float(
                            hydro_case["available_hydro_mw"]
                        ),
                        import_limit_mw=float(
                            transfer["import_limit_mw"]
                        ),
                        import_price_real_inr_per_mwh=float(
                            price["real_2021_22_inr_per_mwh"]
                        ),
                        caps=caps,
                        annualized_costs=costs,
                        bess_duration_h=float(bess["duration_hours"]),
                        charge_efficiency=float(
                            bess["charge_efficiency_symmetric"]
                        ),
                        discharge_efficiency=float(
                            bess["discharge_efficiency_symmetric"]
                        ),
                        unserved_tolerance_mwh=float(
                            proxy["objective"]["unserved_tolerance_mwh"]
                        ),
                    )
                    cases.append(
                        {
                            "demand_case": demand_id,
                            "transfer_case": transfer_id,
                            "import_limit_mw": float(
                                transfer["import_limit_mw"]
                            ),
                            "hydro_availability_case": hydro_case["id"],
                            "hydro_case_classification": hydro_case[
                                "source_classification"
                            ],
                            "interday_window_case": window_case["id"],
                            "interday_window_classification": window_case[
                                "classification"
                            ],
                            **solved,
                        }
                    )

    expected = 2 * 3 * 2 * 4
    if len(cases) != expected:
        raise RuntimeError("v1.2 did not solve the complete 48-case matrix")

    baseline = {
        (
            row["demand_case"],
            row["transfer_case"],
            row["hydro_availability_case"],
        ): row
        for row in cases
        if row["window_days"] == 1
    }
    for row in cases:
        base = baseline[
            (
                row["demand_case"],
                row["transfer_case"],
                row["hydro_availability_case"],
            )
        ]
        row["change_vs_1d"] = {
            "unserved_mwh": (
                row["stage2_unserved_mwh"]
                - base["stage2_unserved_mwh"]
            ),
            "shortage_reduction_mwh": (
                base["stage2_unserved_mwh"]
                - row["stage2_unserved_mwh"]
            ),
            "imports_mwh": row["imports_mwh"] - base["imports_mwh"],
            "solar_mw": (
                row["built"]["solar_combined_mw"]
                - base["built"]["solar_combined_mw"]
            ),
            "wind_mw": (
                row["built"]["wind_onshore_mw"]
                - base["built"]["wind_onshore_mw"]
            ),
            "bess_power_mw": (
                row["built"]["bess_4h_power_mw"]
                - base["built"]["bess_4h_power_mw"]
            ),
        }

    return {
        "classification": SUITE_CLASS,
        "prepared_date": suite["prepared_date"],
        "hours": hours,
        "full_financial_year": hours == 8760,
        "cases_solved": len(cases),
        "installed_hydro_mw": installed_hydro_mw,
        "daily_hydro_energy_mwh": float(daily_hydro.sum()),
        "station_evidence_classification": evidence["classification"],
        "renewable_profile_alignment": alignment,
        "focus_case": focus,
        "cases": cases,
        "release": suite["release"],
        "interpretation": [
            (
                "The 1-day case is the v1.1 timing boundary: each day preserves "
                "its own hydro MWh."
            ),
            (
                "The 3-, 7- and 30-day cases preserve hydro energy only within "
                "non-overlapping windows and therefore quantify an increasingly "
                "optimistic interday-flexibility upper bound."
            ),
            (
                "Window length is not reservoir storage duration and is not "
                "derived from reservoir volume, head or inflow physics."
            ),
            (
                "The 130 MW Idukki N-1 case is source-anchored; no full outage "
                "chronology is claimed."
            ),
        ],
    }
