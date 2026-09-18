"""Build an explicitly labelled hourly Kerala load proxy from daily SLDC energy.

This module does not create or claim measured hourly telemetry. It reconstructs an
8760-hour chronology for model calibration by preserving observed SLDC daily energy,
interpolating only missing daily totals, and fitting a simple two-peak intraday shape
against CEA's published FY2024-25 load-duration bins and peak reference.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class ProxyFit:
    afternoon_amplitude: float
    night_amplitude: float
    peak_mw: float
    objective: float
    duration_counts: tuple[int, ...]


def complete_daily_energy(
    daily: pd.DataFrame,
    *,
    start: str = "2024-04-01",
    end: str = "2025-03-31",
) -> pd.DataFrame:
    """Return one row per day, preserving observations and interpolating gaps.

    Interpolation is permitted only because the result is a proxy chronology. The
    daily_energy_imputed flag must remain attached to derived hourly data.
    """
    required = {"date", "consumption_mu"}
    missing = required.difference(daily.columns)
    if missing:
        raise ValueError(f"daily data missing required columns: {sorted(missing)}")

    work = daily.loc[:, ["date", "consumption_mu"]].copy()
    work["date"] = pd.to_datetime(work["date"]).dt.normalize()
    if work["date"].duplicated().any():
        raise ValueError("daily data contains duplicate dates")
    work = work.set_index("date").sort_index()

    index = pd.date_range(start, end, freq="D")
    work = work.reindex(index)
    work["daily_energy_imputed"] = work["consumption_mu"].isna()
    work["consumption_mu"] = work["consumption_mu"].interpolate(method="time")

    if work["consumption_mu"].isna().any():
        raise ValueError("daily energy has leading/trailing gaps that cannot be interpolated")
    if (work["consumption_mu"] <= 0).any():
        raise ValueError("daily consumption must be positive")

    work.index.name = "date"
    return work.reset_index()


def _circular_distance(hours: np.ndarray, centre: float) -> np.ndarray:
    distance = np.abs(hours - centre)
    return np.minimum(distance, 24.0 - distance)


def diurnal_shape(
    afternoon_amplitude: float,
    night_amplitude: float,
    *,
    afternoon_hour: float = 15.0,
    night_hour: float = 23.0,
    afternoon_width_h: float = 2.2,
    night_width_h: float = 1.8,
) -> np.ndarray:
    """Return a 24-hour mean-one shape with documented afternoon/night peaks."""
    hours = np.arange(24, dtype=float)
    afternoon = np.exp(
        -0.5 * (_circular_distance(hours, afternoon_hour) / afternoon_width_h) ** 2
    )
    night = np.exp(-0.5 * (_circular_distance(hours, night_hour) / night_width_h) ** 2)
    raw = 1.0 + afternoon_amplitude * afternoon + night_amplitude * night
    return raw / raw.mean()


def build_hourly_proxy(
    daily: pd.DataFrame,
    *,
    afternoon_amplitude: float,
    night_amplitude: float,
    timezone: str = "Asia/Kolkata",
) -> pd.DataFrame:
    """Expand daily energy to hourly MW while conserving every day's energy."""
    shape = diurnal_shape(afternoon_amplitude, night_amplitude)
    records: list[pd.DataFrame] = []

    for row in daily.itertuples(index=False):
        date = pd.Timestamp(row.date)
        timestamps = pd.date_range(date, periods=24, freq="h", tz=timezone)
        mean_mw = float(row.consumption_mu) * 1000.0 / 24.0
        records.append(
            pd.DataFrame(
                {
                    "timestamp": timestamps,
                    "load_mw": mean_mw * shape,
                    "daily_consumption_mu": float(row.consumption_mu),
                    "daily_energy_imputed": bool(row.daily_energy_imputed),
                    "classification": "proxy_reconstruction",
                }
            )
        )

    hourly = pd.concat(records, ignore_index=True)
    hourly["hour_local"] = hourly["timestamp"].dt.hour
    return hourly


def duration_counts(
    load_mw: pd.Series | np.ndarray,
    bins: list[dict[str, Any]],
) -> tuple[int, ...]:
    """Count proxy hours in the CEA load-duration bins."""
    values = np.asarray(load_mw, dtype=float)
    counts: list[int] = []
    for item in bins:
        low = float(item["min_mw"])
        high = float(item["max_mw"])
        counts.append(int(((values >= low) & (values < high)).sum()))
    return tuple(counts)


def fit_proxy_shape(
    daily: pd.DataFrame,
    *,
    bins: list[dict[str, Any]],
    target_peak_mw: float,
) -> ProxyFit:
    """Fit two amplitudes to CEA duration counts and peak without altering daily energy.

    The duration bins are approximate published validation constraints, so the objective
    deliberately avoids forcing an exact match that the source does not support.
    """
    target_counts = np.asarray([int(item["hours"]) for item in bins], dtype=float)
    total_hours = max(float(target_counts.sum()), 1.0)
    best: ProxyFit | None = None

    daily_mean_mw = daily["consumption_mu"].to_numpy(dtype=float) * 1000.0 / 24.0

    for afternoon_amp in np.linspace(0.0, 0.45, 46):
        for night_amp in np.linspace(0.0, 0.55, 56):
            shape = diurnal_shape(float(afternoon_amp), float(night_amp))
            values = (daily_mean_mw[:, None] * shape[None, :]).ravel()
            counts = np.asarray(duration_counts(values, bins), dtype=float)
            duration_rmse = float(
                np.sqrt(np.mean(((counts - target_counts) / total_hours) ** 2))
            )
            peak_mw = float(values.max())
            peak_error = (peak_mw - float(target_peak_mw)) / float(target_peak_mw)
            objective = duration_rmse**2 + 4.0 * peak_error**2

            candidate = ProxyFit(
                afternoon_amplitude=float(afternoon_amp),
                night_amplitude=float(night_amp),
                peak_mw=peak_mw,
                objective=objective,
                duration_counts=tuple(int(value) for value in counts),
            )
            if best is None or candidate.objective < best.objective:
                best = candidate

    if best is None:
        raise RuntimeError("proxy shape fit produced no candidates")
    return best


def proxy_summary(
    daily: pd.DataFrame,
    hourly: pd.DataFrame,
    fit: ProxyFit,
    *,
    bins: list[dict[str, Any]],
    cea_annual_energy_mu: float,
    cea_peak_mw: float,
) -> dict[str, Any]:
    """Create machine-readable provenance and validation diagnostics."""
    annual_energy_mu = float(hourly["load_mw"].sum() / 1000.0)
    imputed_dates = [
        pd.Timestamp(value).date().isoformat()
        for value in daily.loc[daily["daily_energy_imputed"], "date"]
    ]
    return {
        "classification": "proxy_reconstruction_not_measured_telemetry",
        "period": "FY2024-25",
        "timezone": "Asia/Kolkata",
        "resolution": "1h",
        "hours": int(len(hourly)),
        "daily_observations_measured": int((~daily["daily_energy_imputed"]).sum()),
        "daily_observations_interpolated": int(daily["daily_energy_imputed"].sum()),
        "interpolated_dates": imputed_dates,
        "annual_energy_mu": annual_energy_mu,
        "cea_reference_annual_energy_mu": float(cea_annual_energy_mu),
        "annual_energy_difference_pct": 100.0
        * (annual_energy_mu - float(cea_annual_energy_mu))
        / float(cea_annual_energy_mu),
        "peak_mw": float(hourly["load_mw"].max()),
        "cea_reference_peak_mw": float(cea_peak_mw),
        "peak_difference_pct": 100.0
        * (float(hourly["load_mw"].max()) - float(cea_peak_mw))
        / float(cea_peak_mw),
        "shape": {
            "afternoon_peak_hour_local": 15,
            "night_peak_hour_local": 23,
            "afternoon_amplitude": fit.afternoon_amplitude,
            "night_amplitude": fit.night_amplitude,
            "fit_objective": fit.objective,
        },
        "duration_bins": [
            {
                **item,
                "proxy_hours": proxy_count,
                "difference_hours": int(proxy_count) - item["hours"],
            }
            for item, proxy_count in zip(bins, fit.duration_counts, strict=True)
        ],
        "limitations": [
            "Hourly values are reconstructed, not measured Kerala SLDC/KSEBL telemetry.",
            "Eleven missing daily SLDC totals are time-interpolated and explicitly flagged.",
            "CEA frequency bins are published aggregate validation constraints, not an ordered hourly series.",
            "The two-peak intraday shape is a parsimonious calibration assumption, not direct metering evidence.",
        ],
    }
