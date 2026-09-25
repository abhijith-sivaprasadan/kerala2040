"""2030 adequacy-first proxy capacity expansion for Full-PyPSA v0.8."""
from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import yaml
from scipy.optimize import linprog
from scipy.sparse import coo_matrix, vstack

from kerala2040.full_pypsa_cost_finance import (
    annualised_cost_inr_per_kw_year,
    load_cost_finance_suite,
)
from kerala2040.full_pypsa_future_adequacy import (
    _load_base,
    load_future_adequacy_suite,
    morph_load_to_energy_and_peak,
)
from kerala2040.full_pypsa_renewable_capacity import load_capacity_envelope

SUITE_CLASS = (
    "full_pypsa_2030_proxy_capacity_expansion_v0_8_"
    "adequacy_first_not_system_cost_plan"
)


def load_proxy_expansion_suite(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if data.get("classification") != SUITE_CLASS:
        raise ValueError("v0.8 proxy expansion classification mismatch")
    release = data["release"]
    if release["research_proxy_capacity_expansion_counterfactual"] is not True:
        raise ValueError("v0.8 proxy expansion is not released")
    for key in (
        "full_economic_dispatch",
        "total_system_cost_optimization",
        "import_economics_validated",
        "statutory_siting_validated",
        "candidate_spatial_allocation_validated",
        "scenario_recommendation",
        "validated_capacity_plan",
    ):
        if release[key] is not False:
            raise ValueError(f"v0.8 incorrectly enables {key}")
    objective = data["objective"]
    if objective["stage_1"] != "minimize_total_unserved_mwh":
        raise ValueError("v0.8 stage-1 objective changed")
    if objective["import_marginal_cost_inr_per_mwh"] is not None:
        raise ValueError("v0.8 must not invent landed import economics")
    return data


def _align_profiles(profile_path: Path, snapshots: pd.Series) -> tuple[np.ndarray, np.ndarray]:
    profile = pd.read_parquet(profile_path)
    required = {
        "timestamp_ist",
        "solar_p_max_pu",
        "wind_p_max_pu_150m_niwe_anchored",
    }
    missing = required - set(profile.columns)
    if missing:
        raise ValueError(f"v0.6 profile artifact missing columns: {sorted(missing)}")

    ts = pd.to_datetime(profile["timestamp_ist"])
    if getattr(ts.dt, "tz", None) is not None:
        ts = ts.dt.tz_localize(None)
    keyed = profile.assign(_snapshot=ts).set_index("_snapshot")
    wanted = pd.DatetimeIndex(snapshots)
    if wanted.has_duplicates:
        raise ValueError("proxy expansion snapshots are duplicated")
    if keyed.index.has_duplicates:
        raise ValueError("v0.6 profile timestamps are duplicated")
    selected = keyed.reindex(wanted)
    profile_columns = ["solar_p_max_pu", "wind_p_max_pu_150m_niwe_anchored"]
    if selected[profile_columns].isna().any().any():
        raise ValueError("v0.6 renewable profile does not cover expansion chronology")

    solar = selected["solar_p_max_pu"].to_numpy(dtype=float)
    wind = selected["wind_p_max_pu_150m_niwe_anchored"].to_numpy(dtype=float)
    if not np.isfinite(solar).all() or not np.isfinite(wind).all():
        raise ValueError("renewable profiles contain non-finite values")
    if not ((solar >= 0).all() and (solar <= 1).all()):
        raise ValueError("solar profile outside [0,1]")
    if not ((wind >= 0).all() and (wind <= 1).all()):
        raise ValueError("wind profile outside [0,1]")
    return solar, wind


def _annualized_costs(root: Path, bess_cost_case: str) -> dict[str, float]:
    data = load_cost_finance_suite(root / "configs/full_pypsa_cost_finance_v0_5.yaml")
    rate = float(data["finance"]["discount_rate_real_fraction"])
    tech = data["research_2030"]

    def cost(item: dict[str, Any], capex: float) -> float:
        per_kw_year = annualised_cost_inr_per_kw_year(
            capex,
            discount_rate=rate,
            lifetime_years=int(item["lifetime_years"]),
            fixed_om_fraction_capex_per_year=float(
                item["fixed_om_fraction_capex_per_year"]
            ),
        )
        return per_kw_year / 1000.0

    solar = tech["solar_pv"]
    wind = tech["wind_onshore"]
    bess = tech["bess_4h"]
    low, high = [float(x) for x in bess["capex_inr_per_kw_bracket"]]
    if bess_cost_case not in {"low", "high"}:
        raise ValueError("unknown v0.8 BESS cost case")
    bess_capex = low if bess_cost_case == "low" else high
    return {
        "solar_million_inr_per_mw_year": cost(solar, float(solar["capex_inr_per_kw"])),
        "wind_million_inr_per_mw_year": cost(wind, float(wind["capex_inr_per_kw"])),
        "bess_million_inr_per_mw_year": cost(bess, bess_capex),
    }


def _candidate_caps(
    root: Path,
    envelope_case: str,
    suite: dict[str, Any],
) -> dict[str, float]:
    data = load_capacity_envelope(root / "configs/full_pypsa_renewable_capacity_v0_7.yaml")
    if envelope_case not in {"low", "reference", "high"}:
        raise ValueError("unknown renewable capacity envelope case")
    tech = data["technology_envelopes"]
    ground = float(tech["ground_utility_pv"]["derived_additional_headroom_mw"][envelope_case])
    floating = float(tech["floating_pv"]["derived_additional_headroom_mw"][envelope_case])
    wind = float(tech["onshore_wind"]["derived_additional_headroom_mw"][envelope_case])
    bess = float(suite["candidate_treatment"]["bess_4h"]["max_power_mw"])
    return {
        "ground_solar_headroom_mw": ground,
        "floating_solar_headroom_mw": floating,
        "solar_total_headroom_mw": ground + floating,
        "wind_headroom_mw": wind,
        "bess_power_headroom_mw": bess,
    }


def _build_lp(
    residual_load_mw: np.ndarray,
    solar_profile: np.ndarray,
    wind_profile: np.ndarray,
    *,
    import_limit_mw: float,
    caps: dict[str, float],
    bess_duration_h: float,
    charge_efficiency: float,
    discharge_efficiency: float,
) -> dict[str, Any]:
    n = len(residual_load_mw)
    if n <= 0:
        raise ValueError("empty expansion chronology")
    if len(solar_profile) != n or len(wind_profile) != n:
        raise ValueError("renewable profiles and load length differ")

    cap_solar, cap_wind, cap_bess = 0, 1, 2
    blocks = {
        name: 3 + i * n
        for i, name in enumerate(
            ("solar", "wind", "charge", "discharge", "soc", "imports", "unserved", "spill")
        )
    }
    nvars = 3 + 8 * n

    bounds: list[tuple[float, float | None]] = [
        (0.0, float(caps["solar_total_headroom_mw"])),
        (0.0, float(caps["wind_headroom_mw"])),
        (0.0, float(caps["bess_power_headroom_mw"])),
    ]
    bounds.extend([(0.0, None)] * (5 * n))
    bounds.extend([(0.0, float(import_limit_mw))] * n)
    bounds.extend([(0.0, None)] * (2 * n))

    eq_rows: list[int] = []
    eq_cols: list[int] = []
    eq_data: list[float] = []
    b_eq = np.zeros(2 * n, dtype=float)

    for t in range(n):
        row = t
        for name, coefficient in (
            ("solar", 1.0),
            ("wind", 1.0),
            ("discharge", 1.0),
            ("imports", 1.0),
            ("unserved", 1.0),
            ("charge", -1.0),
            ("spill", -1.0),
        ):
            eq_rows.append(row)
            eq_cols.append(blocks[name] + t)
            eq_data.append(coefficient)
        b_eq[row] = float(residual_load_mw[t])

        row = n + t
        prev = n - 1 if t == 0 else t - 1
        for col, value in (
            (blocks["soc"] + t, 1.0),
            (blocks["soc"] + prev, -1.0),
            (blocks["charge"] + t, -float(charge_efficiency)),
            (blocks["discharge"] + t, 1.0 / float(discharge_efficiency)),
        ):
            eq_rows.append(row)
            eq_cols.append(col)
            eq_data.append(value)

    a_eq = coo_matrix((eq_data, (eq_rows, eq_cols)), shape=(2 * n, nvars)).tocsr()

    ub_rows: list[int] = []
    ub_cols: list[int] = []
    ub_data: list[float] = []
    b_ub = np.zeros(5 * n, dtype=float)
    row = 0
    for t in range(n):
        for variable, cap_index, coefficient in (
            ("solar", cap_solar, -float(solar_profile[t])),
            ("wind", cap_wind, -float(wind_profile[t])),
            ("charge", cap_bess, -1.0),
            ("discharge", cap_bess, -1.0),
            ("soc", cap_bess, -float(bess_duration_h)),
        ):
            ub_rows.extend([row, row])
            ub_cols.extend([blocks[variable] + t, cap_index])
            ub_data.extend([1.0, coefficient])
            row += 1

    a_ub = coo_matrix((ub_data, (ub_rows, ub_cols)), shape=(5 * n, nvars)).tocsr()

    return {
        "n": n,
        "nvars": nvars,
        "blocks": blocks,
        "cap_indices": {
            "solar": cap_solar,
            "wind": cap_wind,
            "bess": cap_bess,
        },
        "bounds": bounds,
        "a_eq": a_eq,
        "b_eq": b_eq,
        "a_ub": a_ub,
        "b_ub": b_ub,
    }


def _solve_two_stage(
    lp: dict[str, Any],
    *,
    annualized_costs: dict[str, float],
    unserved_tolerance_mwh: float,
    stage1_minimum_unserved_mwh: float | None = None,
) -> tuple[np.ndarray, dict[str, float]]:
    nvars = int(lp["nvars"])
    n = int(lp["n"])
    blocks = lp["blocks"]
    cap = lp["cap_indices"]

    if stage1_minimum_unserved_mwh is None:
        c1 = np.zeros(nvars, dtype=float)
        c1[blocks["unserved"] : blocks["unserved"] + n] = 1.0
        stage1 = linprog(
            c1,
            A_ub=lp["a_ub"],
            b_ub=lp["b_ub"],
            A_eq=lp["a_eq"],
            b_eq=lp["b_eq"],
            bounds=lp["bounds"],
            method="highs",
        )
        if not stage1.success:
            raise RuntimeError(f"v0.8 adequacy stage failed: {stage1.message}")
        minimum_unserved = float(c1 @ stage1.x)
    else:
        minimum_unserved = float(stage1_minimum_unserved_mwh)
        if minimum_unserved < 0:
            raise ValueError("stage-1 minimum unserved energy cannot be negative")

    shortage_row = np.zeros(nvars, dtype=float)
    shortage_row[blocks["unserved"] : blocks["unserved"] + n] = 1.0
    a_ub_2 = vstack([lp["a_ub"], coo_matrix(shortage_row.reshape(1, -1))]).tocsr()
    b_ub_2 = np.concatenate(
        [lp["b_ub"], [minimum_unserved + float(unserved_tolerance_mwh)]]
    )

    c2 = np.zeros(nvars, dtype=float)
    c2[cap["solar"]] = annualized_costs["solar_million_inr_per_mw_year"]
    c2[cap["wind"]] = annualized_costs["wind_million_inr_per_mw_year"]
    c2[cap["bess"]] = annualized_costs["bess_million_inr_per_mw_year"]
    stage2 = linprog(
        c2,
        A_ub=a_ub_2,
        b_ub=b_ub_2,
        A_eq=lp["a_eq"],
        b_eq=lp["b_eq"],
        bounds=lp["bounds"],
        method="highs",
    )
    if not stage2.success:
        raise RuntimeError(f"v0.8 minimum-build stage failed: {stage2.message}")

    achieved_unserved = float(
        stage2.x[blocks["unserved"] : blocks["unserved"] + n].sum()
    )
    if achieved_unserved > minimum_unserved + float(unserved_tolerance_mwh) + 1e-6:
        raise RuntimeError("v0.8 stage 2 violated minimum-shortage constraint")
    return stage2.x, {
        "stage1_minimum_unserved_mwh": minimum_unserved,
        "stage2_unserved_mwh": achieved_unserved,
        "annualized_candidate_investment_million_inr_per_year": float(c2 @ stage2.x),
    }


def _solar_allocation_range(total_mw: float, caps: dict[str, float]) -> dict[str, float]:
    ground_cap = float(caps["ground_solar_headroom_mw"])
    floating_cap = float(caps["floating_solar_headroom_mw"])
    ground_min = max(0.0, float(total_mw) - floating_cap)
    ground_max = min(float(total_mw), ground_cap)
    if ground_min > ground_max + 1e-7:
        raise RuntimeError("combined solar build cannot be allocated within subtype caps")
    return {
        "ground_solar_min_mw": ground_min,
        "ground_solar_max_mw": ground_max,
        "floating_solar_min_mw": max(0.0, float(total_mw) - ground_max),
        "floating_solar_max_mw": min(float(total_mw), floating_cap),
    }


def solve_proxy_expansion_case(
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
    stage1_minimum_unserved_mwh: float | None = None,
) -> dict[str, Any]:
    lp = _build_lp(
        residual_load_mw,
        solar_profile,
        wind_profile,
        import_limit_mw=import_limit_mw,
        caps=caps,
        bess_duration_h=bess_duration_h,
        charge_efficiency=charge_efficiency,
        discharge_efficiency=discharge_efficiency,
    )
    solution, objective = _solve_two_stage(
        lp,
        annualized_costs=annualized_costs,
        unserved_tolerance_mwh=unserved_tolerance_mwh,
        stage1_minimum_unserved_mwh=stage1_minimum_unserved_mwh,
    )
    n = int(lp["n"])
    blocks = lp["blocks"]
    cap = lp["cap_indices"]

    solar_mw = float(solution[cap["solar"]])
    wind_mw = float(solution[cap["wind"]])
    bess_mw = float(solution[cap["bess"]])
    solar_dispatch = solution[blocks["solar"] : blocks["solar"] + n]
    wind_dispatch = solution[blocks["wind"] : blocks["wind"] + n]
    charge = solution[blocks["charge"] : blocks["charge"] + n]
    discharge = solution[blocks["discharge"] : blocks["discharge"] + n]
    imports = solution[blocks["imports"] : blocks["imports"] + n]
    spill = solution[blocks["spill"] : blocks["spill"] + n]

    solar_available = float(solar_mw * solar_profile.sum())
    wind_available = float(wind_mw * wind_profile.sum())
    return {
        **objective,
        "built": {
            "solar_combined_mw": solar_mw,
            "wind_onshore_mw": wind_mw,
            "bess_4h_power_mw": bess_mw,
            "bess_4h_energy_mwh": bess_mw * float(bess_duration_h),
            "solar_subtype_allocation_range": _solar_allocation_range(solar_mw, caps),
        },
        "dispatch": {
            "solar_generation_mwh": float(solar_dispatch.sum()),
            "wind_generation_mwh": float(wind_dispatch.sum()),
            "solar_available_mwh": solar_available,
            "wind_available_mwh": wind_available,
            "solar_curtailment_mwh": solar_available - float(solar_dispatch.sum()),
            "wind_curtailment_mwh": wind_available - float(wind_dispatch.sum()),
            "bess_charge_mwh": float(charge.sum()),
            "bess_discharge_mwh": float(discharge.sum()),
            "imports_mwh": float(imports.sum()),
            "peak_import_mw": float(imports.max()),
            "spill_mwh": float(spill.sum()),
        },
    }


def run_proxy_expansion_suite(
    root: Path,
    *,
    profile_path: Path,
    hours: int = 8760,
) -> dict[str, Any]:
    if not 24 <= hours <= 8760 or hours % 24:
        raise ValueError("hours must be whole days between 24 and 8760")
    suite = load_proxy_expansion_suite(
        root / "configs/full_pypsa_proxy_expansion_v0_8.yaml"
    )
    future = load_future_adequacy_suite(
        root / "configs/full_pypsa_future_adequacy_v0_4.yaml"
    )
    hourly_base, metadata_base, _ = _load_base(root, future)
    profiles = _align_profiles(profile_path, hourly_base["snapshot_ist_naive"])
    solar_full, wind_full = profiles

    cost_data = load_cost_finance_suite(root / "configs/full_pypsa_cost_finance_v0_5.yaml")
    bess = cost_data["research_2030"]["bess_4h"]
    eta_c = float(bess["charge_efficiency_symmetric"])
    eta_d = float(bess["discharge_efficiency_symmetric"])
    duration = float(bess["duration_hours"])

    demand_lookup = {item["id"]: item for item in future["demand_cases"]}
    transfer_lookup = {item["id"]: item for item in future["transfer_cases"]}
    results: list[dict[str, Any]] = []

    for demand_id in suite["demand_cases"]:
        demand = demand_lookup[demand_id]
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
        solar = solar_full[:hours]
        wind = wind_full[:hours]

        for transfer_id in suite["transfer_cases"]:
            transfer = transfer_lookup[transfer_id]
            for envelope_case in suite["capacity_envelope_cases"]:
                caps = _candidate_caps(root, envelope_case, suite)
                stage1_minimum: float | None = None
                for bess_cost_case in suite["bess_cost_cases"]:
                    costs = _annualized_costs(root, bess_cost_case)
                    solved = solve_proxy_expansion_case(
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
                            suite["objective"]["unserved_tolerance_mwh"]
                        ),
                        stage1_minimum_unserved_mwh=stage1_minimum,
                    )
                    stage1_minimum = float(solved["stage1_minimum_unserved_mwh"])
                    results.append(
                        {
                            "demand_case": demand_id,
                            "source_family": demand["source_family"],
                            "target_annual_energy_mu": float(demand["annual_energy_mu"]),
                            "target_peak_mw": float(demand["peak_mw"]),
                            "morph_scale": float(morph["scale"]),
                            "morph_offset_mw": float(morph["offset_mw"]),
                            "transfer_case": transfer_id,
                            "import_limit_mw": float(transfer["import_limit_mw"]),
                            "capacity_envelope_case": envelope_case,
                            "bess_cost_case": bess_cost_case,
                            "candidate_caps": caps,
                            "annualized_costs": costs,
                            **solved,
                        }
                    )

    return {
        "classification": SUITE_CLASS,
        "prepared_date": suite["prepared_date"],
        "hours": hours,
        "full_financial_year": hours == 8760,
        "cases": results,
        "interpretation": [
            "Stage 1 minimizes unserved energy with source-bounded candidate limits.",
            (
                "Stage 2 minimizes annualized solar/wind/BESS investment while preserving "
                "the stage-1 minimum shortage."
            ),
            (
                "Imports have no economic price in this checkpoint; zero-cost imports are "
                "bounded by the selected ATC sensitivity."
            ),
            (
                "Combined solar build cannot be uniquely split between ground and floating "
                "because both use the same generic cost and hourly screening profile."
            ),
            (
                "Existing hydro/nonhydro remain frozen FY2024-25 daily-average source-energy "
                "replays and are not economically redispatched."
            ),
            (
                "Results are adequacy-first proxy investment sensitivities, not total-system "
                "least-cost plans or statutory siting recommendations."
            ),
        ],
        "source_metadata": {
            "base_chronology_classification": metadata_base["classification"],
            "renewable_profile": str(profile_path),
            "import_economics_validated": False,
            "statutory_siting_validated": False,
        },
    }
