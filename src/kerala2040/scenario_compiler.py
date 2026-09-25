"""Compile Kerala2040 S0-S5 structural specifications into auditable model requests.

This module resolves *structure*, never missing numerical evidence. A compiled
scenario therefore reports blockers until every required numeric input has been
admitted by a later input layer.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import yaml

MODEL_YEARS = (2030, 2035, 2040)
DEMAND_CASES = ("reference", "lower", "higher")
STRESSES = (
    "dry_hydro",
    "cloudy_low_solar",
    "heat_wave",
    "ev_surge",
    "battery_cost_high",
    "import_restriction",
    "import_price_high",
    "extreme_monsoon_flood",
)

_REQUIREMENT_KEYS = {
    "demand_trajectory": ("numerical_series_required", "demand_trajectory"),
    "demand_flexibility": ("numerical_parameters_required", "demand_flexibility"),
    "interstate_trade": ("transfer_limit_required", "interstate_transfer_limit"),
    "hydro_operation": ("hydrology_required", "hydrology"),
    "solar_expansion": ("gis_capacity_ceiling_required", "solar_capacity_ceiling"),
    "wind_expansion": ("gis_capacity_ceiling_required", "wind_capacity_ceiling"),
    "battery_storage": ("cost_and_performance_required", "battery_cost_performance"),
    "pumped_storage": ("site_specific_constraints_required", "pumped_storage_constraints"),
    "ev_smart_charging": ("ev_charging_dataset_required", "ev_charging"),
    "ecological_constraint": ("processed_gis_required", "processed_ecology_gis"),
    "fiscal_constraint": ("finance_dataset_required", "public_finance"),
}
_ALWAYS_REQUIRED = ("import_price_series", "reliability_criterion")


@dataclass(frozen=True)
class ScenarioRequest:
    scenario: str
    model_year: int
    demand_case: str = "reference"
    stress: str | None = None


@dataclass(frozen=True)
class CompiledScenario:
    scenario: str
    model_year: int
    demand_case: str
    stress: str | None
    levers: dict[str, str]
    required_inputs: tuple[str, ...]
    admitted_inputs: tuple[str, ...]
    blockers: tuple[str, ...]
    status: str
    classification: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def load_framework(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if data.get("classification") != "scenario_assumption":
        raise ValueError("Scenario framework must remain classified as scenario_assumption")
    if not data.get("scenarios") or not data.get("dimensions"):
        raise ValueError("Scenario framework is incomplete")
    return data


def _required_inputs(framework: dict[str, Any], levers: dict[str, str]) -> tuple[str, ...]:
    required: set[str] = set(_ALWAYS_REQUIRED)
    dims = framework["dimensions"]
    for dimension, value in levers.items():
        if dimension not in dims:
            raise ValueError(f"Unknown scenario dimension: {dimension}")
        allowed = dims[dimension]["allowed"]
        if value not in allowed:
            raise ValueError(f"Invalid {dimension} value: {value}")
        flag, requirement = _REQUIREMENT_KEYS[dimension]
        if dims[dimension].get(flag):
            # Fixed/off/none levers do not require expansion/flexibility evidence.
            if value not in {"fixed_existing", "off", "none"}:
                required.add(requirement)
        if dimension == "interstate_trade":
            required.add("import_price_series")
    return tuple(sorted(required))


def compile_scenario(
    framework: dict[str, Any],
    request: ScenarioRequest,
    admitted_inputs: set[str] | None = None,
) -> CompiledScenario:
    if request.scenario not in framework["scenarios"]:
        raise ValueError(f"Unknown scenario: {request.scenario}")
    if request.model_year not in MODEL_YEARS:
        raise ValueError(f"model_year must be one of {MODEL_YEARS}")
    if request.demand_case not in DEMAND_CASES:
        raise ValueError(f"demand_case must be one of {DEMAND_CASES}")
    if request.stress is not None and request.stress not in STRESSES:
        raise ValueError(f"Unknown stress test: {request.stress}")

    levers = dict(framework["scenarios"][request.scenario])
    levers["demand_trajectory"] = request.demand_case
    required = set(_required_inputs(framework, levers))

    # Stress cases add evidence; they never silently mutate a numeric value here.
    stress_requirement = {
        "dry_hydro": "dry_hydrology",
        "cloudy_low_solar": "low_solar_profile",
        "heat_wave": "heat_wave_demand",
        "ev_surge": "ev_surge_case",
        "battery_cost_high": "high_battery_cost_case",
        "import_restriction": "restricted_transfer_case",
        "import_price_high": "high_import_price_case",
        "extreme_monsoon_flood": "flood_system_case",
    }
    if request.stress:
        required.add(stress_requirement[request.stress])

    admitted = set(admitted_inputs or ())
    blockers = tuple(sorted(required - admitted))
    return CompiledScenario(
        scenario=request.scenario,
        model_year=request.model_year,
        demand_case=request.demand_case,
        stress=request.stress,
        levers=levers,
        required_inputs=tuple(sorted(required)),
        admitted_inputs=tuple(sorted(admitted & required)),
        blockers=blockers,
        status="READY_TO_BUILD_NETWORK" if not blockers else "UNSOLVED_SPECIFICATION",
        classification="scenario_structure_not_optimised_result",
    )


def compile_matrix(
    framework: dict[str, Any],
    model_years: tuple[int, ...] = MODEL_YEARS,
) -> list[CompiledScenario]:
    return [
        compile_scenario(framework, ScenarioRequest(scenario, year))
        for year in model_years
        for scenario in framework["scenarios"]
    ]
