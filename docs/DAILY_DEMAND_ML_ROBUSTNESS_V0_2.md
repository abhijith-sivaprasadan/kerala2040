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

## Real FY2024-25 robustness result

Reference workflow run: `37407105070` on commit `5e7b9dbbec3b6be43e882e218864fe4d78e1ce15`.

The rolling-origin test supports the v0.1 weather signal, but not uniformly in every month.

### Rolling monthly holdouts

| Holdout | LightGBM weather RMSE change | XGBoost weather RMSE change |
|---|---:|---:|
| Sep 2024 | +16.33% | +10.77% |
| Oct 2024 | -3.37% | +7.79% |
| Nov 2024 | -2.44% | -3.66% |
| Dec 2024 | +20.71% | +40.82% |
| Jan 2025 | +57.49% | +43.98% |
| Feb 2025 | +57.31% | +60.28% |
| Mar 2025 | +24.47% | +13.52% |

Positive values mean that adding ERA5 weather reduced holdout RMSE relative to an independently Optuna-tuned calendar-only model of the same family.

- **LightGBM:** weather wins 5 of 7 folds; median RMSE reduction **20.71%**.
- **XGBoost:** weather wins 6 of 7 folds; median RMSE reduction **13.52%**.
- **November 2024 is the shared failure month.**
- LightGBM also loses slightly in October, while XGBoost still improves.

Across all seven non-overlapping holdouts pooled together:

| Model family | Calendar-only RMSE | Weather RMSE | Pooled RMSE reduction | Weather correlation |
|---|---:|---:|---:|---:|
| LightGBM | 4.657 MU/day | 2.903 MU/day | **37.67%** | 0.892 |
| XGBoost | 4.558 MU/day | 2.865 MU/day | **37.13%** | 0.898 |

This is materially stronger evidence than the original single Jan-Mar split. It also shows that the effect is conditional rather than universal.

### XGBoost feature-group ablation

The original Jan-Mar 2025 holdout was then rerun with independently tuned XGBoost variants.

| Variant | Holdout RMSE | RMSE change vs calendar-only |
|---|---:|---:|
| Calendar only | 6.557 MU/day | — |
| **Calendar + temperature** | **3.402 MU/day** | **+48.11%** |
| Calendar + precipitation | 6.813 MU/day | -3.91% |
| Calendar + radiation | 9.146 MU/day | -39.49% |
| Calendar + wind | 6.720 MU/day | -2.49% |
| Calendar + all weather except temperature | 6.683 MU/day | -1.93% |
| Calendar + all weather | 4.227 MU/day | +35.53% |

Within this holdout, the temperature family carries essentially all of the useful weather signal. Removing temperature eliminates the weather gain; adding all weather performs better than calendar-only but worse than temperature alone.

That should not be read as "radiation, rainfall and wind never matter." With only one financial year and a small sample, the extra groups can add variance and tuning burden. The result supports the narrower claim that **temperature is the dominant currently demonstrated weather predictor**.

### Attribution stability

SHAP stability agrees with the ablation but keeps the calendar signal in perspective.

For LightGBM winning folds:

- annual-cycle `doy_sin`: median 24.9% of total absolute SHAP; top-five in 100% of winning folds;
- mean temperature: median 13.5%; top-five in 80%;
- maximum temperature: median 9.5%; top-five in 60%.

For XGBoost winning folds:

- annual-cycle `doy_sin`: median 32.5%; top-five in 100%;
- maximum temperature: median 7.8%; top-five in 66.7%;
- mean temperature: median 5.1%; top-five in 33.3%.

So the models still rely heavily on seasonality. The weather contribution is real in out-of-sample error terms, but SHAP does not justify a causal interpretation.

### Current promotion status

The v0.2 result passes the **within-year robustness** gate: the weather gain survives most independent monthly holdouts and two different boosted-tree families.

It does **not** yet pass the multi-year generalization gate. The next high-value validation remains a multi-year SLDC × ERA5 replication.

The exact machine-readable result is frozen at:

`data/evidence/daily_demand_ml_robustness_v0_2_2026_10_06.json`

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
