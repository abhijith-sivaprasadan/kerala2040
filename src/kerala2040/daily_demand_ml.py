"""Experimental daily Kerala demand ML using observed targets and verified ERA5 weather.

This module deliberately models daily observed consumption, not the reconstructed
8,760-hour load proxy. Evidence boundaries are explicit: source-reported daily target,
verified ERA5 weather, chronological validation, Optuna tuning, and conditional SHAP.
"""
from __future__ import annotations

import json
import math
from collections.abc import Callable
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.model_selection import TimeSeriesSplit
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

CLASSIFICATION = "experimental_daily_observed_demand_ml_v0_1_not_hourly_forecast"
WEATHER_FEATURES = [
    "temp_mean_c",
    "temp_max_c",
    "temp_min_c",
    "temp_range_c",
    "cooling_degree_hours_24c",
    "hot_hours_gt30c",
    "ghi_kwh_m2_day",
    "precip_mm_day",
    "wet_hours_gt0_1mm",
    "wind_mean_m_s",
    "wind_max_m_s",
]
CALENDAR_FEATURES = [
    "doy_sin",
    "doy_cos",
    "dow_sin",
    "dow_cos",
    "month_sin",
    "month_cos",
    "is_weekend",
]
FEATURES = CALENDAR_FEATURES + WEATHER_FEATURES


def load_observed_daily_consumption(path: Path) -> pd.DataFrame:
    """Load the published FY2024-25 daily target without filling missing dates."""
    payload = json.loads(path.read_text(encoding="utf-8"))
    records = payload.get("records")
    if not isinstance(records, list) or not records:
        raise ValueError("daily-balance JSON must contain non-empty records")

    frame = pd.DataFrame(records)
    required = {"date", "consumption_mu"}
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"daily target missing columns: {sorted(missing)}")

    frame = frame.loc[:, ["date", "consumption_mu"]].copy()
    frame["date"] = pd.to_datetime(frame["date"], errors="raise").dt.normalize()
    frame["consumption_mu"] = pd.to_numeric(frame["consumption_mu"], errors="raise")
    if frame["date"].duplicated().any():
        raise ValueError("daily target contains duplicate dates")
    if frame["consumption_mu"].isna().any():
        raise ValueError("published daily target must not silently contain missing values")
    if not np.isfinite(frame["consumption_mu"]).all() or (frame["consumption_mu"] <= 0).any():
        raise ValueError("daily consumption target must be finite and positive")
    return frame.sort_values("date").reset_index(drop=True)


def aggregate_daily_weather(weather: pd.DataFrame) -> pd.DataFrame:
    """Aggregate five-point verified ERA5 hourly weather to daily features."""
    required = {
        "point",
        "timestamp_utc",
        "temp_c",
        "wind10_m_s",
        "ghi_wh_m2",
        "precip_mm_h",
    }
    missing = required - set(weather.columns)
    if missing:
        raise ValueError(f"ERA5 weather missing columns: {sorted(missing)}")

    frame = weather.loc[:, sorted(required)].copy()
    frame["timestamp_utc"] = pd.to_datetime(frame["timestamp_utc"], utc=True, errors="raise")
    for column in ["temp_c", "wind10_m_s", "ghi_wh_m2", "precip_mm_h"]:
        frame[column] = pd.to_numeric(frame[column], errors="raise")
        if not np.isfinite(frame[column]).all():
            raise ValueError(f"ERA5 weather contains non-finite {column}")

    hourly = (
        frame.groupby("timestamp_utc", as_index=False)[
            ["temp_c", "wind10_m_s", "ghi_wh_m2", "precip_mm_h"]
        ]
        .mean()
        .sort_values("timestamp_utc")
    )
    hourly["timestamp_ist"] = hourly["timestamp_utc"].dt.tz_convert("Asia/Kolkata")
    hourly["date"] = hourly["timestamp_ist"].dt.tz_localize(None).dt.normalize()
    hourly["cooling_degree_h"] = np.clip(hourly["temp_c"] - 24.0, 0.0, None)
    hourly["hot_gt30"] = (hourly["temp_c"] > 30.0).astype(float)
    hourly["wet_gt0_1"] = (hourly["precip_mm_h"] > 0.1).astype(float)

    daily = hourly.groupby("date", sort=True).agg(
        temp_mean_c=("temp_c", "mean"),
        temp_max_c=("temp_c", "max"),
        temp_min_c=("temp_c", "min"),
        cooling_degree_hours_24c=("cooling_degree_h", "sum"),
        hot_hours_gt30c=("hot_gt30", "sum"),
        ghi_wh_m2_day=("ghi_wh_m2", "sum"),
        precip_mm_day=("precip_mm_h", "sum"),
        wet_hours_gt0_1mm=("wet_gt0_1", "sum"),
        wind_mean_m_s=("wind10_m_s", "mean"),
        wind_max_m_s=("wind10_m_s", "max"),
        hourly_rows=("timestamp_utc", "size"),
    ).reset_index()
    daily["ghi_kwh_m2_day"] = daily.pop("ghi_wh_m2_day") / 1000.0
    daily["temp_range_c"] = daily["temp_max_c"] - daily["temp_min_c"]

    complete = daily.loc[daily["hourly_rows"] == 24].copy()
    if complete.empty:
        raise ValueError("ERA5 daily aggregation produced no complete IST days")
    return complete.drop(columns="hourly_rows")


def add_calendar_features(frame: pd.DataFrame) -> pd.DataFrame:
    result = frame.copy()
    date = pd.to_datetime(result["date"], errors="raise")
    doy = date.dt.dayofyear.astype(float)
    dow = date.dt.dayofweek.astype(float)
    month = date.dt.month.astype(float)
    result["doy_sin"] = np.sin(2.0 * np.pi * doy / 365.25)
    result["doy_cos"] = np.cos(2.0 * np.pi * doy / 365.25)
    result["dow_sin"] = np.sin(2.0 * np.pi * dow / 7.0)
    result["dow_cos"] = np.cos(2.0 * np.pi * dow / 7.0)
    result["month_sin"] = np.sin(2.0 * np.pi * month / 12.0)
    result["month_cos"] = np.cos(2.0 * np.pi * month / 12.0)
    result["is_weekend"] = (dow >= 5).astype(float)
    return result


def build_daily_feature_table(observed: pd.DataFrame, weather: pd.DataFrame) -> pd.DataFrame:
    """Join observed daily target to same-day exogenous weather and calendar features."""
    daily_weather = aggregate_daily_weather(weather)
    joined = observed.merge(daily_weather, on="date", how="inner", validate="one_to_one")
    joined = add_calendar_features(joined).sort_values("date").reset_index(drop=True)
    missing = sorted(set(observed["date"]) - set(joined["date"]))
    if missing:
        first_weather = daily_weather["date"].min()
        last_weather = daily_weather["date"].max()
        internal = [date for date in missing if first_weather <= date <= last_weather]
        if internal:
            raise ValueError(f"weather missing for internal observed target dates: {internal[:10]}")
    if joined[FEATURES + ["consumption_mu"]].isna().any().any():
        raise ValueError("ML feature table contains missing values")
    return joined


def chronological_split(
    frame: pd.DataFrame,
    *,
    holdout_start: str = "2025-01-01",
) -> tuple[pd.DataFrame, pd.DataFrame]:
    boundary = pd.Timestamp(holdout_start)
    train = frame.loc[frame["date"] < boundary].copy()
    holdout = frame.loc[frame["date"] >= boundary].copy()
    if len(train) < 120 or len(holdout) < 45:
        raise ValueError("chronological split is too small for the declared experiment")
    if train["date"].max() >= holdout["date"].min():
        raise ValueError("chronological train/holdout ordering violated")
    return train, holdout


def regression_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> dict[str, float]:
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    rmse = float(math.sqrt(mean_squared_error(y_true, y_pred)))
    mae = float(mean_absolute_error(y_true, y_pred))
    if len(y_true) > 1 and np.std(y_true) > 0 and np.std(y_pred) > 0:
        corr = float(np.corrcoef(y_true, y_pred)[0, 1])
    else:
        corr = 0.0
    return {"mae_mu": mae, "rmse_mu": rmse, "correlation": corr}


def _calendar_baseline(
    train: pd.DataFrame,
    holdout: pd.DataFrame,
) -> tuple[Any, np.ndarray]:
    model = make_pipeline(StandardScaler(), Ridge(alpha=1.0))
    model.fit(train[CALENDAR_FEATURES], train["consumption_mu"])
    prediction = model.predict(holdout[CALENDAR_FEATURES])
    return model, np.asarray(prediction, dtype=float)


def _time_series_cv_rmse(
    model_factory: Callable[[dict[str, Any]], Any],
    params: dict[str, Any],
    x: pd.DataFrame,
    y: pd.Series,
    *,
    n_splits: int = 4,
) -> float:
    splitter = TimeSeriesSplit(n_splits=n_splits)
    scores = []
    for train_idx, val_idx in splitter.split(x):
        model = model_factory(params)
        model.fit(x.iloc[train_idx], y.iloc[train_idx])
        pred = model.predict(x.iloc[val_idx])
        scores.append(math.sqrt(mean_squared_error(y.iloc[val_idx], pred)))
    return float(np.mean(scores))


def _tune_lightgbm(
    train: pd.DataFrame,
    *,
    trials: int,
    seed: int,
) -> tuple[dict[str, Any], float]:
    import lightgbm as lgb
    import optuna

    optuna.logging.set_verbosity(optuna.logging.WARNING)
    x = train[FEATURES]
    y = train["consumption_mu"]

    def factory(params: dict[str, Any]) -> Any:
        return lgb.LGBMRegressor(
            objective="regression",
            random_state=seed,
            n_jobs=1,
            verbosity=-1,
            **params,
        )

    def objective(trial: Any) -> float:
        params = {
            "n_estimators": trial.suggest_int("n_estimators", 100, 500),
            "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.12, log=True),
            "num_leaves": trial.suggest_int("num_leaves", 8, 40),
            "max_depth": trial.suggest_int("max_depth", 3, 8),
            "min_child_samples": trial.suggest_int("min_child_samples", 8, 40),
            "subsample": trial.suggest_float("subsample", 0.65, 1.0),
            "colsample_bytree": trial.suggest_float("colsample_bytree", 0.65, 1.0),
            "reg_alpha": trial.suggest_float("reg_alpha", 1e-4, 3.0, log=True),
            "reg_lambda": trial.suggest_float("reg_lambda", 1e-4, 5.0, log=True),
        }
        return _time_series_cv_rmse(factory, params, x, y)

    study = optuna.create_study(
        direction="minimize",
        sampler=optuna.samplers.TPESampler(seed=seed),
    )
    study.optimize(objective, n_trials=trials, show_progress_bar=False)
    return dict(study.best_params), float(study.best_value)


def _tune_xgboost(
    train: pd.DataFrame,
    *,
    trials: int,
    seed: int,
) -> tuple[dict[str, Any], float]:
    import optuna
    import xgboost as xgb

    optuna.logging.set_verbosity(optuna.logging.WARNING)
    x = train[FEATURES]
    y = train["consumption_mu"]

    def factory(params: dict[str, Any]) -> Any:
        return xgb.XGBRegressor(
            objective="reg:squarederror",
            tree_method="hist",
            random_state=seed,
            n_jobs=1,
            **params,
        )

    def objective(trial: Any) -> float:
        params = {
            "n_estimators": trial.suggest_int("n_estimators", 100, 500),
            "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.12, log=True),
            "max_depth": trial.suggest_int("max_depth", 2, 7),
            "min_child_weight": trial.suggest_float("min_child_weight", 1.0, 20.0, log=True),
            "subsample": trial.suggest_float("subsample", 0.65, 1.0),
            "colsample_bytree": trial.suggest_float("colsample_bytree", 0.65, 1.0),
            "reg_alpha": trial.suggest_float("reg_alpha", 1e-4, 3.0, log=True),
            "reg_lambda": trial.suggest_float("reg_lambda", 1e-4, 5.0, log=True),
        }
        return _time_series_cv_rmse(factory, params, x, y)

    study = optuna.create_study(
        direction="minimize",
        sampler=optuna.samplers.TPESampler(seed=seed),
    )
    study.optimize(objective, n_trials=trials, show_progress_bar=False)
    return dict(study.best_params), float(study.best_value)


def _fit_boosted(
    name: str,
    params: dict[str, Any],
    train: pd.DataFrame,
    holdout: pd.DataFrame,
    *,
    seed: int,
) -> tuple[Any, np.ndarray]:
    if name == "lightgbm":
        import lightgbm as lgb

        model = lgb.LGBMRegressor(
            objective="regression",
            random_state=seed,
            n_jobs=1,
            verbosity=-1,
            **params,
        )
    elif name == "xgboost":
        import xgboost as xgb

        model = xgb.XGBRegressor(
            objective="reg:squarederror",
            tree_method="hist",
            random_state=seed,
            n_jobs=1,
            **params,
        )
    else:
        raise ValueError(f"unknown boosted model {name!r}")

    model.fit(train[FEATURES], train["consumption_mu"])
    return model, np.asarray(model.predict(holdout[FEATURES]), dtype=float)


def _shap_importance(model: Any, holdout: pd.DataFrame) -> pd.DataFrame:
    import shap

    explainer = shap.TreeExplainer(model)
    values = explainer.shap_values(holdout[FEATURES])
    array = np.asarray(values, dtype=float)
    if array.ndim != 2 or array.shape[1] != len(FEATURES):
        raise ValueError("unexpected SHAP output shape")
    return (
        pd.DataFrame(
            {
                "feature": FEATURES,
                "mean_abs_shap": np.mean(np.abs(array), axis=0),
            }
        )
        .sort_values("mean_abs_shap", ascending=False)
        .reset_index(drop=True)
    )


def run_daily_demand_ml(
    observed: pd.DataFrame,
    weather: pd.DataFrame,
    *,
    trials: int = 20,
    seed: int = 42,
    holdout_start: str = "2025-01-01",
    out_dir: Path | None = None,
) -> dict[str, Any]:
    """Run the v0.1 experiment and optionally persist machine-readable evidence."""
    table = build_daily_feature_table(observed, weather)
    train, holdout = chronological_split(table, holdout_start=holdout_start)

    _, baseline_pred = _calendar_baseline(train, holdout)
    baseline_metrics = regression_metrics(holdout["consumption_mu"], baseline_pred)

    tune_results = {
        "lightgbm": _tune_lightgbm(train, trials=trials, seed=seed),
        "xgboost": _tune_xgboost(train, trials=trials, seed=seed),
    }

    predictions = pd.DataFrame(
        {
            "date": holdout["date"].dt.strftime("%Y-%m-%d"),
            "observed_consumption_mu": holdout["consumption_mu"].to_numpy(),
            "calendar_ridge_mu": baseline_pred,
        }
    )
    fitted: dict[str, Any] = {}
    model_results: dict[str, Any] = {}

    for name, (params, cv_rmse) in tune_results.items():
        model, pred = _fit_boosted(name, params, train, holdout, seed=seed)
        metrics = regression_metrics(holdout["consumption_mu"], pred)
        beats = bool(metrics["rmse_mu"] < baseline_metrics["rmse_mu"])
        predictions[f"{name}_mu"] = pred
        fitted[name] = model
        model_results[name] = {
            "optuna_trials": int(trials),
            "best_params": params,
            "mean_time_series_cv_rmse_mu": float(cv_rmse),
            "holdout": metrics,
            "beats_calendar_baseline_on_holdout_rmse": beats,
            "shap": {
                "generated": False,
                "rule": "generated only when holdout RMSE beats calendar-only Ridge baseline",
            },
        }

    summary: dict[str, Any] = {
        "classification": CLASSIFICATION,
        "research_question": (
            "Do nonlinear calendar + same-day ERA5 weather features improve prediction "
            "of observed Kerala daily electricity consumption over a calendar-only baseline?"
        ),
        "target": {
            "field": "consumption_mu",
            "unit": "MU/day",
            "source_observed_rows": len(observed),
            "matched_observed_rows": len(table),
            "weather_boundary_excluded_dates": [
                date.date().isoformat()
                for date in sorted(set(observed["date"]) - set(table["date"]))
            ],
            "source": "public/daily-balance.json; Kerala SLDC daily system statistics",
            "hourly_telemetry_target": False,
            "reconstructed_hourly_proxy_used_as_target": False,
        },
        "weather": {
            "source": "verified ERA5 FY2024-25 source artifacts",
            "representative_points": int(weather["point"].nunique()),
            "spatial_aggregation": "equal-weight mean across five representative points",
            "same_day_features": WEATHER_FEATURES,
        },
        "validation": {
            "method": "chronological holdout + expanding TimeSeriesSplit inside training period",
            "train_start": train["date"].min().date().isoformat(),
            "train_end": train["date"].max().date().isoformat(),
            "train_rows": len(train),
            "holdout_start": holdout["date"].min().date().isoformat(),
            "holdout_end": holdout["date"].max().date().isoformat(),
            "holdout_rows": len(holdout),
        },
        "calendar_baseline": {
            "model": "StandardScaler + Ridge(alpha=1.0)",
            "features": CALENDAR_FEATURES,
            "holdout": baseline_metrics,
        },
        "models": model_results,
        "limitations": [
            "Only one financial year is used; this is a small-sample experiment.",
            "Weather uses five representative ERA5 points, not a population/load-weighted statewide field.",
            "Same-day weather association is not a causal elasticity estimate.",
            "The target is daily energy, not measured hourly or 15-minute load.",
            "SHAP explains model attribution under correlated features; it does not establish causality.",
            "A multi-year SLDC x ERA5 study is required before promoting this as a robust forecasting result.",
        ],
    }

    if out_dir is not None:
        out_dir.mkdir(parents=True, exist_ok=True)
        table.to_parquet(out_dir / "feature_table.parquet", index=False)
        predictions.to_csv(out_dir / "holdout_predictions.csv", index=False)

        for name, result in model_results.items():
            if not result["beats_calendar_baseline_on_holdout_rmse"]:
                continue
            importance = _shap_importance(fitted[name], holdout)
            importance.to_csv(out_dir / f"{name}_shap_importance.csv", index=False)
            result["shap"] = {
                "generated": True,
                "rule": "generated only when holdout RMSE beats calendar-only Ridge baseline",
                "top_features": importance.head(10).to_dict(orient="records"),
            }

        (out_dir / "summary.json").write_text(
            json.dumps(summary, indent=2, allow_nan=False) + "\n",
            encoding="utf-8",
        )
    return summary
