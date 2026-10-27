# Kerala2040: critical literature synthesis for an independently reproducible research paper

**Version:** v0.1 · **Prepared:** 27 October 2026  
**Coverage:** published evidence available up to 27 October 2026  
**Research status:** structured critical narrative/scoping-oriented synthesis; **not** a completed PRISMA systematic review, meta-analysis, manuscript submission, or proof of a new Kerala2040 empirical result.  
**Reproducibility:** [44-record evidence matrix](EVIDENCE_MATRIX.csv) and [review protocol/search log](REVIEW_PROTOCOL_AND_SEARCH_LOG.md). Direct prior-art source-code audit: [Hunt & Bloomfield comparison](../../studies/paper-a-2027/HUNT_BLOOMFIELD_PRIOR_ART_REVIEW_2026-10-27.md).

## Abstract (critical review; not the empirical paper's abstract)

The Kerala2040 research programme aims to understand Kerala's observed electricity-demand chronology, weather association, import dependence and hydropower flexibility while retaining strict boundaries between measurements, reanalysis, proxies and hypothetical system models. A significant obstacle to publishing a straightforward weather–electricity-demand study is that closely overlapping Indian research already exists. In particular, Harish, Singh and Tongia (2020) estimated heterogeneous temperature responses for Delhi and Indian states; Hunt and Bloomfield (2025) published daily Indian-state demand models, including explicit Kerala-specific ERA5, XGBoost and SHAP analyses and openly indexed benchmark data; and Porwal et al. (2026) studied state-level weather and demand using Grid-India and Open-Meteo. No defensible novelty claim can be based simply on applying machine learning or reanalysis to Kerala.

This review synthesizes 44 selected scholarly, official and data-provider works spanning six evidence families: observed-demand estimands and reporting boundaries, weather and cooling responses, temporal evaluation and algorithm comparisons, ERA5 source integrity and spatial representation, hydropower and grid operational constraints, and transparent open energy science. The evidence points toward a narrower falsifiable contribution: investigate whether independent Kerala SLDC operational source records, national Grid-India energy-met data, temporal evaluations and original-source quality controls are definitionally and statistically comparable; quantify if measurement and evaluation differences change interpretation, without claiming causal elasticity or a day-ahead forecast. Source-level data admission and a prior-art novelty gate must precede broad new model fitting. An alternate source-quality/accounting methods paper is retained but is not assumed publishable merely because the primary weather study is blocked.

**Keywords:** Kerala; electric power consumption; Grid-India; SLDC; electricity accounting; ERA5; monsoon; weather sensitivity; temporal validation; data provenance; energy-systems modelling; open science.

---

## 1. Research problem and the legitimate scope of a first paper

A convincing journal paper is not a repository of every useful experiment built during Kerala2040. The source and inferential boundary must match a single research question. Existing Kerala2040 work already contains a source-audited FY2024–25 subset of daily Kerala SLDC statements, same-day ERA5 weather at five points, model comparisons and physical-model screens. But neither a long and complete original historical interval load series nor physically certified station-level hydro flexibility has been admitted. The 23 October 2026 public research freeze expressly prevents treating exploratory hourly load proxies, hydro reservoir assumptions or network analyses as measured reality. The 2026–27 plan's first empirical manuscript, Paper A, is therefore limited to **qualified original daily SLDC operational electricity consumption, measured in million units/day (MU/day)** and *retrospective* weather relationships. These bounds come from the [existing project charter](https://github.com/abhijith-sivaprasadan/kerala2040/pull/135), not from a newly executed study.

At least three questions have to be separated:

1. **Data fidelity:** What does a published daily Kerala electricity number measure? How complete, revised and recoverable is the original source? Can it be compared with a different publisher's number?
2. **Retrospective association:** On a qualified historical daily series, do realized weather and calendar features describe the observed energy-met variation, including across changes in financial year?
3. **Operational planning:** Can a constrained real hydro and interchange system offset particular intraday shortages or support a 2040 transition?

Answers to the first two cannot automatically answer the third. A 24-hour energy total can hide a very high evening peak and a very low early-morning trough. A state daily energy record cannot reveal actual 15-minute contingency response, loss-of-load expectation or legal availability of plant water releases. Hence **system adequacy, measured demand/shortage attribution and optimal 2040 investment conclusions remain out of scope** for Paper A until authentic intervals and physical constraint records exist.

### 1.1 Outcome variables that should never be silently conflated

| Quantity | Typical owner/product | What it could describe | Why apparent agreement is not enough |
|---|---|---|---|
| Daily state 'energy met' | Grid-India Power Supply Position; Hunt & Bloomfield archive | Electricity supplied/met according to national reporting convention | Original national source definition, revision history, any residual adjustments and reporting date must be verified |
| Daily Kerala SLDC 'consumption' | Kerala SLDC daily operational system statement | Daily operational state-side consumption field as printed | Field and system boundary need source-level explanation; matching MU/day units do not prove equivalence to Grid-India |
| Annual consumer-side use | Kerala State Planning Board Economic Review; KSEBL reporting | Published consumer-category consumption over a financial year | Consumer sales, system operations, billing, own-use, losses and embedded generation may differ; cannot subtract to infer imports |
| Scheduled drawal | Dispatch/interchange schedules in regional records | A planned or contracted interchange schedule | Schedule is not actual delivered interstate import/export |
| Actual drawal / interchange | Settlement/metered regional/SLDC record | Metered movement across interface at specified blocks | Requires interval, sign, aggregation convention and revision version |
| Hydro station energy/reservoir | KSEBL daily reports and station records | Energy produced or a water/energy stock measure | Does not alone prove available ramping, output at arbitrary hour, multi-reservoir routing, spill or irrigation constraints |
| ERA5 meteorological variables | ECMWF/Copernicus | Reconstructed gridded atmospheric state and accumulated fluxes | Neither a station measurement nor an ex ante day-ahead weather prediction |

**Proposed primary research contribution:** make the definitions and exact period/quality rules observable and reproducible; perform *meaning-matched* comparisons only after admission. A mismatch is not automatically an error, shortage or proof that one provider's record is superior.

---

## 2. Direct Indian and Kerala prior art: the novelty threat is real

### 2.1 Hunt and Bloomfield (2025): closest published full-journal competitor

[Hunt and Bloomfield, *Building and explaining data-driven energy demand models for Indian states*, Environmental Research: Energy (2025), DOI 10.1088/2753-3751/adc7bc](https://doi.org/10.1088/2753-3751/adc7bc) [D01] is **required reading before any new Paper A experiment**. The authors trained daily state-level weather-sensitive XGBoost models using Grid-India/POSOCO Power Supply Position report data and population-weighted meteorological variables. Their features include ERA5-derived atmospheric variables, the universal thermal climate index (UTCI), seasonal/calendar variables and different meteorological temporal aggregates. Their work describes substantial state variation, with a Kerala-specific analysis and SHAP interpretation. The published Kerala test R² of about **0.835** refers to the authors' **own transformed and randomly partitioned model task**, not a benchmark score for our original-unit daily SLDC load. The 2025 paper and its original open data already remove several apparent novelty claims.

The full-text methods/results passages and authors' publicly released [demand modelling functions](https://github.com/kieranmrhunt/india-renewable/blob/master/notebooks/demand/functions.py) were inspected in the earlier research branch. The relevant released default code performs a shuffled 80% training / 15% test / 5% validation split after preprocessing; it also contains an alternative withheld-calendar-year argument which **was not selected in the checked published training notebook**. Critically, the checked workflow runs smoothing/detrending and variance adjustment on the target before the random data split. This is a *different analytical target* from predicting future observed original MU/day and creates a reasonable transformation-sensitivity question. We **must not assert** that the authors committed misconduct or that a specific amount of their reported R² is artificially inflated without an exact independent replication and counterfactual rerun.

A source-split CSV also has duplicate date labels and some date labels assigned to different partitions, but the checked code overwrites that generic split export for multiple states. It cannot be attributed as a leakage event affecting Kerala-specific test scores. This nuance matters; careless criticism of a stronger existing paper would weaken our own credibility.

The authors publicly list an [Indian-state and Kerala dataset on Zenodo](https://doi.org/10.5281/zenodo.14983362), with original and corrected Grid-India demand measures, peaks and meteorology. Their reported model-output file contains transformed observed/predicted values and **must not be used as original MU/day**. Retrieve the national original/corrected source series with exact checksums and compare physical field definitions before any numeric source-boundary conclusion. As of this review, the specific original Zenodo CSV bytes have not been independently hash-admitted into the Kerala2040 research environment.

**Critical appraisal:** This paper offers substantial geographic coverage, public data/code and an interpretable ML workflow. Its randomized and transformed evaluation answers a different question from strict year-forward, original-unit error in a particular Kerala SLDC field. That difference can motivate a new falsifiable experiment, but chronology alone is **not** a sufficient journal novelty claim. A paper titled simply 'Weather-aware Kerala electricity-demand prediction with XGBoost and ERA5' would largely reoccupy established territory. See the more detailed [code and publication comparison](../../studies/paper-a-2027/HUNT_BLOOMFIELD_PRIOR_ART_REVIEW_2026-10-27.md).

### 2.2 Harish, Singh and Tongia (2020): India's temperature-demand response is not unexplored

[Harish, Singh and Tongia, *Impact of temperature on electricity demand: Evidence from Delhi and Indian states*, Energy Policy (2020), DOI 10.1016/j.enpol.2020.111445](https://doi.org/10.1016/j.enpol.2020.111445) [D02] studies temperature response at household and aggregate levels. The publisher describes substantial response heterogeneity across states and income groups. It is therefore incorrect to frame Kerala2040 as the first attempt to identify Indian regional weather-electricity relationships. Equally, coefficients and household patterns estimated in Delhi are **not** automatically applicable to Kerala's aggregate operational series. A household's cooling use is mediated by equipment ownership, income, electricity tariffs, behaviour, season and context; statewide correlations may combine multiple effects with cooling, tourism, rainfall, industry and non-weather demand trends.

**Direct implication:** our model should call variables 'weather-associated' rather than 'causal cooling demand', and results should not be interpreted as uniquely estimating temperature elasticity absent a separate identification strategy. Socioeconomic heterogeneity and aggregation bias must appear in the Discussion.

### 2.3 Porwal et al. (2026): state-level composite-weather effects already studied

[Porwal et al., *Granular Analysis of Weather-Influenced Electricity Demand in Indian States*, IEEE IC3ECSBHI (2026), DOI 10.1109/IC3ECSBHI67834.2026.11468867](https://doi.org/10.1109/IC3ECSBHI67834.2026.11468867) [D03] examines daily 2023–October 2025 Indian-state demand from Grid-India and Open-Meteo data and reports geographic variation in weather dependence. The publisher abstract describes a temperature/humidity/rainfall-related composite approach. **Full text remains unverified**, so assertions about Kerala-specific methods, leakage controls, exact splits, their original-data revisions or any state-by-state statistical performance are premature.

**Direct implication:** simply claiming that temperature, humidity and rain affect different Indian states also overlaps prior art. A full IEEE paper review is necessary before final manuscript novelty wording.

### 2.4 Babu, Ramadesigan and Banerjee (2026): long-term demand and electrification occupy separate ground

[Babu et al., *Medium and long-term electricity demand forecasting for India – Incorporating EV charging and space cooling impacts*, Applied Energy (2026), DOI 10.1016/j.apenergy.2026.128069](https://doi.org/10.1016/j.apenergy.2026.128069) [D04] develops medium/long-horizon India electricity-demand frameworks accounting for EV and cooling effects, including possible timing shifts in peak demand. It differs sharply from Paper A's original operational daily observed target. Comparing headline long-run MAPE with the RMSE of a retrospective weather-augmented daily regression is invalid. Its presence also means a Kerala2040 **2040 extrapolation** cannot be called a first Indian demand/cooling scenario method on the basis of a regional implementation alone.

### 2.5 Household cooling studies: motivation, not a state-level identification strategy

An [Energy Informatics (2022) monitoring study of Indian AC patterns, DOI 10.1186/s42162-022-00228-1](https://doi.org/10.1186/s42162-022-00228-1) [D05] reports monitored urban homes and substantial summer/night AC usage. A separate [Indian-dwellings study (2024), DOI 10.1080/13467581.2024.2314492](https://doi.org/10.1080/13467581.2024.2314492) [D06] uses 41 dwellings and finds differences related to AC ownership, income and other household variables. Neither is a representative observed sample of all Kerala load, and neither can establish how many megawatts of Kerala state demand were attributable to AC in a particular hour.

The appropriate causal language is: humidity, temperature and season may serve as explanatory covariates for daily reported load; **a machine-learning feature contribution is not an estimate of a specific appliance's physical demand contribution**. Study geography, socioeconomics, measured variable and inferential method must remain explicit.

### 2.6 Direct-prior-art conclusion

| Claim | Literature status | Permissible Kerala2040 formulation |
|---|---|---|
| 'First weather ML for Kerala' | **Contradicted** by Hunt & Bloomfield (2025) | Do not use |
| 'First Indian state temperature–demand relationship' | **Contradicted** by Harish et al. (2020) and successors | Do not use |
| 'Using ERA5/SHAP/XGBoost is novel' | **Contradicted** by 2025 source | Do not use |
| 'First public multiyear Indian daily demand dataset' | **Contradicted** by 2025 Zenodo resource | Do not use |
| 'SLDC and national energy-met definitions differ materially' | **Not established** by physical-boundary matching yet | Research question; possible null result |
| 'Year-forward and original-unit evaluation changes inferred weather skill' | **Not established** by executed matched experiment | Potential main falsifiable result |
| 'Original SLDC provenance produces a transferable accounting method' | **Not established** beyond existing repository QA | Candidate Paper A0 research contribution if reproducible and nontrivial |
| 'Five Kerala ERA5 points outperform published population-weighted weather' | **Not established** and potentially false | Secondary paired test only after equal-target coverage |

---

## 3. Model comparison literature: why the strongest model is not necessarily the best research

### 3.1 Forecasting reviews emphasize the task and evaluative comparability

[Kuster, Rezgui and Mourshed (2017), *Electrical load forecasting models: A critical systematic review*, DOI 10.1016/j.scs.2017.08.009](https://doi.org/10.1016/j.scs.2017.08.009) [F01] found that comparing reported errors across heterogeneous electricity forecasting studies is often uninformative because scales, source definitions, tasks, metrics and data periods differ. This directly defeats an easy but misleading claim that Kerala2040's reported 37% relative RMSE improvement in a specific exposed FY2024–25 retrospective comparison 'beats' a competing 2025 Kerala study's reported R² of 0.835. One is relative RMSE against another baseline on different source dates; the other is R² on a transformed target, model and split. No valid mathematical ranking can be obtained from these two headlines.

[Hong and Fan (2016), *Probabilistic electric load forecasting: A tutorial review*, DOI 10.1016/j.ijforecast.2015.11.011](https://doi.org/10.1016/j.ijforecast.2015.11.011) [F02] distinguishes point from probabilistic forecasting and forecast-horizon/use-case evaluation. We should never label same-day ERA5 retrospective association as a day-ahead forecast, much less provide load probability bands without calibration. If a future utility-oriented application is pursued, it needs **weather forecasts available at the operational decision time**, a defined forecast issue hour, horizon-specific model and independently measured targets.

The [2020 electricity load forecasting systematic review, DOI 10.1186/s43067-020-00021-8](https://doi.org/10.1186/s43067-020-00021-8) [F03] and the [2026 hybrid/short-term forecasting review, DOI 10.1016/j.ecmx.2026.102065](https://doi.org/10.1016/j.ecmx.2026.102065) [F04] reinforce that modelling class alone does not guarantee comparability and that review authors scrutinize weak baselines, inconsistent validation and selection bias. The latter is a secondary systematic review whose exact screening standards should not be assumed to transfer to our own project merely by citation.

### 3.2 A fixed learner isolates a research question from algorithm shopping

For Paper A, the immediate question is not 'Can Optuna find a more accurate model?' but 'How much consistent additional association do source-admitted same-day weather features provide beyond a calendar-only description?' A fixed calendar-only Ridge learner and identical Ridge plus predeclared weather features hold model capacity comparatively stable. Report each later FY with paired observed dates. Secondary XGBoost/LightGBM comparisons may be useful to test whether results depend on nonlinear model flexibility, but choosing the most favourable tuned algorithm after seeing test years would change the estimand.

The [2026 leakage-aware temporal preprocessing benchmark, DOI 10.1016/j.ecmx.2026.101791](https://doi.org/10.1016/j.ecmx.2026.101791) [F05] uses fixed modelling architecture to isolate preprocessing and covariate effects under rolling-origin evaluation. Its datasets are **hourly** and do not establish a Kerala daily demand result, but its experimental logic is directly applicable. Our declared treatment should modify the weather covariates, not every aspect of data cleaning, model family and selection procedure simultaneously.

### 3.3 A small valid baseline is more valuable than a complex unverifiable ensemble

A seasonal-naive historical comparison is necessary to contextualize error magnitude. It must look up only previously **observed qualified** dates; if an earlier comparison date is missing, it cannot borrow an unobserved real value. A regularized calendar regression that standardizes within each training fold avoids test-set distribution statistics leaking into training. The 'identical matched days' rule is essential: weather model errors will appear artificially better if hard missing-weather days are removed from its test subset while calendar errors are calculated over a broader set.

**Critical inference:** a complex algorithm that fits the observed year closely can be useful engineering, but it is not by itself stronger evidence of a stable underlying physical weather effect. The project needs replicated definition-specific observation and negative-result reporting first.

---

## 4. Time-series validity: prediction chronology is not scientist blindness

### 4.1 The literature supports *context-specific* validation, not slogans

[Roberts et al. (2017), *Cross-validation strategies for data with temporal, spatial, hierarchical, or phylogenetic structure*, DOI 10.1111/ecog.02881](https://doi.org/10.1111/ecog.02881) [V01] explains how data dependence and non-causal covariates can bias naive randomized evaluation. [Cerqueira, Torgo and Mozetic (2020), *Evaluating time series forecasting models: an empirical study on performance estimation methods*, DOI 10.1007/s10994-020-05910-7](https://doi.org/10.1007/s10994-020-05910-7) [V02] demonstrates that the suitability of blocked CV and repeated holdout depends on stationary/nonstationary behaviour and intended task. [Bergmeir, Hyndman and Koo (2018), DOI 10.1016/j.csda.2017.11.003](https://doi.org/10.1016/j.csda.2017.11.003) [V03] cautions that ordinary cross-validation is not *universally invalid* for every autoregressive prediction problem. It would be inappropriate to dismiss a published model by claiming any random split is always misconduct.

What is defensible is narrower: if the purpose of Paper A is year-forward temporal transfer, the training algorithm should not see **future target values** during fitting/selection, and all treatment comparisons should use exact identical, genuinely later test observations. This evaluates a different question from random-within-history interpolation. It does **not** establish a real operational forecast without weather forecasts issued ex ante.

### 4.2 Prior exposure cannot be undone by later protocol wording

The existing proposed folds are:

- **F1:** fit on qualified historical data through 31 March 2022; test FY2022–23.
- **F2:** fit through 31 March 2023; test FY2023–24.
- **F3:** fit through 31 March 2024; test FY2024–25.

These are intended **retrospective expanding-origin evaluations**. The FY2024–25 period is already known to have informed Kerala2040's earlier weather experiments, so F3 is **analysis-exposed**. The analyst exposure of F1 and F2 is still being audited: date-ordered refitting cannot make a pre-examined test year pristine. Later years may have shaped feature selection, hypothesis choice, source repair rules and the very selection of which periods to report.

Hence neither 'three independent confirmatory replications' nor 'three blind future holdouts' is justified. At most, we can say chronological training on earlier target dates evaluated later observed target periods, with research design exposure explicitly disclosed. We must keep every registered financial year and negative weather gain, not reconstruct an impressive sequence from cherry-picked months.

### 4.3 Transformation and availability audits deserve their own results

A target transformation is not inherently bad. Detrending and season/variance standardization can be scientifically appropriate to isolate anomalous weather effects. But a transformation computed using **all observation dates** before the split can use information about the later period. One study's target 'weather-driven variation after removing long-term socioeconomic growth' is different from another's 'observed daily MU'. In this case, the model score may change because the target has changed, not because one model is intrinsically superior.

Prior-art preprocessing audit experiments should therefore:
1. reproduce the author's published transformed target *as a descriptive replication*, with clear rights;
2. reproduce its date partitions without misattributing a generic CSV to Kerala's particular split;
3. separately compare matched tests on original daily values, using source-equivalent definitions;
4. if feasible, compare train-only vs full-history transforms in a **post-hoc sensitivity** clearly labelled as such;
5. not allege numerical inflation or leakage impact without a documented controlled rerun.

That is a stronger methodological conversation with the 2025 paper than simply asserting 'we use chronological cross-validation and they did not'.

### 4.4 Error metrics and dependence

[Hyndman and Koehler (2006), *Another look at measures of forecast accuracy*, DOI 10.1016/j.ijforecast.2006.03.001](https://doi.org/10.1016/j.ijforecast.2006.03.001) [V04] motivates transparent alternatives to misleading percentage error measures, including scaled absolute errors. Our first outcomes should be per-year RMSE and MAE in **MU/day**, plus a signed error reduction relative to exactly matched calendar-only Ridge:

**Weather-added RMSE skill (%) = 100 × (RMSE_calendar − RMSE_weather) / RMSE_calendar.**

Positive means better fit; negative means deterioration. A pooled average can hide a bad financial year. At only three candidate FY periods there is no credible basis for narrow independent-year confidence intervals. Daily residuals within a monsoon cycle are autocorrelated and missingness may cluster during exceptional weather. Any block-bootstrap interval must be labelled a limited sensitivity estimate, with reasonable block length and assumptions established before inspecting its result. A MASE denominator must derive from training-only observed lags; it may be undefined and should then be reported as such.

A positive retrospective coefficient or SHAP effect remains **model-conditional association**, not a causal estimate of electricity needed for air conditioning under a hypothetical climate intervention.

---

## 5. ERA5 and meteorological exposure: stronger original-source proof is essential

### 5.1 Reanalysis is neither a weather station nor a forecast issue

[Hersbach et al. (2020), *The ERA5 global reanalysis*, DOI 10.1002/qj.3803](https://doi.org/10.1002/qj.3803) [W01] is the scientific foundation for using historical ERA5 variables. It documents a gridded reanalysis system; its values are a model/assimilation product and may differ from local ground stations, notably in topographically complex areas. [Cucchi et al. (2020), *WFDE5: bias-adjusted ERA5 reanalysis data for impact studies*, DOI 10.5194/essd-12-2097-2020](https://doi.org/10.5194/essd-12-2097-2020) [W02] illustrates how impact-study weather datasets may apply further corrections. The existence of bias-corrected derivatives does **not** show our specific five-point raw ERA5 is biased by a known quantity: validation would require appropriate local observations.

The proposed five Kerala representative centers—Thiruvananthapuram, Kochi, Palakkad, Kozhikode and Kannur—are declared points, **not automatically Kerala's population-weighted, load-weighted or area-weighted mean**. Importantly, Hunt and Bloomfield already used population-weighted state weather. Our equal five-point alternative is therefore **not** original just because its geometry is different; demonstrating how equal-weight vs population-weight assumptions change fitted inference would require a matched source-verifiable sensitivity experiment.

### 5.2 Time validity and accumulated fluxes

ERA5 products contain instantaneous, accumulated and mean-rate parameters. ECMWF's [official temporal-semantics documentation](https://confluence.ecmwf.int/pages/viewpage.action?pageId=184288663) [W04] describes UTC validity times and forecast initialization/step conventions; an accumulated field at a stated validity hour can refer to the **preceding accumulation interval**, not a momentary 'rainfall at 00:00' observation. [Cucchi et al. (2020)](https://doi.org/10.5194/essd-12-2097-2020) explains such conversion in an impact-study source context.

Kerala's clock uses UTC+05:30. A UTC hourly interval can cross an IST calendar boundary. Merely assigning each UTC timestamp to its converted IST date and averaging points may violate the physical support of the variable, especially solar energy and precipitation totals. The model intake must establish which hourly intervals contribute to the local civil day, whether fractional hour assignment is needed, and independently reproduce energy/rainfall-integral conservation. Each qualified weather day needs complete original source hours for each of the five declared points, exact unit/geometry/variable checks, original hashes, and a comparison with an independent aggregation routine.

The [ECMWF post-processed ERA5 daily-statistics product, DOI 10.24381/cds.4991cf48](https://doi.org/10.24381/cds.4991cf48) [W03] offers a useful possible cross-check because it allows time-zone-shifted daily summaries, but it is explicitly derived during retrieval rather than a permanently archived static daily product. This too requires source-version and variable-convention documentation before treating two aggregates as equivalent.

### 5.3 Explanatory weather vs operational weather

A **same-day realized reanalysis** value for Kerala's local day can be available only after the weather occurred and data were assimilated. As an explanatory retrospective model, this is legitimate. As a 'day-ahead' tool predicting demand before the day begins, it is not a valid input unless a real issued weather forecast with the same horizon is supplied. Paper A's title, abstract and conclusions should therefore avoid 'day-ahead forecast accuracy' and focus on weather-linked *retrospective description* or carefully qualified year-forward **backtests conditional on realized weather**.

Rainfall, wind, solar, relative humidity and climate indices can be correlated. Interpretable model contributions should be checked for collinearity and seasonal confounding; five weather families plus multiple lags on a short annual sample can produce apparently intricate explanations without a robust independent effect.

---

## 6. Kerala's 2040 context: distinguish existing plans from new evidence

### 6.1 The state already has substantial published transition planning

[CSTEP's *Kerala Energy Transition Roadmap 2040* (2024)](https://cstep.in/publication/kerala-energy-transition-roadmap-2040/) [O01] is a direct policy/energy-modelling antecedent. Its official summary explicitly characterizes Kerala's dependence on imported electricity and studies renewable transition pathways through FY2040. The [Central Electricity Authority's Kerala resource-adequacy plan to FY2035–36](https://cea.nic.in/resource_adequacy_st/report-on-resource-adequacy-plan-for-kerala-up-to-2035-36/) [O02] is a directly relevant formal generation/procurement planning counterpart. [WRI India's *Pathways for Kerala's Clean Energy Transition* issue brief (29 September 2026)](https://wri-india.org/research/pathways-keralas-clean-energy-transition) [O03] also examines renewable expansion, procurement, storage and the practicality of a low-thermal energy transition.

These sources mean a new Kerala '2040 roadmap' must not be marketed as the first independent study of Kerala's import dependence or renewable transition. More importantly, the scenario inputs and objectives in these works differ: a regional historical data/observability audit is **not an alternative investment optimisation**. Comparisons should record baseline year, demand projections, renewable potential, import/tariff assumptions, hydro constraints, adequacy metric and outage/transfer meaning before treating two scenario numbers as contradictory.

The present review uses these official web descriptions to establish scope. **It has not verified every underlying model equation, hourly load-input file, capacity cost assumption or technical appendix.** Those full source documents must be read and source-registered before any numerical critical comparison or model replication is published.

### 6.2 Power supply and consumer accounting have multiple legitimate boundaries

The [Government of India's 2026 parliamentary Power Supply Position annexures](https://www.pib.gov.in/PressReleasePage.aspx?PRID=2223710) [O04] distinguish energy requirement, energy supplied, energy not supplied, peak demand, peak met and unmet peak. This illustrates why a generic 'demand' label is insufficient. The State Planning Board's published annual consumer-side use series and Kerala SLDC daily operating consumption are also different named measures. Their sums should **not** be set equal by default or subtracted to estimate imports or shortages.

A proper source-comparability study should define a field ontology containing:
- physical boundary (consumer metered/billed vs grid supply vs power scheduled vs actual interface);
- energy/power stock/flow dimension (MU, MWh, MW, reservoir level);
- observation frequency and IST or other accounting interval;
- owning publisher/reporting office and data-vintage/revision;
- original source type, hash, rights and missingness status;
- admissible same-definition joins and disallowed cross-boundary calculations.

The main publication opportunity is potentially a **demonstrated consequence** of these definitions on a numeric/statistical conclusion, not merely a table listing agency products. If a crosswalk reveals no material differences after harmonization, that itself limits the novelty of an ontology-only paper and should be reported.

### 6.3 Missing reports and source exposure are scientifically consequential

In the publicly established FY2024–25 Kerala SLDC series, the project records 354 source-report days out of 365. These are the **source coverage of a particular document series**, not a basis for inventing the unobserved dates. Missingness could be associated with maintenance, website archiving or unusual operating conditions, and no mechanism should be assigned without source evidence. A 354-day sum cannot be presented as a measured complete 365-day annual energy total. If an absent document date corresponds to a monsoon system event, dropping it may systematically affect evaluated seasonal skill; this must be assessed as missingness sensitivity, not replaced with modeled observations.

The private multi-FY archive reportedly contains 2,606 source-dated records across 2019–26, but those are not all automatically qualified target days. A methods paper must verify original compressed/uncompressed hashes, extraction fields, validity checks and source-date/right restrictions. Publishing raw records or a linked GitHub ZIP is not automatically licensed merely because the reports were publicly readable.

---

## 7. Hydropower, monsoon risk, transmission and import: important but physically constrained

### 7.1 Hydro flexibility is not nameplate MW

The [2026 systematic review of coupled hydrological and energy scheduling, DOI 10.1016/j.rser.2026.116940](https://doi.org/10.1016/j.rser.2026.116940) [H01] surveys the challenge of short-term hydro regulation models that jointly reflect power and hydrology, noting practical validation gaps. [The value of hydropower flexibility for electricity system decarbonization (2025), DOI 10.1016/j.egyr.2025.02.019](https://doi.org/10.1016/j.egyr.2025.02.019) [H02] explicitly considers how non-power constraints and transmission congestion limit idealized hydro flexibility.

For Kerala2040, a nameplate megawatt value, same-day generated MU and reservoir energy-equivalent figure do not prove that the corresponding plants could deliver an arbitrary additional high-load-hour burst. Authentic constraint admission may require per-unit availability, reservoir storage–head relation, releases/inflows, cascade continuity, irrigation and environmental commitments, forced outages, minimum load, ramp rate and transfer limits. If those are unknown, the only defensible numerical screen is an **optimistic upper bound** and a precise explanation of what constraints were omitted.

### 7.2 Monsoon precipitation does not establish reservoir dispatchability

A [2025 critical review of Kerala flood risk after 2018, DOI 10.1016/j.ejrh.2025.102262](https://doi.org/10.1016/j.ejrh.2025.102262) [H03] describes a large climate/hydrology research literature on spatial flood risks and method gaps. That work motivates attention to extreme rain and changing hydrological dynamics but does not authorize inferring free hydro dispatch from rainfall. The flood hazard, reservoir regulatory and grid balancing literatures study different physical objects. A monsoon river basin could see substantial precipitation while water release or plant operation is limited by flood management, downstream safety, storage state and other commitments.

### 7.3 Network and import constraints must come from original operators

Regional schedules, state procurement amounts and actual net meter flows are not interchangeable. An existing planning transfer ceiling is not automatically a continuously deliverable physical limit under all N−1 outages. Without original interval interstate drawal data and the applicable source-defined operating envelope, the project's 2040 reliability/LOLE and particular contingency claims are illustrative, not measured or physically calibrated.

**Manuscript strategy:** no attempt to force a single paper to answer historical weather association and full hydro/load-shedding attribution. Paper B should be separately designed **only after** these physical source constraints pass the June gate. The present literature does not rescue unverified inputs.

---

## 8. Open-energy science, uncertainty and research integrity

### 8.1 Scientific question before toolchain selection

[Pfenninger, Hawkes and Keirstead (2014), DOI 10.1016/j.rser.2014.02.003](https://doi.org/10.1016/j.rser.2014.02.003) [M01] examines the mismatch between energy-system research challenges and model formulation, resolution and uncertainty. [DeCarolis et al. (2017), DOI 10.1016/j.apenergy.2017.03.001](https://doi.org/10.1016/j.apenergy.2017.03.001) [M02] formalizes transparent, question-driven energy modelling practice. **A PyPSA or OSeMOSYS model is a tool for testing assumed equations, not a certificate that its inputs represent Kerala's observed operation.** The existence of [PyPSA](https://doi.org/10.5334/jors.188) [M06] or [OSeMOSYS](https://doi.org/10.1016/j.enpol.2011.06.033) [M07] code does not establish the source validity of a reserve constraint, plant dispatch or system adequacy result.

[Yue et al. (2018), DOI 10.1016/j.esr.2018.06.003](https://doi.org/10.1016/j.esr.2018.06.003) [M05] reviews uncertainty assessment techniques in energy optimization. Methods such as the [Morris elementary-effects screening](https://doi.org/10.1080/00401706.1991.10484804) [M08] and [Sobol global sensitivity analysis](https://doi.org/10.1016/S0378-4754(00)00270-6) [M09] can quantify response to **defined input distributions/ranges**, but running them on arbitrarily guessed Kerala hydropower/transfer limits will not make those limits physically credible. The data boundary must precede model sensitivity.

### 8.2 Open code, source rights and permanent evidence are different objects

[Pfenninger et al. (2017), DOI 10.1016/j.enpol.2016.11.046](https://doi.org/10.1016/j.enpol.2016.11.046) [M03] and [Pfenninger et al. (2018), DOI 10.1016/j.esr.2017.12.002](https://doi.org/10.1016/j.esr.2017.12.002) [M04] argue for transparent energy-model code and data with practical attention to ownership, licensing and documentation. A public model implementation, a publicly readable official report, a data export license and permission to put bulk original records in Zenodo are **not the same permission**.

Kerala2040 should publish: hypothesis/protocol versions, executable analysis code and dependency versions, original source identifiers and file hashes where safe, documented inclusion/exclusion statuses, reproducible result aggregates and honest negative findings. Private SLDC source bytes should remain private unless their custodian's terms authorize distribution. A GitHub release and Zenodo DOI provide a citable version, **not external peer review** or an implicit licence to republish all inputs.

### 8.3 Do not call this a systematic review merely because it is long

[Tricco et al. (2018), PRISMA-ScR, DOI 10.7326/M18-0850](https://doi.org/10.7326/M18-0850) [P01] and [Page et al. (2021), PRISMA 2020, DOI 10.1136/bmj.n71](https://doi.org/10.1136/bmj.n71) [P02] specify reproducible searches, selection, flow reporting and methods disclosure for their respective review types. The current work is an **auditable, critical narrative/scoping-oriented review** with intentionally limited targeted searches and a 44-item curated matrix. It does *not* include an exhaustive duplicate search of subscription indexes, independent dual screening or a complete exclusion/retrieval flow. Calling it a 'systematic review of all Kerala electricity demand research' would therefore be false. The matrix and search protocol are building blocks for a later appropriately registered scoping review if needed.

---

## 9. Synthesis: where a genuinely original Kerala2040 article might remain

The evidence separates *known published propositions* from *questions we can actually test*. The most promising gap is **methodological comparability and temporal transfer**, not 'a new AI model for Kerala'. A paper with source-audited Kerala operating consumption may contribute if it establishes something scientifically generalizable about inconsistent energy-statistics boundaries, repeated test exposure, same-day weather associations or preprocessing-induced evaluation changes. It cannot assume those effects exist.

### 9.1 Candidate contributions and falsification conditions

| Candidate | Why worth testing | What would disconfirm novelty or effect | Evidence required | Priority |
|---|---|---|---|---|
| **C1: Grid-India vs SLDC observability crosswalk** | Same state, potentially distinct source conventions | Official definitions and matched original values prove identical meaning/behaviour with no meaningful effect; existing papers already cover same crosswalk | Original source manuals and date/field values from both; signed difference/coverage tables where truly comparable | **P0** |
| **C2: year-forward vs random-split evaluation** | Published Kerala weather ML uses historical random partitions; policy analysts may want temporal stability | Matched comparable model shows stable findings under chronology or novelty is already well documented elsewhere | Original-unit matched data, fixed baselines, researcher exposure ledger and appropriately qualified later years | **P0** |
| **C3: original-date completeness and revision influence** | Reporting coverage quality can alter apparent weather associations | No material source revision/selection effects and no new transferable QA method | Original bytes/hashes, revision choices, no-gap inclusion manifest, missingness-stratified sensitivity | **P0** |
| **C4: ERA5 spatial/time conversion sensitivity** | Five equal points and UTC/IST accumulated variables are nontrivial choices | Correct pipeline produces indistinguishable results to established population weighting; no new concept | Full source-hash verified multi-FY hourly weather and matched daily tests | P1 |
| **C5: observed hydro/import flexibility** | Could address actual operating robustness | Cannot source plant and interchange interval limits; no meaningful bounded result | Authentic interval load, real interchange, station/water constraints and validation | P2, after G3 |
| **C6: 2040 least-cost system development** | Relevant to policy | Overlaps CSTEP/CEA/WRI, source uncertainty overwhelms optimization and data insufficient | Independent costs, constraints, meteorology/demand and source-backed network; out of first manuscript | Defer |

### 9.2 Potential reframed titles (not promises)

**Paper A — methodological emphasis, conditional:**
- *Do reporting boundaries and evaluation design change weather–electricity-demand conclusions? A source-audited Kerala retrospective comparison.*
- *Original-unit versus transformed-state demand: provenance and temporal-transfer sensitivity in an Indian electricity-system case study.*

**Paper A0 — independent methods emphasis, conditional:**
- *What do India's state electricity reports measure? A reproducible Kerala source-boundary and data-quality audit.*
- *From daily SLDC reports to comparable research observations: revision provenance, missingness and energy-accounting tests.*

Neither title should be locked until source comparability, prior-art novelty and at least one genuine numerical result are established. A0 cannot be turned into a journal article simply by having a source ontology; independent transferability, error detection or a tested reconciliation method must survive the literature gate. If not, it should be an openly citable technical report, explicitly unreviewed.

### 9.3 A reasonable, non-inflated contribution statement

'We examine the reproducibility and comparability of daily electricity quantities reported for Kerala by operational and national sources, and assess the sensitivity of retrospective weather-associated demand models to original-unit definitions, source qualification and year-forward evaluation. The study makes no claim of day-ahead forecast accuracy, causal temperature effects, real interval shortages or hydropower operating capability.'

That paragraph is suitable for **an introduction draft**, not a conclusion. It describes a planned experiment whose outcome is unknown.

---

## 10. Research-design decisions that follow directly from the literature

**Decision L1 — stop algorithm-first development.** Existing direct competition already reports ERA5 + XGBoost + SHAP for Kerala. Do not spend 100 hours producing another tuned model until source fidelity and contribution survive the novelty test.

**Decision L2 — conduct a source-boundary benchmark before weather acquisition.** Seek the original publicly available national state corrected energy-met dataset and underlying Kerala SLDC qualified original daily field. Verify licence, date coverage, revisions, measurement scope and same-calendar eligibility. A genuine comparison requires byte-level authenticated input, not two numbers found on different websites.

**Decision L3 — preserve retrospective/forecast distinctions.** Same-day realized ERA5 permits a retrospective association backtest, not a deployed day-ahead forecast; observed-day SLDC daily consumption is not a measured hourly load shape.

**Decision L4 — freeze analysis choices with exposure disclosure.** Fix B0 seasonal/lag baseline, B1 calendar Ridge, B2 same Ridge + weather, exact dates, metrics, original-unit transforms and negative-result reporting, and append an exposure ledger for F1/F2/F3; do not describe exposed folds as blind.

**Decision L5 — make the QA methodology independently checkable.** The anticipated Paper A0 question must require a second route to reproduce source parsing and at least one genuinely nontrivial cross-source validity check. A sources inventory is not enough.

**Decision L6 — no unwarranted 2040 physical claims.** The 2024 CSTEP roadmap, 2025 CEA RA plan and September 2026 WRI analysis are already substantial comparators. The first paper should not claim a new 2040 optimum, shortfall/LOLE or unrestricted reservoir scheduling.

**Decision L7 — select the journal based on completed contribution.** Energy Informatics is a plausible energy-data and information-science audience; power systems outlets require more operational validation. Publication and access fees must not motivate inflated claims or false current KTH affiliation.

---

## 11. What is missing from this review before manuscript use?

This document is intentionally transparent about its limitations:

1. **Original public comparator files not admitted.** The 2025 Zenodo Kerala/weather and corrected raw national data are indexed and their access paths known; original CSV files, checksums and actual overlapping values have not been independently validated here.
2. **2026 IEEE full text not yet appraised.** Abstract-level claims only; no fabricated Kerala-specific implementation details.
3. **Full CSTEP/CEA technical appendices not critically re-read in this review.** Their public descriptions confirm prior planning scope, not exact comparability to Kerala2040 assumptions.
4. **Not 44 full-text papers.** The 44-row curated matrix includes publisher abstracts, methods excerpts, government reports, data products, documentation and references inherited from the reviewed charter. Many entries still require final author/venue metadata checks. It must not be cited as '44 articles systematically reviewed'.
5. **No quantitative meta-analysis.** Forecast errors across unmatched tasks cannot be pooled. No original model runs or Kerala numeric discrepancies are introduced here.
6. **Analyst-exposure history incomplete.** F3 is exposed; F1 and F2 may have influenced the historical modelling design and cannot be called independent unexamined test periods.
7. **Official reporting/legal definitions need custodian verification.** A mathematically equal MU unit is not proof of the same physical energy boundary.
8. **Review corpus requires additional targeted retrieval** of Indian regional demand, state interconnection and hydropower operations literature, especially inaccessible full technical documents.

The remedy is evidence acquisition, not overconfident prose. The [review protocol](REVIEW_PROTOCOL_AND_SEARCH_LOG.md) specifies source access, search expansion, note taking and claim audit. Future revisions should cite exact new paper sections and original record versions, retaining this as v0.1 history.

---

## 12. First publication milestone and stop rule

By **30 November 2026**, prepare a one-page novelty verdict with (a) exact published 2025/2026 competitor claims, (b) verified original Grid-India vs Kerala SLDC observable definitions and overlap, (c) an eligible year-forward evaluation protocol, and (d) an explicit source-rights decision. If the new observation yields no generalizable contribution beyond the existing 2025 paper, **do not force Paper A through a full year of source downloads**. Pivot to a carefully tested A0 methods contribution or publish an honest technical report.

The research programme's year-one resource constraint remains **400 planned focused hours**, not an unlimited scientific-literature harvesting project. This literature review is within WP0/WP5; expanded literature work must be balanced against independent source validation and manuscript preparation. The **26 October 2027 freeze** is a truthful record of achieved scientific evidence, not a guarantee that the journal editor has accepted the paper.

## Source register and reference usage

The primary curated sources are indexed in [EVIDENCE_MATRIX.csv](EVIDENCE_MATRIX.csv) under IDs D01–D06 (Indian empirical), F01–F06 (forecasting methods), V01–V04 (validation), W01–W04 (weather), M01–M09 (energy science), H01–H03 (hydro), P01–P03 (review methods), and O01–O09 (official and secondary context).

**Citation standard:** Use the original DOI/publisher for every study. Distinguish author's published findings, source-verified current Kerala2040 observations, planned analyses and methodological inference. The source matrix's access level is a research integrity control, not an endorsement or an invented quality score.

**Status of authorship:** AI-assisted working literature synthesis, requiring a human read-through of the directly cited papers, bibliographic audit and independent scholarly critique before incorporation in any formal journal article. Nothing in this document confers a present KTH affiliation, a manuscript submission, or permission to publish third-party raw data.
