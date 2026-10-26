"""Invented hourly panels only; no SLDC or original ERA5 observations in tests."""
from __future__ import annotations

import pandas as pd
import pytest

from kerala2040.multiyear_daily_study import audit_multiyear_weather_panel
from kerala2040.sources.era5 import POINTS


def _synthetic_panel() -> tuple[pd.DataFrame, pd.DataFrame]:
    # UTC whole-hour source instants map to 00:30..23:30 of a single IST day.
    utc_hours = pd.date_range(
        "2022-04-02 00:30", periods=24, freq="h", tz="Asia/Kolkata"
    ).tz_convert("UTC")
    rows = [
        {
            "point": point, "timestamp_utc": hour, "temp_c": 28.0,
            "wind10_m_s": 3.0, "ghi_wh_m2": 400.0, "precip_mm_h": 0.0
        }
        for point in POINTS for hour in utc_hours
    ]
    observed = pd.DataFrame({"date": pd.to_datetime(["2022-04-02"]),
                             "consumption_mu": [80.0]})
    return observed, pd.DataFrame(rows)


def test_exact_five_point_ist_day_passes_without_certifying_originals() -> None:
    observed, weather = _synthetic_panel()
    report = audit_multiyear_weather_panel(observed, weather)
    assert report["observed_target_ist_days"] == 1
    assert report["required_location_hours_verified"] == 120
    assert report["missing_or_duplicate_location_hours"] == 0
    assert report["original_era5_source_hashes_verified_here"] is False


def test_one_missing_location_hour_rejected_despite_other_four_point_values() -> None:
    observed, weather = _synthetic_panel()
    missing = weather.drop(index=0)
    with pytest.raises(ValueError, match="incomplete"):
        audit_multiyear_weather_panel(observed, missing)


def test_duplicate_location_hour_rejected_before_daily_averaging() -> None:
    observed, weather = _synthetic_panel()
    duplicated = pd.concat([weather, weather.iloc[[0]]], ignore_index=True)
    with pytest.raises(ValueError, match="Duplicate ERA5"):
        audit_multiyear_weather_panel(observed, duplicated)


def test_naive_or_off_grid_weather_instants_rejected() -> None:
    observed, weather = _synthetic_panel()
    no_zone = weather.copy()
    no_zone["timestamp_utc"] = no_zone["timestamp_utc"].dt.tz_localize(None)
    with pytest.raises(ValueError, match="explicit timezone"):
        audit_multiyear_weather_panel(observed, no_zone)

    off_grid = weather.copy()
    off_grid["timestamp_utc"] = off_grid["timestamp_utc"] + pd.Timedelta(minutes=30)
    with pytest.raises(ValueError, match="exact UTC hourly grid"):
        audit_multiyear_weather_panel(observed, off_grid)


def test_all_five_location_identities_required() -> None:
    observed, weather = _synthetic_panel()
    four_points = weather.loc[weather["point"] != "kannur"]
    with pytest.raises(ValueError, match="exact five"):
        audit_multiyear_weather_panel(observed, four_points)


def test_additional_observed_day_requires_independent_weather_coverage() -> None:
    observed, weather = _synthetic_panel()
    missing_second_day = pd.concat([
        observed, pd.DataFrame({"date": [pd.Timestamp("2022-04-03")],
                                "consumption_mu": [81.0]})
    ], ignore_index=True)
    with pytest.raises(ValueError, match="incomplete"):
        audit_multiyear_weather_panel(missing_second_day, weather)
