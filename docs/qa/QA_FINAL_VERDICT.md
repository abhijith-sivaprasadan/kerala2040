# Final scientific QA verdict — CET 2026 conference release

**Audit completed:** 28 September 2026  
**Audited baseline:** Kerala2040 main after PRs #122 and #123  
**QA branch:** `qa/scientific-validation-conference-20260928`

## Executive verdict

**Kerala2040 is scientifically defensible for CET 2026 as a public-data diagnostic and screening study.**

It is **not** defensible as:

- an operator-grade digital twin;
- a calibrated AC/N-1 security model;
- a probabilistic resource-adequacy certification;
- a causal reconstruction of a specific 2026 load-shedding event;
- a hydrologically validated Kerala reservoir/cascade model;
- a statutory renewable-siting assessment;
- or a least-cost 2040 investment plan.

That distinction is not cosmetic. It is the central conclusion of this QA pass.

The project is strongest when it says:

> **I assembled fragmented public evidence, preserved source boundaries and missingness, reconstructed only what was not observed, tested specific mechanisms and sensitivities, cross-checked implementation across modelling frameworks, and refused to promote results where the physical evidence was insufficient.**

## What survived the audit strongly

### 1. Historical accounting and provenance

The historical electricity work is sound for its stated boundaries:

- annual official consumption trends are independently sourced;
- the SLDC archive retains source dates, sections, missingness and contradictory records;
- FY2024–25 has 354 qualified observed daily records and 11 missing dates;
- different accounting boundaries are not forced into one “correct” annual number;
- daily balance closure is correctly understood as an accounting invariant, not independent validation.

**Verdict: GREEN.**

### 2. Demand chronology

The ERA5-sensitive chronology remains useful, with a narrower and more precise interpretation:

- observed daily energy is conserved exactly on 354 days;
- 11 missing daily totals remain explicitly model-only;
- January–March extrema were held out from coefficient fitting;
- ERA5 improves RMSE from 162.0 MW to 155.2 MW relative to the already strong sparse-static reconstruction;
- the result demonstrates useful **intraday-shape information conditional on known daily energy**.

It is not an hourly forecast and not measured telemetry.

The 5904 MW CEA value used by the proxy is a generation-resource-adequacy planning/calibration reference. The newer CEA transmission plan separately reports 5797 MW as the recorded FY2024–25 peak. Kerala2040 now preserves both source contexts instead of treating them as interchangeable.

**Verdict: AMBER/GREEN for reconstruction; RED for forecast interpretation.**

### 3. Future demand and adequacy sensitivities

Keeping CSTEP, CEA/KSERC and transmission-planning scenarios separate is methodologically stronger than averaging them.

The 8,760-hour adequacy screens defensibly establish that, **within the stated model**:

- chronology matters;
- spill and shortage can coexist;
- transfer capability can dominate adequacy outcomes;
- renewable annual energy alone does not guarantee stressed-hour adequacy;
- candidate limits bind in several reference-demand cases.

The absolute future shortage quantities remain scenario results, not forecasts.

**Verdict: AMBER/GREEN screening evidence.**

### 4. Hydro timing

The v1.1/v1.2 hydro result survived the audit particularly well because it asks a clean counterfactual question.

The same hydro energy, when given more temporal freedom, can substantially reduce modeled shortage in timing-limited cases. That benefit declines when the system is deeply transfer/energy constrained.

The large 96.87% reduction in the reference/full-transfer case is valid **for that sensitivity**, not a claim about achievable real dispatch.

**Verdict: GREEN model sensitivity.**

### 5. Idukki source provenance

The QA independently traced and recomputed the important v1.3 numbers:

- full storage **1460 MCM** is directly present in the retained SLDC Idukki rows;
- reported full capability **2190 MU** gives 1500 MWh/MCM gross;
- the configured **1470 MWh/MCM station equivalent** is reproduced from all 354 source rows as the median of station-generation-capability/effective-storage;
- Idukki HEP **780 MW / six 130 MW units** is independently supported by KSEBL project/rule-level material.

However, the v1.3 historical storage replay closes algebraically because the net-water-balance forcing is reconstructed from the same storage and generation series. That is implementation verification, not hydrological validation.

v1.4/v1.5 correctly exist to break that circularity with direct physical inputs.

**Verdict: GREEN provenance; AMBER physical pilot; RED hydrological-validation claim.**

### 6. Interstate transfer

The current CEA planning source supports:

- TTC **4575 MW**;
- ATC/import capability **4455 MW**.

The 80% and 60% cases are transparent authored stress cases.

The project correctly refuses to infer future ATC from transmission MVA/circuit-km additions or from future import requirements.

**Verdict: GREEN source/reference handling.**

### 7. Cost and finance inputs

Primary-source QA confirms:

- CEA Version 2.0 cost assumptions are explicitly at 2021–22 cost level;
- solar ₹41,000/kW;
- onshore wind ₹60,000/kW;
- four-hour BESS ₹47,200–82,200/kW;
- BESS round-trip efficiency 88%;
- CERC Order 12/SM/2026 supports 70:30 debt/equity, 10.71% loan interest, 14% post-tax RoE for non-small-hydro RE and a 9.08% WACC-equivalent discount factor.

These are correctly implemented as **national research/regulatory benchmarks**, not Kerala project quotes or a Kerala project WACC.

**Verdict: GREEN provenance; AMBER project applicability.**

### 8. Import-price economics

The ₹5.05/kWh KSEBL case is an annual weighted procurement-accounting proxy.

The ₹5.24/kWh IEX case has been corrected in QA documentation to mean the FY2023–24 **average MCP** (~₹5.23759/kWh), not the volume-weighted MCP (~₹5.17449/kWh).

The ₹7.13/kWh case is a downstream delivered-cost stress proxy, not a Kerala-border import tariff.

The economics remain partial because existing fleet costs and several system costs are omitted.

**Verdict: GREEN source-boundary use; AMBER partial economics.**

### 9. Cross-framework checks

PyPSA ↔ SciPy and PyPSA ↔ OSeMOSYS agreement is useful independent-implementation evidence.

It establishes that the result is not simply a framework-specific coding artifact under the common mathematical contract.

It does **not** independently validate the common inputs or physical assumptions.

**Verdict: GREEN S4 verification; RED physical-validation interpretation.**

### 10. Transmission topology and hotspot geography

The source-backed 110-kV+ topology and screening workflow remain scientifically useful.

The 21-line result is reproducible:

> 21 source-rating-backed lines exceed their screening rating in all eight tested boundary-injection allocation cases.

“Robust” applies only to that tested uncertainty dimension.

The QA uncovered the most important correction in the project:

- the network model used a genuine 31 March 2023 KSEBL PSS entry of **100 MVA** at Shornur 220/110 kV;
- the current 2026 CEA plan reports **200 MVA + 100 MVA** existing transformation at Shoranur;
- CEA independently identifies Shoranur as constrained and proposes further reinforcement.

Therefore:

> **Shornur/Shoranur remains a defensible geographic transmission hotspot and gains independent external corroboration, but Kerala2040's 100 MVA transformer overload magnitude is not current whole-station loading.**

This is a correction, not a hidden failure.

**Verdict: GREEN hotspot geography; AMBER line-screen magnitudes; RED current 100-MVA whole-station interpretation.**

### 11. Ecology / GIS

The strongest scientific property of the GIS work is that it fails closed.

Incomplete or legally insufficient layers were not converted into a fake “buildable GW” number.

The present work supports:

- terrain/resource context;
- geometry/source QA;
- identification of missing statutory constraints;
- a future siting workflow.

It does not support statutory project siting.

**Verdict: GREEN evidence/feasibility workflow; RED buildable-MW claim.**

### 12. Flexibility pilots

EV charging, industrial scheduling, BESS, pumped-storage analogue and cooling/TES work remain valid synthetic mechanism demonstrations.

They show that authored service can be conserved while timing changes.

They do not estimate statewide achievable MW.

**Verdict: GREEN educational/mechanism experiments; RED statewide impact claim.**

### 13. Wider context and case studies

CIAL, Kochi Metro, Kochi Water Metro, KMML, Total Energy Atlas and budget comparisons can remain if kept in their supporting role.

QA corrections:

- CIAL 50 MW renewable capacity / daytime export / BESS-under-development wording is first-party supported;
- Kochi Metro 5.389 MWp is a documented project-stage configuration, not necessarily the complete current 2026 total;
- Kochi Water Metro 17 MWp is envisaged/design-stage, not installed;
- KMML quantitative current plant-wide savings are not established;
- budget estimates are stage-labelled and are not evidence of universally cheap/high-quality delivery.

**Verdict: GREEN context with explicit vintage/stage boundaries.**

## What the QA found that must never be hidden

A credible audit should change some claims. This one did.

The material findings were:

1. **Shornur transformer vintage mismatch** — current station interpretation corrected.
2. **v1.3 reservoir closure circularity** — reclassified from any possible physical-validation reading to algebraic implementation verification.
3. **ERA5 demand holdout scope** — narrowed to conditional intraday-shape validation, not forecasting.
4. **ERA5 v2 public reproducibility gap** — original fitter/raw ERA5 archive are not currently in the public repository.
5. **cross-solver interpretation** — implementation equivalence, not physical validation.
6. **network robustness scope** — robust to boundary-injection allocation only.
7. **IEX ₹5.24 statistic** — average MCP, not weighted MCP.
8. **5904 vs 5797 MW peak** — retained as distinct CEA planning/reporting contexts rather than silently reconciled.
9. **Kochi Metro / Water Metro vintage-stage wording** — tightened.
10. **population/per-capita timing** — 2026 population projection is not used to recompute the official FY2024–25 816 kWh/person statistic.

A conference answer should state these corrections plainly if asked.

## Remaining open limitations

There is **one material reproducibility limitation that remains open by design**:

### ERA5-sensitive v2 fitting pipeline

The released 8,760-hour chronology is cryptographically pinned and downstream use is reproducible, but the original v2 fitting script and raw ERA5 archive were not committed in PR #110/#113.

This means the released chronology is integrity-verifiable, but the coefficient fit and holdout metrics cannot currently be regenerated from a fresh public clone.

This does not invalidate the result, but it prevents the claim:

> “Every result is fully reproducible from a fresh clone.”

The correct statement is documented in `REPRODUCIBILITY_AUDIT.md`.

Other known limitations are scientific data gates rather than QA defects:

- no operator-grade continuous interval load/interchange telemetry;
- no calibrated bus-load chronology;
- no AC/N-1 operational network model;
- no complete direct Idukki physical inflow/release/cascade model;
- no legally complete renewable siting stack;
- no probabilistic outage/weather reliability model;
- no total-system least-cost economics.

## Is any additional modelling required before CET 2026?

**No new model family is justified before the conference.**

The next useful scientific improvements require **better evidence**, not another solver:

1. measured state interval load and interchange;
2. current bus injections and complete line/transformer parameters;
3. direct Idukki water-balance observations with a verified catchment;
4. statutory spatial exclusion layers;
5. multi-year stochastic weather/outage data;
6. Kerala/project-specific technology and reinforcement costs.

Adding a more sophisticated optimization before those data arrive would increase apparent precision faster than scientific confidence.

## Conference-safe hierarchy of claims

### Tier 1 — strongest: use normally

- official annual/daily historical trends with stated boundaries;
- 354 observed FY2024–25 SLDC dates / 11 missing;
- current CEA 4455 MW ATC snapshot;
- CEA/CERC cost/finance benchmark provenance;
- source-backed network topology;
- Shoranur geographic constraint corroborated independently by CEA;
- descriptive Kerala population/area/electricity context;
- first-party CIAL/KMRL/KWML facts with correct dates/stages.

### Tier 2 — use with explicit “screening/reconstruction” language

- ERA5-sensitive hourly load;
- future hourly demand morphs;
- renewable resource profiles;
- v0.8 adequacy/expansion results;
- import-cost sensitivity;
- hydro v1.1/v1.2;
- Idukki v1.3;
- 21 robust line-screen signals;
- synthetic flexibility pilots.

### Tier 3 — do not claim

- exact cause of a 2026 restriction event;
- measured hourly accuracy;
- causal weather elasticity;
- validated reservoir hydrology;
- current Shornur 100 MVA whole-station capacity/loading;
- operator congestion;
- voltage/frequency/transient stability;
- N-1 security;
- buildable renewable GW;
- probabilistic LOLP;
- optimal 2040 portfolio;
- statewide MW savings from synthetic pilots.

## Final scientific answer if challenged on the project's validity

> “The project deliberately separates observation, reconstruction, sensitivity and validation. Some results are strong official facts, some are model-screening results, and some proposed solutions are hypotheses. During the final QA I found and corrected several over-strong interpretations, including a stale Shornur transformer capacity, circularity in the v1.3 reservoir replay, the exact scope of the ERA5 holdout and the IEX price statistic. I would rather downgrade a claim than defend a number beyond its evidence. The central conclusion that timing, hydro flexibility, external transfer and internal deliverability all matter remains supported, but I do not claim an operator-grade causal or investment model.”

## Release recommendation

**PASS WITH DISCLOSED LIMITATIONS.**

The project is suitable for conference presentation **provided the QA wording corrections are applied to the public release/poster and the speaker follows the claim hierarchy above**.

No RED claim in `claims_matrix.csv` should appear as a positive conclusion.

The QA branch should remain available as the full scientific audit trail even after selected corrections are promoted to main.
