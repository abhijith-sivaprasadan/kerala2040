"""Full-PyPSA Idukki official-KSEB monthly reported-inflow checkpoint v1.5."""
from __future__ import annotations

from pathlib import Path
from typing import Any

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
from kerala2040.kseb_official_input_v1_5 import build_model_input

SUITE_CLASS = "full_pypsa_idukki_kseb_official_v1_5_monthly_reported_inflow_gate"


def load_kseb_official_v15_suite(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if data.get("classification") != SUITE_CLASS:
        raise ValueError("v1.5 KSEB official classification mismatch")
    source = data["official_source"]
    if int(source["required_months"]) != 12:
        raise ValueError("v1.5 requires exactly twelve KSEB monthly files")
    if source["missing_value_policy"] != "fail_closed_no_interpolation":
        raise ValueError("v1.5 must not interpolate official KSEB inflow")
    pilot = data["pilot_period"]
    if int(pilot["required_calendar_days"]) != 365:
        raise ValueError("v1.5 calendar-day requirement changed")
    if int(pilot["required_dispatch_inflow_days"]) != 364:
        raise ValueError("v1.5 dispatch-day requirement changed")
    if int(pilot["hours"]) != 8736:
        raise ValueError("v1.5 pilot-hour requirement changed")
    return data


def assess_kseb_official_gate(
    root: Path,
    bundle_dir: Path | None,
    suite: dict[str, Any],
) -> dict[str, Any]:
    base = {
        "classification": "V1_5_KSEB_OFFICIAL_MONTHLY_SOURCE_GATE",
        "required_months": int(suite["official_source"]["required_months"]),
        "required_calendar_days": int(suite["pilot_period"]["required_calendar_days"]),
        "required_dispatch_inflow_days": int(
            suite["pilot_period"]["required_dispatch_inflow_days"]
        ),
        "missing_value_policy": suite["official_source"]["missing_value_policy"],
    }
    if bundle_dir is None or not bundle_dir.is_dir():
        return {
            **base,
            "status": "blocked_official_monthly_bundle_missing",
            "physical_run_ready": False,
        }

    try:
        checked = build_model_input(root, bundle_dir)
    except (OSError, ValueError) as exc:
        return {
            **base,
            "status": "blocked_official_monthly_bundle_rejected",
            "physical_run_ready": False,
            "reason": str(exc),
        }

    return {
        **base,
        "status": checked["status"],
        "physical_run_ready": bool(checked["physical_run_ready"]),
        "extracted_unique_days": checked["extracted_unique_days"],
        "missing_dates": checked["missing_dates"],
        "invalid_or_missing_storage_dates": checked[
            "invalid_or_missing_storage_dates"
        ],
        "invalid_or_missing_inflow_dates": checked[
            "invalid_or_missing_inflow_dates"
        ],
        "anchor_reconciliation": checked["anchor_reconciliation"],
        "monthly_sources": checked["monthly_sources"],
    }


def load_kseb_official_model_inputs(
    root: Path,
    suite: dict[str, Any],
    bundle_dir: Path,
) -> dict[str, Any]:
    checked = build_model_input(root, bundle_dir)
    if not checked["physical_run_ready"]:
        raise ValueError(
            "v1.5 refuses source filling/interpolation; official KSEB monthly "
            "storage + Inflow (MCM) must pass the complete 365-day gate"
        )

    v13_suite = load_idukki_reservoir_v13_suite(
        root / suite["inherits"]["idukki_stateful_reservoir"]
    )
    legacy_boundary = load_idukki_water_balance_inputs(root, v13_suite)

    frame = checked["frame"].copy()
    frame.index = pd.DatetimeIndex(frame.index)
    dispatch_days = pd.date_range(
        suite["pilot_period"]["start"],
        suite["pilot_period"]["dispatch_end"],
        freq="D",
    )
    terminal_day = pd.Timestamp(suite["pilot_period"]["terminal_storage_date"])

    storage = pd.to_numeric(frame["live_storage_mcm"], errors="coerce")
    storage_now = storage.reindex(dispatch_days)
    storage_next = storage.reindex(dispatch_days + pd.Timedelta(days=1))
    storage_next.index = dispatch_days

    inflow = checked["dispatch_inflow_mcm_day"].reindex(dispatch_days)
    generation = legacy_boundary["generation_mwh"].reindex(dispatch_days)
    if generation.isna().any():
        raise ValueError("v1.5 SLDC Idukki generation boundary does not align")
    conversion = float(legacy_boundary["energy_equivalent_mwh_per_mcm"])
    turbine_water = generation / conversion
    historical_residual = inflow - (storage_next - storage_now) - turbine_water

    return {
        "full_storage_mcm": float(v13_suite["idukki"]["full_effective_storage_mcm"]),
        "initial_storage_mcm": float(storage.loc[pd.Timestamp(dispatch_days[0])]),
        "terminal_storage_mcm": float(storage.loc[terminal_day]),
        "energy_equivalent_mwh_per_mcm": conversion,
        "reported_inflow_mcm_day": inflow,
        "reported_inflow_days": int(inflow.notna().sum()),
        "reported_inflow_sum_mcm": float(inflow.sum()),
        "generation_mwh": generation,
        "monthly_sources": checked["monthly_sources"],
        "anchor_reconciliation": checked["anchor_reconciliation"],
        "historical_non_turbine_residual_mcm_day": historical_residual,
        "historical_non_turbine_residual_negative_days": int(
            historical_residual.lt(0).sum()
        ),
        "historical_non_turbine_residual_min_mcm_day": float(
            historical_residual.min()
        ),
        "historical_non_turbine_residual_max_mcm_day": float(
            historical_residual.max()
        ),
        "historical_non_turbine_residual_sum_mcm": float(
            historical_residual.sum()
        ),
        "sldc_generation_interpolated_days_boundary": int(
            legacy_boundary["interpolated_generation_days"]
        ),
    }


def run_kseb_official_v15_suite(
    root: Path,
    *,
    bundle_dir: Path,
    profile_path: Path,
) -> dict[str, Any]:
    suite = load_kseb_official_v15_suite(
        root / "configs/full_pypsa_idukki_kseb_official_v1_5.yaml"
    )
    source = load_kseb_official_model_inputs(root, suite, bundle_dir)
    v13_suite = load_idukki_reservoir_v13_suite(
        root / suite["inherits"]["idukki_stateful_reservoir"]
    )
    hours = int(suite["pilot_period"]["hours"])

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
        raise ValueError("v1.5 cannot reconcile Idukki and total daily hydro")
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
        raise ValueError("v1.5 hydro capacity split no longer reconciles")

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
                        "physical_kseb_official_inflow": physical,
                    }
                )

    return {
        "classification": SUITE_CLASS,
        "prepared_date": suite["prepared_date"],
        "pilot_days": hours // 24,
        "cases_solved": len(cases),
        "source_qa": {
            "official_monthly_source_files": source["monthly_sources"],
            "daily_anchor_reconciliation": source["anchor_reconciliation"],
            "reported_inflow_days": source["reported_inflow_days"],
            "reported_inflow_sum_mcm": source["reported_inflow_sum_mcm"],
            "initial_storage_mcm": source["initial_storage_mcm"],
            "terminal_storage_mcm": source["terminal_storage_mcm"],
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
            "sldc_generation_interpolated_days_boundary": source[
                "sldc_generation_interpolated_days_boundary"
            ],
        },
        "profile_alignment": alignment,
        "interpretation": {
            "reservoir_storage_is_direct_kseb_monthly_field": True,
            "reported_inflow_is_direct_kseb_monthly_mcm_field": True,
            "missing_reported_inflow_interpolated": False,
            "historical_turbine_water_uses_sldc_generation_boundary": True,
            "non_turbine_release_is_observed_spill": False,
            "head_dependent_efficiency": False,
            "validated_reservoir_operation": False,
        },
        "cases": cases,
    }
