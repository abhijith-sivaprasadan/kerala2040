"""Rolling-origin robustness and weather-group ablation for daily demand ML v0.2.

The v0.2 study reuses the v0.1 evidence contract but asks two harder questions:

1. Does adding ERA5 weather beat the same boosted model family without weather
   across multiple chronological holdout months?
2. Which weather feature groups carry the predictive gain?

Targets remain observed Kerala SLDC daily consumption. The reconstructed hourly load
proxy is never used as a target or feature.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from kerala2040.daily_demand_ml import (
    CALENDAR_FEATURES,
    FEATURES,
    _calendar_baseline,
    _fit_boosted,
    _shap_importance,
    _tune_lightgbm,
    _tune_xgboost,
    build_daily_feature_table,
    regression_metrics,
)

CLASSIFICATION = "experimental_daily_observed_demand_ml_robustness_v0_2"

TEMPERATURE_FEATURES = [
    "temp_mean_c",
    "temp_max_c",
    "temp_min_c",
    "temp_range_c",
    "cooling_degree_hours_24c",
    "hot_hours_gt30c",
]
PRECIPITATION_FEATURES = ["precip_mm_day", "wet_hours_gt0_1mm"]
RADIATION_FEATURES = ["ghi_kwh_m2_day"]
WIND_FEATURES = ["wind_mean_m_s", "wind_max_m_s"]

FEATURE_GROUPS = {
    "calendar_only": CALENDAR_FEATURES,
    "temperature": CALENDAR_FEATURES + TEMPERATURE_FEATURES,
    "precipitation": CALENDAR_FEATURES + PRECIPITATION_FEATURES,
    "radiation": CALENDAR_FEATURES + RADIATION_FEATURES,
    "wind": CALENDAR_FEATURES + WIND_FEATURES,
    "all_except_temperature": (
        CALENDAR_FEATURES
        + PRECIPITATION_FEATURES
        + RADIATION_FEATURES
        + WIND_FEATURES
    ),
    "all_weather": FEATURES,
}


@dataclass(frozen=True)
class RollingFold:
    label: str
    train_start: pd.Timestamp
    train_end: pd.Timestamp
    holdout_start: pd.Timestamp
    holdout_end: pd.Timestamp
    train_rows: int
    holdout_rows: int


def monthly_rolling_folds(
    table: pd.DataFrame,
    *,
    first_holdout: str = "2024-09-01",
    last_holdout: str = "2025-03-01",
    min_train_rows: int = 120,
) -> list[RollingFold]:
    """Build non-overlapping monthly holdouts with strictly past-only training."""
    dates = pd.to_datetime(table["date"], errors="raise")
    starts = pd.date_range(first_holdout, last_holdout, freq="MS")
    folds: list[RollingFold] = []

    for start in starts:
        end = start + pd.offsets.MonthEnd(1)
        train = table.loc[dates < start]
        holdout = table.loc[(dates >= start) & (dates <= end)]
        if len(train) < min_train_rows:
            raise ValueError(
                f"{start.date()} has only {len(train)} training rows; "
                f"minimum is {min_train_rows}"
            )
        if holdout.empty:
            raise ValueError(f"{start.date()} has no observed holdout rows")
        folds.append(
            RollingFold(
                label=start.strftime("%Y-%m"),
                train_start=pd.Timestamp(train["date"].min()),
                train_end=pd.Timestamp(train["date"].max()),
                holdout_start=pd.Timestamp(holdout["date"].min()),
                holdout_end=pd.Timestamp(holdout["date"].max()),
                train_rows=len(train),
                holdout_rows=len(holdout),
            )
        )
    return folds


def _tune_model(
    name: str,
    train: pd.DataFrame,
    *,
    features: list[str],
    trials: int,
    seed: int,
) -> tuple[dict[str, Any], float]:
    if name == "lightgbm":
        return _tune_lightgbm(
            train,
            features=features,
            trials=trials,
            seed=seed,
        )
    if name == "xgboost":
        return _tune_xgboost(
            train,
            features=features,
            trials=trials,
            seed=seed,
        )
    raise ValueError(f"unknown boosted model {name!r}")


def _pct_reduction(reference: float, candidate: float) -> float:
    if reference <= 0:
        raise ValueError("reference metric must be positive")
    return 100.0 * (reference - candidate) / reference


def _pooled_metrics(
    predictions: pd.DataFrame,
    prediction_column: str,
) -> dict[str, float]:
    return regression_metrics(
        predictions["observed_consumption_mu"].to_numpy(),
        predictions[prediction_column].to_numpy(),
    )


def _plot_rolling_predictions(predictions: pd.DataFrame, out_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(11.5, 4.8))
    ax.plot(
        predictions["date"],
        predictions["observed_consumption_mu"],
        label="Observed SLDC",
        linewidth=1.8,
    )
    ax.plot(
        predictions["date"],
        predictions["xgboost_weather_mu"],
        label="XGBoost + ERA5",
        linewidth=1.35,
    )
    ax.plot(
        predictions["date"],
        predictions["xgboost_calendar_only_mu"],
        label="XGBoost calendar-only",
        linewidth=1.1,
        alpha=0.8,
    )
    ax.set_ylabel("Daily consumption (MU)")
    ax.set_xlabel("Chronological rolling holdout date")
    ax.set_title("Kerala daily demand: rolling out-of-sample predictions")
    ax.legend(frameon=False, ncol=3)
    ax.grid(axis="y", alpha=0.2)
    fig.tight_layout()
    fig.savefig(out_path, dpi=220, bbox_inches="tight")
    plt.close(fig)


def _plot_weather_gain(fold_metrics: pd.DataFrame, out_path: Path) -> None:
    pivot = fold_metrics.pivot(
        index="fold",
        columns="model",
        values="weather_rmse_reduction_pct",
    )
    ax = pivot.plot(kind="bar", figsize=(10.2, 4.8), width=0.78)
    ax.axhline(0.0, linewidth=0.8)
    ax.set_ylabel("RMSE reduction vs tuned calendar-only (%)")
    ax.set_xlabel("Monthly holdout")
    ax.set_title("Incremental value of ERA5 weather by rolling holdout")
    ax.legend(title=None, frameon=False)
    ax.grid(axis="y", alpha=0.2)
    ax.figure.tight_layout()
    ax.figure.savefig(out_path, dpi=220, bbox_inches="tight")
    plt.close(ax.figure)


def _plot_shap_stability(stability: pd.DataFrame, out_path: Path) -> None:
    xgb = stability.loc[stability["model"] == "xgboost"].copy()
    if xgb.empty:
        return
    top = (
        xgb.groupby("feature", as_index=False)["normalized_abs_shap"]
        .median()
        .sort_values("normalized_abs_shap", ascending=False)
        .head(10)["feature"]
        .tolist()
    )
    plot = xgb.loc[xgb["feature"].isin(top)]
    pivot = plot.pivot(
        index="fold",
        columns="feature",
        values="normalized_abs_shap",
    )
    ax = pivot.plot(figsize=(11.0, 5.2), marker="o")
    ax.set_ylabel("Share of total |SHAP|")
    ax.set_xlabel("Monthly holdout")
    ax.set_title("XGBoost feature-attribution stability across rolling holdouts")
    ax.legend(title="Feature", bbox_to_anchor=(1.02, 1), loc="upper left", frameon=False)
    ax.grid(axis="y", alpha=0.2)
    ax.figure.tight_layout()
    ax.figure.savefig(out_path, dpi=220, bbox_inches="tight")
    plt.close(ax.figure)


def _plot_feature_group_ablation(ablation: pd.DataFrame, out_path: Path) -> None:
    ordered = ablation.sort_values("holdout_rmse_mu", ascending=True)
    ax = ordered.plot(
        kind="barh",
        x="variant",
        y="holdout_rmse_mu",
        figsize=(8.6, 4.8),
        legend=False,
    )
    ax.set_xlabel("Jan-Mar 2025 holdout RMSE (MU/day)")
    ax.set_ylabel("")
    ax.set_title("XGBoost feature-group ablation")
    ax.grid(axis="x", alpha=0.2)
    ax.figure.tight_layout()
    ax.figure.savefig(out_path, dpi=220, bbox_inches="tight")
    plt.close(ax.figure)


def run_rolling_robustness(
    observed: pd.DataFrame,
    weather: pd.DataFrame,
    *,
    trials: int = 10,
    seed: int = 42,
    first_holdout: str = "2024-09-01",
    last_holdout: str = "2025-03-01",
    out_dir: Path | None = None,
) -> dict[str, Any]:
    """Run rolling model-family robustness plus XGBoost feature-group ablation."""
    table = build_daily_feature_table(observed, weather)
    folds = monthly_rolling_folds(
        table,
        first_holdout=first_holdout,
        last_holdout=last_holdout,
    )

    fold_rows: list[dict[str, Any]] = []
    prediction_frames: list[pd.DataFrame] = []
    shap_rows: list[pd.DataFrame] = []
    fold_details: list[dict[str, Any]] = []

    for fold_index, fold in enumerate(folds):
        train = table.loc[table["date"] <= fold.train_end].copy()
        holdout = table.loc[
            (table["date"] >= fold.holdout_start)
            & (table["date"] <= fold.holdout_end)
        ].copy()

        _, ridge_pred = _calendar_baseline(train, holdout)
        ridge_metrics = regression_metrics(holdout["consumption_mu"], ridge_pred)

        fold_pred = pd.DataFrame(
            {
                "date": holdout["date"].to_numpy(),
                "fold": fold.label,
                "observed_consumption_mu": holdout["consumption_mu"].to_numpy(),
                "ridge_calendar_mu": ridge_pred,
            }
        )
        detail: dict[str, Any] = {
            "fold": fold.label,
            "train_start": fold.train_start.date().isoformat(),
            "train_end": fold.train_end.date().isoformat(),
            "train_rows": fold.train_rows,
            "holdout_start": fold.holdout_start.date().isoformat(),
            "holdout_end": fold.holdout_end.date().isoformat(),
            "holdout_rows": fold.holdout_rows,
            "ridge_calendar": ridge_metrics,
            "models": {},
        }

        for model_index, name in enumerate(["lightgbm", "xgboost"]):
            model_seed = seed + fold_index * 1000 + model_index * 100
            calendar_params, calendar_cv = _tune_model(
                name,
                train,
                features=CALENDAR_FEATURES,
                trials=trials,
                seed=model_seed + 1,
            )
            weather_params, weather_cv = _tune_model(
                name,
                train,
                features=FEATURES,
                trials=trials,
                seed=model_seed + 2,
            )

            _, calendar_pred = _fit_boosted(
                name,
                calendar_params,
                train,
                holdout,
                features=CALENDAR_FEATURES,
                seed=model_seed + 1,
            )
            weather_model, weather_pred = _fit_boosted(
                name,
                weather_params,
                train,
                holdout,
                features=FEATURES,
                seed=model_seed + 2,
            )

            calendar_metrics = regression_metrics(
                holdout["consumption_mu"],
                calendar_pred,
            )
            weather_metrics = regression_metrics(
                holdout["consumption_mu"],
                weather_pred,
            )
            gain = _pct_reduction(
                calendar_metrics["rmse_mu"],
                weather_metrics["rmse_mu"],
            )
            weather_win = bool(
                weather_metrics["rmse_mu"] < calendar_metrics["rmse_mu"]
            )

            fold_pred[f"{name}_calendar_only_mu"] = calendar_pred
            fold_pred[f"{name}_weather_mu"] = weather_pred
            fold_rows.append(
                {
                    "fold": fold.label,
                    "model": name,
                    "train_rows": fold.train_rows,
                    "holdout_rows": fold.holdout_rows,
                    "calendar_rmse_mu": calendar_metrics["rmse_mu"],
                    "weather_rmse_mu": weather_metrics["rmse_mu"],
                    "calendar_mae_mu": calendar_metrics["mae_mu"],
                    "weather_mae_mu": weather_metrics["mae_mu"],
                    "calendar_correlation": calendar_metrics["correlation"],
                    "weather_correlation": weather_metrics["correlation"],
                    "weather_rmse_reduction_pct": gain,
                    "weather_wins_rmse": weather_win,
                }
            )

            model_detail = {
                "optuna_trials_per_variant": trials,
                "calendar_only": {
                    "best_params": calendar_params,
                    "mean_time_series_cv_rmse_mu": calendar_cv,
                    "holdout": calendar_metrics,
                },
                "weather": {
                    "best_params": weather_params,
                    "mean_time_series_cv_rmse_mu": weather_cv,
                    "holdout": weather_metrics,
                },
                "weather_rmse_reduction_pct": gain,
                "weather_wins_rmse": weather_win,
            }

            if weather_win:
                importance = _shap_importance(
                    weather_model,
                    holdout,
                    features=FEATURES,
                )
                total = float(importance["mean_abs_shap"].sum())
                importance["normalized_abs_shap"] = (
                    importance["mean_abs_shap"] / total if total > 0 else 0.0
                )
                importance["fold"] = fold.label
                importance["model"] = name
                importance["rank"] = np.arange(1, len(importance) + 1)
                shap_rows.append(importance)
                model_detail["shap_generated"] = True
            else:
                model_detail["shap_generated"] = False

            detail["models"][name] = model_detail

        prediction_frames.append(fold_pred)
        fold_details.append(detail)

    fold_metrics = pd.DataFrame(fold_rows)
    predictions = pd.concat(prediction_frames, ignore_index=True).sort_values("date")
    shap_stability = (
        pd.concat(shap_rows, ignore_index=True)
        if shap_rows
        else pd.DataFrame(
            columns=[
                "feature",
                "mean_abs_shap",
                "normalized_abs_shap",
                "fold",
                "model",
                "rank",
            ]
        )
    )

    rolling_summary: dict[str, Any] = {}
    for name in ["lightgbm", "xgboost"]:
        subset = fold_metrics.loc[fold_metrics["model"] == name].copy()
        gains = subset["weather_rmse_reduction_pct"].to_numpy()
        rolling_summary[name] = {
            "fold_count": len(subset),
            "weather_rmse_wins": int(subset["weather_wins_rmse"].sum()),
            "weather_rmse_win_rate": float(subset["weather_wins_rmse"].mean()),
            "median_weather_rmse_reduction_pct": float(np.median(gains)),
            "mean_weather_rmse_reduction_pct": float(np.mean(gains)),
            "worst_weather_rmse_reduction_pct": float(np.min(gains)),
            "best_weather_rmse_reduction_pct": float(np.max(gains)),
            "pooled_calendar_only": _pooled_metrics(
                predictions,
                f"{name}_calendar_only_mu",
            ),
            "pooled_weather": _pooled_metrics(
                predictions,
                f"{name}_weather_mu",
            ),
        }

    # Feature-group ablation uses the same untouched Jan-Mar window as v0.1.
    ablation_train = table.loc[table["date"] < pd.Timestamp("2025-01-01")].copy()
    ablation_holdout = table.loc[table["date"] >= pd.Timestamp("2025-01-01")].copy()
    ablation_rows: list[dict[str, Any]] = []
    ablation_detail: dict[str, Any] = {}

    for index, (variant, features) in enumerate(FEATURE_GROUPS.items()):
        variant_seed = seed + 9000 + index * 37
        params, cv_rmse = _tune_model(
            "xgboost",
            ablation_train,
            features=features,
            trials=trials,
            seed=variant_seed,
        )
        _, pred = _fit_boosted(
            "xgboost",
            params,
            ablation_train,
            ablation_holdout,
            features=features,
            seed=variant_seed,
        )
        metrics = regression_metrics(ablation_holdout["consumption_mu"], pred)
        ablation_rows.append(
            {
                "variant": variant,
                "feature_count": len(features),
                "holdout_mae_mu": metrics["mae_mu"],
                "holdout_rmse_mu": metrics["rmse_mu"],
                "holdout_correlation": metrics["correlation"],
            }
        )
        ablation_detail[variant] = {
            "features": features,
            "best_params": params,
            "mean_time_series_cv_rmse_mu": cv_rmse,
            "holdout": metrics,
        }

    ablation = pd.DataFrame(ablation_rows)
    calendar_rmse = float(
        ablation.loc[
            ablation["variant"] == "calendar_only",
            "holdout_rmse_mu",
        ].iloc[0]
    )
    ablation["rmse_reduction_vs_calendar_pct"] = [
        _pct_reduction(calendar_rmse, value)
        for value in ablation["holdout_rmse_mu"]
    ]

    shap_summary: dict[str, Any] = {}
    if not shap_stability.empty:
        for name in ["lightgbm", "xgboost"]:
            subset = shap_stability.loc[shap_stability["model"] == name]
            if subset.empty:
                continue
            grouped = (
                subset.groupby("feature", as_index=False)
                .agg(
                    median_normalized_abs_shap=(
                        "normalized_abs_shap",
                        "median",
                    ),
                    mean_normalized_abs_shap=(
                        "normalized_abs_shap",
                        "mean",
                    ),
                    median_rank=("rank", "median"),
                    top5_frequency=("rank", lambda values: float((values <= 5).mean())),
                )
                .sort_values("median_normalized_abs_shap", ascending=False)
            )
            shap_summary[name] = grouped.head(12).to_dict(orient="records")

    summary = {
        "classification": CLASSIFICATION,
        "target": {
            "source_observed_rows": len(observed),
            "matched_observed_rows": len(table),
            "reconstructed_hourly_proxy_used_as_target": False,
        },
        "rolling_design": {
            "first_holdout": folds[0].holdout_start.date().isoformat(),
            "last_holdout": folds[-1].holdout_end.date().isoformat(),
            "folds": [fold.label for fold in folds],
            "fold_count": len(folds),
            "training_rule": "strictly earlier dates only; expanding window",
            "optuna_trials_per_model_variant_per_fold": trials,
        },
        "rolling_summary": rolling_summary,
        "fold_details": fold_details,
        "shap_stability": shap_summary,
        "feature_group_ablation": {
            "model": "xgboost",
            "holdout": "2025-01-01/2025-03-31",
            "optuna_trials_per_variant": trials,
            "variants": ablation_detail,
            "table": ablation.to_dict(orient="records"),
        },
        "limitations": [
            "All robustness folds still come from one financial year.",
            "Same-day realized ERA5 reanalysis makes this retrospective prediction, not day-ahead forecasting.",
            "Five representative ERA5 points are equally weighted rather than load weighted.",
            "Feature-group ablation is run with XGBoost only because it was the strongest v0.1 model.",
            "SHAP stability is model attribution under correlated features, not causal inference.",
            "Holiday/event indicators are not included in the current feature set.",
        ],
    }

    if out_dir is not None:
        out_dir.mkdir(parents=True, exist_ok=True)
        fold_metrics.to_csv(out_dir / "rolling_fold_metrics.csv", index=False)
        predictions.to_csv(out_dir / "rolling_predictions.csv", index=False)
        shap_stability.to_csv(out_dir / "rolling_shap_stability.csv", index=False)
        ablation.to_csv(out_dir / "feature_group_ablation.csv", index=False)
        (out_dir / "summary.json").write_text(
            json.dumps(summary, indent=2, allow_nan=False) + "\n",
            encoding="utf-8",
        )
        _plot_rolling_predictions(
            predictions,
            out_dir / "rolling_predictions.png",
        )
        _plot_weather_gain(
            fold_metrics,
            out_dir / "weather_gain_by_fold.png",
        )
        _plot_shap_stability(
            shap_stability,
            out_dir / "xgboost_shap_stability.png",
        )
        _plot_feature_group_ablation(
            ablation,
            out_dir / "feature_group_ablation.png",
        )

    return summary
