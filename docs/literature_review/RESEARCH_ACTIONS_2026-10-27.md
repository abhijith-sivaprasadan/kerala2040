# Research implementation gates from the 19-paper synthesis

**Status**: decisions proposed by literature synthesis, not completed implementation or a revised evidence-freeze decision.

| Priority | Action | Acceptance evidence | Why |
| --- | --- | --- | --- |
| P0 | Publish source-to-target measurement boundary and units manifest for annual/SLDC/Grid-India/CEA/CSTEP/WRI | Machine-readable manifest, scope checks, reconciled definition table | CEA, WRI, CSTEP, Harish, Hunt; prevents false forecast comparisons |
| P0 | Freeze exact 353-daily-target cohort and 11 missing SLDC days; QA weather join and IST day | Unmodified raw references, date-level ledger, checksum coverage and outlier decision log | Kerala public freeze; Hersbach; Hunt |
| P0 | Declare task A retrospective same-day explanatory; task B historical forecast-origin (conditional on genuinely available predictors); task C prospectively locked future period | Three distinct protocols with feature availability and no reused test dates | Sesay; Bergmeir; Cerqueira; Roberts |
| P0 | Add train-only detrending, outlier decisions, feature transforms and parameter tuning in each fold, with explicit leakage tests | Splits, fitted-transform histories, reproducible negative controls | Hunt Appendix B; Sesay; Roberts |
| P0 | Maintain published-result comparison table with boundary and validation-protocol labels | No mixed R²/MAPE or served/required energy comparators without harmonisation | Harish; Hunt; Babu; CEA; WRI |
| P1 | Implement naive, seasonal naive, linear/regularised, gradient boosting baselines in identical chronological windows | MAE, RMSE, MASE with train-only scale, paired errors and seasonal/peak slices | Hyndman; Kuster; Sesay |
| P1 | Perform blocked-bootstrap or dependence-aware error uncertainty checks | Explicit autocorrelation treatment, fold/nonindependence notes | Roberts; Cerqueira; Sesay |
| P1 | Test weather ablations and factor stability on locked periods; report SHAP only as attribution | Ablations with error delta and uncertainty; correlated-feature diagnostics | Hunt; Harish |
| P1 | Acquire and preserve multiple independent fiscal-year operational demand observations | Versioned official source with legal reuse, missingness and same measurement boundary | Needed for future-year claim |
| P1 | Compare ERA5/ERA5-Land provenance, rainfall/radiation clocks and local validation | Original downloaded variable and accumulation semantics, local comparison if available | Hersbach |
| P2 | Obtain actual historical hourly/15-min load before upgrading adequacy or load-shape evidence | Primary interval telemetry with source resolution, QA and rights | CSTEP, Babu, WRI, CEA; repo freeze |
| P2 | Resolve CSTEP storage-unit/accounting issue with original method/author | Unit-confirmation citation or full reproducible derivation | CSTEP |
| P2 | Introduce physically measured hydro inflows, constraints and balance checks before coupling | Mass/energy audits, historical dispatch matches and uncertainty scope | Vatanchi; Yue |
| P2 | Differentiate Kerala–rest-of-India import proxy from internal network model | Topology, PTDF/load flow/N-1 tests only when sourced | CEA |
| P2 | Publish a reproducibility archive of derived code and permissible data, not copyrighted third-party PDFs | Licence/right ledger, hashes, environment, tests, stable archival DOI | Pfenninger 2017/2018; DeCarolis |

## Suggested paper structure
1. Exact estimand and primary source lineage.
2. Source completeness, exclusions, source QA and fixed observational panel.
3. ERA5 covariate definitions, spatial and temporal alignment.
4. Protocol: in-domain random-split reference versus chronology-respecting rolling periods.
5. Information-availability matrix: same-day reanalysis, historical lag/covariate availability, weather forecast vintages.
6. Benchmarks and pre-registered metrics including peaks and seasonal slices.
7. Ablation and stability results with dependence-aware intervals.
8. Comparison with Harish (2020), Hunt & Bloomfield (2025), Babu (2026), not a false same-metric ranking.
9. Explicit results unsupported by current source coverage.
10. Open-science appendix and independent reproduction check.

**Release gate:** Until independent interannual source data and a validated forecast-origin feature archive exist, describe operational forecast findings and future-year generalisation as **not established**, regardless of CI passes or within-year retrospective skill.
