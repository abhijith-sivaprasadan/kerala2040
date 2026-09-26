"""Daily-energy-constrained hydro flexibility for Full-PyPSA v1.1."""
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
from kerala2040.full_pypsa_import_economics import (
    load_import_economics_suite,
    solve_import_economic_case,
)
from kerala2040.full_pypsa_proxy_expansion import (
    _align_profiles,
    _annualized_costs,
    _candidate_caps,
    _solar_allocation_range,
    load_proxy_expansion_suite,
)
from kerala2040.full_pypsa_pypsa_equivalence import _build_pypsa_network

SUITE_CLASS = (
    "full_pypsa_hydro_dispatch_v1_1_"
    "daily_energy_constrained_flexible_hydro_not_reservoir_model"
)
HYDRO_NAME = "flexible_daily_energy_hydro"


def load_hydro_dispatch_suite(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if data.get("classification") != SUITE_CLASS:
        raise ValueError("v1.1 hydro dispatch classification mismatch")
    cases = data["hydro_availability_cases"]
    if [item["id"] for item in cases] != [
        "full_available",
        "n_minus_1_idukki_130mw",
        "derate_90pct",
        "derate_80pct",
    ]:
        raise ValueError("v1.1 hydro availability cases changed")
    capacities = [float(item["available_hydro_mw"]) for item in cases]
    if capacities != sorted(capacities, reverse=True):
        raise ValueError("v1.1 hydro availability cases must be descending")
    release = data["release"]
    if release["daily_energy_constrained_hydro_dispatch_ready"] is not True:
        raise ValueError("v1.1 hydro dispatch is not released")
    for key in (
        "station_level_dispatch_validated",
        "reservoir_model_ready",
        "outage_chronology_validated",
        "total_system_cost_optimization",
        "validated_capacity_plan",
        "scenario_recommendation",
    ):
        if release[key] is not False:
            raise ValueError(f"v1.1 incorrectly enables {key}")
    return data


def validate_hydro_evidence(root: Path, suite: dict[str, Any]) -> dict[str, Any]:
    path = root / suite["inherits"]["hydro_evidence"]
    evidence = json.loads(path.read_text(encoding="utf-8"))
    if float(evidence["aggregate_capacity"]["march_2026_hydro_mw"]) != 2284.42:
        raise ValueError("v1.1 March-2026 hydro boundary changed")
    largest = float(
        evidence["station_unit_anchor"]["largest_verified_single_unit_mw"]
    )
    if largest != 130:
        raise ValueError("v1.1 largest source-anchored hydro unit changed")
    n1 = evidence["availability_cases"]["n_minus_1_idukki_130mw"][
        "available_hydro_mw"
    ]
    if abs(float(n1) - (2284.42 - largest)) > 1e-9:
        raise ValueError("v1.1 N-1 hydro arithmetic mismatch")
    return evidence


def _add_daily_hydro_constraints(
    model,
    snapshots: pd.Index,
    daily_targets_mwh: pd.Series,
) -> None:
    hydro = model.variables["Generator-p"].sel(name=HYDRO_NAME)
    days = pd.DatetimeIndex(snapshots).normalize()
    codes, unique_days = pd.factorize(days, sort=False)
    grouper = xr.DataArray(
        codes,
        coords={"snapshot": snapshots},
        dims="snapshot",
        name="hydro_day",
    )
    energy_by_day = hydro.groupby(grouper).sum()
    target = daily_targets_mwh.reindex(
        pd.DatetimeIndex(unique_days).strftime("%Y-%m-%d")
    )
    if target.isna().any() or len(target) != len(unique_days):
        raise ValueError("v1.1 hydro daily targets do not align with snapshots")
    rhs = xr.DataArray(
        target.to_numpy(dtype=float),
        coords={"hydro_day": np.arange(len(target))},
        dims="hydro_day",
    )
    model.add_constraints(
        energy_by_day == rhs,
        name="v11-hydro-daily-energy",
    )


def solve_flexible_hydro_economic_case(
    *,
    timestamps: pd.DatetimeIndex,
    demand_mw: np.ndarray,
    nonhydro_fixed_mw: np.ndarray,
    daily_hydro_targets_mwh: pd.Series,
    hydro_available_mw: float,
    solar_profile: np.ndarray,
    wind_profile: np.ndarray,
    import_limit_mw: float,
    import_price_real_inr_per_mwh: float,
    caps: dict[str, float],
    annualized_costs: dict[str, float],
    bess_duration_h: float,
    charge_efficiency: float,
    discharge_efficiency: float,
    unserved_tolerance_mwh: float,
) -> dict[str, Any]:
    demand = np.asarray(demand_mw, dtype=float)
    nonhydro = np.asarray(nonhydro_fixed_mw, dtype=float)
    if len(demand) != len(nonhydro) or len(demand) != len(timestamps):
        raise ValueError("v1.1 chronology lengths are inconsistent")
    if hydro_available_mw <= 0:
        raise ValueError("v1.1 hydro availability must be positive")
    if float(daily_hydro_targets_mwh.max()) > hydro_available_mw * 24 + 1e-6:
        raise ValueError("v1.1 hydro daily energy exceeds active availability ceiling")

    residual = demand - nonhydro
    network = _build_pypsa_network(
        residual,
        solar_profile,
        wind_profile,
        import_limit_mw=import_limit_mw,
        caps=caps,
        annualized_costs=annualized_costs,
        bess_duration_h=bess_duration_h,
        charge_efficiency=charge_efficiency,
        discharge_efficiency=discharge_efficiency,
    )
    network.set_snapshots(timestamps)
    network.loads_t.p_set.loc[:, "residual_demand"] = residual
    network.generators_t.p_max_pu.loc[:, "candidate_solar"] = solar_profile
    network.generators_t.p_max_pu.loc[:, "candidate_wind"] = wind_profile
    network.add(
        "Generator",
        HYDRO_NAME,
        bus="kerala",
        p_nom=float(hydro_available_mw),
        p_min_pu=0.0,
        p_max_pu=1.0,
        marginal_cost=0.0,
    )
    import_cost_million = float(import_price_real_inr_per_mwh) / 1_000_000.0
    network.generators.at["screened_import", "marginal_cost"] = import_cost_million

    model = network.optimize.create_model(include_objective_constant=False)
    _add_daily_hydro_constraints(model, network.snapshots, daily_hydro_targets_mwh)

    gen_p = model.variables["Generator-p"]
    gen_nom = model.variables["Generator-p_nom"]
    storage_nom = model.variables["StorageUnit-p_nom"]
    unserved = gen_p.sel(name="unserved_load")
    imports = gen_p.sel(name="screened_import")

    model.add_objective(unserved.sum(), overwrite=True)
    status1, condition1 = network.optimize.solve_model(solver_name="highs")
    if status1 != "ok" or condition1 != "optimal":
        raise RuntimeError(f"v1.1 adequacy stage failed: {status1} / {condition1}")
    minimum_unserved = float(
        np.asarray(
            model.variables["Generator-p"].solution.sel(name="unserved_load")
        ).sum()
    )

    model.add_constraints(
        unserved.sum() <= minimum_unserved + float(unserved_tolerance_mwh),
        name="v11-minimum-shortage-cap",
    )
    solar_nom = gen_nom.sel(name="candidate_solar")
    wind_nom = gen_nom.sel(name="candidate_wind")
    bess_nom = storage_nom.sel(name="candidate_bess")
    investment = (
        solar_nom * float(annualized_costs["solar_million_inr_per_mw_year"])
        + wind_nom * float(annualized_costs["wind_million_inr_per_mw_year"])
        + bess_nom * float(annualized_costs["bess_million_inr_per_mw_year"])
    )
    model.add_objective(
        investment + imports.sum() * import_cost_million,
        overwrite=True,
    )
    status2, condition2 = network.optimize.solve_model(solver_name="highs")
    if status2 != "ok" or condition2 != "optimal":
        raise RuntimeError(f"v1.1 economic stage failed: {status2} / {condition2}")

    solution = model.variables
    stage2_unserved = float(
        np.asarray(solution["Generator-p"].solution.sel(name="unserved_load")).sum()
    )
    solar_mw = float(
        np.asarray(solution["Generator-p_nom"].solution.sel(name="candidate_solar")).item()
    )
    wind_mw = float(
        np.asarray(solution["Generator-p_nom"].solution.sel(name="candidate_wind")).item()
    )
    bess_mw = float(
        np.asarray(solution["StorageUnit-p_nom"].solution.sel(name="candidate_bess")).item()
    )
    imports_mwh = float(
        np.asarray(solution["Generator-p"].solution.sel(name="screened_import")).sum()
    )
    hydro = np.asarray(
        solution["Generator-p"].solution.sel(name=HYDRO_NAME),
        dtype=float,
    )
    solved_daily = (
        pd.Series(hydro, index=timestamps)
        .groupby(pd.DatetimeIndex(timestamps).strftime("%Y-%m-%d"))
        .sum()
    )
    aligned_target = daily_hydro_targets_mwh.reindex(solved_daily.index)
    max_daily_residual = float((solved_daily - aligned_target).abs().max())
    if max_daily_residual > 1e-3:
        raise RuntimeError("v1.1 daily hydro energy conservation failed")

    investment_cost = (
        solar_mw * float(annualized_costs["solar_million_inr_per_mw_year"])
        + wind_mw * float(annualized_costs["wind_million_inr_per_mw_year"])
        + bess_mw * float(annualized_costs["bess_million_inr_per_mw_year"])
    )
    import_cost = imports_mwh * import_cost_million
    return {
        "stage1_minimum_unserved_mwh": minimum_unserved,
        "stage2_unserved_mwh": stage2_unserved,
        "built": {
            "solar_combined_mw": solar_mw,
            "wind_onshore_mw": wind_mw,
            "bess_4h_power_mw": bess_mw,
            "bess_4h_energy_mwh": bess_mw * float(bess_duration_h),
            "solar_subtype_allocation_range": _solar_allocation_range(solar_mw, caps),
        },
        "imports_mwh": imports_mwh,
        "hydro_generation_mwh": float(hydro.sum()),
        "hydro_peak_mw": float(hydro.max()),
        "hydro_available_mw": float(hydro_available_mw),
        "max_daily_hydro_energy_residual_mwh": max_daily_residual,
        "annualized_candidate_investment_million_inr_per_year": investment_cost,
        "import_energy_cost_million_real_2021_22_inr_per_year": import_cost,
        "partial_economic_objective_million_real_2021_22_inr_per_year": (
            investment_cost + import_cost
        ),
        "solver": {
            "engine": "PyPSA/Linopy",
            "backend": "HiGHS",
            "stage1": [status1, condition1],
            "stage2": [status2, condition2],
        },
    }


def run_hydro_dispatch_suite(
    root: Path,
    *,
    profile_path: Path,
    hours: int = 8760,
) -> dict[str, Any]:
    if not 24 <= hours <= 8760 or hours % 24:
        raise ValueError("hours must be whole days between 24 and 8760")

    suite = load_hydro_dispatch_suite(
        root / "configs/full_pypsa_hydro_dispatch_v1_1.yaml"
    )
    evidence = validate_hydro_evidence(root, suite)
    imports_suite = load_import_economics_suite(
        root / "configs/full_pypsa_import_economics_v1_0.yaml"
    )
    proxy = load_proxy_expansion_suite(
        root / "configs/full_pypsa_proxy_expansion_v0_8.yaml"
    )
    future = load_future_adequacy_suite(
        root / "configs/full_pypsa_future_adequacy_v0_4.yaml"
    )
    hourly, _, _ = _load_base(root, future)
    timestamps = pd.DatetimeIndex(hourly["snapshot_ist_naive"].iloc[:hours])
    daily_targets = (
        hourly.iloc[:hours]
        .groupby("date")["hydro_fixed_mw"]
        .sum()
        .astype(float)
    )
    solar_full, wind_full, alignment = _align_profiles(
        profile_path,
        hourly["snapshot_ist_naive"],
    )
    cost_data = load_cost_finance_suite(
        root / "configs/full_pypsa_cost_finance_v0_5.yaml"
    )
    bess = cost_data["research_2030"]["bess_4h"]
    duration = float(bess["duration_hours"])
    eta_c = float(bess["charge_efficiency_symmetric"])
    eta_d = float(bess["discharge_efficiency_symmetric"])

    focus = suite["focus_case"]
    caps = _candidate_caps(root, focus["capacity_envelope_case"], proxy)
    costs = _annualized_costs(root, focus["bess_cost_case"])
    price = next(
        item
        for item in imports_suite["import_price_cases"]
        if item["id"] == focus["import_price_case"]
    )
    demand_lookup = {item["id"]: item for item in future["demand_cases"]}
    transfer_lookup = {item["id"]: item for item in future["transfer_cases"]}

    results: list[dict[str, Any]] = []
    for demand_id in suite["demand_cases"]:
        demand_case = demand_lookup[demand_id]
        morphed, _ = morph_load_to_energy_and_peak(
            hourly["load_mw"],
            annual_energy_mu=float(demand_case["annual_energy_mu"]),
            peak_mw=float(demand_case["peak_mw"]),
        )
        demand_values = morphed.to_numpy(dtype=float)[:hours]
        nonhydro = hourly["nonhydro_fixed_mw"].to_numpy(dtype=float)[:hours]
        for transfer_id in suite["transfer_cases"]:
            transfer = transfer_lookup[transfer_id]
            for hydro_case in suite["hydro_availability_cases"]:
                solved = solve_flexible_hydro_economic_case(
                    timestamps=timestamps,
                    demand_mw=demand_values,
                    nonhydro_fixed_mw=nonhydro,
                    daily_hydro_targets_mwh=daily_targets,
                    hydro_available_mw=float(hydro_case["available_hydro_mw"]),
                    solar_profile=solar_full[:hours],
                    wind_profile=wind_full[:hours],
                    import_limit_mw=float(transfer["import_limit_mw"]),
                    import_price_real_inr_per_mwh=float(
                        price["real_2021_22_inr_per_mwh"]
                    ),
                    caps=caps,
                    annualized_costs=costs,
                    bess_duration_h=duration,
                    charge_efficiency=eta_c,
                    discharge_efficiency=eta_d,
                    unserved_tolerance_mwh=float(
                        imports_suite["objective"]["unserved_tolerance_mwh"]
                    ),
                )
                results.append(
                    {
                        "demand_case": demand_id,
                        "transfer_case": transfer_id,
                        "import_limit_mw": float(transfer["import_limit_mw"]),
                        "hydro_availability_case": hydro_case["id"],
                        "hydro_case_classification": hydro_case["classification"],
                        **solved,
                    }
                )

    expected = (
        len(suite["demand_cases"])
        * len(suite["transfer_cases"])
        * len(suite["hydro_availability_cases"])
    )
    if len(results) != expected:
        raise RuntimeError("v1.1 did not solve the complete focused matrix")

    return {
        "classification": SUITE_CLASS,
        "prepared_date": suite["prepared_date"],
        "hours": hours,
        "full_financial_year": hours == 8760,
        "cases_solved": len(results),
        "focus_case": focus,
        "renewable_profile_alignment": alignment,
        "hydro_evidence_classification": evidence["classification"],
        "cases": results,
        "release": suite["release"],
        "interpretation": [
            (
                "Every case preserves the same FY2024-25 daily hydro MWh used by the "
                "earlier proxy chronology; only intraday timing changes."
            ),
            (
                "The 130 MW N-1 case is anchored to the verified Idukki unit size. "
                "The 10% and 20% aggregate deratings are declared stress assumptions."
            ),
            (
                "v1.1 is not a reservoir/cascade model and does not allocate observed "
                "daily hydro energy to individual stations."
            ),
        ],
    }
