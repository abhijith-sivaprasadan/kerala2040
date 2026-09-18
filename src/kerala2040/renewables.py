"""Weather-derived renewable availability profiles for model development."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

_REQUIRED = {"timestamp_utc", "timestamp_ist", "ghi_wh_m2", "temp_c", "wind10_m_s"}


def solar_p_max_pu(
    ghi_wh_m2: pd.Series,
    temp_c: pd.Series,
    *,
    temperature_coefficient_per_c: float = -0.004,
    noct_delta_c_at_1000w_m2: float = 30.0,
) -> pd.Series:
    """Simple PV availability proxy from hourly GHI and ambient temperature."""
    ghi = pd.to_numeric(ghi_wh_m2, errors="coerce").clip(lower=0.0)
    ambient = pd.to_numeric(temp_c, errors="coerce")
    cell_temp = ambient + noct_delta_c_at_1000w_m2 * (ghi / 1000.0)
    temperature_factor = 1.0 + temperature_coefficient_per_c * (cell_temp - 25.0)
    profile = (ghi / 1000.0) * temperature_factor.clip(lower=0.0)
    return profile.clip(lower=0.0, upper=1.0)


def wind_p_max_pu(
    wind10_m_s: pd.Series,
    *,
    hub_height_m: float = 100.0,
    shear_exponent: float = 0.14,
    cut_in_m_s: float = 3.0,
    rated_m_s: float = 12.0,
    cut_out_m_s: float = 25.0,
) -> pd.Series:
    """Generic turbine availability proxy; not a site-specific power curve."""
    wind10 = pd.to_numeric(wind10_m_s, errors="coerce").clip(lower=0.0)
    hub = wind10 * (hub_height_m / 10.0) ** shear_exponent
    values = np.zeros(len(hub), dtype=float)
    wind = hub.to_numpy(dtype=float)

    ramp = (wind >= cut_in_m_s) & (wind < rated_m_s)
    values[ramp] = (
        (wind[ramp] ** 3 - cut_in_m_s**3)
        / (rated_m_s**3 - cut_in_m_s**3)
    )
    rated = (wind >= rated_m_s) & (wind < cut_out_m_s)
    values[rated] = 1.0
    values[~np.isfinite(wind)] = np.nan
    return pd.Series(values, index=wind10.index, dtype="float64")


def build_renewable_profiles(weather: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Build equal-weight representative-point solar/wind profiles."""
    missing = sorted(_REQUIRED - set(weather.columns))
    if missing:
        raise ValueError(f"weather data missing required columns: {missing}")
    work = weather.copy()
    work["timestamp_utc"] = pd.to_datetime(work["timestamp_utc"], utc=True)
    work["timestamp_ist"] = pd.to_datetime(work["timestamp_ist"])
    work["solar_p_max_pu"] = solar_p_max_pu(work["ghi_wh_m2"], work["temp_c"])
    work["wind_p_max_pu"] = wind_p_max_pu(work["wind10_m_s"])

    numeric = [
        "solar_p_max_pu",
        "wind_p_max_pu",
        "temp_c",
        "wind10_m_s",
    ]
    if "precip_mm_h" in work:
        numeric.append("precip_mm_h")
    if "ghi_wh_m2" in work:
        numeric.append("ghi_wh_m2")

    grouped = work.groupby("timestamp_utc", as_index=False)[numeric].mean()
    grouped["timestamp_ist"] = grouped["timestamp_utc"].dt.tz_convert("Asia/Kolkata")
    counts = work.groupby("timestamp_utc").size().rename("points_available")
    grouped = grouped.merge(counts, on="timestamp_utc", how="left")
    grouped["classification"] = "proxy"
    grouped["source_type"] = "weather_derived_resource_profile"
    grouped["source"] = "NASA POWER representative-point hourly weather"

    summary = {
        "classification": "proxy",
        "source_type": "weather_derived_resource_profile",
        "source": "NASA POWER representative-point hourly weather",
        "source_components": [
            {
                "classification": "reanalysis",
                "source_type": "reanalysis_remote_sensing",
                "source": "NASA POWER representative-point hourly weather",
            }
        ],
        "note": "Proxy renewable availability; not measured Kerala solar or wind generation.",
        "hours": len(grouped),
        "period_start_utc": (
            grouped["timestamp_utc"].min().isoformat() if not grouped.empty else None
        ),
        "period_end_utc": (
            grouped["timestamp_utc"].max().isoformat() if not grouped.empty else None
        ),
        "solar_mean_p_max_pu": float(grouped["solar_p_max_pu"].mean()),
        "wind_mean_p_max_pu": float(grouped["wind_p_max_pu"].mean()),
        "points_available_min": int(grouped["points_available"].min()),
        "points_available_max": int(grouped["points_available"].max()),
        "assumptions": {
            "spatial_weighting": "equal_weight_across_available_representative_points",
            "pv_temperature_coefficient_per_c": -0.004,
            "pv_noct_delta_c_at_1000w_m2": 30.0,
            "wind_hub_height_m": 100.0,
            "wind_shear_exponent": 0.14,
            "wind_cut_in_m_s": 3.0,
            "wind_rated_m_s": 12.0,
            "wind_cut_out_m_s": 25.0,
        },
        "limitations": [
            "Profiles are modelled resource availability, not measured Kerala plant generation.",
            "Representative points are equally weighted and are not a GIS capacity-weighted fleet model.",
            "Wind uses a generic cubic power curve and power-law shear assumption.",
            "PV uses a simple GHI/temperature derate rather than a plant-specific tilt/inverter model.",
            "ERA5 can be used as a later cross-check once full FY2024-25 coverage is acquired.",
        ],
    }
    return grouped, summary
