# Kerala2040 — 18-source / 485-page original-PDF visual review

**Version 1, 27 October 2026.** User supplied **18 complete source PDFs** (two Kerala 2040 institutional reports + 16 journal articles/author manuscripts). Every **one of the 485 original pages** was screenshot-rendered and checked sequentially in four-page visual contact sheets. Pages with central maps, charts, model equations and numeric tables were checked again individually at higher resolution. Original screenshots and full third-party PDFs remain **private** and **are not redistributed through this public repository**. The independent 18-page analytic PDF report and 485-row visual coverage inventory were delivered to the research owner outside the repository.

**Methods boundary:** image-based page/figure/appendix review, not mere extracted-text citation harvesting. This is a **critical narrative** source appraisal, *not* PRISMA, author-code replication, a newly acquired electricity meter time series, a quantitative meta-analysis, or external peer review. Source file page numbers below are **PDF 1-indexed** (may differ from journal folio). The paper/code conclusions are those of their authors, not novel Kerala2040 measurements.

## New scientific findings requiring action

### 1. Actual high-resolution electricity data **exist in past investigators' source records** but are not yet in Kerala2040

| Document | Direct figure/text witness | What was actually observed | What authors subsequently constructed | Required data inquiry |
|---|---|---|---|---|
| **P17 Harish, Singh, Tongia (2020)** | PDF p2, study data; p12 Table A3 | NLDC/POSOCO 2009–13 **five-minute state metered load in MW**, aggregated by the authors into **daily mean MW** | Statewise conditional temperature–load regression; not a new original Kerala SLDC interval series | Ask Grid-India/NLDC custodian if source/field definitions and historical digital blocks can be obtained |
| **P02 CSTEP (2024)** | **PDF p33, section 4.2.3, Fig. 12** | Original Kerala **FY2016 15-minute blockwise demand data** referred to explicitly in narrative | **Extrapolated FY2022** 15-min time profile **labelled FY22 in Fig. 12**, then shape projected to FY2030/40 | Ask CSTEP, Kerala Energy Management Centre/utility for the **FY2016 original source**, calendar/block/clock fields, actual revisions and reuse terms |
| **P16 Babu et al. (2026)** | PDF pp4–5 source paragraph; p7 Table 4 | Original Grid-India **state-level hourly electricity demand 2021–23** obtained by authors, using **observed 2023 shapes** | Synthetic future hourly profiles obtained by rescaling the 2023 shapes by modeled daily demand | Request original state-level observed hourly series and exact years/IST boundaries from Grid-India or authors |

**Crucial:** no such five-minute, 15-minute or hourly original source file has been received in the Kerala2040 project as a result of reading these PDFs. A source being cited as available to *another researcher* does not mean it is open access or distributable. In Babu, year names often follow financial-year convention—ask for exact first/last observed timestamps. Future hourly curves based on a historical daily template are **not observed future demand**.

### 2. Kerala temperature response and Kerala weather-driven ML are already published

- **P17 Harish (2020), PDF p12, Kerala column Appendix Table A3:** n=**1,737**, model R² **0.892**; log-demand bin coefficients **0.0211** for 24–27°C and **0.0694** for 27–30°C vs **21–24°C**. Fitted multiplicative contrasts ≈**2.13%** and **7.19%**. These are **2009–13 observational conditional effects on observed restricted load met**, not proof of causal current household cooling elasticity. Blank hotter bins are not estimated zeroes.
- **P18 Hunt & Bloomfield (2025), PDF p25 Table A1, p13 Kerala example, pp21–23 data appendix:** Kerala XGBoost **R² 0.835**, applied to processed/detrended Grid-India daily met energy and random evaluation partition. Their impressive historical conditional score **cannot be compared to original MU/day later-FY errors** without the original dates, transformation/units, source and same-target benchmark.
- **P16 Babu (2026), PDF p7 Table 4:** South regional (not Kerala) MAPE **0.6±0.1% seen/trained period** versus **6.7±0.2% held-later/unseen period**. The authors explicitly distinguish regimes; their absent supplementary state tables (SM2/SM3) must not be fabricated.

**Novelty verdict:** “first Kerala temperature response,” “first Kerala ERA5/XGBoost/SHAP” and “first original hourly curve projection for Indian states” are invalid as novelty claims. Source-boundary authentication and transparent later-year testing are plausible **conditional** differentiators, not yet validated contributions. **Porwal 2026 IEEE complete paper absent**.

### 3. Two Kerala 2040 scenarios cannot be compared as if the same measured target

- **P01 WRI India (2026), PDF p3:** BAU electricity demand **56,057 MU in 2040**, policy pathways with thermal PPA and import assumptions; the report emphasizes 60% of FY2024–25 consumption sourced from out-of-state thermal stations and nearly 70% imports—different denominators.
- **P02 CSTEP (2024), PDF pp7,23–24:** FY2040 end-use BAU trend **40,446 MU**, plus scenario EV/induction and losses yielding **45,519 MU** final requirement, and modeled peak **7,594 MW**. These are **forecasts**, not authentic FY2040 readings.

Arithmetic difference **56,057 − 45,519 = 10,538 MU** (≈23% of CSTEP downstream total); this is **not a scientific disagreement** until base year, growth, consumer vs transmission boundary, imports, missing sectors, fiscal definition and scenario drivers are matched.

### 4. CSTEP storage dimension/semantics gate

**P02 CSTEP PDF p35 Fig. 14** labels FY2040 **3.8 GW / 7,163 GWh** (BAU) and **4.1 GW / 8,108 GWh** (high RE). If *both* GWh and GW are simultaneous installed energy and discharge-power nameplate ratings, ratios imply **~1,885 and ~1,977 hours** of discharge. That is unusual and should **not** be interpreted as battery duration or storage installed energy without clarifying the source's 8,760-hour surplus/deficit time-modeling: could mean annual cumulative energy shifted/deficit or a seasonal netting metric. This is a **definition clarification, NOT a verified model error**. Ask for original power/energy decision variables, SOC constraints, losses and chronological balance; exclude nuclear deployment claims from Kerala2040's study scope.

### 5. Validation and ERA5 assumptions — actual figure-method review

- **P15 Roberts (2017), PDF p54 Fig. 2, pp24–29:** blocked spatial/temporal CV addresses dependence and extrapolation target. Does not prescribe a universal Kerala temporal block size.
- **P14 Cerqueira/Torgo/Mozetič (2020), PDF pp4–5 Figs 1–4 and pp14–22:** repeated chronological holdouts are particularly useful for nonstationary data; stationary cases have different CV properties.
- **P13 Bergmeir/Hyndman/Koo (2018 preprint), PDF p4 Fig. 1 and pp14–15:** conventional K-fold can be legitimate for *stationary purely autoregressive models with uncorrelated errors*. Reject the blanket “random CV universally invalid” assertion. **Our task** is previous-fiscal-year to future-fiscal-year performance; chronological splits fit that specific target, but original researcher exposure must be disclosed.
- **P10 Sesay (2026), PDF pp5–13:** controlled TinyGRU, H=1/6/24 hourly horizons, rolling origins, preprocessing ablations, missing-block/corruption tests. Transfer **methodological QA**, not raw hourly error magnitudes, to Kerala retrospective daily Ridge.
- **P12 Hyndman/Koehler (2006 author manuscript), PDF pp4–5,11–12:** MAE/RMSE in original MU/day, optionally **MASE train-only denominator**. Never compare transformed-target R² with observed MU/day RMSE directly.
- **P11 Hersbach et al. (2020), 90-page accepted manuscript, Figs across pp75–90:** ERA5 hourly 31 km observation-assimilated reanalysis, not direct weather station observations or issued operational weather forecast. UTC→IST calendar-day integration, instantaneous versus accumulation-ending intervals and 5-point weighting must be made physically accurate before claims.

### 6. Source-specific supporting appraisals

| Source | Key visual witness and implication |
|---|---|
| **P03 Pfenninger, Hawkes, Keirstead (2014)** | pp2–6 energy system optimization/simulation/power market taxonomy and resolution/uncertainty/human complexity; choose model appropriate to admitted input resolution |
| **P04 Vatanchi et al. (2026)** | pp3–11 systematic selection and water↔power coupling categories for 106 studies; operational validation is limited; don't assert Idukki dispatch flexibility without inflow, head, reservoir and flow constraints |
| **P05 Yue et al. (2018)** | pp2–12 uncertainty classification: Monte Carlo, stochastic optimization, robust optimization, model-generated alternatives; every bound needs an evidence source |
| **P06 Pfenninger et al. (2018)** | Fig. 1 p2 open data/code/model interrelationships and legal rights; open analysis **does not** license private original meter data redistribution |
| **P07 Pfenninger et al. (2017)** | pp1–5 open-science case and privacy/security/data-access qualification; peer review ≠ input-byte QA |
| **P08 DeCarolis et al. (2017)** | pp3–13 question/scope/features/sensitivity/communication method chain; no sophisticated optimisation without inputs and falsifiable estimand |
| **P09 Kuster et al. (2017)** | pp2–3 inclusion screening; pp10–12 method taxonomy; 113 cases across 41 publications have distinct scales/horizons and are not interchangeable head-to-head results |

## Prescribed Paper A/A0 next gates

1. **Original-source and rights gate**: obtain Kerala SLDC actual daily original, ask CSTEP/EMC for 2016 15-minute, Grid-India for 2021–23 actual hourly, NLDC for 2009–13 five-minute records, plus actual/drawal/import/hydro definitions separately. Request time labels, IST cutovers, update revision, file format, field boundary and licensing; *none* obtained via papers.
2. **Weather gate**: versioned ERA5 acquisition + verified meteorological physical accumulation periods across IST midnight; explicit five-location spatial-weighting sensitivity, original data hashes and missing-year ledger.
3. **Validation gate**: locked calendar-only Ridge vs calendar+same-day ERA5 Ridge on equal qualified original MU/day rows; FY2022–23, FY2023–24, FY2024–25 later-year comparisons, exposed analyses acknowledged. MAE, RMSE, per-year signed weather skill and uncertainty; no day-ahead claim.
4. **Novelty gate**: original-unit target crosswalk against Hunt Grid-India public archive; acquire Porwal full text and Babu supplementary; if Paper A novelty not supported, pivot to bounded observability/accounting paper A0 or explicitly labelled technical report.

**Source corpus completeness:** 18 PDFs × **485 original pages**, every page visually screened, central pages high-resolution rechecked. **Not included:** Porwal full IEEE text; Babu supplementary tables; CEA 2035–36 report; authors' original code/datasets; CSTEP original FY2016 blocks. This work contributes **secondary-literature knowledge**, **not** new original Kerala numerical results.

**Data rights:** This is an original analytical research note. Neither source screenshots nor third-party PDF bytes may be attached to this public PR by default. The private full illustrated PDF, the private four-page thumbnail visual atlas and original SHA/page ledger remain in the user's conversation for review.
