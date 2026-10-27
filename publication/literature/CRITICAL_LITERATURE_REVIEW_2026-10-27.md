# Kerala2040 — critical literature review and publication-positioning synthesis
## Historical electricity data, weather-responsive daily consumption, validation, system flexibility and scholarly novelty

**Version:** 1.0 — 27 October 2026. **Research document, not submitted or peer reviewed; updated with two owner-supplied full PDFs on 27 October 2026.**  
**Study owner:** Independent Kerala2040 research. **Source baseline:** frozen 23 October 2026 Kerala2040 evidence.  
**Scope:** a *structured, critical, non-systematic narrative synthesis* of a **44-record curated source corpus**, supported by targeted inspection of publisher-hosted full text, university-held article text, published methods/code and authoritative official studies. For individual access levels see [EVIDENCE_MATRIX.csv](EVIDENCE_MATRIX.csv), [CLOSEST_STUDIES_CRITICAL_APPRAISALS.md](CLOSEST_STUDIES_CRITICAL_APPRAISALS.md) and [search protocol](REVIEW_PROTOCOL_AND_SEARCH_LOG.md). **Neither 44 full-text reviews nor PRISMA compliance is claimed.**

> **Review verdict:** a journal paper framed as “first Kerala weather-sensitive electricity-demand model using ERA5 / XGBoost / SHAP” would duplicate **Hunt & Bloomfield (2025)**, which published Kerala-specific results and code/data. Kerala2040 may still make an original contribution through independently reconciling **SLDC reported operational consumption** against distinct national data, publishing source-qualification and researcher-exposure protocols, and testing *strict later-year transfer of same-day-weather incremental value*. That contribution remains **conditional on original source access, a truly fair prior-art comparison, and scientific novelty demonstrated in actual results**. If the novelty gate fails, prefer a substantive reporting-boundary methods study (Paper A0) or citable technical report, not an unoriginal ML paper.

## Executive findings: confidence-qualified

| Decision area | Finding supported by literature | Confidence & boundary | Implication |
|---|---|---|---|
| Direct precedent | Hunt & Bloomfield (2025) already analyze **Kerala**, Indian state daily Grid-India demand, meteorological ERA5, XGBoost and SHAP and publish a Kerala score **R²=0.835** for their processed-target, random-split experiment | **High** for published article statements, code-path review; **not** independent numerical reproduction. This is *not* comparable directly with Kerala2040's one-year RMSE. | Reject first-use and arbitrary accuracy superiority claims; reproduce on matched dates/source scopes where possible. |
| Other Indian weather evidence | Harish, Singh & Tongia (2020) estimate heterogeneous temperature sensitivity using Delhi billing and 2009–13 India-wide 5-minute-load-derived daily series; Porwal et al. (2026) link 2023–25 Indian state daily reports with Open-Meteo | **High** for Harish verified owner-provided full PDF including Kerala Table A3, **abstract-level** for Porwal full methods | India-level temperature/weather impact is known; never claim first climate sensitivity study. |
| Evaluation design | Temporal forecasting validation depends on nonstationarity and the estimand; repeated held-out future periods are useful, but random CV is **not categorically invalid** for every autoregression | **High** for Cerqueira 2020 full PDF and published methods; Roberts 2017 reviewed at paper level in existing matrix | FY rolling-origin is worth testing for **future-year transfer**, but F1/F2 researcher exposure must be audited and FY2024–25 F3 is analysis-exposed. |
| Data definitions | Grid-India *energy met*, Kerala SLDC operational daily *consumption*, KSEBL-attributed annual consumer electricity use, scheduled/actual interstate drawal are different source fields not presumed equivalent | **High** for distinct reporting definitions; **unknown** whether numerical differences persist under rigorous reconciled same-day boundary | Treat differences as a falsifiable measurement question, never label one agency wrong without same-boundary evidence. |
| Weather provenance | ERA5 is modeled reanalysis; snapshot values and hourly accumulations have distinct validity times and units; UTC hour records do not automatically define physically integrated IST rainfall/solar totals | **High** for ECMWF primary product documentation and Cucchi et al. 2020 full public article | Hash raw Copernicus input; justify local-day temporal overlap/accumulation independently of successful 24-point timestamp count. |
| Power system | CSTEP (2024), CEA adequacy planning and WRI India (Sep 2026) already provide substantial Kerala future-energy pathways. Hydro scheduling literature documents physical hydrological coupling and limited real-world validation. | **High** for existing documents/summaries and 2026 hydro review; **not** independent replication of any Kerala scenario | No first-2040-roadmap claim; source-gate hydro, transfer limits, actual demand/dispatch before validating physical flexibility. |
| Publication readiness | A clear methodological gap exists *in principle*; whether Kerala2040 has a novel, publishable *empirical result* remains unresolved | **Provisional evaluative judgment**, not a verified journal acceptability statement | Test originality by end-November, actual source/data admission by March; no publication deadline drives forbidden claims. |

### Crucial quantitative noncomparability

The Hunt & Bloomfield (2025) article reports **Kerala XGBoost test R²=0.835** on a detrended/rescaled national Grid-India target evaluated with a reported random sampling design. Kerala2040's FY2024–25 public evidence concerns original-source-qualified **daily operational MU** on **353 observed day/ERA5 matches**, with earlier held-out monthly tests and published weather ablations. A table of 0.835 next to a Kerala2040 percentage RMSE gain would be *invalid*: outcomes, units/target transformation, temporal partition and sample windows differ. Likewise the **29,311.76 MU** Kerala State Planning Board FY2024–25 annual consumer-side statistic is not the sum of **30,666.2569 MU** for 354 SLDC reporting days within an operational definition; the scopes and day coverage differ. None of those figures measures an actual full-year hourly load curve.

---

## 1. Research context: what is already known versus untested

Kerala is an electricity system with material interstate dependence, flexible but hydrologically constrained generation, pronounced seasonal conditions and rapidly evolving demand. Existing *policy and modeling work* already addresses 2040 decarbonization, resource adequacy and renewable expansion. The scientific deficit limiting the Kerala2040 project is not a shortage of model packages; it is source-defined **observed operating data, authenticated high-resolution chronology, original meteorological inputs and physical constraint validation**.

The project's frozen 2026 public record supports (i) official same-definition annual demand trends, (ii) incomplete but original-source-tracked SLDC daily operational figures, (iii) dated reported installed-generation capacity and (iv) within-FY retrospective same-day weather association. It does **not** support measured 15-minute or 8,760-hour state load, loss-of-load probability, empirically demonstrated reasons for specific load shedding, reservoir-free water dispatch, network N-1 adequacy or a validated optimal 2040 investment mix. Literature must not be misused to remove these gaps: peer-reviewed studies from *elsewhere* cannot authenticate data missing from *this* study.

This review answers six questions: **(LRQ1)** published same-topic novelty threat; **(LRQ2)** source-boundary comparability; **(LRQ3)** validation/exposure and preprocessing bias; **(LRQ4)** ERA5 original hourly data semantics; **(LRQ5)** hydro/adequacy/transition precedent; **(LRQ6)** defensible primary-paper or fallback route. These are targeted synthesis questions, *not* hypotheses tested with original Kerala measurements in this review.

## 2. Direct prior studies: the strongest collision and what survives

### 2.1 Hunt & Bloomfield (2025): a formidable direct comparator

Hunt, K. M. R. & Bloomfield, H. C. (2025), *Building and explaining data-driven energy demand models for Indian states*, **Environmental Research: Energy** 2(2), 025003. [DOI 10.1088/2753-3751/adc7bc](https://doi.org/10.1088/2753-3751/adc7bc); [Newcastle full-publication record](https://eprints.ncl.ac.uk/305255); [public research code](https://github.com/kieranmrhunt/india-renewable); [public dataset concept record](https://doi.org/10.5281/zenodo.14983361); [specific archived dataset version](https://zenodo.org/records/14983362).

**Direct paper evidence:** state-by-state daily reported energy met from Grid-India/POSOCO; population-weighted weather with ERA5; thermal stress, temperature and humidity/dew-point variables; daily/weekly/monthly histories; calendar/holiday effects; XGBoost and explainability; nonlinear thresholds; reconstructed longer-run weather-conditioned demand and renewable residual comparisons. Appendix Table A1 includes Kerala full XGBoost **R² 0.835**, UTCI-only XGBoost **0.724**, full neural network **0.751**, and linear regression **0.680** under the published processed-target scheme. The paper itself discloses limitations of preprocessing and extrapolation.

**Public-code inspection recorded independently in** [prior-art memo](../../studies/paper-a-2027/HUNT_BLOOMFIELD_PRIOR_ART_REVIEW_2026-10-27.md): the generic fitting path uses \`train_test_split(..., random_state=123, test_size=0.2)\`, followed by another withheld partition on the remaining split; study notebooks use data transformations including detrending and variance treatment **before** their random sample partition. That combination is **not a demonstrated forward-year deployment test**. However, preprocessing before splitting does not *alone* establish a quantified leakage effect, and its scientific validity depends on whether the purpose is historical association or prospective forecasting. Only a faithful rerun could estimate bias caused by any full-sample transformation. No insinuation of research misconduct is justified.

**What is genuinely different in a potential Kerala2040 study?** Not Kerala as a region, ERA5, XGBoost, an accuracy score, or SHAP. Candidate differences are (a) *field-level* original Kerala SLDC accounting against national Grid-India original energy met, (b) strict later-year comparisons in actual MU/day without full-period outcome detrending, (c) original-source revision/missingness and timestamp/accumulation QA, and (d) properly audited researcher-level historical exposure. Each difference must materially alter what can be inferred; methodological bookkeeping alone does not guarantee a research journal article.

**Best immediate ROI:** inspect the authors' lawfully available \`Kerala.csv\` **and** their \`corrected_daily_energy_met_MU.csv\` together with original code, under official publication licence, before acquiring costly/weather data. The published notebook \`outputs/Kerala.csv\` uses transformed 'observed/predicted' units and is **not** the original reported MU/day. The live public dataset files and original private SLDC archive **have not been jointly source-hash verified** in this review. Published dataset filename dates (2014–24) and article PDF appendix starting 2013 are not reconciled by assumption. These ambiguities belong in the accession ledger.

### 2.2 Harish, Singh & Tongia (2020): a quantified Kerala state-temperature precedent

*Impact of temperature on electricity demand: Evidence from Delhi and Indian states*, **Energy Policy** 140, 111445; [DOI](https://doi.org/10.1016/j.enpol.2020.111445). **Updated 27 October 2026: the research owner supplied the full 14-page published PDF**, not merely a publisher preview; the exact Appendix A3 Kerala coefficients were inspected, as detailed in the [full-PDF appraisal](FULLTEXT_D02_D04_APPRAISAL_2026-10-27.md).

The study used NLDC/POSOCO **2009–2013 state-level five-minute metered load** converted to **daily mean MW**, paired with IMD 1° daily meteorology. Its Model 3 explains **log daily average load** with temperature bins relative to **21–24°C**, precipitation and monthly CEA deficit, plus an extensive set of time/state fixed effects. The original source measures **supply actually served**, which can be reduced by curtailment. That matters to both the scientific estimand and our original-source crosswalk.

**Direct historical Kerala regression result:** Appendix Table A3 (PDF **p. 12**), Kerala column 17: **1,737 dates**, model R² **0.892**, log coefficient **0.0211*** (SE **0.00340**) for **24–27°C** and **0.0694*** (SE **0.00510**) for **27–30°C**. Their exact exponentiated conditional differences are about **2.13%** and **7.19%** relative to 21–24°C. Higher Kerala-temperature bins are **blank in the published table**: this does not establish a zero effect or a valid extrapolation. Those are historical fitted associations for **2009–2013**, not contemporary or causally identified customer cooling demand.

The second part of the study analyses bills for **160,841 Delhi residential consumers**, finding substantial differences in responses for low-income and wealthier households. It cannot independently identify Kerala's customer technology or unmet-energy volumes from aggregate daily MU. **Scientific consequence:** Kerala2040 cannot claim that no published author estimated a Kerala-specific weather response. The genuinely distinct question, if any, is whether changes in **source definition, chronological testing and observation-qualification practices** meaningfully alter current retrospective interpretations. Historic NLDC **five-minute** records mentioned in this paper also warrant a separate legitimate archive enquiry, but the article does **not** authenticate their availability in 2026.

### 2.3 Porwal et al. (2026): overlapping source and weather correlation

*Granular Analysis of Weather-Influenced Electricity Demand in Indian States*, IEEE IC3ECSBHI, DOI [10.1109/IC3ECSBHI67834.2026.11468867](https://doi.org/10.1109/IC3ECSBHI67834.2026.11468867). The **publisher abstract** establishes daily Indian-state Grid-India Power Supply Position reports **April 2023–October 2025** paired with Open-Meteo weather and heterogeneity of state-level weather correlation. Its full paper methods, Kerala table and split decisions are **not verified**; do not allege omissions based solely on lack of abstract detail.

**Consequence:** a different meteorological archive, longer date range, or state-wise correlation map is not enough novelty. Acquire the paper lawfully before claiming a contrast in model, sampling or operational boundary.

### 2.4 Babu, Ramadesigan & Banerjee (2026): measured historical hourly data, synthetic future hourly profiles

*Medium and long-term electricity demand forecasting for India – Incorporating EV charging and space cooling impacts*, **Applied Energy** 420, 128069; [DOI](https://doi.org/10.1016/j.apenergy.2026.128069). **Updated 27 October 2026: owner-supplied full 18-page published PDF inspected, excluding separate supplementary materials.** See the [full-PDF critical appraisal](FULLTEXT_D02_D04_APPRAISAL_2026-10-27.md).

The study trains state-wise medium-term LSTMs using **Grid-India published daily series**, MERRA-2 weather, GDP and calendar information, then develops longer-term demand scenarios incorporating changing cooling and electric-vehicle charging. The key finding for *our data acquisition*, rather than a modeling first, is explicit on **PDF p. 4**: **Grid-India supplied actual state-level hourly demand data for 2021–2023**. Authors **selected 2023** as a **single reference set of observed hourly shapes**, normalized each daily profile and multiplied it by forecast daily energy to produce **future synthetic hour-by-hour demand curves**. These curves are **not observed future hourly load**, and the original 2021–23 source files have **not** been obtained by Kerala2040.

**Evaluation nuance (Table 4, PDF p. 7):** South regional MAPE is **0.6±0.1%** when the target FY2023 lies *inside* model training and **6.7±0.2%** when the period is excluded from model training. **This is the South regional result, not Kerala's state error**; individual Kerala errors appear in supplementary SM2/SM3 **not yet supplied**. The authors explicitly present both evaluation regimes and should not be accused of hiding their in-sample error. The report's preprocessing order could invite a leakage audit but is **not enough to assert that future information was used in training without checking code/appendix**.

For long-run scenarios, the study holds **2023 meteorology** in the normalized GDP demand baseline, adds cooling changes estimated via CMIP6-driven degree days and assumed AC ownership, and EV demand based on adoption pathways. The authors explicitly warn that **reusing one reference year's hourly shape**, GDP-proportional AC growth and building-sector extrapolation limit their projections (PDF pp. 16–17). Its 2070 demand outcomes are **conditional scenarios**, not Kerala's observed hourly 2040 demand or power-flow constraints.

**Consequence:** add **Grid-India** as an official historical data custodian for the **actual measured 2021–23 hourly series**, alongside Kerala SLDC and NLDC's older five-minute holdings. Do not equate a constructed hourly load curve with measurement or add Babu's model performance to a Kerala2040 same-target RMSE leaderboard. No credible “first Indian state future hourly profile” claim remains. The scientific merit of our actual original-source validation work is still **conditional**.

### 2.5 Household and cooling evidence: mechanism is not identified from a state regression

The 2022/2024 Indian dwelling and air-conditioning papers in matrix D05/D06 study small monitored dwelling samples and variation in cooling services, with drastically different units and selection. Alongside Harish et al., they demonstrate that *aggregate temperature–energy associations are composites of wealth, cooling adoption, industry, holidays and access constraints*. Ecological daily SHAP attributions cannot separately identify residential AC, causal adaptation, night peaks or unserved customers. **Keep them contextual and source-graded; do not transfer household coefficients to the Kerala SLDC statewide series.**

## 3. Inferential integrity: what is the question actually estimating?

### 3.1 The weather effect is a retrospective error contrast, not a causal effect

Let \(Y_d\) be a qualified, original-source daily SLDC operational-consumption observation for IST date \(d\). Let \(C_d\) contain calendar controls, \(W_d\) same-day verified ERA5-derived features, and \(T_f\) the set of identical qualified evaluation dates in later fiscal year \(f\). Fit the **same fixed Ridge** learning algorithm on *strictly earlier* training targets using calendar-only versus calendar+weather features. The registered signed outcome is

\[
 S_f = 100\,\frac{\mathrm{RMSE}(Y,\widehat{Y}_{C};T_f)-\mathrm{RMSE}(Y,\widehat{Y}_{C,W};T_f)}{\mathrm{RMSE}(Y,\widehat{Y}_{C};T_f)}.
\]

A positive \(S_f\) means a smaller retrospective error on **that observed test set**, not better predictions available at the day-ahead dispatch decision. Weather is historical *realized reanalysis*, not weather forecasts available ahead of the actual daily consumption. The estimated object is thus **incremental retrospective predictive association** given one chosen spatial aggregation and model family, not causal elasticity, outage risk or operational forward forecast skill. A negative outcome is publishable.

### 3.2 Three fiscal years do not equal three blind independent experiments

Existing F1 FY2022–23, F2 FY2023–24 and F3 FY2024–25 are **chronological test windows** *if and only if* actual training/normalisation is correctly separated. FY2024–25 was already studied, including model tuning and rolling months; classify it as **analysis-exposed**. F1 and F2 have uncertain prior researcher exposure because evolving Kerala2040 methodology and feature choices may have been influenced by later datasets. **Retrospective chronological cross-year assessment is honest; three prospectively locked, mutually independent confirmations is not.** Logged exposed model/design history and fixed protocol are mandatory.

The 2020 empirical validation paper by **Cerqueira, Torgo & Mozetič** (Machine Learning 109, 1997–2028; DOI [10.1007/s10994-020-05910-7](https://doi.org/10.1007/s10994-020-05910-7)) compares cross-validation, forward holdout and prequential methods across **174 real-world and 3 synthetic series**. It finds repeated held-out test periods more appropriate for examined *nonstationary* series, but blocked CV can be defensible in stationary cases. **Bergmeir, Hyndman & Koo (2018)** likewise warn against an over-simple “all random CV is wrong” rule for well-behaved autoregressive models. The correct Kerala2040 justification is the intended **generalization to later fiscal years under trend/regime change**, not a rhetorical claim that every random fit in Hunt & Bloomfield must be invalid.

**Roberts et al. (2017)** motivate explicit spatiotemporal dependence and structured validation. A forward-date training fence handles model-fitting temporal leakage, but *not* analyst peek, full-sample detrending, optimization against exposed years or sample selection after observing scores.

### 3.3 Fixed model and preprocessing are part of the scientific treatment

A 2026 *Energy Conversion and Management: X* open-access article [DOI 10.1016/j.ecmx.2026.101791](https://doi.org/10.1016/j.ecmx.2026.101791) fixes a small GRU learner and varies temporal preprocessing under rolling origin across two **hourly non-Kerala datasets**. It reports nonuniform sensitivity to scaling, anomaly handling and lookback windows. This **does not validate Kerala2040's actual daily models** and is not evidence of quantified Hunt/Bloomfield leakage; it supports **holding the learner fixed** while testing a change in information provided, fitting scalers inside each training fold, and publishing preprocessing decisions.

**Hyndman & Koehler (2006)** support careful scale-sensitive errors and train-only scaled denominators. Paper A should show **per-year RMSE and MAE in MU/day, same days for both arms, signed percentage RMSE skill**, coverage, dependence and all negative years. Do not compare unaligned R² with other authors' transformed-target scores. Predefined seasonal naive baselines must use observed historic lags, not fictional values in unavailable days.

### 3.4 What statistical uncertainty can say

Daily residuals are autocorrelated and error distribution may vary seasonally. Simple independent-daily-row normal intervals or a neat “three-year statistically significant” p-value overstate information. Show all annual effects, their spread, autocorrelation diagnostics and conditional block-bootstrap sensitivity *only if* the block length and dependency assumptions are justified and documented in advance. Source missingness concentrated in storm/high-demand periods can itself bias aggregate accuracy. A more sophisticated model can be a **secondary** result, but cannot replace the registered fixed Ridge contrast after inspecting a negative primary result.

## 4. Observations, data rights and the A0 contribution

### 4.1 An auditable measurement ontology

A rigorous comparison needs six explicitly named constructs:

| Construct | Expected observation unit and what it is *not* | Current admissible role |
|---|---|---|
| Kerala SLDC daily operational \`consumption\` | Publisher-reported MU/day and document date, qualified by original-day energy-balance checks; **not** 15-minute demand | Primary **Paper A** target and **A0** source series |
| Grid-India PSP daily \`energy met\` | National published energy supply/met MU/day; exact metering/geographic boundary, source date and revision must be checked | External comparator **only after original record crosswalk** |
| Annual KSEBL-attributed consumer-use series | State Planning Board annual consumer-side MU per FY | Separate trend/context; **not** a plug-in replacement for daily SLDC totals |
| Actual interstate drawal/exchange | Metered interval series with sign convention and accounting-period boundaries | Needed for actual import/operational energy balance; **not** a synonym for schedule |
| Scheduled interstate drawal | Commitment/schedule, not realised interchange | Planning/accounting comparator, not a measured actual flow |
| State hourly/15-minute load met | Source measured MW point/interval with explicit boundary and missingness | **Not admitted** in current Kerala2040 freeze; cannot imply outages, peaks or LOLE |

The existing private \`kerala2040-source-archive\` is documented as **2,606 dated source days** across 2019–26, a source count not guaranteed to equal qualified daily observations. FY2024–25 public coverage is **354/365** original daily reports with **11 unavailable**, not a complete year. Yearly public consumer statistics and SLDC daily observed totals differ in source definition; do not force equality or derive unexplained “losses” from their subtraction. In A0, the novel scientific object, if any, would be a **replicable definition/provenance method** with clearly typed fields, source-version qualification, missingness categories and independent same-boundary validation, not just a count of reports.

### 4.2 Why this could matter beyond Kerala — and why it might not

The proposed A0 method would mark original publisher, exact field semantics, time period, spatial boundary, official revision, unit, primary-source hash, access rights, quality status and whether cross-source operations are *permitted*. A testable improvement is: *when two public quantities look numerically conflicting, does applying this ontology consistently recover genuine same-boundary comparators and reject unsupported arithmetic, with objectively lower extraction/definition error?*

**This is a design hypothesis, not an observed improvement.** Data provenance, ontologies and source quality frameworks are well-established elsewhere; a regional glossary without independent tests is probably **technical-report level**. Require (1) explicit novelty against energy-data interoperability studies, (2) reproducible multi-year evidence, (3) second-method or actual external checks, (4) cross-provider comparators and (5) rights-aware reporting. If these fail, **do not submit A0 as a research article by default**.

### 4.3 Independent benchmarking must preserve original units and coverage

Hunt & Bloomfield provide an open benchmark with source data/corrected national daily series. Downloading their dataset, verifying publisher hashes, and matching *true MU/day* to separately source-verified SLDC *true MU/day* may establish whether the constructs are comparable and on which dates. Do not numerically join code outputs with transformed targets whose \`observed\` column is near 10 or infer official data error from a different boundary. If no common definition exists, **“not comparable” is a result about information architecture**, not a fabricated numerical ratio.

**Data governance:** provider-accessible original PDFs are not automatically freely redistributable by third parties. The project can release code, source metadata and permissible aggregates while keeping original SLDC rows privately gated until custodian terms permit more. Full independent replication may be partly access-limited; disclose exactly what independent reviewers can inspect, and choose publication venue accordingly.

## 5. ERA5: meteorology is not just a timestamp join

**Hersbach et al. (2020)** establishes ERA5 as a global reanalysis, which is model-derived and observationally constrained rather than a set of local surface-station measurements. **Cucchi et al. (2020)** describe WFDE5, an independently constructed hourly bias-adjusted ERA5-driven product. Their [open article](https://essd.copernicus.org/articles/12/2097/2020/) explicitly identifies atmospheric field validity time and states that for accumulated fields the validity hour is generally the **end of the interval**. ECMWF's [ERA5 time/step documentation](https://confluence.ecmwf.int/pages/viewpage.action?pageId=111150967) distinguishes instantaneous analysis, accumulated forecast quantities and mean rates.

**Kerala2040's fixed five points** (Thiruvananthapuram, Kochi, Palakkad, Kozhikode, Kannur) have equal weights. This is a screening geographic representation, **not** population weighted weather, demand-weighted weather or a statewide measured atmosphere. Hunt & Bloomfield's population-weighted approach is at least as defensible *in principle* and must be used as a meaningful comparator when source access permits. Spatio-temporal sensitivity may be a secondary article contribution only if evidence and results justify it.

**Critical integration detail:** 00:00 UTC occurs at 05:30 IST; an hourly ERA5 *instantaneous value* at 00:00 UTC describes a time point, while total precipitation/shortwave accumulated up to 00:00 UTC covers a preceding window. Simple \`.tz_convert('Asia/Kolkata').groupby(date).sum()\` is **not automatically a physically aligned IST midnight-to-midnight energy/rainfall integration**. For half-hour boundaries, explicitly prorate or obtain an independently justified exact hourly-period method; verify totals against native UTC monthly accumulations and independent daily ERA5 statistics as a check where product definitions match. **A 24-timestamp-per-point validation check is necessary but insufficient** for accumulated quantities.

### Original-source weather admission gates

1. Original Copernicus artefact and extraction manifest with date, variable, original resolution, request geometry, licence and SHA-256.
2. Original NetCDF/GRIB member inspection: dimensions, grid selection (including anomalous multi-cell responses), units, time bounds, accumulating-variable support, full initial/final day context.
3. Qualified **24 hourly instant records × five declared locations per observed IST day**, duplicates and missing hours rejected without four-point averaging.
4. Independent conservation/integration checks for precipitation and radiation plus source-version stability and geographic sensitivity.
5. Explicit statement **ERA5 reanalysis same day ≠ operational day-ahead meteorological forecast**.

If these original data do not exist for required fiscal years by **31 March 2027**, the Paper A multiyear inference gate **fails** regardless of normalized-Parquet completeness or passing synthetic CI.

## 6. Hydro flexibility, electricity imports and 2040 strategy — what literature cannot validate for us

### 6.1 Existing Kerala transition and adequacy evidence

- **CSTEP (2024)** *Kerala Energy Transition Roadmap 2040* addresses renewable targets, indigenous generation, power imports and scenario constraints. Its [official summary](https://cstep.in/publication/kerala-energy-transition-roadmap-2040/) states internal generation meets approximately **30–35%** of electricity requirements in the study baseline. This is *their assumption/boundary*, not a newly independently verified Kerala2040 number.
- **CEA Kerala resource adequacy plan** (official [resource adequacy documents](https://cea.nic.in/resource_adequacy_st/report-on-resource-adequacy-plan-for-kerala-up-to-2035-36/)) tackles future adequacy, demand/resource profiles and planning scenarios. Underlying hourly planning inputs **do not become observed interval load** merely because CEA used them.
- **WRI India (29 September 2026)** *Pathways for Kerala's Clean Energy Transition* studies 2040 pathways and external procurement. The [official brief](https://wri-india.org/research/pathways-keralas-clean-energy-transition) reports roughly **70% imports** under its boundary and a demanding exploratory zero-thermal pathway; quote any MW target only with exact model basis and qualifications. These are **institutional/policy models**, not peer-reviewed operational validations.

**Gap remaining:** differences between planning assumptions and authenticated operating observations, especially real intra-day interchange/load chronology, hydro/storage constraints and actual transfer capability. Historical diagnosis must precede speculative capacity sizing.

### 6.2 Hydrological coupling has well-known hard constraints

The 2026 [short-term hydropower regulation systematic review](https://doi.org/10.1016/j.rser.2026.116940) surveys **106 studies** and identifies infrequent strong two-way hydrology/electricity-system coupling and scarce real-world validation. A 2025 published paper on hydropower flexibility also stresses non-power water uses/network bottlenecks (see H02 in the matrix; only abstract-level details verified).

For Idukki or downstream cascade redispatch, **installed MW is not usable hour-by-hour energy**. Need source-stated reservoir usable storage and water-energy conversion, inflow chronology, operating head, ramp/unit limits, spill, irrigation/environmental releases, cascade routing, availability and actual dispatch/interchange observations. Optimistic energy-preserving rescheduling is at most a **bracket**, not a physically validated hydro response. Official ATC/nameplate figures cannot establish contemporaneous safe N-1 transfer.

### 6.3 Implication for year-one research allocation

A second paper on hydro/import flexibility is not protected at 10 hours/week: it is a **source-gated future output**, especially if KSEBL interval-data outreach fails. WP3 documents true/unknown/upper-bound cases and stops by June; WP4 may be zero. Do not split the manuscript effort between three unrelated technologies to manufacture a “Kerala 2040” omnibus novelty claim.

## 7. Review-method transparency and evidence map

The branch's [matrix](EVIDENCE_MATRIX.csv) holds **44 selected records** (32 presently classified as peer-reviewed research/review/software/conference, and 12 other government, provider or methodological records; *per-curated-corpus classification, not a population statistic*). Full texts are **not** available for all 44. Explicit categories: direct-demand precedents D; forecasting reviews F; statistical validation V; weather W; energy/hydro methods M/H; review-method guides P; official/other O. We rely on journal articles for scholarly contributions, official agencies for **their published policies/measurement definitions**, software for implementable methodology, and private Kerala source bytes **only after actual verification**.

**What this review is:** a structured narrative critical synthesis with explicit research question, curator-built evidence matrix, per-record access level, nearest-study table, sources, key methodological contradictions and a falsifiable novelty decision. **What it is not:** exhaustive PRISMA systematic/scoping review, dual independent screening, comprehensive bibliometric map, meta-analysis, or an independently run replication of the competing 2025 model. Missing search hit counts, access-denied full papers and lack of independent duplicate screening **cannot be filled by invention**. A future systematic review would require a genuinely reproducible database export/deduplication/exclusion register before adopting PRISMA-ScR reporting standards (Tricco et al. 2018; Page et al. 2021).

The [critical appraisals](CLOSEST_STUDIES_CRITICAL_APPRAISALS.md) document the twenty closest sources and differentiate paper full-text, abstracts and source repositories. Numeric claims are attributed to authors under their own estimands and evaluation, not transferred into Kerala2040.

## 8. Competing-paper assessment: novelty adjudication

| Proposed contribution | Already covered? | Proof required before claiming | Current verdict |
|---|---|---|---|
| First Indian/ Kerala weather-demand ML with ERA5, XGBoost, SHAP | **Yes: Hunt/Bloomfield 2025** | None: claim directly contradicted | **REJECT** |
| First Indian-state temperature–demand relation | **Yes: Harish et al. 2020 and others** | None | **REJECT** |
| A higher predictive RMSE/R² score than Hunt & Bloomfield | Published targets, transforms, metrics and splits are different | Refit both models on exact same original target/dates/features where legitimate | **NOT ESTABLISHED** |
| Verified *SLDC vs Grid-India* fiscal-year source-boundary crosswalk | Not established by existing sources in our corpus as done to this original-source depth | Retrieve both actual original data, definitions and matched date records, verify SHA and missingness | **PROMISING, NOT PROVEN** |
| Strict year-forward weather-added fixed-learner retrospective MU/day comparison | Differentiates Hunt & Bloomfield's main random-split reported evaluation | Authentic multiyear ERA5 and SLDC, exposure ledger, matched baseline, report every sign/negative period | **PROMISING, BLOCKED** |
| Spatial representativeness superiority of five-point ERA5 | Hunt's population-weighted ERA5 already strong comparator | Actual comparison with native source, weights, sensitivity and meaningful result | **UNPROVEN; NO CLAIM** |
| Reusable energy-source ontology/QA and quantified miscomparability | Other provenance methodologies exist; this corpus lacks a precise Kerala equivalent so far | Independent source-boundary audit, transferability check, prior methods comparator and genuinely nontrivial discrepancies | **POTENTIAL A0; NOVELTY UNKNOWN** |
| Real hydro/import flexibility and operational reliability result | System-method literature and prior Kerala scenarios exist, but actual constraints unavailable | Authentic interval load/exchange and reservoir/plant physical operation | **NOT ADMISSIBLE NOW** |
| First Kerala 2040 roadmap / least-cost mix | **CSTEP 2024, CEA planning, WRI 2026** already supply existing pathways | N/A | **REJECT** |

### Conditional contribution sentence for a future manuscript

> We examine whether independently source-qualified Kerala SLDC daily operational consumption, rather than a national Grid-India reported energy-met product, exhibits stable added retrospective explanatory value from same-day reanalysis weather when matched calendar models are evaluated in successive fiscal years. By maintaining source-vintage, measurement-boundary and researcher-exposure audits, the analysis tests how data definitions and temporal evaluation affect the interpretation of previously reported Kerala weather-demand relationships.

**This is a proposed contribution**, to be kept in draft until the source equivalence crosswalk and year-forward tests actually produce scientifically meaningful evidence. It should not be used as an accepted published abstract today.

## 9. Paper A versus A0 decision framework

**Stage N0: immediate (27 October–30 November 2026).** Read Hunt & Bloomfield's full public material/code, ingest their published *actual-MU* reference dataset with hash and licence, acquire/verify rights to private SLDC originals, document field and date comparability, and write **one falsifiable novelty contrast**. Do not spend 80 more ERA5 request-windows before answering whether a cheaper public reference solves the question.

**Stage N1: by 31 January 2027.** Freeze or amend a prospective *additional analysis* protocol (not a retroactive preregistration of already seen periods); produce a 25–35 carefully selected reference matrix with at least 15 close study text appraisals, and a two-page Paper A0 methods prospectus/QA tables. Request actual outside reviewer feedback; no implied endorsement.

**Stage G2: 31 March 2027.** If original five-point multiyear ERA5 weather plus qualified private SLDC target source chain are authenticated and analytical novelty persists, execute fixed Ridge B1/B2 and retained negative outcomes. Otherwise pivot to source ontology/missingness A0 if and only if novel and independently checkable, else citable reproducible technical report. A no-go is not rescued by unseen ML hyperparameters.

**Stage manuscript: 30 June–31 August 2027.** At most one primary scientific paper; freeze results by June, manuscript v1 by August. Study limitation must acknowledge earlier exposed FY2024–25 and possible F1/F2 research design influence, with no hollow “three independent confirmatory years” language. Signed results, data rights and independent numerical checks required.

**Stage submission: Sep–Oct 2027.** Review at least 15 near-journal articles under current official journal scope, file a candid disclosure/access statement, secure a no-APC/waiver/funding route and human critical review attempt. October 26 release may be a rigorous report if data or article novelty fail. *Acceptance is outside the schedule's control*.

### Falsifiable outcome ladder

1. **If original targets prove semantically non-comparable:** publish the precise ontology + incompatible-boundary methodology only if independently validated and scholarly novel; no fake correlation or arithmetic deficit.
2. **If targets comparable and weather adds stable value across year-forward tests:** report per-FY signed gains with all exposed-fold caveats and sensitivity.
3. **If weather effect reverses or vanishes:** report robust failure and explain what source/validation choices change, without spin.
4. **If original ERA5 cannot be admitted:** no new weather performance claim; a grounded data-source quality study or properly identified technical report remains.
5. **If neither scientific contribution passes prior art:** explicitly declare manuscript not journal-ready, preserve the versioned evidence and move the next research question to new actual operational data.

## 10. Research implications for upcoming modelling and writing

- **Change original novelty title:** avoid “first weather-sensitive Kerala model.” Working title is *Measurement boundaries and retrospective year-forward weather sensitivity in Kerala's operational daily electricity reporting* (only if empirically supported).
- **Retain strong equal-model baseline:** fixed Ridge calendar-only versus fixed Ridge + weather on exactly same dates; complex ML post hoc only when warranted.
- **Make prior work an integral comparison:** replicate Hunt/Bloomfield's published Kerala target/data first, then evaluate a *new* source-equivalent subset if possible. Distinguish one model's original publication target/split from our own.
- **Write explicit causal and operational exclusions:** no observed day-ahead accuracy, plant hydro opportunity, state load shedding, AC ownership or causal socioeconomic sensitivity from current daily data.
- **Audit missingness and atmospheric support:** 11 missing original 2024–25 daily reports; hash, revisions, IST midnight, accumulated variables; no estimated days represented as measured.
- **Source rights and external validity:** store restricted originals privately; a clear independent rerun path may require controlled custodian permissions and data availability disclosure.
- **Use WP5 efficiently:** write the Introduction, data dictionary and methods as soon as actual fields are understood. Do not manufacture “results” to meet a calendar.
- **Ask one real scientific question at a time:** demand-weather is Paper A; hydro/grid adequacy are longer-run opportunities contingent on actual hourly and water operating data.

## 11. Source anchors and verification notes

**Direct scholarly comparators**

- [Hunt & Bloomfield (2025), Environmental Research: Energy, DOI 10.1088/2753-3751/adc7bc](https://doi.org/10.1088/2753-3751/adc7bc); [Newcastle university article record](https://eprints.ncl.ac.uk/305255); [public code](https://github.com/kieranmrhunt/india-renewable); [Zenodo data](https://doi.org/10.5281/zenodo.14983361). Exact Kerala scores drawn from available published article appendix/table rendering, not independent reproduction.
- [Harish, Singh & Tongia (2020), Energy Policy, DOI 10.1016/j.enpol.2020.111445](https://doi.org/10.1016/j.enpol.2020.111445) — publisher full article sections concerning 2009–13 national series, household sample, treatment and interpretation.
- [Porwal et al. (2026), IEEE IC3ECSBHI, DOI 10.1109/IC3ECSBHI67834.2026.11468867](https://doi.org/10.1109/IC3ECSBHI67834.2026.11468867) — *abstract only*, full methodology unresolved.
- [Babu, Ramadesigan & Banerjee (2026), Applied Energy, DOI 10.1016/j.apenergy.2026.128069](https://doi.org/10.1016/j.apenergy.2026.128069) — *publisher abstract/highlights*, not full paper.

**Statistical, meteorological and energy methods**

- [Cerqueira, Torgo & Mozetič (2020), Machine Learning, 10.1007/s10994-020-05910-7](https://doi.org/10.1007/s10994-020-05910-7) — full publicly accessible **32-page manuscript PDF** reviewed for abstract/design/approach.
- [Roberts et al. (2017), Ecography, 10.1111/ecog.02881](https://doi.org/10.1111/ecog.02881).
- [Bergmeir, Hyndman & Koo (2018), Computational Statistics & Data Analysis, 10.1016/j.csda.2017.11.003](https://doi.org/10.1016/j.csda.2017.11.003).
- [Hyndman & Koehler (2006), International Journal of Forecasting, 10.1016/j.ijforecast.2006.03.001](https://doi.org/10.1016/j.ijforecast.2006.03.001).
- [Leakage-aware benchmarking (2026), Energy Conversion and Management: X, 10.1016/j.ecmx.2026.101791](https://doi.org/10.1016/j.ecmx.2026.101791) — open publisher full text; different target/horizons from Kerala.
- [Hersbach et al. (2020), QJRMS, 10.1002/qj.3803](https://doi.org/10.1002/qj.3803).
- [Cucchi et al. (2020), Earth System Science Data, 10.5194/essd-12-2097-2020](https://essd.copernicus.org/articles/12/2097/2020/) — open full publisher article; UTC validity, accumulation and bias adjustment.
- [ECMWF ERA5 time/step terminology](https://confluence.ecmwf.int/pages/viewpage.action?pageId=111150967) — authoritative vendor documentation, not peer-reviewed standalone research.
- [Hydro scheduling systematic review (2026), RSER, 10.1016/j.rser.2026.116940](https://doi.org/10.1016/j.rser.2026.116940) — open publisher article/abstract, 106-study evidence base.
- [Pfenninger, Hawkes & Keirstead (2014), RSER](https://doi.org/10.1016/j.rser.2014.02.003); [DeCarolis et al. (2017), Applied Energy](https://doi.org/10.1016/j.apenergy.2017.03.001); [Pfenninger et al. (2017), Energy Policy](https://doi.org/10.1016/j.enpol.2016.11.046).

**Institutional and source references (not peer-reviewed novelty evidence)**

- [Kerala State Planning Board Economic Review 2025](https://spb.kerala.gov.in/sites/default/files/2026-01/ER%202025%20Volume1%20Eng%20final.pdf); [Kerala SLDC archive](https://sldckerala.com/index.php?id=1).
- [CSTEP Kerala Energy Transition Roadmap 2040 (2024)](https://cstep.in/publication/kerala-energy-transition-roadmap-2040/); [CEA Kerala resource adequacy plan](https://cea.nic.in/resource_adequacy_st/report-on-resource-adequacy-plan-for-kerala-up-to-2035-36/); [WRI India Kerala pathways (29 Sep 2026)](https://wri-india.org/research/pathways-keralas-clean-energy-transition).
- [PRISMA scoping extension — Tricco et al. (2018)](https://doi.org/10.7326/M18-0850); [PRISMA 2020 — Page et al.](https://doi.org/10.1136/bmj.n71): **reporting standards** only; this branch does *not* claim compliance.

**Evidence custody note:** References, access grades and distinctions come from publisher abstracts, selectively available complete articles, official university repositories, public code and existing public Kerala2040 source-gate records. No private SLDC input was exposed or independently revalidated and no cross-source new Kerala quantitative comparison was performed in creating this review. Dates and source states apply to **27 October 2026** only.

---

### Editorial recommendation

**Do not currently promise an Energy Informatics journal paper based on a headline weather-model improvement.** First execute the Hunt/Bloomfield *original-unit data accession + source-boundary comparison* as a bounded November novelty gate. If it yields a reproducible, nontrivial distinction and sufficient independently admissible meteorology, Paper A can become a narrow research article on **source definition and year-forward stability**. If not, develop A0 rigorously and accept a technical report if needed.

**The literature review itself is ready as a complete structured critical *narrative synthesis* with transparent evidence limits. The proposed experimental Paper A and A0 remain unvalidated and cannot be called publication-ready research findings.**
