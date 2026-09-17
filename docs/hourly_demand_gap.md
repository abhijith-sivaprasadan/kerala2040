# Kerala hourly-demand data gap

## Status

**Not yet secured as a complete public historical series for FY2024-25.**

Kerala SLDC exposes strong daily system statistics and daily reservoir information, but the public
interfaces currently connected by this project do not provide a complete state 15-minute demand
archive. Grid-India Daily PSP supplies independent daily energy/peak data; its workbook `TimeSeries`
sheet is national rather than Kerala-specific.

## Evidence that higher-resolution Kerala data exist

- CSTEP's 2024 Kerala Energy Transition Roadmap analysed a 15-minute Kerala load curve and says
  its FY22 shape was extrapolated from FY16 observations.
- The Kerala Resource Adequacy Plan up to 2031-32 analyses the state's FY2022-23 hourly demand
  pattern and seasonal hourly profiles.
- Kerala planning/demand-forecast regulations require distribution licensees to maintain historical
  hourly or sub-hourly demand data and provide state-level forecasts through SLDC.
- Kerala's 2026 Carbon Neutral Pathway shows peak-day hourly demand curves for multiple historical years.

These documents prove analytical use of hourly data; they do **not** by themselves provide the raw
8,760/35,040-row series needed for reproducible model calibration.

## Safe fallback order

1. Continue searching primary SLDC/KSEBL/KSERC/CEA/Grid-India downloadable archives.
2. If no public raw series is available, request the historical series from KSEBL/SLDC or obtain it
   from a user-supplied source.
3. For CET-only prototyping, a published/profile-based reconstruction may be built, but it must be
   tagged `proxy` and constrained to exactly match validated daily/annual energy and published peak
   metrics. It must not be presented as measured telemetry.

This gate is deliberate: PyPSA can optimize a mathematically clean synthetic curve and still produce
misleading conclusions if the evening peak, monsoon seasonality or hydro/import covariance are wrong.
