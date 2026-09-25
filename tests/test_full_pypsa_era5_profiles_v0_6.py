"""QA for Full-PyPSA ERA5 renewable profile pipeline v0.6."""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import yaml

from kerala2040.era5_renewable_profiles import (
    _nearest_grid_index,
    build_era5_screening_profiles,
    load_profile_suite,
)

ROOT = Path(__file__).resolve().parents[1]


def test_v06_suite_stays_non_expansion():
    suite = load_profile_suite(
        ROOT / "configs/full_pypsa_era5_renewable_profiles_v0_6.yaml"
    )
    assert suite["release"]["source_to_screening_profiles_ready"] is True
    assert suite["release"]["capacity_expansion_ready"] is False
    assert suite["aggregation"]["capacity_weighted_profile"] == "blocked"


def test_nearest_grid_selection_handles_multicell_box():
    lat = np.array([12.0, 11.75])
    lon = np.array([75.25, 75.50])
    assert _nearest_grid_index(
        lat,
        lon,
        target_lat=11.8745,
        target_lon=75.3704,
    ) in {(0, 0), (1, 0), (0, 1), (1, 1)}
    i, j = _nearest_grid_index(
        lat,
        lon,
        target_lat=11.76,
        target_lon=75.49,
    )
    assert (i, j) == (1, 1)


def test_profile_build_is_bounded_and_diagnostic_only():
    times = pd.date_range("2024-04-01", periods=24, freq="h", tz="UTC")
    rows = []
    for point in ["thiruvananthapuram", "kochi", "palakkad", "kozhikode", "kannur"]:
        for hour, ts in enumerate(times):
            rows.append(
                {
                    "point": point,
                    "timestamp_utc": ts,
                    "timestamp_ist": ts.tz_convert("Asia/Kolkata"),
                    "temp_c": 28.0,
                    "wind10_m_s": 6.0,
                    "ghi_wh_m2": 700.0 if 6 <= hour <= 17 else 0.0,
                    "precip_mm_h": 0.0,
                    "era5_latitude": 10.0,
                    "era5_longitude": 76.0,
                }
            )
    weather = pd.DataFrame(rows)
    suite = yaml.safe_load(
        (ROOT / "configs/full_pypsa_era5_renewable_profiles_v0_6.yaml").read_text()
    )
    point_profiles, statewide, summary = build_era5_screening_profiles(weather, suite)
    assert len(point_profiles) == 120
    assert len(statewide) == 24
    for col in ["solar_p_max_pu", "wind_p_max_pu_150m_niwe_anchored"]:
        assert point_profiles[col].between(0, 1).all()
        assert statewide[col].between(0, 1).all()
    assert summary["model_admitted_for_capacity_expansion"] is False
    assert "diagnostic" in summary["validation_diagnostics"]["rule"].lower()
