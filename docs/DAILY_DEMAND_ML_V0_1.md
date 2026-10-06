# Daily observed-demand ML v0.1

**Classification:** experimental daily observed-demand ML; not an hourly forecast and not measured-hour validation.

## Purpose

This experiment asks a narrow question:

> Do nonlinear calendar + same-day ERA5 weather features improve prediction of **observed Kerala daily electricity consumption** over a simple calendar-only baseline?

It exists to test whether LightGBM/XGBoost add genuine predictive information to the current Kerala2040 evidence base. It does **not** train against the reconstructed 8,760-hour load proxy.

## Evidence used

### Target

- `public/daily-balance.json`
- Kerala SLDC daily electricity consumption, in MU/day
- 354 published FY2024-25 daily observations
- missing dates are not interpolated for the ML target

### Weather

The workflow downloads the already recovered and independently QA-checked FY2024-25 ERA5 source artifacts used elsewhere in Kerala2040.

Five representative locations are used:

- Thiruvananthapuram
- Kochi
- Palakkad
- Kozhikode
- Kannur

Hourly temperature, wind, downward shortwave radiation and precipitation are converted to local IST, equal-weighted across the five points and aggregated to daily features.

This is a screening representation, not a population/load-weighted statewide meteorological field.

## Features

Calendar:

- day-of-year sine/cosine
- day-of-week sine/cosine
- month sine/cosine
- weekend flag

Same-day ERA5:

- mean / maximum / minimum temperature
- daily temperature range
- cooling degree-hours above 24 °C
- hours above 30 °C
- daily shortwave-radiation total
- daily precipitation
- wet hours
- mean / maximum 10 m wind speed

No reconstructed hourly demand value is used as a feature or target.

## Models

1. **Calendar baseline:** standardized Ridge regression.
2. **LightGBM calendar-only ablation:** calendar features only, independently tuned with Optuna.
3. **LightGBM full model:** calendar + ERA5 weather features, independently tuned with Optuna.
4. **XGBoost calendar-only ablation:** calendar features only, independently tuned with Optuna.
5. **XGBoost full model:** calendar + ERA5 weather features, independently tuned with Optuna.

Optuna minimizes mean RMSE over expanding `TimeSeriesSplit` folds inside the training period. The calendar-only boosted variants are necessary to distinguish a **weather contribution** from a gain that could come only from using a nonlinear model family.

## Holdout rule

- training: Apr-Dec 2024 observations
- untouched holdout: Jan-Mar 2025 observations

The split is chronological. Random train/test splitting is not used.

## SHAP rule

SHAP is generated **only** for a full weather model whose Jan-Mar holdout RMSE beats **both** the linear Ridge calendar baseline and the independently tuned calendar-only version of the same boosted model family.

This creates a stricter gate: the full model must show incremental out-of-sample value from the weather feature set before SHAP is used to interpret it. SHAP values are still model attribution under correlated features, not causal demand elasticities.

## Real FY2024-25 result

Reference workflow run: `37394745601` on commit `ec359eb95aba5a6c1e7288253153f8ea57486929`.

The experiment matched **353 of 354** published daily SLDC observations to complete local-day ERA5 weather. **2024-04-01** was excluded because the recovered ERA5 artifact begins at 00:00 UTC, leaving only 19 hours for that first IST calendar day. No missing hours were fabricated.

Training used **267 observations from 2 April through 31 December 2024**. The untouched holdout contains **86 observations from 1 January through 31 March 2025**.

| Model | Weather? | Holdout MAE (MU/day) | Holdout RMSE (MU/day) | Correlation |
|---|---:|---:|---:|---:|
| Ridge calendar baseline | No | 7.893 | 9.188 | 0.703 |
| LightGBM, tuned calendar-only | No | 6.123 | 7.150 | 0.888 |
| **LightGBM, tuned calendar + ERA5** | **Yes** | **3.139** | **3.778** | **0.932** |
| XGBoost, tuned calendar-only | No | 6.649 | 7.659 | 0.864 |
| **XGBoost, tuned calendar + ERA5** | **Yes** | **2.623** | **3.179** | **0.922** |

Against the independently Optuna-tuned calendar-only version of the same model family, adding ERA5 weather reduces holdout RMSE by:

- **47.16% for LightGBM**
- **58.50% for XGBoost**

This ablation is the important result. It shows that the improvement is not explained only by replacing a linear calendar model with gradient-boosted trees. In this one-year experiment, the same boosted model families perform substantially better when same-day ERA5 weather information is added.

Both models therefore passed the SHAP gate. The largest SHAP attribution remains the annual-cycle term `doy_sin`, but **mean temperature is the second-ranked feature in both models**. Temperature minima/maxima, cooling degree-hours and precipitation also appear among leading attributions. These are model attributions, not causal elasticities.

XGBoost has the lowest holdout MAE and RMSE; LightGBM has the slightly higher holdout correlation. That does not justify choosing a permanent "winner" from one financial year.

The machine-readable evidence snapshot is committed at `data/evidence/daily_demand_ml_v0_1_2026_10_06.json`.

### What this result supports

It supports the bounded statement:

> In a one-financial-year retrospective experiment, adding same-day ERA5 weather features materially improved out-of-sample prediction of observed Kerala daily electricity consumption relative to independently tuned calendar-only LightGBM and XGBoost models.

It does **not** support the claims that weather causes the inferred demand changes, that the model is an operational day-ahead forecaster, or that it has been validated across multiple years.

Same-day **realized reanalysis weather** is used, so this is retrospective weather-demand modelling. The next high-value validation is a multi-year SLDC × ERA5 replication.

## Promotion gate

The v0.1 result remains experimental even if a boosted model wins.

It should be promoted into the main public findings only if:

1. a boosted model materially beats the calendar baseline on the untouched holdout;
2. the result is stable enough to survive sensitivity checks; and
3. the same modelling contract can later be repeated over a multi-year SLDC × ERA5 dataset.

The preferred next research step is multi-year alignment, not training on reconstructed hourly targets.

## Run

    python -m pip install -e ".[dev,ml,era5]"
    python scripts/run_daily_demand_ml_v0_1.py \
      --weather results/models/full_pypsa/era5_renewables_v0_6/weather_points.parquet \
      --trials 20

The GitHub Actions workflow `.github/workflows/daily-demand-ml-v0.1.yml` performs the full source-artifact recovery, QA, feature build, model tuning, holdout evaluation and conditional SHAP generation.
