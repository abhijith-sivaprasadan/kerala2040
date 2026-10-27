# Cross-paper synthesis: Kerala2040 research boundaries and publication direction

**Date:** 27 October 2026 · **Corpus:** 19 reviewed documents / 520 uploaded PDF page positions  
**Status:** source-grounded literature synthesis; no independent rerun of third-party original numerical models. The project's public evidence freeze remains in force.

## Executive conclusion

These papers **do not support claiming novelty simply for using ERA5, XGBoost, SHAP, state-wise energy-demand models, or scenarios to 2040**. Harish et al. (2020) published Kerala-specific temperature-load associations; Hunt and Bloomfield (2025) already applied ERA5-like population-weighted meteorology, XGBoost and SHAP to Indian states, reporting Kerala R² = 0.835 in a random held-out sample; Babu et al. (2026) investigates EV/cooling influences and long-run demand. A defensible Kerala2040 contribution is instead a **reproducible, measurement-boundary-aware, leakage-audited and chronologically evaluated assessment of weather-associated daily electricity demand**, demonstrating what changes under deployment-realistic validation and explicit data provenance. This is a research hypothesis to test, not a novelty result already established.

## 1. Demand is not one interchangeable quantity

CEA, WRI and CSTEP project different quantities, with different accounting scopes. WRI reports **46,642 MU** for FY2035–36 in its demand pathway whereas CEA reports **55,996 MU** for projected energy requirements. The arithmetic difference is 9,354 MU (16.7% of the CEA figure); it **cannot** yet be called a forecast error because electricity sales, gross energy required, losses and captive/open-access treatments are not reconciled. CSTEP's FY2040 **45,519 MU** includes specified additions and T&D losses, whereas its **40,446 MU** is a more restricted baseline sales projection; do not interchange them. CEA's **13,868 MU** possible FY2035–36 shortage refers to the case with existing and planned contractual resources, not the recommended expanded resource portfolio.

The project's own State Planning Board annual **29,311.76 MU** FY2024–25 consumer-side series and SLDC **30,666.2569 MU** summed daily operating-boundary consumption across 354 observed days are not rival estimates of the same metric. Eleven SLDC daily source reports are absent. Harish et al. analyse restricted load actually served, with monthly deficit controls; Hunt and Bloomfield extract daily energy **supplied**. A valid forecast cannot remove this measurement distinction by calling every label 'demand'.

**Resolution:** maintain an estimand/source-boundary table: institution, field, units, geographical coverage, time interval, loss boundary, supplied versus unrestricted, missingness, and legitimate joins. Explicitly label latent unmet demand as not identified by observed consumption alone.

## 2. Historical association is not future-date prediction

Hunt and Bloomfield use random 80/20 splitting and five-fold cross-validation; 2023-normalised targets undergo LOESS detrending and variance adjustment, apparently computed over a full series. The appendix does not establish train-only transformations for each forecast origin. These methods are meaningful for a weather-conditioned retrospective reconstruction, but do **not** establish future-year predictive independence. Kerala's published test R² values (Appendix Table A1) are XGBoost **0.835**, UTCI-only **0.724**, neural network **0.751**, and linear regression **0.680** under their procedure; these are not legitimate pass/fail thresholds for a different time holdout, target and preprocessing pipeline.

Babu et al. distinguish an evaluation period represented within training (regional MAPE approximately **0.6–1.9%**) from held-out-period comparisons (approximately **4.9–6.7%** for the five reported regions). Bergmeir et al. allow shuffled CV only under restrictive autoregressive assumptions; Cerqueira et al. show ranking changes with stationarity and algorithm; Roberts et al. warn that dependency in covariates and inputs invalidates simplistic independence checks; Sesay shows how preprocessing and future-looking features change apparent skill. None of these papers says that 'chronological' automatically means unbiased: rolling tests can overlap, transforms can leak, and model-selection exposure must be documented.

**Resolution:** distinguish (A) same-day explanatory reconstruction using observed ERA5, (B) retrospective rolling-origin or subsequent fiscal-year prediction using ONLY information available at origin, and (C) genuinely prospective locked forecasts. Evaluate baselines, tree ensembles, uncertainty and error metrics on identical periods. Freeze hyperparameters and preprocessing before the last confirmation block.

## 3. Weather data need a precise time/measurement boundary

Hersbach et al. establish that ERA5 is an **assimilated reanalysis**, not a direct hourly station observation and not a weather forecast known on the day being forecast. ERA5-Land has different grid resolution and conventions for some accumulated variables. Kerala's monsoon rainfall, orographic contrasts, solar irradiance and local humidity require external consistency checks; global ERA5 validation does not prove local Kerala performance. UTCI's relationship with heat stress is useful but the reduced Hunt–Bloomfield UTCI-only model loses Kerala fit. Harish et al. find Kerala coefficients **0.0211** for 24–27 °C and **0.0694** for 27–30 °C compared with 21–24 °C; the exact transformations are **2.13%** and **7.19%**, within their 2009–2013 served-load panel. No Kerala coefficient at 30–33 °C is reported; do not extrapolate an estimated extreme-heat response.

For predictive tasks, separately maintain contemporaneous weather reconstructions and weather **forecast vintages**. If vintage forecasts are unavailable, describe the model as a retrospective weather-conditioned analysis, not an operational ahead-of-time forecast. Validate IST UTC/local-day construction, accumulated radiation/rainfall conventions, lag windows, missing observations and population-weighted spatial aggregation.

## 4. SHAP is explanation of fitted-model behaviour, not proof of cause

Hunt and Bloomfield's Kerala Figures 5 and 7 identify daily and seven-day temperature as influential, and their Figure 3 shows a marked Sunday signature. Harish et al.'s econometric fixed-effects results independently suggest a nonlinear temperature relationship, but estimate served-load associations over an earlier period. The methods, populations and estimands differ. Strongly correlated temperature, dewpoint, seasonal and calendar variables can redistribute SHAP allocations; retraining with UTCI changes both feature construction and model skill. A higher SHAP value is **not** a controlled causal effect of heat, air-conditioner ownership or holiday policy.

**Resolution:** separate predictive contribution (out-of-time ablation), conditional association (regression with controls), and causal effect (requires a separate identification strategy). Add blocked bootstrap intervals and stability plots by season/year; check extreme observations and flagged zero values against original reports before replacing them.

## 5. Annual scenario plausibility is not hourly power-system adequacy

WRI explicitly excludes hourly dispatch, detailed storage and grid flow. CSTEP's future hourly demand relies on extrapolating a FY2016 15-minute profile; Babu et al. use a normalised **2023 hourly shape** for future profiles. CEA's ORDENA adequacy analysis is materially more operational, but the annex models **Kerala and rest of India as two nodes**, not the internal Kerala transmission network. Hence these publications do not independently prove network congestion, N−1 reliability, feasible import flexibility, storage deliverability or actual unserved energy at a substation.

CSTEP reports storage pairs such as **3.8 GW / 7,163 GWh** and **4.1 GW / 8,108 GWh** for FY2040; taken literally these imply roughly 1,885 and 1,978 hours duration. The numbers/units are repeated in the source but their physical interpretation is unresolved. Preserve the printed labels and classify energy-capacity input as **not admissible** until author/method clarification.

Pfenninger et al. (2014) and DeCarolis et al. (2017) both support explicitly selecting temporal, technical and geographical model resolution by the actual decision problem. Passing a solver or matching annual totals does not validate hourly adequacy.

## 6. Hydro models and uncertainty require explicit coupling depth

Vatanchi et al. classify 106 hydropower scheduling studies as 76 uncoupled, 24 sequential, three iterative and three fully coupled. This does not establish that the most coupled category is always suitable, nor that Kerala2040 already achieves it. A reservoir inflow time series used as an input to a power model is an **exogenous coupling**, not proof of a simultaneous water–power optimisation with head variation, spillage, ecological release and multi-reservoir constraints.

Yue et al. distinguish Monte Carlo sensitivity, stochastic recourse, robust optimisation and modelling to generate alternatives. Their approaches answer different questions. For current Kerala2040, the minimum credible path is source-characterised hydro state and inflow, historical checks, physically feasible stress tests and uncertainty bands. Multi-stage stochastic operation is later work contingent on measured and credible water-system data.

## 7. Openness, QA and citations are independent dimensions

Pfenninger et al. (2017, 2018) and DeCarolis et al. (2017) converge on open methodology and independently checkable data processing, model specification, tests, versioning and authorship/licensing boundaries. A GitHub repository or a Zenodo DOI confers neither scientific validation nor the right to redistribute third-party source PDFs. The 19 visual audits identify several published-document problems (CSTEP appendix totals/formula sign; CEA small category sums; WRI chart labelling; review study counts; figure/reference mistakes). Such problems warrant a **source qualification**, not blanket rejection of a work or a fabricated corrected value.

For the audit series itself, preserve original document hashes, exact versions, page-level observation method, numerical check scripts, source of each claim and explicit 'not reproduced' labels. Rendering a page or assigning 'inspected=yes' automatically cannot certify individual reading.

## Reconciled comparison table

| Published result or claim | Proper use in Kerala2040 | Not justified |
| --- | --- | --- |
| Harish Kerala weather-response coefficients, 2009–2013 | Historical served-load association comparator | Kerala unrestricted demand or response beyond observed bins |
| Hunt–Bloomfield Kerala R² 0.835 (random split) | In-domain random-split benchmark and reproducible-method challenge | Future-year predictive skill or causal temperature effects |
| Babu national/region scenarios and forecast validation | Cooling/EV pathway sensitivities, evaluation-design caution | Dynamically predicted future hourly shapes from 2023 normalisation |
| CSTEP FY2040 45,519 MU, load shapes and storage | Labelled scenario comparison requiring boundary reconciliation | Validated storage sizing or actual future adequacy |
| WRI FY2035–36 46,642 MU | Scenario-specific sales/demand path | Direct apples-to-apples error against CEA requirements |
| CEA FY2035–36 55,996 MU requirements / 13,868 MU baseline shortage | Official scenario comparator and reliability-method example | Same shortage under recommended build-out; full internal network validation |
| ERA5 historical hourly meteorology | Documented reconstructed historical covariates | Observed local station truth or contemporaneously available weather forecasts |
| Kerala2040 FY2024–25 353 matched daily observations | Retrospective same-day explanatory analysis only | Multi-year independent or operational forecast claim |

## Recommended publication position

**Working research question:** *How do measurement boundary, causal preprocessing and chronological evaluation affect apparent weather–electricity-demand relationships in Kerala?*

**Potential contribution (conditional):** an original source-audited daily Kerala dataset and pipeline; tested influence of splitting/preprocessing choices; interpretable, season-specific meteorological associations; honest quantification of data/missingness/forecast-availability limits. Results must show a measurable effect or important null result to establish novelty. Until at least one independent future-period dataset is admitted, claims must remain within retrospective same-day/within-year evidence.

**Do not headline yet:** hourly/15-min load reconstruction as measured telemetry; physical grid adequacy; state-wide heat causal effects; 2040 installed-capacity prescriptions; storage requirements derived from unverified units; numerical drought/blackout risks based on standardised z-score supply–demand differences.

See [actions and acceptance gates](RESEARCH_ACTIONS_2026-10-27.md) and the existing [public evidence freeze](../RESEARCH_FREEZE_2026-10-23.md).
