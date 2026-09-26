"""Source-reported Idukki inflow and explicit release gate for v1.4.

The public repository does not redistribute the private SLDC reservoir_rows.csv.
A physical v1.4 run therefore requires the exact source-hashed private file used
by the Phase 4 audit. Missing pilot-day inflow is never interpolated.
"""
from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import yaml

from kerala2040.full_pypsa_cost_finance import load_cost_finance_suite
from kerala2040.full_pypsa_future_adequacy import (
    _load_base,
    load_future_adequacy_suite,
    morph_load_to_energy_and_peak,
)
from kerala2040.full_pypsa_hydro_flex_v1_1 import _daily_targets
from kerala2040.full_pypsa_idukki_reservoir_v1_3 import (
    _add_other_hydro_daily_constraints,
    _build_idukki_network,
    load_idukki_reservoir_v13_suite,
    load_idukki_water_balance_inputs,
)
from kerala2040.full_pypsa_import_economics import load_import_economics_suite
from kerala2040.full_pypsa_proxy_expansion import (
    _align_profiles,
    _annualized_costs,
    _candidate_caps,
    _solar_allocation_range,
    load_proxy_expansion_suite,
)

SUITE_CLASS = "full_pypsa_idukki_inflow_release_v1_4_source_reported_inflow_gate"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_idukki_inflow_v14_suite(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if data.get("classification") != SUITE_CLASS:
        raise ValueError("v1.4 Idukki inflow classification mismatch")

    source = data["private_source"]
    expected = (
        "b7d4439135edbe02d9e577892e090aafaf92f58606cdc04ee9b6d39e608036c9"
    )
    if source["expected_sha256"] != expected:
        raise ValueError("v1.4 private SLDC source hash changed")
    if int(data["pilot_period"]["required_inflow_days"]) != 364:
        raise ValueError("v1.4 pilot inflow-day requirement changed")
    if data["pilot_period"]["missing_inflow_policy"] != (
        "fail_closed_no_interpolation"
    ):
        raise ValueError("v1.4 must not interpolate missing reported inflow")

    release = data["release"]
    for key in (
        "v1_3_stateful_reservoir_verified",
        "source_reported_inflow_ingestion_code_ready",
        "explicit_non_turbine_release_variable_ready",
    ):
        if release[key] is not True:
            raise ValueError(f"v1.4 expected release flag is false: {key}")
    if release["source_reported_inflow_model_run_ready"] is not False:
        raise ValueError("v1.4 must remain blocked before private-source execution")
    for key in (
        "observed_spill_chronology_ready",
        "environmental_release_constraint_ready",
        "head_dependent_efficiency_ready",
        "cascade_model_ready",
        "full_reservoir_model_validated",
        "validated_capacity_plan",
        "scenario_recommendation",
    ):
        if release[key] is not False:
            raise ValueError(f"v1.4 incorrectly enables {key}")
    return data


def validate_private_inflow_rows(
    path: Path,
    *,
    expected_sha256: str,
    start: str,
    dispatch_end: str,
    required_columns: list[str],
) -> dict[str, Any]:
    actual_sha = sha256(path)
    if actual_sha != expected_sha256:
        raise ValueError(
            "Private reservoir_rows.csv SHA-256 does not match the Phase 4 "
            f"audited source: {actual_sha}"
        )

    frame = pd.read_csv(path, parse_dates=["date"], low_memory=False)
    missing_columns = sorted(set(required_columns) - set(frame.columns))
    if missing_columns:
        raise ValueError(
            f"Private reservoir_rows.csv missing columns: {missing_columns}"
        )

    idukki = frame.loc[
        frame["reservoir"].astype(str).str.upper().eq("IDUKKI")
    ].copy()
    if idukki["date"].duplicated().any():
        raise ValueError("Private source has duplicate Idukki reservoir dates")

    days = pd.date_range(start, dispatch_end, freq="D")
    raw = pd.to_numeric(idukki.set_index("date")["inflow_mcm_day"], errors="coerce")
    inflow = raw.reindex(days)
    valid = inflow.notna() & inflow.ge(0) & inflow.le(300)
    missing_days = days[~valid.to_numpy()]

    return {
        "actual_sha256": actual_sha,
        "idukki_source_rows": int(len(idukki)),
        "pilot_days_required": int(len(days)),
        "pilot_days_source_reported_valid": int(valid.sum()),
        "missing_or_invalid_pilot_dates": [
            day.strftime("%Y-%m-%d") for day in missing_days
        ],
        "complete_for_physical_run": bool(valid.all()),
        "inflow_mcm_day": inflow.where(valid),
    }


def assess_private_inflow_gate(
    private_source: Path | None,
    suite: dict[str, Any],
) -> dict[str, Any]:
    source = suite["private_source"]
    base = {
        "classification": "V1_4_PRIVATE_INFLOW_SOURCE_GATE",
        "required_filename": source["required_filename"],
        "expected_sha256": source["expected_sha256"],
        "required_pilot_inflow_days": int(
            suite["pilot_period"]["required_inflow_days"]
        ),
        "missing_inflow_policy": suite["pilot_period"]["missing_inflow_policy"],
    }
    if private_source is None or not private_source.is_file():
        return {
            **base,
            "status": "blocked_private_source_missing",
            "physical_run_ready": False,
        }

    try:
        checked = validate_private_inflow_rows(
            private_source,
            expected_sha256=source["expected_sha256"],
            start=suite["pilot_period"]["start"],
            dispatch_end=suite["pilot_period"]["dispatch_end"],
            required_columns=list(source["required_columns"]),
        )
    except ValueError as exc:
        return {
            **base,
            "status": "blocked_private_source_rejected",
            "physical_run_ready": False,
            "reason": str(exc),
        }

    return {
        **base,
        "status": (
            "ready_source_complete"
            if checked["complete_for_physical_run"]
            else "blocked_source_inflow_gaps"
        ),
        "physical_run_ready": bool(checked["complete_for_physical_run"]),
        "actual_sha256": checked["actual_sha256"],
        "idukki_source_rows": checked["idukki_source_rows"],
        "pilot_days_source_reported_valid": checked[
            "pilot_days_source_reported_valid"
        ],
        "missing_or_invalid_pilot_dates": checked[
            "missing_or_invalid_pilot_dates"
        ],
    }


def load_reported_inflow_inputs(
    root: Path,
    suite: dict[str, Any],
    private_source: Path,
) -> dict[str, Any]:
    gate = validate_private_inflow_rows(
        private_source,
        expected_sha256=suite["private_source"]["expected_sha256"],
        start=suite["pilot_period"]["start"],
        dispatch_end=suite["pilot_period"]["dispatch_end"],
        required_columns=list(suite["private_source"]["required_columns"]),
    )
    if not gate["complete_for_physical_run"]:
        dates = gate["missing_or_invalid_pilot_dates"]
        preview = ", ".join(dates[:12])
        suffix = "..." if len(dates) > 12 else ""
        raise ValueError(
            "v1.4 refuses inflow interpolation; recover source-reported Idukki "
            f"inflow for {len(dates)} pilot dates: {preview}{suffix}"
        )

    v13_suite = load_idukki_reservoir_v13_suite(
        root / suite["inherits"]["idukki_stateful_reservoir"]
    )
    base = load_idukki_water_balance_inputs(root, v13_suite)
    dispatch_days = pd.DatetimeIndex(base["dispatch_days"])
    reported_inflow = gate["inflow_mcm_day"].reindex(dispatch_days)
    if reported_inflow.isna().any():
        raise RuntimeError("v1.4 reported inflow unexpectedly lost after source gate")

    storage = base["storage_mcm"]
    storage_now = storage.reindex(dispatch_days)
    storage_next = storage.reindex(dispatch_days + pd.Timedelta(days=1))
    storage_next.index = dispatch_days
    generation_mwh = base["generation_mwh"].reindex(dispatch_days)
    conversion = float(base["energy_equivalent_mwh_per_mcm"])

    turbine_water_mcm = generation_mwh / conversion
    historical_non_turbine_residual = (
        reported_inflow - (storage_next - storage_now) - turbine_water_mcm
    )

    return {
        **base,
        "private_source_sha256": gate["actual_sha256"],
        "reported_inflow_mcm_day": reported_inflow,
        "reported_inflow_days": int(reported_inflow.notna().sum()),
        "reported_inflow_sum_mcm": float(reported_inflow.sum()),
        "historical_non_turbine_residual_mcm_day": historical_non_turbine_residual,
        "historical_non_turbine_residual_negative_days": int(
            historical_non_turbine_residual.lt(0).sum()
        ),
        "historical_non_turbine_residual_min_mcm_day": float(
            historical_non_turbine_residual.min()
        ),
        "historical_non_turbine_residual_max_mcm_day": float(
            historical_non_turbine_residual.max()
        ),
        "historical_non_turbine_residual_sum_mcm": float(
            historical_non_turbine_residual.sum()
        ),
    }


def solve_idukki_reported_inflow_case(
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
    reported_inflow_mcm_day: pd.Series,
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
    system_cost_tolerance_million_inr: float = 1e-6,
) -> dict[str, Any]:
    if reported_inflow_mcm_day.isna().any():
        raise ValueError("v1.4 reported inflow contains missing values")
    if (reported_inflow_mcm_day < 0).any():
        raise ValueError("v1.4 reported inflow contains negative values")

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
        idukki_net_water_balance_mcm_day=reported_inflow_mcm_day,
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
        raise RuntimeError(f"v1.4 stage 1 failed: {status1} / {condition1}")
    minimum_unserved = float(
        np.asarray(
            model.variables["Generator-p"].solution.sel(name="unserved_load")
        ).sum()
    )

    model.add_constraints(
        unserved.sum() <= minimum_unserved + float(unserved_tolerance_mwh),
        name="v14-minimum-shortage-cap",
    )
    gen_nom = model.variables["Generator-p_nom"]
    storage_nom = model.variables["StorageUnit-p_nom"]
    solar_nom = gen_nom.sel(name="candidate_solar")
    wind_nom = gen_nom.sel(name="candidate_wind")
    bess_nom = storage_nom.sel(name="candidate_bess")
    imports = gen_p.sel(name="screened_import")
    import_cost = float(import_price_real_inr_per_mwh) / 1_000_000.0
    system_cost = (
        solar_nom * float(annualized_costs["solar_million_inr_per_mw_year"])
        + wind_nom * float(annualized_costs["wind_million_inr_per_mw_year"])
        + bess_nom * float(annualized_costs["bess_million_inr_per_mw_year"])
        + imports.sum() * import_cost
    )
    model.add_objective(system_cost, overwrite=True)
    status2, condition2 = n.optimize.solve_model(solver_name="highs")
    if status2 != "ok" or condition2 != "optimal":
        raise RuntimeError(f"v1.4 stage 2 failed: {status2} / {condition2}")

    solved_gen_nom = model.variables["Generator-p_nom"].solution
    solved_storage_nom = model.variables["StorageUnit-p_nom"].solution
    solved_p = model.variables["Generator-p"].solution
    minimum_system_cost = (
        float(np.asarray(solved_gen_nom.sel(name="candidate_solar")).item())
        * float(annualized_costs["solar_million_inr_per_mw_year"])
        + float(np.asarray(solved_gen_nom.sel(name="candidate_wind")).item())
        * float(annualized_costs["wind_million_inr_per_mw_year"])
        + float(np.asarray(solved_storage_nom.sel(name="candidate_bess")).item())
        * float(annualized_costs["bess_million_inr_per_mw_year"])
        + float(np.asarray(solved_p.sel(name="screened_import")).sum())
        * import_cost
    )

    model.add_constraints(
        system_cost
        <= minimum_system_cost + float(system_cost_tolerance_million_inr),
        name="v14-minimum-system-cost-cap",
    )
    release = -gen_p.sel(name="idukki_additional_water_release")
    model.add_objective(release.sum(), overwrite=True)
    status3, condition3 = n.optimize.solve_model(solver_name="highs")
    if status3 != "ok" or condition3 != "optimal":
        raise RuntimeError(f"v1.4 stage 3 failed: {status3} / {condition3}")

    solution = model.variables
    p = solution["Generator-p"].solution
    link_p = solution["Link-p"].solution
    store_e = solution["Store-e"].solution
    solved_gen_nom = solution["Generator-p_nom"].solution
    solved_storage_nom = solution["StorageUnit-p_nom"].solution

    idukki_dispatch = np.asarray(
        link_p.sel(name="idukki_turbine"),
        dtype=float,
    )
    storage_mwh = np.asarray(
        store_e.sel(name="idukki_reservoir"),
        dtype=float,
    )
    release_mwh = -np.asarray(
        p.sel(name="idukki_additional_water_release"),
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

    return {
        "stage1_minimum_unserved_mwh": minimum_unserved,
        "stage2_minimum_system_cost_million_inr": minimum_system_cost,
        "stage3_unserved_mwh": float(np.asarray(p.sel(name="unserved_load")).sum()),
        "built": {
            "solar_combined_mw": solar_mw,
            "wind_onshore_mw": wind_mw,
            "bess_4h_power_mw": bess_mw,
            "bess_4h_energy_mwh": bess_mw * float(bess_duration_h),
            "solar_subtype_allocation_range": _solar_allocation_range(solar_mw, caps),
        },
        "imports_mwh": float(np.asarray(p.sel(name="screened_import")).sum()),
        "other_hydro_generation_mwh": float(
            np.asarray(p.sel(name="other_hydro")).sum()
        ),
        "idukki_generation_mwh": float(idukki_dispatch.sum()),
        "idukki_generation_peak_mw": float(idukki_dispatch.max()),
        "idukki_storage_min_mcm": float(storage_mwh.min() / conversion),
        "idukki_storage_max_mcm": float(storage_mwh.max() / conversion),
        "idukki_storage_terminal_mcm": float(storage_mwh[-1] / conversion),
        "idukki_non_turbine_release_mcm": float(release_mwh.sum() / conversion),
        "solver": {
            "engine": "PyPSA/Linopy",
            "backend": "HiGHS",
            "stage1": [status1, condition1],
            "stage2": [status2, condition2],
            "stage3": [status3, condition3],
        },
    }


def run_idukki_inflow_v14_suite(
    root: Path,
    *,
    private_source: Path,
    profile_path: Path,
) -> dict[str, Any]:
    suite = load_idukki_inflow_v14_suite(
        root / "configs/full_pypsa_idukki_inflow_release_v1_4.yaml"
    )
    source = load_reported_inflow_inputs(root, suite, private_source)

    v13_suite = load_idukki_reservoir_v13_suite(
        root / suite["inherits"]["idukki_stateful_reservoir"]
    )
    hours = int(v13_suite["pilot_period"]["hours"])

    import_suite = load_import_economics_suite(
        root / v13_suite["inherits"]["import_economics"]
    )
    proxy = load_proxy_expansion_suite(
        root / v13_suite["inherits"]["proxy_expansion"]
    )
    future = load_future_adequacy_suite(
        root / v13_suite["inherits"]["future_demand"]
    )
    hourly_base, _, observed = _load_base(root, future)
    daily_total_hydro = _daily_targets(hourly_base, hours)

    daily_idukki = source["generation_mwh"].copy()
    daily_idukki.index = pd.DatetimeIndex(daily_idukki.index).strftime("%Y-%m-%d")
    other_hydro_daily = daily_total_hydro - daily_idukki.reindex(
        daily_total_hydro.index
    )
    if other_hydro_daily.isna().any() or (other_hydro_daily < -1e-6).any():
        raise ValueError("v1.4 cannot reconcile Idukki and total daily hydro")
    other_hydro_daily = other_hydro_daily.clip(lower=0.0)

    solar_full, wind_full, alignment = _align_profiles(
        profile_path,
        hourly_base["snapshot_ist_naive"],
    )
    cost_data = load_cost_finance_suite(
        root / v13_suite["inherits"]["cost_finance"]
    )
    bess = cost_data["research_2030"]["bess_4h"]
    focus = v13_suite["focus_case"]
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
    other_hydro_power_mw = float(v13_suite["other_hydro"]["installed_power_mw"])
    if abs((other_hydro_power_mw + 780.0) - installed_hydro_mw) > 1e-6:
        raise ValueError("v1.4 hydro capacity split no longer reconciles")

    cases: list[dict[str, Any]] = []
    for demand_id in v13_suite["demand_cases"]:
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

        for transfer_id in v13_suite["transfer_cases"]:
            transfer = transfer_lookup[transfer_id]
            for availability in v13_suite["idukki_availability_cases"]:
                physical = solve_idukki_reported_inflow_case(
                    residual_after_nonhydro_mw=residual,
                    snapshots=snapshots,
                    other_hydro_daily_mwh=other_hydro_daily,
                    other_hydro_power_mw=other_hydro_power_mw,
                    idukki_power_mw=float(availability["powerhouse_mw"]),
                    idukki_full_storage_mcm=float(source["full_storage_mcm"]),
                    idukki_initial_storage_mcm=float(source["initial_storage_mcm"]),
                    idukki_terminal_storage_mcm=float(source["terminal_storage_mcm"]),
                    idukki_energy_equivalent_mwh_per_mcm=float(
                        source["energy_equivalent_mwh_per_mcm"]
                    ),
                    reported_inflow_mcm_day=source["reported_inflow_mcm_day"],
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
                cases.append(
                    {
                        "demand_case": demand_id,
                        "transfer_case": transfer_id,
                        "idukki_availability_case": availability["id"],
                        "physical_reported_inflow": physical,
                    }
                )

    return {
        "classification": SUITE_CLASS,
        "prepared_date": suite["prepared_date"],
        "pilot_days": hours // 24,
        "cases_solved": len(cases),
        "private_source_sha256": source["private_source_sha256"],
        "source_qa": {
            "reported_inflow_days": source["reported_inflow_days"],
            "reported_inflow_sum_mcm": source["reported_inflow_sum_mcm"],
            "historical_non_turbine_residual_negative_days": source[
                "historical_non_turbine_residual_negative_days"
            ],
            "historical_non_turbine_residual_min_mcm_day": source[
                "historical_non_turbine_residual_min_mcm_day"
            ],
            "historical_non_turbine_residual_max_mcm_day": source[
                "historical_non_turbine_residual_max_mcm_day"
            ],
            "historical_non_turbine_residual_sum_mcm": source[
                "historical_non_turbine_residual_sum_mcm"
            ],
            "interpolated_storage_days_v1_3_boundary": source[
                "interpolated_storage_days"
            ],
            "interpolated_generation_days_v1_3_boundary": source[
                "interpolated_generation_days"
            ],
        },
        "profile_alignment": alignment,
        "interpretation": {
            "reported_inflow_is_source_field": True,
            "missing_reported_inflow_interpolated": False,
            "non_turbine_release_is_observed_spill": False,
            "head_dependent_efficiency": False,
            "validated_reservoir_operation": False,
        },
        "cases": cases,
    }
