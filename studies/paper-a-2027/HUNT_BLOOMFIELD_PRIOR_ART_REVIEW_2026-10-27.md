# Critical prior-art assessment: Hunt & Bloomfield (2025) and Porwal et al. (2026)

**Date assessed:** 27 October 2026 · **Status:** literature/methods evidence, **not** a newly validated Kerala2040 energy-system result.
**Implication:** *Paper A's scientific contribution must be retested before further multiyear ERA5 acquisition and fitting*. This memo amends the assumptions of the draft [Paper A protocol](PROTOCOL_DRAFT_v0_1.md), but does not lock a new protocol, alter public research claims, or create a source-validated model.

## 1. The strongest prior art exists already — and includes Kerala

**Hunt, Kieran M. R. & Bloomfield, Hannah C. (2025)**. *Building and explaining data-driven energy demand models for Indian states*. **Environmental Research: Energy**, 2(2), 025003, published 9 April 2025. DOI: [10.1088/2753-3751/adc7bc](https://doi.org/10.1088/2753-3751/adc7bc).

**Evidentiary access and scope:** official [Newcastle University publisher bibliographic/abstract record](https://eprints.ncl.ac.uk/305255) plus accessible article full-text rendering at [ResearchGate](https://www.researchgate.net/publication/390401650_Building_and_explaining_data-driven_energy_demand_models_for_Indian_states), including Methods sections 2.1–2.4, results 3.1–3.2, appendix A and results table A1. The University of Reading PDF endpoint was protected against automated retrieval during this inspection; do not imply that a locally archived original PDF or original analysis data has been independently source-hash verified. **The scientific statements below come from article text, not Kerala2040 simulation.**

### Specific methods and findings directly relevant to Paper A

| Dimension | What the published 2025 article actually does | Kerala2040 implication |
|---|---|---|
| Study unit | Daily energy met / electricity supplied to **each Indian state**, from **Grid-India/POSOCO national PSP daily PDF reports** | *Not* necessarily the same field/definition as Kerala SLDC daily reported `consumption_qualified_mu`; original metadata required for a boundary match |
| Historical study data | Reports from **1 January 2013 to 28 April 2024** (paper appendix A); public linked dataset labelled **2014–2024** | Kerala2040 cannot claim first openly available Indian state-level multiyear observed-demand data |
| Weather | **ERA5** 2 m temperature and dew point, 10 m winds, solar radiation, clouds; thermal-stress **UTCI** | Using ERA5 is **not new**, and five fixed points cannot claim to be a better spatial representation without validation |
| Geography | Population-weighted state meteorology across 32 Indian states, **explicitly including Kerala** | Kerala-only geography is insufficient novelty |
| Timescale/features | Same-day weather plus 7 d/30 d means, extrema, calendar weekday/day-of-year, state and national holidays | Short/long climate-memory effects and holiday variables have already been considered |
| ML | XGBoost per state, Bayesian hyperparameter search, explained using **SHAP**; MLR and simple neural net comparison | Neither XGBoost nor SHAP nor a weather-versus-simple-linear contrast can establish originality |
| Train/test design | Reported **random 80/20 train/test split**, and internal five-fold CV for hyperparameter choices (paper Methods 2.2.3) | Our **strict chronological fiscal-year** assessment differs materially in target generalisation task; quantify consequences without alleging that published results are invalid |
| Kerala-specific outcome | Appendix D, Table A1: Kerala test **R²=0.835** full XGBoost, **0.724** reduced UTCI XGBoost, **0.751** full NN, **0.680** multivariate linear regression | Published Kerala-specific figures are **not** to be compared directly with our FY2024–25 RMSE; response scaling, target, period and split differ |
| Kerala-specific analysis | Figure 5 examines **three Kerala demand dates**, and figure 7 includes Kerala; strong role for **1 d and 7 d mean temperature**, weekday effects and monsoon transition | Cannot claim Kerala-specific weather–demand relationships were unexplored; even several localized interpretations are already published |
| Outputs | Original paper, public source code and open [Zenodo daily electricity/weather dataset](https://doi.org/10.5281/zenodo.14983362) | **A usable external benchmark** exists; first investigate source scope/actual values before paying/expending hours for custom acquisition |

**Context:** the paper's Kerala R² values are **their reported retrospective random-split test results**, not Kerala2040 results or prospective forecasting skill. They do not establish measured hourly demand, causal temperature elasticity, or proof of Kerala outages.

### Public benchmark dataset (not yet locally admitted)

[Hunt and Bloomfield, *Daily electricity demand data for Indian states (2014–2024)*, Zenodo version DOI **10.5281/zenodo.14983362**](https://zenodo.org/records/14983362), 6 March 2025, states file `Kerala.csv` with publisher-listed **MD5 `12ac3ecf4bdcc3dfe5bdc0ca2ce13d03`**; separate `corrected_daily_energy_met_MU.csv` **MD5 `172540c2c13282cc3dd4c9679b537aa0`**, and peak-met/peak-unmet tables. Dataset description says national-grid reports and meteorological variables are paired. The original `Kerala.csv` (~3.7 MB) and cross-state corrected CSV have **NOT been downloaded, parsed, or hash-authenticated in this study at this point**. A Zenodo listing and recorded MD5 are source metadata, not local verification; do not promote a cross-source numerical discrepancy or weather baseline until bytes are obtained.

Important: Some descriptions of the dataset and the paper describe a *2014–2024* dataset, while appendix A describes coverage beginning in **2013**. Verify exact row-date support from original Zenodo files; do not resolve by guessing. The quoted random-split R² cannot be equated with the proposed source-audited chronological skill.

## 2. Secondary competitor also overlaps

**Porwal et al. (2026), *Granular Analysis of Weather-Influenced Electricity Demand in Indian States***; IEEE IC3ECSBHI, pages 1091–1096, DOI [10.1109/IC3ECSBHI67834.2026.11468867](https://doi.org/10.1109/IC3ECSBHI67834.2026.11468867), indexed April 2026.

**Verified from publisher abstract, not full text:** Indian state daily demand April 2023–October 2025 from Grid-India PSP, paired with Open-Meteo historical weather and a composite temperature/humidity/rainfall weather indicator. Full model, Kerala-specific outputs and chronological splitting **not verified**. Do not claim their treatment of source revisions, missingness or cross-year validation until the full paper is obtained.

## 3. Consequences for Paper A publication novelty

**Rejected as novelty claims (already published):**
1. First Indian-state or Kerala daily demand/weather ML experiment.
2. First use of ERA5 / XGBoost / SHAP for Kerala demand.
3. First discussion of Kerala daily temperature/weekday/monsoon effects.
4. First public Indian-state daily electricity and weather dataset.
5. A claim that stronger FY2024–25 retrospective single-year RMSE on a different target/split proves superiority to Hunt and Bloomfield's published Kerala R².

**Candidate novel questions, conditional on real observations (not pre-asserted contributions):**

**N1 — Source-boundary reproducibility and measurement sensitivity (high priority).**
- Are Grid-India `daily_energy_met_MU` and Kerala SLDC `consumption_qualified_mu` identical constructs, or do their official measurement boundaries materially differ?
- Can each series be joined on IST date **without filling missing days**, and what are the timing/definition/revision limitations?
- If a difference exists, characterize it only after matching publisher units, period and physical scope. *A difference is not by itself an error or evidence of imports/shortage.*

**N2 — Genuine year-forward transfer of weather-added skill (high priority).**
- Preselect a fixed Ridge calendar-only vs calendar+weather test across actual FY later-year chronology, with audit of researcher exposure. This differs from a randomized retrospective split, but comparison requires running an appropriately *comparable* benchmark under matched target, feature and exact test-date conditions.
- Test whether weather-related incremental skill is stable across monsoon and later years or a single-year development artefact.
- Pre-register **training and period shifts**, with no claims of independent blind inference on already exposed fiscal years.

**N3 — Independent data and spatial representation sensitivity (secondary).**
- Compare five-point equal-weighted ERA5 versus **published population-weighted ERA5** and/or a single simple regional point if original data and rights permit. Never claim the five-point average is more representative without evidence.
- Use the Hunt/Bloomfield dataset as an external comparator or a transparent publicly accessible benchmark **without relabelling their Grid-India target as SLDC observed demand**.

**N4 — Methodological source-QA framework (fallback A0).**
- Provenance + version changes + missed dates + physical accounting boundary crosswalk, plus independent extraction/reconciliation checks, are feasible research contributions **only if** the resulting method/outcome exceeds a descriptive inventory and can be validated on original records.

### Early decision to prevent low-return data work

**By 30 November 2026**, before significant new Copernicus ERA5 download volume:
- Retrieve original published `Kerala.csv` and `corrected_daily_energy_met_MU.csv` bytes from Zenodo, confirm MD5 and appropriate licence, inspect actual coverage and provider metadata; keep derived comparisons separately source-labeled.
- Compare actual fiscal-year/date overlap **only** against an equivalent documented SLDC field, preserving both target columns, missing dates, differing definitions, and non-comparable classifications.
- Review published feature sets, split and reproducibility code; write one **falsifiable novelty statement** stronger than 'ERA5 improves XGBoost over calendar'.
- If no independent novelty remains after the comparator, **pivot the protected publication** toward source-accounting methodology A0 or the hydro/import physical problem *subject to its data gate*. Don't continue a year-long ML paper on the basis of aesthetics or one-year accuracy gains.

## 4. New minimal comparison table to fill after original files become available

| Question | Hunt/Bloomfield Grid-India series | Kerala2040 SLDC series | Gate |
|---|---|---|---|
| Original publisher/field | POSOCO/NLDC daily `energy met` (exact source record/vintage to verify) | Kerala SLDC original statement `consumption` (exact record/version to verify) | Both source dictionaries |
| Units | Daily MU | Daily MU | Same unit, **not automatically same physical boundary** |
| Calendar | Source report date (confirm IST/noon/period coverage) | SLDC source-dated IST days | Confirm identical 24 h or reporting period |
| Missingness | Original/corrected values (verify correction logic) | Qualified original source dates and gaps | No zero/synthetic joins |
| Revision policy | Dataset corrected values and original national sources | Private original + revision/hash manifest | Versions disclosed |
| Comparable estimand | **Not yet established** | **Not yet established** | No numeric difference inference until verified |
| Exact overlap | To be computed from bytes | To be computed from original hash-verified dates | No invented counts |

## 5. Read and reproducibility status

| Task | State |
|---|---|
| Official published paper metadata, abstract and DOI verified | **DONE** |
| Accessible full-text methods/results sections and Kerala-specific appendix table read | **DONE** (article HTML rendering; original paper PDF not locally retained) |
| Public Zenodo dataset and checksums inventoried | **DONE** (publisher listing only) |
| Prior 2026 IEEE abstract and DOI screened | **DONE** |
| Hunt/Bloomfield GitHub code independently rerun | **NOT DONE** |
| Original Zenodo Kerala CSV downloaded & MD5 confirmed | **NOT DONE** (download attempts failed) |
| Independently authenticated private Kerala SLDC multi-FY rows | **NOT DONE** |
| Cross-source paired value comparison and missingness figure | **NOT DONE** |
| New multiyear weather/ML run | **NOT DONE; blocked by source gate** |

**Scientific practice:** conclusions about existing published research are separate from new local observations. This memo is a literature review and revised experiment design; it is **not a new energy-system finding or a release of restricted data**.
