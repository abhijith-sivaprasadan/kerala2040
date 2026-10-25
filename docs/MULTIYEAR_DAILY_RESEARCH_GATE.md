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
