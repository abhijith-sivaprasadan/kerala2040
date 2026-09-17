import math

from kerala2040.sources.nasa_power import parse_hourly_payload


def test_power_parser_timestamps_units_and_fill_value():
    payload = {
        "properties": {
            "parameter": {
                "T2M": {"2025040100": 27.05, "2025040101": 27.32},
                "ALLSKY_SFC_SW_DWN": {"2025040100": -999.0, "2025040101": 58.0},
            }
        },
        "header": {
            "fill_value": -999.0,
            "time_standard": "UTC",
            "start": "20250401",
            "end": "20250401",
            "api": {"version": "test"},
        },
        "parameters": {
            "T2M": {"units": "C"},
            "ALLSKY_SFC_SW_DWN": {"units": "Wh/m^2"},
        },
    }
    frame, meta = parse_hourly_payload(payload)
    assert len(frame) == 2
    assert str(frame.loc[0, "timestamp_utc"].tzinfo) == "UTC"
    assert str(frame.loc[0, "timestamp_ist"].tzinfo) == "Asia/Kolkata"
    assert math.isnan(frame.loc[0, "ghi_wh_m2"])
    assert frame.loc[1, "ghi_wh_m2"] == 58.0
    assert meta["time_standard"] == "UTC"
