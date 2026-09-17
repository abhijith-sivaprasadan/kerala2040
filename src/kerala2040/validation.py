"""Cross-source validation helpers.

These functions compare overlapping official datasets without assuming that differently
labelled accounting concepts must be identical.
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd


def compare_daily_energy(sldc: pd.DataFrame, grid_india: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Compare Kerala SLDC daily consumption with Grid-India daily energy met.

    The two series are retained under source-specific names. Differences are diagnostics,
    not corrections: source definitions can legitimately differ.
    """
    required_sldc = {"date", "consumption_mu"}
    required_grid = {"date", "energy_met_mu"}
    missing_sldc = sorted(required_sldc - set(sldc.columns))
    missing_grid = sorted(required_grid - set(grid_india.columns))
    if missing_sldc:
        raise ValueError(f"SLDC frame missing required columns: {missing_sldc}")
    if missing_grid:
        raise ValueError(f"Grid-India frame missing required columns: {missing_grid}")

    left = sldc[["date", "consumption_mu"]].copy()
    right = grid_india[["date", "energy_met_mu"]].copy()
    left["date"] = pd.to_datetime(left["date"]).dt.normalize()
    right["date"] = pd.to_datetime(right["date"]).dt.normalize()
    left["consumption_mu"] = pd.to_numeric(left["consumption_mu"], errors="coerce")
    right["energy_met_mu"] = pd.to_numeric(right["energy_met_mu"], errors="coerce")

    merged = left.merge(right, on="date", how="inner", validate="one_to_one").sort_values("date")
    merged["difference_mu"] = merged["consumption_mu"] - merged["energy_met_mu"]
    merged["absolute_difference_mu"] = merged["difference_mu"].abs()
    denominator = merged["consumption_mu"].where(merged["consumption_mu"] > 0)
    merged["difference_pct_of_sldc"] = 100.0 * merged["difference_mu"] / denominator
    merged["absolute_difference_pct_of_sldc"] = merged["difference_pct_of_sldc"].abs()

    valid = merged.dropna(subset=["consumption_mu", "energy_met_mu"])
    correlation = valid["consumption_mu"].corr(valid["energy_met_mu"]) if len(valid) >= 2 else np.nan
    summary: dict[str, Any] = {
        "overlap_days": len(merged),
        "valid_overlap_days": len(valid),
        "mean_difference_mu": float(valid["difference_mu"].mean()) if not valid.empty else None,
        "median_absolute_difference_mu": float(valid["absolute_difference_mu"].median()) if not valid.empty else None,
        "p95_absolute_difference_mu": float(valid["absolute_difference_mu"].quantile(0.95)) if not valid.empty else None,
        "median_absolute_difference_pct_of_sldc": float(valid["absolute_difference_pct_of_sldc"].median()) if not valid.empty else None,
        "correlation": float(correlation) if np.isfinite(correlation) else None,
        "interpretation": (
            "Diagnostic comparison only. Kerala SLDC 'consumption' and Grid-India MOP_E "
            "'energy met' are source-specific accounting concepts and are not forced to match."
        ),
    }
    return merged.reset_index(drop=True), summary


def monthly_energy_balance(frame: pd.DataFrame) -> pd.DataFrame:
    """Aggregate the validated SLDC daily balance to calendar months."""
    required = {"date", "consumption_mu", "internal_generation_mu", "net_import_interface_mu"}
    missing = sorted(required - set(frame.columns))
    if missing:
        raise ValueError(f"daily frame missing required columns: {missing}")
    data = frame.copy()
    data["date"] = pd.to_datetime(data["date"])
    data["month"] = data["date"].dt.to_period("M").dt.to_timestamp()
    result = (
        data.groupby("month", as_index=False)
        .agg(
            consumption_mu=("consumption_mu", "sum"),
            internal_generation_mu=("internal_generation_mu", "sum"),
            net_import_interface_mu=("net_import_interface_mu", "sum"),
            observed_days=("date", "nunique"),
        )
        .sort_values("month")
    )
    result["import_share"] = result["net_import_interface_mu"] / result["consumption_mu"]
    result["internal_share"] = result["internal_generation_mu"] / result["consumption_mu"]
    return result.reset_index(drop=True)
