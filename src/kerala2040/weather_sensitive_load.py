"""ERA5-sensitive hourly Kerala load reconstruction from daily energy + intraday anchors.

This is a proxy chronology, never measured hourly telemetry. It preserves each
available SLDC daily energy total exactly; the 11 missing daily totals retain the
existing model-only interpolation flag. ERA5-Land daily weather and SLDC selected
intraday consumption extrema are used to estimate day-specific shape, while a
chronological Jan-Mar 2025 holdout measures shape skill.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from kerala2040.load_proxy import complete_daily_energy, diurnal_shape, duration_counts

START = "2024-04-01"
END = "2025-03-31"
TRAIN_END = "2024-12-31"
TEST_START = "2025-01-01"
ROOT_CLASS = "proxy_reconstruction_not_measured_telemetry"
ROW_CLASS = "proxy_reconstruction"

ANCHORS = {
    ("minimum", "night"): "night_min",
    ("maximum", "morning"): "morning_max",
    ("minimum", "day"): "day_min",
    ("maximum", "day"): "day_max",
    ("maximum", "evening"): "evening_max",
}
ANCHOR_ORDER = ("night_min", "morning_max", "day_min", "day_max", "evening_max")
WEATHER_COLUMNS = (
    "t2m_mean_c",
    "t2m_min_c",
    "t2m_max_c",
    "dewpoint_mean_c",
    "rh_approx_pct",
    "rainfall_mm",
    "wind10_mean_ms",
    "wind10_max_ms",
    "ssrd_kwh_m2",
    "total_runoff_mm",
    "soilwater1_mean",
)
RIDGE_ALPHA = 8.0


@dataclass(frozen=True)
class AnchorMetric:
    n: int
    mae_mw: float
    rmse_mw: float


def _clock_hours(value: str) -> float:
    parts = str(value).strip().split(":")
    if len(parts) < 2:
        raise ValueError(f"Invalid clock value: {value}")
    return int(parts[0]) + int(parts[1]) / 60.0


def interval_midpoint_hours(start: str, end: str) -> float:
    a = _clock_hours(start)
    b = _clock_hours(end)
    if b < a:
        b += 24.0
    return ((a + b) / 2.0) % 24.0


def _circular_interpolate(hour: float | np.ndarray, xs: np.ndarray, ys: np.ndarray) -> np.ndarray:
    order = np.argsort(xs)
    x = np.asarray(xs, dtype=float)[order]
    y = np.asarray(ys, dtype=float)[order]
    ext_x = np.concatenate([x - 24.0, x, x + 24.0])
    ext_y = np.concatenate([y, y, y])
    return np.interp(np.asarray(hour, dtype=float), ext_x, ext_y)


def _calendar_features(dates: pd.Series) -> pd.DataFrame:
    dt = pd.to_datetime(dates)
    doy = dt.dt.dayofyear.to_numpy(dtype=float)
    angle = 2.0 * np.pi * doy / 365.25
    out = pd.DataFrame({
        "sin_doy": np.sin(angle),
        "cos_doy": np.cos(angle),
        "sin_2doy": np.sin(2.0 * angle),
        "cos_2doy": np.cos(2.0 * angle),
        "weekend": (dt.dt.dayofweek >= 5).astype(float).to_numpy(),
    }, index=dt.index)
    weekday = pd.get_dummies(dt.dt.dayofweek, prefix="dow", dtype=float)
    weekday.index = dt.index
    for i in range(6):
        col = f"dow_{i}"
        out[col] = weekday[col] if col in weekday else 0.0
    return out


def feature_frame(daily: pd.DataFrame, *, include_weather: bool) -> pd.DataFrame:
    base = _calendar_features(daily["date"])
    if not include_weather:
        return base
    missing = set(WEATHER_COLUMNS).difference(daily.columns)
    if missing:
        raise ValueError(f"ERA5 daily table missing weather columns: {sorted(missing)}")
    w = daily.loc[:, WEATHER_COLUMNS].apply(pd.to_numeric, errors="coerce")
    if w.isna().any().any() or not np.isfinite(w.to_numpy(dtype=float)).all():
        raise ValueError("ERA5 weather features must be finite for all 365 days")
    out = base.copy()
    out["t2m_mean_c"] = w.t2m_mean_c
    out["t2m_range_c"] = w.t2m_max_c - w.t2m_min_c
    out["dewpoint_mean_c"] = w.dewpoint_mean_c
    out["rh_approx_pct"] = w.rh_approx_pct
    out["rainfall_log1p_mm"] = np.log1p(np.maximum(w.rainfall_mm, 0.0))
    out["wind10_mean_ms"] = w.wind10_mean_ms
    out["wind10_max_ms"] = w.wind10_max_ms
    out["ssrd_kwh_m2"] = w.ssrd_kwh_m2
    out["runoff_log1p_mm"] = np.log1p(np.maximum(w.total_runoff_mm, 0.0))
    out["soilwater1_mean"] = w.soilwater1_mean
    out["temp_x_solar"] = w.t2m_mean_c * w.ssrd_kwh_m2
    out["temp_x_rh"] = w.t2m_mean_c * w.rh_approx_pct
    out["rain_x_wind"] = np.log1p(np.maximum(w.rainfall_mm, 0.0)) * w.wind10_mean_ms
    return out.astype(float)


def prepare_daily(daily_balance: pd.DataFrame, weather: pd.DataFrame) -> pd.DataFrame:
    required = {"date", "status", "consumption_mu"}
    if not required.issubset(daily_balance):
        raise ValueError(f"Daily balance missing {sorted(required - set(daily_balance))}")
    raw = daily_balance[["date", "consumption_mu"]].copy()
    complete = complete_daily_energy(raw, start=START, end=END)
    status = daily_balance[["date", "status", "internal_generation_mu", "hydro_mu", "net_import_mu"]].copy()
    status["date"] = pd.to_datetime(status.date).dt.normalize()
    if len(status) != 365 or status.date.duplicated().any():
        raise ValueError("Expected exactly 365 unique SLDC daily rows")
    complete = complete.merge(status, on="date", how="left", validate="one_to_one")

    wx = weather.copy()
    if "index" in wx:
        wx = wx.drop(columns="index")
    wx["date"] = pd.to_datetime(wx.date).dt.normalize()
    if len(wx) != 365 or wx.date.duplicated().any():
        raise ValueError("Expected exactly 365 unique ERA5 daily rows")
    expected = pd.date_range(START, END, freq="D")
    if not wx.date.sort_values().reset_index(drop=True).equals(pd.Series(expected)):
        raise ValueError("ERA5 daily dates do not exactly cover FY2024-25")
    out = complete.merge(wx, on="date", how="left", validate="one_to_one")
    if len(out) != 365:
        raise ValueError("Daily join changed fiscal-year population")
    return out.sort_values("date").reset_index(drop=True)


def prepare_extrema(extrema: pd.DataFrame, daily: pd.DataFrame) -> pd.DataFrame:
    e = extrema.rename(columns={
        "category": "event",
        "metric": "quantity",
        "time_from": "time_from_ist",
        "time_to": "time_to_ist",
    }).copy()
    needed = {"date", "event", "period", "quantity", "mw", "time_from_ist", "time_to_ist"}
    if not needed.issubset(e):
        raise ValueError(f"Extrema file missing {sorted(needed - set(e))}")
    e["date"] = pd.to_datetime(e.date).dt.normalize()
    e["event"] = e.event.astype(str).str.casefold()
    e["period"] = e.period.astype(str).str.casefold()
    e["quantity"] = e.quantity.astype(str).str.casefold()
    e = e[e.quantity.eq("consumption")].copy()
    e["anchor"] = [ANCHORS.get((a, b)) for a, b in zip(e.event, e.period, strict=True)]
    e = e[e.anchor.notna()].copy()
    if e.duplicated(["date", "anchor"]).any():
        raise ValueError("Multiple SLDC consumption extrema for the same date/anchor")
    e["mw"] = pd.to_numeric(e.mw, errors="coerce")
    if e.mw.isna().any() or (e.mw <= 0).any():
        raise ValueError("Consumption extrema must be finite positive MW")
    e["reported_hour"] = [
        interval_midpoint_hours(a, b)
        for a, b in zip(e.time_from_ist, e.time_to_ist, strict=True)
    ]
    observed = daily.loc[~daily.daily_energy_imputed, ["date", "consumption_mu"]].copy()
    e = e.merge(observed, on="date", how="inner", validate="many_to_one")
    e["daily_mean_mw"] = e.consumption_mu * 1000.0 / 24.0
    e["ratio"] = e.mw / e.daily_mean_mw
    if not e.ratio.between(0.35, 2.5).all():
        raise ValueError("Intraday extrema ratios outside broad QA bounds")
    return e.sort_values(["date", "anchor"]).reset_index(drop=True)


def _fit_model(x: pd.DataFrame, y: pd.Series):
    model = make_pipeline(StandardScaler(), Ridge(alpha=RIDGE_ALPHA))
    model.fit(x, y)
    return model


def _metric(actual: np.ndarray, predicted: np.ndarray) -> AnchorMetric:
    error = np.asarray(predicted, dtype=float) - np.asarray(actual, dtype=float)
    return AnchorMetric(
        n=int(len(error)),
        mae_mw=float(np.mean(np.abs(error))),
        rmse_mw=float(np.sqrt(np.mean(error**2))),
    )


def fit_anchor_models(
    daily: pd.DataFrame,
    extrema: pd.DataFrame,
) -> tuple[dict[str, Any], pd.DataFrame, dict[str, float]]:
    calendar = feature_frame(daily, include_weather=False)
    weather = feature_frame(daily, include_weather=True)
    date_index = pd.DatetimeIndex(daily.date)

    wide = extrema.pivot(index="date", columns="anchor", values="ratio").reindex(date_index)
    if set(ANCHOR_ORDER).difference(wide.columns):
        raise ValueError("At least one expected consumption anchor is absent")
    train_mask = date_index <= pd.Timestamp(TRAIN_END)
    test_mask = date_index >= pd.Timestamp(TEST_START)

    predictions = pd.DataFrame({"date": date_index})
    metadata: dict[str, Any] = {}
    canonical_hours: dict[str, float] = {}
    for anchor in ANCHOR_ORDER:
        y = wide[anchor]
        fit_mask = train_mask & y.notna().to_numpy()
        test_valid = test_mask & y.notna().to_numpy()
        if fit_mask.sum() < 150 or test_valid.sum() < 40:
            raise ValueError(f"Insufficient chronological data for {anchor}")
        calendar_model = _fit_model(calendar.loc[fit_mask], y.loc[fit_mask])
        weather_model = _fit_model(weather.loc[fit_mask], y.loc[fit_mask])
        low = max(0.4, float(y.loc[fit_mask].quantile(0.01)) - 0.04)
        high = min(2.2, float(y.loc[fit_mask].quantile(0.99)) + 0.04)
        predictions[f"{anchor}_calendar"] = np.clip(calendar_model.predict(calendar), low, high)
        predictions[f"{anchor}_weather"] = np.clip(weather_model.predict(weather), low, high)
        metadata[anchor] = {
            "training_days": int(fit_mask.sum()),
            "test_days": int(test_valid.sum()),
            "clip_ratio": [low, high],
            "weather_feature_names": weather.columns.tolist(),
            "weather_standardised_ridge_coefficients": {
                name: float(value)
                for name, value in zip(
                    weather.columns,
                    weather_model.named_steps["ridge"].coef_,
                    strict=True,
                )
            },
        }
        train_times = extrema[
            extrema.anchor.eq(anchor) & extrema.date.le(pd.Timestamp(TRAIN_END))
        ].reported_hour
        canonical_hours[anchor] = float(train_times.median())
    return metadata, predictions, canonical_hours


def _shape_from_anchor_values(values: dict[str, float], canonical_hours: dict[str, float]) -> np.ndarray:
    xs = np.array([canonical_hours[a] for a in ANCHOR_ORDER], dtype=float)
    ys = np.array([values[a] for a in ANCHOR_ORDER], dtype=float)
    # Preserve source semantics: minima must not exceed their neighbouring maxima.
    ys[0] = min(ys[0], ys[1] - 0.01, ys[4] - 0.01)
    ys[2] = min(ys[2], ys[1] - 0.005, ys[3] - 0.01)
    ys = np.clip(ys, 0.45, 2.0)
    hours = np.arange(24, dtype=float)
    shape = _circular_interpolate(hours, xs, ys)
    # A small fixed-shape blend prevents five reported extrema from becoming sharp corners.
    old = diurnal_shape(0.43, 0.39)
    shape = 0.85 * shape + 0.15 * old
    shape = np.clip(shape, 0.45, None)
    return shape / shape.mean()


def build_profile(
    daily: pd.DataFrame,
    predictions: pd.DataFrame,
    canonical_hours: dict[str, float],
    *,
    model: str,
) -> tuple[pd.DataFrame, dict[pd.Timestamp, np.ndarray]]:
    if model not in {"weather", "calendar"}:
        raise ValueError("model must be weather or calendar")
    p = predictions.set_index("date")
    rows = []
    shapes: dict[pd.Timestamp, np.ndarray] = {}
    for row in daily.itertuples(index=False):
        date = pd.Timestamp(row.date)
        values = {
            anchor: float(p.loc[date, f"{anchor}_{model}"])
            for anchor in ANCHOR_ORDER
        }
        shape = _shape_from_anchor_values(values, canonical_hours)
        shapes[date] = shape
        mean_mw = float(row.consumption_mu) * 1000.0 / 24.0
        times = pd.date_range(date, periods=24, freq="h", tz="Asia/Kolkata")
        for hour, timestamp in enumerate(times):
            rows.append({
                "timestamp": timestamp.isoformat(),
                "load_mw": float(mean_mw * shape[hour]),
                "daily_consumption_mu": float(row.consumption_mu),
                "daily_energy_imputed": bool(row.daily_energy_imputed),
                "classification": ROW_CLASS,
            })
    return pd.DataFrame(rows), shapes


def build_old_profile(daily: pd.DataFrame) -> tuple[pd.DataFrame, dict[pd.Timestamp, np.ndarray]]:
    shape = diurnal_shape(0.43, 0.39)
    rows = []
    shapes = {}
    for row in daily.itertuples(index=False):
        date = pd.Timestamp(row.date)
        shapes[date] = shape.copy()
        mean_mw = float(row.consumption_mu) * 1000.0 / 24.0
        times = pd.date_range(date, periods=24, freq="h", tz="Asia/Kolkata")
        for hour, timestamp in enumerate(times):
            rows.append({
                "timestamp": timestamp.isoformat(),
                "load_mw": float(mean_mw * shape[hour]),
                "daily_consumption_mu": float(row.consumption_mu),
                "daily_energy_imputed": bool(row.daily_energy_imputed),
                "classification": ROW_CLASS,
            })
    return pd.DataFrame(rows), shapes


def _shape_value(shape: np.ndarray, fractional_hour: float) -> float:
    hours = np.arange(24, dtype=float)
    return float(_circular_interpolate(fractional_hour, hours, shape))


def validate_extrema(
    extrema: pd.DataFrame,
    daily: pd.DataFrame,
    predictions: pd.DataFrame,
    shapes: dict[pd.Timestamp, np.ndarray],
    old_shapes: dict[pd.Timestamp, np.ndarray],
) -> dict[str, Any]:
    test = extrema[extrema.date.ge(pd.Timestamp(TEST_START))].copy()
    pred = predictions.set_index("date")
    daily_mean = daily.set_index("date").consumption_mu * 1000.0 / 24.0
    actual = test.mw.to_numpy(dtype=float)
    direct_weather = np.array([
        float(daily_mean.loc[r.date]) * float(pred.loc[r.date, f"{r.anchor}_weather"])
        for r in test.itertuples()
    ])
    direct_calendar = np.array([
        float(daily_mean.loc[r.date]) * float(pred.loc[r.date, f"{r.anchor}_calendar"])
        for r in test.itertuples()
    ])
    curve_weather = np.array([
        float(daily_mean.loc[r.date]) * _shape_value(shapes[r.date], float(r.reported_hour))
        for r in test.itertuples()
    ])
    curve_old = np.array([
        float(daily_mean.loc[r.date]) * _shape_value(old_shapes[r.date], float(r.reported_hour))
        for r in test.itertuples()
    ])
    report = {
        "population": {
            "test_rows": int(len(test)),
            "test_days": int(test.date.nunique()),
            "period": f"{TEST_START} to {END}",
        },
        "overall": {
            "old_fixed_curve": asdict(_metric(actual, curve_old)),
            "calendar_anchor_model": asdict(_metric(actual, direct_calendar)),
            "era5_anchor_model": asdict(_metric(actual, direct_weather)),
            "era5_hourly_curve": asdict(_metric(actual, curve_weather)),
        },
        "by_anchor": {},
    }
    for anchor in ANCHOR_ORDER:
        mask = test.anchor.eq(anchor).to_numpy()
        report["by_anchor"][anchor] = {
            "old_fixed_curve": asdict(_metric(actual[mask], curve_old[mask])),
            "era5_anchor_model": asdict(_metric(actual[mask], direct_weather[mask])),
            "era5_hourly_curve": asdict(_metric(actual[mask], curve_weather[mask])),
        }
    old_rmse = report["overall"]["old_fixed_curve"]["rmse_mw"]
    new_rmse = report["overall"]["era5_hourly_curve"]["rmse_mw"]
    report["era5_curve_rmse_change_vs_old_pct"] = 100.0 * (new_rmse - old_rmse) / old_rmse
    return report


def _daily_residual(hourly: pd.DataFrame, daily: pd.DataFrame) -> float:
    times = pd.to_datetime(hourly.timestamp, utc=True).dt.tz_convert("Asia/Kolkata")
    work = hourly.assign(date=times.dt.tz_localize(None).dt.normalize())
    energy = work.groupby("date").load_mw.sum() / 1000.0
    ref = daily.set_index("date").consumption_mu
    return float((energy - ref).abs().max())


def _duration_report(values: np.ndarray, bins: list[dict[str, Any]]) -> dict[str, Any]:
    counts = duration_counts(values, bins)
    target = np.array([int(b["hours"]) for b in bins], dtype=float)
    got = np.array(counts, dtype=float)
    return {
        "counts": [
            {**b, "proxy_hours": int(c), "difference_hours": int(c - int(b["hours"]))}
            for b, c in zip(bins, counts, strict=True)
        ],
        "count_rmse_hours": float(np.sqrt(np.mean((got - target) ** 2))),
    }


def create_proxy_and_summary(
    daily_balance: pd.DataFrame,
    weather: pd.DataFrame,
    extrema: pd.DataFrame,
    *,
    bins: list[dict[str, Any]],
    cea_peak_mw: float,
) -> tuple[dict[str, Any], pd.DataFrame, dict[str, Any]]:
    daily = prepare_daily(daily_balance, weather)
    anchors = prepare_extrema(extrema, daily)
    model_meta, predictions, canonical_hours = fit_anchor_models(daily, anchors)
    weather_hourly, weather_shapes = build_profile(
        daily, predictions, canonical_hours, model="weather"
    )
    old_hourly, old_shapes = build_old_profile(daily)
    validation = validate_extrema(
        anchors, daily, predictions, weather_shapes, old_shapes
    )
    old_values = old_hourly.load_mw.to_numpy(dtype=float)
    new_values = weather_hourly.load_mw.to_numpy(dtype=float)
    summary = {
        "classification": ROOT_CLASS,
        "method": "ERA5_Land_daily_weather_plus_SLDC_selected_intraday_extrema_ridge_shape_model",
        "period": f"{START} to {END}",
        "timezone": "Asia/Kolkata",
        "resolution": "1h",
        "hours": int(len(weather_hourly)),
        "train_period": f"{START} to {TRAIN_END}",
        "test_period": f"{TEST_START} to {END}",
        "weather_columns": list(WEATHER_COLUMNS),
        "ridge_alpha": RIDGE_ALPHA,
        "canonical_anchor_hours_from_training": canonical_hours,
        "anchor_models": model_meta,
        "validation_against_selected_intraday_consumption_extrema": validation,
        "daily_observations_measured": int((~daily.daily_energy_imputed).sum()),
        "daily_observations_interpolated": int(daily.daily_energy_imputed.sum()),
        "interpolated_dates": [
            d.date().isoformat()
            for d in daily.loc[daily.daily_energy_imputed, "date"]
        ],
        "daily_energy_conservation_max_abs_residual_mu": _daily_residual(weather_hourly, daily),
        "old_fixed_profile_daily_energy_conservation_max_abs_residual_mu": _daily_residual(old_hourly, daily),
        "cea_reference_peak_mw": float(cea_peak_mw),
        "old_fixed_profile_peak_mw": float(old_values.max()),
        "era5_sensitive_profile_peak_mw": float(new_values.max()),
        "old_fixed_peak_error_pct": 100.0 * (old_values.max() - cea_peak_mw) / cea_peak_mw,
        "era5_sensitive_peak_error_pct": 100.0 * (new_values.max() - cea_peak_mw) / cea_peak_mw,
        "cea_duration_bins_old_fixed_profile": _duration_report(old_values, bins),
        "cea_duration_bins_era5_sensitive_profile": _duration_report(new_values, bins),
        "limits": [
            "Hourly values remain reconstructed proxy values, not metered hourly Kerala demand.",
            "ERA5-Land is reanalysis weather, not station-measured statewide weather.",
            "SLDC selected extrema are sparse intraday anchors, not a continuous load curve.",
            "Eleven missing daily SLDC energy totals remain model-only linear interpolations and are flagged.",
            "Chronological holdout validates selected extrema only; it does not establish full-hour accuracy.",
            "No causal interpretation is assigned to weather coefficients.",
        ],
    }
    proxy = {
        "classification": ROOT_CLASS,
        "source_type": "weather_sensitive_reconstruction_from_observed_daily_energy_and_selected_intraday_extrema",
        "source": "Kerala SLDC daily statistics + selected intraday extrema + Kerala-area ERA5-Land daily weather",
        "note": "ERA5-sensitive hourly proxy; not measured hourly or 15-minute Kerala telemetry.",
        "period": "FY2024-25",
        "timezone": "Asia/Kolkata",
        "interval": "1h",
        "shape_model": summary["method"],
        "records": weather_hourly[[
            "timestamp", "load_mw", "daily_consumption_mu",
            "daily_energy_imputed", "classification"
        ]].to_dict(orient="records"),
    }
    return proxy, weather_hourly, summary
