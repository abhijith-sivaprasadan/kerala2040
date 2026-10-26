# Kerala2040: evidence-to-freeze research programme, 2026–2027

**Status: REVISED 10-HOUR/WEEK RESEARCH CHARTER — EFFORT CONFIRMED; REMAINING GOVERNANCE/OUTREACH DECISIONS OPEN; NOT A MODEL OR EVIDENCE PROMOTION**  
**Prepared:** 26 October 2026 · **Time budget confirmed:** 10 hours per week · **Work window:** 1 November 2026–26 October 2027  
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

Build one auditable common evidence layer and pursue a *minimum publishable historical result* before a conditional model scenario paper. At the confirmed 10-hour weekly ceiling, protect Paper A even if the second research stream must stop.

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
| Babu, Ramadesigan & Banerjee (2026), *Applied Energy*, DOI [10.1016/j.apenergy.2026.128069](https://doi.org/10.1016/j.apenergy.2026.128069) | A recent India-wide medium/long-term demand, cooling and EV projection comparator; not independent validation of Kerala's daily SLDC operating-consumption series |
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

## 5. Optimized 10-hour-per-week scope: work packages and gates

**Confirmed resource constraint:** 10 hours/week for **50 active weeks** within 1 November 2026–26 October 2027 = **500 hours gross ceiling**. Pre-allocate **400 research hours** (roughly 8/week) and keep **100 genuinely uncommitted contingency hours** (roughly 2/week) for paid-work/job-search disruption, licensing problems, technical faults, illness or unexpected agency requests. Do not promise 500 hours of deliverables; do not turn the buffer into automatic scope expansion. The plan assumes two approximately non-active weeks across the 360-day window. Log actual work and adjust at monthly gates.

### Investment order: Paper A is the critical path

| WP | Focused-hour budget | Decision level | Explicit finished output | Stop/acceptance rule |
|---|---:|---|---|---|
| **WP0 — protocol and bounded literature** | **35** | P0 mandatory | Registered RQ-A/B, bibliographic evidence matrix, data definitions, FY split manifest, hypothesis and null-result rules | Protocol frozen by 31 January; prospective amendments logged before tests |
| **WP1 — source verification and intake** | **90** | P0 mandatory | Reconciled qualified private SLDC archive; authentic ERA5 5-point chronology where obtainable; source/rights/hash ledger | No unverified original files, interpolated demand or invented missing SLDC days admitted |
| **WP2 — multi-year retrospective demand/weather benchmark** | **110** | P0 mandatory if source gate passes | Baselines, fixed-Ridge and *optional* weather-ML analysis, per-FY results, uncertainty, null outcomes and reproducer | March data go/no-go; no multi-year claim if planned out-of-FY evaluation is incomplete |
| **WP3 — hydro/import/network evidence triage** | **35** | P1, contingent | Source-gated single-mechanism constraint inventory and a rigorous feasibility/unknowns note; numerical comparison only if support exists | June 30 physical-data go/no-go; don't promise a new dispatch model |
| **WP4 — limited paired sensitivity** | **20** | P2, gated and dispensable | At most one pre-registered small paired experiment, plus energy/balance and parameter provenance tests | Not started if missing hourly observations/physical bounds would make result misleading |
| **WP5 — writing, external review, provenance release and freeze** | **110** | P0 mandatory | Paper A (weather analysis **or** primary-data methods fallback), atlas update, replication report, submission-ready package, tagged freeze | Full manuscript by August, critique/reproduction in September, release 26 October |
| **Total** | **400** | | | |

**Allocation change from the first draft:** WP0 42→35; WP1 82→90; WP2 80→110; WP3 70→35; WP4 55→20; WP5 71→110 hours. **345/400 planned hours (86.25%)** now support protocol + historical evidence + statistics + publication. WP3/WP4 cannot displace any P0 acceptance criterion.

**Do not parallelize three manuscript tracks.** The primary output is one rigorous article. An independent hydro-flexibility note is a technical appendix/working paper if time/data allow, **not** a second submission requirement. Website changes convey published, accepted source boundaries; they are not a separate front-end development workstream.

### WP0 — 35 hours, primarily November–January

- Pre-register Paper A's main question: does *same-day observed/reanalysis weather* add retrospective explanatory information beyond calendar controls for Kerala SLDC qualified daily consumption in **later fiscal-year tests**?
- Read and annotate a **bounded 25–35** relevant peer-reviewed papers (methods, Indian weather–load evidence, system balancing, ERA5 methods), recording DOI, question, study geography, observational unit, split/bias risk, useful design choice and counterevidence. This is a targeted scoping review, **not** a PRISMA systematic review.
- Lock target field, units, source boundary, FY year definitions, fixed 5-point geography, missingness policy, comparison metrics, and fiscal-year test windows. Explicitly disclose prior inspection of FY2024–25.
- Choose the primary, *no-tuning* Ridge experiment and simple baselines now; any boosted-tree tuning happens strictly inside later training folds if original-source availability justifies it.
- **Deliverable 31 Jan 2027:** dated protocol, evidence matrix, preregistered decision log and no-claims audit.

### WP1 — 90 hours, November–April; do not wait for agencies

- Use the already curated **private** original/derived SLDC 2019–2026 source archive and its locked original+uncompressed hashes; validate annual/day-of-FY definitions and qualified daily target semantics. Restrict publication of row-level source data until source rights reviewed. Cross-compare with Economic Review's **distinct** consumer-side series without forcing a reconciliation.
- **Outreach, user-approved only:** send the existing SLDC/KSEBL interval load + actual interchange request, including the 11 missing FY2024–25 report days. Request the CSTEP/CEA FY2016/FY2024–25 existing underlying demand datasets if practicable; no outcome assumed.
- Preserve the **already verified 20 FY2024–25 location-quarter ERA5 source slots** separately. Five FY2020–21 through FY2024–25 periods at five points × four quarters imply **100 location-quarter source slots total** for full planned analyses, of which 20 are already reported verified in the earlier FY2024–25 QA: **80 additional slots as a nominal plan**, subject to verified overlap, quotas and source retention. This is a **request-plan count**, not a claim of acquisition or 80 files; ZIPs may contain multiple components and cost caps may require monthly splits.
- Pilot **one** pre-2024 financial year before scaling. Hash original response bytes; verify the exact location selection, units, provider data identity, full UTC hours and IST-day semantics; recorded accumulated radiation/precipitation conversion must have an independent conservation check. UTC HH:00 instants correspond to IST HH:30: local calendar assignment alone does not prove correctly integrated IST-day accumulated flux. Boundary-hour/previous-day requirements must be resolved **before** comparing with daily targets. A complete local date must have 24 point-hours at all five points, with explicit temporal support.
- Failed download, one-point missingness, inaccessible originals, unverified transformed Parquet, or incompatible units **fail closed**. Do not treat CI's synthetically tested normalized-panel gate as original-source authentication.
- **Milestones:** December bounded-year pilot; January scalable reproducible acquisition; February first independently reverified additional period; **31 March** frozen coverage roster; April source accounting closeout.
- **G1:** a manifest of PASS / FAILED / NOT_OBTAINED by source, study date and five-point coverage, with immutable digests and explicit licensing. Missing hourly *load* does not block the *daily* paper, but it blocks observed hourly peaks and operating adequacy claims.

### WP2 — 110 hours, January–July; one carefully compared experiment

- Study the observed, qualified SLDC daily **MU/day** target. There is **no** substitution of annual sales, reconstructed hourly model output, daily Grid-India values or SRPC actual interchange into that field.
- **Primary designed folds:** expanding-origin train dates strictly before **FY2022–23**, **FY2023–24** and **FY2024–25** tests. All full-year claims require exact five-point hourly provenance for training and evaluation days, source revisions logged, and qualified observed daily targets. Unobserved SLDC days remain missing. Explicitly declare the FY2024–25 evaluation exposed to prior inspections. Do not choose years by favourable results.
- **Falsifiable primary contrast:** StandardScaler + Ridge(alpha=1) calendar-only versus the same fixed learner with weather features. Baselines include a predeclared seasonal/lag-naive variant computed using **only accessible earlier observed days**, not nonexistent values on missing days. Use identical qualified test dates and target scope for paired comparison. Complex models (XGBoost/LightGBM and Optuna) are subordinate post-hoc robustness only after the registered fixed comparison succeeds.
- Primary outcomes: **per-fiscal-year RMSE and MAE (MU/day)** plus predeclared signed weather-added RMSE skill. Secondary: training-only defined MASE scale, high-demand-date error, year-to-year spread, month/monsoon stratification, residual dependence and point-weighting sensitivity. A block bootstrap is only a sensitivity device when dependence/block selection is defensible; three FY test groups do not justify precise independent-year confidence bounds.
- No target leakage; no same-day weather sold as day-ahead information. SHAP is description, not causal identification. Record worst-year and **all negative** month/year results. If after time-split evaluation no weather signal remains, that is still a publishable *negative* analytical finding.
- **March 31 G2a:** if a complete original multi-year weather chain for predeclared cross-year folds is unavailable, **stop spending WP2 hours on ML tuning**; pivot Paper A to the descriptive/source-quality manuscript, preserving a source-gated runnable appendix. A partial opportunistic fold cannot be presented as a successful multi-year replication.
- **June 30 G2b:** if eligible data exist, the registered table, reproducible Ridge baseline, per-year errors, leakage tests and uncertainty ledger must be complete. July is independent re-run, error analysis and figure lock, not open-ended model search.

### WP3 — 35 hours, May–August; documentary test before computation

- One priority mechanism: **Idukki/plant-cluster hydro timing versus dependency on dependable imports**. Build a dated station/source constraint ledger: capacity/nameplate, unit count, cascade boundaries, measured daily hydro MWh, usable reservoir storage, inflow/release, routing, irrigation/environmental commitments, availability and ramping *only where independently established*. Unknown means unknown.
- Separate three levels: (1) original/fixed energy schedule, (2) *optimistic* energy-conserving timing upper bound, and **only if verified station/storage bounds exist** (3) physically constrained opportunity estimate. The third cannot be simulated and called admissible just because a config entry exists.
- Existing 4,455 MW ATC remains a dated planning benchmark for scenario sensitivity, *not* proof that this MW was continuously deliverable. Preserve distinction between scheduled drawal, actual exchange and load. No new AC/N-1 project-cost conclusions.
- **June 30 G3:** decision memo whether primary evidence supports a constrained numerical extension. If NO: archive a hydro data-gap/optimistic-bound technical note and redeploy remaining model hours to Paper A/source evidence. If YES: permit one limited source-backed mechanism; preserve identical inputs and independent water/energy balance invariants.
- A second journal manuscript does **not** enter the year-one acceptance criteria.

### WP4 — maximum 20 hours, July–September; hard gate

- Only when G1, G2 and G3 provide reliable enough inputs: register one small, matched paired comparison of hydro availability or import derating (e.g. fixed vs capacity-constrained hydro timing at the same daily MWh and demand chronology). At most **three credible factor families**, with provenance, source-supported ranges and a single robustness table. Begin with simple deterministic bounds; no obligation to run expensive Morris, Sobol or Monte Carlo.
- Reject outputs that do not conserve energy/water, have source-unsupported transfer ceilings, reclassify proxy load as measured, fail solver checks, or imply observed outage probabilities. If no credible setup, **zero** WP4 modelling hours should be spent.
- **G4 31 August:** conditional opportunity report or signed no-go decision, never a fabricated 2040 optimum. Unused hours move to WP1/WP2/WP5 with dated rationale.

### WP5 — 110 hours distributed through the year, concentrated August–October

**Primary Paper A (single protected deliverable), provisional title:** *Weather-sensitive electricity consumption in Kerala: a source-audited multi-year retrospective evaluation*.

**Fallback Paper A0 if weather cannot be admitted:** *Public-data quality, operational boundary definitions and historical electricity-balance accounting for Kerala: a reproducible audit*. This alternative must not imply an unperformed multi-year weather test; article suitability depends on actual novelty/complete evidence.

- **30 Nov:** one-page problem and planned evidence claim; responsible authorship and affiliations only.
- **31 Jan:** paper outline, 25–35 paper matrix, preregistered tests and statistical analysis plan.
- **30 Apr:** Methods and data-dictionary sections drafted, with sources/reproducibility and missing-data flow.
- **30 Jun:** registered results and tables *or explicit source-blocker result*; choose the A or A0 title and scope without post-hoc cherry-picking.
- **31 Jul:** reproducibility-ready figures, provisional results/discussion and chosen journal/outlet shortlist. Do not commit to a venue without checking the real fit, fees and rights.
- **31 Aug:** complete manuscript **v1**, references, supplementary methods, provenance table and uncertainty/limitations; **new-model/new-source claim admission cutoff**.
- **30 Sep:** independent clean-environment replication; request structured critique from at least one methods expert and one Kerala operational/source expert if reachable. Log what feedback was and was not actually received.
- **26 Oct:** research bundle frozen: DOI/preprint if permissible and appropriate, source-restriction-aware reproducibility kit, release manifests, immutable Git tags, website evidence refresh, paper submission when scientifically ready, and a next-study limitations backlog.

Maintain a narrow public-facing site: **observe → validate → conditional mechanism → uncertainty → source limits**, with no promotion of old proxy-stress numbers. Do not build a new dashboard unless it is required to inspect reproducibility.

## 6. Month-by-month execution contract and earned milestones

This is **400 planned focused hours** over twelve months. Each line's effort is the sum of WP0–WP5, and the WP columns sum exactly to the package ceilings. The machine-readable [monthly budget and gate ledger](RESEARCH_PROGRAMME_2026_2027_BUDGET.json) is checked to sum to **400 hours**, including the work-package ceilings; keep document and JSON in sync when changing hours. Work not justified by a passing upstream gate is reassigned after documented review; do not retrospectively relabel the hours already worked.

| Month (2026–27) | WP0 | WP1 | WP2 | WP3 | WP4 | WP5 | Hours | Monthly deliverable / gate |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| **Nov 2026** | 22 | 8 | 0 | 0 | 0 | 2 | **32** | Review charter, RQs, paper evidence matrix, QA protocol; prepare agency outreach; one-page Paper A sketch |
| **Dec 2026** | 9 | 18 | 0 | 0 | 0 | 3 | **30** | Hash/rights/source boundary audit; one extra-year ERA5 pilot or documented blocked attempt |
| **Jan 2027** | 4 | 24 | 6 | 0 | 0 | 2 | **36** | Register splits/hypotheses; source windows reproducible; normalization and integrity pipeline locked |
| **Feb 2027** | 0 | 22 | 10 | 0 | 0 | 2 | **34** | Independently audit one new source period; build matched qualified-date map and baseline test harness |
| **Mar 2027** | 0 | 12 | 20 | 0 | 0 | 4 | **36** | **31 Mar: GO/NO-GO A vs A0**; full weather provenance if possible, otherwise non-weather source audit |
| **Apr 2027** | 0 | 6 | 20 | 0 | 0 | 8 | **34** | Full registered Ridge holdout work (if eligible); Methods + data definition draft |
| **May 2027** | 0 | 0 | 22 | 4 | 0 | 6 | **32** | Baselines and error tables; station-source ledger first pass; Figures 1–2 |
| **Jun 2027** | 0 | 0 | 20 | 6 | 0 | 6 | **32** | **30 Jun:** freeze Paper A/A0 results; hydro physical-constraint gate; draft Results |
| **Jul 2027** | 0 | 0 | 12 | 12 | 4 | 6 | **34** | Independent model rerun, registered uncertainty, hydro feasibility check; first full figures |
| **Aug 2027** | 0 | 0 | 0 | 13 | 10 | 11 | **34** | **31 Aug:** complete paper v1; final admissible model/source results; external comparator audit |
| **Sep 2027** | 0 | 0 | 0 | 0 | 6 | 26 | **32** | Critique, clean-room replication, negative results, copy review and figure/source audit |
| **Oct 1–26 2027** | 0 | 0 | 0 | 0 | 0 | 34 | **34** | Complete publication/release package, tag provenance, site lock, **26 Oct freeze** |
| **Total** | **35** | **90** | **110** | **35** | **20** | **110** | **400** | |

This is a **capacity ceiling**, not a factual estimate that every source request takes a fixed number of hours. Large API waits, meetings and background execution are counted by actual researcher attention, not wall-clock task duration. If publication reviewers or CDS quotas consume the contingency, update the monthly ledger and reduce scope.

### Every active week's operating rhythm (8 planned + 2 uncommitted hours)

- **2 hours**: primary research literature/protocol/source reading and provenance.
- **2 hours**: original data intake, numerical verification or tests.
- **2 hours**: single current technical critical-path task (model comparison only after source admission).
- **2 hours**: written research artefact, figures, reproduction and weekly evidence log.
- **2 hours held free**: job interviews, job search, unexpected source/coding failures or rest. Do not count those as promised technical output.

Weekly exit: one verifiable commit, signed research log, documented externally blocked action, or manuscript improvement — **not** a quota for more code or PRs. Review at most once per month against hours actually spent, evidence delivered, uncertainty reduced and paper-readiness; stop technical branches which do not meet the next gate.

### Two planned decision forks — no scope inflation

**31 March 2027: source G2a.**
- GO: source-hash-verified complete planned multi-FY ERA5 × qualified SLDC dates → fixed Ridge across registered FY folds, then later robust ML if justified.
- NO-GO: change Paper A into **Paper A0**, a source/missingness/consumption-boundary descriptive methods article. Preserve old one-year weather findings as historical evidence only; do not claim multi-year replication, and reassign future WP2 hours to primary-source accounting, year-stratified descriptive analysis and manuscript methods.

**30 June 2027: hydro G3 and bounded-scenario G4.**
- GO: independently sourced physical operating limits and valid hourly inputs permit one controlled model mechanism (no guaranteed positive effect).
- NO-GO: cease additional physical hydro/2040 optimisation development. Of the **55 WP3+WP4 hours**, **10 WP3 hours are scheduled by June**; redeploy the remaining **25 WP3 + 20 WP4 = 45 hours** (if still unspent) as **+10 WP1**, **+15 WP2**, **+20 WP5**. A purely illustrative physical-feasibility note may be retained but not presented as a validated second article.

**Alternate allocation after this June NO-GO** (if the scheduled first 10 hours of WP3 have actually been spent): WP0 35 + WP1 100 + WP2 125 + WP3 10 + WP4 0 + WP5 130 = **400 hours**, with an updated month-hour ledger preserving the total. This is a scenario budget, not a retroactive revision to recorded time.

## 7. Risk-adjusted scientific return, publication ladder and progress board

**Planning judgment, not a measured economic ROI:** compare tasks using (1) evidence gap eliminated, (2) falsifiable research question served, (3) eligibility for Paper A, (4) access uncertainty, (5) hours to verified result and (6) engineering/job-portfolio demonstrability. The strongest return per hour is original-data and original-weather QA feeding a paper; a novel solver without measured hourly load contributes almost nothing to a defensible 2040 conclusion.

| Rank | Default next-best investment | Why | Kill/pivot condition |
|---|---|---|---|
| **1** | Authenticated daily SLDC/source boundary ledger and original ERA5 pilot | Unblocks primary study and prevents false operational claims | Access/rights refused → publish missingness and source QA |
| **2** | Register and reproduce fixed multi-year Ridge contrasts | Directly tests the existing one-year weather story with simple, falsifiable statistics | Missing complete historic weather → switch to A0 source-audit paper |
| **3** | Manuscript-first drafting and clean re-run | Converts code into coherent evidence, criticism and a citable outcome | No defensible results → keep methods/null claims, not a fabricated signal |
| **4** | Single hydro/transfer physical-evidence audit | Closest physical mechanism to existing research question | No source-backed operating constraints by June → stop |
| **5** | One small paired scenario/uncertainty test | Useful only after observed/data-model gates | Source/physical gate fails → no runs |
| **6** | New UI, model families, all-Kerala optimisation, fine-grained district network | Likely low return in this budget | Defer entirely until after 2027 freeze |

**Paper A acceptance ladder:**
1. **Mandatory by Jan:** preregistered question + reference inventory + frozen source boundaries.
2. **Mandatory by Mar:** binary weather-source evidence gate recorded publicly; choose A or A0.
3. **Mandatory by Jun:** repeatable result tables with all null/negative outcomes; no asserted multi-year skill without original input verification.
4. **Mandatory by Aug:** complete manuscript v1 and supplementary reproducibility files; identify at least two candidate publication outlets and their data/fee constraints.
5. **Mandatory by Sep:** external-review attempt and independent computer-level replication. Unavailable reviewers must be disclosed, not falsely claimed.
6. **Mandatory by Oct:** release and research-freeze tag; journal/preprint submission only when defensible and permitted. **Peer-reviewed acceptance and external agency responses cannot be guaranteed**.

**Tracking board states:** \`backlog\`, \`source-blocked\`, \`ready\`, \`in-review\`, \`verified\`, \`rejected\`, \`frozen\`. Every ticket should have an evidence source, estimated focused hours, verification result, manuscript figure/table or claim it unlocks, and a stop condition. Limit **active work in progress to two tasks**: one evidence/analysis task and one writing/reproducibility task.

**Freeze checklist:** 2026 public-claim snapshot retained; all new sources have rights/boundary/hash; paper artifact has traceable per-year test results and failures; original and processed provenance separated; no leakage of restricted data; documented model conservation tests; every chart caption labels observed/proxy/simulation; no 2040 least-cost, real-world LOLE, outage attribution or legally buildable MW asserted without independent validation; clean installation and rerun; website and repository pinned to the same reviewed evidence commit; final tag dated 26 October 2027.


## 8. Verification, claims, ethics and shutdown rules

**Sources and provenance:** immutable hashes of original raw bytes, edition and revision time, retrieval UTC, spatial/temporal boundary, units, licence, code commit, variable transform and independent quality flags. Restricted original inputs stay private and never leak via CI logs or website.

**Statistical:** use only qualified observed targets; predeclare time splits; reproduce baselines; no within-period leakage, future revision leakage or imputed ground truth; report changes including negative/null folds, error distribution and test-period exposures.

**Power/water:** check signed energy, power × duration, reservoir/inflow/release conservation, capacity/availability, transfer direction/constraints, simultaneous hydro and thermal output, and optimisation solver residuals. Storage shifts energy with losses and does not create it.

**Scenario and causality:** the case must state factual observables, model assumptions and counterfactual mechanism. Do not use terms 'identified cause', 'validated reliability', 'prevents load shedding' or 'least cost' without independently suitable evidence. Published benchmarks can challenge but do not automatically validate the new model.

**Stopping rules:** if two successive quarterly gates fail for unavailable original measurements, retire the corresponding calibrated objective and keep a labelled bounded methods study; if by 30 June 2027 no admissible new historical hourly material and no source-supported hydro constraints exist, stop new 2040 optimization runs entirely. If WP2 gets no adequate multiyear weather, publish a source-completeness audit plus multiyear *non-weather* observed SLDC descriptive study, not fake weather generalization.

**Public release minimum, irrespective of access:** provenance/evidence-atlas update, methodology note, at least one reproducible descriptive result built on admissible observation, quantitative missingness and uncertainty, and published negative results where encountered. Full planning adequacy and exact investment recommendations are optional and likely out of scope.

## 9. Confirmed inputs and open authorizations

**Confirmed 26 October 2026:** the research owner can sustainably allocate **10 hours/week**. The optimized **400 planned + 100 contingency** annual resource ceiling is adopted as the working planning assumption in this **draft**.

**Default working choices, pending later review:** prioritize a single peer-reviewable Paper A and an accurate reproducibility-oriented website; use **Kerala statewide daily SLDC operating data** as the central study boundary. District-level electricity demand and new network expansion are not admitted without independently verified records. Paper A's venue will be chosen against actual fit after early results; journal acceptance is not an output guarantee.

**Still requiring explicit user choice or separate permission:**
1. Authorize the existing SLDC/KSEBL data-access email to be **sent** (draft alone grants no permission); decide whether to approach an academic referee or institutional collaborator.
2. Confirm whether the private \`kerala2040-source-archive\` and original Copernicus files can be securely accessed for local source-byte verification and whether an independent reviewer can audit restricted evidence without redistribution.
3. Decide whether to invite an academic coauthor for manuscript review or keep independent authorship. Never imply an affiliation or endorsement that is not real.
4. Choose a journal/preprint versus solely archived report after Paper A evidence and data-rights review. No pay-to-publish commitment is presumed.

**Governance:** approving this 10-hour budget does not authorize sending emails, publication of private data, unlocking blocked claims, changing the October 2026 website freeze, or merging this planning PR. Keep this charter in draft until the outstanding authorizations are resolved.
