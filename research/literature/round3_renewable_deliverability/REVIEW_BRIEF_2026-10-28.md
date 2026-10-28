# Kerala2040 Literature Review — Round 3
## Renewable-energy deliverability, distribution-grid hosting capacity, curtailment and storage

**Research record:** 28 October 2026 • **Status:** distinct thematic scoping and publication-source screening, **not** completed full-text appraisal or a new empirical result.  
**Corpus:** 33 candidate records in [SCREENING_MATRIX.csv](SCREENING_MATRIX.csv): 25 peer-reviewed journal candidates and 8 institutional/regulatory comparators. DOI/title and abstracts/pages were screened from publisher, institutional or official online listings; each paper needs original full-text checks. 0/33 are marked fully critically reviewed in this round.  
**Separate from:** Round 1 (demand/weather ML, measurement-boundary accounting, broad modelling/validation) and Round 2 (Kerala hydro/reservoir operation, monsoon and flood-control versus power flexibility). A cross-round **paper-ID** deduplication check with the still-developing Round 2 roster remains open.

### 1. Scope and motivation

This round asks a different question from whether Kerala *could build* renewables: **What evidence would be required to demonstrate that additional solar/wind electricity can reach consumers, when, where and under which physical, operational and regulatory conditions?**

Primary coverage:
1. Distributed and rooftop solar **hosting capacity**: low-/medium-voltage feeder impedance, voltage rise, protection, harmonics, transformer ampacity, reverse flow, customer load and representative chronology.
2. Utility-scale renewable **grid evacuation** and transmission constraints: connection and transfer capacity, modeled network bottlenecks, transmission investment and overbuilding.
3. **Curtailment**: measured dispatch-down instructions versus estimates based on potential output; technical versus commercial/offtake restrictions.
4. **Battery and flexibility mechanisms**: energy/power/duration limits, charge availability, losses, dispatch rules, price or ancillary incentives; compare with network reinforcement and demand flexibility.
5. Distinction between **nameplate MW, simulated renewable potential, source-observed AC generation, metered self-consumption/export, accepted grid injection, settlement energy and delivered load**.

Out of scope: primary hydro reservoir-release, cascade operation and flood-control optimisation (Round 2); ERA5-to-observed daily consumption and fiscal-year prediction tests (Round 1 / Paper A); a new Kerala least-cost 2040 expansion claim; unobserved grid outages or actual AC/N-1 security results from exploratory maps.

### 2. Candidate research questions (for literature appraisal, not a third-paper commitment)

- **R3-Q1 / definition:** Which source boundaries and denominators do published studies use for RE capacity factor, curtailment, hosting capacity and deliverable electricity, and where are incompatible indicators compared?
- **R3-Q2 / physical admissibility:** Which grid observables are necessary to make Kerala feeder or transmission deliverability inferences—actual lines, impedance, ratings, transformer configuration, nodal load/generation, voltage and switching constraints—and which are absent from currently admitted evidence?
- **R3-Q3 / counterfactual design:** Do studies separate the effects of load shifting, dispatch reform, storage placement and line upgrades using **paired, calibrated** alternatives, rather than attributing all changes to one technology?
- **R3-Q4 / transferability:** Which results from Karnataka, Indian southern/interregional models or international feeder benchmarks can be transferred as *methods* to Kerala, versus invalid numerical transplantations?

### 3. Initial critical synthesis — what the verified publisher/institutional material supports

#### A. Resource availability is not grid-delivered renewable electricity

Hunt et al. (R3-003; DOI 10.1002/met.2196) provide an Indian reanalysis-based potential/realized-capacity reconstruction, with open code and a source dataset indicated on the publisher page. Their source is relevant for **weather-to-potential** and *calibrated simulated generation* methods, not proof that every potential MWh is physically injected or dispatched by Kerala.

Motiwala et al. (R3-017) examine poor performance at existing utility-scale Indian PV projects and associated underused evacuation infrastructure. Two opposite risks must be kept separate: insufficient lines can constrain generation; underperforming generation can leave costly lines underused.

**Admissibility rule:** no conversion from solar MW or ERA5 irradiance to a statement such as “Kerala can deliver X GWh” without historical performance, clipping/availability, topology, export/dispatch restrictions and an explicit electricity accounting boundary.

#### B. Curtailment has multiple competing mechanisms

Sambasivam and Xu (R3-002; Karnataka 2017–2019) report a calibrated/validated MILP interpretation of reduced PV curtailment, including irrigation load shifting and dispatch reform. These attributed counterfactual improvements are **not Kerala effect sizes**, and the strength of their empirical identification must be checked against full-paper data and model validation.

A 2026 Ember report (R3-O07) estimates India inter-state curtailment from **modeled generation potential and transfer headroom**; its numbers must not be reclassified as directly metered Kerala curtailment. The new 2026 IEEE Access structured review (R3-023) groups curtailment causes across networks, system operation, markets and demand flexibility; methods/selection criteria still need full-paper reading.

**Admissibility rule:** never label the difference between weather-potential energy and recorded generation as grid-caused curtailment without availability, outages, maintenance, dispatch instructions and plant-level or operator confirmation.

#### C. Transmission can be insufficient or excessive

Venkataramana et al. (R3-001; *Applied Energy* 2025) use a Southern/Western regional 15-minute capacity-expansion and dispatch framework. Their centralised versus regional compliance result is pertinent to questions of pooling, trade, batteries and allocation. A result for a two-region model is **not** empirical evidence of an actual Kerala corridor's rated or secure transfer capacity.

The Indian transmission policy study (R3-004; DOI 10.1016/j.enpol.2023.113437) argues that anticipatory policy and governance can yield **overbuilding** even during renewable expansion. This directly challenges the unsupported presumption that increasing transmission MW is always efficient. NREL's 2017 Greening the Grid (R3-O02), IEA's 2021 India study (R3-O01) and the CEA 2024 transmission plan launch (R3-O03) are policy/model precedents, not direct 2026 Kerala telemetry.

**Admissibility rule:** distinguish installed circuit length, circuit thermal rating, active operating margins, interregional transfer capabilities, actual import schedule and metered net drawal. Do not compute measured Kerala N-1 overload or adequacy probability from uncalibrated public infrastructure sketches.

#### D. Hosting capacity is a definition-dependent physical limit

Koirala et al. (R3-005), de Oliveira et al. (R3-006), Qammar et al. (R3-008), and Mulenga & Etherden (R3-009) emphasise different hosting-capacity definitions, time-series or stochastic uncertainty, and limits from network topology and electrical state. Sahu et al. (R3-014) add harmonics as one potential limiting mechanism, while Rawat et al. (R3-013) analyse coupled EV flexibility. Ramadhani et al. (R3-007) demonstrate detailed city/network-level inputs, but their Swedish feeder values cannot be borrowed for Kerala.

**Admissibility rule:** Kerala rooftop capacity (MW) and household adoption counts are not measured feeder hosting capacity (MW) or evidence of voltage violation. Any Kerala-specific physical result requires corresponding topology, real demand/generation chronology, base voltage and protection/ampacity data. A simplified feeder example may be labelled *illustrative* only.

#### E. Batteries are not free dispatch capacity

R3-012, R3-015 and R3-016 investigate control, uncertainty and mini-grid regulation for PV-plus-storage; R3-001 shows storage interacts with other expansion and regional constraints. Before a Kerala storage counterfactual, record storage power MW, energy MWh, duration h, charging origin, roundtrip losses, reserve margins, dispatch timing and installed versus scenario status.

**Admissibility rule:** do not turn storage energy throughput in GWh/y into battery installation in GWh, nor assume battery storage reduces curtailment if its operation, power rating, charge location or network access is unspecified. For any result, report both scenario base and intervention under matched demand and renewable inputs.

### 4. Why Kerala is a meaningful case, without a premature novelty claim

Kerala's rooftop expansion appears prominently in public planning material: the Kerala State Planning Board's *Kerala Development Report 2026* discusses a high rooftop share in its solar portfolio (R3-O04). This institutional claim is an invitation to **verify the original report's exact date, units, and definitions**, not a source-admitted independent dataset.

KSEB's public E-Kiran guidance (R3-O05) references the 2020 net-metering framework and electricity metering conditions. Meanwhile KSERC's 2025 renewable-energy discussion/draft materials were subject to regulatory and court processes. **Treat R3-O08 only as draft/historical policy material until the operative gazetted provisions, subsequent orders, effective dates and legal status have been checked.** Regulatory text is not a power-flow measurement.

This creates a **possible research gap, not yet an established novel contribution**: reconciling Kerala PV installation and export records with independently source-verified feeder and transmission constraints, separating source-observed deliverability from hypothetical engineering screens.

### 5. Full-paper priority queue — no completed-audit claims

| Rank | Record | Why the original paper matters | Specific falsification / verification task |
| --- | --- | --- | --- |
| 1 | [R3-002, Karnataka curtailment](https://doi.org/10.1016/j.enpol.2022.113334) | Closest Indian observed policy/curtailment example | Locate measured curtailment, validation years, baseline and MILP counterfactual identification |
| 2 | [R3-001, India interregional coordination](https://doi.org/10.1016/j.apenergy.2025.126134) | Regional transfer + storage framework | Inspect 15-min source chronology, transmission abstraction, capacity/energy and spatial pooling |
| 3 | [R3-005, HC benchmark](https://doi.org/10.1016/j.rser.2021.111899) | Clear uncertainty/limit definitions | Extract feeder inputs, operational thresholds and deterministic-vs-stochastic comparison |
| 4 | [R3-006, PV hosting-capacity planning](https://doi.org/10.1016/j.epsr.2024.111138) | Closest operational design method | Document observed network, uncertainty definition, tested voltage/thermal criteria |
| 5 | R3-003, India renewable potential | Open benchmark / renewable proxy | Inspect production validation, grid-cell/plant locations, and observed-versus-derived fields |
| 6 | R3-004, India transmission overbuilding | Critical counterexample | Identify evidence of overinvestment and the policy mechanism; do not generalize numeric cost |
| 7 | R3-013, Indian EV/PV stochastic planning | Demand-side distributed flexibility | Audit network realism, state variables, constraints and independent data |
| 8 | R3-014, power-quality hosting limit | Feeder engineering blind spot | Verify harmonic model and real operating measurements |
| 9 | R3-023, 2026 curtailment review | Definitions and coverage check | Inspect search protocol, inclusions and categories; avoid review-as-primary evidence |
| 10 | R3-016, India VPP + BESS regulations | Regulatory scope and technical interface | Differentiate law, proposal, hypothetical implementation and actual field test |

A paper can be marked **fully critically reviewed** only after inspecting complete source text, methods, data/source tables, figures, limitations and (when claimed) supplement, extracting page-specific evidence and explicitly logging unknowns. Publisher abstract/full article metadata alone remains *screening only*.

### 6. Evidence ledger schema for a later empirical study

**Physical/energy accounting chain** (these are distinct evidence objects):

1. Installed PV or wind **nameplate DC/AC MW**, commissioned date, owner and connection point.
2. Weather-derived **theoretical resource** and model assumptions.
3. Calibrated potential plant **AC generation** and observed generation at an original meter.
4. Prosumer **self-consumption**, gross generation, net export and export meter semantics.
5. Operator **curtailment instruction**, separately measured unrealised output (if possible), maintenance/forced outage.
6. Feeder/transformer **technical limit**: impedance, base voltage, thermal ampacity, harmonics/protection, switch states and time.
7. Transmission **transfer limit** and **actual** interchange (scheduled versus metered separately).
8. Storage **power**, **energy**, state of charge, grid connection, losses and dispatch.
9. Delivered **consumer/system target boundary**: never equate SLDC daily operational consumption with annual consumer-side utility use.

Suggested evidence-grade fields: `source_owner, source_vintage, original_url_or_file_hash, license, period_start/end, timezone, observation_unit, electrical_boundary, observed_vs_modelled, temporal_resolution, spatial_resolution, raw_data_available, independent_QA, analyst_exposure, uncertainty_source`.

### 7. Research integrity, stopping rules and relation to primary manuscript

- This is a **parallel literature theme**, not authorization to divert the 400-hour Paper A/A0 publication programme to a third journal manuscript.
- Do not add Kerala hosting-capacity, congestion, curtailment, forced outage or reliability results to the public evidence baseline solely from literature or proxy power-flow models.
- Stop before quantified Kerala network conclusions if original line ratings/impedances, node-level load/PV data, actual switch status and calibration are unavailable. A source-gap and methods synthesis remains valid.
- No raw agency datasets or third-party copyrighted PDFs should be pushed to public GitHub absent redistribution rights.
- All **0/33** candidates in this batch remain *not full-text critically appraised*. Dates, author lists, article versions and source rights are to be double-checked during full-text review.
- No assertion of PRISMA systematic review, fresh Kerala curtailment evidence, independent peer review or an original 2040 optimum.

### 8. Preliminary decision

**Round 3 is worth screening deeply** because it targets a different scientific gate: *whether energy and infrastructure that are theoretically or administratively available are physically and commercially deliverable.* The most useful negative result may be a documented inability to make credible Kerala hosting-capacity or curtailment claims from public data—without inventing them. The strongest immediate full-text priority is R3-002 followed by R3-001, R3-005 and R3-006.

## Provenance and files

- Source-by-source dated candidate matrix: [SCREENING_MATRIX.csv](SCREENING_MATRIX.csv).
- Transparent search, selection, deduplication and appraisal protocol: [SEARCH_AND_APPRAISAL_PROTOCOL.md](SEARCH_AND_APPRAISAL_PROTOCOL.md).
- Existing Kerala2040 main publication literature matrix: `publication/literature/EVIDENCE_MATRIX.csv` on the still-unmerged `publication/literature-review-2026` branch.
- The current document is a non-PRISMA *critical scoping note based on publicly verifiable summaries and publisher metadata*, not a finished systematic literature review or a validated experiment.
