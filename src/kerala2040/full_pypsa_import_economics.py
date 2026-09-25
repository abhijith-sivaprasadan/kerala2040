"""Import-economic sensitivity for the direct-PyPSA expansion programme v1.0."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
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
)
from kerala2040.full_pypsa_pypsa_equivalence import _build_pypsa_network

SUITE_CLASS = (
    "full_pypsa_import_economics_v1_0_"
    "partial_economic_expansion_not_total_system_cost"
)


def load_import_economics_suite(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if data.get("classification") != SUITE_CLASS:
        raise ValueError("v1.0 import-economics classification mismatch")
    prices = data["import_price_cases"]
    if [item["id"] for item in prices] != [
        "ksebl_weighted_purchase",
        "iex_dam_wholesale",
        "delivered_bulk_stress",
    ]:
        raise ValueError("v1.0 import-price case ordering changed")
    if any(float(item["real_2021_22_inr_per_mwh"]) <= 0 for item in prices):
        raise ValueError("v1.0 import-price cases must be positive")
    forward = data["forward_transfer_benchmarks"]
    if float(forward["current_ATC_mw"]) != 4455:
        raise ValueError("v1.0 current ATC benchmark changed")
    if forward["future_ATC_mw"] is not None:
        raise ValueError("v1.0 must not invent a future ATC")
    release = data["release"]
    if release["import_economic_sensitivity_ready"] is not True:
        raise ValueError("v1.0 import economics not released")
    for key in (
        "total_system_cost_optimization",
        "future_ATC_validated",
        "landed_import_cost_validated",
        "existing_fleet_economic_dispatch",
        "validated_capacity_plan",
        "scenario_recommendation",
    ):
        if release[key] is not False:
            raise ValueError(f"v1.0 incorrectly enables {key}")
    return data


def validate_import_evidence(root: Path, suite: dict[str, Any]) -> dict[str, Any]:
    path = root / suite["inherits"]["transfer_economics_evidence"]
    evidence = json.loads(path.read_text(encoding="utf-8"))
    deflator = evidence["price_basis"]["deflator"]
    ratio = float(deflator["fy2021_22_average"]) / float(deflator["fy2023_24_average"])
    if abs(ratio - float(deflator["nominal_2023_24_to_real_2021_22_ratio"])) > 1e-12:
        raise ValueError("v1.0 CPI deflator arithmetic mismatch")
    keys = evidence["import_price_benchmarks"]
    for item in suite["import_price_cases"]:
        source = keys[item["source_key"]]
        expected = float(source["nominal_inr_per_mwh"]) * ratio
        if abs(expected - float(item["real_2021_22_inr_per_mwh"])) > 1e-9:
            raise ValueError("v1.0 real import-price arithmetic mismatch")
    transfer = evidence["transfer_evidence"]
    if float(transfer["current_2026"]["atc_import_mw"]) != 4455:
        raise ValueError("v1.0 evidence current ATC mismatch")
    if float(transfer["planning_2029_30"]["additional_import_expected_mw"]) != 2696:
        raise ValueError("v1.0 2029-30 CEA import requirement changed")
    if float(transfer["planning_2034_35"]["additional_import_expected_mw"]) != 2020:
        raise ValueError("v1.0 2034-35 CEA import requirement changed")
    if transfer["future_atc_mw"] is not None:
        raise ValueError("source evidence must keep future ATC unresolved")
    return evidence


def solve_import_economic_case(
    *,
    residual_load_mw: np.ndarray,
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
    import_cost_million_inr_per_mwh = float(import_price_real_inr_per_mwh) / 1_000_000.0
    network.generators.at["screened_import", "marginal_cost"] = (
        import_cost_million_inr_per_mwh
    )
    model = network.optimize.create_model(include_objective_constant=False)
    gen_p = model.variables["Generator-p"]
    gen_nom = model.variables["Generator-p_nom"]
    storage_nom = model.variables["StorageUnit-p_nom"]
    unserved = gen_p.sel(name="unserved_load")

    model.add_objective(unserved.sum(), overwrite=True)
    status1, condition1 = network.optimize.solve_model(solver_name="highs")
    if status1 != "ok" or condition1 != "optimal":
        raise RuntimeError(f"v1.0 adequacy stage failed: {status1} / {condition1}")
    minimum_unserved = float(
        np.asarray(model.variables["Generator-p"].solution.sel(name="unserved_load")).sum()
    )

    model.add_constraints(
        unserved.sum() <= minimum_unserved + float(unserved_tolerance_mwh),
        name="v10-minimum-shortage-cap",
    )
    solar_nom = gen_nom.sel(name="candidate_solar")
    wind_nom = gen_nom.sel(name="candidate_wind")
    bess_nom = storage_nom.sel(name="candidate_bess")
    imports = gen_p.sel(name="screened_import")
    investment_objective = (
        solar_nom * float(annualized_costs["solar_million_inr_per_mw_year"])
        + wind_nom * float(annualized_costs["wind_million_inr_per_mw_year"])
        + bess_nom * float(annualized_costs["bess_million_inr_per_mw_year"])
    )
    model.add_objective(
        investment_objective + imports.sum() * import_cost_million_inr_per_mwh,
        overwrite=True,
    )
    status2, condition2 = network.optimize.solve_model(solver_name="highs")
    if status2 != "ok" or condition2 != "optimal":
        raise RuntimeError(f"v1.0 economic stage failed: {status2} / {condition2}")

    solution = model.variables
    stage2_unserved = float(
        np.asarray(solution["Generator-p"].solution.sel(name="unserved_load")).sum()
    )
    if stage2_unserved > minimum_unserved + float(unserved_tolerance_mwh) + 1e-6:
        raise RuntimeError("v1.0 economic stage violated minimum-shortage constraint")
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
    investment_cost = (
        solar_mw * float(annualized_costs["solar_million_inr_per_mw_year"])
        + wind_mw * float(annualized_costs["wind_million_inr_per_mw_year"])
        + bess_mw * float(annualized_costs["bess_million_inr_per_mw_year"])
    )
    import_cost = imports_mwh * import_cost_million_inr_per_mwh

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
        "annualized_candidate_investment_million_inr_per_year": investment_cost,
        "import_energy_cost_million_real_2021_22_inr_per_year": import_cost,
        "partial_economic_objective_million_real_2021_22_inr_per_year": (
            investment_cost + import_cost
        ),
        "import_price_real_2021_22_inr_per_mwh": float(import_price_real_inr_per_mwh),
        "solver": {
            "engine": "PyPSA/Linopy",
            "backend": "HiGHS",
            "stage1": [status1, condition1],
            "stage2": [status2, condition2],
        },
    }


def run_import_economics_suite(
    root: Path,
    *,
    profile_path: Path,
    hours: int = 8760,
) -> dict[str, Any]:
    if not 24 <= hours <= 8760 or hours % 24:
        raise ValueError("hours must be whole days between 24 and 8760")
    suite = load_import_economics_suite(
        root / "configs/full_pypsa_import_economics_v1_0.yaml"
    )
    evidence = validate_import_evidence(root, suite)
    reference_suite = load_proxy_expansion_suite(
        root / "configs/full_pypsa_proxy_expansion_v0_8.yaml"
    )
    future = load_future_adequacy_suite(
        root / "configs/full_pypsa_future_adequacy_v0_4.yaml"
    )
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

    results: list[dict[str, Any]] = []
    for demand_id in suite["demand_cases"]:
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

        for transfer_id in suite["transfer_cases"]:
            transfer = transfer_lookup[transfer_id]
            for envelope_case in suite["capacity_envelope_cases"]:
                caps = _candidate_caps(root, envelope_case, reference_suite)
                for bess_cost_case in suite["bess_cost_cases"]:
                    costs = _annualized_costs(root, bess_cost_case)
                    for price in suite["import_price_cases"]:
                        solved = solve_import_economic_case(
                            residual_load_mw=residual,
                            solar_profile=solar,
                            wind_profile=wind,
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
                                reference_suite["objective"]["unserved_tolerance_mwh"]
                            ),
                        )
                        results.append(
                            {
                                "demand_case": demand_id,
                                "transfer_case": transfer_id,
                                "import_limit_mw": float(transfer["import_limit_mw"]),
                                "capacity_envelope_case": envelope_case,
                                "bess_cost_case": bess_cost_case,
                                "import_price_case": price["id"],
                                **solved,
                            }
                        )

    expected = (
        len(suite["demand_cases"])
        * len(suite["transfer_cases"])
        * len(suite["capacity_envelope_cases"])
        * len(suite["bess_cost_cases"])
        * len(suite["import_price_cases"])
    )
    if len(results) != expected:
        raise RuntimeError("v1.0 did not solve the complete configured matrix")

    return {
        "classification": SUITE_CLASS,
        "prepared_date": suite["prepared_date"],
        "hours": hours,
        "full_financial_year": hours == 8760,
        "cases_solved": len(results),
        "price_basis": suite["price_basis"],
        "forward_transfer_benchmarks": suite["forward_transfer_benchmarks"],
        "renewable_profile_alignment": alignment,
        "cases": results,
        "release": suite["release"],
        "interpretation": [
            (
                "Stage 1 preserves the v0.8/v0.9 adequacy-first formulation. Stage 2 "
                "trades annualized candidate investment against source-bounded import "
                "energy price proxies on one real 2021-22 INR basis."
            ),
            (
                "Existing hydro/nonhydro are frozen and carry no economic dispatch cost, "
                "so the reported objective is partial and not total system cost."
            ),
            (
                "The CEA 2696 MW (2029-30) and 2020 MW (2034-35) figures are forward "
                "peak import requirements, not future ATC values."
            ),
            (
                "No higher future transfer cap is invented; 4455 MW remains the only "
                "source-valued ATC, alongside the existing 80% and 60% stress cases."
            ),
        ],
        "evidence_classification": evidence["classification"],
    }
