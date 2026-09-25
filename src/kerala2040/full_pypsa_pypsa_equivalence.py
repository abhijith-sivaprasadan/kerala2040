"""Direct PyPSA equivalence check for Full-PyPSA proxy expansion v0.9."""
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
from kerala2040.full_pypsa_proxy_expansion import (
    _align_profiles,
    _annualized_costs,
    _candidate_caps,
    _solar_allocation_range,
    load_proxy_expansion_suite,
    run_proxy_expansion_suite,
)
from kerala2040.full_pypsa_renewable_capacity import load_capacity_envelope

SUITE_CLASS = "full_pypsa_v0_9_direct_pypsa_equivalence_to_v0_8_proxy_expansion"


def load_pypsa_equivalence_suite(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if data.get("classification") != SUITE_CLASS:
        raise ValueError("v0.9 PyPSA equivalence classification mismatch")
    if data["solver"]["engine"] != "PyPSA_Network_optimize":
        raise ValueError("v0.9 must use the direct PyPSA optimization stack")
    release = data["release"]
    if release["direct_pypsa_equivalence_checkpoint"] is not True:
        raise ValueError("v0.9 equivalence checkpoint not released")
    for key in (
        "v0_8_reference_replaced",
        "full_economic_capacity_expansion_ready",
        "validated_capacity_plan",
        "scenario_recommendation",
    ):
        if release[key] is not False:
            raise ValueError(f"v0.9 incorrectly enables {key}")
    return data


def _build_pypsa_network(
    residual_load_mw: np.ndarray,
    solar_profile: np.ndarray,
    wind_profile: np.ndarray,
    *,
    import_limit_mw: float,
    caps: dict[str, float],
    annualized_costs: dict[str, float],
    bess_duration_h: float,
    charge_efficiency: float,
    discharge_efficiency: float,
):
    import pypsa

    residual = np.asarray(residual_load_mw, dtype=float)
    solar = np.asarray(solar_profile, dtype=float)
    wind = np.asarray(wind_profile, dtype=float)
    if len(residual) == 0 or len(solar) != len(residual) or len(wind) != len(residual):
        raise ValueError("v0.9 PyPSA inputs have inconsistent chronology")
    if not np.isfinite(residual).all() or not np.isfinite(solar).all() or not np.isfinite(wind).all():
        raise ValueError("v0.9 PyPSA inputs must be finite")
    if (solar < 0).any() or (solar > 1).any() or (wind < 0).any() or (wind > 1).any():
        raise ValueError("v0.9 renewable profiles must stay in [0,1]")
    if import_limit_mw <= 0:
        raise ValueError("v0.9 import limit must be positive")

    snapshots = pd.RangeIndex(len(residual), name="snapshot")
    network = pypsa.Network()
    network.set_snapshots(snapshots)
    network.snapshot_weightings.loc[:, :] = 1.0
    network.add("Bus", "kerala")
    network.add("Load", "residual_demand", bus="kerala", p_set=residual)

    network.add(
        "Generator",
        "candidate_solar",
        bus="kerala",
        p_nom_extendable=True,
        p_nom_min=0.0,
        p_nom_max=float(caps["solar_total_headroom_mw"]),
        p_max_pu=solar,
        capital_cost=float(annualized_costs["solar_million_inr_per_mw_year"]),
        marginal_cost=0.0,
    )
    network.add(
        "Generator",
        "candidate_wind",
        bus="kerala",
        p_nom_extendable=True,
        p_nom_min=0.0,
        p_nom_max=float(caps["wind_headroom_mw"]),
        p_max_pu=wind,
        capital_cost=float(annualized_costs["wind_million_inr_per_mw_year"]),
        marginal_cost=0.0,
    )
    network.add(
        "Generator",
        "screened_import",
        bus="kerala",
        p_nom=float(import_limit_mw),
        marginal_cost=0.0,
    )
    unserved_cap = max(float(np.maximum(residual, 0.0).max()), 1.0)
    network.add(
        "Generator",
        "unserved_load",
        bus="kerala",
        p_nom=unserved_cap,
        marginal_cost=0.0,
    )
    network.add(
        "StorageUnit",
        "candidate_bess",
        bus="kerala",
        p_nom_extendable=True,
        p_nom_min=0.0,
        p_nom_max=float(caps["bess_power_headroom_mw"]),
        max_hours=float(bess_duration_h),
        efficiency_store=float(charge_efficiency),
        efficiency_dispatch=float(discharge_efficiency),
        cyclic_state_of_charge=True,
        capital_cost=float(annualized_costs["bess_million_inr_per_mw_year"]),
        marginal_cost=0.0,
    )
    return network


def _solution_scalar(variable, *, name: str) -> float:
    value = variable.solution.sel(name=name)
    return float(np.asarray(value).item())


def _solution_series(variable, *, name: str) -> np.ndarray:
    value = variable.solution.sel(name=name)
    return np.asarray(value, dtype=float)


def solve_pypsa_equivalence_case(
    *,
    residual_load_mw: np.ndarray,
    solar_profile: np.ndarray,
    wind_profile: np.ndarray,
    import_limit_mw: float,
    caps: dict[str, float],
    annualized_costs: dict[str, float],
    bess_duration_h: float,
    charge_efficiency: float,
    discharge_efficiency: float,
    unserved_tolerance_mwh: float,
) -> dict[str, Any]:
    network = _build_pypsa_network(
        residual_load_mw,
        solar_profile,
        wind_profile,
        import_limit_mw=import_limit_mw,
        caps=caps,
        annualized_costs=annualized_costs,
        bess_duration_h=bess_duration_h,
        charge_efficiency=charge_efficiency,
        discharge_efficiency=discharge_efficiency,
    )
    model = network.optimize.create_model()

    gen_p = model.variables["Generator-p"]
    gen_nom = model.variables["Generator-p_nom"]
    storage_nom = model.variables["StorageUnit-p_nom"]
    unserved = gen_p.sel(name="unserved_load")
    imports = gen_p.sel(name="screened_import")

    model.add_objective(unserved.sum(), overwrite=True)
    status1, condition1 = network.optimize.solve_model(solver_name="highs")
    if status1 != "ok" or condition1 != "optimal":
        raise RuntimeError(f"v0.9 PyPSA stage 1 failed: {status1} / {condition1}")
    minimum_unserved = float(np.asarray(unserved.solution).sum())

    model.add_constraints(
        unserved.sum() <= minimum_unserved + float(unserved_tolerance_mwh),
        name="v09-minimum-shortage-cap",
    )
    solar_nom = gen_nom.sel(name="candidate_solar")
    wind_nom = gen_nom.sel(name="candidate_wind")
    bess_nom = storage_nom.sel(name="candidate_bess")
    investment_objective = (
        solar_nom * float(annualized_costs["solar_million_inr_per_mw_year"])
        + wind_nom * float(annualized_costs["wind_million_inr_per_mw_year"])
        + bess_nom * float(annualized_costs["bess_million_inr_per_mw_year"])
    )
    model.add_objective(investment_objective, overwrite=True)
    status2, condition2 = network.optimize.solve_model(solver_name="highs")
    if status2 != "ok" or condition2 != "optimal":
        raise RuntimeError(f"v0.9 PyPSA stage 2 failed: {status2} / {condition2}")

    stage2_solar = _solution_scalar(gen_nom, name="candidate_solar")
    stage2_wind = _solution_scalar(gen_nom, name="candidate_wind")
    stage2_bess = _solution_scalar(storage_nom, name="candidate_bess")
    stage2_unserved = float(np.asarray(unserved.solution).sum())
    annualized_investment = (
        stage2_solar * float(annualized_costs["solar_million_inr_per_mw_year"])
        + stage2_wind * float(annualized_costs["wind_million_inr_per_mw_year"])
        + stage2_bess * float(annualized_costs["bess_million_inr_per_mw_year"])
    )

    model.add_constraints(solar_nom == stage2_solar, name="v09-fix-solar-capacity")
    model.add_constraints(wind_nom == stage2_wind, name="v09-fix-wind-capacity")
    model.add_constraints(bess_nom == stage2_bess, name="v09-fix-bess-capacity")
    model.add_objective(imports.sum(), overwrite=True)
    status3, condition3 = network.optimize.solve_model(solver_name="highs")
    if status3 != "ok" or condition3 != "optimal":
        raise RuntimeError(f"v0.9 PyPSA stage 3 failed: {status3} / {condition3}")

    stage3_unserved = float(np.asarray(unserved.solution).sum())
    stage3_imports = float(np.asarray(imports.solution).sum())
    solar_dispatch = _solution_series(gen_p, name="candidate_solar")
    wind_dispatch = _solution_series(gen_p, name="candidate_wind")
    unserved_dispatch = _solution_series(gen_p, name="unserved_load")
    import_dispatch = _solution_series(gen_p, name="screened_import")

    return {
        "stage1_minimum_unserved_mwh": minimum_unserved,
        "stage2_unserved_mwh": stage2_unserved,
        "stage3_reporting_unserved_mwh": stage3_unserved,
        "annualized_candidate_investment_million_inr_per_year": annualized_investment,
        "stage3_minimum_imports_mwh": stage3_imports,
        "built": {
            "solar_combined_mw": stage2_solar,
            "wind_onshore_mw": stage2_wind,
            "bess_4h_power_mw": stage2_bess,
            "bess_4h_energy_mwh": stage2_bess * float(bess_duration_h),
            "solar_subtype_allocation_range": _solar_allocation_range(stage2_solar, caps),
        },
        "dispatch": {
            "solar_generation_mwh": float(solar_dispatch.sum()),
            "wind_generation_mwh": float(wind_dispatch.sum()),
            "imports_mwh": stage3_imports,
            "peak_import_mw": float(import_dispatch.max()),
            "hours_with_unserved": int((unserved_dispatch > 1e-6).sum()),
            "max_unserved_mw": float(unserved_dispatch.max()),
        },
        "solver": {
            "engine": "PyPSA/Linopy",
            "backend": "HiGHS",
            "stage1": [status1, condition1],
            "stage2": [status2, condition2],
            "stage3": [status3, condition3],
        },
    }


def _compare_case(
    reference: dict[str, Any],
    pypsa_case: dict[str, Any],
    tolerances: dict[str, float],
) -> dict[str, Any]:
    checks: dict[str, dict[str, float | bool]] = {}

    def check(key: str, a: float, b: float, tolerance_key: str) -> None:
        tolerance = float(tolerances[tolerance_key])
        diff = abs(float(a) - float(b))
        checks[key] = {
            "reference": float(a),
            "pypsa": float(b),
            "abs_difference": diff,
            "tolerance": tolerance,
            "passed": diff <= tolerance,
        }

    check(
        "stage1_minimum_unserved_mwh",
        reference["stage1_minimum_unserved_mwh"],
        pypsa_case["stage1_minimum_unserved_mwh"],
        "stage1_unserved_mwh_abs",
    )
    check(
        "stage2_unserved_mwh",
        reference["stage2_unserved_mwh"],
        pypsa_case["stage2_unserved_mwh"],
        "stage2_unserved_mwh_abs",
    )
    check(
        "stage3_reporting_unserved_mwh",
        reference["stage3_reporting_unserved_mwh"],
        pypsa_case["stage3_reporting_unserved_mwh"],
        "stage3_unserved_mwh_abs",
    )
    for technology, key in (
        ("solar_combined_mw", "solar_combined_mw"),
        ("wind_onshore_mw", "wind_onshore_mw"),
        ("bess_4h_power_mw", "bess_4h_power_mw"),
    ):
        check(
            f"built.{technology}",
            reference["built"][key],
            pypsa_case["built"][key],
            "candidate_capacity_mw_abs",
        )
    check(
        "annualized_candidate_investment_million_inr_per_year",
        reference["annualized_candidate_investment_million_inr_per_year"],
        pypsa_case["annualized_candidate_investment_million_inr_per_year"],
        "annualized_investment_million_inr_per_year_abs",
    )
    check(
        "stage3_minimum_imports_mwh",
        reference["stage3_minimum_imports_mwh"],
        pypsa_case["stage3_minimum_imports_mwh"],
        "stage3_imports_mwh_abs",
    )
    return {
        "passed": all(bool(item["passed"]) for item in checks.values()),
        "checks": checks,
    }


def run_pypsa_equivalence_suite(
    root: Path,
    *,
    profile_path: Path,
    hours: int = 8760,
) -> dict[str, Any]:
    if not 24 <= hours <= 8760 or hours % 24:
        raise ValueError("hours must be whole days between 24 and 8760")

    suite = load_pypsa_equivalence_suite(
        root / "configs/full_pypsa_pypsa_equivalence_v0_9.yaml"
    )
    reference_suite = load_proxy_expansion_suite(
        root / "configs/full_pypsa_proxy_expansion_v0_8.yaml"
    )
    future = load_future_adequacy_suite(
        root / "configs/full_pypsa_future_adequacy_v0_4.yaml"
    )
    capacity = load_capacity_envelope(
        root / "configs/full_pypsa_renewable_capacity_v0_7.yaml"
    )
    if not capacity["release"]["statewide_2030_proxy_capacity_expansion_candidate_limits_ready"]:
        raise ValueError("v0.7 candidate limits are no longer released")

    scipy_reference = run_proxy_expansion_suite(
        root,
        profile_path=profile_path,
        hours=hours,
    )
    reference_lookup = {
        (
            case["demand_case"],
            case["transfer_case"],
            case["capacity_envelope_case"],
            case["bess_cost_case"],
        ): case
        for case in scipy_reference["cases"]
    }

    hourly_base, _, _ = _load_base(root, future)
    solar_full, wind_full, alignment = _align_profiles(
        profile_path,
        hourly_base["snapshot_ist_naive"],
    )
    cost_data = load_cost_finance_suite(
        root / "configs/full_pypsa_cost_finance_v0_5.yaml"
    )
    bess = cost_data["research_2030"]["bess_4h"]
    duration = float(bess["duration_hours"])
    eta_c = float(bess["charge_efficiency_symmetric"])
    eta_d = float(bess["discharge_efficiency_symmetric"])

    demand_lookup = {item["id"]: item for item in future["demand_cases"]}
    transfer_lookup = {item["id"]: item for item in future["transfer_cases"]}
    tolerances = suite["comparison"]["tolerances"]
    comparisons: list[dict[str, Any]] = []

    for demand_id in reference_suite["demand_cases"]:
        demand = demand_lookup[demand_id]
        morphed, _ = morph_load_to_energy_and_peak(
            hourly_base["load_mw"],
            annual_energy_mu=float(demand["annual_energy_mu"]),
            peak_mw=float(demand["peak_mw"]),
        )
        residual = (
            morphed.to_numpy(dtype=float)
            - hourly_base["hydro_fixed_mw"].to_numpy(dtype=float)
            - hourly_base["nonhydro_fixed_mw"].to_numpy(dtype=float)
        )[:hours]
        solar = solar_full[:hours]
        wind = wind_full[:hours]

        for transfer_id in reference_suite["transfer_cases"]:
            transfer = transfer_lookup[transfer_id]
            for envelope_case in reference_suite["capacity_envelope_cases"]:
                caps = _candidate_caps(root, envelope_case, reference_suite)
                for bess_cost_case in reference_suite["bess_cost_cases"]:
                    costs = _annualized_costs(root, bess_cost_case)
                    pypsa_case = solve_pypsa_equivalence_case(
                        residual_load_mw=residual,
                        solar_profile=solar,
                        wind_profile=wind,
                        import_limit_mw=float(transfer["import_limit_mw"]),
                        caps=caps,
                        annualized_costs=costs,
                        bess_duration_h=duration,
                        charge_efficiency=eta_c,
                        discharge_efficiency=eta_d,
                        unserved_tolerance_mwh=float(
                            reference_suite["objective"]["unserved_tolerance_mwh"]
                        ),
                    )
                    key = (
                        demand_id,
                        transfer_id,
                        envelope_case,
                        bess_cost_case,
                    )
                    reference = reference_lookup[key]
                    comparison = _compare_case(reference, pypsa_case, tolerances)
                    comparisons.append(
                        {
                            "demand_case": demand_id,
                            "transfer_case": transfer_id,
                            "capacity_envelope_case": envelope_case,
                            "bess_cost_case": bess_cost_case,
                            "reference": reference,
                            "pypsa": pypsa_case,
                            "comparison": comparison,
                        }
                    )

    expected = len(reference_suite["demand_cases"]) * len(
        reference_suite["transfer_cases"]
    ) * len(reference_suite["capacity_envelope_cases"]) * len(
        reference_suite["bess_cost_cases"]
    )
    if len(comparisons) != expected:
        raise RuntimeError("v0.9 did not compare the complete v0.8 case matrix")
    failed = [case for case in comparisons if not case["comparison"]["passed"]]
    if failed:
        first = failed[0]
        raise RuntimeError(
            "v0.9 direct PyPSA equivalence failed for "
            f"{first['demand_case']} / {first['transfer_case']} / "
            f"{first['capacity_envelope_case']} / {first['bess_cost_case']}"
        )

    maxima: dict[str, float] = {}
    for case in comparisons:
        for key, item in case["comparison"]["checks"].items():
            maxima[key] = max(maxima.get(key, 0.0), float(item["abs_difference"]))

    return {
        "classification": SUITE_CLASS,
        "prepared_date": suite["prepared_date"],
        "hours": hours,
        "full_financial_year": hours == 8760,
        "cases_compared": len(comparisons),
        "all_cases_passed": not failed,
        "maximum_absolute_differences": maxima,
        "tolerances": tolerances,
        "renewable_profile_alignment": alignment,
        "comparisons": comparisons,
        "interpretation": [
            (
                "v0.9 rebuilds v0.8 through direct PyPSA Network/Linopy optimization "
                "with HiGHS rather than scipy.optimize.linprog."
            ),
            (
                "Equivalence is numerical formulation QA only; it does not resolve "
                "the economic, hydro, outage, siting or grid-hosting blockers."
            ),
        ],
    }
