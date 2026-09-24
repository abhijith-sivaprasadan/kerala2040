<div align="center">

![Kerala2040 — our land, our energy future](docs/assets/social-card.svg)

# Kerala2040

**കേരളത്തിന്റെ ഊർജഭാവി · Our land. Our energy future.**

*An open, evidence-first research project on Kerala’s electricity system, energy resilience and possible pathways to 2040.*

[Explore the website](https://kerala2040.github.io/) · [Methodology](docs/methodology.md) · [Evidence](docs/evidence_register.md) · [Next steps](docs/NEXT_STEPS.md)

</div>

---

## The question

**What would it take for Kerala to meet its future energy needs more reliably, affordably and sustainably—while remaining connected to India's grid, protecting land and water, and making investment financially credible?**

Kerala2040 investigates electricity demand, in-state generation, interstate imports, hydro and monsoon exposure, solar, wind, storage, grid flexibility, ecological constraints and financing. It starts with a defensible historical system account before comparing possible 2030–2040 pathways. Energy sovereignty here means *less forced dependence and more resilience*, **not** electricity autarky.

This is independent research by [Abhijith Sivaprasadan](https://github.com/abhijith-sivaprasadan). It is **not an official Government of Kerala, KSEBL or SLDC forecast, policy recommendation or approved development plan**.

## Explore the project

| Start here | What it answers |
|---|---|
| **[Public research experience](https://kerala2040.github.io/)** | A Kerala-rooted guide through the energy question, observed evidence, maps, scenarios and open questions. |
| **[Research methodology](docs/methodology.md)** | How sources become constraints, calibrated models and explicit scenario comparisons. |
| **[Evidence and provenance](docs/PROVENANCE_CORE_RULES.md)** | What counts as observed, reported, reanalysis, derived, proxy or external-study evidence. |
| **[Research plan](docs/research_plan.md)** | Work packages spanning demand, hydro, renewables, grid, ecology, circular industry and finance. |
| **[Readiness and missing inputs](docs/AUDIT_RELEASE_GATES.md)** | Why source acquisition or a solver run alone does not make a 2040 result defensible. |
| **[Release notes](docs/releases/v1.0.1.md)** | The historical-data publication and its precise limitations. |

The [website](https://kerala2040.github.io/) is a *published, pinned evidence snapshot*. The `main` branch is ongoing research and may contain newer analysis than the deployed website; the site's `SOURCE_COMMIT` and `RELEASE_MANIFEST.json` identify its exact source version. Do not mistake development-only results for published findings.

## KMML circular-industry case · CET 2026 / 24 September 2026

[Source-qualified process chapter](docs/KMML_CIRCULAR_INDUSTRY_CASE_2026_09_24.md) · [Ten-stream auditable case register](data/evidence/industry/kmml_source_bounded_case_2026_09_24.json) · [Interactive Industry process explorer](https://kerala2040.github.io/#industry).

Kerala Minerals and Metals Ltd's official chloride-route descriptions allow us to distinguish **nine separate units/branches**, including the existing HCl regeneration loop, and **ten non-interchangeable material, water and energy streams**. Its **FY2022–23** annual report records 10 MT of *sponge iron from oxide in two trials*, TiO2 fines of 1–2 g/L in U400 polishing-pond overflow and a separate approximately 300 m³/day filter-backwash claim; neither the pilot quantities nor historical nameplate capacities are current annual performance. Iron oxide brick commercialization is a separate **historical** company claim; the titanium-sponge line is a different product. This is a **completed descriptive process study**, not quantified recovery, annual savings, emissions, or independent regulatory approval. The measured KMML release gate stays closed.

## Kerala Total Energy Atlas: official sector emissions and fuel-method crosswalk · 24 September 2026

[Official CY2023 sectoral GHG research chapter](docs/KERALA_TOTAL_ENERGY_ATLAS_SECTOR_GHG_METHODS_2026_09_24.md) · [source-labelled 2023 emissions & historic GCV register](data/evidence/total_energy/kerala_ghg_sector_bridge_2026_09_24.json) · [dynamic homepage comparison](https://kerala2040.github.io/#overview).

The [Kerala DoECC Energy GHG portal](https://climatechange.envt.kerala.gov.in/emissions-estimates/energy/) reports **calendar-2023 energy-sector 20.64 MtCO₂e** with source categories transport **13.59**, residential energy **3.20**, and industrial energy **1.89 MtCO₂e**. These are **modelled emissions and partial categories**, NOT energy (Mtoe), all fuel-tonnes, electricity input or FY2024–25 final consumption. Its prior June 2024 2005–2021 report gives 2020 **16.96 MtCO₂e**, whereas the current portal cites **17.09 MtCO₂e**, so inventory vintages are **not spliced**. The official BEE/CII/EMC action-plan annex supplies historic **gross**, not net, fuel calorific values; multiplying them by unverified FY2024–25 petroleum sales to announce a total-energy balance is prohibited. A structured data-request pack for PPAC, EMC/CII/BEE and DoECC is complete but **not sent**. The current FY2024–25 fuel×sector energy, import balance and current emissions release gates remain closed; the research workbench now indexes this distinct source-scoped stream.

## Petroleum product sales by full financial year · Kerala Total Energy Atlas · 24 September 2026

[Source and revision audit](docs/PPAC_KERALA_FULL_YEAR_SALES_SOURCE_AUDIT_2026_09_24.md) · [Annual sales evidence register](data/evidence/total_energy/ppac_full_fy_kerala_source_audit_2026_09_24.json) · [Live interactive charts](https://kerala2040.github.io/#overview).

Six **full-fiscal-year** Kerala PPAC all-petroleum-product sales rows FY2019–20 through FY2024–25 have been extracted with distinct source tiers. Original PPAC indexed historical PDF text covers 2019–20–2023–24; the FY2024–25 all-POL **6,939.7 thousand tonnes**, petrol **1,879.4**, diesel **2,419.3** come from a named, full-text reproduction of PPAC's exact FY2024–25 Ready Reckoner, while its original publisher PDF image is **not accessible/verified** and remains a release caveat. Petrol/diesel are within the all-POL total, not additional tonnage. FY2019–20 HSD is missing, not zero; 2022–23 publication revisions are recorded. PPAC sales mass is never promoted to Kerala in-state final energy, an import fraction or sector fuel use. EMC's source fuel×sector calculation workbook was not publicly located and its original-data/corrigendum request is documented; original H1 record remains separate. Two additional source-inspectable interactive homepage charts and full tests have been added.

## Kerala Total Energy Atlas · historical baseline and provisional fuel sales · 24 September 2026

[Source-verified first chapter](docs/KERALA_TOTAL_ENERGY_ATLAS_BASELINE_2026_09_24.md) · [machine-readable temporal/source register](data/evidence/total_energy/kerala_total_energy_source_register_2026_09_24.json) · [interactive homepage atlas](https://kerala2040.github.io/#overview).

This **new non-electricity workstream** admits EMC/CII's original six **FY2014–15–FY2019–20** Kerala total-final-energy graphic (9.18 → 10.78 Mtoe), and its **FY2019–20 integer-rounded** source shares: oil 64%, utility electricity 19%, imported coal 16%, gas 1%. The year-ending labels, rounded-share limitations and historical reporting boundary are recorded in the source register. A separate **PPAC provisional April–September 2024 selected-product sales** panel adds LPG, petrol, diesel, ATF and SKO in thousand metric tonnes. PPAC PDF indexed text was retrieved, but direct original-PDF visual/download access failed; these provisional sales **remain page-image-QA pending**, and are not annualised. PPAC 2024 nominal refinery/LNG/retail infrastructure is tagged context only. Three new homepage graphs render interactive source values and coverage notes. A **current FY2024–25 all-carrier final-energy balance, sector demand, fuel import share and emissions remain null**, not filled using unrelated annual electricity or infrastructure.

## Latest verified milestone · 22 September 2026

**The NIWE 150 m Kerala wind-resource × GLO-90 surface-terrain analysis has been executed on real, hash-verified inputs.** From 19,475,568 national atlas rows, the original NWIC Kerala polygon selects **200,692** onshore resource point centres; the modelled wind-speed median is **3.91 m/s at 150 m**. Sampling the independently derived 90 m GLO-90 DSM slope yields **199,853** finite slope results and **839** missing samples. The median sampled DSM slope is **4.96°**.

A 16-combination wind-speed × surface-slope matrix and point-count histogram are now documented in the [executed result](docs/NIWE_150M_KERALA_TERRAIN_REAL_DATA_RESULT_2026_09_22.md) and [machine-readable audit](data/evidence/gis/niwe_150m_kerala_real_wind_DSM_slope_2026_09_22.json), with a [reproducible original-source clip rebuild](scripts/rebuild_kerala_niwe_clip_from_originals.py). **These are modelled resource-point statistics—not legally eligible land, wind-farm layouts, actual generation, km² or MW.** Private source rows and NIWE-derived maps are not republished in this public repo.

**LRIS 2.0 reconnaissance** identified an all-district layer catalogue; browser-served district/block/local-body GeoJSON; Level 1/2 land-use, roads and slope *summary* JSON; and GeoServer WMS map images. The tested standard WFS endpoint returned **“Service WFS is disabled.”** This does not disprove other authorised GIS access; no underlying land-use polygons or notification-linked forest/paddy/ESZ exclusions have been acquired from LRIS. See [the source-scoped LRIS inventory](data/evidence/gis/lris_public_services_discovery_2026_09_22.json).

### District-level wind and terrain: exact point partition achieved

The original **NWIC District Boundary GeoJSON** was checked against the same NWIC-state-clipped NIWE source points and GLO-90 DSM-slope samples. All **200,692** points are uniquely assigned across **14** NWIC Kerala district geometries: **0 unmatched, 0 multiply assigned**. All 199,853 valid and 839 missing slope samples, wind/slope histograms and all 16 hypothetical threshold totals reconcile. [Completed district report](docs/NIWE_NWIC_DISTRICT_WIND_TERRAIN_RESULT_2026_09_22.md) · [public-safe 14-district aggregate](data/evidence/gis/niwe_nwic_district_wind_terrain_2026_09_22.json).

**The earlier LRIS partition finding remains part of the audit history:** the separate LRIS geometry left 330 NIWE points unmatched; NWIC closes this population without moving points to a nearby district. District totals also change because LRIS and NWIC trace different source-defined boundaries. No original polygons or private NIWE point rows are redistributed.

Completeness here applies **only to descriptive administrative point assignment**, not land-use clearance, notified forest/paddy/wetland/ESZ boundaries, turbine siting, grid hosting, source-vintage/reuse-rights review, eligible km² or feasible MW. Every such capacity/model gate remains closed.

### Website research experience · interactive source charts and topic navigation · 24 September 2026

The historical electricity, wind and solar figure galleries now render **from audited packaged aggregate JSON and the pinned research ledger**, not linked pre-rendered SVG images. Nine newly interactive charts expose per-point source readouts, touch/click, keyboard arrow inspection and source tables; comparison plots also expose series controls, while wind supports original source-threshold and district selectors. The existing FY2024–25 monthly electricity and hydro timelines now offer date-aware readouts without filling missing days. Sitewide link navigation exposes **all eight topics** on every view; mobile navigation switches before the header becomes overcrowded.

The official annual KSEBL-attributed historical series is **distinct from the pinned SLDC FY2024–25 observed-day bundle** and has independent source/coverage admission checks. The static SVGs remain as optional repository poster exports, not the browser's chart engine. The website repository still pins its own immutable research commit; a research merge alone never automatically advances that release pointer.

### Historical electricity story · CET source-audited synthesis · 24 September 2026

**The historical electricity chapter now has a defined research answer, not only a list of inputs:** the [KSEBL-attributed annual state-consumption series](docs/CET_HISTORICAL_ELECTRICITY_STORY_2026_09_24.md) rises from **22,540.32 MU (FY2020–21)** to **29,311.76 MU (FY2024–25)**; separately, Kerala SLDC source-matched operational daily consumption rises **24.12% on 356 paired calendar dates** from FY2020–21 to FY2025–26. Net import and hydel shares are reported on **qualified observed FY days**, with explicit FY coverage, and evening peak fields are never represented as metered hourly load. **The KSEBL and SLDC numbers use different reporting boundaries even when the SLDC FY has 365/365 days; do not subtract them to invent losses or an annual correction.**

[Conference-ready four-figure chapter](docs/CET_HISTORICAL_ELECTRICITY_STORY_2026_09_24.md) · [Machine-readable audit](data/evidence/sldc/cet_historical_electricity_story_2026_09_24.json). The 11 missing FY2024–25 SLDC dates, measured interval load/interchange and full cross-source boundary reconciliation remain open. This finished **descriptive history** is not a validated 2040 system optimisation or a public-site release promotion.

### Historical SLDC five-section source audit · 23 September 2026

**Kerala SLDC five-section reports spanning 6 August 2019–23 September 2026 have been collected and normalized offline, without inventing hourly measurements.** Across 2,606 requested calendar dates, Statistics and Imports contain **2,576** source-dated and SHA-256-matched reports each, while Storage, Availability and Others contain **2,577** each. The 2019–2021 Statistics schema includes 614 earlier reduced-layout pages and the newer layout has 1,962 reports. The first day is a selected crawl boundary, not a verified date of first SLDC publication.

The daily energy balance identifies one anomalous **5 December 2019** source record; its reported values are preserved but excluded from qualified consumption analysis. FY2024–25 remains **354/365 observed daily records** (30,666.2569 MU summed across those observed days, **not** a full-year total), and there is **no actual continuous 15/30/60-minute demand or generation chronology** in these reports. [Research audit and findings](docs/SLDC_FIVE_SECTION_2019_2026_SOURCE_AUDIT_2026_09_23.md) · [Public-safe evidence QA](data/evidence/sldc/sldc_five_section_2019_2026_public_qa_2026_09_23.json) · [Offline reproducer](scripts/process_sldc_five_section_archive.py).

Nine gzip-compressed curated CSV tables and their SHA-256 manifest are verified in the separate **private** [`kerala2040-source-archive`](https://github.com/abhijith-sivaprasadan/kerala2040-source-archive/tree/main/curated/sldc_2019_2026) repository ([merged private PR #1](https://github.com/abhijith-sivaprasadan/kerala2040-source-archive/pull/1)). The original third-party HTML ZIP remains in the user-held source archive; no source HTML or source-labelled private CSV table is committed to this public research repository. Private access does not grant public redistribution rights.

### Idukki hydro–energy pilot · phase 4 · 23 September 2026

The first **source-matched Idukki station + reservoir** pilot links 2,606 source-calendar dates, including 1,359 Idukki-gauge rainfall dates, 2,414 inflow dates, 2,546 named-station generation dates and 2,577 reservoir storage volumes. The observed rain–inflow one-day-lag association is descriptive; the **434-train / 158-test** complete-case retrospective inflow model reduces held-out MAE **37.24% relative to previous-day persistence**, but uses same-day observed rain and is **not** a forecasting or flood-causal result. A flood-event comparison and **illustrative, non-project-specific** pumped-storage physics audit are included. The **2018 SLDC energy, ERA5-Land basin weather, verified Atlas metered rows, turbine releases and operating PSP constraints remain unavailable/not integrated.**

[Phase-4 research report](docs/PHASE4_IDUKKI_HYDRO_ENERGY_RESEARCH_2026_09_23.md) · [source-safe aggregate audit](data/evidence/sldc/idukki_hydro_energy_phase4_2026_09_23.json) · [reproducible retrospective pipeline](analysis/idukki_hydro_energy_phase4.py) · [opt-in ERA5-Land original acquisition request planner](scripts/request_era5_land_hydro_monthly.py). Date-level source rows stay private.

### Electricity demand and affordability · official annual source review · 23 September 2026

A separate **non-renewable workstream** now establishes the FY2024–25 KSEBL customer-category energy/revenue baseline and the different official boundaries for Kerala consumption, KSEBL sales, energy entering Kerala and incomplete SLDC observed-day reports. In particular, **29,311.76 MU** official broad consumption, **28,544.05 MU** category-table sale including trading, and **32,306.15 MU** system periphery input are **not interchangeable measures of hourly demand**; the existing 30,666.2569 MU SLDC total covers only 354 days and has a separate operational definition. There is **no new 8,760-hour measured load, 2040 demand projection, or cost-to-serve model** here.

[Official-source demand-sector/accounting review](docs/DEMAND_SECTOR_ACCOUNTING_BASELINE_2026_09_23.md) · [Existing metered interval data request](docs/SLDC_DATA_REQUEST_DRAFT.md) · [Historical demand gap](docs/hourly_demand_gap.md).

### ERA5-Land August 2019 · real-source exploratory weather audit · 24 September 2026

The first actual **user-supplied original ERA5-Land GRIB** pilot has now processed **24 parameters** for August 2019, with 31 fully complete IST days of core rainfall on **1,034 valid 0.1° source land pixels**, a separate audited July boundary day, original forecast-step deaccumulation, 50:50 allocation of the hourly accumulation crossing IST midnight, and exact-array verification of a redundant 31 August download. Source GDAL mislabels numerical kelvin as Celsius and lacks the label for ECMWF potential evaporation parameter 228251; both are source-mapped explicitly. The **entire bounding-box land footprint contains areas outside Kerala**, and the example Idukki-vicinity rectangle is **not a verified reservoir watershed**. Illustrative full-bbox/rectangle rainfall totals **380.65/537.73 mm for August** are NOT state or catchment rainfall findings; all user source files and detailed cell/day outputs remain out of the public repo. **Verified catchment rainfall dates, new inflow scores, and 2018 electricity: still zero.**

[Real-GRIB August exploratory audit](docs/ERA5_LAND_AUG2019_ORIGINALS_EXPLORATORY_AUDIT_2026_09_24.md) · [Verified-catchment Phase 5 gate](docs/PHASE5_IDUKKI_ERA5_BASIN_WEATHER_2026_09_23.md).

### Idukki basin-weather Phase 5 · implementation only · 23 September 2026

**The next-stage ERA5-Land → Idukki basin weather workflow is implemented, not yet executed against a verified catchment and original reanalysis data.** Offline GRIB extraction, an independent catchment-polygon-to-equal-area-pixel-weight builder, strict ERA5-Land hourly deaccumulation and IST daily QA, and paired chronological gauge-versus-basin inflow experiments are available. The original rainfall accumulation at 00 UTC belongs to the preceding day; a date is admitted only with **all 25 original hourly inputs (23 full and two 50%-allocated midnight-crossing intervals) at every weighted grid cell**. A catchment polygon must represent the Idukki **reservoir-intercepted area**, not the entire Periyar basin or a district.

**Verified Idukki-reservoir catchment weather dates processed: 0. New catchment inflow holdout skill estimates: none.** The pre-existing five-point FY2024–25 ERA5 chronology does not meet this basin gate. This does not supersede the executed Phase 4 results or unlock a 2018 electricity history or a pumped-storage feasibility conclusion.

[Phase 5 research status and private execution workflow](docs/PHASE5_IDUKKI_ERA5_BASIN_WEATHER_2026_09_23.md) · [Offline source GRIB extractor](scripts/extract_idukki_era5_land_grib.py) · [Reviewed-catchment weights](scripts/build_idukki_phase5_weights.py) · [IST daily and paired-model processor](analysis/idukki_phase5_weather.py).

### SLDC daily advanced analysis · phase 2 · 23 September 2026

**No-imputation, matched-calendar-date analysis** of the verified 2019–2026 SLDC archive: FY2020–21 to FY2025–26 consumption on 356 matched month/days changes **+24.1%** (68.88 → 85.49 MU/day), while FY2023–24 to FY2025–26 changes **+1.17%** on 355 paired month/days. Observed import and hydel energy shares vary materially; the source Statistics Evening Peak reaches 6,195 MW on 23 April 2026, but differs from the separately reported Others evening extrema. Named Idukki reservoir seasonality and an independently rechecked source error in the 13 March 2026 KUNDALA percentage are included. **All confirmed missing days remain missing; no full-year totals or hourly series are inferred.**

[Advanced research report](docs/SLDC_ADVANCED_DAILY_ANALYSIS_2026_09_23.md) · [Aggregate machine-readable analysis](data/evidence/sldc/sldc_daily_advanced_aggregate_2026_09_23.json) · [Reproducible offline analysis](analysis/analyze_sldc_2019_2026.py). The private curated day/row tables remain in the separate source archive and are not redistributed here.

### Solar phase 1 closeout · 23 September 2026

**The bounded descriptive solar-PV source-resource and paired-seasonality analysis is complete.** Rechecked all 14 original GSA 2.0 yearly/daily/monthly native 30-arcsecond windows against original NWIC district boundaries. Exactly **46,241** Kerala PVOUT pixel centres uniquely enter the 14 source-defined districts: **zero missing source values across annual + daily + all 12 months**, zero overlap, zero inferred nearest-district allocation. The long-term publisher-reference-system median annual PVOUT is **1,493.51 kWh/kWp/year**. Paired February and July per original source pixel yield median **2.267 kWh/kWp/day** difference and **43.60%** decrease; district paired median decline examples **32.23% in Thiruvananthapuram** and **49.22% in Wayanad**.

[Solar phase 1 report and frozen research question](docs/SOLAR_PHASE1_NWIC_DISTRICT_SEASONALITY_RESULT_2026_09_23.md) · [Source-safe aggregate + exact QA](data/evidence/solar/gsa2_nwic_district_paired_seasonality_2026_09_23.json) · [12-month poster figure](docs/assets/solar-phase1-monthly-20260923.svg) · [Annual district comparison](docs/assets/solar-phase1-district-annual-20260923.svg) · [Paired seasonal district figure](docs/assets/solar-phase1-district-seasonality-20260923.svg).

**Source limit:** GSA's 1999–2018 publisher-modelled reference-PV climatology is not actual FY2024–25 generation, a plant design, permitted roof/land/water area or installable MW. Source reuse rights and real-fleet yield calibration remain open; solar is **not admitted to the 2040 model**.

### Wind phase 1 closeout · 23 September 2026

**The bounded, descriptive onshore-wind resource and terrain analysis is complete.** The original-source NIWE 150 m × GLO-90 DSM × NWIC district workflow accounts for all **200,692** Kerala point centres in 14 districts, with **199,853** valid and **839** missing slope samples. We now publish district-normalized percentages and all 16 speed/slope threshold sensitivities, not just raw counts. The illustrative **≥7 m/s, ≤10°** subset contains **8,637** modelled resource centres statewide (4.3217% of valid-slope centres), including **6,330 / 23,020** in Palakkad (27.4978%) and **1,804 / 22,328** in Idukki (8.0795%). These are *source-point* fractions, **not developable district area or construction priorities**.

[Wind phase 1 research report](docs/WIND_PHASE1_DISTRICT_NORMALIZED_CLOSEOUT_2026_09_23.md) · [Normalized aggregate and denominator QA](data/evidence/gis/niwe_nwic_district_normalized_wind_terrain_2026_09_23.json) · [Poster figure: district comparison](docs/assets/wind-district-normalized-20260923.svg) · [Poster figure: terrain response](docs/assets/wind-terrain-sensitivity-20260923.svg)

**Out of phase 1 scope:** legal forest/paddy/wetland/ESZ land eligibility, access and turbine pads, turbine model and yield, measured hourly wind, KSEBL connection/hosting and feasible MW. Source use rights and vintage are not independently verified. They remain separate research gates—not tasks silently labelled complete under Wind.

## What has actually been established?

*Research status: 23 September 2026. Source coverage and scientific model readiness are separate things.*

| Area | Current evidence | Not yet established |
|---|---|---|
| **Electricity baseline** | 354 observed SLDC daily dates in FY2024–25; observed-day source-attribution PyPSA replay. [Daily model](docs/OBSERVED_DAILY_PYPSA.md). | The 11 missing dates; measured continuous statewide hourly / 15-minute load and interchange; calibrated hourly dispatch. |
| **Weather** | ERA5 source/chronology QA for five representative locations × 8,760 UTC hours = 43,800 point-hours. [Source QA](data/evidence/weather/era5_fy2024_25_source_qa_2026_09_21.json). | Validated statewide weather-to-generation modelling. |
| **Solar** | **Phase 1 descriptive PVOUT complete:** 46,241 native pixels assigned once across 14 NWIC districts, all 12 monthly layers matched, 43.60% median paired Feb→Jul decline. GHI native clip separately audited. [Solar research result](docs/SOLAR_PHASE1_NWIC_DISTRICT_SEASONALITY_RESULT_2026_09_23.md). | Measured FY2024–25 PV validation and rooftop/ground/floating buildable MW. |
| **Wind** | **Phase 1 descriptive analysis complete:** 200,692 NIWE centres, 199,853 valid slope samples, all 14 NWIC districts and district-normalized 16-threshold wind × terrain sensitivity. [Full wind closeout](docs/WIND_PHASE1_DISTRICT_NORMALIZED_CLOSEOUT_2026_09_23.md). | Legally eligible sites, turbine layout, actual hourly yield, buildable MW, grid evacuation and offshore resource assessment. |
| **Hydro, grid and land** | Source inventories, terrain/hazard QA and LRIS public-service discovery, including the tested disabled WFS route. [LRIS evidence](data/evidence/gis/lris_public_services_discovery_2026_09_22.json). | Verified reservoir cascades/operations, connection-point hosting capacity and notification-linked, technology-specific statutory GIS screens. |
| **2040 scenarios** | Source-labelled benchmark pathways and explicitly proxy-labelled PyPSA sensitivities. [Limitations](docs/PYPSA_2040_PROXY_SCREENING.md). | Calibrated least-cost, reliable or permitted 2040 build-out. |

**Available data are not automatically approved model inputs.** In the downloaded NWDP FY2024–25 solar series, **6,007 of 6,007 values were zero, including daytime**: it cannot validate PV output. Five-point ERA5-to-PV/wind hourly results are illustrative *proxies*, not measured generation or Kerala-wide predictions. No defensible buildable solar/wind MW is currently claimed. See the [renewables handoff](docs/RENEWABLE_FIVE_STEP_HANDOFF_2026_09_22.md) and [capacity gates](data/evidence/solar/solar_wind_feasible_capacity_gates_2026_09_22.json).

## How the research is designed

```text
Source files + source permissions + provenance
                    │
                    ▼
       Acquisition → byte/units/time QA
                    │
                    ▼
       Historical electricity reconciliation
                    │
         ┌──────────┴──────────┐
         ▼                     ▼
   Weather & resource     Hydro & land/grid
   conversion checks      spatial constraints
         └──────────┬──────────┘
                    ▼
          Calibrated system model
                    │
                    ▼
   2040 scenario, reliability & cost tests
                    │
                    ▼
     Ecological + fiscal trade-off reporting
```

The direction of travel is *evidence → validation → constraints → model → uncertainty*. Missing source fields stay missing; they are not silently replaced by convenient numbers. See the [provenance contract](docs/PROVENANCE_CORE_RULES.md) and [methodology](docs/methodology.md).

## Solar and wind: a dedicated research track

The September 2026 acquisition includes Global Solar Atlas India rasters, the NIWE wind atlas, solar studies and selected NWDP telemetry. The official NWIC Kerala state geometry is used for **descriptive native-grid, pixel-/point-centre clips**; clipping does not establish legal site eligibility. Five representative-point FY2024–25 ERA5 profiles are a **sensitivity exercise**, not validated generation.

Five downloaded source-folder trees have been uploaded to and independently SHA-256-restored from a **separate private archive**. A subsequent **26-layer India GSA PVOUT native-grid consistency audit passed across 8,796,068 valid-positive cells per comparison**; it verifies internal annual/monthly-versus-daily representation, **not** FY2024–25 PV generation or buildable capacity. The PDF inventory rendered all 2,945 pages, but page-by-page visual interpretation remains pending. Public records retain provenance and asset hashes, **not the third-party raw data**:

- [What is archived and what was verified](data/evidence/solar/renewable_five_folder_private_archive_2026_09_22.json)
- [Solar and wind source interpretation](docs/SOLAR_WIND_CONSOLIDATED_ANALYSIS_2026_09_22.md)
- [Kerala-native resource clipping](docs/KERALA_NATIVE_RENEWABLE_RESOURCE_CLIPS_2026_09_22.md)
- [Executed NIWE wind × DSM slope analysis](docs/NIWE_150M_KERALA_TERRAIN_REAL_DATA_RESULT_2026_09_22.md)
- [Completed NWIC 14-district wind × DSM partition](docs/NIWE_NWIC_DISTRICT_WIND_TERRAIN_RESULT_2026_09_22.md)
- [Completed wind phase 1: normalized district sensitivity and poster figures](docs/WIND_PHASE1_DISTRICT_NORMALIZED_CLOSEOUT_2026_09_23.md)
- [Audited 14-district aggregate without source coordinates](data/evidence/gis/niwe_nwic_district_wind_terrain_2026_09_22.json)
- [NIWE × slope public-safe aggregate results](data/evidence/gis/niwe_150m_kerala_real_wind_DSM_slope_2026_09_22.json)
- [LRIS 2.0 public-service discovery and disabled WFS record](data/evidence/gis/lris_public_services_discovery_2026_09_22.json)
- [Resource-to-capacity constraints](data/evidence/solar/solar_wind_feasible_capacity_gates_2026_09_22.json)
- [Reproducible five-folder archival workflow](scripts/archive_renewable_folders_private.py)
- [GeoTIFF pixel checks and every-page PDF visual review](docs/SOLAR_WIND_TIFF_PDF_REVIEW_2026_09_22.md)
- [Kerala SAC/NWDP wetlands × source GSA, NISE and NIWE crosswalk](docs/KERALA_WATERBODIES_SAC_NWDP_GSA_NISE_NIWE_2026_09_22.md)

Folder snapshots preserve nested *file bytes and hierarchy*. They do **not** prove that all 17 separately inventoried historic publisher-original ZIP/PDF byte streams were independently archived. The separate [exact-original manifest](data/evidence/solar/solar_batch_2026_09_21_originals_manifest.json) retains that distinction. Storage integrity does not grant redistribution rights or model admission.

## Run the research code

**Supported Python: 3.11–3.12.** These commands run from the public repository root; do not publish third-party source binaries or API tokens.

```powershell
git clone https://github.com/abhijith-sivaprasadan/kerala2040.git
cd kerala2040

py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"

python scripts/check_readiness.py
python scripts/build_site.py --check
python -m pytest
```

For GIS work, install the optional geospatial dependencies:

```powershell
python -m pip install -e ".[dev,geo]"
```

Build and preview the website:

```powershell
python scripts/build_site.py --output _site
python -m http.server 5173 --directory _site --bind 127.0.0.1
```

Open **http://127.0.0.1:5173/**, not `docs/index.html` as a file URL. For ingestion examples, see [next steps](docs/NEXT_STEPS.md) and [data connectivity](docs/data_connectivity_v1.md). Acquisition workflows may need network access, source permissions or local originals.

### Repository guide

| Location | Purpose |
|---|---|
| [`docs/`](docs/) | Public site source, methods, audits, figures and research handoffs |
| [`data/evidence/`](data/evidence/) | Versioned, source-qualified QA and evidence summaries |
| [`scripts/`](scripts/) | Acquisition, reconciliation, GIS, model and archive workflows |
| [`src/kerala2040/`](src/kerala2040/) | Reusable implementation |
| [`configs/`](configs/) | Source definitions, assumptions and release gates |
| [`tests/`](tests/) | Parser, integrity, scientific-contract and site checks |
| [`results/`](results/) | Locally generated model runs and figures; not automatically released |

## Contribute, cite, and reuse

Useful contributions include primary-source provenance, reproducible corrections, tests, Kerala-specific input data **with verified access terms**, and scrutiny of assumptions or units. Read [CONTRIBUTING.md](CONTRIBUTING.md) and [the decision log](docs/decision_log.md). Do not commit personal information, restricted network data or raw third-party files to the public repository.

Code is licensed under [MIT](LICENSE); **that licence does not relicense third-party datasets, imagery, reports or other attributed source material**. Cite the specific tagged research release using [CITATION.cff](CITATION.cff) and, where applicable, the upstream data publishers.

---

*Kerala2040 is built to make assumptions and unknowns inspectable—not to replace them with a single confident 2040 number.*
