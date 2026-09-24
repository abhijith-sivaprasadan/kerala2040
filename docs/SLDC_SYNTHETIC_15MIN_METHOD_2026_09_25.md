# FY2024–25 daily-anchored synthetic quarter-hour demand — research prototype

**Classification:** `SYNTHETIC_15MIN_DAILY_SLDC_ANCHORED_NOT_OBSERVED_INTERVAL_LOAD`.

Run from repository root:

```bash
python scripts/build_sldc_synthetic_15min.py --out-dir outputs/sldc_synthetic_15min
pytest -q tests/test_sldc_synthetic_15min.py
```

Exports: `daily_anchors.csv` (365 rows, observation status and source hash), `synthetic_15min.csv` (96 quarter-hours × available days × 3 explicitly assumed shapes), and `qa.json` (observed and estimated contributions, leave-one-observed-day-out benchmark and limitations). IST and UTC interval-start timestamps are included. Each modelled daily shape is exactly reconciled to its own SLDC daily MU: sum of interval-average MW × 0.25 hours = daily MU × 1000 MWh. Hourly average MW = mean of four consecutive quarter-hour MW.

The official FY2024–25 daily archive reports 354 observed days and 11 missing. By default the missing dates are filled with **labelled candidate local linear interpolation**, only where observed bracketing dates are within seven days; `--no-estimate-missing` leaves them unavailable. This does not reconstruct measured data. The blind benchmark compares interpolation against a local median on held-out *observed* days; neither benchmark nor its errors validates the quarter-hour shape or calibrates a confidence interval. Do not describe estimated-day totals as official annual consumption.

The normalized same-calendar-date cross-year method is implemented as a **separate, private-input benchmark** in `analysis/benchmark_sldc_cross_year_gaps.py`. The admitted FY2024–25 public CSV alone cannot run it. Retrieve the qualified `daily_system.csv` from the private curated archive and run:\n\n```bash\npython analysis/benchmark_sldc_cross_year_gaps.py --input /PRIVATE/PATH/daily_system.csv --out outputs/sldc_cross_year_gap_qa.json\npytest -q tests/test_sldc_cross_year_gaps.py\n```\n\nThe method masks each target observation, uses other years' same Gregorian date divided by each analogue's nearby median, and multiplies the median factor by the target year's local median. It compares paired predictions against interpolation, reports yearwise diagnostics and skips dates with fewer than three other-year analogues. This is **single-date masking, not strict leave-one-year-out**; weekday, movable festivals, weather and growth are not fully controlled. Do not promote this estimator to the 11 real gaps until its private-data benchmark is executed and evaluated. Do not publish detailed private source rows. Likewise the three quarter-hour shapes are structural sensitivities, not probabilistic draws calibrated to observed Kerala ramps. The method named `flat` includes a tiny seeded illustrative perturbation; it is not literally constant. There is no ERA5 weather linkage, renewable coincidence, dispatch optimisation, hydro inflow or stochastic probability in this prototype.

**Release gate:** observed daily anchors and synthetic interval load must remain separate; no quarter-hour measured-load accuracy, historical peak, statewide storage MW, optimisation result or 2040 capacity claim is licensed by this generator.
