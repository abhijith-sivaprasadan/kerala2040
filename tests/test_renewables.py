import pandas as pd

from kerala2040.renewables import build_renewable_profiles


def test_weather_profiles_are_bounded_and_labelled():
    times = pd.date_range("2024-04-01", periods=3, freq="h", tz="UTC")
    weather = pd.DataFrame(
        {
            "timestamp_utc": list(times) * 2,
            "timestamp_ist": list(times.tz_convert("Asia/Kolkata")) * 2,
            "ghi_wh_m2": [0.0, 500.0, 1000.0] * 2,
            "temp_c": [25.0, 30.0, 35.0] * 2,
            "wind10_m_s": [0.0, 5.0, 15.0] * 2,
            "precip_mm_h": [0.0, 1.0, 0.0] * 2,
            "point": ["a"] * 3 + ["b"] * 3,
        }
    )
    profiles, summary = build_renewable_profiles(weather)

    assert len(profiles) == 3
    assert profiles["solar_p_max_pu"].between(0, 1).all()
    assert profiles["wind_p_max_pu"].between(0, 1).all()
    assert profiles["points_available"].eq(2).all()
    assert summary["classification"] == "modelled_resource_profile"
    assert "not measured" in summary["note"].lower()
    assert "NASA POWER" in summary["source"]
