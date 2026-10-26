# Multi-year observed daily Kerala demand: source admission and evaluation

The 2019–2026 daily SLDC source archive has already been curated into a
**private** `kerala2040-source-archive` repository. It has 2,606 dated
source days. Qualified fiscal years include 2020–21 (365 source days),
2021–22 (362), 2022–23 (362), 2023–24 (365), 2024–25 (354) and
2025–26 (356). The observed daily consumption is not the unobserved
full-hourly power system; do not infer interval load from it.

This work adds a source-hash admission contract: the private compressed
`daily_system.csv.gz` must match the original private
`PRIVATE_DERIVED_SLDC_MANIFEST.json` at both gzip and uncompressed CSV
hashes. Only records with `energy_balance_qualified=True` and a positive
`consumption_qualified_mu` are admitted. Source rows must remain private
pending third-party redistribution rights review.

A fixed, non-tuned Ridge comparison can then evaluate calendar-only
against calendar plus same-day ERA5 across sequential FY2022–23, FY2023–24
and FY2024–25 retrospective holdouts, with all training dates before each
test date. No future demand target is permitted in a training fold.
**This analysis is not complete yet:** historical hourly ERA5 files matching
the full multi-year observed window (IST aggregation, pinned original source
and five geographic sampling points) have not been admitted. The runner
fails on missing weather days instead of reusing FY2024–25 weather or
inventing meteorological values.

Private invocation (do not run with confidential inputs on public CI):

```bash
python scripts/run_multiyear_daily_study.py \
  --private-daily-gzip PRIVATE/daily_system.csv.gz \
  --private-manifest PRIVATE/PRIVATE_DERIVED_SLDC_MANIFEST.json \
  --weather-parquet PRIVATE/weather_points_multiyear.parquet \
  --output PRIVATE/results/multiyear_era5_qa.json
```

The first prerequisite is original multi-year ERA5 weather with explicit
source hashes and no full-period gaps. Previously inspected later years
mean these are **retrospective rolling evaluations, not blind forecasts**.
The public research freeze is unchanged until independently reviewed inputs
and results are admitted in a separate PR.

## Normalized five-point ERA5 panel gate — 26 October 2026

Before the existing fixed-Ridge retrospective comparison fits a model, it now
calls `audit_multiyear_weather_panel` in
`src/kerala2040/multiyear_daily_study.py`. For **every SLDC observed IST
target date**, it requires exactly **24 UTC whole-hour timestamps at each of
the same five declared representative ERA5 locations**. This explicitly
rejects missing one-location hours, duplicate point-hour pairs, timezone-naive
timestamps, off-grid sampling and unrecognised/missing locations. One present
hour at four locations is **not** a legitimate five-point hourly mean.

The day boundary is **India Standard Time (UTC+05:30)**, so exact UTC
HH:00 source instants fall at local HH:30. Missing non-target SLDC days
are not invented. The existing source-target reader still admits only
`energy_balance_qualified=True` SLDC daily observations from the
private hash-verified source archive.

The private runner now records the normalized Parquet's SHA-256, separately
from original Copernicus artifact provenance. **A Parquet hash verifies the
file inspected, not the underlying ERA5 acquisition, sampling geometry,
forecast/accumulation conversion, or scientific fitness.** The new panel
verdict is therefore labelled
`normalized_reanalysis_weather_panel_qa_not_source_authentication`,
and explicitly says upstream original source hashes were *not* verified by
that operation. Earlier FY2024–25 robustness figures and public evidence
freeze are unchanged.

### Acceptance remains blocked

The independently pinned, original-source-hash verified, multi-year
2019–2025 ERA5 hourly table across five geographic points has **not been
supplied/admitted**. Passing the synthetic QA tests is software verification,
not a positive historical weather result. Once genuine multi-year source
artifacts are acquired, independently verify source bytes and point/grid
selection before using this panel preflight and fitting. Keep source rows
private until redistribution rights are reviewed. Do not rebrand same-day
reanalysis as day-ahead forecasting.
