"""Explicitly published 2040 demand references on an *unmeasured* FY2024-25 shape.

This module deliberately does NOT forecast hourly demand, validate Kerala's
future grid, supply techno-economic inputs or choose an optimal generation mix.
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from kerala2040.chronological_screen import PROXY_CLASS

REFERENCE_CLASS = "published_external_scenario"
RESULT_CLASS = "scenario_screening_using_proxy_2040_reference_not_hourly_forecast"


def demand_references(
    cstep_demand: pd.DataFrame,
    published: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    """Keep CSTEP and CN50 published values distinct; never blend scopes."""
    required = {
        "financial_year", "published_final_demand_with_td_losses_mu", "classification"
    }
    if not required.issubset(cstep_demand):
        raise ValueError("CSTEP demand file missing source fields")
    year = cstep_demand.loc[cstep_demand.financial_year == 2040]
    if len(year) != 1 or year.iloc[0]["classification"] != REFERENCE_CLASS:
        raise ValueError("Require one published CSTEP FY2040 row")
    cstep = float(year.iloc[0]["published_final_demand_with_td_losses_mu"])
    refs = published["references"]
    cstep_ref = refs["cstep_2024"]
    if not np.isclose(cstep, cstep_ref["fy2040"]["final_demand_with_td_losses_mu"]):
        raise ValueError("CSTEP CSV and published-reference registry disagree")
    cn_ref = refs["kerala_cn50_2026"]
    demand = cn_ref["net_grid_demand_twh"]
    cases = {
        "cstep_2024_bau": {
            "target_mu": cstep,
            "publisher": cstep_ref["publisher"],
            "source_url": cstep_ref["primary_url"],
            "source_id": "cstep_2024",
            "boundary": "CSTEP final demand with reported T&D losses, FY2040",
        },
        "cn50_2026_bau": {
            "target_mu": float(demand["bau_2040"]) * 1000,
            "publisher": cn_ref["publisher"],
            "source_url": cn_ref["primary_url"],
            "source_id": "kerala_cn50_2026",
            "boundary": "CN50 BAU net grid demand in 2040",
        },
        "cn50_2026_transition": {
            "target_mu": float(demand["cn50_2040"]) * 1000,
            "publisher": cn_ref["publisher"],
            "source_url": cn_ref["primary_url"],
            "source_id": "kerala_cn50_2026",
            "boundary": "CN50 transition-case net grid demand in 2040",
        },
    }
    for key, case in cases.items():
        if not np.isfinite(case["target_mu"]) or case["target_mu"] <= 0:
            raise ValueError(f"Invalid published demand for {key}")
        case["classification"] = REFERENCE_CLASS
        case["model_year"] = 2040
        case["scope_warning"] = (
            "CSTEP final demand with losses and CN50 net grid demand have different "
            "study boundaries; treat as separate cases, NOT matched forecasts."
        )
    return cases


def scale_reference_load(
    historical_hourly: pd.DataFrame,
    historical_meta: dict[str, Any],
    case: dict[str, Any],
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Reuse hourly shape and 11 missing-day flags without claiming measured hours.

    The 8760 source snapshots remain dated FY2024-25: they represent a
    *weather/shape year* used for the 2040 experiment, not a 2040 calendar.
    This is important because chronological fiscal years can include leap days.
    """
    if historical_meta.get("load_classification") != PROXY_CLASS:
        raise ValueError("Historical load must be classified as reconstructed proxy")
    if historical_meta.get("observed_days") != 354 or historical_meta.get("imputed_days") != 11:
        raise ValueError("Missing-day evidence must be preserved")
    if len(historical_hourly) != 8760 or historical_hourly.snapshot_ist_naive.duplicated().any():
        raise ValueError("Require full 8760-hour shape before sampling any shorter window")
    if case.get("classification") != REFERENCE_CLASS or case.get("model_year") != 2040:
        raise ValueError("2040 demand must use an explicitly published reference case")
    source_load = historical_hourly.load_mw.to_numpy(dtype=float)
    if not np.isfinite(source_load).all() or (source_load <= 0).any():
        raise ValueError("Invalid source load proxy")
    source_mwh = float(source_load.sum())
    target_mwh = float(case["target_mu"]) * 1000
    if not np.isfinite(target_mwh) or target_mwh <= 0:
        raise ValueError("Invalid published annual demand")
    factor = target_mwh / source_mwh
    scaled = historical_hourly.copy()
    scaled["historical_load_proxy_mw"] = source_load
    scaled["load_mw"] = source_load * factor
    if not np.isclose(scaled.load_mw.sum(), target_mwh, rtol=0, atol=1e-5):
        raise RuntimeError("Annual demand reference is not conserved")
    meta = {
        **historical_meta,
        "classification": RESULT_CLASS,
        "period": "FY2024-25 representative chronology rescaled for 2040 sensitivity",
        "model_year": 2040,
        "shape_year": "FY2024-25; NOT measured hourly or a future-year forecast",
        "published_demand_reference": case,
        "historical_shape_energy_mwh_proxy": source_mwh,
        "full_year_2040_reference_mwh": target_mwh,
        "annual_shape_scale_factor": factor,
        "historical_generation_assumption": (
            "FY2024-25 SLDC daily hydro/nonhydro generation fixed at daily-average MW, "
            "including model-only interpolation on 11 missing days. NOT 2040 plant dispatch."
        ),
        "import_rating_assumption": (
            "User-configured screening bound; NOT independently verified Kerala ATC/TTC."
        ),
        "cost_optimal_2040_result": False,
        "measured_hourly_telemetry_used": False,
    }
    return scaled, meta
