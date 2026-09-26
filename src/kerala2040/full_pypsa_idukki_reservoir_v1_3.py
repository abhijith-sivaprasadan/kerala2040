"""Stateful Idukki reservoir pilot for Full-PyPSA v1.3.

This module deliberately models only the Idukki reservoir as a stateful hydro
store. Its water input is a reconstructed net water-balance residual derived
from observed effective storage changes and Idukki station generation. It is
not labelled or interpreted as catchment inflow.
"""
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
from kerala2040.full_pypsa_hydro_flex_v1_1 import _daily_targets
from kerala2040.full_pypsa_hydro_interday_v1_2 import solve_hydro_interday_case
from kerala2040.full_pypsa_import_economics import load_import_economics_suite
from kerala2040.full_pypsa_proxy_expansion import (
    _align_profiles,
    _annualized_costs,
    _candidate_caps,
    _solar_allocation_range,
    load_proxy_expansion_suite,
)

SUITE_CLASS = (
    "full_pypsa_idukki_reservoir_v1_3_"
    "stateful_net_water_balance_pilot_not_catchment_inflow_model"
)


def load_idukki_reservoir_v13_suite(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if data.get("classification") != SUITE_CLASS:
        raise ValueError("v1.3 Idukki reservoir classification mismatch")

    period = data["pilot_period"]
    if int(period["hours"]) != 8736:
        raise ValueError("v1.3 pilot period changed")
    if period["start"] != "2024-04-01":
        raise ValueError("v1.3 pilot start changed")
    if period["dispatch_end"] != "2025-03-30":
        raise ValueError("v1.3 dispatch end changed")
    if period["terminal_storage_date"] != "2025-03-31":
        raise ValueError("v1.3 terminal storage date changed")

    idukki = data["idukki"]
    if float(idukki["full_effective_storage_mcm"]) != 1460.0:
        raise ValueError("v1.3 Idukki storage boundary changed")
    if float(idukki["station_energy_equivalent_mwh_per_mcm"]) != 1470.0:
        raise ValueError("v1.3 Idukki energy-equivalent conversion changed")

    availability = data["idukki_availability_cases"]
    if [item["id"] for item in availability] != [
        "full_available",
        "n_minus_1_130mw",
    ]:
        raise ValueError("v1.3 availability cases changed")
    if [float(item["powerhouse_mw"]) for item in availability] != [780.0, 650.0]:
        raise ValueError("v1.3 powerhouse boundaries changed")

    release = data["release"]
    for key in (
        "idukki_stateful_reservoir_pilot_ready",
        "reconstructed_net_water_balance_ready",
        "same_horizon_v1_2_comparison_ready",
    ):
        if release[key] is not True:
            raise ValueError(f"v1.3 expected release flag is false: {key}")
    for key in (
        "catchment_inflow_model_ready",
        "observed_spill_release_model_ready",
        "head_dependent_efficiency_ready",
        "cascade_model_ready",
        "environmental_release_model_ready",
        "hydro_economic_dispatch_validated",
        "full_reservoir_model_validated",
        "total_system_cost_optimization",
        "validated_capacity_plan",
        "scenario_recommendation",
    ):
        if release[key] is not False:
            raise ValueError(f"v1.3 incorrectly enables {key}")
    return data


def load_idukki_water_balance_inputs(
    root: Path,
    suite: dict[str, Any],
) -> dict[str, Any]:
    start = pd.Timestamp(suite["pilot_period"]["start"])
    dispatch_end = pd.Timestamp(suite["pilot_period"]["dispatch_end"])
    terminal_date = pd.Timestamp(suite["pilot_period"]["terminal_storage_date"])
    storage_days = pd.date_range(start, terminal_date, freq="D")
    dispatch_days = pd.date_range(start, dispatch_end, freq="D")

    reservoir = pd.read_csv(
        root / suite["source_files"]["reservoir_daily"],
        parse_dates=["date"],
    )
    idukki_res = reservoir.loc[
        reservoir["reservoir_name_as_reported"].eq("IDUKKI")
    ].copy()
    idukki_res = idukki_res.set_index("date").sort_index()

    storage_observed = pd.to_numeric(
        idukki_res["effective_storage_mcm"],
        errors="coerce",
    ).reindex(storage_days)
    observed_storage_days = int(storage_observed.notna().sum())
    storage = storage_observed.interpolate(method="time", limit_area="inside")
    if storage.isna().any():
        raise ValueError("v1.3 cannot close Idukki storage gaps at period boundaries")

    ratio_source = idukki_res.loc[
        idukki_res["effective_storage_mcm"].notna()
        & idukki_res["generation_capability_station_mu"].notna()
        & (idukki_res["effective_storage_mcm"] > 0)
    ]
    ratio = (
        pd.to_numeric(
            ratio_source["generation_capability_station_mu"],
            errors="coerce",
        )
        * 1000.0
        / pd.to_numeric(ratio_source["effective_storage_mcm"], errors="coerce")
    ).dropna()
    if ratio.empty:
        raise ValueError("v1.3 cannot derive Idukki station energy equivalent")
    derived_conversion = float(ratio.median())
    configured_conversion = float(
        suite["idukki"]["station_energy_equivalent_mwh_per_mcm"]
    )
    if abs(derived_conversion - configured_conversion) > 2.0:
        raise ValueError(
            "v1.3 source-derived Idukki energy equivalent no longer matches config"
        )

    hydro = pd.read_csv(
        root / suite["source_files"]["hydro_station_daily"],
        parse_dates=["date"],
    )
    idukki_gen = hydro.loc[
        hydro["station_name_as_reported"].eq("Idukki")
    ].copy()
    idukki_gen = idukki_gen.set_index("date").sort_index()
    generation_observed_mu = pd.to_numeric(
        idukki_gen["generation_mu"],
        errors="coerce",
    ).reindex(dispatch_days)
    observed_generation_days = int(generation_observed_mu.notna().sum())
    generation_mu = generation_observed_mu.interpolate(
        method="time",
        limit_area="inside",
    )
    if generation_mu.isna().any():
        raise ValueError("v1.3 cannot close Idukki generation gaps at period boundaries")
    generation_mwh = generation_mu * 1000.0

    storage_now = storage.reindex(dispatch_days)
    storage_next = storage.reindex(dispatch_days + pd.Timedelta(days=1))
    storage_next.index = dispatch_days
    net_water_balance_mcm_day = (
        storage_next - storage_now + generation_mwh / configured_conversion
    )

    initial_storage_mcm = float(storage.loc[start])
    terminal_storage_mcm = float(storage.loc[terminal_date])
    replay_terminal = initial_storage_mcm + float(
        (
            net_water_balance_mcm_day
            - generation_mwh / configured_conversion
        ).sum()
    )
    replay_residual_mcm = replay_terminal - terminal_storage_mcm
    if abs(replay_residual_mcm) > 1e-6:
        raise RuntimeError("v1.3 source water-balance replay does not close")

    return {
        "dispatch_days": dispatch_days,
        "storage_mcm": storage,
        "generation_mwh": generation_mwh,
        "net_water_balance_mcm_day": net_water_balance_mcm_day,
        "initial_storage_mcm": initial_storage_mcm,
        "terminal_storage_mcm": terminal_storage_mcm,
        "full_storage_mcm": float(suite["idukki"]["full_effective_storage_mcm"]),
        "energy_equivalent_mwh_per_mcm": configured_conversion,
        "derived_energy_equivalent_mwh_per_mcm": derived_conversion,
        "observed_storage_days": observed_storage_days,
        "interpolated_storage_days": int(len(storage_days) - observed_storage_days),
        "observed_generation_days": observed_generation_days,
        "interpolated_generation_days": int(
            len(dispatch_days) - observed_generation_days
        ),
        "historical_replay_terminal_residual_mcm": replay_residual_mcm,
    }


def _hourly_from_daily(
    daily: pd.Series,
    snapshots: pd.DatetimeIndex,
    *,
    divide_by_24: bool,
) -> np.ndarray:
    days = pd.DatetimeIndex(snapshots).normalize()
    source = daily.copy()
    source.index = pd.DatetimeIndex(source.index).normalize()
    values = source.reindex(days)
    if values.isna().any():
        raise ValueError("v1.3 daily source does not align with hourly snapshots")
    arr = values.to_numpy(dtype=float)
    if divide_by_24:
        arr = arr / 24.0
    return arr


def _build_idukki_network(
    residual_after_nonhydro_mw: np.ndarray,
    solar_profile: np.ndarray,
    wind_profile: np.ndarray,
    *,
    snapshots: pd.DatetimeIndex,
    other_hydro_daily_mwh: pd.Series,
    other_hydro_power_mw: float,
    idukki_power_mw: float,
    idukki_full_storage_mcm: float,
    idukki_initial_storage_mcm: float,
    idukki_terminal_storage_mcm: float,
    idukki_energy_equivalent_mwh_per_mcm: float,
    idukki_net_water_balance_mcm_day: pd.Series,
    import_limit_mw: float,
    import_price_real_inr_per_mwh: float,
    caps: dict[str, float],
    annualized_costs: dict[str, float],
    bess_duration_h: float,
    charge_efficiency: float,
    discharge_efficiency: float,
):
    import pypsa

    if idukki_power_mw <= 0:
        raise ValueError("v1.3 Idukki power must be positive")
    if not 0 <= idukki_initial_storage_mcm <= idukki_full_storage_mcm:
        raise ValueError("v1.3 initial storage outside bounds")
    if not 0 <= idukki_terminal_storage_mcm <= idukki_full_storage_mcm:
        raise ValueError("v1.3 terminal storage outside bounds")
    if (other_hydro_daily_mwh < -1e-6).any():
        raise ValueError("v1.3 non-Idukki daily hydro energy became negative")
    if (other_hydro_daily_mwh > other_hydro_power_mw * 24 + 1e-6).any():
        raise ValueError("v1.3 non-Idukki daily hydro energy exceeds power ceiling")

    conversion = float(idukki_energy_equivalent_mwh_per_mcm)
    inflow_energy_mw = _hourly_from_daily(
        idukki_net_water_balance_mcm_day * conversion,
        snapshots,
        divide_by_24=True,
    )
    full_storage_mwh = float(idukki_full_storage_mcm) * conversion
    initial_storage_mwh = float(idukki_initial_storage_mcm) * conversion
    terminal_storage_mwh = float(idukki_terminal_storage_mcm) * conversion
    soc_set = pd.Series(np.nan, index=snapshots, dtype=float)
    soc_set.iloc[-1] = terminal_storage_mwh

    n = pypsa.Network()
    n.set_snapshots(snapshots)
    n.snapshot_weightings.loc[:, :] = 1.0
    n.add("Bus", "kerala")
    n.add(
        "Load",
        "residual_after_nonhydro",
        bus="kerala",
        p_set=residual_after_nonhydro_mw,
    )
    n.add(
        "StorageUnit",
        "idukki_reservoir",
        bus="kerala",
        p_nom=float(idukki_power_mw),
        max_hours=full_storage_mwh / float(idukki_power_mw),
        state_of_charge_initial=initial_storage_mwh,
        state_of_charge_set=soc_set,
        cyclic_state_of_charge=False,
        p_min_pu=0.0,
        p_max_pu=1.0,
        efficiency_store=1.0,
        efficiency_dispatch=1.0,
        standing_loss=0.0,
        inflow=inflow_energy_mw,
        spill_cost=0.0,
        marginal_cost=0.0,
    )
    n.add(
        "Generator",
        "other_hydro",
        bus="kerala",
        p_nom=float(other_hydro_power_mw),
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
        + float(idukki_power_mw)
        + float(other_hydro_power_mw),
        1.0,
    )
    n.add(
        "Generator",
        "electric_spill_sink",
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
    return n


def _add_other_hydro_daily_constraints(
    model,
    snapshots: pd.DatetimeIndex,
    daily_mwh: pd.Series,
) -> None:
    p = model.variables["Generator-p"].sel(name="other_hydro")
    days = pd.DatetimeIndex(snapshots).normalize()
    codes, unique_days = pd.factorize(days, sort=False)
    grouper = xr.DataArray(
        codes,
        coords={"snapshot": np.asarray(snapshots)},
        dims="snapshot",
        name="other_hydro_day",
    )
    lhs = p.groupby(grouper).sum()
    target = daily_mwh.reindex(
        pd.DatetimeIndex(unique_days).strftime("%Y-%m-%d")
    )
    if target.isna().any():
        target = daily_mwh.copy()
        target.index = pd.DatetimeIndex(target.index).strftime("%Y-%m-%d")
        target = target.reindex(pd.DatetimeIndex(unique_days).strftime("%Y-%m-%d"))
    if target.isna().any():
        raise ValueError("v1.3 non-Idukki hydro targets do not align")
    rhs = xr.DataArray(
        target.to_numpy(dtype=float),
        coords={"other_hydro_day": np.arange(len(target))},
        dims="other_hydro_day",
    )
    model.add_constraints(
        lhs=lhs,
        sign="=",
        rhs=rhs,
        name="v13-other-hydro-daily-energy",
    )


def solve_idukki_reservoir_case(
    *,
    residual_after_nonhydro_mw: np.ndarray,
    snapshots: pd.DatetimeIndex,
    other_hydro_daily_mwh: pd.Series,
    other_hydro_power_mw: float,
    idukki_power_mw: float,
    idukki_full_storage_mcm: float,
    idukki_initial_storage_mcm: float,
    idukki_terminal_storage_mcm: float,
    idukki_energy_equivalent_mwh_per_mcm: float,
    idukki_net_water_balance_mcm_day: pd.Series,
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
    n = _build_idukki_network(
        residual_after_nonhydro_mw,
        solar_profile,
        wind_profile,
        snapshots=snapshots,
        other_hydro_daily_mwh=other_hydro_daily_mwh,
        other_hydro_power_mw=other_hydro_power_mw,
        idukki_power_mw=idukki_power_mw,
        idukki_full_storage_mcm=idukki_full_storage_mcm,
        idukki_initial_storage_mcm=idukki_initial_storage_mcm,
        idukki_terminal_storage_mcm=idukki_terminal_storage_mcm,
        idukki_energy_equivalent_mwh_per_mcm=idukki_energy_equivalent_mwh_per_mcm,
        idukki_net_water_balance_mcm_day=idukki_net_water_balance_mcm_day,
        import_limit_mw=import_limit_mw,
        import_price_real_inr_per_mwh=import_price_real_inr_per_mwh,
        caps=caps,
        annualized_costs=annualized_costs,
        bess_duration_h=bess_duration_h,
        charge_efficiency=charge_efficiency,
        discharge_efficiency=discharge_efficiency,
    )
    model = n.optimize.create_model(include_objective_constant=False)
    _add_other_hydro_daily_constraints(model, snapshots, other_hydro_daily_mwh)

    gen_p = model.variables["Generator-p"]
    unserved = gen_p.sel(name="unserved_load")
    model.add_objective(unserved.sum(), overwrite=True)
    status1, condition1 = n.optimize.solve_model(solver_name="highs")
    if status1 != "ok" or condition1 != "optimal":
        raise RuntimeError(f"v1.3 stage 1 failed: {status1} / {condition1}")
    minimum_unserved = float(
        np.asarray(
            model.variables["Generator-p"].solution.sel(name="unserved_load")
        ).sum()
    )

    model.add_constraints(
        unserved.sum() <= minimum_unserved + float(unserved_tolerance_mwh),
        name="v13-minimum-shortage-cap",
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
        raise RuntimeError(f"v1.3 stage 2 failed: {status2} / {condition2}")

    solution = model.variables
    p = solution["Generator-p"].solution
    su_dispatch = solution["StorageUnit-p_dispatch"].solution
    soc = solution["StorageUnit-state_of_charge"].solution
    spill = solution["StorageUnit-spill"].solution
    solved_gen_nom = solution["Generator-p_nom"].solution
    solved_storage_nom = solution["StorageUnit-p_nom"].solution

    idukki_dispatch = np.asarray(
        su_dispatch.sel(name="idukki_reservoir"),
        dtype=float,
    )
    idukki_soc_mwh = np.asarray(
        soc.sel(name="idukki_reservoir"),
        dtype=float,
    )
    idukki_spill_mwh = np.asarray(
        spill.sel(name="idukki_reservoir"),
        dtype=float,
    )
    conversion = float(idukki_energy_equivalent_mwh_per_mcm)

    solar_mw = float(
        np.asarray(solved_gen_nom.sel(name="candidate_solar")).item()
    )
    wind_mw = float(
        np.asarray(solved_gen_nom.sel(name="candidate_wind")).item()
    )
    bess_mw = float(
        np.asarray(solved_storage_nom.sel(name="candidate_bess")).item()
    )
    stage2_unserved = float(np.asarray(p.sel(name="unserved_load")).sum())
    imports_mwh = float(np.asarray(p.sel(name="screened_import")).sum())

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
        "other_hydro_generation_mwh": float(
            np.asarray(p.sel(name="other_hydro")).sum()
        ),
        "idukki_generation_mwh": float(idukki_dispatch.sum()),
        "idukki_generation_peak_mw": float(idukki_dispatch.max()),
        "idukki_storage_min_mcm": float(idukki_soc_mwh.min() / conversion),
        "idukki_storage_max_mcm": float(idukki_soc_mwh.max() / conversion),
        "idukki_storage_terminal_mcm": float(idukki_soc_mwh[-1] / conversion),
        "idukki_spill_equivalent_mwh": float(idukki_spill_mwh.sum()),
        "idukki_spill_equivalent_mcm": float(
            idukki_spill_mwh.sum() / conversion
        ),
        "solver": {
            "engine": "PyPSA/Linopy",
            "backend": "HiGHS",
            "stage1": [status1, condition1],
            "stage2": [status2, condition2],
        },
    }


def run_idukki_reservoir_v13_suite(
    root: Path,
    *,
    profile_path: Path,
) -> dict[str, Any]:
    suite = load_idukki_reservoir_v13_suite(
        root / "configs/full_pypsa_idukki_reservoir_v1_3.yaml"
    )
    source = load_idukki_water_balance_inputs(root, suite)
    hours = int(suite["pilot_period"]["hours"])

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
    daily_total_hydro = _daily_targets(hourly_base, hours)

    daily_idukki = source["generation_mwh"].copy()
    daily_idukki.index = pd.DatetimeIndex(daily_idukki.index).strftime("%Y-%m-%d")
    other_hydro_daily = daily_total_hydro - daily_idukki.reindex(
        daily_total_hydro.index
    )
    if other_hydro_daily.isna().any():
        raise ValueError("v1.3 Idukki generation does not align with base hydro")
    if (other_hydro_daily < -1e-6).any():
        raise ValueError("v1.3 Idukki generation exceeds total hydro on a model day")
    other_hydro_daily = other_hydro_daily.clip(lower=0.0)

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
    installed_hydro_mw = float(
        observed["electricity"]["capacity_mix_mw"]["hydel"]
    )
    other_hydro_power_mw = float(suite["other_hydro"]["installed_power_mw"])
    if abs((other_hydro_power_mw + 780.0) - installed_hydro_mw) > 1e-6:
        raise ValueError("v1.3 hydro capacity split no longer reconciles")

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
            for availability in suite["idukki_availability_cases"]:
                idukki_power_mw = float(availability["powerhouse_mw"])
                aggregate_available_mw = other_hydro_power_mw + idukki_power_mw

                physical = solve_idukki_reservoir_case(
                    residual_after_nonhydro_mw=residual,
                    snapshots=snapshots,
                    other_hydro_daily_mwh=other_hydro_daily,
                    other_hydro_power_mw=other_hydro_power_mw,
                    idukki_power_mw=idukki_power_mw,
                    idukki_full_storage_mcm=float(source["full_storage_mcm"]),
                    idukki_initial_storage_mcm=float(
                        source["initial_storage_mcm"]
                    ),
                    idukki_terminal_storage_mcm=float(
                        source["terminal_storage_mcm"]
                    ),
                    idukki_energy_equivalent_mwh_per_mcm=float(
                        source["energy_equivalent_mwh_per_mcm"]
                    ),
                    idukki_net_water_balance_mcm_day=source[
                        "net_water_balance_mcm_day"
                    ],
                    solar_profile=solar_full[:hours],
                    wind_profile=wind_full[:hours],
                    import_limit_mw=float(transfer["import_limit_mw"]),
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

                baselines: dict[str, Any] = {}
                for window_days in suite["comparison"][
                    "same_horizon_v1_2_windows_days"
                ]:
                    solved = solve_hydro_interday_case(
                        residual_after_nonhydro_mw=residual,
                        snapshots=snapshots,
                        daily_hydro_mwh=daily_total_hydro,
                        window_days=int(window_days),
                        solar_profile=solar_full[:hours],
                        wind_profile=wind_full[:hours],
                        installed_hydro_mw=installed_hydro_mw,
                        available_hydro_mw=aggregate_available_mw,
                        import_limit_mw=float(transfer["import_limit_mw"]),
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
                    baselines[f"window_{int(window_days)}d"] = solved

                cases.append(
                    {
                        "demand_case": demand_id,
                        "transfer_case": transfer_id,
                        "import_limit_mw": float(transfer["import_limit_mw"]),
                        "idukki_availability_case": availability["id"],
                        "idukki_power_mw": idukki_power_mw,
                        "aggregate_hydro_available_mw": aggregate_available_mw,
                        "physical_stateful": physical,
                        "v1_2_same_horizon": baselines,
                        "comparison": {
                            "unserved_delta_vs_1d_mwh": (
                                physical["stage2_unserved_mwh"]
                                - baselines["window_1d"]["stage2_unserved_mwh"]
                            ),
                            "unserved_delta_vs_30d_mwh": (
                                physical["stage2_unserved_mwh"]
                                - baselines["window_30d"]["stage2_unserved_mwh"]
                            ),
                        },
                    }
                )

    return {
        "classification": SUITE_CLASS,
        "prepared_date": suite["prepared_date"],
        "pilot_hours": hours,
        "pilot_days": hours // 24,
        "cases_solved": len(cases),
        "comparison_solves": len(cases)
        * len(suite["comparison"]["same_horizon_v1_2_windows_days"]),
        "source_qa": {
            "observed_storage_days": source["observed_storage_days"],
            "interpolated_storage_days": source["interpolated_storage_days"],
            "observed_generation_days": source["observed_generation_days"],
            "interpolated_generation_days": source[
                "interpolated_generation_days"
            ],
            "derived_energy_equivalent_mwh_per_mcm": source[
                "derived_energy_equivalent_mwh_per_mcm"
            ],
            "historical_replay_terminal_residual_mcm": source[
                "historical_replay_terminal_residual_mcm"
            ],
            "initial_storage_mcm": source["initial_storage_mcm"],
            "terminal_storage_mcm": source["terminal_storage_mcm"],
            "net_water_balance_min_mcm_day": float(
                source["net_water_balance_mcm_day"].min()
            ),
            "net_water_balance_max_mcm_day": float(
                source["net_water_balance_mcm_day"].max()
            ),
            "net_water_balance_sum_mcm": float(
                source["net_water_balance_mcm_day"].sum()
            ),
        },
        "profile_alignment": alignment,
        "interpretation": {
            "stateful_idukki": True,
            "net_water_balance_is_catchment_inflow": False,
            "head_dependent_efficiency": False,
            "observed_spill_release": False,
            "validated_reservoir_operation": False,
        },
        "cases": cases,
    }
