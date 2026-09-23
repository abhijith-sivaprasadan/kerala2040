# Kerala2040 · SLDC × Idukki rainfall/inflow × flood-event phase 3 (23 September 2026)

**Scope / provenance:** Offline join of source-curated five-section Kerala SLDC daily reports (6 August 2019–23 September 2026) with the **named Idukki reservoir row** from the same original dated source. Full original source fingerprints are in `public_flood_hydro_weather_qa.json`. No interpolation. This stage does **not** claim matched statewide ERA5 reanalysis or actual Energy Atlas data: those original data were not present in the analysis workspace. Nor does it claim a causal flood effect, statewide flood mapping, full daily telemetry or pumped-storage readiness.

## Executed source join

- The join retains **2,606 daily date slots**, including confirmed unavailable source dates. **1,359** dates have a source-reported *Idukki reservoir rainfall* field and **2,414** have source-reported *Idukki reservoir inflow*; the remaining fields remain missing, **not zero**. Overlap is limited by actual field availability and source reporting schemas.
- **Idukki rainfall vs Idukki inflow:** Pearson r = **0.627** on **1,344** coincident days; r = **0.598** after year-month demeaning. This is a descriptive **same-reservoir** relationship, not a catchment runoff coefficient.
- **Idukki rainfall vs statewide qualified electricity consumption:** Pearson r = **−0.209**, 1,358 days; r = **−0.249** after year-month demeaning. This does not identify rainfall as a cause; temperature, calendar, event disruptions and spatial heterogeneity are unadjusted.
- **Idukki rainfall vs statewide hydel total:** r = **+0.085**, 1,358 days; after year-month demeaning **−0.099**. Same-day rainfall is not interchangeable with water released for generation, which can be scheduled using water accumulated earlier.
- **Idukki storage % vs statewide hydel MU:** r = **+0.265**, 2,576 days; after year-month demeaning **+0.182**. Reservoir stock is not an instantaneous hydropower output, and aggregate hydel includes other plants.

**Interpretation rule:** month-year demeaning only removes each calendar month's mean within a given year. It does **not** control serial correlation, station coverage, reservoir operations or confounding. No significance or causal estimate is claimed.

## Time-stamped event windows: descriptive only

| Event window (IST days) | Physical category / geography | Qualified daily energy days | Mean consumption MU/day | Mean hydel MU/day | Mean import MU/day | Idukki-gauge mean rain mm/day | Idukki mean inflow MCM/day |
|---|---|---:|---:|---:|---:|---:|---:|
| 8–20 Aug 2018 | Statewide historic flood benchmark | **0** | — | — | — | — | — |
| 8–14 Aug 2019 | Multi-district flooding | 7 | 50.46 | 13.37 | 35.94 | 58.81 | 65.23 |
| 6–11 Aug 2020 | Pettimudi / heavy-rain landslide; **not** statewide flood claim | 6 | 55.76 | 22.27 | 32.05 | 89.07 | 75.27 |
| 15–20 Oct 2021 | Floods and landslides, central/southern Kerala | 6 | 69.77 | 34.40 | 33.58 | 46.53 | 46.59 |
| 29 Jul–4 Aug 2024 | Wayanad landslides; separately classified hazard | 7 | 74.32 | 35.88 | 35.76 | 35.23 | 38.40 |
| 20–22 Sep 2026 | **Localized** Nilambur/Malappuram flash flood | 3 | 92.03 | 22.02 | 67.58 | 19.53 | 11.28 |

**These are event-window means, not estimated changes attributable to the event.** The 2026 Nilambur event is in Malappuram; an Idukki-reservoir rain gauge *cannot* test local rainfall in Nilambur. The absence of 2018 electricity rows is a strict boundary of this archive. Detailed calendar-by-day joined rows remain private.

### Source anchors for dated hazard categories

- 2018 primary historical anchor: [KSDMA 2018 source collection](https://sdma.kerala.gov.in/floods_2018/) and [October 2018 post-disaster needs assessment](https://sdma.kerala.gov.in/wp-content/uploads/2020/08/Kerala-Post-Disaster-Needs-Assessment.pdf); [CWC reservoir/flood report archive reference](https://www.preventionweb.net/publication/study-report-kerala-floods-august-2018).
- [KSDMA 2019 government disaster memorandum](https://sdma.kerala.gov.in/disaster-memoranda/) and [documented 2019 flooding chronology](https://sdma.kerala.gov.in/wp-content/uploads/2026/03/LNOB_MB_CMID2026.pdf).
- [NDRF Pettimudi landslide report](https://www.ndrf.gov.in/en/operations/landslide-idukki-kerala-2020).
- [KSDMA October 2021 event report](https://sdma.kerala.gov.in/wp-content/uploads/2022/05/Event-report_October-2021.pdf).
- [KSDMA Meppadi 2024 memorandum](https://sdma.kerala.gov.in/disaster-memoranda/).
- [21 September 2026 report of localized Nilambur flash flood](https://www.newindianexpress.com/states/kerala/2026/Sep/21/flash-flood-in-kottapuzha-river-claims-five-lives-in-nilambur-one-missing).

**Do not label every monsoon season as a statewide flood.** The 2018 and 2019 disasters, 2020 Pettimudi and 2024 Wayanad landslides, 2021 October flood and September 2026 Nilambur flash flood differ in timing, catchment and mechanism. A candidate event catalogue may expand only with verified KSDMA/IMD district dates and mapped footprints; 2023/2025 must not be invented as identical flood events.

## ERA5 join: source available elsewhere, not executed here

Previous Kerala2040 ERA5 acquisition concerns **five representative points during FY2024–25**, hourly `t2m`, `u10`, `v10`, `ssrd` and `tp`. No original daily ERA5 CSV/NetCDF and no full **2018–2026 ERA5** chronology was accessible to this execution. The present script accepts a source-audited `--weather-daily` CSV with **one explicit IST calendar day per row**, daily `rainfall_mm` and optional daily `t2m_c`, with documented geographic aggregation upstream. Never treat 5 point measurements as an area-weighted Kerala rainfall estimate, or sum ERA5 accumulated fields without checking conventions.

Next controlled extension: acquire and aggregate *basin-specific* 2018–2026 ERA5 (`tp` and `t2m`) at suitable drainage-basin polygons or transparent location proxies; compare lagged 0–7-day rainfall, 7/30-day accumulated rainfall, antecedent storage/inflow and electricity demand while controlling calendar effects and verifying spatial coverage. For 2018, link only to independent historic KSEB/CEA energy reporting **if dated data are located**; otherwise report hydrology/impact without an SLDC 2018 load figure.

## Pumped-storage hydro: separate project and constraints ledger

The [CEA's Kerala hydro-development profile](https://cea.nic.in/wp-content/uploads/hpi/2024/10/State_Profile_on_Hydro_Development.pdf) listed **two proposed 600 MW pumped-storage entries**: Idukki (600 MW) and Pallivasal (600 MW), with allocation/feasibility still open in the dated 2024 snapshot. They are **not** existing verified pumped-storage capacity, not annual generation MU and not evidence that full-flood-season pumping can be scheduled. The separately proposed [Idukki Extension Scheme, 800 MW, under Survey & Investigation in a February 2025 Government of India answer](https://powermin.gov.in/sites/default/files/uploads/LS06.02.2025_Eng.pdf) must not be counted as the Idukki **600 MW pumped-storage project**; extension and PSP technology are separate classifications.

A [Kerala State Planning Board technical study](https://spb.kerala.gov.in/sites/default/files/inline-files/3.PUMP_.pdf) examined head-to-waterway ratios of existing hydro schemes, citing Idukki and Kuttiyadi, but **an indicative ratio is not a DPR, ecological clearance, operating head, pump efficiency, lower reservoir capacity or grid availability**. The State also has flood-control and downstream safety duties; pumping **does not destroy floodwater** and water returned to the upper reservoir requires explicitly reserved headroom, spill rules and lower-basin safety. A hypothetical round-trip efficiency (e.g. 75–80%) would be a scenario assumption, never an observed Kerala plant parameter.

A screened candidate requires (a) independently verified upper/lower reservoirs and civil topology; (b) head and active water volume; (c) wet/dry season rule curves and downstream spill constraints; (d) pump/turbine ratings and efficiencies; (e) transmission deliverability and prices; (f) verified legal and ecological exclusions. Pumping during extreme flood conditions cannot be recommended without flood-operations design.

## Energy Atlas / EnergyMap: complement, not substitution

[Catalogue](https://www.energymap.in/data) advertises plant registry, interstate flows, NPP daily plant output, 15-minute **RLDC metered renewable** generation and grid operation/PSP datasets; per-state and per-source coverage **still must be verified**. [Kerala dashboard](https://www.energymap.in/states/kerala) labels its real-time demand **modelled** and per-plant settled output a separate Growth-tier offering. [Grid registry](https://www.energymap.in/data-shop/grid-registry) is a partial reference snapshot, not historical availability or hosting capability.

The `--atlas-observed` interface requires date, metric, value, explicit observed/metered `source_type`, a source label, source_url and affirmative verified flag. It **rejects** modelled/blended rows and **keeps accepted rows in a separate private candidate file**, not silently blended into official SLDC daily energy. Source labels alone are not independently verified: check sample against original CEA/RLDC/settlement documents, units/boundaries and access/licence before publication or model use. At execution time no Energy Atlas observed extract was present: **0 Atlas rows integrated**, not a claim that none exist.

## Technical reproducibility and data-sharing

Run `python analysis/analyze_sldc_hydro_flood_weather.py --curated <private-curated-folder> --out <private-output-folder>`. Optional `--weather-daily` and `--atlas-observed` arguments activate only when real auditable input CSVs are provided. Public repo may hold this report, source-safe QA and code; original HTML and date-level source rows stay in the private research archive. No generation or import inference for source gaps; no causal attribution or pumped storage estimate at this stage.
