"""ERA5 source-artifact to renewable-profile pipeline for Full-PyPSA v0.6.

The source artifacts were independently byte/chronology checked before this module is
allowed to consume them. This module makes one additional explicit spatial choice:
for each representative location it selects the nearest returned ERA5 grid cell.
It then converts the verified variables to hourly weather and uses the repository's
existing transparent PV/wind proxy functions.

Outputs remain screening profiles, not measured generation or buildable capacity.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import h5py
import numpy as np
import pandas as pd
import yaml

from kerala2040.renewables import wind_p_max_pu
from kerala2040.sources.era5 import POINTS

SUITE_CLASS = "full_pypsa_era5_renewable_profile_screen_v0_6_not_expansion_admitted"
_REQUIRED_VARIABLES = {"t2m", "u10", "v10", "ssrd", "tp"}


def load_profile_suite(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if data.get("classification") != SUITE_CLASS:
        raise ValueError("ERA5 renewable profile suite classification mismatch")
    if data["spatial_sampling"]["method"] != "nearest_era5_grid_cell_to_representative_coordinate":
        raise ValueError("v0.6 spatial sampling method changed")
    expected = list(POINTS)
    if data["source_artifacts"]["expected_points"] != expected:
        raise ValueError("v0.6 representative point set changed")
    if data["release"]["capacity_expansion_ready"] is not False:
        raise ValueError("v0.6 must not release capacity expansion")
    return data


def _nearest_grid_index(
    latitudes: np.ndarray,
    longitudes: np.ndarray,
    *,
    target_lat: float,
    target_lon: float,
) -> tuple[int, int]:
    """Return nearest latitude/longitude indices using squared angular distance."""
    lat = np.asarray(latitudes, dtype=float)
    lon = np.asarray(longitudes, dtype=float)
    if lat.ndim != 1 or lon.ndim != 1 or not len(lat) or not len(lon):
        raise ValueError("ERA5 latitude/longitude coordinates must be non-empty 1D arrays")
    distances = (lat[:, None] - target_lat) ** 2 + (lon[None, :] - target_lon) ** 2
    flat = int(np.argmin(distances))
    return tuple(int(x) for x in np.unravel_index(flat, distances.shape))


def _read_component(
    path: Path,
    *,
    target_lat: float,
    target_lon: float,
) -> tuple[pd.DatetimeIndex, dict[str, np.ndarray], float, float]:
    with h5py.File(path, "r") as nc:
        times = pd.to_datetime(nc["valid_time"][:].astype(np.int64), unit="s", utc=True)
        latitudes = np.asarray(nc["latitude"][:], dtype=float)
        longitudes = np.asarray(nc["longitude"][:], dtype=float)
        lat_i, lon_i = _nearest_grid_index(
            latitudes,
            longitudes,
            target_lat=target_lat,
            target_lon=target_lon,
        )
        selected_lat = float(latitudes[lat_i])
        selected_lon = float(longitudes[lon_i])
        values: dict[str, np.ndarray] = {}
        for variable in _REQUIRED_VARIABLES.intersection(nc.keys()):
            field = np.asarray(nc[variable][:], dtype=float)
            if field.shape != (len(times), len(latitudes), len(longitudes)):
                raise ValueError(f"unexpected ERA5 shape for {variable}: {field.shape}")
            values[variable] = field[:, lat_i, lon_i]
    return times, values, selected_lat, selected_lon


def read_location_quarter(artifact_dir: Path) -> pd.DataFrame:
    """Read one independently verified location-quarter artifact directory."""
    manifest_path = artifact_dir / "retrieval_attempt.json"
    report = json.loads(manifest_path.read_text(encoding="utf-8"))
    points = report["selection"]["points"]
    periods = report["selection"]["periods"]
    if len(points) != 1 or len(periods) != 1:
        raise ValueError("artifact must contain exactly one representative point/quarter")
    point = points[0]
    if point not in POINTS:
        raise ValueError(f"unknown representative point {point!r}")
    target_lat, target_lon = POINTS[point]

    series_by_variable: dict[str, list[pd.Series]] = {
        variable: [] for variable in _REQUIRED_VARIABLES
    }
    selected_grids: set[tuple[float, float]] = set()

    for entry in report["files"]:
        source = artifact_dir / "source_files" / Path(entry["path"]).name
        times, values, selected_lat, selected_lon = _read_component(
            source,
            target_lat=target_lat,
            target_lon=target_lon,
        )
        selected_grids.add((selected_lat, selected_lon))
        for variable, array in values.items():
            series_by_variable[variable].append(
                pd.Series(array, index=times, name=variable)
            )

    missing = [name for name, items in series_by_variable.items() if not items]
    if missing:
        raise ValueError(f"incomplete ERA5 quarter variables: {sorted(missing)}")
    if len(selected_grids) != 1:
        raise ValueError("ERA5 source components selected different grid cells")

    assembled: dict[str, pd.Series] = {}
    for variable, items in series_by_variable.items():
        combined = pd.concat(items).sort_index()
        if combined.index.has_duplicates:
            raise ValueError(f"overlapping timestamps for ERA5 variable {variable}")
        assembled[variable] = combined

    by_time = pd.concat(assembled, axis=1, join="outer").sort_index()
    if by_time.isna().any().any():
        raise ValueError("ERA5 location-quarter variables do not share complete chronology")
    if by_time.index.has_duplicates:
        raise ValueError("duplicate timestamps after ERA5 quarter assembly")

    selected_lat, selected_lon = next(iter(selected_grids))
    by_time.index.name = "timestamp_utc"
    by_time = by_time.reset_index()
    by_time["point"] = point
    by_time["target_latitude"] = target_lat
    by_time["target_longitude"] = target_lon
    by_time["era5_latitude"] = selected_lat
    by_time["era5_longitude"] = selected_lon
    return by_time


def recover_full_year_weather(root: Path) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Read all 20 artifact directories and require 8,760 hours at each point."""
    manifests = sorted(root.rglob("retrieval_attempt.json"))
    if len(manifests) != 20:
        raise ValueError(f"expected 20 ERA5 location-quarter artifacts, found {len(manifests)}")
    chunks = [read_location_quarter(path.parent) for path in manifests]
    raw = pd.concat(chunks, ignore_index=True)
    raw["timestamp_utc"] = pd.to_datetime(raw["timestamp_utc"], utc=True)

    rows: list[pd.DataFrame] = []
    grid_selection: dict[str, dict[str, float]] = {}
    for point, frame in raw.groupby("point", sort=True):
        frame = frame.sort_values("timestamp_utc").reset_index(drop=True)
        if len(frame) != 8760 or frame["timestamp_utc"].duplicated().any():
            raise ValueError(f"FY2024-25 chronology incomplete for {point}")
        expected = pd.date_range(
            "2024-04-01T00:00:00Z",
            "2025-03-31T23:00:00Z",
            freq="h",
        )
        if not frame["timestamp_utc"].reset_index(drop=True).equals(pd.Series(expected)):
            raise ValueError(
                f"FY2024-25 timestamps do not match expected UTC chronology for {point}"
            )
        coordinates = frame[["era5_latitude", "era5_longitude"]].drop_duplicates()
        if len(coordinates) != 1:
            raise ValueError(f"selected ERA5 grid cell changed across quarters for {point}")
        grid_selection[point] = {
            "target_latitude": float(frame["target_latitude"].iloc[0]),
            "target_longitude": float(frame["target_longitude"].iloc[0]),
            "era5_latitude": float(frame["era5_latitude"].iloc[0]),
            "era5_longitude": float(frame["era5_longitude"].iloc[0]),
        }
        rows.append(frame)

    weather = pd.concat(rows, ignore_index=True)
    weather["temp_c"] = weather["t2m"] - 273.15
    weather["wind10_m_s"] = np.hypot(weather["u10"], weather["v10"])
    weather["ghi_wh_m2"] = weather["ssrd"].clip(lower=0.0) / 3600.0
    weather["precip_mm_h"] = weather["tp"].clip(lower=0.0) * 1000.0
    weather["timestamp_ist"] = weather["timestamp_utc"].dt.tz_convert("Asia/Kolkata")

    summary = {
        "classification": "verified_era5_source_converted_to_hourly_weather_not_generation",
        "points": len(grid_selection),
        "hours_per_point": 8760,
        "point_hours": len(weather),
        "spatial_method": "nearest_era5_grid_cell_to_representative_coordinate",
        "selected_grid_cells": grid_selection,
        "weather_conversions": {
            "temp_c": "t2m - 273.15",
            "wind10_m_s": "hypot(u10, v10)",
            "ghi_wh_m2": "max(ssrd,0) / 3600",
            "precip_mm_h": "max(tp,0) * 1000",
        },
    }
    return weather, summary


def build_era5_screening_profiles(
    weather: pd.DataFrame,
    suite: dict[str, Any],
) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    """Build point profiles plus an explicitly equal-weight statewide screening profile."""
    required = {"point", "timestamp_utc", "ghi_wh_m2", "temp_c", "wind10_m_s"}
    missing = required - set(weather)
    if missing:
        raise ValueError(f"ERA5 weather missing profile inputs: {sorted(missing)}")

    point_profiles = weather[
        [
            "point",
            "timestamp_utc",
            "timestamp_ist",
            "temp_c",
            "wind10_m_s",
            "ghi_wh_m2",
            "precip_mm_h",
            "era5_latitude",
            "era5_longitude",
        ]
    ].copy()
    solar_cfg = suite["profile_models"]["solar"]
    ghi = point_profiles["ghi_wh_m2"].to_numpy(dtype=float)
    ambient = point_profiles["temp_c"].to_numpy(dtype=float)
    cell_temp = ambient + float(
        solar_cfg["cell_temperature_rise_K_per_W_m2"]
    ) * ghi
    temp_factor = np.clip(
        1.0
        + float(solar_cfg["temperature_coefficient_per_K"])
        * (cell_temp - 25.0),
        0.0,
        1.5,
    )
    point_profiles["solar_p_max_pu"] = np.clip(
        ghi
        / 1000.0
        * float(solar_cfg["performance_ratio"])
        * temp_factor,
        0.0,
        1.0,
    )
    wind_cfg = suite["profile_models"]["wind"]
    alpha = float(wind_cfg["shear_exponent"])
    hub_height = float(wind_cfg["hub_height_m"])
    anchors = {
        point: float(value) for point, value in wind_cfg["NIWE_mean_150m_m_s"].items()
    }
    point_profiles["wind150_height_proxy_m_s"] = (
        point_profiles["wind10_m_s"] * (hub_height / 10.0) ** alpha
    )
    point_profiles["wind150_mean_anchored_m_s"] = np.nan
    point_profiles["wind_p_max_pu_150m_niwe_anchored"] = np.nan
    for point, indices in point_profiles.groupby("point").groups.items():
        if point not in anchors:
            raise ValueError(f"missing NIWE 150 m mean anchor for {point}")
        height_proxy = point_profiles.loc[indices, "wind150_height_proxy_m_s"]
        if float(height_proxy.mean()) <= 0:
            raise ValueError(f"non-positive ERA5 wind mean for {point}")
        anchored = height_proxy * anchors[point] / float(height_proxy.mean())
        point_profiles.loc[indices, "wind150_mean_anchored_m_s"] = anchored
        point_profiles.loc[indices, "wind_p_max_pu_150m_niwe_anchored"] = (
            wind_p_max_pu(
                anchored,
                hub_height_m=10.0,
                shear_exponent=0.0,
            ).to_numpy()
        )

    cols = ["solar_p_max_pu", "wind_p_max_pu_150m_niwe_anchored"]
    statewide = (
        point_profiles.groupby("timestamp_utc", as_index=False)[cols]
        .mean()
        .sort_values("timestamp_utc")
        .reset_index(drop=True)
    )
    statewide["timestamp_ist"] = statewide["timestamp_utc"].dt.tz_convert("Asia/Kolkata")
    statewide["points_available"] = len(POINTS)
    statewide["classification"] = "equal_weight_era5_representative_point_screening_profile"

    per_point = {}
    for point, frame in point_profiles.groupby("point", sort=True):
        per_point[point] = {
            "solar_specific_yield_proxy_kwh_per_kw_year": float(frame["solar_p_max_pu"].sum()),
            "wind_150m_NIWE_anchor_m_s": anchors[point],
            "wind_150m_anchored_capacity_factor_proxy": float(
                frame["wind_p_max_pu_150m_niwe_anchored"].mean()
            ),
            "wind_150m_anchored_full_load_hours_proxy": float(
                frame["wind_p_max_pu_150m_niwe_anchored"].sum()
            ),
        }

    solar_yield = float(statewide["solar_p_max_pu"].sum())
    gsa = float(
        suite["validation_anchors"]["gsa_statewide_median_annual_pvout_kwh_per_kwp"]
    )
    measured = suite["validation_anchors"]["measured_solar_generation"]
    measured_specific_yield = {
        name: float(item["fy2024_25_generation_mu"]) * 1000.0 / float(item["capacity_mw"])
        for name, item in measured.items()
    }
    regression_expected = suite["validation_anchors"][
        "prior_local_single_cell_regression_kwh_per_kw"
    ]
    regression = {
        point: {
            "expected_kwh_per_kw": float(expected),
            "v0_6_kwh_per_kw": float(
                per_point[point]["solar_specific_yield_proxy_kwh_per_kw_year"]
            ),
            "difference_kwh_per_kw": float(
                per_point[point]["solar_specific_yield_proxy_kwh_per_kw_year"]
                - float(expected)
            ),
        }
        for point, expected in regression_expected.items()
    }
    wind_regression_expected = suite["validation_anchors"]["prior_local_wind_proxy_flh"]
    wind_regression = {
        point: {
            "expected_flh": float(expected),
            "v0_6_flh": float(
                per_point[point]["wind_150m_anchored_full_load_hours_proxy"]
            ),
            "difference_flh": float(
                per_point[point]["wind_150m_anchored_full_load_hours_proxy"]
                - float(expected)
            ),
        }
        for point, expected in wind_regression_expected.items()
    }
    if len(statewide) == 8760:
        tolerance = suite["validation_anchors"]["full_year_regression_tolerance"]
        solar_max = max(abs(item["difference_kwh_per_kw"]) for item in regression.values())
        wind_max = max(abs(item["difference_flh"]) for item in wind_regression.values())
        if solar_max > float(tolerance["solar_kwh_per_kw"]):
            raise ValueError("full-year v0.6 PV regression exceeded tolerance")
        if wind_max > float(tolerance["wind_full_load_hours"]):
            raise ValueError("full-year v0.6 wind regression exceeded tolerance")

    summary = {
        "classification": SUITE_CLASS,
        "hours": len(statewide),
        "aggregation": "equal_weight_across_five_representative_points",
        "model_admitted_for_capacity_expansion": False,
        "statewide_screening": {
            "solar_specific_yield_proxy_kwh_per_kw_year": solar_yield,
            "solar_capacity_factor_proxy": float(statewide["solar_p_max_pu"].mean()),
            "wind_150m_NIWE_anchored_capacity_factor_proxy": float(
                statewide["wind_p_max_pu_150m_niwe_anchored"].mean()
            ),
        },
        "per_point": per_point,
        "validation_diagnostics": {
            "gsa_statewide_median_annual_pvout_kwh_per_kwp": gsa,
            "era5_proxy_minus_gsa_pct": 100.0 * (solar_yield - gsa) / gsa,
            "measured_specific_yield_kwh_per_kw": measured_specific_yield,
            "prior_local_single_cell_regression": regression,
            "prior_local_wind_proxy_regression": wind_regression,
            "rule": "diagnostic comparison only; no profile calibration or force-fit",
        },
        "limitations": [
            "Five representative points are not a statewide capacity-weighted fleet.",
            "PV proxy has no tilt/azimuth/inverter/soiling model.",
            "Wind shape is mean-anchored to NIWE 150 m atlas values, not measured turbine yield.",
            "No legal/ecological/grid buildable-capacity ceiling is applied.",
            "Measured solar anchors are annual energy only and cannot validate hourly shape.",
        ],
    }
    return point_profiles, statewide, summary
