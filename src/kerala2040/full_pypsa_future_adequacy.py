"""Future-demand adequacy counterfactual built on the v0.2 proxy chronology.

This is deliberately not a capacity plan. It preserves the ordering of the
FY2024-25 reconstructed hourly shape, morphs it to published future annual-energy
and peak anchors, freezes FY2024-25 internal generation as a counterfactual, and
tests explicit interstate-transfer bounds.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import yaml

from kerala2040.chronological_screen import (
    ScreeningAssumptions,
    build_hourly_screening_network,
    dispatch_summary,
    prepare_inputs,
    solve_hourly_screening,
)

SUITE_CLASS = "full_pypsa_future_demand_adequacy_counterfactual_not_capacity_plan"


def load_future_adequacy_suite(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if data.get("classification") != SUITE_CLASS:
        raise ValueError("future adequacy suite classification mismatch")
    demand = data.get("demand_cases", [])
    if [case.get("id") for case in demand] != [
        "lower_FY2030",
        "lower_FY2035",
        "lower_FY2040",
        "reference_FY2030_31",
        "reference_FY2034_35",
    ]:
        raise ValueError("future demand cases changed or reordered")
    transfer = data.get("transfer_cases", [])
    if [float(case["import_limit_mw"]) for case in transfer] != [
        4455.0,
        3564.0,
        2673.0,
    ]:
        raise ValueError("future adequacy transfer bounds changed")
    release = data.get("release", {})
    if release.get("research_counterfactual_screen") is not True:
        raise ValueError("future adequacy screen not released")
    for key in ("economic_dispatch", "capacity_expansion", "scenario_recommendation"):
        if release.get(key) is not False:
            raise ValueError(f"future adequacy suite incorrectly enables {key}")
    return data


def morph_load_to_energy_and_peak(
    load_mw: pd.Series,
    *,
    annual_energy_mu: float,
    peak_mw: float,
) -> tuple[pd.Series, dict[str, float]]:
    """Affine-morph one full-year shape to exact annual-energy and peak anchors."""
    values = pd.to_numeric(load_mw, errors="coerce").to_numpy(dtype=float)
    if len(values) != 8760 or not np.isfinite(values).all() or (values <= 0).any():
        raise ValueError("load morphology requires 8760 finite positive hourly values")
    target_mean = float(annual_energy_mu) * 1000.0 / 8760.0
    source_mean = float(values.mean())
    source_peak = float(values.max())
    if not target_mean > 0 or not float(peak_mw) > target_mean:
        raise ValueError("future annual energy and peak anchors are inconsistent")
    if source_peak <= source_mean:
        raise ValueError("source chronology has no peak-to-mean spread")

    scale = (float(peak_mw) - target_mean) / (source_peak - source_mean)
    offset = target_mean - scale * source_mean
    transformed = offset + scale * values
    if scale <= 0 or not np.isfinite(transformed).all() or (transformed <= 0).any():
        raise ValueError("affine future-load morphology produced invalid demand")

    achieved_energy_mu = float(transformed.sum() / 1000.0)
    achieved_peak_mw = float(transformed.max())
    if abs(achieved_energy_mu - float(annual_energy_mu)) > 1e-6:
        raise RuntimeError("future-load morphology missed annual-energy anchor")
    if abs(achieved_peak_mw - float(peak_mw)) > 1e-6:
        raise RuntimeError("future-load morphology missed peak anchor")

    return pd.Series(transformed, index=load_mw.index), {
        "source_mean_mw": source_mean,
        "source_peak_mw": source_peak,
        "target_mean_mw": target_mean,
        "target_peak_mw": float(peak_mw),
        "scale": float(scale),
        "offset_mw": float(offset),
        "achieved_energy_mu": achieved_energy_mu,
        "achieved_peak_mw": achieved_peak_mw,
    }


def _load_base(\n    root: Path, suite: dict[str, Any]\n) -> tuple[pd.DataFrame, dict[str, Any], dict]:
    proxy = json.loads((root / suite["base_chronology"]).read_text(encoding="utf-8"))
    qa = json.loads((root / suite["qa"]).read_text(encoding="utf-8"))
    daily = pd.read_csv(root / suite["base_daily_source_energy"])
    observed = json.loads(
        (root / suite["observed_capacity_reference"]).read_text(encoding="utf-8")
    )
    hourly, metadata = prepare_inputs(
        proxy,
        daily,
        expected_missing_dates=qa["missing_dates"],
    )
    return hourly, metadata, observed


def run_future_adequacy_suite(root: Path, *, hours: int = 8760) -> dict[str, Any]:
    """Run demand-anchor x transfer-bound adequacy counterfactuals."""
    if not 24 <= hours <= 8760 or hours % 24:
        raise ValueError("hours must be whole days between 24 and 8760")

    suite = load_future_adequacy_suite(
        root / "configs/full_pypsa_future_adequacy_v0_3.yaml"
    )
    hourly_base, metadata_base, observed = _load_base(root, suite)
    capacities = observed["electricity"]["capacity_mix_mw"]
    installed_hydro_mw = float(capacities["hydel"])
    installed_nonhydro_mw = float(
        observed["electricity"]["installed_capacity_mw"] - installed_hydro_mw
    )

    results: list[dict[str, Any]] = []
    for demand_case in suite["demand_cases"]:
        morphed, morph = morph_load_to_energy_and_peak(
            hourly_base["load_mw"],
            annual_energy_mu=float(demand_case["annual_energy_mu"]),
            peak_mw=float(demand_case["peak_mw"]),
        )
        hourly = hourly_base.copy()
        hourly["load_mw"] = morphed
        hourly = hourly.iloc[:hours].copy()
        metadata = {
            **metadata_base,
            "classification": (
                "scenario_screening_using_proxy_future_demand_counterfactual_"\n                "not_forecast_hourly_telemetry"
            ),
            "future_demand_case": demand_case["id"],
            "future_demand_source_family": demand_case["source_family"],
            "future_demand_source_year": demand_case["source_year"],
            "future_load_morphology": morph,
            "internal_generation_future_treatment": (
                "FY2024-25 daily-average source-energy replay frozen as counterfactual"
            ),
            "modeled_window_hours": hours,
        }

        for transfer_case in suite["transfer_cases"]:
            assumptions = ScreeningAssumptions(
                import_limit_mw=float(transfer_case["import_limit_mw"]),
                objective_import_per_mwh=float(suite["objective"]["import_per_mwh"]),
                objective_unserved_per_mwh=float(
                    suite["objective"]["unserved_per_mwh"]
                ),
            )
            network = build_hourly_screening_network(
                hourly,
                metadata,
                assumptions,
                installed_hydro_mw=installed_hydro_mw,
                installed_nonhydro_mw=installed_nonhydro_mw,
            )
            status, condition = solve_hourly_screening(network)
            summary = dispatch_summary(network, hourly, status, condition)
            unserved = network.generators_t.p["unserved_load"]
            imports = network.generators_t.p["screened_import"]
            results.append(
                {
                    "demand_case": demand_case["id"],
                    "source_family": demand_case["source_family"],
                    "source_year": demand_case["source_year"],
                    "target_annual_energy_mu": float(demand_case["annual_energy_mu"]),
                    "target_peak_mw": float(demand_case["peak_mw"]),
                    "morph_scale": morph["scale"],
                    "morph_offset_mw": morph["offset_mw"],
                    "transfer_case": transfer_case["id"],
                    "import_limit_mw": float(transfer_case["import_limit_mw"]),
                    "load_mwh_modelled_window": float(summary["load_mwh_proxy"]),
                    "imports_mwh_modelled": float(summary["imports_mwh_modelled"]),
                    "peak_import_mw_modelled": float(imports.max()),
                    "unserved_energy_mwh": float(summary["unserved_mwh_modelled"]),
                    "unserved_energy_pct": float(summary["unserved_pct_modelled"]),
                    "hours_with_unserved": int((unserved > 1e-6).sum()),
                    "max_unserved_mw": float(unserved.max()),
                    "solver_status": status,
                    "solver_condition": condition,
                }
            )

    return {
        "classification": SUITE_CLASS,
        "prepared_date": suite["prepared_date"],
        "hours": hours,
        "full_financial_year": hours == 8760,
        "future_hourly_demand_measured": False,
        "future_generation_forecast": False,
        "economic_dispatch": False,
        "capacity_expansion": False,
        "cases": results,
        "interpretation": [
            (
                "Published future annual-energy and peak anchors are imposed exactly, "
                "but the ordered hourly shape is a morphed FY2024-25 proxy."
            ),
            (
                "FY2024-25 internal generation is frozen as a deliberately harsh "
                "no-expansion counterfactual, not a forecast of future generation."
            ),
            (
                "Transfer limits are current/synthetic sensitivity bounds, not "\n                "committed "
                "2030-2040 import capability."
            ),
            (
                "Unserved energy identifies pressure on the frozen system; it does not "
                "state how much new capacity Kerala should build."
            ),
        ],
    }
