# Kerala power system under stress — research synthesis

**Prepared:** 28 September 2026  
**Status:** public-data diagnostic and screening study; not an operational post-mortem or investment plan

## Research problem

Kerala2040 now starts from a present-day engineering question:

> **Why is Kerala susceptible to electricity shortages and peak-hour supply restrictions, and what structural and operational factors determine whether the system can meet demand during stressed periods?**

The 2040 question follows from the diagnosis:

> **Given those vulnerabilities, which changes should be tested to make Kerala's electricity supply more resilient as demand grows?**

This is deliberately different from beginning with a preferred technology or a pre-selected capacity-expansion target. The sequence is **observe → diagnose → identify constraints → screen responses → validate later**.

The project does **not** claim to reconstruct the exact causes of any specific 2026 load-shedding event. Event-level attribution would require interval dispatch, outage, market, reservoir and network telemetry that is not publicly available in the present evidence bundle.

## Working synthesis

The evidence supports the following screening hypothesis:

> **Kerala's susceptibility to supply stress emerges from interactions among weather-sensitive peak demand, dependence on external electricity, hydropower timing and availability, and internal transmission constraints rather than from a single statewide annual-energy deficit.**

That statement is a synthesis of public-data screening results. It is not a calibrated reliability assessment, AC security study or causal event reconstruction.

## Research questions and what the evidence says

### RQ1 — How has Kerala's electricity balance changed, and how structurally dependent is it on external electricity?

**Finding:** Kerala's electricity demand has grown while electricity arriving from outside the state remains a major component of the operating balance.

The official broad consumption series rises from **22,540.32 MU in FY2020–21 to 29,311.76 MU in FY2024–25**. The independently audited SLDC archive also shows a **24.1% increase** in daily consumption between FY2020–21 and FY2025–26 on 356 matched calendar dates.

The project keeps official accounting boundaries separate: annual consumption, category-wise sales, periphery input and reported import-energy totals are not interchangeable and are not divided into an unsupported single "import dependence percentage."

**Evidence:** [historical electricity story](CET_HISTORICAL_ELECTRICITY_STORY_2026_09_24.md), [advanced SLDC analysis](SLDC_ADVANCED_DAILY_ANALYSIS_2026_09_23.md), [grid and transfer audit](GRID_TRANSFER_CONTRACTS_FY2024_25_AUDIT.md).

**Confidence:** high for the descriptive historical trend; lower for interval import dependence because continuous measured import telemetry is unavailable.

### RQ2 — Is stress mainly an annual-energy shortage or a chronological peak/flexibility problem?

**Finding:** chronology matters materially.

The ERA5-sensitive reconstruction preserves all **354 observed FY2024–25 daily SLDC energy totals** exactly and flags the 11 missing days as model-only. On held-out January–March 2025 extrema it improves the hourly-shape proxy from **367.9 MW MAE / r = 0.659** for the old fixed shape to **124.9 MW MAE / r = 0.968**. The reconstructed annual peak is **5,923.3 MW**, close to the separate 5,904 MW CEA reference.

In future adequacy screens, renewable spill and unserved energy can occur in the same annual scenario. That is a strong sign that the problem cannot be understood from annual MWh alone: energy can be available at the wrong time.

**Evidence:** [ERA5-sensitive hourly load](ERA5_WEATHER_SENSITIVE_HOURLY_LOAD_PROXY_2026_09_27.md), [chronological screening](PYPSA_CHRONOLOGICAL_SCREENING.md), [Full-PyPSA programme](FULL_PYPSA_SCENARIO_PROGRAMME.md).

**Confidence:** high that timing matters in the screening model; not a claim of measured continuous-hour validation.

### RQ3 — How important is hydropower flexibility?

**Finding:** the timing of hydro energy can have exceptionally high adequacy value.

In the reference-demand / 4,455 MW transfer-capability screening case, allowing the **same daily hydro energy** to move within each day reduces modeled unserved energy from about **375.03 GWh to 11.75 GWh**, a **96.87% reduction**. At lower transfer capability the benefit remains positive but becomes much smaller.

The interday bracket strengthens the same conclusion. At 4,455 MW transfer capability, extending the exact hydro-energy conservation window from one day to 15 days reduces remaining unserved energy from **11.751 GWh to 0.160 GWh**. At severe transfer limitation, additional hydro timing cannot remove most of the deficit.

This does **not** prove that real reservoirs can operate with those windows. The v1.1/v1.2 cases are timing bounds; the v1.3 Idukki model adds state but still uses a reconstructed net water-balance residual rather than validated catchment inflow.

**Evidence:** [Full-PyPSA programme](FULL_PYPSA_SCENARIO_PROGRAMME.md), [hydro operations audit](HYDRO_RESERVOIR_OPERATIONS_AUDIT.md), [Idukki Phase 4 research](PHASE4_IDUKKI_HYDRO_ENERGY_RESEARCH_2026_09_23.md).

**Confidence:** strong as a sensitivity result; physical reservoir validation remains incomplete.

### RQ4 — How vulnerable is Kerala to interstate supply and transfer availability?

**Finding:** dependable external transfer is one of the strongest adequacy levers in the screening model.

The planning sensitivity retains the dated **4,455 MW ATC** benchmark and tests 80% and 60% cases instead of inventing a future ATC. Under reference FY2030–31 demand, unserved-energy fractions rise sharply as the assumed transfer ceiling falls. Increasing local renewable capacity and hydro flexibility helps, but in severe transfer cases the candidate limits bind before the shortage is removed.

Import-price sensitivity and import-availability sensitivity therefore answer different questions. A higher price can change the local build/import trade-off when the system is not already adequacy-bound; a hard transfer constraint can remain binding even when more local capacity would otherwise be economically attractive.

**Evidence:** [grid and transfer audit](GRID_TRANSFER_CONTRACTS_FY2024_25_AUDIT.md), [Full-PyPSA programme](FULL_PYPSA_SCENARIO_PROGRAMME.md).

**Confidence:** strong directional screening signal; future ATC, simultaneous corridor limits and landed hourly procurement prices are not validated.

### RQ5 — Can internal transmission stress exist even when the statewide balance looks adequate?

**Finding:** yes, within the public-network screening model.

The completed KSEBL robustness screen tests **233 source-backed primary lines** under eight extreme allocations of Kerala's residual interstate import. **21 lines remain overloaded in all eight tested boundary-allocation cases**, forming **12 connected robust corridor groups**.

The historical transformer screen used a 31 March 2023 PSS snapshot in which Shornur had a **100 MVA 220/110-kV entry**, so the model also flagged that element in all eight cases. A post-release QA check against the current 2026 CEA transmission plan found that Shoranur is now reported with **200 MVA + 100 MVA** existing transformation and is independently identified by CEA as a constrained station with further reinforcement planned. The 100 MVA model overload ratio is therefore **not a current whole-station loading estimate**.

Shornur remains the strongest multi-voltage **geographic hotspot** in the public screening: robust 110-kV and 220-kV corridor groups meet there, and the location is independently corroborated by CEA planning evidence.

The correct claim is therefore:

> **Under the public-data FY2024–25 chronological screening model, Shornur emerges as the strongest multi-voltage internal transmission hotspot across the tested boundary-injection allocation envelope. Current CEA planning evidence independently corroborates Shoranur as a constrained location, while the Kerala2040 transformer overload magnitude remains a historical-screening result rather than a current operator loading estimate.**

This is not a calibrated AC load-flow, voltage-stability or N-1 security conclusion and is not converted directly into an upgrade MW or cost.

**Evidence:** [robust network bottlenecks](KSEB_NETWORK_ROBUST_BOTTLENECKS_V1_0.md), [network screening closeout](KSEB_NETWORK_SCREENING_CLOSEOUT_V0_1.md).

**Confidence:** strong screening robustness; planning-grade reinforcement design remains future work.

## Weather is a two-sided system driver

Kerala's electricity system is **weather-coupled on both sides of the balance equation**.

- Heat and humidity affect the timing and magnitude of cooling-related demand.
- Monsoon rainfall affects reservoir conditions and hydropower opportunity.
- Cloud, rainfall and wind alter variable-renewable output.
- Floods and landslides can become infrastructure hazards.

The present project quantifies the first point with an ERA5-sensitive demand reconstruction and explores the hydro/rainfall relationship around Idukki. It does not yet contain a future-climate ensemble or a fully validated rainfall–runoff–reservoir model.

## Ecology is a feasibility boundary, not a decoration

Ecological work is not presented as a cause of present shortages. It answers a different question:

> **If the engineering model identifies more generation, storage or transmission as useful, where can those assets actually fit?**

The project has completed official-boundary work, DEM and terrain processing, landslide diagnostics, protected-area source audits, waterbody analysis and renewable-resource crosswalks. It has **not** promoted those layers into legally complete buildable-MW ceilings.

Forest/wetland notifications, validated hazard geometries, technology-specific setbacks, community and land-use constraints, and project-level permitting remain necessary before a spatial investment recommendation.

See [forest/DEM/wetland/landslide audit](FOREST_DEM_WETLANDS_LANDSLIDE_GIS_AUDIT.md) and [renewable consolidated analysis](SOLAR_WIND_CONSOLIDATED_ANALYSIS_2026_09_22.md).

## RQ6 — What responses look worth testing?

The project can go further than a generic list because early-stage experiments already test several mechanisms. They remain **candidate responses**, not an optimized plan.

### Do more with what already exists

- improved hydro scheduling and reservoir coordination;
- demand response and time-of-use signals;
- managed EV charging;
- flexible cooling and thermal storage;
- flexible non-critical industrial loads;
- better forecasting and operational coordination.

The WP6 pilots show that the same end service can be delivered at a different time in simplified examples. They do not establish statewide MW savings.

### Add flexibility infrastructure

- BESS where short-duration electrical shifting is valuable;
- pumped-storage hydro where topography, water, civil works and ecology make it credible;
- thermal storage where the service being shifted is thermal rather than electrical;
- targeted substations and transmission reinforcement where network evidence justifies it.

Storage does not create electricity and normally introduces losses. Its value is temporal: moving usable energy from lower-value or surplus hours into stressed hours.

### Add supply where it solves the diagnosed problem

Solar, wind and other generation remain part of the solution space, but annual renewable MWh alone cannot guarantee evening adequacy. New capacity should be evaluated jointly with timing, network connection, ecology, land, storage and dependable imports.

## What this study can and cannot conclude

### Supported now

- demand is growing and the hourly shape matters;
- weather improves reconstruction of demand timing;
- hydro timing has very large adequacy value in some screening cases;
- severe transfer constraints dominate many otherwise useful flexibility measures;
- internal network bottlenecks can persist under radically different import-injection assumptions;
- ecological and land constraints must bound future infrastructure rather than be added after optimisation;
- several flexibility interventions are technically plausible enough to justify deeper study.

### Not supported yet

- the exact cause of a particular 2026 restriction event;
- a planning-grade loss-of-load probability or reliability standard;
- a calibrated AC/N-1 security assessment;
- a validated reservoir/cascade operating policy;
- legally defensible renewable buildable-MW ceilings;
- a least-cost investment portfolio;
- project-specific transmission upgrade MW and cost;
- a claim that any one intervention will eliminate load shedding.

## Modelling freeze for the CET/public release

For the current release, **no new model family should be added unless it either changes a material conclusion or uses genuinely new evidence**.

The remaining work is synthesis, communication, final QA and release packaging. Two optional evidence upgrades remain scientifically valuable but are not blockers:

1. independently validated Idukki catchment → ERA5 rainfall → observed inflow work;
2. the official KSEB FY2024–25 reservoir/inflow run if the required monthly source workbooks become accessible.

Kerala2040 should therefore be published as a **public-data diagnostic and screening study**, not as an exact optimal 2040 plan.
