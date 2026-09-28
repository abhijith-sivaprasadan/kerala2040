# Kerala2040

## Kerala Power System Under Stress

**A data-driven investigation of demand, hydropower, import dependence and transmission constraints — and what those findings imply for a more resilient Kerala.**

കേരളത്തിന്റെ ഊർജഭാവി · Kerala's energy future

[Public website](https://kerala2040.github.io/) · [Research synthesis](docs/POWER_SYSTEM_STRESS_SYNTHESIS_2026_09_28.md) · [Methods and evidence](docs/evidence_register.md) · [Current next steps](docs/NEXT_STEPS.md)

---

## The question

Kerala2040 started as a broad exploration of possible energy pathways to 2040. The evidence collected along the way points to a more useful starting point:

> **Why is Kerala susceptible to electricity shortages and peak-hour supply restrictions, and what structural and operational factors determine whether the power system can meet demand during stressed periods?**

The future question comes second:

> **Given those vulnerabilities, what changes should be tested to make Kerala's electricity supply more resilient as demand grows toward 2040?**

This is a **diagnosis-first** project. It does not begin by assuming that Kerala simply needs more generation, more solar, more batteries or more imports. It asks where the constraint actually is: annual energy, the difficult hour, hydropower timing, external supply, internal transmission, land/ecology, or some interaction among them.

The study does **not** claim to reconstruct the exact cause of a particular 2026 load-shedding event. Public data are not sufficient for an event-level operational post-mortem. The current work instead identifies and stress-tests structural vulnerabilities that can make the system susceptible to supply restrictions.

## Meet Kerala

Kerala is a narrow tropical state on India's south-west coast, between the **Arabian Sea** and the **Western Ghats**. More than 36 million people live in **38,863 km²**. Coastal cities, beaches and backwaters sit within short distances of densely settled lowlands, plantations, reservoirs, steep highlands and tropical forests.

That geography is not background decoration. It is part of the electricity problem:

- dense settlement limits easy land and corridor availability;
- the Western Ghats provide rainfall, elevation and river systems for hydropower while also containing sensitive and difficult terrain;
- monsoon and heat affect both electricity demand and hydro conditions;
- a compact, heavily settled state must move large amounts of electricity through a constrained internal network;
- future generation, storage and transmission must coexist with forests, wetlands, water systems, agriculture, settlements and hazards.

For an international audience, particularly at CET/KTH, a few scale comparisons help:

| Perspective | Kerala | Sweden |
|---|---:|---:|
| Population | ~36 million, mid-2020s projection | 10.61 million, July 2026 |
| Area | 38,863 km² | >400,000 km² land |
| FY2024–25 / 2024 electricity use | 29.31 TWh | 125.3 TWh excluding losses |
| Per-capita electricity use | 816 kWh/year in FY2024–25 | roughly an order of magnitude higher |

The comparison is **context, not a ranking**. Sweden and Kerala have very different climates, industrial structures, heating needs and electricity systems. The important point is that Kerala serves more than three times Sweden's population on less than one-tenth the land area while electricity use per person remains much lower and is still growing.

A descriptive Kerala/Swedish context note, including landscape, culture, heavy-mineral sands, case studies and sourced infrastructure-budget examples, is here: [Kerala context for a Swedish audience](docs/KERALA_CONTEXT_FOR_SWEDISH_AUDIENCE_2026_09_28.md).

Official context sources include the [Kerala Department of Economics & Statistics](https://ecostat.kerala.gov.in/page/key-statistics), [Kerala State Planning Board](https://spb.kerala.gov.in/en/7036/), [Statistics Sweden](https://www.scb.se/BE0101-en) and the [Swedish Energy Agency](https://www.energimyndigheten.se/nyhetsarkiv/2025/slutgiltig-statistik-for-el-och-fjarrvarme-2024/).

## What the evidence says so far

### 1. Demand is growing, but annual MWh are not the whole problem

Official broad electricity consumption rises from **22,540.32 MU in FY2020–21 to 29,311.76 MU in FY2024–25**. The audited SLDC archive independently shows a **24.1% increase** in daily consumption between FY2020–21 and FY2025–26 on 356 matched calendar dates.

Yet adequacy results show that renewable spill and shortage can occur in the same annual scenario. Electricity can exist in the system and still be unavailable **when it is needed**.

### 2. Weather helps explain the shape of demand

The ERA5-sensitive 8,760-hour demand reconstruction preserves all **354 observed FY2024–25 daily SLDC energy totals** exactly; the 11 missing days remain explicitly model-only.

On held-out January–March 2025 extrema, the weather-sensitive reconstruction improves the old fixed-shape error from **367.9 MW MAE to 124.9 MW**, with correlation improving from **0.659 to 0.968**. Its reconstructed annual peak is **5,923.3 MW**, close to the separate 5,904 MW CEA reference.

This is better chronology, not continuous measured-hour validation.

### 3. Hydro's timing can matter as much as its annual energy

In the reference-demand / 4,455 MW transfer-capability screening case, allowing the **same daily hydro MWh** to shift within the day reduces modeled unserved energy from about **375.03 GWh to 11.75 GWh** — a **96.87% reduction**.

Longer timing windows reduce the remaining shortage further in the healthy-transfer case. The same flexibility has much less power when external transfer is heavily constrained.

The implication is not "operate reservoirs exactly like this model." It is that **hydro scheduling, water availability and temporal flexibility deserve first-order attention**.

### 4. External electricity is a structural part of the system

Kerala's official statistics and SLDC records show large electricity flows from outside the state. The project keeps the different official accounting boundaries separate rather than manufacturing a single unsupported import-share number.

In the adequacy screens, reducing the assumed interstate transfer ceiling from the dated **4,455 MW ATC** benchmark produces much larger supply stress. More renewable generation and hydro flexibility help, but severe transfer constraints can still dominate.

Interconnection is therefore neither "bad" nor merely emergency backup. The research question is how much dependence is economical and resilient, and what happens when external supply becomes scarce or physically constrained.

### 5. Statewide balance can hide internal network stress

The public KSEBL network screen tests **233 source-backed primary lines** under eight radically different ways of allocating Kerala's residual interstate import.

**21 lines remain overloaded in all eight tested boundary-injection cases**, forming **12 robust corridor groups**. A historical 31 March 2023 PSS snapshot also caused the screening model to flag a **100 MVA Shornur 220/110-kV transformer element** in every case.

**QA correction (28 September 2026):** the current CEA Kerala transmission plan reports **200 MVA + 100 MVA** of existing transformation at Shoranur and independently identifies the station and nearby corridors as constrained, with further reinforcement planned. The Kerala2040 **hotspot location is therefore independently corroborated**, but the model's 100 MVA transformer loading must not be interpreted as current whole-station loading.

Under this public-data screening model, **Shornur emerges as the strongest multi-voltage internal transmission hotspot robust to the tested boundary-injection allocation envelope**. This is a congestion/deliverability screen, not an AC/N-1 operator-state result.

This is not a calibrated AC or N-1 security assessment and is not converted directly into an upgrade MW or cost.

## The emerging explanation

The current evidence supports a working synthesis:

> **Kerala's susceptibility to power-system stress appears to come from the interaction of weather-sensitive peak demand, dependence on external electricity, hydropower timing and availability, and internal transmission constraints rather than from one simple statewide annual-energy deficit.**

The detailed evidence and confidence boundaries for each research question are in [POWER_SYSTEM_STRESS_SYNTHESIS_2026_09_28.md](docs/POWER_SYSTEM_STRESS_SYNTHESIS_2026_09_28.md).

## Weather is on both sides of the balance

Kerala's electricity system is **weather-coupled on both demand and supply**.

Heat and humidity can increase cooling-related demand. Monsoon rainfall affects reservoirs and hydro opportunity. Clouds and wind affect variable renewable resources. Extreme rainfall and landslides can become infrastructure hazards.

The current project quantifies the demand-weather link, analyses Idukki rainfall/inflow/reservoir records and screens hydro timing. A full future-climate and physical catchment model remains later work.

## Ecology is a constraint on solutions

The ecological work is not presented as a cause of current power cuts. It answers:

> **If a model says Kerala would benefit from more generation, storage or transmission, where can that infrastructure actually fit?**

Completed work includes official-boundary processing, DEM/terrain analysis, landslide diagnostics, protected-area source audits, waterbody work and renewable-resource crosswalks.

What is **not** complete is equally important: statutory forest/wetland/ESZ/coastal/paddy constraints, technology-specific setbacks, community/land feasibility and therefore a legally defensible "Kerala can build X GW here" result.

See [FOREST_DEM_WETLANDS_LANDSLIDE_GIS_AUDIT.md](docs/FOREST_DEM_WETLANDS_LANDSLIDE_GIS_AUDIT.md) and [SOLAR_WIND_CONSOLIDATED_ANALYSIS_2026_09_22.md](docs/SOLAR_WIND_CONSOLIDATED_ANALYSIS_2026_09_22.md).

## Managing symptoms vs reducing vulnerability

A short-term response is not automatically a bad response. Buying power from outside, conserving reservoir water or asking consumers to reduce peak demand can be economically rational.

The structural question is:

> **When is a temporary response the cheapest sensible option, and when does repeated dependence reveal a root constraint that is better addressed through a durable operating change or investment?**

That turns a common public debate into an engineering problem:

| What people experience | Short-term response | Structural question |
|---|---|---|
| evening shortage | short-term procurement / load restriction | is dependable peak supply or flexibility insufficient? |
| low reservoir conditions | conserve hydro / buy more power | how weather-coupled is firm supply? |
| daytime solar but evening stress | export / curtail / import later | is storage or demand shifting valuable? |
| local network congestion | switching / operating workaround | does a corridor or transformer need reinforcement? |
| rising demand | peak conservation appeals | can efficiency, tariffs and flexible loads reduce the difficult hour? |

The project aims to make these mechanisms understandable to readers without power-system training.

## What might help? Preliminary, not prescriptive

Early-stage models and engineering reasoning identify several responses worth deeper testing.

### Do more with what already exists

- better hydro scheduling and forecasting;
- demand response and time-of-use signals;
- managed EV charging;
- flexible cooling and thermal storage;
- flexible non-critical industrial loads;
- better coordination of available supply.

### Add flexibility infrastructure

- BESS for appropriate short-duration electrical shifting;
- pumped-storage hydro where the specific reservoirs, civil works, water balance and ecology support it;
- thermal storage where the service being shifted is thermal;
- targeted substation and transmission reinforcement.

Storage does not create electricity and normally introduces losses. Its value is moving usable energy from one time to another.

### Add new supply where it addresses the diagnosed constraint

Solar, wind and other generation remain important possibilities, but annual renewable MWh alone do not guarantee evening adequacy. New supply has to be considered together with timing, network connection, ecology, land, storage and dependable interconnection.

These are **candidate directions, not a validated least-cost portfolio**.

## Kerala already contains pieces of this transition

Existing projects can make the abstract system easier to understand:

- **CIAL** reports 50 MW of renewable capacity, daytime grid export and a BESS project intended for nighttime use of solar electricity.
- **Kochi Metro** reports 5.389 MWp of station/depot solar.
- **Kochi Water Metro** operates battery-electric water transport and has described a future 17 MWp solar concept for its energy needs.
- **KMML** provides a separate industrial/circular-material case connected to Kerala's heavy-mineral geology.

These are case studies, not explanations for statewide supply stress. Sources and boundaries are documented in [KERALA_CONTEXT_FOR_SWEDISH_AUDIENCE_2026_09_28.md](docs/KERALA_CONTEXT_FOR_SWEDISH_AUDIENCE_2026_09_28.md).

## Budget-conscious engineering

Kerala's infrastructure problem is also a capital-allocation problem.

Official examples include rough estimates of **₹180 crore for a 30 MW Manjappara pumped-storage project** and **₹573 crore for a 100 MW Mudirapuzha pumped-storage project**, while the Kerala 2025–26 budget earmarks **₹1,156.76 crore for the energy sector**.

For Swedish readers the site will show dated, approximate SEK equivalents alongside the original INR figures. The purpose is scale, not a claim that Kerala always builds cheaply or without overruns.

The more useful question is:

> **With limited capital, which intervention removes the most persistent vulnerability per unit of money, land and environmental impact?**

## Research questions

| Question | Present status |
|---|---|
| **RQ1. How has the electricity balance changed and how important is external supply?** | strong descriptive evidence |
| **RQ2. Annual shortage or chronological peak/flexibility problem?** | strong screening evidence that timing matters |
| **RQ3. How valuable is hydropower flexibility?** | very strong sensitivity result; physical reservoir validation incomplete |
| **RQ4. How vulnerable is Kerala to external transfer availability and price?** | strong screening signal; future ATC/market detail incomplete |
| **RQ5. Can internal network stress persist despite statewide balance?** | robust public-network screening result |
| **RQ6. Which interventions best reduce vulnerability?** | preliminary mechanism tests; future validation required |

The full research plan is [docs/research_plan.md](docs/research_plan.md).

## Where the rest of the project fits

The project has accumulated substantial work. It is not being discarded; it is being given a clearer role.

### Core diagnostic evidence

- audited SLDC electricity history;
- ERA5-sensitive demand;
- installed-generation census;
- PyPSA adequacy and import sensitivities;
- hydro timing / Idukki studies;
- KSEBL network reconstruction and robustness;
- PyPSA ↔ OSeMOSYS numerical equivalence.

### Feasibility and context

- solar/wind resource work;
- land, terrain, ecology and hazard audits;
- Total Energy Atlas;
- project finance / public-budget context;
- CIAL / Kochi Metro / Water Metro examples;
- KMML and wider industrial-energy work.

### Candidate-response experiments

- cooling and thermal storage;
- managed EV charging;
- industrial flexibility;
- BESS;
- pumped-storage analogue;
- integrated flexibility experiments.

The old work packages remain documented, but they no longer compete as equal homepage stories.

## Evidence discipline

Kerala2040 keeps four evidence levels separate:

1. **Observed / source reported**
2. **Derived from observed data**
3. **Screening model / sensitivity**
4. **Educational hypothesis / candidate response**

A model result does not become an observation because it is plotted. A public website does not make an unresolved source gate pass.

Important examples:

- 11 missing FY2024–25 SLDC dates remain missing in the observed dataset.
- the 8,760-hour load series is a reconstruction, not telemetry;
- the five-site solar/wind profiles are resource proxies, not a statewide fleet;
- v1.1/v1.2 hydro flexibility is a timing sensitivity, not a reservoir rule curve;
- v1.3 Idukki uses a reconstructed net water-balance residual, not observed catchment inflow;
- network overloads are screening findings, not upgrade prescriptions;
- solver equivalence validates implementation agreement, not physical truth.

Read [PROVENANCE_CORE_RULES.md](docs/PROVENANCE_CORE_RULES.md), [AUDIT_RELEASE_GATES.md](docs/AUDIT_RELEASE_GATES.md) and [evidence_register.md](docs/evidence_register.md).

## Current status: modelling freeze

For the CET/public release, **no new model family should be added unless it changes a material conclusion or uses genuinely new evidence**.

The remaining work is:

- close the final network-planning integration/CI gate;
- align README, website and poster;
- publish the findings hierarchy clearly;
- run final repository and browser QA;
- freeze and publish a reproducible evidence snapshot.

Optional later work includes independently validated Idukki catchment hydrology, the official KSEB reservoir run when source workbooks become accessible, calibrated AC/N-1 analysis, legally complete siting constraints, and a full least-cost/reliability investment optimisation.

See [NEXT_STEPS.md](docs/NEXT_STEPS.md).

## Repository map

| Area | Where to look |
|---|---|
| Main research synthesis | [docs/POWER_SYSTEM_STRESS_SYNTHESIS_2026_09_28.md](docs/POWER_SYSTEM_STRESS_SYNTHESIS_2026_09_28.md) |
| Kerala / Swedish context | [docs/KERALA_CONTEXT_FOR_SWEDISH_AUDIENCE_2026_09_28.md](docs/KERALA_CONTEXT_FOR_SWEDISH_AUDIENCE_2026_09_28.md) |
| Research plan | [docs/research_plan.md](docs/research_plan.md) |
| Historical electricity | [docs/CET_HISTORICAL_ELECTRICITY_STORY_2026_09_24.md](docs/CET_HISTORICAL_ELECTRICITY_STORY_2026_09_24.md) |
| ERA5 demand | [docs/ERA5_WEATHER_SENSITIVE_HOURLY_LOAD_PROXY_2026_09_27.md](docs/ERA5_WEATHER_SENSITIVE_HOURLY_LOAD_PROXY_2026_09_27.md) |
| PyPSA programme | [docs/FULL_PYPSA_SCENARIO_PROGRAMME.md](docs/FULL_PYPSA_SCENARIO_PROGRAMME.md) |
| Hydro/Idukki | [docs/PHASE4_IDUKKI_HYDRO_ENERGY_RESEARCH_2026_09_23.md](docs/PHASE4_IDUKKI_HYDRO_ENERGY_RESEARCH_2026_09_23.md) |
| Network findings | [docs/KSEB_NETWORK_ROBUST_BOTTLENECKS_V1_0.md](docs/KSEB_NETWORK_ROBUST_BOTTLENECKS_V1_0.md) |
| Ecology/GIS | [docs/FOREST_DEM_WETLANDS_LANDSLIDE_GIS_AUDIT.md](docs/FOREST_DEM_WETLANDS_LANDSLIDE_GIS_AUDIT.md) |
| Solar/wind | [docs/SOLAR_WIND_CONSOLIDATED_ANALYSIS_2026_09_22.md](docs/SOLAR_WIND_CONSOLIDATED_ANALYSIS_2026_09_22.md) |
| Flexibility pilots | [docs/WP6_KERALA_GRID_INTEGRATION_GATE_2026_09_24.md](docs/WP6_KERALA_GRID_INTEGRATION_GATE_2026_09_24.md) |
| Total Energy Atlas | [docs/KERALA_TOTAL_ENERGY_ATLAS_BASELINE_2026_09_24.md](docs/KERALA_TOTAL_ENERGY_ATLAS_BASELINE_2026_09_24.md) |
| Circular industry | [docs/KMML_CIRCULAR_INDUSTRY_CASE_2026_09_24.md](docs/KMML_CIRCULAR_INDUSTRY_CASE_2026_09_24.md) |
| Release gates / next work | [docs/NEXT_STEPS.md](docs/NEXT_STEPS.md) |

## Reproduce the project

Python **3.11** is the reference runtime.

```bash
git clone https://github.com/abhijith-sivaprasadan/kerala2040.git
cd kerala2040

python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate

python -m pip install -e ".[dev]"
ruff check src tests scripts
pytest
```

Build the website:

```bash
PYTHONPATH=src python scripts/build_site.py --output _site
node --test tests/web.test.cjs
node tests/site.browser.cjs _site
```

Some source-acquisition and hydrology workflows intentionally fail closed when the exact upstream evidence is not available. That is a provenance feature, not a request to replace missing observations with synthetic data.

## Project boundary

Kerala2040 is an independent research project by **Abhijith Sivaprasadan**. CET 2026 / KTH affiliation describes the presentation context; it does not imply institutional endorsement of the project's findings.

The repository is open for inspection, criticism and reproduction. Claims should be cited from their underlying source or evidence file rather than from a screenshot or presentation summary.
