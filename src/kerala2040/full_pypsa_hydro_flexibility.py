"""Bracket intraday hydro flexibility in the full-PyPSA proxy adequacy screen.

v0.2 fixed each day's hydro energy as a flat 24-hour average. v0.3 keeps the
same daily hydro MWh but adds an optimistic upper-bound mode that may redispatch
that energy freely within each day, bounded by aggregate installed hydro MW.

This is intentionally not a reservoir/cascade model and not validated dispatch.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import xarray as xr
import yaml

from kerala2040.chronological_screen import (
    ScreeningAssumptions,
    prepare_inputs,
)
from kerala2040.full_pypsa_proxy_adequacy import (
    load_proxy_adequacy_suite,
    load_v02_selection,
    run_proxy_adequacy_suite,
)

CLASSIFICATION = "full_pypsa_hydro_flexibility_bracket_v0_3_not_validated_dispatch"
HYDRO_NAME = "daily_energy_redispatch_hydro"


def load_hydro_flexibility_config(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if data.get("classification") != CLASSIFICATION:
        raise ValueError("hydro flexibility configuration classification mismatch")
    release = data.get("release", {})
    if release.get("research_hydro_flexibility_bracket_ready") is not True:
        raise ValueError("hydro flexibility bracket is not released")
    if release.get("validated_hydro_dispatch_ready") is not False:
        raise ValueError("v0.3 incorrectly claims validated hydro dispatch")
    if release.get("reservoir_model_ready") is not False:
        raise ValueError("v0.3 incorrectly claims a reservoir model")
    if release.get("capacity_expansion_ready") is not False:
        raise ValueError("v0.3 incorrectly permits capacity expansion")
    return data


def _load_inputs(
    root: Path,
    suite: dict[str, Any],
) -> tuple[pd.DataFrame, dict[str, Any], dict[str, Any]]:
    proxy = json.loads((root / suite["chronology"]).read_text(encoding="utf-8"))
    qa = json.loads((root / suite["qa"]).read_text(encoding="utf-8"))
    observed = json.loads(
        (root / suite["observed_capacity_reference"]).read_text(encoding="utf-8")
    )
    daily = pd.read_csv(root / suite["daily_source_energy"])
    hourly, metadata = prepare_inputs(
        proxy,
        daily,
        expected_missing_dates=qa["missing_dates"],
    )
    metadata["source_archive_sha256"] = qa["source_archive_sha256"]
    metadata["input_qa"] = "verified daily SLDC accounting plus proxy hourly chronology"
    return hourly, metadata, observed


def build_daily_hydro_redispatch_network(
    hourly: pd.DataFrame,
    metadata: dict[str, Any],
    assumptions: ScreeningAssumptions,
    *,
    installed_hydro_mw: float,
    installed_nonhydro_mw: float,
):
    """Build a one-bus screen with flexible intraday hydro and fixed nonhydro.

    Hydro is bounded only by aggregate installed MW. A separate custom constraint
    enforces exact conservation of each day's hydro energy.
    """
    assumptions.validate()
    if hourly.empty or hourly.snapshot_ist_naive.duplicated().any():
        raise ValueError("nonempty unique hourly timestamps are required")
    if installed_hydro_mw <= 0 or installed_nonhydro_mw <= 0:
        raise ValueError("installed capacities must be positive")
    if hourly.nonhydro_fixed_mw.max() > installed_nonhydro_mw + 1e-6:
        raise ValueError("daily-average nonhydro exceeds installed nonhydro capacity")

    daily_hydro_mwh = hourly.groupby("date").hydro_fixed_mw.sum()
    if (daily_hydro_mwh <= 0).any():
        raise ValueError("daily hydro energy must be positive")
    daily_hours = hourly.groupby("date").size()
    if not daily_hours.eq(24).all():
        raise ValueError("daily hydro redispatch requires complete 24-hour days")
    max_daily_hydro_mwh = installed_hydro_mw * daily_hours
    if (daily_hydro_mwh > max_daily_hydro_mwh + 1e-6).any():
        raise ValueError("daily hydro energy exceeds installed-capacity energy ceiling")

    import pypsa

    snapshots = pd.DatetimeIndex(hourly.snapshot_ist_naive)
    network = pypsa.Network()
    network.set_snapshots(snapshots)
    network.snapshot_weightings.loc[:, :] = 1.0
    for carrier in (
        "electricity",
        "hydro",
        "nonhydro",
        "interstate_import",
        "unserved",
    ):
        network.add("Carrier", carrier)
    network.add("Bus", "kerala", carrier="electricity")
    network.add(
        "Load",
        "reconstructed_load",
        bus="kerala",
        p_set=hourly.load_mw.to_numpy(),
    )
    network.add(
        "Generator",
        HYDRO_NAME,
        bus="kerala",
        carrier="hydro",
        p_nom=installed_hydro_mw,
        p_min_pu=0.0,
        p_max_pu=1.0,
        marginal_cost=0.0,
    )
    nonhydro_pu = hourly.nonhydro_fixed_mw.to_numpy(dtype=float) / installed_nonhydro_mw
    network.add(
        "Generator",
        "fixed_daily_nonhydro",
        bus="kerala",
        carrier="nonhydro",
        p_nom=installed_nonhydro_mw,
        p_min_pu=nonhydro_pu,
        p_max_pu=nonhydro_pu,
        marginal_cost=0.0,
    )
    network.add(
        "Generator",
        "screened_import",
        bus="kerala",
        carrier="interstate_import",
        p_nom=assumptions.import_limit_mw,
        marginal_cost=assumptions.objective_import_per_mwh,
    )
    network.add(
        "Generator",
        "unserved_load",
        bus="kerala",
        carrier="unserved",
        p_nom=max(float(hourly.load_mw.max()), 1.0),
        marginal_cost=assumptions.objective_unserved_per_mwh,
    )
    network.meta = {
        **metadata,
        "assumptions": {
            "import_limit_mw": assumptions.import_limit_mw,
            "objective_import_per_mwh": assumptions.objective_import_per_mwh,
            "objective_unserved_per_mwh": assumptions.objective_unserved_per_mwh,
        },
        "hydro_mode": "daily_energy_redispatch_upper_bound",
        "hydro_energy_constraint": "exact daily MWh conservation",
        "hydro_power_constraint": f"0 <= p <= {installed_hydro_mw} MW aggregate",
        "hours_in_run": len(hourly),
    }
    return network, daily_hydro_mwh.astype(float)


def solve_daily_hydro_redispatch(
    network,
    daily_hydro_mwh: pd.Series,
) -> tuple[str, str]:
    """Solve with one exact hydro-energy equality per modelled day."""

    def add_daily_hydro_constraints(n, sns) -> None:
        p_hydro = n.model.variables["Generator-p"].sel(
            name=HYDRO_NAME,
            snapshot=sns,
        )
        weights = n.snapshot_weightings["generators"].loc[sns]
        snapshot_days = pd.DatetimeIndex(sns).normalize()
        codes, unique_days = pd.factorize(snapshot_days, sort=False)
        grouper = xr.DataArray(
            codes,
            coords={"snapshot": sns},
            dims="snapshot",
            name="hydro_day",
        )
        energy_by_day = (p_hydro * weights).groupby(grouper).sum()
        target = daily_hydro_mwh.reindex(
            pd.DatetimeIndex(unique_days).strftime("%Y-%m-%d")
        )
        if target.isna().any() or len(target) != len(unique_days):
            raise ValueError("daily hydro target does not align with active snapshots")
        rhs = xr.DataArray(
            target.to_numpy(dtype=float),
            coords={"hydro_day": np.arange(len(target))},
            dims="hydro_day",
        )
        n.model.add_constraints(
            lhs=energy_by_day,
            sign="=",
            rhs=rhs,
            name="Hydro-daily-energy-conservation",
        )

    status, condition = network.optimize(
        solver_name="highs",
        extra_functionality=add_daily_hydro_constraints,
        include_objective_constant=False,
    )
    if status != "ok" or condition != "optimal":
        raise RuntimeError(f"PyPSA HiGHS unsuccessful: {status} / {condition}")
    return status, condition


def _redispatch_case_summary(
    network,
    hourly: pd.DataFrame,
    daily_hydro_mwh: pd.Series,
    status: str,
    condition: str,
) -> dict[str, Any]:
    p = network.generators_t.p
    load = network.loads_t.p_set["reconstructed_load"].to_numpy(dtype=float)
    hydro = p[HYDRO_NAME].to_numpy(dtype=float)
    nonhydro = p["fixed_daily_nonhydro"].to_numpy(dtype=float)
    imports = p["screened_import"].to_numpy(dtype=float)
    unserved = p["unserved_load"].to_numpy(dtype=float)
    balance = hydro + nonhydro + imports + unserved - load
    max_balance = float(np.max(np.abs(balance)))
    if max_balance > 1e-3:
        raise RuntimeError(f"solved hourly power balance residual {max_balance} MW")

    dates = hourly["date"].to_numpy()
    hydro_daily = (
        pd.DataFrame({"date": dates, "hydro_mw": hydro})
        .groupby("date")
        .hydro_mw.sum()
    )
    target = daily_hydro_mwh.reindex(hydro_daily.index)
    max_daily_residual = float((hydro_daily - target).abs().max())
    if max_daily_residual > 1e-3:
        raise RuntimeError(
            f"daily hydro energy conservation residual {max_daily_residual} MWh"
        )

    total_load = float(load.sum())
    unserved_mwh = float(unserved.sum())
    return {
        "solver_status": status,
        "solver_condition": condition,
        "load_mwh_proxy": total_load,
        "imports_mwh_modelled": float(imports.sum()),
        "peak_import_mw_modelled": float(imports.max()),
        "unserved_energy_mwh": unserved_mwh,
        "deterministic_nens_pct": 100 * unserved_mwh / total_load,
        "hours_with_unserved": int((unserved > 1e-6).sum()),
        "max_unserved_mw": float(unserved.max()),
        "hydro_generation_mwh": float(hydro.sum()),
        "hydro_peak_mw_modelled": float(hydro.max()),
        "hydro_min_mw_modelled": float(hydro.min()),
        "hydro_peak_capacity_fraction": float(
            hydro.max() / network.generators.at[HYDRO_NAME, "p_nom"]
        ),
        "max_daily_hydro_energy_residual_mwh": max_daily_residual,
        "max_abs_hourly_balance_residual_mw": max_balance,
    }


def run_hydro_flexibility_bracket(
    root: Path,
    *,
    hours: int = 8760,
) -> dict[str, Any]:
    """Compare the flat daily replay with an optimistic daily hydro redispatch."""
    if not 24 <= hours <= 8760 or hours % 24:
        raise ValueError("hours must be whole days between 24 and 8760")

    config = load_hydro_flexibility_config(
        root / "configs/full_pypsa_hydro_flexibility_v0_3.yaml"
    )
    suite = load_proxy_adequacy_suite(
        root / "configs/full_pypsa_proxy_adequacy_v0_2.yaml"
    )
    selection = load_v02_selection(
        root / "configs/research_input_selection_v0_2.yaml"
    )
    flat = run_proxy_adequacy_suite(root, hours=hours)
    hourly, metadata, observed = _load_inputs(root, suite)
    hourly = hourly.iloc[:hours].copy()
    metadata["modeled_window_hours"] = hours
    metadata["full_financial_year"] = hours == 8760

    capacities = observed["electricity"]["capacity_mix_mw"]
    installed_hydro_mw = float(capacities["hydel"])
    installed_nonhydro_mw = float(
        observed["electricity"]["installed_capacity_mw"] - installed_hydro_mw
    )
    flat_by_id = {case["id"]: case for case in flat["cases"]}
    redispatched = []

    for case in suite["cases"]:
        assumptions = ScreeningAssumptions(
            import_limit_mw=float(case["import_limit_mw"]),
            objective_import_per_mwh=float(suite["objective"]["import_per_mwh"]),
            objective_unserved_per_mwh=float(suite["objective"]["unserved_per_mwh"]),
        )
        network, daily_hydro_mwh = build_daily_hydro_redispatch_network(
            hourly,
            metadata,
            assumptions,
            installed_hydro_mw=installed_hydro_mw,
            installed_nonhydro_mw=installed_nonhydro_mw,
        )
        status, condition = solve_daily_hydro_redispatch(
            network,
            daily_hydro_mwh,
        )
        summary = _redispatch_case_summary(
            network,
            hourly,
            daily_hydro_mwh,
            status,
            condition,
        )
        baseline = flat_by_id[case["id"]]
        summary.update(
            {
                "id": case["id"],
                "role": case["role"],
                "import_limit_mw": float(case["import_limit_mw"]),
                "unserved_energy_change_vs_flat_mwh": (
                    summary["unserved_energy_mwh"]
                    - float(baseline["unserved_energy_mwh"])
                ),
                "hours_with_unserved_change_vs_flat": (
                    summary["hours_with_unserved"]
                    - int(baseline["hours_with_unserved"])
                ),
                "max_unserved_change_vs_flat_mw": (
                    summary["max_unserved_mw"]
                    - float(baseline["max_unserved_mw"])
                ),
            }
        )
        if summary["unserved_energy_mwh"] > float(
            baseline["unserved_energy_mwh"]
        ) + 1e-4:
            raise RuntimeError(
                "optimistic hydro redispatch unexpectedly increases unserved energy"
            )
        redispatched.append(summary)

    return {
        "classification": CLASSIFICATION,
        "selection_classification": selection["classification"],
        "prepared_date": config["prepared_date"],
        "period": suite["period"],
        "hours": hours,
        "full_financial_year": hours == 8760,
        "flat_daily_average": flat["cases"],
        "daily_energy_redispatch_upper_bound": redispatched,
        "interpretation": [
            "Both modes use reconstructed hourly load, not measured interval telemetry.",
            (
                "Both conserve the same observed/imputed daily hydro MWh and retain "
                "the same fixed daily-average nonhydro energy."
            ),
            (
                "The redispatch mode is optimistic: it can move each day's aggregate "
                "hydro energy freely among that day's hours up to installed hydro MW."
            ),
            (
                "Any reduction in unserved energy therefore measures sensitivity to "
                "the flat-hydro assumption, not validated reservoir flexibility."
            ),
            (
                "Reservoir storage, cascade routing, environmental releases, outages, "
                "head effects and internal transmission remain unresolved."
            ),
        ],
        "release": {
            "validated_hydro_dispatch": False,
            "reservoir_model": False,
            "economic_dispatch": False,
            "probabilistic_LOLP": False,
            "capacity_expansion": False,
        },
    }
