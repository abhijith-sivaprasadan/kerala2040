# Paper A — retrospective registered-analysis protocol v0.1 (DRAFT)

**Created:** 26 October 2026. **Owner:** independent Kerala2040 research project.
**State:** `DRAFT_UNLOCKED`, **not** preregistered, accepted, executed or a new scientific finding.
**Planning authority:** draft [2026–27 research charter PR #135](https://github.com/abhijith-sivaprasadan/kerala2040/pull/135); the public [23 October 2026 evidence freeze](../../docs/RESEARCH_FREEZE_2026-10-23.md) remains in force.
**Change rule:** A reviewer must approve and timestamp v1.0 *before the next full multiyear results inspection*. Preserve this draft, all amendments and analysis decisions. A locked protocol today cannot retroactively make earlier exposure prospective.

## Scientific question and estimand

> For *qualified, source-recorded* Kerala SLDC **daily operational electricity consumption (MU/day)**, does five-point same-day ERA5 weather reduce retrospective prediction error compared with the identical fixed calendar-only regression learner, on later fiscal-year periods trained only on prior days?

This is an **observational retrospective association**, not day-ahead forecast skill, observed hourly load prediction, a causal temperature elasticity or a load-shedding mechanism.

- **Target:** original-source qualified `consumption_qualified_mu` for each IST calendar date from the private SLDC manifest; do not substitute public annual consumer-side sales or the reconstructed hourly proxy.
- **Domain:** statewide SLDC reporting boundary, **daily MU**. Financial year is 1 April–31 March.
- **Weather:** ERA5 *reanalysis* at five already-declared representative point boxes (Thiruvananthapuram, Kochi, Palakkad, Kozhikode, Kannur); equal weighting is a **declared modelling assumption**, not Kerala area/load weighting.
- **Comparison:** paired calendar Ridge vs calendar+same-day-weather Ridge on *identical eligible observed dates*. No post-hoc switching to the best boosted model after inspecting held-out results.
- **Inference label:** `retrospective_chronological_backtest`; even a chronologically later fold is **not automatically researcher-unexposed**.

## Proposed outcome definitions (lock before new evaluation)

| Status | Parameter | Proposed decision |
|---|---|---|
| PRIMARY | Held-out RMSE in MU/day | Per-FY `sqrt(mean((y - yhat)^2))` for the same eligible test dates in both model arms |
| PRIMARY | Signed weather-added RMSE skill | Per-FY `100 × (RMSE_calendar - RMSE_calendar+weather) / RMSE_calendar`; report every positive **and negative** value |
| SECONDARY | MAE in MU/day | Per-FY, both arms; pooled after per-year table, never instead of per-year outcomes |
| SECONDARY | Seasonal/lag-naive comparison | Must compute historical lag/seasonal reference **from qualified earlier observed dates** only; do not fill missing source days |
| SECONDARY | MASE | Scale denominator defined solely on each training fold, with undefined denominators reported unavailable |
| EXPLORATORY | Monsoon/season and high-demand errors, weather-family ablations | Report with multiplicity/exploratory warning; never select favourable months as independent confirmation |
| EXPLORATORY | LightGBM, XGBoost, SHAP | After the *fixed* Ridge analysis, with training-only tuning and separate retrospective labels; SHAP non-causal |

**Statistical uncertainty:** show all three separate FY outcomes and heterogeneity; inspect residual autocorrelation and the effect of missing source days. A confidence interval treating individual daily rows as independent would be misleading. No arbitrary positive gain is required: null/worse weather contribution is a legitimate result. Significance testing and block-bootstrap choices require prior design review; do not retrofit them to results.

## Proposed data and split eligibility

- The private SLDC archive is reported in `docs/MULTIYEAR_DAILY_RESEARCH_GATE.md` as **2,606 original source-dated rows**, not 2,606 qualified targets. Verify both the original compressed and decompressed SHA-256 values against its actual private manifest, and check `energy_balance_qualified=True`.
- Existing fixed expanding-origin target folds in `src/kerala2040/multiyear_daily_study.py`:
  - **F1:** train eligible 2020-04-01..2022-03-31; test FY2022–23.
  - **F2:** train eligible 2020-04-01..2023-03-31; test FY2023–24.
  - **F3:** train eligible 2020-04-01..2024-03-31; test FY2024–25.
- Do not guess exact qualified target counts for each fold from the count of *source reports*. They must be recomputed after source verification.
- FY2024–25 was repeatedly used in the earlier v0.1/v0.2 experiment and is **researcher-exposed**. F1 and F2 are *not certified pristine* either: future outcomes may already have influenced choices. The mandatory [exposure register](EXPOSURE_AND_SOURCE_REGISTER.md) explicitly records what is verified and unknown. Chronological split protects the fitter from future target rows but cannot undo human/research-design leakage.
- All trained models: `StandardScaler() + Ridge(alpha=1.0)`; calendar feature set and weather feature set currently defined in `src/kerala2040/daily_demand_ml.py`. Training-only standardization in pipeline, exact same date join for each comparison, no missing target imputation or filling missing meteorology.
- Five-point weather original-source integrity: exact original Copernicus files, provider date/grid identity, SHA-256, variable units, release/accumulated flux temporal semantics, UTC-to-IST alignment and 24 unique whole-UTC-hours per location per observed IST day. At the IST 00:30/23:30 boundaries, verify that temperature and *interval accumulated* radiation/precipitation use correctly supported time intervals; a mere timezone timestamp relabel is not physical integration proof.
- **Current admission blocker:** no independently source-hash-verified complete multiyear ERA5 chain for training plus registered tests. Existing normalized five-point QA is not original source authentication. Never fake missing weather or operational load.
- **Proposed cutoff:** verify admitted multiyear source coverage **by 31 March 2027**; if unavailable, formally switch the one protected manuscript to Paper A0; archive runnable Paper A protocol without claims of completed multiyear validation.

## Prior analysis exposure and alternative

Historical FY2024–25 has already been tested against several ML model families, including tuned and weather-ablation variants; see `docs/DAILY_DEMAND_ML_V0_1.md` and `docs/DAILY_DEMAND_ML_ROBUSTNESS_V0_2.md`. Prior published results must be described in the final manuscript, **not** passed off as newly independent evidence. A genuinely prospective later period may be added only if data/admission rights and protocol-lock timing permit, and must be labelled separately; no such future test is currently secured.

Paper A0's **different** question and novelty criteria appear in [the fallback prospectus](PAPER_A0_PROSPECTUS_DRAFT.md). The original 23 October 2026 research freeze is not overwritten merely by editing these methodological plans.

## Decisions needed before lock v1.0

1. Confirm fixed primary weather contrast and RMSE + signed skill endpoints (the fixed Ridge learner, not boosting, is the confirmatory default).
2. Decide whether same-day weather is **strictly explanatory** in title/abstract; recommended yes. Do not promise day-ahead skill.
3. Audit F1/F2 researcher exposures and date-level SLDC qualification.
4. Decide how to handle exact UTC-boundary hours for daily precipitation/radiation; verify provider units and integration empirically before selecting aggregation.
5. Approve missing-day/partial-weather eligibility and predeclared naive baseline lag.
6. Set a source-hash-verified completeness criterion for **all registered folds**, or transparently downgrade to a smaller explicitly exploratory analysis.

**This v0.1 is a proposal to discuss, not a completed analysis registration.**
