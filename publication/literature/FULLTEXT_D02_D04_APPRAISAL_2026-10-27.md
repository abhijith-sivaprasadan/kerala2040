# Full-PDF critical appraisals: D02 Harish (2020) and D04 Babu (2026)

**Research notebook:** 27 October 2026. **Scope:** Two complete publisher-formatted journal article PDFs supplied privately by the research owner and read across methods, figures, tabulated results, appendices and conclusions. **Not** reproductions of the original studies or independent source-data access. **No third-party PDF bytes are committed here.**

## Uploaded primary-file provenance (private, non-redistributed)

| Stable matrix ID | Article / original source | Input PDF pages | Original uploaded PDF SHA-256 | Access state |
|---|---|---:|---|---|
| **D02** | Santosh Harish, Nishmeet Singh, Rahul Tongia, *Impact of temperature on electricity demand: Evidence from Delhi and Indian states*, **Energy Policy** 140 (2020) 111445; DOI **10.1016/j.enpol.2020.111445** | **14** | \`384d54f7ce35912890f30ab41514f27fe7f68ffe1f42897c7ce48a82e0b7496d\` | User-provided full publisher PDF; text, critical tables and graphical pages examined |
| **D04** | Aravinda De Chinnu Arul Babu, Venkatasailanathan Ramadesigan, Rangan Banerjee, *Medium and long-term electricity demand forecasting for India – Incorporating EV charging and space cooling impacts*, **Applied Energy** 420 (2026) 128069; DOI **10.1016/j.apenergy.2026.128069** | **18** | \`046deeab21e3c7bd77338e058748808b94d586ec0991da4bab9367d79892738b\` | User-provided full publisher PDF; methods, Figs 1–14, Table 4, discussion and conclusions examined; **supplementary materials not supplied** |

**Important:** these are cryptographic identities of the *owner-provided PDFs*, not publisher-certified document identities, nor proof that the supplementary data/calculation can be reproduced. The owner supplied the files directly in ChatGPT; no published source PDF is mirrored into public GitHub.

## D02 — Harish, Singh & Tongia (2020) [full-text reappraisal]

### What it studied and with what observed data

- **Explicit questions (p. 2):** how short-run temperature changes associate with electricity usage at state/region and Delhi household levels; and how household response differs between disadvantaged and affluent groups.
- **Aggregate grid source:** NLDC/POSOCO **five-minute measured load (MW)** across Indian states, **2009–2013**, aggregated by authors into **daily mean MW**. Their data are *restricted load met*, **not uncurtailed underlying demand**. They explain variable load shedding and incorporate **monthly CEA reported supply deficit** as a limited, imperfect adjustment (p. 2). Their original 5-minute observations were shared with authors; the article does **not** establish present-day online access or licensed reuse for us.
- **Weather:** IMD 1°×1° gridded daily temperature and precipitation by Indian state; distinct Delhi NOAA Safdarjung station temperature/humidity for the residential bill panel (p. 3). **Not ERA5**.
- **Residential counterpoint:** TPDDL de-identified bills, Delhi January 2014–September 2017, sample **160,841 consumers** and around **5.14 million billed-cycle rows** after sampling and selection; the original raw billing data are not in this upload (p. 3, Table 2).
- **Statistical method:** semiparametric temperature-bin **log-linear fixed-effect regressions**. State regression \`Model 3\` uses log daily average load with temperature bins referenced to **21–24°C**, precipitation and monthly supply deficit plus state, month, year, state×month and state×year effects (p. 4). This is an observational adjustment, **not a standalone experimental/counterfactual proof** of caused load increases.
- **Kerala-specific result** (Appendix Table A3, **PDF p. 12**, column 17): **1,737 Kerala days**, reported regression \`R²=0.892\`; **24–27°C log coefficient 0.0211*** (SE 0.00340)** and **27–30°C 0.0694*** (SE 0.00510)**, both relative to days at 21–24°C. Exact multiplicative changes are \`exp(beta)-1\`: approximately **2.13%** and **7.19%**. **No estimate is displayed for Kerala in the 30–33°C row or higher bins**; it is *not* a zero effect. Those are **historical conditional model coefficients**, not contemporary 2026 measured cooling demand and not directly comparable with an ML RMSE or SHAP contribution.
- **Pooled results** (p. 5 and p. 6): authors report an 11–14% short-run aggregate rise over 30°C relative to temperate reference with major regional/state heterogeneity; **do not automatically apply pooled Delhi or all-India values to Kerala**.
- **Income/ecological caution:** Delhi's household temperature response is sharply weaker among low-income / JJ-cluster consumers (p. 7–8); state aggregate models do **not** identify household AC ownership or access. Financial and rationing confounders cannot be resolved by statewide weather-only learner.

### Scientific strengths

1. **Two genuinely different observational aggregation levels** — 5-minute grid load converted to daily means and household billing — help distinguish ecological inference from device/consumer behaviour.
2. Transparent linear predictor and fixed effects (state/year/month interactions), reference temperature bins, reported uncertainty and **state-specific coefficients** including Kerala.
3. Direct acknowledgement that **metered energy served can understate latent demand** under curtailment, with a partial CEA monthly-deficit covariate.

### Limitations / fair interpretation

- No clean causal temperature elasticity is identified from source definitions alone; author interprets short-run weather variation as exogenous under model assumptions, but supply restrictions and unmeasured economic/operational drivers remain important. Monthly supply deficit cannot recover unseen **hourly** unmet load.
- Grid outcome reported as **daily mean MW**, not the Kerala SLDC source \`consumption_qualified_mu\` in **MU/day**; converting units is arithmetically possible only when the true 24-h interval/boundaries and metered scope are known. Do not assert their KL data matches our original daily reports.
- Restrained **temperature-support range** in humid coastal Kerala: high-bin coefficients are blank in the printed table, thus no extrapolation beyond 30°C from its Kerala-specific table. State coefficients may be driven by seasonal covariates, actual met load and the model's temporal effects; no transport of estimates to FY2024–25 without testing.
- The 2009–13 source five-minute archive **does not belong** to Kerala2040's authentic current datasets; the paper is *documentary evidence that NLDC possessed such resolution for historical analysis*, not evidence that it is accessible or can be merged.
- The full paper prints an Appendix Table A3 with Kerala values, eliminating any literature claim that pre-2025 research did not measure Kerala temperature response.

### Required study implications

- **No first Kerala temperature-response claim.** Literature argument should cite the 2020 Appendix A3 Kerala regression alongside the 2025 Hunt/Bloomfield Kerala XGBoost experiment.
- Separate **daily-average power MW**, **daily integrated MU**, **energy met**, **reported consumption**, and **latent unmet demand**. Set a genuine source-boundary crosswalk prerequisite.
- The future grid data outreach should mention **historic state five-minute load was available for 2009–13 to Harish et al. through NLDC**, while asking the custodian if archives can now be retrieved in any retained format. Do not claim permission or public availability from this publication.
- If Paper A's future measured series includes load-shedding, registered sensitivity to observed/official supply restrictions may be required; no fictional unserved energy series.

## D04 — Babu, Ramadesigan & Banerjee (2026) [full-text reappraisal]

### What it studied

A **medium-term (1–2-year) state-wise daily demand LSTM** and a **long-run model through 2070** combining GDP trends, weather, additional cooling and EV charging, with **hourly *constructed forecasts*** intended for power-capacity planning. They do **not** claim to have collected a continuous measured hourly 2040 future load curve.

### Original historical data, crucial for our custodian request

**Most important previously unverified finding (p. 4, section 2.1):** the authors **obtained state-level hourly demand from GRID-INDIA for 2021–2023**. They then **selected 2023 observed hourly curves**, normalized each day's hourly profile to its total, and used it as a **shape/template** to rescale projected daily demand into *future* hourly estimates. If adjacent-day boundary-hour demand differs by >25%, they blend the preceding three hours to smooth it (pp. 4–5). This proves that state-level hourly *observations were used and accessible to these investigators*, **not** that a public 2021–23 file can now be downloaded or that the authors release interval records for Kerala. **Do not present their future hourly series as original observed dispatch/load.**

**Potentially actionable official contacts from the paper (PDF p. 17 Acknowledgment):** authors explicitly credit former GRID-India CMD **Narasimhan S. R.** and **Vivek Pandey, Chief General Manager, GRID-India, and his team** for guiding/providing data. These are **historical published role identifications**, not verified 2026/current job titles, authorised personal contacts, or automatic authority to share data. Relevant request channels: GRID-INDIA's official data-access route in addition to Kerala SLDC/KSEBL; a separate courteous author request to corresponding author Ramadesigan (publisher correspondence **venkatr@iitb.ac.in**, p. 1) is another practical lead, subject to approval before sending.

**Original daily and weather sources (p. 4):** GRID-INDIA's published daily reports FY2015–FY2024; MERRA-2 reanalysis, MoSPI GDP; three most populated cities per state with 2011 census weights. They exclude **April 2020–December 2021** from the study's daily model training due to pandemic disruption; original 2021–23 hourly archived intake is a separately described source.

**Year-label warning:** p. 4 explicitly says named years in the study represent **financial years** (e.g., “2015” runs April 2015–March 2016). Thus the author-labelled **2021–2023 hourly source period** must **not** be converted into a calendar-year start/end without checking the actual timestamped export. Ask Grid-India or the authors to specify the first/last interval, UTC/IST labelling, aggregation semantics and state boundary.

### Medium-term methodology & model evaluation

- LSTM on daily data with GDP, temperature, wind, solar irradiance, rainfall, RH and cyclic month/day/weekend features, train/validation/test separation and Smooth L1 loss, early stopping. The paper reports state MAPE typically <5% in **Supplementary Table SM2, not supplied here**, so **we cannot authenticate Kerala's specific MAPE** from the main file.
- **Table 4, p. 7:** a valuable genuine source-exposed vs held-out demonstration. Predicts FY2023 (**Jan–Mar 2024 shown in Fig. 4**): models trained **through Mar 2024** (*seen data*) have substantially lower error than models trained **through Mar 2023** (*unseen data*). The **South regional** (not Kerala state!) **MAPE rises from 0.6±0.1% (seen) to 6.7±0.2% (unseen)**. Their reported errors capture change between an in-training and later-period evaluation, **not** proof that full design was prospectively analyst-unexposed or that the same score holds for Kerala.
- **Potential data preprocessing leakage concern (p. 4):** narrative says data cleaned/outliers removed/missing values interpolated *before* it describes sequence creation, dataset partition, and feature normalization; the text **does not prove** whether transformations were estimated with full-series lookahead or entirely within the training window. Code/appendix/source verification is needed before assigning leakage severity. Stronger claim would be unjustified.
- The table's labelled “seen data” is **explicitly in-sample/exposed**, not a fair future-year validation; their **unseen** scenario is the relevant comparator (though still not a replicated independent test).
- The authors' **2025 demand increase**, **2030–2070 projections** and **scenario ranges** are forecast scenarios, not observed Kerala history.

### Long-term framework and major assumptions

- For long-horizon GDP growth, the model predicts normalized demand per GDP using **fixed 2023 weather** to avoid unphysical projections from future reanalysis features, then multiplies by OECD/EY GDP scenarios. Separately estimates climate-driven incremental cooling from **21 CMIP6 models** and cooling-degree days, plus EV adoption trajectories via lagged Gompertz vehicle ownership projections (pp. 5–9).
- Additional cooling uses a residential archetype-room CDD relationship and **assumes it transfers to the broader residential/commercial sector**; future AC ownership scales with GDP for lack of adoption data. Cooling demand annual -> monthly -> hourly via reused shape profiles (pp. 5–7).
- Projected demand **6935 ±175 TWh by 2070** under OECD GDP scenario (p. 12), plus indicative added national cooling up to **270 TWh** and EV charging up to **375 TWh** (p. 15–16). These are **conditional modeled national scenario values**, not likely measured Kerala outcomes. The authors' **Fig. 14** illustrates a modeled shift toward higher evening demand under one high-emissions case.
- Authors explicitly acknowledge **single 2023 reference intraday profile** and proportional-to-GDP AC growth as major limitations (p. 17). They provide main paper data **“on request”** (p. 17). Supplementary materials are via DOI; neither the actual GRID-INDIA 2021–23 interval files nor state SM2/SM3 error tables are attached to the provided 18-page main PDF.
- No independent source-file QA, external validation or supplementary algorithmic replication performed here.

### Scientific strengths

1. State-level separately trained model and explicit **seen vs unseen** evaluation contrast, important acknowledgement of forecasting performance inflation when training includes the target year.
2. Combines distinct demand drivers and model input scopes, and openly distinguishes measured historical source from constructed 2040/2070 hourly time series.
3. Demonstrates **specific actual Grid-India hourly source existence/access in 2021–23** with source owner acknowledgement and a simple reusable normalization workflow that we must **not mistake for observation**.

### Limitations / fair interpretation

- Future hourly curves inherit a single historical hourly shape from 2023; time-of-use of cooling, EVs, intra-day transfer constraints and system disturbances may change. Single-year template + smoothing **cannot validate actual hourly 2040 system adequacy**.
- Entire-country year-ahead demand results and aggregate South-region MAPE cannot substitute for **Kerala SLDC original MU/day**. The hourly source might be different Grid-India boundaries from SLDC consumption and actual interstate drawal.
- Solar/weather forecasts vs retrospective reanalysis must be distinguished for honest operational decision-use.
- Additional EV/cooling projections depend on GDP, policy penetration, vehicle efficiencies, split between home/public charging, climate and model selection; any future Kerala scenario should carry sensitivity/bracket and never import national central projections by simple proportional allocation.

### Required study implications

- **Priority escalate actual interval load-access request:** original verified **state-level hourly 2021–23 Grid-India records** and any earlier/later records in 5-minute/15-minute/hourly electronic formats. State precise physical field, IST block boundaries, averaging scheme and revision/vintage; retrieve actual interchange alongside hourly load and hydro if available.
- Cite Babu as direct precedent for **Indian-state hourly load-based planning forecasts** and medium-term LSTM; no claim our eventual use of hourly demand shape estimation is unique. We still can be different by **not inventing an observed hourly profile where only synthetic downscaling exists**.
- Consider using this paper's **two evaluation windows** to justify reporting performance on genuinely later dates instead of an artificially rosy within-trained-period accuracy table. Do not claim their study is flawed: the authors deliberately label both regimes and report both.
- **Reevaluate strategic Paper A/A0 scope:** original-source operating-data comparison and authentic 2021–23 measured hour-level validation may be worth more than another ERA5/XGBoost/SHAP model. Measured interval data access is an independent source gate, not a guaranteed published dataset.

## Across-study comparability decision

| Attribute | D02 Harish 2020 | D04 Babu 2026 | Hunt/Bloomfield 2025 (separate full-PDF review) | Kerala2040 currently admitted |
|---|---|---|---|---|
| Observed grid target | NLDC state **5-min measured MW**, reduced to **daily average MW** | GRID-INDIA daily energy from PSP reports, **2021–23 measured hourly state demand** only as template source | Grid-India reported daily energy met, transformed target used in predictive models | Kerala SLDC daily original-source-qualified operational consumption (MU/day) |
| Temperature source | **IMD** 1° gridded daily weather | **MERRA-2** daily meteorology and bias-corrected future **CMIP6** | **ERA5** population-weighted meteorology | **ERA5** five equal-weight representative stations |
| Inference | Temperature-bin observational FE association | LSTM medium/long-term forecasts; future demand components | Statistical ML association/explanation, published random partition | FY2024–25 retrospective observational weather association; multiyear paper is **not** source-admitted |
| Clock/interval data | 2009–13 original NLDC **5-min** source; original records not available to Kerala2040 | 2021–23 original GRID-INDIA **hourly** source; actual records not available to Kerala2040 | Published daily data, no certified actual Kerala interval load in this source | No authenticated actual Kerala 15-minute/hourly load or interchange |
| Kerala-specific demonstrated output | Appendix Table A3 Kerala state coefficients (historical) | South-region Table 4; Kerala-specific SM2/SM3 **unavailable in main PDF** | Kerala full XGBoost test R² 0.835 on processed target | Previously published FY2024–25 incomplete day audit and retrospective weather ablations |
| Current permitted conclusion | Kerala temperature sensitivity *was already studied* in a formal published state model | Indian-state hourly measurements were used in a peer-reviewed study, but future curves are downscaled estimates | ML geographic/algorithmic first use ruled out | **Novelty awaits original source comparison**; no unearned claims |

## Follow-up: exact data requests supported by these new publications

**Without implying any historical permission or current staff affiliation, ask official source custodians or corresponding authors whether they can provide:**

1. Historic **actual Kerala state demand/load met**, ideally continuous 5-minute/15-minute/hourly with dates, all intervals including missingness, earliest retained digital source through most recent.
2. The **2021–23 statewide measured hourly demand** underlying Babu et al.'s published work, and associated original GRID-INDIA definitions for “state-level hourly demand.” If national licensing restricts sharing, ask for an official public/archived URL and point-of-contact.
3. Historical **actual** state net grid drawal, imports/exports, and separate scheduled interchange at original time-step. Never equate actual flows with schedules or the met demand curve.
4. Original **hydro generation**, unit/metered plant daily/interval energy, reservoir operational limits (if held), and per-period data dictionary and source revisions, only as an optional separate source path.
5. Clear data reuse/licence/redistribution terms, especially if independent machine-readable open research outputs are anticipated. We can publish *derived research code* openly without assuming licence to redistribute their measured telemetry.

**Outreach must remain a draft unless the owner explicitly requests sending.** No personal contact details are inferred beyond the published corresponding author email and public institutional names. Do not represent the research as a KTH-sponsored project.

## What is NOT accomplished

- Original 5-minute NLDC 2009–13 data not downloaded.
- Original hourly GRID-INDIA 2021–23 data not downloaded.
- None of the requested PDF supplementary materials or author code (Babu) obtained in this review.
- No original Kerala SLDC daily records compared numerically to NLDC / GRID-INDIA or reproduced from the two papers.
- No private raw file leaked; no unreviewed result promoted into the October public findings freeze.
