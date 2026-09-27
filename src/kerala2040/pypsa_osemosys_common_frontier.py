"""PyPSA versus TZ-OSeMOSYS comparison at the v1.3 common frontier.

This module does not use the old v0.8 SciPy LP as a reference. It prepares one
shared set of v1.3 physical/economic inputs, solves each case independently in
direct PyPSA/Linopy and TZ-OSeMOSYS/HiGHS, and compares the resulting system
outputs.

The common frontier deliberately stops at v1.3 because v1.4b/v1.5 source
reported inflow remains evidence-gated. The v1.3 net water-balance residual is
not catchment inflow.
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
from kerala2040.full_pypsa_idukki_reservoir_v1_3 import (
    load_idukki_reservoir_v13_suite,
    load_idukki_water_balance_inputs,
    solve_idukki_reservoir_case,
)
from kerala2040.full_pypsa_import_economics import load_import_economics_suite
from kerala2040.full_pypsa_proxy_expansion import (
    _align_profiles,
    _annualized_costs,
    _candidate_caps,
    load_proxy_expansion_suite,
)
from kerala2040.osemosys_capacity_benchmark import (
    REGION,
    TZ_OSEMOSYS_GIT_COMMIT,
    YEAR,
    _annual_activity,
    _new_capacity,
    _profile_dict,
    _solution_scalar,
)

COMMON_CLASS = "pypsa_osemosys_common_frontier_v1_3c_stateful_idukki_cross_framework"
ELECTRICITY = "electricity"
SOLAR = "solar-new"
WIND = "wind-new"
IMPORTS = "imports"
UNSERVED = "unserved"
OTHER_HYDRO = "other-hydro"
BASE_SURPLUS = "negative-residual-fixed-source"
BESS_POWER = "bess-power-investment"
BESS_CONVERTER = "bess-converter"
BESS_STORAGE = "bess-storage"
IDUKKI_STORAGE = "idukki-reservoir"
IDUKKI_INFLOW = "idukki-net-positive-source"
IDUKKI_OUTFLOW = "idukki-net-negative-outflow"
IDUKKI_TURBINE = "idukki-turbine"
IDUKKI_RELEASE = "idukki-additional-water-release"


def load_common_frontier_suite(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if data.get("classification") != COMMON_CLASS:
        raise ValueError("common-frontier classification mismatch")
    contract = data["common_contract"]
    if int(contract["horizon_hours"]) != 8736 or int(contract["horizon_days"]) != 364:
        raise ValueError("common-frontier horizon changed without review")
    expected = (
        len(contract["demand_cases"])
        * len(contract["transfer_cases"])
        * len(contract["idukki_availability_cases"])
    )
    if expected != int(contract["expected_cases"]) or expected != 12:
        raise ValueError("common-frontier case matrix changed unexpectedly")
    if data["frameworks"]["osemosys"]["tz_osemosys_git_commit"] != TZ_OSEMOSYS_GIT_COMMIT:
        raise ValueError("TZ-OSeMOSYS pin differs from the audited Step-10 commit")
    release = data["release"]
    if release["common_cross_framework_comparison"] is not True:
        raise ValueError("common comparison is not released")
    for key in (
        "observed_catchment_inflow_model",
        "total_system_cost_optimization",
        "validated_capacity_plan",
        "scenario_recommendation",
    ):
        if release[key] is not False:
            raise ValueError(f"common frontier incorrectly enables {key}")
    return data


def _demand_mapping(
    residual_mw: np.ndarray,
    timeslices: list[str],
) -> tuple[float, dict[str, float], np.ndarray]:
    residual = np.asarray(residual_mw, dtype=float)
    if len(residual) != len(timeslices) or not np.isfinite(residual).all():
        raise ValueError("common-frontier residual chronology is invalid")
    demand = np.maximum(residual, 0.0)
    surplus_source = np.maximum(-residual, 0.0)
    annual = float(demand.sum())
    if annual <= 0:
        raise ValueError("common-frontier positive residual demand is zero")
    profile = {
        name: float(value / annual)
        for name, value in zip(timeslices, demand, strict=True)
    }
    return annual, profile, surplus_source


def _activity(
    model: Any,
    technology: str,
    mode: str,
):
    return model._m["RateOfActivity"].sel(
        REGION=REGION,
        TECHNOLOGY=technology,
        MODE_OF_OPERATION=mode,
        YEAR=YEAR,
    )


def _fixed_activity_constraint(
    model: Any,
    technology: str,
    mode: str,
    values_mwh: np.ndarray,
    timeslices: list[str],
    name: str,
) -> None:
    n = len(timeslices)
    rhs = xr.DataArray(
        np.asarray(values_mwh, dtype=float) * float(n),
        coords={"TIMESLICE": timeslices},
        dims="TIMESLICE",
    )
    model._m.add_constraints(
        _activity(model, technology, mode) == rhs,
        name=name,
    )


def _daily_activity_constraints(
    model: Any,
    technology: str,
    mode: str,
    daily_mwh: np.ndarray,
    n: int,
) -> None:
    act = _activity(model, technology, mode)
    if n != len(daily_mwh) * 24:
        raise ValueError("daily hydro targets do not match hourly horizon")
    for day, target in enumerate(np.asarray(daily_mwh, dtype=float)):
        start = day * 24
        stop = start + 24
        model._m.add_constraints(
            act.isel(TIMESLICE=slice(start, stop)).sum()
            == float(target) * float(n),
            name=f"Kerala2040OtherHydroDailyEnergy{day:03d}",
        )


def _build_osemosys_v13_model(
    *,
    residual_after_nonhydro_mw: np.ndarray,
    other_hydro_daily_mwh: np.ndarray,
    other_hydro_power_mw: float,
    idukki_power_mw: float,
    idukki_full_storage_mcm: float,
    idukki_initial_storage_mcm: float,
    idukki_terminal_storage_mcm: float,
    idukki_energy_equivalent_mwh_per_mcm: float,
    idukki_net_water_balance_mcm_day: np.ndarray,
    solar_profile: np.ndarray,
    wind_profile: np.ndarray,
    import_limit_mw: float,
    import_price_real_inr_per_mwh: float,
    caps: dict[str, float],
    annualized_costs: dict[str, float],
    bess_duration_h: float,
    charge_efficiency: float,
    discharge_efficiency: float,
    stage: int,
    unserved_cap_mwh: float | None = None,
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
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError("Install the pinned TZ-OSeMOSYS dependency") from exc

    if stage not in {1, 2}:
        raise ValueError("common-frontier stage must be 1 or 2")

    residual = np.asarray(residual_after_nonhydro_mw, dtype=float)
    solar = np.asarray(solar_profile, dtype=float)
    wind = np.asarray(wind_profile, dtype=float)
    n = len(residual)
    if n != 8736 or n % 24:
        raise ValueError("v1.3 common frontier requires exactly 8736 hourly snapshots")
    if len(solar) != n or len(wind) != n:
        raise ValueError("renewable profile length mismatch")
    if len(other_hydro_daily_mwh) != n // 24:
        raise ValueError("other-hydro daily series length mismatch")
    if len(idukki_net_water_balance_mcm_day) != n // 24:
        raise ValueError("Idukki daily water-balance series length mismatch")
    if not 0 < charge_efficiency <= 1 or not 0 < discharge_efficiency <= 1:
        raise ValueError("BESS efficiencies must lie in (0,1]")

    timeslices = [f"h{i:04d}" for i in range(n)]
    year_split = {name: 1.0 / n for name in timeslices}
    demand_mwh, demand_profile, negative_residual = _demand_mapping(residual, timeslices)

    conversion = float(idukki_energy_equivalent_mwh_per_mcm)
    daily_water_energy = np.asarray(idukki_net_water_balance_mcm_day, dtype=float) * conversion
    hourly_water_energy = np.repeat(daily_water_energy / 24.0, 24)
    positive_water = np.maximum(hourly_water_energy, 0.0)
    negative_water = np.maximum(-hourly_water_energy, 0.0)

    stage2 = stage == 2
    unserved_limit = None
    if stage2:
        if unserved_cap_mwh is None or unserved_cap_mwh < 0:
            raise ValueError("stage 2 requires the stage-1 unserved cap")
        unserved_limit = float(unserved_cap_mwh)

    def fixed_technology(
        technology_id: str,
        capacity_mw: float,
        mode: OperatingMode,
        *,
        activity_annual_max: float | None = None,
    ) -> Technology:
        return Technology(
            id=technology_id,
            operating_life=1,
            capex=0,
            opex_fixed=0,
            residual_capacity=max(float(capacity_mw), 1e-9),
            capacity_activity_unit_ratio=float(n),
            capacity_additional_max=0,
            activity_annual_max=activity_annual_max,
            operating_modes=[mode],
        )

    technologies = [
        Technology(
            id=SOLAR,
            operating_life=1,
            capex=(
                float(annualized_costs["solar_million_inr_per_mw_year"])
                if stage2
                else 0.0
            ),
            opex_fixed=0,
            residual_capacity=0,
            capacity_activity_unit_ratio=float(n),
            capacity_factor=_profile_dict(solar, timeslices),
            capacity_additional_max=float(caps["solar_total_headroom_mw"]),
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
            capex=(
                float(annualized_costs["wind_million_inr_per_mw_year"])
                if stage2
                else 0.0
            ),
            opex_fixed=0,
            residual_capacity=0,
            capacity_activity_unit_ratio=float(n),
            capacity_factor=_profile_dict(wind, timeslices),
            capacity_additional_max=float(caps["wind_headroom_mw"]),
            operating_modes=[
                OperatingMode(
                    id="generate-wind",
                    opex_variable=0,
                    output_activity_ratio={ELECTRICITY: 1.0},
                )
            ],
        ),
        fixed_technology(
            IMPORTS,
            import_limit_mw,
            OperatingMode(
                id="import-electricity",
                opex_variable=(
                    float(import_price_real_inr_per_mwh) / 1_000_000.0
                    if stage2
                    else 0.0
                ),
                output_activity_ratio={ELECTRICITY: 1.0},
            ),
        ),
        fixed_technology(
            UNSERVED,
            max(float(np.maximum(residual, 0.0).max()), 1.0),
            OperatingMode(
                id="unserved-electricity",
                opex_variable=1.0 if stage == 1 else 0.0,
                output_activity_ratio={ELECTRICITY: 1.0},
            ),
            activity_annual_max=unserved_limit,
        ),
        fixed_technology(
            OTHER_HYDRO,
            other_hydro_power_mw,
            OperatingMode(
                id="generate-other-hydro",
                opex_variable=0,
                output_activity_ratio={ELECTRICITY: 1.0},
            ),
        ),
        fixed_technology(
            IDUKKI_TURBINE,
            idukki_power_mw,
            OperatingMode(
                id="generate-idukki",
                opex_variable=0,
                output_activity_ratio={ELECTRICITY: 1.0},
                from_storage={"*": {IDUKKI_STORAGE: True}},
            ),
        ),
        fixed_technology(
            IDUKKI_INFLOW,
            max(float(positive_water.max()), 1.0),
            OperatingMode(
                id="fixed-positive-water",
                opex_variable=0,
                to_storage={"*": {IDUKKI_STORAGE: True}},
            ),
        ),
        fixed_technology(
            IDUKKI_OUTFLOW,
            max(float(negative_water.max()), 1.0),
            OperatingMode(
                id="fixed-negative-water",
                opex_variable=0,
                from_storage={"*": {IDUKKI_STORAGE: True}},
            ),
        ),
        fixed_technology(
            IDUKKI_RELEASE,
            max(float(positive_water.max()) + float(idukki_power_mw), 1.0),
            OperatingMode(
                id="release-water",
                opex_variable=0,
                from_storage={"*": {IDUKKI_STORAGE: True}},
            ),
        ),
        fixed_technology(
            BASE_SURPLUS,
            max(float(negative_residual.max()), 1.0),
            OperatingMode(
                id="fixed-negative-residual",
                opex_variable=0,
                output_activity_ratio={ELECTRICITY: 1.0},
            ),
        ),
        Technology(
            id=BESS_POWER,
            operating_life=1,
            capex=(
                float(annualized_costs["bess_million_inr_per_mw_year"])
                if stage2
                else 0.0
            ),
            opex_fixed=0,
            residual_capacity=0,
            capacity_activity_unit_ratio=float(n),
            capacity_additional_max=float(caps["bess_power_headroom_mw"]),
            operating_modes=[
                OperatingMode(id="investment-marker", opex_variable=0)
            ],
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
                    input_activity_ratio={
                        ELECTRICITY: 1.0 / float(charge_efficiency)
                    },
                    to_storage={"*": {BESS_STORAGE: True}},
                ),
                OperatingMode(
                    id="discharge",
                    opex_variable=0,
                    output_activity_ratio={
                        ELECTRICITY: float(discharge_efficiency)
                    },
                    from_storage={"*": {BESS_STORAGE: True}},
                ),
            ],
        ),
    ]

    model = Model(
        id=f"kerala2040-common-frontier-v13-stage{stage}",
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
            ),
            Storage(
                id=IDUKKI_STORAGE,
                capex=0,
                operating_life=1,
                residual_capacity=float(idukki_full_storage_mcm) * conversion,
                initial_level=float(idukki_initial_storage_mcm) * conversion,
                minimum_charge=0,
            ),
        ],
        discount_rate=0.05,
        depreciation_method="straight-line",
    )

    model._build()
    m = model._m

    # Fixed source chronologies. OSeMOSYS activity is annualized; multiplying
    # the one-hour MWh target by n reverses YearSplit=1/n.
    _fixed_activity_constraint(
        model,
        IDUKKI_INFLOW,
        "fixed-positive-water",
        positive_water,
        timeslices,
        "Kerala2040FixedPositiveWater",
    )
    _fixed_activity_constraint(
        model,
        IDUKKI_OUTFLOW,
        "fixed-negative-water",
        negative_water,
        timeslices,
        "Kerala2040FixedNegativeWater",
    )
    _fixed_activity_constraint(
        model,
        BASE_SURPLUS,
        "fixed-negative-residual",
        negative_residual,
        timeslices,
        "Kerala2040FixedNegativeResidual",
    )
    _daily_activity_constraints(
        model,
        OTHER_HYDRO,
        "generate-other-hydro",
        np.asarray(other_hydro_daily_mwh, dtype=float),
        n,
    )

    # Existing Idukki storage cannot be expanded.
    m.add_constraints(
        m["NewStorageCapacity"].sel(
            REGION=REGION,
            STORAGE=IDUKKI_STORAGE,
            YEAR=YEAR,
        )
        == 0,
        name="Kerala2040FixedIdukkiStorageCapacity",
    )

    # Candidate BESS: four-hour energy rating and exact grid-side power limits.
    new_power = m["NewCapacity"].sel(
        REGION=REGION,
        TECHNOLOGY=BESS_POWER,
        YEAR=YEAR,
    )
    new_bess_energy = m["NewStorageCapacity"].sel(
        REGION=REGION,
        STORAGE=BESS_STORAGE,
        YEAR=YEAR,
    )
    m.add_constraints(
        new_bess_energy == float(bess_duration_h) * new_power,
        name="Kerala2040BessFourHourEnergyPowerTie",
    )
    bess_activity = m["RateOfActivity"].sel(
        REGION=REGION,
        TECHNOLOGY=BESS_CONVERTER,
        YEAR=YEAR,
    )
    charge = bess_activity.sel(MODE_OF_OPERATION="charge")
    discharge = bess_activity.sel(MODE_OF_OPERATION="discharge")
    m.add_constraints(
        charge <= float(charge_efficiency) * new_power * float(n),
        name="Kerala2040BessGridChargePowerLimit",
    )
    m.add_constraints(
        discharge <= new_power * float(n) / float(discharge_efficiency),
        name="Kerala2040BessGridDischargePowerLimit",
    )

    # Replace the generic first-period storage constraints so the two stores use
    # their actual boundary conditions: cyclic BESS and observed Idukki initial
    # stock. Canonical OSeMOSYS recursion/capacity constraints remain intact.
    m.remove_constraints("StorageLevelStart")
    level = m["StorageLevel"].sel(REGION=REGION, YEAR=YEAR)
    net = model._linear_expressions["NetCharge"].sel(REGION=REGION, YEAR=YEAR)

    bess_level = level.sel(STORAGE=BESS_STORAGE)
    bess_net = net.sel(STORAGE=BESS_STORAGE)
    m.add_constraints(
        bess_level.isel(TIMESLICE=0) - bess_level.isel(TIMESLICE=-1)
        == bess_net.isel(TIMESLICE=0),
        name="Kerala2040BessCyclicBoundary",
    )

    idukki_level = level.sel(STORAGE=IDUKKI_STORAGE)
    idukki_net = net.sel(STORAGE=IDUKKI_STORAGE)
    initial_mwh = float(idukki_initial_storage_mcm) * conversion
    terminal_mwh = float(idukki_terminal_storage_mcm) * conversion
    m.add_constraints(
        idukki_level.isel(TIMESLICE=0)
        == initial_mwh + idukki_net.isel(TIMESLICE=0),
        name="Kerala2040IdukkiInitialStorage",
    )
    m.add_constraints(
        idukki_level.isel(TIMESLICE=-1) == terminal_mwh,
        name="Kerala2040IdukkiTerminalStorage",
    )
    return model


def _solve_osemosys_stage(model: Any, conversion: float) -> dict[str, Any]:
    status, termination = model.solve(solver_name="highs")
    if status != "ok" or termination != "optimal":
        raise RuntimeError(
            f"common-frontier TZ-OSeMOSYS solve failed: {status}/{termination}"
        )
    solution = model.solution
    storage = np.asarray(
        solution["StorageLevel"].sel(
            REGION=REGION,
            STORAGE=IDUKKI_STORAGE,
            YEAR=YEAR,
        ),
        dtype=float,
    )
    release_mwh = _annual_activity(solution, IDUKKI_RELEASE)
    return {
        "status": status,
        "termination": termination,
        "stage_unserved_mwh": _annual_activity(solution, UNSERVED),
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
        "other_hydro_generation_mwh": _annual_activity(solution, OTHER_HYDRO),
        "idukki_generation_mwh": _annual_activity(solution, IDUKKI_TURBINE),
        "idukki_release_mwh": release_mwh,
        "idukki_release_mcm": release_mwh / conversion,
        "idukki_storage_min_mcm": float(storage.min() / conversion),
        "idukki_storage_max_mcm": float(storage.max() / conversion),
        "idukki_storage_terminal_mcm": float(storage[-1] / conversion),
    }


def solve_osemosys_v13_case(**kwargs: Any) -> dict[str, Any]:
    tolerance = float(kwargs.pop("unserved_tolerance_mwh"))
    conversion = float(kwargs["idukki_energy_equivalent_mwh_per_mcm"])

    stage1 = _solve_osemosys_stage(
        _build_osemosys_v13_model(stage=1, **kwargs),
        conversion,
    )
    stage2 = _solve_osemosys_stage(
        _build_osemosys_v13_model(
            stage=2,
            unserved_cap_mwh=stage1["stage_unserved_mwh"] + tolerance,
            **kwargs,
        ),
        conversion,
    )
    return {
        "stage1_minimum_unserved_mwh": stage1["stage_unserved_mwh"],
        "stage2_unserved_mwh": stage2["stage_unserved_mwh"],
        "built": {
            "solar_combined_mw": stage2["solar_mw"],
            "wind_onshore_mw": stage2["wind_mw"],
            "bess_4h_power_mw": stage2["bess_mw"],
            "bess_4h_energy_mwh": stage2["bess_energy_mwh"],
        },
        "imports_mwh": stage2["imports_mwh"],
        "other_hydro_generation_mwh": stage2["other_hydro_generation_mwh"],
        "idukki_generation_mwh": stage2["idukki_generation_mwh"],
        "idukki_storage_min_mcm": stage2["idukki_storage_min_mcm"],
        "idukki_storage_max_mcm": stage2["idukki_storage_max_mcm"],
        "idukki_storage_terminal_mcm": stage2["idukki_storage_terminal_mcm"],
        "idukki_additional_release_equivalent_mwh": stage2["idukki_release_mwh"],
        "idukki_additional_release_equivalent_mcm": stage2["idukki_release_mcm"],
        "solver": {
            "engine": "TZ-OSeMOSYS/Linopy",
            "backend": "HiGHS",
            "stage1": [stage1["status"], stage1["termination"]],
            "stage2": [stage2["status"], stage2["termination"]],
        },
    }


def _objective(
    result: dict[str, Any],
    costs: dict[str, float],
    import_price_real_inr_per_mwh: float,
) -> float:
    return (
        float(result["built"]["solar_combined_mw"])
        * float(costs["solar_million_inr_per_mw_year"])
        + float(result["built"]["wind_onshore_mw"])
        * float(costs["wind_million_inr_per_mw_year"])
        + float(result["built"]["bess_4h_power_mw"])
        * float(costs["bess_million_inr_per_mw_year"])
        + float(result["imports_mwh"])
        * float(import_price_real_inr_per_mwh)
        / 1_000_000.0
    )


def _compare(
    pypsa: dict[str, Any],
    osemosys: dict[str, Any],
    costs: dict[str, float],
    import_price: float,
    acceptance: dict[str, float],
) -> dict[str, Any]:
    differences = {
        "stage1_unserved_mwh": (
            float(osemosys["stage1_minimum_unserved_mwh"])
            - float(pypsa["stage1_minimum_unserved_mwh"])
        ),
        "stage2_unserved_mwh": (
            float(osemosys["stage2_unserved_mwh"])
            - float(pypsa["stage2_unserved_mwh"])
        ),
        "solar_mw": (
            float(osemosys["built"]["solar_combined_mw"])
            - float(pypsa["built"]["solar_combined_mw"])
        ),
        "wind_mw": (
            float(osemosys["built"]["wind_onshore_mw"])
            - float(pypsa["built"]["wind_onshore_mw"])
        ),
        "bess_mw": (
            float(osemosys["built"]["bess_4h_power_mw"])
            - float(pypsa["built"]["bess_4h_power_mw"])
        ),
        "imports_mwh": float(osemosys["imports_mwh"]) - float(pypsa["imports_mwh"]),
        "other_hydro_generation_mwh": (
            float(osemosys["other_hydro_generation_mwh"])
            - float(pypsa["other_hydro_generation_mwh"])
        ),
        "idukki_generation_mwh": (
            float(osemosys["idukki_generation_mwh"])
            - float(pypsa["idukki_generation_mwh"])
        ),
        "idukki_storage_min_mcm": (
            float(osemosys["idukki_storage_min_mcm"])
            - float(pypsa["idukki_storage_min_mcm"])
        ),
        "idukki_storage_max_mcm": (
            float(osemosys["idukki_storage_max_mcm"])
            - float(pypsa["idukki_storage_max_mcm"])
        ),
        "idukki_storage_terminal_mcm": (
            float(osemosys["idukki_storage_terminal_mcm"])
            - float(pypsa["idukki_storage_terminal_mcm"])
        ),
        "idukki_release_mcm": (
            float(osemosys["idukki_additional_release_equivalent_mcm"])
            - float(pypsa["idukki_additional_release_equivalent_mcm"])
        ),
        "stage2_objective_million_inr": (
            _objective(osemosys, costs, import_price)
            - _objective(pypsa, costs, import_price)
        ),
    }

    pass_flag = (
        abs(differences["stage1_unserved_mwh"]) <= acceptance["unserved_abs_mwh"]
        and abs(differences["stage2_unserved_mwh"]) <= acceptance["unserved_abs_mwh"]
        and abs(differences["solar_mw"]) <= acceptance["capacity_abs_mw"]
        and abs(differences["wind_mw"]) <= acceptance["capacity_abs_mw"]
        and abs(differences["bess_mw"]) <= acceptance["capacity_abs_mw"]
        and abs(differences["imports_mwh"]) <= acceptance["imports_abs_mwh"]
        and abs(differences["other_hydro_generation_mwh"])
        <= acceptance["hydro_generation_abs_mwh"]
        and abs(differences["idukki_generation_mwh"])
        <= acceptance["hydro_generation_abs_mwh"]
        and abs(differences["idukki_storage_terminal_mcm"])
        <= acceptance["idukki_terminal_storage_abs_mcm"]
        and float(pypsa["idukki_storage_min_mcm"])
        >= -acceptance["idukki_storage_bound_tolerance_mcm"]
        and float(osemosys["idukki_storage_min_mcm"])
        >= -acceptance["idukki_storage_bound_tolerance_mcm"]
        and float(pypsa["idukki_storage_max_mcm"])
        <= 1460.0 + acceptance["idukki_storage_bound_tolerance_mcm"]
        and float(osemosys["idukki_storage_max_mcm"])
        <= 1460.0 + acceptance["idukki_storage_bound_tolerance_mcm"]
        and abs(differences["stage2_objective_million_inr"])
        <= acceptance["objective_abs_million_inr"]
    )
    return {
        "status": "PASS" if pass_flag else "STRUCTURAL_DIFFERENCE",
        "differences_osemosys_minus_pypsa": differences,
        "pypsa_stage2_objective_million_inr": _objective(
            pypsa, costs, import_price
        ),
        "osemosys_stage2_objective_million_inr": _objective(
            osemosys, costs, import_price
        ),
        "operational_path_diagnostics": {
            "idukki_min_storage_difference_mcm": differences[
                "idukki_storage_min_mcm"
            ],
            "idukki_max_storage_difference_mcm": differences[
                "idukki_storage_max_mcm"
            ],
            "note": (
                "Intermediate reservoir trajectories are not a planning-"
                "equivalence gate because the shared stage-2 objective does "
                "not uniquely determine hourly water timing."
            ),
        },
        "release_difference_is_diagnostic_not_gate": True,
    }


def run_common_frontier(
    root: Path,
    *,
    profile_path: Path,
    suite_path: Path,
    only_case: tuple[str, str, str] | None = None,
) -> dict[str, Any]:
    suite = load_common_frontier_suite(suite_path)
    contract = suite["common_contract"]
    v13 = load_idukki_reservoir_v13_suite(
        root / contract["stateful_idukki"]
    )
    source = load_idukki_water_balance_inputs(root, v13)
    hours = int(contract["horizon_hours"])

    import_suite = load_import_economics_suite(
        root / contract["import_economics"]
    )
    proxy = load_proxy_expansion_suite(
        root / contract["candidate_expansion"]
    )
    future = load_future_adequacy_suite(root / contract["demand"])
    hourly_base, _, observed = _load_base(root, future)
    daily_total_hydro = _daily_targets(hourly_base, hours)

    daily_idukki = source["generation_mwh"].copy()
    daily_idukki.index = pd.DatetimeIndex(daily_idukki.index).strftime("%Y-%m-%d")
    other_hydro_daily = daily_total_hydro - daily_idukki.reindex(
        daily_total_hydro.index
    )
    if other_hydro_daily.isna().any() or (other_hydro_daily < -1e-6).any():
        raise ValueError("common frontier cannot reconcile Idukki and total hydro")
    other_hydro_daily = other_hydro_daily.clip(lower=0.0)

    solar_full, wind_full, alignment = _align_profiles(
        profile_path,
        hourly_base["snapshot_ist_naive"],
    )
    cost_data = load_cost_finance_suite(root / contract["costs"])
    bess = cost_data["research_2030"]["bess_4h"]
    caps = _candidate_caps(
        root,
        contract["capacity_envelope_case"],
        proxy,
    )
    costs = _annualized_costs(root, contract["bess_cost_case"])

    price_lookup = {
        item["id"]: item for item in import_suite["import_price_cases"]
    }
    price = price_lookup[contract["import_price_case"]]
    import_price = float(price["real_2021_22_inr_per_mwh"])

    demand_lookup = {item["id"]: item for item in future["demand_cases"]}
    transfer_lookup = {
        item["id"]: item for item in future["transfer_cases"]
    }
    availability_lookup = {
        item["id"]: item for item in v13["idukki_availability_cases"]
    }

    snapshots = pd.DatetimeIndex(
        hourly_base["snapshot_ist_naive"].iloc[:hours].to_numpy(),
        name="snapshot",
    )
    other_hydro_power_mw = float(v13["other_hydro"]["installed_power_mw"])
    installed_hydro_mw = float(
        observed["electricity"]["capacity_mix_mw"]["hydel"]
    )
    if abs((other_hydro_power_mw + 780.0) - installed_hydro_mw) > 1e-6:
        raise ValueError("common-frontier hydro capacity split no longer reconciles")

    acceptance = {
        key: float(value) for key, value in suite["acceptance"].items()
    }
    cases: list[dict[str, Any]] = []

    for demand_id in contract["demand_cases"]:
        demand = demand_lookup[demand_id]
        morphed, morph = morph_load_to_energy_and_peak(
            hourly_base["load_mw"],
            annual_energy_mu=float(demand["annual_energy_mu"]),
            peak_mw=float(demand["peak_mw"]),
        )
        residual = (
            morphed.to_numpy(dtype=float)
            - hourly_base["nonhydro_fixed_mw"].to_numpy(dtype=float)
        )[:hours]

        for transfer_id in contract["transfer_cases"]:
            transfer = transfer_lookup[transfer_id]
            for availability_id in contract["idukki_availability_cases"]:
                case_key = (demand_id, transfer_id, availability_id)
                if only_case is not None and case_key != only_case:
                    continue
                availability = availability_lookup[availability_id]
                common_kwargs = {
                    "residual_after_nonhydro_mw": residual,
                    "other_hydro_daily_mwh": other_hydro_daily.to_numpy(dtype=float),
                    "other_hydro_power_mw": other_hydro_power_mw,
                    "idukki_power_mw": float(availability["powerhouse_mw"]),
                    "idukki_full_storage_mcm": float(source["full_storage_mcm"]),
                    "idukki_initial_storage_mcm": float(
                        source["initial_storage_mcm"]
                    ),
                    "idukki_terminal_storage_mcm": float(
                        source["terminal_storage_mcm"]
                    ),
                    "idukki_energy_equivalent_mwh_per_mcm": float(
                        source["energy_equivalent_mwh_per_mcm"]
                    ),
                    "idukki_net_water_balance_mcm_day": source[
                        "net_water_balance_mcm_day"
                    ].to_numpy(dtype=float),
                    "solar_profile": solar_full[:hours],
                    "wind_profile": wind_full[:hours],
                    "import_limit_mw": float(transfer["import_limit_mw"]),
                    "import_price_real_inr_per_mwh": import_price,
                    "caps": caps,
                    "annualized_costs": costs,
                    "bess_duration_h": float(bess["duration_hours"]),
                    "charge_efficiency": float(
                        bess["charge_efficiency_symmetric"]
                    ),
                    "discharge_efficiency": float(
                        bess["discharge_efficiency_symmetric"]
                    ),
                    "unserved_tolerance_mwh": float(
                        proxy["objective"]["unserved_tolerance_mwh"]
                    ),
                }

                pypsa = solve_idukki_reservoir_case(
                    snapshots=snapshots,
                    other_hydro_daily_mwh=other_hydro_daily,
                    idukki_net_water_balance_mcm_day=source[
                        "net_water_balance_mcm_day"
                    ],
                    **{
                        key: value
                        for key, value in common_kwargs.items()
                        if key
                        not in {
                            "other_hydro_daily_mwh",
                            "idukki_net_water_balance_mcm_day",
                        }
                    },
                )
                osemosys = solve_osemosys_v13_case(**common_kwargs)
                comparison = _compare(
                    pypsa,
                    osemosys,
                    costs,
                    import_price,
                    acceptance,
                )
                cases.append({
                    "case_id": (
                        f"{demand_id}__{transfer_id}__{availability_id}"
                    ),
                    "demand_case": demand_id,
                    "transfer_case": transfer_id,
                    "idukki_availability_case": availability_id,
                    "import_limit_mw": float(transfer["import_limit_mw"]),
                    "idukki_power_mw": float(availability["powerhouse_mw"]),
                    "demand_morph": {
                        "scale": float(morph["scale"]),
                        "offset_mw": float(morph["offset_mw"]),
                    },
                    "pypsa": pypsa,
                    "osemosys": osemosys,
                    "comparison": comparison,
                })

    expected_cases = 1 if only_case is not None else int(contract["expected_cases"])
    if len(cases) != expected_cases:
        raise RuntimeError(
            f"common-frontier solved {len(cases)} cases, expected {expected_cases}"
        )

    maxima: dict[str, float] = {}
    for row in cases:
        for key, value in row["comparison"][
            "differences_osemosys_minus_pypsa"
        ].items():
            maxima[key] = max(maxima.get(key, 0.0), abs(float(value)))

    return {
        "classification": COMMON_CLASS,
        "prepared_date": suite["prepared_date"],
        "hours": hours,
        "days": hours // 24,
        "cases_compared": len(cases),
        "case_filter": list(only_case) if only_case is not None else None,
        "all_cases_pass": all(
            row["comparison"]["status"] == "PASS" for row in cases
        ),
        "maximum_absolute_differences": maxima,
        "acceptance": acceptance,
        "source_qa": {
            "observed_storage_days": source["observed_storage_days"],
            "interpolated_storage_days": source["interpolated_storage_days"],
            "observed_generation_days": source["observed_generation_days"],
            "interpolated_generation_days": source[
                "interpolated_generation_days"
            ],
            "initial_storage_mcm": source["initial_storage_mcm"],
            "terminal_storage_mcm": source["terminal_storage_mcm"],
            "net_water_balance_sum_mcm": float(
                source["net_water_balance_mcm_day"].sum()
            ),
            "renewable_profile_alignment": alignment,
        },
        "common_contract": contract,
        "newer_evidence_not_admitted": suite["newer_evidence_not_admitted"],
        "interpretation": [
            "Neither framework is treated as the reference optimizer.",
            "Both are solved from the same prepared source inputs at the v1.3 frontier.",
            "The v1.3 reconstructed water term is a net balance residual, not observed catchment inflow.",
            "A pass establishes cross-framework agreement for this model boundary, not physical validation of a Kerala capacity plan.",
        ],
        "cases": cases,
    }
