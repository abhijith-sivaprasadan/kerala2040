"""Independent TZ-OSeMOSYS cross-framework capacity-expansion benchmark.

This module maps the existing Kerala2040 Full-PyPSA v0.8 adequacy-first proxy
capacity-expansion problem onto canonical OSeMOSYS commodity, technology and
storage equations. It preserves the v0.8 three-stage lexicographic objective:

1. minimize unserved energy;
2. minimize annualized candidate investment at the stage-1 shortage floor;
3. minimize imports with stage-2 capacities fixed.

The benchmark is implementation/structural evidence only. It inherits every
v0.8 source and proxy limitation and is not a validated Kerala capacity plan.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

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
    load_proxy_expansion_suite,
    solve_proxy_expansion_case,
)

TZ_OSEMOSYS_GIT_COMMIT = "2c95ef395858ad530fb38a0dfb5c142283964d24"
BENCHMARK_CLASS = (
    "independent_TZ_OSeMOSYS_capacity_expansion_benchmark_v0_1_"
    "not_validated_capacity_plan"
)
REGION = "KERALA"
YEAR = 2030
ELECTRICITY = "electricity"
SOLAR = "solar-new"
WIND = "wind-new"
IMPORTS = "imports"
UNSERVED = "unserved"
BESS_POWER = "bess-power-investment"
BESS_CONVERTER = "bess-converter"
BESS_STORAGE = "bess-storage"


@dataclass(frozen=True)
class BenchmarkCase:
    demand_case: str
    transfer_case: str
    envelope_case: str
    bess_cost_case: str

    @property
    def id(self) -> str:
        return (
            f"{self.demand_case}__{self.transfer_case}__"
            f"{self.envelope_case}__{self.bess_cost_case}"
        )


def load_benchmark_suite(path: Path) -> dict[str, Any]:
    import yaml

    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if data.get("classification") != BENCHMARK_CLASS:
        raise ValueError("OSeMOSYS benchmark classification mismatch")
    if data["implementation"]["tz_osemosys_git_commit"] != TZ_OSEMOSYS_GIT_COMMIT:
        raise ValueError("TZ-OSeMOSYS commit pin changed without code review")
    if data["release"]["cross_framework_benchmark"] is not True:
        raise ValueError("benchmark release flag is false")
    for key in ("validated_capacity_plan", "scenario_recommendation", "economic_dispatch_ready"):
        if data["release"][key] is not False:
            raise ValueError(f"benchmark incorrectly enables {key}")
    return data


def _profile_dict(values: np.ndarray, names: list[str]) -> dict[str, float]:
    return {name: float(value) for name, value in zip(names, values, strict=True)}


def _demand_profile(
    residual_load_mw: np.ndarray,
    names: list[str],
) -> tuple[float, dict[str, float]]:
    if len(residual_load_mw) != len(names):
        raise ValueError("residual chronology and time-slice labels differ")
    if not np.isfinite(residual_load_mw).all():
        raise ValueError("residual load contains non-finite values")
    minimum = float(residual_load_mw.min())
    if minimum < -1e-7:
        raise ValueError(
            "OSeMOSYS residual-demand mapping requires non-negative hourly residual load; "
            f"minimum was {minimum:.6f} MW. Represent fixed supply explicitly before proceeding."
        )
    residual = np.maximum(residual_load_mw.astype(float), 0.0)
    annual_mwh = float(residual.sum())
    if annual_mwh <= 0:
        raise ValueError("residual annual energy must be positive")
    return annual_mwh, {
        name: float(value / annual_mwh)
        for name, value in zip(names, residual, strict=True)
    }


def _solution_scalar(solution: Any, variable: str, **coords: Any) -> float:
    return float(solution[variable].sel(**coords).item())


def _new_capacity(solution: Any, technology: str) -> float:
    return _solution_scalar(
        solution,
        "NewCapacity",
        REGION=REGION,
        TECHNOLOGY=technology,
        YEAR=YEAR,
    )


def _annual_activity(solution: Any, technology: str) -> float:
    return _solution_scalar(
        solution,
        "TotalTechnologyAnnualActivity",
        REGION=REGION,
        TECHNOLOGY=technology,
        YEAR=YEAR,
    )


def _build_osemosys_model(
    *,
    residual_load_mw: np.ndarray,
    solar_profile: np.ndarray,
    wind_profile: np.ndarray,
    import_limit_mw: float,
    caps: dict[str, float],
    costs: dict[str, float],
    bess_duration_h: float,
    charge_efficiency: float,
    discharge_efficiency: float,
    stage: int,
    unserved_cap_mwh: float | None = None,
    fixed_capacities: dict[str, float] | None = None,
):
    try:
        from tz.osemosys import (
            Commodity,
            Model,
            OperatingMode,
            Region,
            Storage,
            Technology,
            TimeDefinition,
        )
    except ImportError as exc:  # pragma: no cover - workflow installs pinned dependency
        raise RuntimeError(
            "Install the pinned TZ-OSeMOSYS dependency before running Step 10."
        ) from exc

    if stage not in {1, 2, 3}:
        raise ValueError("stage must be 1, 2 or 3")
    n = len(residual_load_mw)
    if n < 24 or n % 24:
        raise ValueError("benchmark horizon must contain whole days and at least 24 hours")
    if len(solar_profile) != n or len(wind_profile) != n:
        raise ValueError("renewable profile length mismatch")
    if not 0 < charge_efficiency <= 1 or not 0 < discharge_efficiency <= 1:
        raise ValueError("BESS efficiencies must lie in (0, 1]")

    timeslices = [f"h{i:04d}" for i in range(n)]
    demand_mwh, demand_profile = _demand_profile(residual_load_mw, timeslices)
    year_split = {name: 1.0 / n for name in timeslices}

    def investment_bounds(name: str, upper: float) -> dict[str, Any]:
        if stage == 3:
            if fixed_capacities is None or name not in fixed_capacities:
                raise ValueError(f"stage 3 missing fixed capacity for {name}")
            value = float(fixed_capacities[name])
            return {
                "capacity_additional_min": value,
                "capacity_additional_max": value,
            }
        return {"capacity_additional_max": float(upper)}

    annualised = stage == 2
    solar_cost = float(costs["solar_million_inr_per_mw_year"]) if annualised else 0.0
    wind_cost = float(costs["wind_million_inr_per_mw_year"]) if annualised else 0.0
    bess_cost = float(costs["bess_million_inr_per_mw_year"]) if annualised else 0.0

    unserved_limit = None
    if stage in {2, 3}:
        if unserved_cap_mwh is None or unserved_cap_mwh < 0:
            raise ValueError("stage 2/3 requires a non-negative unserved-energy cap")
        unserved_limit = float(unserved_cap_mwh)

    technologies = [
        Technology(
            id=SOLAR,
            operating_life=1,
            capex=solar_cost,
            opex_fixed=0,
            residual_capacity=0,
            capacity_activity_unit_ratio=float(n),
            capacity_factor=_profile_dict(solar_profile, timeslices),
            **investment_bounds(SOLAR, float(caps["solar_total_headroom_mw"])),
            operating_modes=[
                OperatingMode(
                    id="generate-solar",
                    opex_variable=0,
                    output_activity_ratio={ELECTRICITY: 1.0},
                )
            ],
        ),
        Technology(
            id=WIND,
            operating_life=1,
            capex=wind_cost,
            opex_fixed=0,
            residual_capacity=0,
            capacity_activity_unit_ratio=float(n),
            capacity_factor=_profile_dict(wind_profile, timeslices),
            **investment_bounds(WIND, float(caps["wind_headroom_mw"])),
            operating_modes=[
                OperatingMode(
                    id="generate-wind",
                    opex_variable=0,
                    output_activity_ratio={ELECTRICITY: 1.0},
                )
            ],
        ),
        Technology(
            id=IMPORTS,
            operating_life=1,
            capex=0,
            opex_fixed=0,
            residual_capacity=float(import_limit_mw),
            capacity_activity_unit_ratio=float(n),
            capacity_additional_max=0,
            operating_modes=[
                OperatingMode(
                    id="import-electricity",
                    opex_variable=1.0 if stage == 3 else 0.0,
                    output_activity_ratio={ELECTRICITY: 1.0},
                )
            ],
        ),
        Technology(
            id=UNSERVED,
            operating_life=1,
            capex=0,
            opex_fixed=0,
            residual_capacity=max(float(residual_load_mw.max()), 1.0),
            capacity_activity_unit_ratio=float(n),
            capacity_additional_max=0,
            activity_annual_max=unserved_limit,
            operating_modes=[
                OperatingMode(
                    id="unserved-electricity",
                    opex_variable=1.0 if stage == 1 else 0.0,
                    output_activity_ratio={ELECTRICITY: 1.0},
                )
            ],
        ),
        # Investment-only technology. Its NewCapacity is the BESS AC power rating.
        # Dispatch is handled by BESS_CONVERTER and custom constraints below so
        # grid-side charge and discharge limits exactly match v0.8 despite losses.
        Technology(
            id=BESS_POWER,
            operating_life=1,
            capex=bess_cost,
            opex_fixed=0,
            residual_capacity=0,
            capacity_activity_unit_ratio=float(n),
            **investment_bounds(BESS_POWER, float(caps["bess_power_headroom_mw"])),
            operating_modes=[OperatingMode(id="investment-marker", opex_variable=0)],
        ),
        Technology(
            id=BESS_CONVERTER,
            operating_life=1,
            capex=0,
            opex_fixed=0,
            residual_capacity=1_000_000.0,
            capacity_activity_unit_ratio=float(n),
            capacity_additional_max=0,
            operating_modes=[
                OperatingMode(
                    id="charge",
                    opex_variable=0,
                    input_activity_ratio={ELECTRICITY: 1.0 / float(charge_efficiency)},
                    to_storage={"*": {BESS_STORAGE: True}},
                ),
                OperatingMode(
                    id="discharge",
                    opex_variable=0,
                    output_activity_ratio={ELECTRICITY: float(discharge_efficiency)},
                    from_storage={"*": {BESS_STORAGE: True}},
                ),
            ],
        ),
    ]

    model = Model(
        id=f"kerala2040-step10-stage{stage}",
        time_definition=TimeDefinition(
            id=f"hourly-{n}",
            years=[YEAR],
            seasons=[1],
            day_types=[1],
            daily_time_brackets=[1],
            timeslices=timeslices,
            timeslice_in_season={name: 1 for name in timeslices},
            timeslice_in_daytype={name: 1 for name in timeslices},
            timeslice_in_timebracket={name: 1 for name in timeslices},
            year_split=year_split,
        ),
        regions=[Region(id=REGION)],
        commodities=[
            Commodity(
                id=ELECTRICITY,
                demand_annual=demand_mwh,
                demand_profile=demand_profile,
            )
        ],
        impacts=[],
        technologies=technologies,
        storage=[
            Storage(
                id=BESS_STORAGE,
                capex=0,
                operating_life=1,
                residual_capacity=0,
                initial_level=0,
                minimum_charge=0,
            )
        ],
        # A positive discount rate avoids the 0/0 annuity singularity in the
        # TZ-OSeMOSYS financial expressions. With a one-year technology life,
        # CRF * PVAnnuity = 1 and first-year discount factor = 1, so the stage-2
        # capex coefficient remains exactly the supplied annualized v0.8 cost.
        discount_rate=0.05,
        depreciation_method="straight-line",
    )

    # Build canonical OSeMOSYS equations first, then add only the bridge
    # constraints needed to map the existing v0.8 BESS definition exactly.
    model._build()
    m = model._m
    new_power = m["NewCapacity"].sel(
        REGION=REGION,
        TECHNOLOGY=BESS_POWER,
        YEAR=YEAR,
    )
    new_energy = m["NewStorageCapacity"].sel(
        REGION=REGION,
        STORAGE=BESS_STORAGE,
        YEAR=YEAR,
    )
    m.add_constraints(
        new_energy == float(bess_duration_h) * new_power,
        name="Kerala2040BessFourHourEnergyPowerTie",
    )

    activity = m["RateOfActivity"].sel(REGION=REGION, TECHNOLOGY=BESS_CONVERTER, YEAR=YEAR)
    charge = activity.sel(MODE_OF_OPERATION="charge")
    discharge = activity.sel(MODE_OF_OPERATION="discharge")
    # RateOfActivity is annualized. Charge activity represents stored energy,
    # while discharge activity represents storage withdrawal. These constraints
    # therefore reproduce the v0.8 grid-side power rating exactly after losses.
    m.add_constraints(
        charge <= float(charge_efficiency) * new_power * float(n),
        name="Kerala2040BessGridChargePowerLimit",
    )
    m.add_constraints(
        discharge <= new_power * float(n) / float(discharge_efficiency),
        name="Kerala2040BessGridDischargePowerLimit",
    )

    # TZ-OSeMOSYS fixes first-period storage level to StorageLevelStart. v0.8
    # instead uses a cyclic state equation linking the first hour to the final
    # hour. Replace only that boundary equation; all other canonical OSeMOSYS
    # storage recursion and capacity constraints remain intact.
    m.remove_constraints("StorageLevelStart")
    level = m["StorageLevel"].sel(REGION=REGION, STORAGE=BESS_STORAGE, YEAR=YEAR)
    net = model._linear_expressions["NetCharge"].sel(
        REGION=REGION,
        STORAGE=BESS_STORAGE,
        YEAR=YEAR,
    )
    m.add_constraints(
        level.isel(TIMESLICE=0) - level.isel(TIMESLICE=-1) == net.isel(TIMESLICE=0),
        name="Kerala2040CyclicStorageBoundary",
    )
    return model


def _solve_stage(model) -> dict[str, Any]:
    status, termination = model.solve(solver_name="highs")
    if status != "ok" or termination != "optimal":
        raise RuntimeError(f"TZ-OSeMOSYS solve failed: {status}/{termination}")
    solution = model.solution
    objective = float(model._objective) if model._objective is not None else float("nan")
    return {
        "status": status,
        "termination": termination,
        "unserved_mwh": _annual_activity(solution, UNSERVED),
        "imports_mwh": _annual_activity(solution, IMPORTS),
        "solar_mw": _new_capacity(solution, SOLAR),
        "wind_mw": _new_capacity(solution, WIND),
        "bess_mw": _new_capacity(solution, BESS_POWER),
        "bess_energy_mwh": _solution_scalar(
            solution,
            "NewStorageCapacity",
            REGION=REGION,
            STORAGE=BESS_STORAGE,
            YEAR=YEAR,
        ),
        "objective": objective,
    }


def solve_osemosys_three_stage(
    *,
    residual_load_mw: np.ndarray,
    solar_profile: np.ndarray,
    wind_profile: np.ndarray,
    import_limit_mw: float,
    caps: dict[str, float],
    costs: dict[str, float],
    bess_duration_h: float,
    charge_efficiency: float,
    discharge_efficiency: float,
    unserved_tolerance_mwh: float,
) -> dict[str, Any]:
    common = {
        "residual_load_mw": residual_load_mw,
        "solar_profile": solar_profile,
        "wind_profile": wind_profile,
        "import_limit_mw": import_limit_mw,
        "caps": caps,
        "costs": costs,
        "bess_duration_h": bess_duration_h,
        "charge_efficiency": charge_efficiency,
        "discharge_efficiency": discharge_efficiency,
    }

    stage1 = _solve_stage(_build_osemosys_model(stage=1, **common))
    cap2 = stage1["unserved_mwh"] + float(unserved_tolerance_mwh)
    stage2 = _solve_stage(_build_osemosys_model(stage=2, unserved_cap_mwh=cap2, **common))
    fixed = {
        SOLAR: stage2["solar_mw"],
        WIND: stage2["wind_mw"],
        BESS_POWER: stage2["bess_mw"],
    }
    cap3 = stage1["unserved_mwh"] + float(unserved_tolerance_mwh) + 1e-6
    stage3 = _solve_stage(
        _build_osemosys_model(
            stage=3,
            unserved_cap_mwh=cap3,
            fixed_capacities=fixed,
            **common,
        )
    )
    return {"stage1": stage1, "stage2": stage2, "stage3": stage3}


def _prepare_case(
    root: Path,
    profile_path: Path,
    case: BenchmarkCase,
    hours: int,
) -> dict[str, Any]:
    suite = load_proxy_expansion_suite(root / "configs/full_pypsa_proxy_expansion_v0_8.yaml")
    future = load_future_adequacy_suite(root / "configs/full_pypsa_future_adequacy_v0_4.yaml")
    hourly_base, metadata_base, _ = _load_base(root, future)
    solar_full, wind_full, alignment = _align_profiles(
        profile_path,
        hourly_base["snapshot_ist_naive"],
    )
    demand_lookup = {item["id"]: item for item in future["demand_cases"]}
    transfer_lookup = {item["id"]: item for item in future["transfer_cases"]}
    if case.demand_case not in demand_lookup:
        raise ValueError(f"unknown demand case: {case.demand_case}")
    if case.transfer_case not in transfer_lookup:
        raise ValueError(f"unknown transfer case: {case.transfer_case}")

    demand = demand_lookup[case.demand_case]
    morphed, morph = morph_load_to_energy_and_peak(
        hourly_base["load_mw"],
        annual_energy_mu=float(demand["annual_energy_mu"]),
        peak_mw=float(demand["peak_mw"]),
    )
    residual = (
        morphed.to_numpy(dtype=float)
        - hourly_base["hydro_fixed_mw"].to_numpy(dtype=float)
        - hourly_base["nonhydro_fixed_mw"].to_numpy(dtype=float)
    )[:hours]
    if float(residual.min()) < -1e-7:
        raise ValueError(
            "selected v0.8 case contains negative residual load and requires explicit "
            "fixed-generation representation before OSeMOSYS admission"
        )

    cost_data = load_cost_finance_suite(root / "configs/full_pypsa_cost_finance_v0_5.yaml")
    bess = cost_data["research_2030"]["bess_4h"]
    transfer = transfer_lookup[case.transfer_case]
    return {
        "case": case,
        "residual_load_mw": residual,
        "solar_profile": solar_full[:hours],
        "wind_profile": wind_full[:hours],
        "import_limit_mw": float(transfer["import_limit_mw"]),
        "caps": _candidate_caps(root, case.envelope_case, suite),
        "costs": _annualized_costs(root, case.bess_cost_case),
        "bess_duration_h": float(bess["duration_hours"]),
        "charge_efficiency": float(bess["charge_efficiency_symmetric"]),
        "discharge_efficiency": float(bess["discharge_efficiency_symmetric"]),
        "unserved_tolerance_mwh": float(suite["objective"]["unserved_tolerance_mwh"]),
        "metadata": {
            "base_chronology_classification": metadata_base["classification"],
            "renewable_profile_alignment": alignment,
            "morph_scale": float(morph["scale"]),
            "morph_offset_mw": float(morph["offset_mw"]),
            "residual_min_mw": float(residual.min()),
            "residual_max_mw": float(residual.max()),
            "residual_energy_mwh": float(residual.sum()),
        },
    }


def run_case(
    root: Path,
    profile_path: Path,
    case: BenchmarkCase,
    hours: int,
    acceptance: dict[str, float],
) -> dict[str, Any]:
    data = _prepare_case(root, profile_path, case, hours)
    solve_kwargs = {
        key: data[key]
        for key in (
            "residual_load_mw",
            "solar_profile",
            "wind_profile",
            "import_limit_mw",
            "caps",
            "costs",
            "bess_duration_h",
            "charge_efficiency",
            "discharge_efficiency",
            "unserved_tolerance_mwh",
        )
    }
    reference = solve_proxy_expansion_case(**solve_kwargs)
    osemosys = solve_osemosys_three_stage(**solve_kwargs)

    differences = {
        "stage1_unserved_mwh": (
            osemosys["stage1"]["unserved_mwh"] - reference["stage1_minimum_unserved_mwh"]
        ),
        "stage2_unserved_mwh": (
            osemosys["stage2"]["unserved_mwh"] - reference["stage2_unserved_mwh"]
        ),
        "solar_mw": osemosys["stage2"]["solar_mw"] - reference["built"]["solar_combined_mw"],
        "wind_mw": osemosys["stage2"]["wind_mw"] - reference["built"]["wind_onshore_mw"],
        "bess_mw": osemosys["stage2"]["bess_mw"] - reference["built"]["bess_4h_power_mw"],
        "stage3_imports_mwh": (
            osemosys["stage3"]["imports_mwh"] - reference["dispatch"]["imports_mwh"]
        ),
    }
    pass_flag = (
        abs(differences["stage1_unserved_mwh"]) <= acceptance["unserved_abs_mwh"]
        and abs(differences["stage2_unserved_mwh"]) <= acceptance["unserved_abs_mwh"]
        and abs(differences["solar_mw"]) <= acceptance["capacity_abs_mw"]
        and abs(differences["wind_mw"]) <= acceptance["capacity_abs_mw"]
        and abs(differences["bess_mw"]) <= acceptance["capacity_abs_mw"]
        and abs(differences["stage3_imports_mwh"]) <= acceptance["imports_abs_mwh"]
    )
    return {
        "case_id": case.id,
        "hours": hours,
        "status": "PASS" if pass_flag else "STRUCTURAL_DIFFERENCE",
        "acceptance": acceptance,
        "differences": differences,
        "osemosys": osemosys,
        "v0_8_reference": {
            "stage1_minimum_unserved_mwh": reference["stage1_minimum_unserved_mwh"],
            "stage2_unserved_mwh": reference["stage2_unserved_mwh"],
            "stage3_reporting_unserved_mwh": reference["stage3_reporting_unserved_mwh"],
            "built": reference["built"],
            "imports_mwh": reference["dispatch"]["imports_mwh"],
        },
        "inputs": {
            "import_limit_mw": data["import_limit_mw"],
            "caps": data["caps"],
            "costs": data["costs"],
            "bess_duration_h": data["bess_duration_h"],
            "charge_efficiency": data["charge_efficiency"],
            "discharge_efficiency": data["discharge_efficiency"],
        },
        "metadata": data["metadata"],
    }


def run_benchmark(
    root: Path,
    *,
    profile_path: Path,
    cases: list[BenchmarkCase],
    hours: int,
    suite_path: Path,
) -> dict[str, Any]:
    if hours < 24 or hours > 8760 or hours % 24:
        raise ValueError("hours must be whole days between 24 and 8760")
    suite = load_benchmark_suite(suite_path)
    acceptance = {key: float(value) for key, value in suite["acceptance"].items()}
    results = [run_case(root, profile_path, case, hours, acceptance) for case in cases]
    return {
        "classification": BENCHMARK_CLASS,
        "prepared_date": suite["prepared_date"],
        "implementation": suite["implementation"],
        "reference_model": suite["reference_model"],
        "hours": hours,
        "full_financial_year": hours == 8760,
        "cases": results,
        "all_cases_pass_numeric_equivalence": all(row["status"] == "PASS" for row in results),
        "limitations": [
            "inherits all Full-PyPSA v0.8 proxy demand, renewable, ATC and capacity-envelope limits",
            "does not validate landed import prices, statutory siting, grid hosting or 2040 assets",
            "reproduces v0.8 lexicographic accounting and is not a new policy scenario",
            "BESS uses canonical OSeMOSYS storage plus explicit bridge constraints for exact v0.8 mapping",
        ],
    }
