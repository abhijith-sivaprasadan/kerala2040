# Literature review Round 4 — Protocol and search log
**Topic:** Climate-related electricity-grid resilience, observed outages, extreme-event asset damage and post-disaster restoration.
**Search performed:** 28 October 2026. **Review status:** exploratory structured narrative screening, not PRISMA systematic review, full-text critical appraisal, numerical verification, or new Kerala measurement.

## Strict separation from the first three rounds

- **Round 1:** Weather-to-daily-operational demand, demand/energy target definitions, chronological validation, ERA5 and broad energy models. R4 excludes demand-prediction modelling unless the paper's *primary outcome* is power failure, outage duration or restoration.
- **Round 2:** Reservoir water availability, hydropower dispatch, cascade rules, rainfall/monsoon and flood-management-versus-power trade-offs. R4 **excludes** reservoir-release/rule-curve optimization and rainfall climatology except as a *hazard input* to infrastructure damage.
- **Round 3:** Solar/wind hosting capacity, network evacuation, curtailment, battery capacity and RE deliverability in non-disaster operation. R4 focuses on **loss of electrical service, restoration and hazard-induced damage**, not ordinary-network RE accommodation.
- **Paper A/A0:** Literature-only parallel queue. The one-manuscript 400-hour Kerala2040 research charter and 23 October 2026 public evidence freeze remain binding. R4 is **not** a pre-approval for a fourth research article.

## Central falsifiable question

**Which attributes of Kerala's historical electricity-service losses and recovery after extreme weather are directly observable in admissible primary records, and which resilience and adaptation claims remain untestable without original outage and asset-damage data?**

Research questions for appraisal only:
- **R4-Q1 / measurement:** Do published studies distinguish an outage *event*, affected service *connection*, customer interruption *duration*, feeder or transformer *damage*, unserved *energy* and *restoration rate*? Are hazard dates and analysis windows stated?
- **R4-Q2 / observational identification:** Can authors substantiate hazard-to-outage associations against calendar, maintenance, demand and reporting confounders? Which models are trained/tested on **observed** faults and which simulate failures?
- **R4-Q3 / physical fragility:** Which asset-specific fragility and repair-time functions have empirical source traces for coastal flooding, extreme rainfall, wind and landslides? What is the sensitivity to asset age/health and hazard trajectory?
- **R4-Q4 / adaptation:** Do controlled alternatives for asset hardening, undergrounding, meshing, operational switching, portable generation or emergency crews show field-observed recovery or only modelled improvement?
- **R4-Q5 / critical services:** What restoration prioritization information is needed for hospitals, water pumps, emergency shelters and socially vulnerable consumers? The framework must not invent public critical-load lists or feeder mappings.

## Search log

Discovery sources: general web search, DOI resolution / journal publisher landing pages, official Indian government and Kerala institutional websites, original preprint discussion page. These are **not** a complete Scopus, Web of Science or OpenAlex export. Search result counts and screening PRISMA flow are not inferred.

| Theme | Queries actually searched or close variants (28 Oct 2026) | Intent |
|---|---|---|
| India empirical outages | `India electricity grid extreme weather resilience cyclone flood outages academic paper DOI 2021 2025`; `India electricity outages climate temperature floods extreme weather study SAIDI reliability DOI` | Find actual outage samples and Indian context |
| India field recovery | `Cyclone Fani power distribution restoration Odisha resilience study journal DOI`; `Kerala 2018 floods electricity power KSEB distribution damage restoration scientific paper DOI` | Historic power-asset damage and response |
| Fragility models | `climate hazard power transmission line failure fragility curve flood landslide India DOI`; `power outage restoration extreme weather spatial data empirical study distribution resilience DOI` | Observed-vs-synthetic fault probabilities |
| Review / metrics | `power system resilience weather disaster critical review metrics restoration DOI`; `climate change electricity transmission distribution infrastructure vulnerability extreme events systematic review DOI` | Reliability versus resilience measurement |
| Recoverability and equity | `power distribution outage flood resilience 2023 2024 DOI`; `climate extremes transmission electricity grid vulnerability 2025 2024 DOI` | Critical-load and intervention metrics |
| Kerala official evidence | `KSEB annual administration report 2018 2019 flood reconnect restoration`; `World Bank Kerala post disaster needs assessment 2018 power energy losses` | Raw-source rights and missing data |
| National guidance | `CEA disaster management plan power sector India 2025 cyclone resilience PDF`; `India Ministry of Power guidelines distribution electricity disaster climate resilience 2023 2024` | Dated statutory/administrative plans |

Full article versions, exact issue/page dates and metadata remain subject to document-level verification despite DOI-title screening. This is a **fixed candidate list as of the stated date**, not a claim of exhaustive search.

## Matrix structure and counts

- **32 journal research/review candidate records** with DOI and canonical `https://doi.org/<doi>` link.
- **One independent discussion/preprint** (Verschuur and Balakrishnan 2024, `10.5194/egusphere-2024-3176`); do not describe as peer-reviewed journal paper unless a separately verified version appears.
- **Nine official, institutional and operator/practitioner comparator records**, with `source_url`, empty DOI field.
- **42 total candidates; 33 DOI-bearing records, 9 non-DOI sources.**
- DOI-string comparison completed against existing R1 44-entry and R3 33-entry matrices: **zero exact matches**; not a complete title/version match. Round 2's 40-item roster still needs cross-round deduplication.
- **Full texts critically appraised:** 0/42; **independent numerical reproductions:** 0/42.
- Source statuses: `publisher_doi_title_screened`, `publisher_preprint_record_checked`, or `official_or_journal_web_listing_checked`. None means actual original full PDF was obtained and assessed.
- No redistribution of proprietary PDF scans, utility telemetry, personally identifiable power outage data or infrastructure vulnerability configurations.

## Inclusion rules

1. Published scientific work primarily assesses **electricity infrastructure failure, interruption, restoration, service risk, or adaptation** from extreme hazard; or a well-defined methods/review benchmark essential for interpreting those quantities.
2. India/Kerala preference; strong international observational comparators retained where method transfers but effect sizes cannot.
3. Journal DOI metadata checked against official journal/DOI landing page; preprint and practitioner/official records distinctly labelled.
4. Extract only what the source explicitly supports. Prefer observed outage logs, asset incident records and independent failure calibration.
5. Deliberately retain contradictory studies on outage data aggregation, hazard correlations, uncertainty, synthetic case studies and impacts on critical customers.
6. Include older 2020–21 foundational India cases where uniquely relevant; prioritize 2023–26 newer methods.

## Exclusion / deferral rules

- Rainfall, river inundation or reservoir studies with no **electricity-asset damage or outage outcome**.
- Renewable hosting capacity, BESS siting, EV flexibility, or congestion absent an event-triggered **service-loss and recovery** endpoint (Round 3).
- Electricity demand growth and temperature-response forecasting without an independently observed power-outage outcome (Round 1).
- Invented event histories, unlabeled synthetic damage curves, attribution of all lost load to weather based on date coincidence, unsourced asset-failure rates.
- Generic policy advocacy with no testable outcome, unless official documents establish actual data definitions or original event reporting.
- Do not count multiple versions of a preprint/published article as separate studies; cross-check DOI and title after full-text acquisition.

## Appraisal workflow for each selected paper

For every research source, capture:
- DOI, official title, exact authors, journal and article type; publisher URL, date, full-source license and source-byte SHA256 (if legitimately obtained).
- Study geography, event years, hazard metadata and original custodian.
- Physical entity: feeder, substation, transformer, transmission tower/line, generation unit, microgrid or service connection.
- Response variable and meter/record: SAIDI/SAIFI only if definitions and original connection counts exist; interruption count, minutes, customer-hours, connection-days, unserved MW/MWh (careful time integration), financial losses.
- Data and reporting: actual source rows versus annual narrative, service quality report versus model, event records versus hazard proxy, damage inspection.
- Time/space precision: time-zone, overlapping event deduplication, spatial geocoding, missing events, changing infrastructure/customer base.
- Inference: confounding controls, counterfactual, pre/post comparisons, data leakage, unobserved reporting incentives, external validation.
- Adaptation analysis: hardening/undergrounding/meshing/DER/microgrids/restoration crew; measured versus optimized outcome.
- Physical model admission: topology, line and transformer ratings, fragility/asset health, actual switches, critical-service chronology, access constraints.
- Explicitly reported **limitations and counterevidence**; page/table/figure provenance and 2–3 Kerala2040 implications.

**Status ladder** (separate booleans):
1. DOI/publisher **metadata screened**.
2. Original full text **obtained with access conditions**.
3. Full document, methods, tables/figures and supplements **critically appraised**.
4. Reproduction dataset/source chain independently **verified**.
5. Kerala-specific original outage/asset observations **admitted**.
6. Historical Kerala damage/recovery estimates **independently crosschecked**.

The source list is currently only at step 1. Do not equate availability of a PDF with critical appraisal.

## Operational and publication red lines

- Kerala2018 restoration counts **do not** equal a continuous sampled feeder/customer SAIDI/SAIFI series; reconstructing customer-hours requires durations and denominators, not just counts restored.
- A resilience **curve** generated from synthetic probabilities is not measured Kerala resilience.
- Hazard forecast/reanalysis is not field-recorded voltage, broken tower, reported fault, or causal meteorological explanation.
- Annual consumer-side electricity series and SLDC daily operating energy **cannot** substitute for interruption/outage observations.
- Statements of CEA planning criteria, action-plan provisions or proposed hardening are not evidence those investments are built and calibrated.
- Power-system **reliability, resource adequacy, LOLE/LOLP**, and **extreme-event resilience** are related but distinct: no observed reliability numbers without outage records and a suitable denominator.
- No publication-quality assertion of a distinctive Kerala scientific gap until nearest original cases and full-text studies have been inspected.

## Gated next step — after Round 2 and Round 3 full paper analysis

Stage 1: download legally accessible candidate PDFs and check title/author/DOI/version metadata.
Stage 2: appraise 10 highest-priority sources and all three Kerala/India operational anchors in the context of real empirical source limits.
Stage 3: prepare an **observability matrix**: variable, authority, event, geometry, validity, rights, possible lawful aggregated publication.
Stage 4: do a novelty/falsification check; choose either a narrow source-audited **resilience evidence atlas** or no extra manuscript. Do not weaken the primary one-paper charter.
