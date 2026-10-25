# Frozen daily demand ML study: source-to-claim reconciliation

This script reconciles the seven published September 2024–March 2025
chronological holdouts from the **frozen observed-SLDC daily target** evidence.
It checks that every stored win count, median, mean, range, and reported
XGBoost weather-group ablation reduction agrees arithmetically with the
month-level observations already recorded.

```bash
python scripts/audit_frozen_daily_ml.py
pytest -q tests/test_frozen_daily_ml_evidence.py
```

This is a *new independent tabulation check*, not an independent training rerun
and not additional original meteorological or energy data. No new outcomes are
invented. The reported pooled RMSE reductions are recomputed from stored pooled
RMSE values, **not** by averaging fold percentage reductions. Seven consecutive
monthly evaluations under expanding training windows are correlated; their
win counts are descriptive, not seven IID hypothesis-test replications.
The leave-one-fold-out positive-count range describes the stability of the
reported sign under omission of one month, not a confidence interval.

The research freeze remains unchanged. Same-day **realised ERA5** features make
the study retrospective rather than operational day-ahead forecasting. The
target is **observed daily** Kerala SLDC demand; no reconstructed hourly peak,
operational load-shedding cause, causal weather elasticity or multiyear
generalisation is inferred. Independent second-year observations and locked
time-order evaluation are required to upgrade the evidence.
