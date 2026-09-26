"""Full-PyPSA execution layer for the Idukki v1.4b inflow sensitivity.

This runner consumes private v1.4b daily inflow scenarios and solves the same
three-stage stateful Idukki model used by strict v1.4. It never upgrades the
source-informed series to observed inflow.
"""
from __future__ import annotations

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
from kerala2040.full_pypsa_idukki_inflow_release_v1_4 import (
    solve_idukki_reported_inflow_case,
)
from kerala2040.full_pypsa_idukki_reservoir_v1_3 import (
    load_idukki_reservoir_v13_suite,
    load_idukki_water_balance_inputs,
)
from kerala2040.full_pypsa_import_economics import load_import_economics_suite
from kerala2040.full_pypsa_proxy_expansion import (
    _align_profiles,
    _annualized_costs,
    _candidate_caps,
    load_proxy_expansion_suite,
)
from kerala2040.idukki_cumulative_inflow_v1_4b import (
    build_source_informed_inflow_scenarios,
    load_v14b_suite,
)

RUNNER_CLASS = (
    "full_pypsa_idukki_v1_4b_sensitivity_runner_"
    "source_informed_not_observed_inflow"
)


def load_v14b_runner_suite(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if data.get("classification") != RUNNER_CLASS:
        raise ValueError("v1.4b sensitivity runner classification mismatch")

    matrix = data["matrix"]
    expected = (
        len(matrix["inflow_scenarios"])
        * len(matrix["demand_cases"])
        * len(matrix["transfer_cases"])
        * len(matrix["idukki_availability_cases"])
    )
    if expected != int(matrix["expected_cases"]) or expected != 60:
        raise ValueError("v1.4b runner matrix changed unexpectedly")

    release = data["release"]
    if release["runner_code_ready"] is not True:
        raise ValueError("v1.4b runner code-ready flag is false")
    if release["real_60_case_matrix_executed"] is not False:
        raise ValueError("public config must not claim the real private matrix ran")
    if release["strict_v1_4_source_reported_model_ready"] is not False:
        raise ValueError("v1.4b runner must not promote strict v1.4")
    return data


def load_private_inflow_scenario(
    path: Path,
    *,
    expected_days: pd.DatetimeIndex,
) -> pd.Series:
    frame = pd.read_csv(path, parse_dates=["date"])
    required = {"date", "inflow_mcm_day", "input_class"}
    missing = sorted(required - set(frame.columns))
    if missing:
        raise ValueError(f"v1.4b private scenario missing columns: {missing}")
    if frame["date"].duplicated().any():
        raise ValueError("v1.4b private scenario contains duplicate dates")

    values = pd.to_numeric(frame["inflow_mcm_day"], errors="coerce")
    series = pd.Series(values.to_numpy(dtype=float), index=frame["date"])
    series = series.reindex(expected_days)
    if series.isna().any():
        raise ValueError("v1.4b private scenario does not cover every pilot day")
    if (series < 0).any() or (series > 300).any():
        raise ValueError("v1.4b private scenario inflow outside [0,300] MCM/day")
    return series


def summarize_sensitivity(cases: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str, str], list[dict[str, Any]]] = {}
    for case in cases:
        key = (
            case["demand_case"],
            case["transfer_case"],
            case["idukki_availability_case"],
        )
        grouped.setdefault(key, []).append(case)

    summary: list[dict[str, Any]] = []
    for key, rows in grouped.items():
        if len(rows) != 5:
            raise ValueError(
                f"v1.4b expected five inflow scenarios for system case {key}"
            )
        shortage = np.asarray(
            [row["physical"]["stage3_unserved_mwh"] for row in rows],
            dtype=float,
        )
        release = np.asarray(
            [row["physical"]["idukki_non_turbine_release_mcm"] for row in rows],
            dtype=float,
        )
        generation = np.asarray(
            [row["physical"]["idukki_generation_mwh"] for row in rows],
            dtype=float,
        )
        solar = np.asarray(
            [row["physical"]["built"]["solar_combined_mw"] for row in rows],
            dtype=float,
        )
        wind = np.asarray(
            [row["physical"]["built"]["wind_onshore_mw"] for row in rows],
            dtype=float,
        )
        bess = np.asarray(
            [row["physical"]["built"]["bess_4h_power_mw"] for row in rows],
            dtype=float,
        )
        summary.append({
            "demand_case": key[0],
            "transfer_case": key[1],
            "idukki_availability_case": key[2],
            "inflow_scenarios": sorted(row["inflow_scenario"] for row in rows),
            "unserved_mwh_min": float(shortage.min()),
            "unserved_mwh_max": float(shortage.max()),
            "unserved_mwh_range": float(shortage.max() - shortage.min()),
            "idukki_generation_mwh_range": float(
                generation.max() - generation.min()
            ),
            "idukki_non_turbine_release_mcm_range": float(
                release.max() - release.min()
            ),
            "solar_mw_range": float(solar.max() - solar.min()),
            "wind_mw_range": float(wind.max() - wind.min()),
            "bess_power_mw_range": float(bess.max() - bess.min()),
        })
    return sorted(
        summary,
        key=lambda row: (
            row["demand_case"],
            row["transfer_case"],
            row["idukki_availability_case"],
        ),
    )


def run_v14b_sensitivity_suite(
    root: Path,
    *,
    private_reservoir_rows: Path,
    private_work_dir: Path,
    profile_path: Path,
) -> dict[str, Any]:
    runner = load_v14b_runner_suite(
        root / "configs/full_pypsa_idukki_v1_4b_sensitivity_runner.yaml"
    )
    inflow_suite = load_v14b_suite(
        root / runner["inherits"]["cumulative_inflow"]
    )
    stateful_suite = load_idukki_reservoir_v13_suite(
        root / runner["inherits"]["stateful_reservoir"]
    )

    input_qa = build_source_informed_inflow_scenarios(
        private_reservoir_rows,
        inflow_suite,
        private_output_dir=private_work_dir,
    )
    expected_scenarios = list(runner["matrix"]["inflow_scenarios"])
    if list(input_qa["scenarios"]) != expected_scenarios:
        raise ValueError("v1.4b generated scenario order/set changed")

    source_boundary = load_idukki_water_balance_inputs(root, stateful_suite)
    hours = int(stateful_suite["pilot_period"]["hours"])
    snapshots_days = pd.DatetimeIndex(source_boundary["dispatch_days"])
    scenario_series = {
        scenario_id: load_private_inflow_scenario(
            private_work_dir / f"{scenario_id}.csv",
            expected_days=snapshots_days,
        )
        for scenario_id in expected_scenarios
    }

    import_suite = load_import_economics_suite(
        root / stateful_suite["inherits"]["import_economics"]
    )
    proxy = load_proxy_expansion_suite(
        root / stateful_suite["inherits"]["proxy_expansion"]
    )
    future = load_future_adequacy_suite(
        root / stateful_suite["inherits"]["future_demand"]
    )
    hourly_base, _, observed = _load_base(root, future)
    daily_total_hydro = _daily_targets(hourly_base, hours)

    daily_idukki = source_boundary["generation_mwh"].copy()
    daily_idukki.index = pd.DatetimeIndex(daily_idukki.index).strftime("%Y-%m-%d")
    other_hydro_daily = daily_total_hydro - daily_idukki.reindex(
        daily_total_hydro.index
    )
    if other_hydro_daily.isna().any() or (other_hydro_daily < -1e-6).any():
        raise ValueError("v1.4b cannot reconcile Idukki and total daily hydro")
    other_hydro_daily = other_hydro_daily.clip(lower=0.0)

    solar_full, wind_full, alignment = _align_profiles(
        profile_path,
        hourly_base["snapshot_ist_naive"],
    )
    cost_data = load_cost_finance_suite(
        root / stateful_suite["inherits"]["cost_finance"]
    )
    bess = cost_data["research_2030"]["bess_4h"]
    focus = stateful_suite["focus_case"]
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
    availability_lookup = {
        item["id"]: item for item in stateful_suite["idukki_availability_cases"]
    }

    snapshots = pd.DatetimeIndex(
        hourly_base["snapshot_ist_naive"].iloc[:hours].to_numpy(),
        name="snapshot",
    )
    installed_hydro_mw = float(
        observed["electricity"]["capacity_mix_mw"]["hydel"]
    )
    other_hydro_power_mw = float(stateful_suite["other_hydro"]["installed_power_mw"])
    if abs((other_hydro_power_mw + 780.0) - installed_hydro_mw) > 1e-6:
        raise ValueError("v1.4b hydro capacity split no longer reconciles")

    cases: list[dict[str, Any]] = []
    for demand_id in runner["matrix"]["demand_cases"]:
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

        for transfer_id in runner["matrix"]["transfer_cases"]:
            transfer = transfer_lookup[transfer_id]
            for availability_id in runner["matrix"]["idukki_availability_cases"]:
                availability = availability_lookup[availability_id]
                for scenario_id in expected_scenarios:
                    physical = solve_idukki_reported_inflow_case(
                        residual_after_nonhydro_mw=residual,
                        snapshots=snapshots,
                        other_hydro_daily_mwh=other_hydro_daily,
                        other_hydro_power_mw=other_hydro_power_mw,
                        idukki_power_mw=float(availability["powerhouse_mw"]),
                        idukki_full_storage_mcm=float(
                            source_boundary["full_storage_mcm"]
                        ),
                        idukki_initial_storage_mcm=float(
                            source_boundary["initial_storage_mcm"]
                        ),
                        idukki_terminal_storage_mcm=float(
                            source_boundary["terminal_storage_mcm"]
                        ),
                        idukki_energy_equivalent_mwh_per_mcm=float(
                            source_boundary["energy_equivalent_mwh_per_mcm"]
                        ),
                        reported_inflow_mcm_day=scenario_series[scenario_id],
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
                    cases.append({
                        "inflow_scenario": scenario_id,
                        "inflow_input": input_qa["scenarios"][scenario_id],
                        "demand_case": demand_id,
                        "transfer_case": transfer_id,
                        "idukki_availability_case": availability_id,
                        "idukki_power_mw": float(availability["powerhouse_mw"]),
                        "physical": physical,
                    })

    expected_cases = int(runner["matrix"]["expected_cases"])
    if len(cases) != expected_cases:
        raise RuntimeError(
            f"v1.4b solved {len(cases)} cases, expected {expected_cases}"
        )

    return {
        "classification": RUNNER_CLASS,
        "prepared_date": runner["prepared_date"],
        "cases_solved": len(cases),
        "private_source_sha256": input_qa["private_source_sha256"],
        "input_qa": input_qa,
        "profile_alignment": alignment,
        "sensitivity_summary": summarize_sensitivity(cases),
        "interpretation": {
            "strict_v1_4_source_reported_series_complete": False,
            "source_informed_sensitivity_only": True,
            "non_turbine_release_is_observed_spill": False,
            "head_dependent_efficiency": False,
            "validated_reservoir_operation": False,
            "validated_capacity_plan": False,
        },
        "cases": cases,
    }
