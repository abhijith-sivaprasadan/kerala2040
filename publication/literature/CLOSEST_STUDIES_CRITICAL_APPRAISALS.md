# Closest studies — structured critical appraisal and applicability crosswalk

**Status 27 October 2026:** Twenty targeted evidence entries in publication-impact order. **Access levels are part of the result.** These are not twenty verified full-text reviews; some assessments rely on publisher abstracts, section snippets or the author's released code. No study's statistically reported number is transferred directly into Kerala2040.

**Legend:** **FULL/SECTIONS** = accessible full text or substantive body/method/figure sections checked. **ABSTRACT** = publisher abstract, highlights, snippets, indexing only (insufficient to adjudicate full method). **CODE** = source-available program inspected, not rerun. **OFFICIAL** = government/provider/institutional source; not peer-reviewed article. **OLDER MATRIX** = bibliographic review only. **Action** identifies a reproducible check needed before publication.

## Tier 1 — direct competing studies (highest novelty impact)

### 1. Hunt & Bloomfield (2025) — Indian states data-driven electricity-demand models [D01]

- **Citation:** [Environmental Research: Energy, DOI 10.1088/2753-3751/adc7bc](https://doi.org/10.1088/2753-3751/adc7bc).
- **Access:** FULL/SECTIONS (publisher article HTML/research accessible body including methods and Table A1), CODE (public code inspected); no independent scientific reproduction and Zenodo data hashes not downloaded.
- **Data unit/scope:** national Grid-India reported state-specific daily energy met, with Kerala; data history reported from 2013 in article appendix, public labelled release '2014–2024' requires row verification.
- **Weather/method:** population-weighted ERA5 and thermally relevant variables, varied temporal lags; XGBoost/SHAP; holidays/calendar; detrended/variance-scaled training target.
- **Validation:** published generic code's random partition; authors' own result **Kerala R²=0.835** full XGBoost. Their scale and partitions differ from our original MU/chronological FY tests.
- **Valid claim:** existing Kerala-specific ERA5/XGBoost/SHAP original scholarly precedent **eliminates** algorithm/geography novelty.
- **Unresolved:** precise original-target mapping versus SLDC operating field; original national data hashes/rights, how preprocessing and split procedure affect FY-forward performance. Full model rerun not performed.
- **Design response:** first source-field equivalence and chronological out-of-year test under identical accepted daily dates; treat source compare and validation as the contribution, not an ML superiority claim.

### 2. Harish, Singh & Tongia (2020) — India/Delhi temperature response [D02]

- **Citation:** [Energy Policy, DOI 10.1016/j.enpol.2020.111445](https://doi.org/10.1016/j.enpol.2020.111445).
- **Access:** FULL/SECTIONS on ScienceDirect official paper body, abstract and methods/data section excerpts.
- **Data unit/scope:** Delhi household billing, **160,841 consumers** over nearly 4 years; distinct national **2009–13 state 5-minute-load-derived daily mean load**. Load is load **met** under curtailment, not unrestrained demand.
- **Method:** semiparametric nonlinear temperature response with observed socioeconomic heterogeneity.
- **Finding:** states vary materially; demand response is not a single portable heat-load coefficient.
- **Unresolved:** household covariates do not exist in current Kerala SLDC daily record; no Kerala-specific causal identification from same-day ML.
- **Response:** restrict Paper A to aggregate association and measurement boundary; cite as the earliest important state-scale antecedent and add temperature confounding caveat.

### 3. Porwal et al. (2026) — state-level daily weather correlation [D03]

- **Citation:** [IEEE IC3ECSBHI, DOI 10.1109/IC3ECSBHI67834.2026.11468867](https://doi.org/10.1109/IC3ECSBHI67834.2026.11468867).
- **Access:** **ABSTRACT only**, six-page paper not retrieved.
- **Data:** Grid-India Power Supply Position daily Indian states Apr 2023–Oct 2025 and Open-Meteo.
- **Methods/finding allowed:** weather-dependent heterogeneity across states; composite temperature/humidity/rainfall described in public metadata.
- **Unknown:** exact Kerala output, temporal evaluation, source revisions, statistical controls, processing.
- **Response:** do not allege missing controls or superiority without full text. Attempt lawful author/library full text before final novelty section.

### 4. Babu, Ramadesigan & Banerjee (2026) — India's EV/cooling demand growth [D04]

- **Citation:** [Applied Energy, DOI 10.1016/j.apenergy.2026.128069](https://doi.org/10.1016/j.apenergy.2026.128069).
- **Access:** **ABSTRACT / publisher highlights**, not complete paid article.
- **Focus:** medium/long-term electricity demand planning, EV growth, space cooling and changing peak hour; does not establish actual Kerala daily operational SLDC weather-Ridge contrast.
- **Response:** acknowledge India planning forecasting precedent; don't transfer national 2070 cooling effects to observed Kerala days or claim a first long-run electricity plan.

### 5. Indian dwelling air-conditioning patterns (2022) [D05]

- **Citation:** [Energy Informatics, DOI 10.1186/s42162-022-00228-1](https://doi.org/10.1186/s42162-022-00228-1).
- **Access:** **ABSTRACT**, authors/check specific site before citing final manuscript.
- **Focus:** monitored Indian dwellings and cooling-related electricity-use timing at household scale. This is not statewide day-level operational load.
- **Response:** explain why an aggregate correlation does not identify AC operation, income, night-demand or specific customer technology.

### 6. Variation in electricity use in Indian dwellings (2024) [D06]

- **Citation:** [DOI 10.1080/13467581.2024.2314492](https://doi.org/10.1080/13467581.2024.2314492).
- **Access:** **ABSTRACT**, author names pending exact source verification.
- **Focus:** between-household variance with and without air-conditioning, a different unit than SLDC.
- **Response:** use as context on ecological aggregation and avoid importing household demand/causal elasticity coefficients into Kerala grid data.

## Tier 2 — forecasting/reproducibility methods

### 7. Cerqueira, Torgo & Mozetič (2020) — time-series performance estimation [V02]

- **Citation:** [Machine Learning, DOI 10.1007/s10994-020-05910-7](https://doi.org/10.1007/s10994-020-05910-7); [public 32-page PDF](https://kt.ijs.si/igor_mozetic/papers/CerTorMoz-TimeSer-MACH-20.pdf).
- **Access:** **FULL/SECTIONS** paper text verified, beginning abstract, definitions and design; no reproduction of its 174-real-series experiment.
- **Experiment:** compares cross-validation, prequential and several future holdouts on stationary and nonstationary time series.
- **Finding:** in their nonstationary real-series setting, repeated out-of-sample test periods better approximate later error; blocked CV can be useful for stationary series.
- **Response:** justify year-forward FY tests based on **later-year transfer objective**, not dogmatic assertion random CV is always wrong. Register folds, source qualification and exposure.

### 8. Roberts et al. (2017) — spatial and temporal cross-validation [V01]

- **Citation:** [Ecography, DOI 10.1111/ecog.02881](https://doi.org/10.1111/ecog.02881).
- **Access:** **full-text rendering cited in matrix**, line-level study-method checks not completed in this update.
- **Concept:** dependent data can invalidate naive independence assumptions; spatial/temporal blocking must be chosen for the intended prediction/generalization setting.
- **Response:** day autocorrelation, year holdouts and fixed five-point/weather choices; cannot use a 24-hour spatial panel as 120 independent statewide meteorological observations.

### 9. Bergmeir, Hyndman & Koo (2018) — when cross-validation can be valid [V03]

- **Citation:** [Computational Statistics & Data Analysis, DOI 10.1016/j.csda.2017.11.003](https://doi.org/10.1016/j.csda.2017.11.003).
- **Access:** **OLDER MATRIX / bibliographic**.
- **Key nuance:** standard CV is not categorically forbidden for pure autoregressive setups meeting appropriate assumptions.
- **Response:** keep comparator criticism precise, distinguishing Hunt's historical-association aim from our year-forward validation aim; don't claim publication invalid solely because random partition was used.

### 10. Hyndman & Koehler (2006) — accuracy measures [V04]

- **Citation:** [International Journal of Forecasting, DOI 10.1016/j.ijforecast.2006.03.001](https://doi.org/10.1016/j.ijforecast.2006.03.001).
- **Access:** **OLDER MATRIX / bibliographic abstract**.
- **Focus:** scaled forecast errors and known weaknesses of MAPE across series.
- **Response:** choose RMSE, MAE and train-only MASE where defined. Do not define a scaled denominator over the entire measured/evaluation period.

### 11. Leakage-aware benchmarking of temporal data preparation (2026) [F05]

- **Citation:** [Energy Conversion and Management: X, DOI 10.1016/j.ecmx.2026.101791](https://doi.org/10.1016/j.ecmx.2026.101791).
- **Access:** **FULL/SECTIONS**, publisher openly displays source, methods, results and limitations.
- **Study:** two non-Kerala **hourly** datasets and horizons 1,6,24 hours, fixed TinyGRU with matched rolling origins, test preprocessing and anomaly treatment.
- **Findings/limits:** data preparation can change score enough to matter; effect size and direction differ across datasets, and their short second dataset has weak statistical power.
- **Response:** avoid interpreting differences in Hunt's transformed target versus our source MU as a benchmark; keep preprocessing explicit and train-only. No direct effect size transfer.

### 12. Kuster, Rezgui & Mourshed (2017) — electrical load forecasting review [F01]

- **Citation:** [Sustainable Cities and Society, DOI 10.1016/j.scs.2017.08.009](https://doi.org/10.1016/j.scs.2017.08.009).
- **Access:** **ABSTRACT and selected publisher sections** (matrix), not full 113-application extraction independently replicated.
- **Finding:** heterogeneous targets, scales and horizons make cross-study accuracy ranking misleading.
- **Response:** a source-aligned same-dates comparability table is more meaningful than a leaderboard of published R² and Kerala2040 RMSE.

### 13. Hong & Fan (2016) — probabilistic load forecasting [F02]

- **Citation:** [International Journal of Forecasting, DOI 10.1016/j.ijforecast.2015.11.011](https://doi.org/10.1016/j.ijforecast.2015.11.011).
- **Access:** **publisher full-text rendering** cited in matrix, not formally rechecked in this update.
- **Contribution:** probabilistic forecast distributions distinguish uncertainty-aware operational forecasts from single retrospective point models.
- **Response:** no claimed confidence for day-ahead reliability or outage probability from same-day ERA5 weather and a deterministic Ridge fit.

## Tier 3 — meteorological provenance and physical-model constraints

### 14. Hersbach et al. (2020) — ERA5 global reanalysis [W01]

- **Citation:** [QJRMS, DOI 10.1002/qj.3803](https://doi.org/10.1002/qj.3803).
- **Access:** **bibliographic + publisher abstract**.
- **Result:** reanalysis produces physically coherent historical model-based fields, not measured Kerala station weather and not contemporaneous forecast issuance.
- **Response:** preserve original retrieval, source revision/grid-cell choices; five point mean represents a modelling assumption.

### 15. Cucchi et al. (2020) — WFDE5 and time semantics [W02]

- **Citation:** [Earth System Science Data, DOI 10.5194/essd-12-2097-2020](https://essd.copernicus.org/articles/12/2097/2020/).
- **Access:** **FULL/SECTIONS**, open publisher discussion, temporal validity and forcing QA checked.
- **Finding:** hourly ERA5-derived product and bias correction; **accumulated weather fields' reported validity time represents end of supported interval**, unlike weather time snapshots.
- **Response:** validate IST civil-day support and accumulation intervals, especially midnight crossings; five-point 24-sample pass alone insufficient. WFDE5 resolution/source is different; not an automatic replacement.

### 16. Pfenninger, Hawkes & Keirstead (2014) — 21st-century energy modelling [M01]

- **Citation:** [Renewable and Sustainable Energy Reviews, DOI 10.1016/j.rser.2014.02.003](https://doi.org/10.1016/j.rser.2014.02.003).
- **Access:** **bibliographic/abstract prior review**, no full line-specific method extraction this turn.
- **Principle:** question-led modelling, temporal/geographic granularity, uncertainty and transparency.
- **Response:** do not respond to missing interval Kerala data by adding a more complex solver or 2040 dispatch model.

### 17. DeCarolis et al. (2017) — formal energy-optimization best practice [M02]

- **Citation:** [Applied Energy, DOI 10.1016/j.apenergy.2017.03.001](https://doi.org/10.1016/j.apenergy.2017.03.001).
- **Access:** **bibliographic/abstract prior review**.
- **Principle:** model formulation/verification, data, assumption transparency and communication for decision use.
- **Response:** distinguish hypothetical hydro cases from physically supported historical operations; document source gates and exact model limitations.

### 18. Coupled hydrological and power scheduling systematic review (2026) [H01]

- **Citation:** [Renewable and Sustainable Energy Reviews, DOI 10.1016/j.rser.2026.116940](https://doi.org/10.1016/j.rser.2026.116940).
- **Access:** **publisher abstract/highlights** (review of **106** published short-term hydro studies).
- **Finding:** fully iterative water/electricity co-coupling and independent real-world verification are infrequent; significant region/station-size bias.
- **Response:** require observed reservoir/inflow/release/plant dispatch and hydro unit constraints before claiming a usable flexible-resource response; unbounded energy shifting is upper-bound only.

## Tier 4 — essential official Kerala contextual sources (not peer-reviewed)

### 19. CSTEP (2024) — Kerala Energy Transition Roadmap 2040 [O01]

- **Source:** [CSTEP official report](https://cstep.in/publication/kerala-energy-transition-roadmap-2040/).
- **Access:** **OFFICIAL summary**, not independent model/data replication.
- **Content:** renewable 2040 energy transition scenarios, material imports, national RPO/transition outlook.
- **Response:** no first Kerala2040 energy mix/roadmap claim. Treat CSTEP's existing assumptions/data with their own dates and scopes, not actual operational measurements.

### 20. WRI India (2026) — Kerala clean energy pathways [O03]

- **Source:** [WRI India issue brief, published 29 Sep 2026](https://wri-india.org/research/pathways-keralas-clean-energy-transition).
- **Access:** **OFFICIAL summary**, not independently reproduced scenario work.
- **Content:** approximate 70% power imports under its definition, implications of domestic renewable expansion, storage and procurement to 2040.
- **Response:** no claim Kerala2040 uniquely identified import dependence or 2040 pathway opportunities. Power imports in a planning report are not authenticated SLDC **actual 15-minute net drawal**.

## Remaining reference classes and full-matrix caution

The [44-record curated matrix](EVIDENCE_MATRIX.csv) further covers resource adequacy (CEA), Kerala daily source archives, more electricity-forecasting reviews, PRISMA-ScR methods, energy model open-data ethics, hydropower flexibility, extreme-weather models and renewable weather calibration (e.g. Stafford/Pfenninger). Those sources are not simply “fully reviewed” by their presence in the matrix; consult \`access_level\` before attribution. Metadata rows with \`authors_to_verify\` remain deliberately unresolved and should not enter a final manuscript bibliography until exact author list is confirmed.

**Critical appraisal is a judgement about the implication of *what was accessible*.** It does not prove that missing full-text authors failed to perform a method not mentioned in their abstract. Do not make this review appear like systematic dual-screened PRISMA work.

## A twenty-paper novelty question checklist

1. Can paper A show a *genuinely different original observed variable*, not just different agency filenames? Need source dictionaries.
2. Would a strict FY later-year model rank weather differently after holding actual data scope and target scale constant?
3. Are full-sample detrending choices material under fair matched reproduction? Need documented experiment, not allegation.
4. Does private SLDC original-source QA change the pattern of missing/excluded stress days?
5. Is there a difference in India/IST day-period reporting boundary between sources?
6. Does changing equal-five-point versus population-weighted weather materially affect conclusions?
7. Are extreme-day findings stable after independent residual serial-dependence checks?
8. Can a journal reviewer reproduce original inputs legally, or only legal aggregates/provenance metadata?
9. Does a data ontology yield generalizable measurable improvements beyond a government field glossary?
10. If all substantive differences vanish, will we explicitly publish a technical report rather than a duplicative article?

**End point:** submit **one scientifically differentiated manuscript or an honestly scoped report**; originality remains conditional on original-source data and independent tests, not literature rhetoric.
