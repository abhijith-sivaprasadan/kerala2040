"""Synthetic-only regression tests: no claim that actual ERA5 or basin geometry arrived."""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "analysis"))
from idukki_phase5_weather import compare_models, ingest_hourly, load_weights


def weights_file(tmp_path: Path, support="IDUKKI_RESERVOIR_INTERCEPTED_CATCHMENT"):
    file = tmp_path / "weights.csv"
    pd.DataFrame([
        {"latitude": 9.5, "longitude": 77.0, "weight": .25},
        {"latitude": 9.6, "longitude": 77.1, "weight": .75},
    ]).assign(source_id="synthetic_not_actual_geometry",
             spatial_support=support,
             geometry_sha256=hashlib.sha256(b"synthetic polygon").hexdigest()
             ).to_csv(file, index=False)
    return file


def hours():
    # ERA5-Land 00 UTC is previous day's step24, 01 UTC is current step1.
    utc = pd.date_range("2017-12-31T17:00:00Z", "2018-01-02T00:00:00Z", freq="h")
    rows = []
    for lat, lon in ((9.5, 77.0), (9.6, 77.1)):
        for t in utc:
            step = t.hour or 24
            # One millimetre per accumulated forecast hour, kelvin source.
            rows.append({"valid_time_utc": t.strftime("%Y-%m-%dT%H:%M:%SZ"),
                         "latitude": lat, "longitude": lon,
                         "tp_accum_m": step / 1000, "t2m_k": 300.0})
    return pd.DataFrame(rows)


def test_ist_deaccumulation_midnight_and_two_pixel_weights(tmp_path):
    w, _ = load_weights(weights_file(tmp_path))
    inp = tmp_path / "hourly.csv"
    hours().to_csv(inp, index=False)
    daily, qa = ingest_hourly(inp, w, "2018-01-01", "2018-01-01")
    assert qa["complete_basin_rain_days"] == 1
    assert daily.rainfall_mm.iloc[0] == pytest.approx(24.0)
    assert daily.t2m_c.iloc[0] == pytest.approx(26.85)
    assert daily.rain_pixels_complete.iloc[0] == 2


def test_missing_hour_invalidates_entire_ist_day_not_zero(tmp_path):
    w, _ = load_weights(weights_file(tmp_path))
    inp = tmp_path / "hourly.csv"
    h = hours()
    h = h.loc[~((h.latitude == 9.5)
                & (h.valid_time_utc == "2018-01-01T00:00:00Z"))]
    h.to_csv(inp, index=False)
    daily, qa = ingest_hourly(inp, w, "2018-01-01", "2018-01-01")
    assert qa["complete_basin_rain_days"] == 0
    assert np.isnan(daily.rainfall_mm.iloc[0])
    assert daily.rain_pixels_complete.iloc[0] == 1



def test_midnight_straddling_hour_split_half_to_each_ist_day(tmp_path):
    weights, _ = load_weights(weights_file(tmp_path))
    h = hours()
    # Add ten extra millimetres to UTC hour ENDING Jan-01 19:00,
    # i.e. local Jan-02 00:30. Exactly half belongs to Jan-01.
    t = pd.to_datetime(h.valid_time_utc, utc=True)
    later = ((t.dt.date == pd.Timestamp("2018-01-01").date())
             & (t.dt.hour >= 19)) | (t == pd.Timestamp("2018-01-02T00:00:00Z"))
    h.loc[later, "tp_accum_m"] += 0.010
    h.loc[t == pd.Timestamp("2018-01-01T19:00:00Z"), "t2m_k"] = 310.
    inp = tmp_path / "nonuniform.csv"
    h.to_csv(inp, index=False)
    daily, qa = ingest_hourly(inp, weights, "2018-01-01", "2018-01-01")
    assert qa["complete_basin_rain_days"] == 1
    assert daily.rainfall_mm.iloc[0] == pytest.approx(29.)  # 24 + 10/2
    assert daily.t2m_c.iloc[0] == pytest.approx(26.85 + 10./48.)


def test_missing_next_midnight_boundary_rejects_preceding_day(tmp_path):
    weights, _ = load_weights(weights_file(tmp_path))
    h = hours()
    h = h[h.valid_time_utc != "2018-01-01T19:00:00Z"]
    inp = tmp_path / "missing_boundary.csv"
    h.to_csv(inp, index=False)
    daily, qa = ingest_hourly(inp, weights, "2018-01-01", "2018-01-01")
    assert qa["complete_basin_rain_days"] == 0
    assert pd.isna(daily.rainfall_mm.iloc[0])

def test_wrong_spatial_support_rejected(tmp_path):
    with pytest.raises(ValueError, match="Idukki-reservoir"):
        load_weights(weights_file(tmp_path, "WHOLE_PERIYAR_BASIN"))


def test_bad_weights_and_duplicate_hours_rejected(tmp_path):
    p = weights_file(tmp_path)
    w = pd.read_csv(p)
    w.loc[0, "weight"] = .5
    w.to_csv(p, index=False)
    with pytest.raises(ValueError, match="sum to exactly one"):
        load_weights(p)
    w = weights_file(tmp_path)
    weights, _ = load_weights(w)
    inp = tmp_path / "hourly.csv"
    h = hours()
    pd.concat([h, h.iloc[:1]], ignore_index=True).to_csv(inp, index=False)
    with pytest.raises(ValueError, match="Duplicate pixel/hour"):
        ingest_hourly(inp, weights, "2018-01-01", "2018-01-01")


def test_negative_deaccumulation_rejected(tmp_path):
    weights, _ = load_weights(weights_file(tmp_path))
    h = hours()
    ix = h.index[(h.latitude == 9.5) &
                 (h.valid_time_utc == "2018-01-01T03:00:00Z")][0]
    h.loc[ix, "tp_accum_m"] = 0.0001
    inp = tmp_path / "hourly.csv"
    h.to_csv(inp, index=False)
    with pytest.raises(ValueError, match="Negative ERA5-Land increment"):
        ingest_hourly(inp, weights, "2018-01-01", "2018-01-01")


def test_models_never_score_without_full_weather_history():
    dates = pd.date_range("2024-12-20", "2025-02-01", freq="D")
    phase4 = pd.DataFrame({"date": dates, "inflow_mcm_day_analysis": 10.0,
                           "inflow_lag1_mcm_day": 10.0,
                           "rainfall_mm_analysis": 1.0})
    for k in range(8):
        phase4[f"rain_lag{k}_mm"] = 1.0
    weather = pd.DataFrame({"date": dates, "rainfall_mm": np.nan,
                            "t2m_c": np.nan})
    result = compare_models(phase4, weather)
    assert result["experiments"]["antecedent_only"]["scores"] is None
    assert result["experiments"]["same_day_diagnostic"]["scores"] is None
