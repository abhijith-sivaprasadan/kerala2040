"""Historical-baseline diagnostics for Kerala electricity data."""

from __future__ import annotations

from datetime import date
from typing import Any

import numpy as np
import pandas as pd

_REQUIRED_DAILY_COLUMNS = {
    "date",
    "internal_generation_mu",
    "net_import_interface_mu",
    "consumption_mu",
    "balance_error_mu",
}


def add_daily_indicators(frame: pd.DataFrame) -> pd.DataFrame:
    """Add transparent daily shares without inventing missing components."""
    missing = sorted(_REQUIRED_DAILY_COLUMNS - set(frame.columns))
    if missing:
        raise ValueError(f"daily baseline missing required columns: {missing}")

    result = frame.copy()
    result["date"] = pd.to_datetime(result["date"]).dt.normalize()
    consumption = pd.to_numeric(result["consumption_mu"], errors="coerce")
    valid = consumption.where(consumption > 0)
    result["import_share"] = pd.to_numeric(
        result["net_import_interface_mu"], errors="coerce"
    ) / valid
    result["internal_share"] = pd.to_numeric(
        result["internal_generation_mu"], errors="coerce"
    ) / valid

    if "hydel_total_mu" in result:
        result["hydro_share_consumption"] = pd.to_numeric(
            result["hydel_total_mu"], errors="coerce"
        ) / valid
    return result.sort_values("date").reset_index(drop=True)


def summarise_daily_baseline(
    frame: pd.DataFrame,
    *,
    expected_start: date | str | None = None,
    expected_end: date | str | None = None,
    minimum_coverage: float = 0.95,
    balance_tolerance_mu: float = 0.05,
) -> dict[str, Any]:
    """Summarise coverage and energy balance for a historical calibration gate."""
    data = add_daily_indicators(frame)
    if data.empty:
        raise ValueError("daily baseline is empty")

    duplicate_days = int(data["date"].duplicated().sum())
    observed_start = data["date"].min().normalize()
    observed_end = data["date"].max().normalize()
    target_start = pd.Timestamp(expected_start).normalize() if expected_start else observed_start
    target_end = pd.Timestamp(expected_end).normalize() if expected_end else observed_end
    if target_end < target_start:
        raise ValueError("expected_end must be on or after expected_start")

    if not 0 < minimum_coverage <= 1 or balance_tolerance_mu < 0:
        raise ValueError("Coverage must be in (0, 1] and balance tolerance nonnegative")
    outside = ~data["date"].between(target_start, target_end)
    if outside.any():
        raise ValueError("Daily evidence contains invalid or out-of-period dates")
    numeric = data[["consumption_mu", "internal_generation_mu", "net_import_interface_mu"]].apply(
        pd.to_numeric, errors="coerce"
    )
    invalid_rows = ~np.isfinite(numeric).all(axis=1) | (numeric["consumption_mu"] <= 0)
    # Recompute the identity; a stale parser-provided error must not pass the gate.
    calculated_balance = (
        numeric["internal_generation_mu"] + numeric["net_import_interface_mu"]
        - numeric["consumption_mu"]
    ).abs()

    expected_index = pd.date_range(target_start, target_end, freq="D")
    observed_index = pd.DatetimeIndex(data["date"].dropna().unique())
    missing_days = expected_index.difference(observed_index)
    coverage = len(observed_index.intersection(expected_index)) / len(expected_index)

    consumption_mu = pd.to_numeric(data["consumption_mu"], errors="coerce").sum(min_count=1)
    internal_mu = pd.to_numeric(data["internal_generation_mu"], errors="coerce").sum(min_count=1)
    imports_mu = pd.to_numeric(data["net_import_interface_mu"], errors="coerce").sum(min_count=1)
    balance = pd.to_numeric(data["balance_error_mu"], errors="coerce").abs()
    invalid_rows |= ~np.isfinite(balance)
    balance = pd.concat([balance, calculated_balance], axis=1).max(axis=1)
    max_balance_error = float(balance.max()) if balance.notna().any() else float("nan")

    summary: dict[str, Any] = {
        "observed_start": observed_start.date().isoformat(),
        "observed_end": observed_end.date().isoformat(),
        "expected_start": target_start.date().isoformat(),
        "expected_end": target_end.date().isoformat(),
        "rows": len(data),
        "expected_days": len(expected_index),
        "coverage_fraction": float(coverage),
        "missing_days_count": len(missing_days),
        "missing_days": [stamp.date().isoformat() for stamp in missing_days],
        "duplicate_days": duplicate_days,
        "invalid_rows": int(invalid_rows.sum()),
        "gate_scope": "daily_coverage_and_accounting_only",
        "hourly_model_calibrated": False,
        "aggregation_scope": "observed_days_only",
        "consumption_twh": float(consumption_mu / 1000.0),
        "internal_generation_twh": float(internal_mu / 1000.0),
        "net_import_twh": float(imports_mu / 1000.0),
        "aggregate_import_share": float(imports_mu / consumption_mu),
        "aggregate_internal_share": float(internal_mu / consumption_mu),
        "daily_import_share_median": float(data["import_share"].median()),
        "daily_import_share_p95": float(data["import_share"].quantile(0.95)),
        "max_abs_balance_error_mu": max_balance_error,
        "balance_tolerance_mu": float(balance_tolerance_mu),
        "minimum_coverage": float(minimum_coverage),
    }

    if "hydel_total_mu" in data:
        hydro_mu = pd.to_numeric(data["hydel_total_mu"], errors="coerce").sum(min_count=1)
        summary["hydro_generation_twh"] = float(hydro_mu / 1000.0)
        summary["hydro_share_consumption"] = float(hydro_mu / consumption_mu)
        summary["hydro_share_internal_generation"] = float(hydro_mu / internal_mu)

    finite_balance = np.isfinite(max_balance_error)
    summary["calibration_gate_pass"] = bool(
        coverage >= minimum_coverage
        and duplicate_days == 0
        and not invalid_rows.any()
        and finite_balance
        and max_balance_error <= balance_tolerance_mu
    )
    return summary
