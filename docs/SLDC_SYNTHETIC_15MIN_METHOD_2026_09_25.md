# FY2024–25 daily-anchored synthetic quarter-hour demand — research prototype

**Classification:** `SYNTHETIC_15MIN_DAILY_SLDC_ANCHORED_NOT_OBSERVED_INTERVAL_LOAD`.

Run from repository root:

```bash
python scripts/build_sldc_synthetic_15min.py --out-dir outputs/sldc_synthetic_15min
pytest -q tests/test_sldc_synthetic_15min.py
```

Exports: `daily_anchors.csv` (365 rows, observation status and source hash), `synthetic_15min.csv` (96 quarter-hours × available days × 3 explicitly assumed shapes), and `qa.json` (observed and estimated contributions, leave-one-observed-day-out benchmark and limitations). IST and UTC interval-start timestamps are included. Each modelled daily shape is exactly reconciled to its own SLDC daily MU: sum of interval-average MW × 0.25 hours = daily MU × 1000 MWh. Hourly average MW = mean of four consecutive quarter-hour MW.

The official FY2024–25 daily archive reports 354 observed days and 11 missing. By default the missing dates are filled with **labelled candidate local linear interpolation**, only where observed bracketing dates are within seven days; `--no-estimate-missing` leaves them unavailable. This does not reconstruct measured data. The blind benchmark compares interpolation against a local median on held-out *observed* days; neither benchmark nor its errors validates the quarter-hour shape or calibrates a confidence interval. Do not describe estimated-day totals as official annual consumption.

The user's proposed normalized same-calendar-date cross-year method is **not implemented** because the present admitted package is only FY2024–25. It must first have cross-year source QA, leave-one-year-out benchmarking, weekday/festival and secular-growth controls; then compare it on identical masked days before using it to estimate actual gaps. Likewise the three quarter-hour shapes are structural sensitivities, not probabilistic draws calibrated to observed Kerala ramps. The method named `flat` includes a tiny seeded illustrative perturbation; it is not literally constant. There is no ERA5 weather linkage, renewable coincidence, dispatch optimisation, hydro inflow or stochastic probability in this prototype.

**Release gate:** observed daily anchors and synthetic interval load must remain separate; no quarter-hour measured-load accuracy, historical peak, statewide storage MW, optimisation result or 2040 capacity claim is licensed by this generator.
