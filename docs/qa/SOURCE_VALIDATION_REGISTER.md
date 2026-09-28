# Source validation register

**Audit date:** 28 September 2026

This register records whether the source behind a Kerala2040 claim is:

- **P1 — primary / first-party:** originating agency, regulator, utility, company or data producer;
- **P2 — primary-adjacent:** official meeting/order quoting the originating agency or a preserved indexed snapshot from an official publication;
- **S — secondary:** press/report/third party;
- **M — model product:** e.g. ERA5, GSA; authoritative as a data product but not a direct observation of Kerala's power system.

A source can be primary and still be stale. Vintage is audited separately.

## Electricity, demand and planning

| Source family | Class | What Kerala2040 uses it for | QA result |
|---|---|---|---|
| Kerala State Planning Board, Economic Review | P1 | annual consumption, generation, per-capita/statistical context | **GREEN**; keep accounting definitions/year |
| Kerala Development Report 2026 | P1 | 29.31 TWh / 816 kWh-person context | **GREEN** |
| KSEBL / Kerala SLDC daily reports | P1 | daily consumption, internal generation, imports, reservoir/station records | **GREEN with source gaps**; daily archive is not interval telemetry |
| CEA/KSERC Kerala Generation Resource Adequacy plan | P1 | future annual energy/peak scenarios and the **5904 MW** FY2024–25 planning-reference peak used in the load-proxy calibration | **GREEN as its own planning/accounting context**; do not relabel 5904 as the KSEBL recorded annual maximum |
| CEA Kerala Transmission Resource Adequacy plan (2026) | P1 | **5797 MW recorded FY2024–25 peak**, 5836 MW March-2026 peak, current TTC/ATC, future high demand, official transmission constraints/plans | **GREEN and especially valuable as independent network cross-check** |
| Forum of Regulators / CEA crunch-period presentation | P1/P2 | FY2024–25 Kerala 5,904 MW peak cross-check | **GREEN aggregate reference**; not hourly telemetry |
| CSTEP long-term Kerala scenario | external study | lower demand trajectory | **GREEN as a named scenario**, not truth |
| SRPC meeting documents | P1/P2 | earlier dated TTC/ATC snapshots | **GREEN if date named**; do not mix with 2026 snapshot |

### Population context correction

The current official Economic Review 2024 population table gives **36.207 million for Kerala in 2026** (36,207 thousand), sourced there to national population projections.

This supports the public site's approximate “36 million” language.

### Population / per-capita timing boundary

The public context intentionally juxtaposes a **2026 projected population (36.207 million)** with separately sourced **FY2024–25 electricity statistics**. The official FY2024–25 per-capita electricity figure **816 kWh/person/year** already embeds the population denominator used by that official statistical product.

Do **not** divide 29.31 TWh by the 2026 projected population and use the result to “correct” the official 816 kWh/person figure. They are different time/reference contexts. The +100 kWh/person × 36.207 million = 3.62 TWh calculation is explicitly an educational scale illustration using the 2026 projection, not a reconstruction of FY2024–25 per-capita consumption.

A much older Kerala projection publication gives a different 2026 value (~37.254 million). The current context should use the newer projection series and **must not mix projection vintages**.

**Status: GREEN after fixing the projection-series provenance in QA notes.**

## Weather and renewable resources

| Source | Class | Use | QA result |
|---|---|---|---|
| ECMWF ERA5-Land | M | hourly weather chronology | **GREEN data product**; reanalysis, not station measurement |
| Global Solar Atlas | M | annual/seasonal solar resource cross-check | **AMBER as independent model-product check**, not plant validation |
| NIWE wind resource | P1/M | long-term wind mean / resource context | **GREEN source**, but **not independent validation after the model is mean-anchored to it** |
| measured/public plant annual generation references | P1 where available | annual plausibility checks | **GREEN only at compatible plant/year boundary** |

### ERA5 precipitation processing

For Idukki Phase 5, the processor explicitly deaccumulates ERA5-Land accumulated precipitation and handles the UTC→IST half-hour boundary by splitting the straddling UTC hour 50/50.

The **50/50 split is an assumption of uniform rainfall within the hour**, not information from ERA5.

**Status: AMBER methodology; acceptable for daily aggregation if documented.**

## Generation fleet

| Source family | Use | QA |
|---|---|---|
| CEA installed-generation statistics | fleet totals / category definitions | **GREEN**, dated |
| KSEBL station lists / public records | asset identification | **GREEN with mapping limitations** |
| MNRE/ANERT/other official RE statistics | distributed/renewable cross-check | **GREEN when date/category matched** |

Small/distributed generation category differences must stay explicit. Do not claim that one table “misses” assets when its published category definition excludes them.

## Import and economic inputs

| Source | Use | QA |
|---|---|---|
| KSERC FY2023–24 true-up / KSEBL procurement record | ₹5.05/kWh weighted purchase case | **GREEN for that accounting boundary** |
| IEX FY2023–24 DAM market snapshot | ₹5.24/kWh average-MCP benchmark | **GREEN with boundary correction**: first-party IEX yearly snapshot gives MCP ₹5.23759/kWh and weighted MCP ₹5.17449/kWh. The model's ₹5.24 case is therefore an average-MCP proxy, not a volume-weighted purchase price. CERC's market-monitoring report independently gives the full-market weighted DAM price at about ₹5.16/kWh. |
| Kerala regulatory downstream-licensee order | ₹7.13/kWh high delivered-cost example | **GREEN as downstream stress proxy**, **RED as Kerala-border import tariff** |
| RBI CPI | nominal→real conversion | **GREEN** if exact index rows retained |
| CERC Order 12/SM/2026 (23 Aug 2026) + RE Tariff Regulations 2024 | debt/equity, RoE, loan interest and WACC-equivalent discount benchmark | **GREEN regulatory benchmark**: order states 70:30 debt/equity, 10.71% loan interest, 14% post-tax RoE for non-SHP RE and derives 9.08% post-tax WACC-equivalent discount factor for all non-SHP technologies. This remains a national regulatory benchmark, not a Kerala project WACC. |
| CEA *Report on Optimal Generation Capacity Mix for 2029–30, Version 2.0* (Apr 2023), Annexure financial parameters | solar/wind/BESS capex benchmark | **GREEN source/unit verification**: table is explicitly at 2021–22 cost level; solar declines to ₹4.1 Cr/MW (=₹41,000/kW), onshore wind ₹6 Cr/MW (=₹60,000/kW), 4-hour BESS ₹8.22→4.72 Cr/MW (=₹82,200→₹47,200/kW), 1% O&M and 14-year BESS life. Technical annexure gives 12% BESS round-trip losses (=88% efficiency). These are CEA planning assumptions, not Kerala EPC quotes. |

## Transmission network

### KSEBL public Grid Map / SLDs

**Class:** P1.  
**Use:** topology and equipment-text evidence.

**Status:** **GREEN structural**, subject to source date.

### KSEBL Power System Statistics 2022–23 snapshot

The repository's compact source is not an original PDF byte copy. It is a cryptographically pinned model-relevant snapshot preserved from **search-indexed text of the official KSEBL PDF** because the legacy KSEBL endpoint was inaccessible.

The snapshot correctly records:

- publisher/title;
- source date 31 March 2023;
- printed table/page ranges;
- indexed text locators;
- a payload SHA-256;
- `source_pdf_sha256 = null`.

This is good provenance behavior: no fake PDF hash was invented.

**Status: AMBER P2.** Suitable for historical screening evidence, weaker than original-byte archival evidence and potentially stale.

### Shornur/Shoranur independent check

The 2023 snapshot contains:

> Shornur 220/110 kV — 100 MVA × 1 = 100 MVA.

The 2026 CEA transmission plan reports existing Shoranur transformation as **200 MVA + 100 MVA** and still identifies transformer loading as a constraint, with additional transformation/rearrangement planned.

**Audit conclusion:**

- old 100 MVA source is genuine for its 2023 snapshot;
- it is not sufficient as the current whole-station capacity;
- the current hotspot geography is independently corroborated;
- quantitative Kerala2040 transformer loading should be downgraded.

### Independent line-corridor corroboration

The CEA 2026 plan independently identifies reinforcement/constraint work involving several areas also highlighted by Kerala2040's screen, including:

- Shoranur-related 220/110-kV corridors;
- Shornur–Koppam / nearby 110-kV reinforcement;
- Kalamassery–Edayar;
- Vennakkara / Malampuzha;
- Malaparamba / Shoranur area.

This is **S6 external physical/planning corroboration of hotspot geography**, not numerical validation of Kerala2040 flows.

## Hydrology and reservoirs

| Source | Use | QA |
|---|---|---|
| SLDC reservoir reports | rainfall/inflow/storage daily records | **GREEN for reported fields**, not basin hydrology |
| SLDC named-station generation | Idukki daily energy | **GREEN with gaps**, not turbine discharge |
| CEA Idukki project documentation | 649.3 km² catchment target / plant context | **GREEN as independent area target** |
| FAO reservoir literature | independent historical area cross-check | **supporting secondary/technical source** |
| LRIS KML/WMS geometry | watersheds/drains/waterbodies | **GREEN geometry provenance**, redistribution rights separate |
| NWIC/WRIS hydro boundaries | desired independent catchment gate | **NOT YET ADMITTED** |
| KSEB Dam Safety monthly workbooks | intended v1.5 direct storage/inflow | **GATED / unavailable in exact required bundle** |

No Phase 5 basin result may be promoted until the geometry gate passes.

### Idukki v1.3 storage and energy-equivalent trace

The retained FY2024–25 SLDC `reservoir_daily.csv` contains **354 Idukki rows** and explicitly carries the source columns `full_reservoir_storage_mcm`, `full_reservoir_storage_reported_mu`, `effective_storage_mcm`, `generation_capability_gross_mu` and `generation_capability_station_mu`.

For Idukki the source rows report:

- full reservoir storage: **1,460 MCM**;
- full reservoir reported capability: **2,190 MU**;
- therefore gross source ratio: **2,190,000 MWh / 1,460 MCM = 1,500 MWh/MCM**.

The v1.3 runner does **not** use 1,500. It derives a station-equivalent conversion from every admissible daily row:

`generation_capability_station_mu × 1000 / effective_storage_mcm`.

Independent QA recomputation over all **354 Idukki rows** gives median **1,470.00001987 MWh/MCM** (range approximately 1,469.9979–1,470.0017), matching the configured **1,470 MWh/MCM**.

This establishes provenance and arithmetic. It does **not** make 1,470 a first-principles hydraulic conversion: it inherits the SLDC source's station-generation-capability field and collapses changing head, turbine efficiency and hydraulic losses into one fixed operational equivalent.

KSEBL Dam Safety independently confirms the Idukki HEP installed capacity of **780 MW** and the physical Idukki/Cheruthoni/Kulamavu common-reservoir configuration; KSEBL's rule-level report states six 130 MW machines.

## GIS / ecology

| Source | Use | QA |
|---|---|---|
| NWIC official Kerala boundary | state clipping | **GREEN** |
| Copernicus GLO-90 | elevation/DSM | **GREEN raster source**, not DTM/buildability |
| GSI landslide layers | hazard geometry | **BLOCKED where invalid / incomplete** |
| KFD / WDPA protected-area evidence | conservation crosswalk | **AMBER / incomplete statutory exclusion stack** |
| NRSC LULC | historical land-use evidence | **AMBER depending product acquisition/provenance** |
| SAC waterbody / wetland products | water-resource context | **AMBER**, not complete legal exclusion |
| NIWE/NISE/GSA | renewable resource | **GREEN as resource products**, not siting permissions |

The absence of a layer is never interpreted as absence of a constraint.

## Kerala public examples

### CIAL

First-party CIAL AGM page states:

- **50 MW installed renewable-energy capacity**;
- excess solar produced during the day is supplied to the grid;
- BESS for nighttime solar use is underway;
- green hydrogen project is in final stage.

Source:  
https://cial.aero/News-Updates/AGM2025

**Status: GREEN.**

### Kochi Metro

First-party KMRL project page states rooftop 2.67 MWp + ground 2.719 MWp = **5.389 MWp** for the cited project configuration.

Source:  
https://corporate.kochimetro.org/the-project

A newer/current KMRL sustainability page also indicates solar deployment has continued to expand, so **5.389 MWp should be framed as the documented original/project-stage configuration, not necessarily total current 2026 solar capacity**.

**Status: AMBER current-capacity wording; GREEN historical/project figure.**

### Kochi Water Metro

FY2023–24 KWML Annual Report, energy-conservation section states:

- electric hybrid/LTO battery boat system;
- opportunity charging;
- terminal roofs and pontoon canopies designed for PV;
- **17 MWp PV installations can power the entire energy needs**;
- land-based solar action still in process.

Source:  
https://cdn-dev.watermetro.co.in/KMWL_Bilingual_Annual_Report_2023_24_bb6fbf9dce.pdf

**Status: GREEN only as envisaged/planning statement. Not installed 17 MWp.**

## Kerala context / social and geographic sources

| Claim | Source | QA |
|---|---|---|
| area 38,863 km² | Kerala DES | **GREEN** |
| 2026 projected population 36.207m | Kerala Economic Review 2024 table, national projection source | **GREEN** |
| FY24–25 29.31 TWh and 816 kWh/person | Kerala Development Report / Economic Review | **GREEN** |
| heavy-mineral Chavara deposit and ~0.82 Mt monazite | Kerala Mining & Geology | **GREEN** |
| Western Ghats/forest context | Kerala Forest Dept / established geography | **GREEN descriptive** |
| “God's Own Country” | tourism slogan | **context only**, not scientific descriptor |
| “Scandinavia of India” | not needed | **omit from headline/public identity** |

## Swedish comparison sources

| Claim | Source | QA |
|---|---|---|
| Sweden population 10,613,531 July 2026 | Statistics Sweden | **GREEN** |
| 2024 electricity use 125.3 TWh excluding losses | Swedish Energy Agency | **GREEN** |
| county land/population comparisons | SCB | **GREEN if exact year stated** |

These are orientation comparisons only. They are not efficiency rankings.

## Budget sources

### Kerala Budget 2025–26

Official Budget in Brief reports:

- **Power**: ₹1,156.76 crore 2025–26 BE.

Official Budget Speech states:

- ₹1,156.76 crore energy-sector allocation;
- **₹100 crore additional** for pumped/storage scheme;
- **₹1,088.80 crore** KSEBL outlay.

**Status: GREEN.**

### Pumped-storage planning estimates

Official/regulatory project material tied to G.O.(Rt) No.84/2024/POWER lists:

- Manjappara 30 MW — ₹180 crore;
- Mudirapuzha 100 MW — ₹573 crore;
- planning/feasibility stage.

**Status: GREEN as early estimates, not realized costs.**

## Industry / KMML / wider energy

KMML official qualitative process descriptions and historical technical documents are suitable for:

- process topology;
- known material streams;
- identifying measurement/recovery questions.

They do not establish a current measured plant-wide mass-energy-water balance.

**Status: GREEN qualitative / RED quantified current savings.**

EMC/CII total-energy statistics and PPAC fuel sales are historical contextual datasets. Preserve their dates/units and do not merge them as if contemporaneous.

## Source-quality rule for the conference

When a source has changed over time, the safest answer is:

> “My model used the source snapshot available for that model version. The QA pass found a newer authoritative source; I therefore updated the interpretation rather than pretending the older snapshot was current.”

That is exactly the correct response for Shornur.
