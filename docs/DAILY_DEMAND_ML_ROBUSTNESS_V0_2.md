# Daily demand ML robustness v0.2

**Classification:** experimental rolling-origin robustness and weather-feature ablation.

This study is the direct robustness extension of `DAILY_DEMAND_ML_V0_1.md`. It uses the same observed Kerala SLDC daily-consumption target and the same verified FY2024-25 ERA5 source chain. The reconstructed 8,760-hour load proxy is not used as a target or feature.

## Questions

### 1. Rolling robustness

Does the ERA5 weather gain survive multiple chronological test windows, or was the Jan-Mar 2025 v0.1 holdout unusually favourable?

Seven non-overlapping monthly holdouts are used:

- September 2024
- October 2024
- November 2024
- December 2024
- January 2025
- February 2025
- March 2025

For every fold:

1. training contains only dates before the holdout month;
2. LightGBM calendar-only is independently Optuna-tuned;
3. LightGBM calendar + all ERA5 weather is independently Optuna-tuned;
4. XGBoost calendar-only is independently Optuna-tuned;
5. XGBoost calendar + all ERA5 weather is independently Optuna-tuned;
6. the full weather model is compared against the tuned calendar-only model of the same family;
7. SHAP is calculated only for a fold in which weather improves holdout RMSE.

The key robustness quantities are:

- weather wins / 7 folds;
- median RMSE reduction from weather;
- worst-fold RMSE reduction;
- best-fold RMSE reduction;
- pooled out-of-sample MAE, RMSE and correlation.

A negative weather RMSE reduction is retained as a failure rather than hidden.

## 2. Weather feature-group ablation

The strongest v0.1 model family, XGBoost, is used to ask which weather families carry predictive information on the original Jan-Mar 2025 holdout.

Every variant retains the same calendar features and is independently Optuna-tuned.

Variants:

- calendar only;
- calendar + temperature;
- calendar + precipitation;
- calendar + shortwave radiation;
- calendar + wind;
- calendar + all weather except temperature;
- calendar + all weather.

### Temperature group

- mean temperature;
- maximum temperature;
- minimum temperature;
- daily temperature range;
- cooling degree-hours above 24 °C;
- hours above 30 °C.

### Precipitation group

- daily precipitation;
- wet-hour count.

### Radiation group

- daily downward shortwave-radiation total.

### Wind group

- mean 10 m wind speed;
- maximum 10 m wind speed.

The `all_except_temperature` variant is included to test whether the temperature family contributes information beyond the remaining weather variables.

## SHAP stability

For rolling folds where the full weather model beats its tuned calendar-only counterpart, mean absolute SHAP values are normalized to sum to one within each fold.

The study records:

- median normalized attribution;
- mean normalized attribution;
- median rank;
- top-five frequency across successful folds.

This is an attribution-stability diagnostic, not causal inference.

## Figures

The workflow produces:

- `rolling_predictions.png` — observed vs rolling XGBoost weather and calendar-only predictions;
- `weather_gain_by_fold.png` — incremental RMSE reduction from weather for both model families;
- `xgboost_shap_stability.png` — normalized XGBoost SHAP attribution across rolling folds;
- `feature_group_ablation.png` — Jan-Mar XGBoost feature-group RMSE comparison.

## Evidence boundary

This is still a one-financial-year retrospective study.

It does not establish:

- multi-year generalization;
- causal weather-demand elasticities;
- day-ahead forecasting performance;
- measured hourly or 15-minute forecasting performance.

Same-day realized ERA5 reanalysis is used. The purpose is to determine whether the weather signal seen in v0.1 is robust enough to justify the higher-cost next step: multi-year SLDC × ERA5 alignment.

## Run

    python -m pip install -e ".[dev,ml,era5]"
    python scripts/run_daily_demand_robustness_v0_2.py \
      --weather results/models/full_pypsa/era5_renewables_v0_6/weather_points.parquet \
      --trials 10

The reproducible workflow is `.github/workflows/daily-demand-ml-robustness-v0.2.yml`.
