# Kerala2040: evidence-to-freeze research programme, 2026–2027

**Status: PROPOSED RESEARCH CHARTER — NOT APPROVED, NOT A MODEL OR EVIDENCE PROMOTION**  
**Prepared:** 26 October 2026 · **Work window:** 1 November 2026–26 October 2027  
**Public evidence baseline:** `docs/RESEARCH_FREEZE_2026-10-23.md` (immutable scientific claims until individually reviewed)  
**Proposed research freeze:** 26 October 2027; new data/model-result admissions cease 31 August 2027, except independently reviewed corrections.  
**Owner:** Abhijith Sivaprasadan · independent research, no implied KTH/KSEBL/agency endorsement.

> **Problem-led question:** How do Kerala's demand variability, dependence on electricity imports, hydropower operating constraints and network limitations interact to affect electricity-system resilience, and which response mechanisms remain promising after uncertainty and physical feasibility checks?

The word *resilience* here requires an explicit metric and disturbance. The programme may report descriptive historical exposure and *conditional* adequacy-model responses. It may not assert observed interruption risk, real-event causation, LOLE, calibrated N-1 risk, or a 2040 optimal investment portfolio without the corresponding validated observations and system model.

## 1. Why change the research strategy?

Kerala2040 already has far more models than observed hourly operational evidence. Its strongest public evidence comprises official reported FY2020–21 to FY2024–25 annual consumption, source-audited FY2024–25 daily SLDC records (354/365 observed reports, 11 missing), an installed-generation stock statistic, and a one-year rolling weather–demand exercise with 353 matched observed SLDC daily demand and complete IST-day ERA5. The public-facing study froze these findings on 23 October 2026 and explicitly downgraded modeled hourly stress/network/hydro projections to exploratory status.

Scientific bottlenecks:
1. **Different meters/boundaries:** official annual consumer-side consumption cannot be subtracted from SLDC operating daily consumption to infer imports or loss. There are 11 missing daily reports in FY2024–25. The reconstructed hourly demand is *not measured telemetry*.
2. **External generalization:** the within-FY weather contribution won 6/7 XGBoost and 5/7 LightGBM monthly folds, but cannot yet be generalized beyond FY2024–25. Same-day ERA5 reanalysis is not an operational forecast.
3. **Physical dispatch:** seven-day and FY2030–31 hydro tests use unverified dispatch freedom/ramp/storage; source-verified station availability, inflow, releases, topology and constraints are not yet reconciled.
4. **Network and imports:** source-backed robust line screening is not calibrated AC/N-1 or reliable delivered ATC over hours. Daily import totals do not give independently authenticated state hourly interchange and load.
5. **Future uncertainty:** a 2040 system-wide cost optimum cannot be defended without verified time series, vintaged project costs, constraints and institutional/rights definitions.

Build one auditable common evidence layer and pursue a *minimum publishable historical result* before a conditional model scenario paper.

## 2. Scope and contributions — choose what to claim, not only what to code

**Primary contribution A (mandatory):** an open, reproducible audit of multi-year Kerala SLDC daily operating quantities, source completeness, seasonality, units, metering boundaries, missingness and cross-source consistency. Keep protected/raw third-party material private when necessary; make reusable code, source manifests, method and permitted derived aggregates public.

**Primary contribution B (priority):** a retrospective, multi-financial-year benchmark: observed qualified daily SLDC demand versus same-day ERA5 at five fixed Kerala points, with calendar/seasonal and simple statistical baselines; expanding-origin fiscal-year holdouts; no temporal leakage; error distribution and uncertainty. Publish **negative** weather gains if observed.

**Conditional contribution C:** hydro/import flexibility envelopes under source-supported station or reservoir bounds, compared against explicitly optimistic bounds and conservative fixed schedules. Report *model opportunity bounds* unless metered dispatch and water-balance checks support stronger conclusions.

**Conditional contribution D:** robust network and scenario comparisons only for independently supported physical and economic inputs. Model outputs cannot be translated into recommended projects or actual blackout probabilities by changing labels.

**Explicitly outside this year's core scope:** inventing a full 2040 pathway, nuclear/SMR deployment, simultaneous full AC network expansion + basin hydrology + land permitting + multi-sector decarbonization, attributing a specific load-shedding event from daily data, and new ML architectures without demonstrated incremental evidence.

## 3. Research questions, hypotheses and disconfirming results

| ID | Predeclared question | Main outcome and comparison | What would falsify a strong claim? |
|---|---|---|---|
| RQ-A | What is actually measured in Kerala's electricity balance, how complete are the sources, and what changes across financial years? | Audited matched-boundary annual/monthly/daily series; observed-vs-missing by day; cross-publisher discrepancy register | Source semantics incompatible, unreliable coverage or unreconciled boundaries: publish audit, not a derived synthetic series |
| RQ-B | Does same-day ERA5 weather improve retrospective explanation of SLDC qualified daily consumption across genuinely later fiscal years? | Per-FY RMSE, MAE, MASE, signed skill versus frozen calendar and seasonal-naive baselines, year-level variation | Weather gains vanish, reverse sign, or only occur after tuning on test folds; report negative result and limit claims |
| RQ-C | How do heat, hydro availability and external supply indicators co-vary on observed days? | Seasonally controlled descriptive contrasts and uncertainty; each predictor tied to exact reporting boundary | No robust association after calendar/season and temporal uncertainty; do not claim specific outage cause |
| RQ-D | How much *modelled* redispatch benefit remains when actual station/storage/environmental constraints replace optimistic hydro timing? | Same total daily energy, same demand/import assumptions, controlled cases and energy/water conservation | New physical limits eliminate benefit or source data do not support constraint estimates: retain upper-bound-only result |
| RQ-E | Under which documented import/network conditions would the ranking of candidate demand shifting, hydro flexibility, storage and local resources change? | Robust ranges over predeclared credible inputs; qualitative dominance or ranked uncertainty, not one optimal MW | Rankings are unstable, model infeasible, or inputs not admissible: report indeterminacy; suppress investment prescription |

**Hypotheses are testable proposals, not pre-decided findings.** Pre-register model choices, transforms and comparisons before any new evaluation, and keep the already inspected FY2024–25 period declared *exposed*, never pristine.

## 4. Literature-to-method crosswalk

Peer-reviewed anchors and official benchmarks, to be mapped into a citation-manager library and updated with forward/backward citation screening:

| Source | Research use, not borrowed numerical truth |
|---|---|
| Pfenninger, Hawkes & Keirstead (2014), *Renewable and Sustainable Energy Reviews*, DOI [10.1016/j.rser.2014.02.003](https://doi.org/10.1016/j.rser.2014.02.003) | Challenges of temporal/spatial resolution, complexity, uncertainty and transparency |
| DeCarolis et al. (2017), *Applied Energy*, DOI [10.1016/j.apenergy.2017.03.001](https://doi.org/10.1016/j.apenergy.2017.03.001) | Problem-driven ESOM questions, model boundaries, review and uncertainty |
| Roberts et al. (2017), *Ecography*, DOI [10.1111/ecog.02881](https://doi.org/10.1111/ecog.02881) | Reject random cross-validation with temporally/spatially structured data |
| Hyndman & Koehler (2006), *International Journal of Forecasting*, DOI [10.1016/j.ijforecast.2006.03.001](https://doi.org/10.1016/j.ijforecast.2006.03.001) | Transparent scaling/selection of forecasting error metrics (MASE plus MAE/RMSE) |
| Hersbach et al. (2020), *Q. J. Royal Meteorological Society*, DOI [10.1002/qj.3803](https://doi.org/10.1002/qj.3803) | ERA5 is reanalysis, not station measurements or forecasts available at decision time |
| Staffell & Pfenninger (2016), *Energy*, DOI [10.1016/j.energy.2016.08.068](https://doi.org/10.1016/j.energy.2016.08.068); Pfenninger & Staffell (2016), DOI [10.1016/j.energy.2016.08.060](https://doi.org/10.1016/j.energy.2016.08.060) | Wind/PV time series require independent bias/performance checks against actual measured plant/fleet outputs |
| Brown, Hörsch & Schlachtberger (2018), *Journal of Open Research Software*, DOI [10.5334/jors.188](https://doi.org/10.5334/jors.188); Howells et al. (2011), *Energy Policy*, DOI [10.1016/j.enpol.2011.06.033](https://doi.org/10.1016/j.enpol.2011.06.033) | Use PyPSA/OSeMOSYS as transparent mathematical frameworks; libraries are not validation of input data |
| Frysztacki et al. (2021), *The strong effect of network resolution...*, [arXiv:2101.10859](https://arxiv.org/abs/2101.10859) | Spatial aggregation and network bottlenecks can change apparent model optima (study is not Kerala calibration) |
| Kiehle et al. (2025 online / 2026 volume), *Energy, Ecology and Environment*, DOI [10.1007/s40974-025-00385-5](https://doi.org/10.1007/s40974-025-00385-5) | Environmental-flow and cascade constraints must appear in hydro opportunity estimates |
| Morris (1991), *Technometrics*, DOI [10.1080/00401706.1991.10484804](https://doi.org/10.1080/00401706.1991.10484804); Sobol (2001), *Mathematics and Computers in Simulation*, DOI [10.1016/S0378-4754(00)00270-6](https://doi.org/10.1016/S0378-4754(00)00270-6) | Screening then global sensitivity only for a bounded, computationally tractable, physically valid model |
| Pfenninger et al. (2017), *Energy Policy*, DOI [10.1016/j.enpol.2016.11.046](https://doi.org/10.1016/j.enpol.2016.11.046); Morrison (2018), *Energy Strategy Reviews*, DOI [10.1016/j.esr.2017.12.010](https://doi.org/10.1016/j.esr.2017.12.010) | Reproducible open code; disclose data redistribution, intellectual-property and security boundaries |
| Saltelli et al. (2020), *Nature*, [model manifesto](https://www.nature.com/articles/d41586-020-01812-9) | Quantitative models should show assumptions, uncertainty and policy limits |

Primary Kerala comparators — **not held-out truth or interchangeable projection numbers**:
- [CSTEP, *Kerala Energy Transition Roadmap 2040* (2024)](https://cstep.in/publication/kerala-energy-transition-roadmap-2040/).
- [CEA, *Resource Adequacy Plan for Kerala to 2035–36*](https://cea.nic.in/resource_adequacy_st/report-on-resource-adequacy-plan-for-kerala-up-to-2035-36/).
- [WRI India, *Pathways for Kerala's Clean Energy Transition* (29 September 2026)](https://wri-india.org/research/pathways-keralas-clean-energy-transition).
- [Kerala State Planning Board, *Economic Review 2025*](https://spb.kerala.gov.in/sites/default/files/2026-01/ER%202025%20Volume1%20Eng%20final.pdf).
- [Kerala SLDC original daily records](https://sldckerala.com/index.php?id=1).

Before comparing forecasts, register each study's scope (gross/final/net electricity, calendar/FY endpoints, demand electrification assumptions, installed versus delivered capacity, imported renewables, loss treatment, emissions and study publication vintage). Do **not** blend CSTEP/WRI/CEA estimates into a single unsupported consensus trajectory.

## 5. Work packages and decision gates

### WP0 — research design, literature and governance (42 focused hours)

- Freeze the 23 October 2026 version as the published baseline; branch future results rather than overwriting the historical claim trail.
- Systematic *targeted* search: indexed peer-reviewed papers, bibliographic snowballing, report methods; citation table with research gap, definitions, data and applicability, strengths and weaknesses. This is not a PRISMA systematic review unless a search-and-screen protocol is explicitly registered.
- Register RQs, metrics, null/no-improvement outcomes, selection criteria and end points **before** new modelling runs. Maintain a decision log of justified amendments.
- Data schema: one canonical IST-day register, financial-year periods, unit dictionaries, provenance licence, original SHA-256 and per-variable source boundary. Separate daily SLDC, annual consumer-side, SRPC actual drawal, scheduled drawal, CEA study inputs.
- G0: every public promoted metric has a source chain; claims are labelled observed / derived / proxy / scenario.

### WP1 — primary data recovery and accounting (82 focused hours)

Parallel early outreach (not a guaranteed delivery):
- Kerala SLDC/KSEBL for hourly/15-minute state demand and actual interstate interchange, metadata, and the 11 missing FY2024–25 daily reports. Existing draft: `docs/SLDC_DATA_REQUEST_DRAFT.md`; user approval required before sending.
- CSTEP/EMC for the original FY2016 15-minute dataset referenced in the roadmap; CEA for whether FY2024–25 hourly underlying inputs can be released. Request official aggregate data only; avoid system-security details.
- KSEB reservoir station-level and storage/inflow/monthly returns; SRPC revisions of actual versus scheduled drawal.

Compute and store **private** SHA-256 originals, retrieval dates, source URLs, schema, licence and access scope. Verify daily count, duplicated dates, financial-year boundary and missingness; do not fill absent SLDC days with simulated values. Audited source days remain separate from the 365-day operational calendar. For different meter/measurement definitions, report separate series and unresolved difference — no rescaling to close an impossible reconciliation.

Historical ERA5: additional multi-year exact-hour source windows for five fixed points. Request in bounded batches, respect Copernicus quotas, archive original ZIP/NetCDF and validate variable units, coordinates, timestamp semantics, UTC-to-IST conversion (boundary hours matter), missing/duplicate records and source hashes. Re-use the FY2024–25 original/source-QA workflow patterns. Don't treat a passing normalized Parquet panel as authentication of upstream GRIB/NetCDF.

G1: separate per-product PASS/FAIL/NOT_OBTAINED records, including rights. Missing primary hourly load does **not** block the daily descriptive or retrospective daily-weather paper, but does block operational-load validation.

### WP2 — robust multi-year observed daily demand × ERA5 (80 focused hours)

Study unit: qualified original SLDC daily consumption **MU/day**, *not* reconstructed hourly demand, and not a year-end consumer-sales series.

- Fixed fiscal-year, strictly chronological expanding-window holdouts. Existing intended windows: FY2022–23, FY2023–24 and FY2024–25 with training only before each held-out period; document all exposure and data-revision risk.
- Baselines before complex ML: seasonal naive (same weekday/season where feasible, otherwise declared lag), calendar-only Ridge, annual/seasonal mean; optional day-of-week and public holiday metadata only if source-defined. Missing target dates remain missing.
- Primary analysis: a predeclared fixed Ridge alpha=1 calendar versus calendar+weather comparison, matching current private runner. Only after this succeeds consider LightGBM/XGBoost with training-only nested temporal hyperparameter tuning, no test leakage, and fair tuning budget. Different accuracy and model complexity do not imply causal effect.
- Performance: per-FY and pooled RMSE/MAE in MU/day; seasonal-naive-scaled error with denominator defined on each training fold; worst-year signed weather uplift; median/uncertainty of FY uplift; tail/high-demand-day error. Do not make a pooled skill number the only headline.
- Uncertainty: report financial-year-level variability (only three out-of-year test windows), and moving/block bootstrap sensitivity only where block lengths are justified. Show negative months and years; inspect residual autocorrelation and regime change. Avoid pseudo-precise confidence intervals from treating correlated daily dates as independent.
- Ablations: same-day temperature, humidity **only if acquired and predeclared**, precipitation, radiation, wind, seasonal controls, regional point weighting; explicit forecast-vs-retrospective distinction and temporal aggregation. SHAP as descriptive model attribution only, not causation.
- Strict output: executable fold manifests, original archive hash lineage, model input hashing, and aggregate outcomes. No raw restricted rows publicly uploaded.

G2: the per-FY experiment reproduces independently and no evidence leakage occurs; *no minimum positive performance threshold*. Null/worse weather results are legitimate scientific output. Never label same-day reanalysis as an operational day-ahead forecast.

### WP3 — source-constrained hydro, imports and network evidence (70 focused hours)

Start with descriptive measured daily hydro energy, reservoir storage and reported exchange (source boundaries separate), then choose **one** technically testable flexibility mechanism. Default: a station-cluster/Idukki hydro timing envelope, not a Kerala-wide optimal cascade.

- Plant register: station/unit name, effective MW, unit count, dates, storage MWh/water units, head, upstream/downstream routing, reservoir conservation, daily release/inflow, minimum environmental/irrigation releases, exclusions and provenance. No assumed 400 MW/h aggregate ramp promoted to observed.
- Build three identical-input comparisons: frozen original hydro schedule; optimized unconstrained energy-conserving theoretical upper bound; source-supported constrained schedule. Preserve exact daily hydro MWh when comparing timing and reject infeasible water balances. Cross-check externally observable peaks and daily/monthly hydro energy as far as admissible.
- Transfers: schedule and actual import must never be conflated. Test 4,455 MW source-dated ATC as an explicit benchmark/sensitivity parameter, not an observed full-hour available transfer limit. Never infer outage or observed unmet demand from optimization penalties.
- Network: preserve historic public-source robust screening; do not call Shornur a verified AC/N-1 vulnerability absent topology, impedances, injections, contingency and limit verification. New network investment results require separate gate.

G3: report a source-supported feasible bracket **only** if physical constraints are traceable and independent invariants pass. Otherwise report optimistic upper bound with missing evidence and terminate calibrated hydro-extension claims.

### WP4 — restrained scenarios and global uncertainty (55 focused hours)

Only start if G1–G3 yield enough evidence to support the chosen quantities. Use model discrepancy ledgers for unvalidated variables. Predeclare a *small factor table*: historical demand growth range, external transfer availability, hydro operating envelope, weather year, solar/wind availability (if validated against output), demand-shifting fraction and storage duration/efficiency.

- Separate physically supported ranges, official planning-study comparators and invented *stress assumptions*. Never silently mix into a probability distribution.
- Screening stage: single-factor or Morris elementary effects to find material drivers at reasonable cost; only use Sobol/Monte Carlo when joint distributions have evidential meaning and computational expense is justified.
- Paired identical-case comparisons with/without an intervention, common weather/demand/sample constraints, conserved hydro/water/storage energy and solver residual checks; log infeasible runs and non-dominance.
- If original hourly load is still absent, demonstrate conditional effects under *explicitly proxy-labelled* profiles, not probabilistic LOLP/LOLE or predicted shortages. Report intervals of sensitivity, not project investment sizes.

G4: intervention ranking survives declared stressors and independent basic consistency. If ranks reverse, this is a research result: publish **uncertain ranking**, not an invented winner.

### WP5 — manuscripts, review, published release and freeze (71 focused hours)

Prepare:
1. **Paper A:** open-data/source-assessment plus multi-year retrospective daily weather-demand study; primary submission candidate when WP1–WP2 evidence supports it.
2. **Technical report B:** conditional Kerala hydro/import flexibility mechanics with explicit missing-input and optimistic-versus-constrained bounds; a second article only if genuine new independent validation is achieved.
3. **Kerala2040 Evidence Atlas:** one public site which walks source → definition → method → result → uncertainty → data-rights, and cleanly segregates exploratory models.
4. Reproducible release: author citation metadata, bibliography/DOIs, environment lock, original source manifests with rights restrictions, frozen git SHAs, unit/physical/property tests, exact command-line reproducer, figures with traceability, null results and limitations.

Commission at least two structured methodological critiques where possible (energy-system modeller and Kerala operational/SLDC domain expert). External feedback must not be asserted if not obtained. Preprint or journal **submission** is an aspiration; acceptance cannot be promised.

G5: cut off adding claims by 31 August 2027; September is rebuttal, audit and reproducibility time; freeze versioned materials 26 October 2027. If data gates are unmet, release the strongest verified **descriptive and methods** article rather than force a 2040 optimum.

## 6. One-year calendar: hard decision points

| Window | Primary milestone | Exit criterion and fallback |
|---|---|---|
| Nov 2026 (M1) | Approve charter and effort ceiling; bibliography; scope/metrics registration; custodian outreach; dependency board | Named baseline and rights ledger; if emails unanswered, escalate to written data-access/official publications (do not claim received) |
| Dec 2026 (M2) | Consolidate private SLDC archive and annual boundary table; small extra-year ERA5 acquisition pilot | One additional audited year of source-point coverage, or documented cost/access failure; no fit |
| Jan 2027 (M3) | Scale ERA5 acquisition and full IST day gate; source audit and missingness tables | Exact original hash chain and normalized 5×24 panels for first eligible multiyear set; partial-year gaps documented |
| Feb 2027 (M4) | Execute predeclared fixed Ridge fiscal-year comparisons, independent script reconstruction | Per-holdout errors and null outcomes, not a cherry-picked winning model |
| Mar 2027 (M5) | Temporal robustness/ablation/uncertainty, core evidence atlas v2 and paper A outline | Negative-fold and assumption tables; paper A viable even if weather gain weak |
| Apr 2027 (M6) | Historical system/station hydro and SRPC exchange inventory; physical bounds | Explicit station provenance; if unavailable, narrow to audit + conditional upper bounds |
| May 2027 (M7) | Matched hydro/import model brackets and physical residual tests; independent network source audit | No 'validated' label without primary source-backed operation |
| Jun 2027 (M8) | Review physical-data sufficiency and freeze small factor set | Go/no-go for scenario experiments; if no, shift time to Paper A and evidence atlas |
| Jul 2027 (M9) | Limited paired stress experiments with source/cost boundaries and Morris screening if valid | Stable/unstable ranking with infeasibility logs; no invented reliability probabilities |
| Aug 2027 (M10) | Compare CSTEP, CEA and WRI 2026 assumptions and outputs; complete manuscripts and figures | All *new* empirical results submitted for internal review; **31 Aug data/model claim cutoff** |
| Sep 2027 (M11) | Independent methodological review, replication on clean environment, scientific QA/site audit | Critical issues documented/repaired; draft frozen |
| Oct 1–26 2027 (M12) | Reconcile citations, versions, licences; paper submission/preprint where ready, archive and final freeze | Release manifest, tag, source commit and archived artefacts; one-page limitations and follow-up register |

The October freeze is a publication milestone, **not** an obligation to claim that every proposed model passed.

## 7. Resource budget and risk-adjusted ROI (planning judgments, not calibrated measurements)

**Base capacity:** 10 hours/week × 50 active weeks ≈ 500 gross hours. Reserve **100 hours (20%)** for job-search conflicts, data-access delays, debugging and expert responses; budget **400 focused research hours**. All ranges are provisional until the researcher states real available hours.

| WP | Focused hours | Priority | Expected research/portfolio payoff | Main dependency |
|---|---:|---|---|---|
| WP0. Research protocol, literature, release discipline | 42 | **P0** | Prevents invalid work; strong research credibility; reusable manuscripts | None |
| WP1. Source recovery, daily boundary reconciliation and ERA5 audit | 82 | **P0** | Largest evidence bottleneck, enables all substantive claims | SLDC rights; CDS API quotas |
| WP2. Multi-year demand-weather study | 80 | **P0** | Highest near-term independently testable paper candidate | Multi-year original ERA5 inputs |
| WP3. Hydro/import/network source-constrained boundaries | 70 | **P1** | Direct engineering value, rich negative/conditional results | Physical asset + water/dispatch data |
| WP4. Bounded screening and sensitivity | 55 | **P2 / gated** | High scientific value *if* sources arrive, otherwise high overclaim risk | G1–G3 |
| WP5. Manuscript, reproducible release and freeze | 71 | **P0** | Converts a year of work into citable paper/portfolio | Basic programme completed |
| **Total** | **400** | | | |

Relative decision priority (qualitative, not fabricated empirical ROI): **(1)** get custodian data + rights, **(2)** verify the multi-year ERA5 chain, **(3)** complete Paper A, **(4)** peer critique/reproduce, **(5)** constrain one hydro mechanism, **(6)** optional robustness experiments, **(7)** only then improve visuals or broaden modelling. New code/UI receives no priority unless it eliminates a source/error/reproduction blocker or makes a defensible result clearer.

At **6 hours/week**, cut WP4, reduce WP3 to documentary validation, and pursue Paper A + atlas only. At **15+ hours/week**, use the extra capacity for original-source recovery, independent expert checks and stronger statistical sensitivity — **not** indiscriminate new model families.

## 8. Verification, claims, ethics and shutdown rules

**Sources and provenance:** immutable hashes of original raw bytes, edition and revision time, retrieval UTC, spatial/temporal boundary, units, licence, code commit, variable transform and independent quality flags. Restricted original inputs stay private and never leak via CI logs or website.

**Statistical:** use only qualified observed targets; predeclare time splits; reproduce baselines; no within-period leakage, future revision leakage or imputed ground truth; report changes including negative/null folds, error distribution and test-period exposures.

**Power/water:** check signed energy, power × duration, reservoir/inflow/release conservation, capacity/availability, transfer direction/constraints, simultaneous hydro and thermal output, and optimisation solver residuals. Storage shifts energy with losses and does not create it.

**Scenario and causality:** the case must state factual observables, model assumptions and counterfactual mechanism. Do not use terms 'identified cause', 'validated reliability', 'prevents load shedding' or 'least cost' without independently suitable evidence. Published benchmarks can challenge but do not automatically validate the new model.

**Stopping rules:** if two successive quarterly gates fail for unavailable original measurements, retire the corresponding calibrated objective and keep a labelled bounded methods study; if by 30 June 2027 no admissible new historical hourly material and no source-supported hydro constraints exist, stop new 2040 optimization runs entirely. If WP2 gets no adequate multiyear weather, publish a source-completeness audit plus multiyear *non-weather* observed SLDC descriptive study, not fake weather generalization.

**Public release minimum, irrespective of access:** provenance/evidence-atlas update, methodology note, at least one reproducible descriptive result built on admissible observation, quantitative missingness and uncertainty, and published negative results where encountered. Full planning adequacy and exact investment recommendations are optional and likely out of scope.

## 9. Open decisions requiring the researcher's input

1. **Effort ceiling:** actual sustainable time: 6, 10 or 15 hours/week? This controls whether WP3–WP4 survive.
2. **Publication target:** academic Paper A + transparent website (recommended), policy briefing, or both? Journal fit should follow the first multiyear results and consultation with an academic coauthor, not be assumed now.
3. **Data outreach authorization:** SLDC/KSEBL draft exists, but *sending it is a separate explicit action*. Availability of an academic referee/introduction may affect response odds.
4. **Access:** whether the private `kerala2040-source-archive` and original ERA5 files remain under user access, and whether a trusted collaborator can handle restricted source evidence.
5. **Geographic boundary:** treat Kerala state as one balancing aggregate (recommended baseline) or split into districts only after independently admissible district load/network data arrive.

**Charter is DRAFT pending these choices.** Do not silently alter the public research freeze or companion website as part of approving a planning document.
