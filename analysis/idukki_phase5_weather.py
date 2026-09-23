#!/usr/bin/env python3
"""Phase 5: audited ERA5-Land hourly pixels -> Idukki IST days -> inflow diagnostics.

This is an OFFLINE processor, not a CDS downloader. It refuses to convert the
whole Periyar basin, district boundaries, five ERA5 sample points, or an
unverified raster bbox into an Idukki-reservoir catchment average.

Input hourly CSV (original-archive-derived, private):
  valid_time_utc,latitude,longitude,tp_accum_m,t2m_k
Input basin grid weights CSV (prepared from independently audited geometry):
  latitude,longitude,weight,source_id,spatial_support,geometry_sha256
All pixels in the weights file must match the hourly grid. IST days require
25 source intervals (23 full + 2 half), all valid at EVERY selected
pixel; missing values never become zero or partial-day totals.

Example:
 python analysis/idukki_phase5_weather.py --hourly-csv PRIVATE/hourly.csv \
   --weights-csv PRIVATE/idukki_weights.csv --curated PRIVATE/SLDC \
   --out PRIVATE/phase5

The emitted daily CSV and diagnostic calendar contain source-level data and
MUST remain private pending a source/reuse rights decision.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.preprocessing import StandardScaler

from idukki_hydro_energy_phase4 import calendar_join

START = "2018-01-01"
END = "2026-09-23"
SUPPORT = "IDUKKI_RESERVOIR_INTERCEPTED_CATCHMENT"
UTC_FORMAT = re.compile(r"(?:Z|\+00:00)$")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _numbers(frame: pd.DataFrame, fields: list[str]) -> None:
    for field in fields:
        converted = pd.to_numeric(frame[field], errors="coerce")
        if converted.isna().any() or not np.isfinite(converted).all():
            raise ValueError(f"Non-finite or missing numeric field: {field}")
        frame[field] = converted


def load_weights(path: Path) -> tuple[pd.DataFrame, dict]:
    weights = pd.read_csv(path)
    needed = {"latitude", "longitude", "weight", "source_id",
              "spatial_support", "geometry_sha256"}
    if not needed.issubset(weights):
        raise ValueError(f"Weights lack {sorted(needed - set(weights))}")
    if weights.empty:
        raise ValueError("No basin pixels")
    _numbers(weights, ["latitude", "longitude", "weight"])
    if weights.duplicated(["latitude", "longitude"]).any():
        raise ValueError("Duplicated weight coordinates")
    if not weights.latitude.between(-90, 90).all() or not weights.longitude.between(-180, 180).all():
        raise ValueError("Invalid latitude/longitude")
    if not weights.weight.gt(0).all() or not np.isclose(weights.weight.sum(), 1.0, atol=1e-6):
        raise ValueError("Weights must be positive and sum to exactly one")
    for col in ("source_id", "spatial_support", "geometry_sha256"):
        if weights[col].isna().any() or weights[col].nunique() != 1:
            raise ValueError(f"One non-empty documented {col} required")
        if not str(weights[col].iloc[0]).strip():
            raise ValueError(f"Blank {col}")
    if weights.spatial_support.iloc[0] != SUPPORT:
        raise ValueError("Not the independently verified Idukki-reservoir intercepted catchment")
    geometry = str(weights.geometry_sha256.iloc[0])
    if re.fullmatch(r"[0-9a-f]{64}", geometry) is None:
        raise ValueError("Invalid source geometry SHA-256")
    return weights, {"source_id": str(weights.source_id.iloc[0]),
                     "spatial_support": SUPPORT, "geometry_sha256": geometry,
                     "n_source_pixels": int(len(weights)), "weights_sha256": sha256(path)}


def ingest_hourly(hourly_path: Path, weights: pd.DataFrame,
                  first: str = START, last: str = END) -> tuple[pd.DataFrame, dict]:
    h = pd.read_csv(hourly_path, dtype={"valid_time_utc": str})
    required = {"valid_time_utc", "latitude", "longitude", "tp_accum_m", "t2m_k"}
    if not required.issubset(h):
        raise ValueError(f"Hourly CSV lacks {sorted(required - set(h))}")
    if h.empty or h.valid_time_utc.isna().any() or not h.valid_time_utc.str.contains(
            UTC_FORMAT).all():
        raise ValueError("All timestamp strings must explicitly be UTC (Z or +00:00)")
    h["time"] = pd.to_datetime(h.valid_time_utc, utc=True, errors="raise")
    if not h.time.dt.minute.eq(0).all() or not h.time.dt.second.eq(0).all():
        raise ValueError("ERA5-Land validity timestamps must end on exact UTC hours")
    _numbers(h, ["latitude", "longitude"])
    # Unlike rainfall, temperature and precipitation cells may be missing.
    for field in ("tp_accum_m", "t2m_k"):
        h[field] = pd.to_numeric(h[field], errors="coerce")
        if np.isinf(h[field]).any():
            raise ValueError(f"Infinite {field}")
    if h.duplicated(["time", "latitude", "longitude"]).any():
        raise ValueError("Duplicate pixel/hour; source forecast streams or files overlap")
    if h.tp_accum_m.lt(-1e-9).any() or h.t2m_k.dropna().lt(150).any():
        raise ValueError("Implausible source accumulated precipitation / kelvin")
    # Fail closed if the incoming grid contains unweighted extra cells or
    # omits a selected cell in every hour: this is not a basin average.
    grid = h[["latitude", "longitude"]].drop_duplicates()
    matched = grid.merge(weights[["latitude", "longitude"]], how="outer",
                         indicator=True, validate="one_to_one")
    if not matched._merge.eq("both").all():
        raise ValueError("Hourly pixel grid does not match independently verified weights")
    h = h.merge(weights[["latitude", "longitude", "weight"]],
                on=["latitude", "longitude"], validate="many_to_one")
    h = h.sort_values(["latitude", "longitude", "time"]).reset_index(drop=True)
    grp = h.groupby(["latitude", "longitude"], sort=False)
    before = grp["tp_accum_m"].shift(1)
    before_t = grp["time"].shift(1)
    midnight = h.time.dt.hour.eq(0)
    first_step = h.time.dt.hour.eq(1)
    consecutive = h.time.sub(before_t).eq(pd.Timedelta(hours=1))
    # For ERA5-Land hourly original GRIB: 01 UTC is forecast step 1;
    # 00 UTC is prior forecast day's step 24. Both 00 and 02..23
    # require a consecutive previous validity hour to subtract.
    increment = h.tp_accum_m - before
    increment = increment.where(consecutive & before.notna())
    increment = increment.mask(first_step, h.tp_accum_m)
    # If a 23->00 transition is missing, midnight MUST remain missing.
    bad_negative = increment.lt(-1e-7)
    if bad_negative.any():
        raise ValueError("Negative ERA5-Land increment: input may be deaccumulated or wrong stream")
    h["rain_hour_mm"] = (increment.clip(lower=0) * 1000).where(increment.notna())
    local_interval_end = h.time + pd.Timedelta(hours=5, minutes=30)
    h["temp_hour_c"] = h.t2m_k - 273.15
    # Hourly UTC increments cannot directly resolve a half-hour IST midnight.
    # A UTC hour ending at local 00:30 spans 23:30-00:30: split its
    # precipitation/temperature 50:50 between local dates, explicitly
    # assuming a uniform intra-hour rate. Every IST day consequently needs
    # 23 full hourly increments and TWO half-hour contributions: 25 source
    # intervals with effective total weight 24 hours per selected pixel.
    boundary = local_interval_end.dt.hour.eq(0) & local_interval_end.dt.minute.eq(30)
    h["date"] = local_interval_end.dt.tz_localize(None).dt.normalize()
    h["fraction"] = np.where(boundary, 0.5, 1.0)
    prior = h.loc[boundary].copy()
    prior["date"] = (local_interval_end.loc[boundary] - pd.Timedelta(hours=1)
                     ).dt.tz_localize(None).dt.normalize()
    prior["fraction"] = 0.5
    pieces = pd.concat([h, prior], ignore_index=True)
    pieces["rain_piece_mm"] = pieces.rain_hour_mm * pieces.fraction
    pieces["temp_piece_c_hours"] = pieces.temp_hour_c * pieces.fraction
    pix = pieces.groupby(["date", "latitude", "longitude", "weight"],
                         as_index=False).agg(
        n_source_intervals=("time", "size"),
        effective_hours=("fraction", "sum"),
        n_rain_segments=("rain_piece_mm", "count"),
        n_temp_segments=("temp_piece_c_hours", "count"),
        rain_mm=("rain_piece_mm", "sum"),
        temp_c_hours=("temp_piece_c_hours", "sum"))
    complete = pix.n_source_intervals.eq(25) & np.isclose(pix.effective_hours, 24)
    pix["rain_ok"] = complete & pix.n_rain_segments.eq(25)
    pix["temp_ok"] = complete & pix.n_temp_segments.eq(25)
    # Never convert empty/partial sums to a zero-valued observation.
    pix["rain_mm"] = pix.rain_mm.where(pix.rain_ok)
    pix["temp_c"] = (pix.temp_c_hours / 24).where(pix.temp_ok)
    pix["weighted_rain"] = pix.rain_mm * pix.weight
    pix["weighted_temp"] = pix.temp_c * pix.weight
    daily = pix.groupby("date", as_index=False).agg(
        pixels_seen=("weight", "size"),
        rain_pixels_complete=("rain_ok", "sum"),
        temp_pixels_complete=("temp_ok", "sum"),
        rain_weight=("weight", lambda w: float(w.sum())),
        rainfall_mm=("weighted_rain", "sum"),
        t2m_c=("weighted_temp", "sum"))
    n = len(weights)
    daily["rainfall_mm"] = daily.rainfall_mm.where(daily.rain_pixels_complete.eq(n)
                                                    & daily.pixels_seen.eq(n))
    daily["t2m_c"] = daily.t2m_c.where(daily.temp_pixels_complete.eq(n)
                                        & daily.pixels_seen.eq(n))
    dates = pd.DataFrame({"date": pd.date_range(first, last, freq="D")})
    daily = dates.merge(daily, on="date", how="left", validate="one_to_one")
    daily["pixels_seen"] = daily.pixels_seen.fillna(0).astype(int)
    for c in ("rain_pixels_complete", "temp_pixels_complete"):
        daily[c] = daily[c].fillna(0).astype(int)
    qa = {"hourly_source_sha256": sha256(hourly_path),
          "n_hourly_pixel_rows": int(len(h)),
          "n_selected_source_pixels": n,
          "date_slots": int(len(daily)),
          "complete_basin_rain_days": int(daily.rainfall_mm.count()),
          "complete_basin_temperature_days": int(daily.t2m_c.count()),
          "missing_or_incomplete_rain_days": int(daily.rainfall_mm.isna().sum()),
          "earliest_complete_day": (daily.loc[daily.rainfall_mm.notna(), "date"].min().date().isoformat()
                                    if daily.rainfall_mm.notna().any() else None),
          "latest_complete_day": (daily.loc[daily.rainfall_mm.notna(), "date"].max().date().isoformat()
                                  if daily.rainfall_mm.notna().any() else None),
          "era5_land_tp_convention": "accum_since_00UTC; validity_00UTC=prior_day_step24",
          "ist_interval_convention": "UTC interval end +05:30; split 00:30 ends 50:50",
          "temporal_allocation_assumption": "uniform rate within midnight-straddling UTC hour",
          "daily_missing_policy": "25 nonmissing source intervals (23 full + two half) per IST day and pixel"}
    return daily, qa


def _scores(y: np.ndarray, p: np.ndarray) -> dict:
    return {"mae_mcm_day": round(float(mean_absolute_error(y, p)), 5),
            "rmse_mcm_day": round(float(np.sqrt(mean_squared_error(y, p))), 5)}


def compare_models(phase4: pd.DataFrame, weather: pd.DataFrame) -> dict:
    """Paired gauge/ERA diagnostic AND antecedent-only one-day-ahead experiment.

    At t, the antecedent experiment uses rainfall only through t-1 and a
    reported previous-day inflow. This still cannot prove operational forecast
    skill: future weather availability, gauge latency and extremes are untested.
    """
    d = phase4.merge(weather[["date", "rainfall_mm", "t2m_c"]].rename(
        columns={"rainfall_mm": "basin_rainfall_mm", "t2m_c": "basin_t2m_c"}),
        on="date", how="left", validate="one_to_one")
    d = d.set_index("date", verify_integrity=True).asfreq("D")
    for lag in range(8):
        d[f"era_lag{lag}"] = d.basin_rainfall_mm.shift(lag)
    d = d.reset_index()
    out = {"classification": "retrospective_historical_validation_NOT_operational_forecast",
           "split": {"train_end": "2024-12-31", "test_start": "2025-01-01"},
           "basin_rain_inflow_pairs": int(d[["basin_rainfall_mm",
                                             "inflow_mcm_day_analysis"]].dropna().shape[0]),
           "source_gauge_rain_inflow_pairs": int(d[["rainfall_mm_analysis",
                                                   "inflow_mcm_day_analysis"]].dropna().shape[0]),
           "experiments": {}}
    for mode, offsets in (("antecedent_only", range(1, 8)),
                          ("same_day_diagnostic", range(8))):
        era = [f"era_lag{j}" for j in offsets]
        gauge = [f"rain_lag{j}_mm" for j in offsets]
        common = ["inflow_lag1_mcm_day"]
        cols = ["date", "inflow_mcm_day_analysis", *common, *era, *gauge]
        both = d[cols].replace([np.inf, -np.inf], np.nan).dropna()
        train = both[both.date.le("2024-12-31")]
        test = both[both.date.ge("2025-01-01")]
        result = {"paired_complete_case_train_days": int(len(train)),
                  "paired_complete_case_test_days": int(len(test)),
                  "gauge_and_era_scored_on_identical_dates": True,
                  "same_day_rain_used": mode == "same_day_diagnostic"}
        if len(train) < 100 or len(test) < 50:
            result["status"] = "insufficient_paired_complete_cases"
            result["scores"] = None
            out["experiments"][mode] = result
            continue
        ytrain = train.inflow_mcm_day_analysis.to_numpy()
        ytest = test.inflow_mcm_day_analysis.to_numpy()
        scores = {"previous_day_inflow_persistence": _scores(
            ytest, test.inflow_lag1_mcm_day.to_numpy())}
        for name, features in (("era5_basin_rain", [*era, *common]),
                               ("sldc_idukki_gauge", [*gauge, *common])):
            scale = StandardScaler().fit(train[features])
            model = Ridge(alpha=10.0).fit(scale.transform(train[features]), ytrain)
            pred = np.maximum(0, model.predict(scale.transform(test[features])))
            scores[name] = _scores(ytest, pred)
        result.update({"status": "held_out_scored", "scores": scores})
        out["experiments"][mode] = result
    out["limitations"] = [
        "Basin rain is ECMWF reanalysis, not a measured basin gauge",
        "All model comparisons are on identical complete-case dates per experiment",
        "No claim of flood-event causality, live forecast skill, or 2018 SLDC electricity",
        "No temperature feature, station head, turbine discharge or pumped storage inferred",
    ]
    return out


def run(hourly: Path, weights_file: Path, curated: Path, output: Path,
        first: str, last: str) -> dict:
    if pd.Timestamp(first) > pd.Timestamp(last):
        raise ValueError("Start must be <= end")
    output.mkdir(parents=True, exist_ok=True)
    weights, geometry_qa = load_weights(weights_file)
    weather, hourly_qa = ingest_hourly(hourly, weights, first, last)
    # Fail closed: no research claim or public QA produced if nothing is admitted.
    if not weather.rainfall_mm.notna().any():
        raise ValueError("No complete 24-hour IST basin-rainfall days; inspect private QA")
    phase4, hashes = calendar_join(curated)
    models = compare_models(phase4, weather)
    weather["source_id"] = geometry_qa["source_id"] + "::ERA5-Land"
    weather["spatial_support"] = SUPPORT
    weather["precipitation_processing"] = "original ERA5-Land deaccumulated hourly_increment, IST"
    weather["geometry_sha256"] = geometry_qa["geometry_sha256"]
    # Never accidentally publish these date-level tables or original archive rows.
    weather.to_csv(output / "idukki_phase5_weather_daily_PRIVATE.csv", index=False)
    qa = {"classification": "ERA5_LAND_CATCHMENT_WEATHER_REANALYSIS_NOT_METORED_OR_CAUSAL",
          "observation_coverage": hourly_qa, "verified_geometry": geometry_qa,
          "curated_sldc_sha256": hashes, "model_comparisons": models,
          "2018_sldc_electricity_observations": 0,
          "private_weather_daily": "idukki_phase5_weather_daily_PRIVATE.csv"}
    (output / "idukki_phase5_public_qa.json").write_text(
        json.dumps(qa, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({"status": "observed_hourly_input_processed",
                      "basin_rain_days": hourly_qa["complete_basin_rain_days"],
                      "paired_test_days_antecedent":
                          models["experiments"]["antecedent_only"]["paired_complete_case_test_days"],
                      "private_output": str(output)}, indent=2))
    return qa


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--hourly-csv", required=True, type=Path)
    parser.add_argument("--weights-csv", required=True, type=Path)
    parser.add_argument("--curated", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--start", default=START)
    parser.add_argument("--end", default=END)
    args = parser.parse_args()
    run(args.hourly_csv, args.weights_csv, args.curated, args.out, args.start, args.end)


if __name__ == "__main__":
    main()
