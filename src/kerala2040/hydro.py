"""Hydro-system diagnostics built only from observed/reanalysis inputs."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

_REQUIRED_DAILY = {
    "date",
    "hydel_total_mu",
    "net_import_interface_mu",
    "consumption_mu",
}
_REQUIRED_STORAGE = {
    "date",
    "generation_capability_gross_mu",
    "storage_pct_energy_weighted",
    "inflow_mu",
}


def kerala_season(month: int) -> str:
    """Return a transparent Kerala seasonal grouping used only for diagnostics."""
    if month in {6, 7, 8, 9}:
        return "southwest_monsoon"
    if month in {10, 11}:
        return "post_monsoon"
    return "dry_intermonsoon"


def _weather_daily(weather: pd.DataFrame) -> pd.DataFrame:
    if weather.empty:
        return pd.DataFrame(columns=["date"])
    if "timestamp_ist" not in weather:
        raise ValueError("weather data require timestamp_ist")

    work = weather.copy()
    work["timestamp_ist"] = pd.to_datetime(work["timestamp_ist"])
    work["date"] = work["timestamp_ist"].dt.tz_localize(None).dt.normalize()

    point_keys = ["date"]
    if "point" in work:
        point_keys.append("point")

    aggregations: dict[str, str] = {}
    for column in ["temp_c", "rh_pct", "wind10_m_s"]:
        if column in work:
            aggregations[column] = "mean"
    for column in ["ghi_wh_m2", "precip_mm_h"]:
        if column in work:
            aggregations[column] = "sum"
    if not aggregations:
        return work[["date"]].drop_duplicates()

    point_daily = work.groupby(point_keys, as_index=False).agg(aggregations)
    rename = {
        "temp_c": "temp_c_mean",
        "rh_pct": "rh_pct_mean",
        "wind10_m_s": "wind10_m_s_mean",
        "ghi_wh_m2": "ghi_wh_m2_day_mean",
        "precip_mm_h": "precip_mm_day_mean",
    }
    point_daily = point_daily.rename(columns=rename)
    numeric = [column for column in point_daily.columns if column not in point_keys]
    return point_daily.groupby("date", as_index=False)[numeric].mean()


def build_hydro_daily(
    daily: pd.DataFrame,
    storage: pd.DataFrame,
    weather: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """Join daily power balance, reservoir state and optional weather."""
    missing_daily = sorted(_REQUIRED_DAILY - set(daily.columns))
    missing_storage = sorted(_REQUIRED_STORAGE - set(storage.columns))
    if missing_daily:
        raise ValueError(f"daily balance missing required columns: {missing_daily}")
    if missing_storage:
        raise ValueError(f"storage data missing required columns: {missing_storage}")

    power = daily.copy()
    reservoirs = storage.copy()
    power["date"] = pd.to_datetime(power["date"]).dt.normalize()
    reservoirs["date"] = pd.to_datetime(reservoirs["date"]).dt.normalize()

    result = power.merge(
        reservoirs[
            [
                "date",
                "generation_capability_gross_mu",
                "storage_pct_energy_weighted",
                "inflow_mu",
            ]
        ],
        on="date",
        how="inner",
        validate="one_to_one",
    )
    if weather is not None and not weather.empty:
        result = result.merge(_weather_daily(weather), on="date", how="left")

    result["season"] = result["date"].dt.month.map(kerala_season)
    result["hydro_avg_mw"] = pd.to_numeric(result["hydel_total_mu"]) * 1000.0 / 24.0
    result["imports_avg_mw"] = (
        pd.to_numeric(result["net_import_interface_mu"]) * 1000.0 / 24.0
    )
    result["hydro_share"] = (
        pd.to_numeric(result["hydel_total_mu"])
        / pd.to_numeric(result["consumption_mu"]).replace(0, np.nan)
    )
    return result.sort_values("date").reset_index(drop=True)


def _correlation(frame: pd.DataFrame, left: str, right: str) -> float | None:
    if left not in frame or right not in frame:
        return None
    pair = frame[[left, right]].apply(pd.to_numeric, errors="coerce").dropna()
    if len(pair) < 3 or pair[left].nunique() < 2 or pair[right].nunique() < 2:
        return None
    return float(pair.corr().iloc[0, 1])


def hydro_operating_envelope(frame: pd.DataFrame) -> list[dict[str, Any]]:
    """Summarise observed hydro output conditional on reservoir storage bands."""
    if frame.empty:
        return []
    work = frame[["storage_pct_energy_weighted", "hydel_total_mu"]].dropna().copy()
    if work.empty:
        return []

    bins = [-np.inf, 20, 40, 60, 80, np.inf]
    labels = ["<=20", "20-40", "40-60", "60-80", ">80"]
    work["storage_band_pct"] = pd.cut(
        work["storage_pct_energy_weighted"],
        bins=bins,
        labels=labels,
        include_lowest=True,
    )
    records: list[dict[str, Any]] = []
    for label, group in work.groupby("storage_band_pct", observed=True):
        values = group["hydel_total_mu"]
        records.append(
            {
                "storage_band_pct": str(label),
                "days": int(len(group)),
                "hydro_mu_q10": float(values.quantile(0.10)),
                "hydro_mu_median": float(values.median()),
                "hydro_mu_q90": float(values.quantile(0.90)),
            }
        )
    return records


def summarise_hydro(frame: pd.DataFrame) -> dict[str, Any]:
    """Create empirical hydro/import/storage diagnostics without causal claims."""
    seasonal: dict[str, dict[str, float | int]] = {}
    for season, group in frame.groupby("season"):
        seasonal[str(season)] = {
            "days": int(len(group)),
            "hydro_mu_mean": float(group["hydel_total_mu"].mean()),
            "hydro_mu_median": float(group["hydel_total_mu"].median()),
            "net_import_mu_mean": float(group["net_import_interface_mu"].mean()),
            "storage_pct_mean": float(group["storage_pct_energy_weighted"].mean()),
            "inflow_mu_mean": float(group["inflow_mu"].mean()),
        }

    correlations = {
        "hydro_vs_storage_pct": _correlation(
            frame, "hydel_total_mu", "storage_pct_energy_weighted"
        ),
        "hydro_vs_inflow": _correlation(frame, "hydel_total_mu", "inflow_mu"),
        "imports_vs_hydro": _correlation(
            frame, "net_import_interface_mu", "hydel_total_mu"
        ),
    }
    if "precip_mm_day_mean" in frame:
        correlations["hydro_vs_precipitation"] = _correlation(
            frame, "hydel_total_mu", "precip_mm_day_mean"
        )

    return {
        "classification": "derived_from_observed_daily_hydro_storage_and_weather",
        "causal_interpretation": False,
        "days": int(len(frame)),
        "period_start": frame["date"].min().date().isoformat() if not frame.empty else None,
        "period_end": frame["date"].max().date().isoformat() if not frame.empty else None,
        "correlations": correlations,
        "seasonal": seasonal,
        "operating_envelope": hydro_operating_envelope(frame),
        "limitations": [
            "Correlations describe observed co-movement and do not establish dispatch causality.",
            "System reservoir storage is an energy-weighted aggregate across reported reservoirs.",
            "Weather is representative-point reanalysis/remote-sensing input when supplied.",
            "Missing SLDC archive dates are not interpolated in this hydro analysis.",
        ],
    }
