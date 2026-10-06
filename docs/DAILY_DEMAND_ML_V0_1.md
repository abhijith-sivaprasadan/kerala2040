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
2. **LightGBM:** tuned with Optuna.
3. **XGBoost:** tuned with Optuna.

Optuna minimizes mean RMSE over expanding `TimeSeriesSplit` folds inside the training period.

## Holdout rule

- training: Apr-Dec 2024 observations
- untouched holdout: Jan-Mar 2025 observations

The split is chronological. Random train/test splitting is not used.

## SHAP rule

SHAP is generated **only** for a boosted model whose Jan-Mar holdout RMSE beats the calendar-only Ridge baseline.

SHAP values are treated as model attribution under correlated features, not as causal demand elasticities.

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
