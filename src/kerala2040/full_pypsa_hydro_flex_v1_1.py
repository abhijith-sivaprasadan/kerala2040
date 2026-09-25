"""Daily-energy-constrained hydro flexibility in the v1.0 PyPSA expansion screen."""
from __future__ import annotations

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
from kerala2040.full_pypsa_import_economics import load_import_economics_suite
from kerala2040.full_pypsa_proxy_expansion import (
    _align_profiles,
    _annualized_costs,
    _candidate_caps,
    _solar_allocation_range,
    load_proxy_expansion_suite,
)

SUITE_CLASS = "full_pypsa_hydro_flex_v1_1_daily_energy_constrained_partial_economics"


def load_hydro_flex_v11_suite(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if data.get("classification") != SUITE_CLASS:
        raise ValueError("v1.1 hydro-flex classification mismatch")
    release = data["release"]
    if release["daily_energy_constrained_hydro_expansion_sensitivity_ready"] is not True:
        raise ValueError("v1.1 hydro flexibility not released")
    for key in (
        "reservoir_model_ready",
        "station_outage_model_ready",
        "hydro_economic_dispatch_validated",
        "total_system_cost_optimization",
        "validated_capacity_plan",
        "scenario_recommendation",
    ):
        if release[key] is not False:
            raise ValueError(f"v1.1 incorrectly enables {key}")
    return data


def _daily_targets(hourly_base: pd.DataFrame, hours: int) -> pd.Series:
    hourly = hourly_base.iloc[:hours].copy()
    counts = hourly.groupby("date").size()
    if not counts.eq(24).all():
        raise ValueError("v1.1 requires complete 24-hour days")
    target = hourly.groupby("date")["hydro_fixed_mw"].sum().astype(float)
    if (target <= 0).any():
        raise ValueError("v1.1 daily hydro energy must be positive")
    return target


def _build_network(
    residual_after_nonhydro_mw: np.ndarray,
    solar_profile: np.ndarray,
    wind_profile: np.ndarray,
    *,
    snapshots: pd.DatetimeIndex,
    daily_hydro_mwh: pd.Series,
    installed_hydro_mw: float,
    hydro_available_fraction: float,
    import_limit_mw: float,
    import_price_real_inr_per_mwh: float,
    caps: dict[str, float],
    annualized_costs: dict[str, float],
    bess_duration_h: float,
    charge_efficiency: float,
    discharge_efficiency: float,
):
    import pypsa

    available_hydro_mw = float(installed_hydro_mw) * float(hydro_available_fraction)
    if not 0 < hydro_available_fraction <= 1:
        raise ValueError("hydro availability fraction must be in (0,1]")
    if (daily_hydro_mwh > available_hydro_mw * 24 + 1e-6).any():
        raise ValueError("hydro availability case cannot deliver preserved daily hydro energy")

    n = pypsa.Network()
    n.set_snapshots(snapshots)
    n.snapshot_weightings.loc[:, :] = 1.0
    n.add("Bus", "kerala")
    n.add("Load", "residual_after_nonhydro", bus="kerala", p_set=residual_after_nonhydro_mw)
    n.add(
        "Generator",
        "daily_energy_hydro",
        bus="kerala",
        p_nom=available_hydro_mw,
        p_min_pu=0.0,
        p_max_pu=1.0,
        marginal_cost=0.0,
    )
    n.add(
        "Generator",
        "candidate_solar",
        bus="kerala",
        p_nom_extendable=True,
        p_nom_max=float(caps["solar_total_headroom_mw"]),
        p_max_pu=solar_profile,
        capital_cost=float(annualized_costs["solar_million_inr_per_mw_year"]),
        marginal_cost=0.0,
    )
    n.add(
        "Generator",
        "candidate_wind",
        bus="kerala",
        p_nom_extendable=True,
        p_nom_max=float(caps["wind_headroom_mw"]),
        p_max_pu=wind_profile,
        capital_cost=float(annualized_costs["wind_million_inr_per_mw_year"]),
        marginal_cost=0.0,
    )
    n.add(
        "Generator",
        "screened_import",
        bus="kerala",
        p_nom=float(import_limit_mw),
        marginal_cost=float(import_price_real_inr_per_mwh) / 1_000_000.0,
    )
    n.add(
        "Generator",
        "unserved_load",
        bus="kerala",
        p_nom=max(float(np.maximum(residual_after_nonhydro_mw, 0).max()), 1.0),
        marginal_cost=0.0,
    )
    spill_cap = max(
        float(np.maximum(-residual_after_nonhydro_mw, 0).max())
        + float(caps["solar_total_headroom_mw"])
        + float(caps["wind_headroom_mw"])
        + float(import_limit_mw)
        + available_hydro_mw,
        1.0,
    )
    n.add(
        "Generator",
        "spill_sink",
        bus="kerala",
        p_nom=spill_cap,
        p_min_pu=-1.0,
        p_max_pu=0.0,
        marginal_cost=0.0,
    )
    n.add(
        "StorageUnit",
        "candidate_bess",
        bus="kerala",
        p_nom_extendable=True,
        p_nom_max=float(caps["bess_power_headroom_mw"]),
        max_hours=float(bess_duration_h),
        efficiency_store=float(charge_efficiency),
        efficiency_dispatch=float(discharge_efficiency),
        cyclic_state_of_charge=True,
        capital_cost=float(annualized_costs["bess_million_inr_per_mw_year"]),
        marginal_cost=0.0,
    )
    return n, available_hydro_mw


def _add_daily_hydro_constraints(model, snapshots, daily_hydro_mwh: pd.Series) -> None:
    p = model.variables["Generator-p"].sel(name="daily_energy_hydro")
    days = pd.DatetimeIndex(snapshots).normalize()
    codes, unique_days = pd.factorize(days, sort=False)
    grouper = xr.DataArray(
        codes,
        coords={"snapshot": np.asarray(snapshots)},
        dims="snapshot",
        name="hydro_day",
    )
    lhs = p.groupby(grouper).sum()
    target = daily_hydro_mwh.reindex(pd.DatetimeIndex(unique_days).strftime("%Y-%m-%d"))
    if target.isna().any():
        raise ValueError("daily hydro targets do not align with model snapshots")
    rhs = xr.DataArray(
        target.to_numpy(dtype=float),
        coords={"hydro_day": np.arange(len(target))},
        dims="hydro_day",
    )
    model.add_constraints(lhs=lhs, sign="=", rhs=rhs, name="v11-daily-hydro-energy")


def solve_hydro_flex_case(
    *,
    residual_after_nonhydro_mw: np.ndarray,
    snapshots: pd.DatetimeIndex,
    daily_hydro_mwh: pd.Series,
    solar_profile: np.ndarray,
    wind_profile: np.ndarray,
    installed_hydro_mw: float,
    hydro_available_fraction: float,
    import_limit_mw: float,
    import_price_real_inr_per_mwh: float,
    caps: dict[str, float],
    annualized_costs: dict[str, float],
    bess_duration_h: float,
    charge_efficiency: float,
    discharge_efficiency: float,
    unserved_tolerance_mwh: float,
) -> dict[str, Any]:
    n, available_hydro_mw = _build_network(
        residual_after_nonhydro_mw,
        solar_profile,
        wind_profile,
        snapshots=snapshots,
        daily_hydro_mwh=daily_hydro_mwh,
        installed_hydro_mw=installed_hydro_mw,
        hydro_available_fraction=hydro_available_fraction,
        import_limit_mw=import_limit_mw,
        import_price_real_inr_per_mwh=import_price_real_inr_per_mwh,
        caps=caps,
        annualized_costs=annualized_costs,
        bess_duration_h=bess_duration_h,
        charge_efficiency=charge_efficiency,
        discharge_efficiency=discharge_efficiency,
    )
    model = n.optimize.create_model(include_objective_constant=False)
    _add_daily_hydro_constraints(model, snapshots, daily_hydro_mwh)
    gen_p = model.variables["Generator-p"]
    unserved = gen_p.sel(name="unserved_load")
    model.add_objective(unserved.sum(), overwrite=True)
    status1, condition1 = n.optimize.solve_model(solver_name="highs")
    if status1 != "ok" or condition1 != "optimal":
        raise RuntimeError(f"v1.1 stage 1 failed: {status1} / {condition1}")
    minimum_unserved = float(
        np.asarray(
            model.variables["Generator-p"].solution.sel(name="unserved_load")
        ).sum()
    )

    model.add_constraints(
        unserved.sum() <= minimum_unserved + float(unserved_tolerance_mwh),
        name="v11-minimum-shortage-cap",
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
    status2, condition2 = n.optimize.solve_model(solver_name="highs")
    if status2 != "ok" or condition2 != "optimal":
        raise RuntimeError(f"v1.1 stage 2 failed: {status2} / {condition2}")

    p = model.variables["Generator-p"].solution
    hydro = np.asarray(p.sel(name="daily_energy_hydro"), dtype=float)
    stage2_unserved = float(np.asarray(p.sel(name="unserved_load")).sum())
    solved_gen_nom = model.variables["Generator-p_nom"].solution
    solved_storage_nom = model.variables["StorageUnit-p_nom"].solution
    solar_mw = float(np.asarray(solved_gen_nom.sel(name="candidate_solar")).item())
    wind_mw = float(np.asarray(solved_gen_nom.sel(name="candidate_wind")).item())
    bess_mw = float(np.asarray(solved_storage_nom.sel(name="candidate_bess")).item())
    imports_mwh = float(np.asarray(p.sel(name="screened_import")).sum())
    hydro_by_day = pd.Series(hydro, index=snapshots).groupby(snapshots.normalize()).sum()
    target = daily_hydro_mwh.reindex(hydro_by_day.index.strftime("%Y-%m-%d"))
    max_daily_residual = float(np.max(np.abs(hydro_by_day.to_numpy() - target.to_numpy())))

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
        "hydro_available_power_mw": available_hydro_mw,
        "hydro_available_fraction": float(hydro_available_fraction),
        "max_daily_hydro_energy_residual_mwh": max_daily_residual,
        "solver": {
            "engine": "PyPSA/Linopy",
            "backend": "HiGHS",
            "stage1": [status1, condition1],
            "stage2": [status2, condition2],
        },
    }


def run_hydro_flex_v11_suite(root: Path, *, profile_path: Path, hours: int = 8760) -> dict[str, Any]:
    if not 24 <= hours <= 8760 or hours % 24:
        raise ValueError("hours must be whole days between 24 and 8760")
    suite = load_hydro_flex_v11_suite(root / "configs/full_pypsa_hydro_flex_v1_1.yaml")
    import_suite = load_import_economics_suite(root / suite["inherits"]["import_economics"])
    proxy = load_proxy_expansion_suite(root / suite["inherits"]["proxy_expansion"])
    future = load_future_adequacy_suite(root / suite["inherits"]["future_demand"])
    hourly_base, _, observed = _load_base(root, future)
    daily_hydro = _daily_targets(hourly_base, hours)
    capacities = observed["electricity"]["capacity_mix_mw"]
    installed_hydro_mw = float(capacities["hydel"])
    maximum_daily_hydro_mwh = float(daily_hydro.max())
    minimum_feasible_hydro_power_mw = maximum_daily_hydro_mwh / 24.0
    minimum_feasible_hydro_fraction = (
        minimum_feasible_hydro_power_mw / installed_hydro_mw
    )
    configured_fractions = [
        float(x["available_power_fraction"])
        for x in suite["matrix"]["hydro_availability_cases"]
    ]
    if min(configured_fractions) + 1e-12 < minimum_feasible_hydro_fraction:
        raise ValueError(
            "configured hydro availability falls below exact-daily-energy feasibility floor"
        )

    solar_full, wind_full, alignment = _align_profiles(
        profile_path, hourly_base["snapshot_ist_naive"]
    )
    cost_data = load_cost_finance_suite(root / suite["inherits"]["cost_finance"])
    bess = cost_data["research_2030"]["bess_4h"]
    demand_lookup = {x["id"]: x for x in future["demand_cases"]}
    transfer_lookup = {x["id"]: x for x in future["transfer_cases"]}
    price_lookup = {x["id"]: x for x in import_suite["import_price_cases"]}
    caps = _candidate_caps(root, suite["matrix"]["capacity_envelope_case"], proxy)
    costs = _annualized_costs(root, suite["matrix"]["bess_cost_case"])

    cases = []
    for demand_id in suite["matrix"]["demand_cases"]:
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
        snapshots = pd.DatetimeIndex(
            hourly_base["snapshot_ist_naive"].iloc[:hours].to_numpy(),
            name="snapshot",
        )
        for transfer_id in suite["matrix"]["transfer_cases"]:
            transfer = transfer_lookup[transfer_id]
            for hydro_case in suite["matrix"]["hydro_availability_cases"]:
                for price_id in suite["matrix"]["import_price_cases"]:
                    price = price_lookup[price_id]
                    solved = solve_hydro_flex_case(
                        residual_after_nonhydro_mw=residual,
                        snapshots=snapshots,
                        daily_hydro_mwh=daily_hydro,
                        solar_profile=solar_full[:hours],
                        wind_profile=wind_full[:hours],
                        installed_hydro_mw=installed_hydro_mw,
                        hydro_available_fraction=float(hydro_case["available_power_fraction"]),
                        import_limit_mw=float(transfer["import_limit_mw"]),
                        import_price_real_inr_per_mwh=float(price["real_2021_22_inr_per_mwh"]),
                        caps=caps,
                        annualized_costs=costs,
                        bess_duration_h=float(bess["duration_hours"]),
                        charge_efficiency=float(bess["charge_efficiency_symmetric"]),
                        discharge_efficiency=float(bess["discharge_efficiency_symmetric"]),
                        unserved_tolerance_mwh=float(proxy["objective"]["unserved_tolerance_mwh"]),
                    )
                    cases.append({
                        "demand_case": demand_id,
                        "transfer_case": transfer_id,
                        "import_limit_mw": float(transfer["import_limit_mw"]),
                        "hydro_availability_case": hydro_case["id"],
                        "import_price_case": price_id,
                        **solved,
                    })

    expected = 2 * 3 * 3 * 3
    if len(cases) != expected:
        raise RuntimeError("v1.1 did not solve the complete 54-case matrix")
    if max(c["max_daily_hydro_energy_residual_mwh"] for c in cases) > 1e-3:
        raise RuntimeError("v1.1 daily hydro energy conservation failed")

    return {
        "classification": SUITE_CLASS,
        "prepared_date": suite["prepared_date"],
        "hours": hours,
        "full_financial_year": hours == 8760,
        "cases_solved": len(cases),
        "installed_hydro_mw": installed_hydro_mw,
        "daily_hydro_energy_mwh": float(daily_hydro.sum()),
        "maximum_daily_hydro_mwh": maximum_daily_hydro_mwh,
        "minimum_feasible_hydro_power_mw": minimum_feasible_hydro_power_mw,
        "minimum_feasible_hydro_fraction": minimum_feasible_hydro_fraction,
        "renewable_profile_alignment": alignment,
        "cases": cases,
        "release": suite["release"],
        "interpretation": [
            "Hydro can move within each day but cannot move energy between days.",
            "Every modelled day preserves the same FY2024-25 observed/imputed hydro MWh as v0.3.",
            "Availability cases derate only the aggregate hydro power ceiling; they are synthetic outage sensitivities, not station outage histories.",
            "Reservoir/cascade physics and hydro opportunity cost remain unresolved.",
        ],
    }
