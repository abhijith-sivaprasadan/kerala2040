# Scientific claims audit

**Audit date:** 28 September 2026  
**Scope:** headline and supporting claims currently present in Kerala2040.

This document is intentionally conservative. A result can be numerically correct and still receive AMBER status if the public wording could overstate what the evidence supports.

## Summary matrix

| ID | Domain | Claim | Validation class | Independence | Status |
|---|---|---|---|---|---|
| H01 | historical | FY2020–21 → FY2024–25 broad consumption rose 22,540.32 → 29,311.76 MU | S1 | independent official annual source | GREEN |
| H02 | historical | SLDC daily consumption increased ~24.1% on 356 matched dates FY20–21 → FY25–26 | S1/S2 | same SLDC reporting family | GREEN |
| H03 | historical | FY24–25 has 354 qualified SLDC daily records and 11 missing | S1/S2 | source-archive audit | GREEN |
| H04 | historical | internal generation + net imports ≈ consumption | S2 | not independent | GREEN as accounting QA only |
| D01 | demand | released v2 is an 8,760-hour reconstruction, not telemetry | S1/S2/S3 | n/a | GREEN |
| D02 | demand | Jan–Mar extrema holdout: ERA5 shape RMSE 155.2 MW vs static 162.0 MW | S5 | conditional on observed daily energy | GREEN with qualification |
| D03 | demand | reconstructed peak 5923.3 MW is close to CEA 5904 MW | S1/S2 | external aggregate but peak may be calibration anchor | AMBER |
| D04 | demand | weather coefficients are causal demand elasticities | none | none | RED |
| R01 | renewable | five-site ERA5 PV/wind profiles provide usable screening chronology | S2/S3 + plausibility | partial | AMBER |
| R02 | renewable | NIWE validates the wind annual mean | circular | low | RED |
| R03 | renewable | capacity envelopes are legal/buildable Kerala MW | none | no | RED |
| G01 | generation | generator census boundaries reconcile official capacity definitions | S1/S2 | multiple official source families | GREEN |
| A01 | adequacy | chronological timing can produce spill and shortage in the same year | S2/S3 model result | model-internal | GREEN as model behavior |
| A02 | adequacy | current ATC reference is 4455 MW at 31-Mar-2026 | S1 | official CEA | GREEN |
| A03 | adequacy | 80%/60% ATC cases are observed conditions | none; synthetic | no | RED |
| A04 | adequacy | 80%/60% ATC cases are transparent transfer-stress sensitivities | S3 | n/a | GREEN |
| E01 | economics | import price cases represent distinct price/accounting boundaries | S1 | multiple sources | GREEN |
| E02 | economics | v1.0 is a total-system least-cost plan | none | no | RED |
| E03 | economics | lexicographic adequacy-first avoids inventing VOLL | methodological | n/a | GREEN |
| HYO1 | hydro | v1.1 same-day hydro reshaping substantially reduces shortage in some cases | S3 model sensitivity | model-internal | GREEN as sensitivity |
| HYO2 | hydro | v1.2 longer timing windows show flexibility cannot solve deep transfer deficits | S3 | model-internal | GREEN as sensitivity |
| HYO3 | hydro | v1.3 historical storage closure validates hydrology | circular S2 | no | RED |
| HYO4 | hydro | v1.3 is a stateful pilot under reconstructed net-water-balance forcing | S2/S3 | n/a | GREEN |
| HYO5 | hydro | Phase 4 rainfall–inflow model is a forecast | none | no | RED |
| HYO6 | hydro | Phase 4 37.24% MAE improvement is a retrospective held-out diagnostic | S5 on complete cases | partial | GREEN with qualification |
| HYO7 | hydro | Phase 5 Idukki catchment is validated | none | no | RED |
| N01 | network | public 110-kV+ topology is source-backed | S1/S3 | public KSEBL evidence | GREEN |
| N02 | network | 21 lines overload in all eight boundary-allocation cases under screening model | S3 | within model | GREEN |
| N03 | network | those 21 are proven current operator congestion | none | no | RED |
| N04 | network | Shornur is a geographic transmission hotspot | S3 + S6 | independently corroborated by CEA | GREEN |
| N05 | network | current Shornur station capacity is 100 MVA | stale source | contradicted by newer CEA | RED |
| N06 | network | model proves N-1/voltage/transient stability | none | no | RED |
| X01 | solver | PyPSA/SciPy/OSeMOSYS agreement reduces implementation-risk | S4 | shared assumptions | GREEN |
| X02 | solver | cross-solver agreement validates physical reality | none | no | RED |
| GIS1 | ecology | current GIS work establishes statutory buildable MW | none | no | RED |
| GIS2 | ecology | GIS work identifies source/geometry gaps and constrains future siting workflow | S1/S3 | multiple layers | GREEN |
| F01 | flexibility | WP6 examples show mechanisms that can shift load while preserving authored service | S2/S3 | synthetic | GREEN as demonstration |
| F02 | flexibility | WP6 gives statewide achievable peak reduction | none | no | RED |
| T01 | total energy | historical fuel/final-energy data provide wider context | S1 | dated historical sources | GREEN with vintage |
| C01 | KMML | qualitative process topology / historical recovery leads are documented | S1 | source-backed qualitative | GREEN |
| C02 | KMML | current plant mass-energy-water savings are quantified | none | no | RED |
| K01 | context | CIAL 50 MW RE + daytime export + BESS-underway statement | S1/S6 | CIAL first-party | GREEN |
| K02 | context | Kochi Water Metro 17 MWp is installed capacity | contradicted by source | no | RED |
| K03 | context | 17 MWp is an envisaged amount that “can power” KWML needs | S1 | KWML annual report | GREEN |
| B01 | budget | ₹1,156.76 crore 2025–26 power-sector outlay | S1 | Kerala Budget | GREEN |
| B02 | budget | ₹180/₹573 crore are completed Manjappara/Mudirapuzha costs | wrong stage | no | RED |
| B03 | budget | ₹180/₹573 crore are early project estimates in PSP planning | S1 | official/regulatory project material | GREEN |
| Q01 | synthesis | system stress likely reflects interacting timing/import/hydro/network vulnerabilities | synthesis | multiple independent/partly modeled strands | AMBER / defensible hypothesis |
| Q02 | event | Kerala2040 proves exact cause of a specific 2026 load-shedding episode | no event dataset | no | RED |
| Q03 | solution | storage/hydro scheduling/DR/grid reinforcement are an optimized solution portfolio | no | no | RED |
| Q04 | solution | they are candidate responses motivated by screening mechanisms | synthesis | bounded | GREEN |

---

## H — Historical electricity and accounting

### H01 — Official broad consumption trend

**Claim:** broad electricity consumption increases from 22,540.32 MU in FY2020–21 to 29,311.76 MU in FY2024–25.

**Evidence:** Kerala State Planning Board / Economic Review annual series.

**Audit:** source values are independent of the Kerala2040 model. They should be labelled by the official accounting boundary.

**Status:** **GREEN.**

**Conference-safe explanation:**  
“This is the state's published annual series. I use it to establish the long-run direction, not as an hourly model input.”

### H02 — Matched-date SLDC growth

The ~24.1% matched-date increase is a valid descriptive statistic because dates are matched before comparison. It avoids bias from comparing different missing-date patterns.

It is not a causal growth model and does not isolate weather/economy/population.

**Status:** **GREEN descriptive.**

### H03 — 354/365 observed FY2024–25 days

This count is source-audited and missing dates are explicit.

The 11 missing dates must never be described as observed after interpolation.

**Status:** **GREEN.**

### H04 — Daily energy balance identity

Correct for QA, but not independent validation.

**Status:** **GREEN as S2 only.**

---

## D — Demand chronology and ERA5

### D01 — 8,760-hour chronology

The chronology is explicitly reconstructed. Exact daily-energy conservation is desirable because the reliable daily source is retained while only the within-day shape is modeled.

**Status:** **GREEN if always called a proxy/reconstruction.**

### D02 — Held-out extrema

The reported improvement from static shape to ERA5-sensitive shape is scientifically meaningful but narrower than a forecasting result.

Key point: daily energy is known on the held-out days.

**Status:** **GREEN with the phrase “held-out intraday-shape reconstruction conditional on daily energy.”**

### D03 — annual peak agreement

If the CEA peak is part of the calibration objective/constraints, agreement to that same number cannot be treated as independent validation.

Use it as a consistency/calibration check.

**Status:** **AMBER.**

### D04 — weather coefficients

Because the proxy is daily-normalized and predictors covary with clock time/season and behavior, coefficients are not causal elasticities.

**Status:** **RED as causal claim.**

---

## G/R — Fleet and renewable resource

### G01 — installed fleet

The census work is strongest where technology/date/size thresholds are explicitly reconciled. The CEA convention that reports small solar separately must not be mistaken for omission.

**Status:** **GREEN for capacity accounting, subject to stated dates.**

### R01 — five-site profile

Five representative ERA5 cells cannot represent the true capacity-weighted Kerala fleet. Equal weighting is a transparent approximation chosen because candidate spatial weights were not admitted.

**Status:** **AMBER screening input.**

### R02 — wind NIWE anchor

The profile's mean wind is forced to NIWE. NIWE cannot independently validate the resulting mean.

**Status:** **RED if phrased as validation.**

### R03 — renewable capacity envelope

The low/reference/high caps are study-derived scenario envelopes. They deliberately fail the legal/ecological/site/hosting-capacity gate.

**Status:** **GREEN as scenario caps; RED as “buildable potential.”**

---

## A/E — Adequacy and economics

### A01 — spill and shortage coexist

This is a valid inference about the model's chronology: annual renewable energy availability is not sufficient to guarantee supply at stressed hours.

It is not proof that identical physical spill/shortage quantities will occur in Kerala.

**Status:** **GREEN as screening inference.**

### A02 — 4,455 MW ATC

Current CEA transmission planning evidence reports TTC 4,575 MW and ATC 4,455 MW at the dated 31 March 2026 snapshot.

The model uses 4,455 only as a reference bound, not an annual guarantee.

**Status:** **GREEN.**

### A03/A04 — transfer haircut cases

80% and 60% are authored stress cases.

Their value is sensitivity: if a conclusion appears only at one arbitrary haircut, it is fragile; if the direction persists, it is more informative.

**Status:** **GREEN as sensitivities, RED as observations.**

### E01 — import prices

The cases intentionally span:

- annual KSEBL procurement accounting;
- wholesale IEX DAM;
- a downstream high delivered-cost example.

They are not a time series of the same border price.

**Status:** **GREEN if boundaries remain explicit.**

### E02 — total-system cost

Existing generation is replayed/unpriced and many costs are absent; therefore the model is not total-system least cost.

**Status:** **RED.**

### E03 — lexicographic objective

Solving adequacy before cost is a defensible choice because an arbitrary value of lost load would otherwise determine the trade-off.

This does mean the optimization is not a welfare/economic-dispatch solution.

**Status:** **GREEN methodology.**

---

## HYO — Hydro and Idukki

### HYO1 — daily flexibility

The 96.87% reduction in one reference case is a valid sensitivity result under the stated constraints.

Do not generalize the percentage to real Kerala operation.

**Status:** **GREEN as model sensitivity.**

### HYO2 — longer windows

The direction is robust within the model: temporal flexibility is most valuable where the underlying energy/transfer balance is not deeply deficient.

**Status:** **GREEN as screening inference.**

### HYO3/HYO4 — v1.3

Historical storage replay closure is algebraic. See circularity audit.

The stateful optimization remains useful because it imposes a stock constraint instead of treating hydro as unconstrained hourly energy.

**Status:** **GREEN as stateful pilot; RED as hydrological validation.**

### HYO5/HYO6 — Phase 4

The 37.24% held-out MAE reduction is valid on the exact complete-case retrospective test population. Same-day rain prevents calling it a one-day-ahead forecast.

**Status:** **GREEN with qualification.**

### HYO7 — Phase 5 catchment

The catchment gate remains closed. This is scientifically preferable to accepting a geometry merely because its area looks plausible.

**Status:** **RED for “validated catchment”; GREEN for fail-closed methodology.**

---

## N — Transmission

### N01 — topology

Public KSEBL grid map / SLD evidence supports the physical 110-kV+ topology at screening level.

**Status:** **GREEN structural.**

### N02 — 21 robust lines

This is reproducible model output under eight boundary-allocation cases.

**Status:** **GREEN within the screening definition.**

### N03 — operator congestion

The model lacks measured bus loads, measured generator dispatch, calibrated impedances, current complete station configuration, reactive power and N-1 operation.

**Status:** **RED.**

### N04 — Shornur hotspot

The geographic signal is independently strengthened by CEA's current transmission plan, which separately identifies Shoranur and multiple nearby corridors as constraints/reinforcement targets.

**Status:** **GREEN geographic screening conclusion.**

### N05 — 100 MVA current capacity

The current CEA source supersedes the old 2023 interpretation for present station configuration.

**Status:** **RED current-capacity claim.**

### N06 — “grid stability”

Do not use the network screen as evidence of frequency stability, rotor-angle stability, small-signal stability, voltage stability or transient stability.

**Status:** **RED.**

Use **network stress / congestion / deliverability screening** instead.

---

## X — Cross-framework checks

### X01/X02

Agreement across implementations is useful scientific software verification. It helps answer “is this just a PyPSA quirk?”

It does not answer “are the assumptions true?”

**Status:** **GREEN S4 / RED physical-validation claim.**

---

## GIS — Ecology, terrain and siting

### GIS1

No legal buildable-MW result is supported.

**Status:** **RED.**

### GIS2

The work successfully identifies:

- official geometry where available;
- invalid geometry;
- missing districts/layers;
- unresolved statutory boundaries;
- terrain/resource overlap questions.

That is meaningful evidence acquisition/QA.

**Status:** **GREEN.**

---

## F — WP6 flexibility

The pilots are deliberately synthetic.

Good claims:

- a scheduling algorithm can conserve the authored service while moving load;
- storage losses and stock constraints can be made explicit;
- thermal storage can trade electricity timing against thermal comfort/storage state.

Bad claims:

- “Kerala can save X MW with this intervention.”

**Status:** **GREEN mechanism demonstration; RED statewide impact.**

---

## T/C — wider energy and industry

### T01 — Total Energy Atlas

Historical final-energy/fuels/emissions datasets add context but have different years and units. They should not be merged into one current Sankey without an explicit reconciliation model.

**Status:** **GREEN as historical context.**

### C01/C02 — KMML

Qualitative process topology and historical recovery opportunities are source-supported.

Current measured mass/energy/water balances and quantified savings are not available.

**Status:** **GREEN qualitative / RED quantitative savings.**

---

## K/B — Kerala examples and budgets

### K01 — CIAL

First-party CIAL reporting says total installed renewable capacity is 50 MW, daytime excess solar is supplied to the grid, and a BESS project for nighttime solar use is underway.

**Status:** **GREEN as a case study.**

It is not evidence about statewide causal mechanisms.

### K02/K03 — Water Metro

KWML's FY2023–24 annual report says terminal roofs/pontoons are designed for PV and that **17 MWp “can power” the entire energy needs**, while land-based solar steps were still in process.

Therefore 17 MWp is an envisaged requirement/concept, not installed capacity.

**Status:** **GREEN only with future/envisaged wording.**

### B01 — state power budget

Kerala's 2025–26 Budget in Brief reports ₹1,156.76 crore under Power. The Budget Speech also states ₹100 crore additional for pumped/storage schemes and ₹1,088.80 crore KSEBL outlay.

**Status:** **GREEN.**

### B02/B03 — Manjappara/Mudirapuzha

The ₹180 crore / ₹573 crore figures are planning-stage estimates, not completed EPC costs.

**Status:** **GREEN as estimates; RED as actual costs.**

---

## Q — Overall synthesis

### Q01

The project's central synthesis is a multi-factor hypothesis:

> demand timing + weather + hydro flexibility + external transfer + internal deliverability interact to create vulnerability.

This is supported by a combination of observations, source-backed facts, sensitivities and independent transmission-plan corroboration.

It should remain a **synthesis hypothesis**, not an event-causal theorem.

**Status:** **AMBER but defensible.**

### Q02

Exact 2026 event cause is not reconstructed.

**Status:** **RED.**

### Q03/Q04

Solutions are candidate response classes, not an optimized portfolio.

**Status:** **GREEN as future work, RED as recommendation.**

## Bottom line

The defensible contribution is not:

> “I built a perfect digital twin and solved Kerala's load shedding.”

It is:

> “I assembled and audited fragmented public evidence, reconstructed a bounded chronology, tested several failure mechanisms transparently, found which conclusions survive sensitivity checks, and kept higher-confidence planning claims fail-closed when the required data were not available.”
