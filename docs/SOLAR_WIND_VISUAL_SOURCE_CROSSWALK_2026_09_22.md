# Kerala2040 — illustrated-source evidence crosswalk: NISE, NIWE and World Bank

**Review date:** 2026-09-22. **Purpose:** distinguish what the actual reports' maps, diagrams, data tables, and image-based annexures demonstrate from what the Kerala2040 generation/siting model is authorized to claim. **No source raw PDF images are rehosted here.** Citations refer to PDF page number (physical PDF count, not printed internal numbering).

## Source and review-status ledger

| Source | Actual material reached | Visual status |
|---|---|---|
| NISE, *Solar PV Potential of India: Floating Solar* (June 2026) | User-attached original 121-page PDF; physical pages 53–55, 61–73 and 99–101 inspected in page-image view alongside extracted tables. | **Selected methodology, maps, tables, Kerala annexure visually inspected.** Not a declaration that all 121 pages were independently read. |
| ESMAP/World Bank, *Global Photovoltaic Power Potential by Country* (June 2020) | [Official public 62-page PDF](https://documents1.worldbank.org/curated/en/466331592817725242/pdf/Global-Photovoltaic-Power-Potential-by-Country.pdf), physically viewed figures/tables on PDF pp.20 and 27–29 (printed pp.7 and 14–16), and read associated methodology on printed pp.6–16. | **Relevant tables/masks/maps visually inspected.** Public PDF filename matches the locally catalogued report; byte-for-byte equality with the user's private copy was not tested. |
| NIWE, *India's Wind Potential Atlas at 120m agl* (October 2019) | [Official report listing](https://niwe.res.in/Open_data_Set/technical_report/19/) and searchable [publisher PDF](https://niwe.res.in/static/pdf/India%27s_Wind_Potential_Atlas_at_120m_agl.pdf) including preface and state-wise tabular material. The official PDF endpoint could not be opened in page-image mode here; user's 77-page original exists in the private five-folder snapshot, not as a directly attached PDF in this conversation. | **Publisher-text and summary cross-check only; visual page-by-page and original SHA256 check still OPEN.** Do not label this atlas visually audited. |
| NIWE 150 m native atlas ZIP | User's earlier local spatial QA and separately archived Wind-folder nested ZIP. | **Distinct atlas, grid and vintage; NOT NIWE 120 m atlas tables.** No new binary grid analysis from this report review. |

## 1. NISE: report illustrations and Kerala annexure

### Geographic and siting pipeline (PDF pp.61–73)

- **PDF p.62, Figure 5:** the visible logic separates resource screening (GSA GHI), waterbody identity, water persistence, bathymetry and road/substation proximity; it is not a pixel-to-MW direct conversion. This **is a national study-specific decision tree**, not a Kerala legally certified approval map.
- **PDF pp.63–66, Figures 6–8:** the India GHI legend spans daily GHI classes including 4.1–4.5, 4.6–5.0 and 5.1–5.5 kWh/m²/day. The two other maps depict **10 km proximity to roads and to OSM substations**; these are adjacency masks, not actual feeder hosting capacity or proof of a usable interconnection. The text mentions retaining a 2 km road buffer for future expansion; retain exact source wording and do not equate it to a Kerala statutory setback.
- **PDF pp.67–72, Figures 9–14:** Hirakud is a *demonstration from Odisha* showing sequential waterbody, seasonality, depth and accessibility overlays; the area narrows from **499.48 km² initial area → 317.03 km² year-round water → 204.54 km² joint seasonality/depth → 187.91 km² after road proximity → 99.50 km² with substation proximity** (PDF p.68 textual explanation). The maps on pp.70–72 show the corresponding differently coloured/trimmed areas. **No Kerala reservoir feasibility map is supplied by this Hirakud illustration.**
- **Textual threshold cross-check (PDF pp.61, 65, 67):** GHI >4.5 kWh/m²/day; GSW seasonality >11 months; modelled water depth 3–30 m; road and substation proximity 10 km. Sources include HydroLakes, JRC Global Surface Water, GLOBathy, OSM and GSA. Study exclusions are reusable *methodological ideas*, not verified local suitability.

### Kerala capacity: interpret image-based table headings correctly

**PDF p.73, Table 6 image**, confirmed against table text; its **columns are two alternatives**, not two contributions:

| Metric | NISE source figure |
|---|---:|
| Identified Kerala waterbody area | 219.02 km² |
| Study-filtered waterbody area | 109.19 km² |
| Study estimate **without** the 20%-surface cap | **5.73 GWp** |
| Study-filtered area after maximum 20% of each waterbody | 42.29 km² |
| Study estimate **with** the 20%-surface cap | **2.22 GWp** |

The report states nominal **0.019 km² per MW** (PDF p.72). This cannot be used as a statewide multiplier without a locally verified eligible-water-area register and technology layouts. The 20% value is a *screening cap*, not a reservoir operator's clearance, environmental approval, engineering floating coverage limit or grid offer.

**PDF pp.99–101, original Kerala annexure page images** provide IDs, waterbody names, majority districts, areas and both potential columns. They warrant a **record-identity exception register before aggregating or accepting the Kerala total**:

| Source record/example | Evidence issue requiring geographic confirmation |
|---|---|
| `Arabian Sea`, HydroLakes IDs **179964, 1403533**, Thiruvananthapuram, PDF p.99 | Marine-named features appear in a predominantly inland-hydrolake workflow. NISE's stated scope includes nearshore but excludes offshore; classify as **needs polygon/basin/nearshore engineering verification**, not an automatically valid reservoir or an automatically invalid row. |
| `Ezhimala` (1400810), `Ilaveezhapoonjira` (179813, 1402591), `Kottisheri Hill` (179645), `Pamba Malai` (1402924), pp.100–101 | Terrain-name or non-obvious lake labels: resolve actual HydroLakes polygons and whether they represent water, incorrect place-name attribution or a neighbouring feature. Names alone do not prove false geometry. |
| `Ashtamudi Lake` two IDs **15848/15850** (p.100); `Paravur Lake` two IDs (p.101); multiple `Kuttanad` and `Kuthiathode` IDs (p.100) | **Do not deduplicate on name alone** or assume distinct IDs never overlap; check hydrolake polygon geometry, multipart splits and water-area intersection. |
| `Nakshathra Kunnu` HydroLakes ID **15833**, Idukki (p.101) | Attributed 38.92 km² initial, 26.70 km² study-feasible and **0.41 GW after 20% cap**; verify actual waterbody identity before treating this as a developable dam/reservoir. This is also the selected Kerala *yield-simulation* representative in Table 4 (p.54). |

### Source simulation is **not** Kerala generation validation

**PDF pp.51–55, Tables 3–4 and Figure 4:** SAM comparison uses site-specific representative conditions, a 5° floating tilt and a study-modelled water-temperature correction `Twater=4.27+0.55×Tair` (reported in the study). The Kerala representative `Nakshathra Kunnu` has **+3.71% in Case 4, +4.12% in Case 5**, with negatives ~0.38–0.40% for Cases 1–3. These are **relative simulated configuration changes**, not floating-PV CUF, Kerala statewide annual MWh, or independently observed cooling. Table 3's simulation module is **585 Wp**, while the separate potential calculation on PDF p.72 states **545 Wp**: record these as two separate study assumptions; do not silently merge them into a single plant specification.

**Decision for Kerala2040:** NISE **2.22 and 5.73 GWp stay attributed alternative published study scenarios**. The annexure is a *candidate investigation list* once IDs/polygons can be checked. **Do not enter either number as model-feasible, permitted, commissioned or generatable capacity.**

## 2. World Bank / ESMAP PV potential: inspect actual map meaning

- **PDF p.20 (printed p.7), Table 2.1 image:** GHI, TEMP, PVOUT, seasonality index and simplified LCOE are **different layers**, with nominal **30 arcsec ~1 km** study maps. PVOUT is energy **per kWp** of a particular reference PV configuration, not capacity per map cell. The published GSA India raw-resource families have their own native resolutions, so do not treat all World Bank study outputs as interchangeable layers.
- **PDF pp.20–22, Table 2.2 image/text:** auxiliary global layers include elevation/slope, built-up density, settlement clusters, tree cover, ESA land cover, water and WDPA/IUCN protected polygons. Input vintages and grids differ, thus the report describes harmonization and raster-algebra masking. A source mask pixel is not a Kerala land/legal certificate.
- **PDF p.27 (printed p.14), Figures 2.3/2.4 images:** **Ethiopia** examples showing five *primary/Level-1* screens: terrain, water, compact forest, remote/uninhabited and intra-urban areas; then two *secondary/Level-2* screens: cropland and IUCN areas. They are neither Kerala maps nor Kerala statutory categories.
- **PDF p.28 (printed p.15), Figures 2.5/2.6 images:** the global maps show the subtraction of primary and then secondary exclusion zones. **Orange/non-grey on a global map does not establish rights to build, terrain engineering or free grid hosting in Kerala.**
- **PDF p.29 (printed p.16), Figure 2.7 image:** Ethiopia Level 0 → Level 1 → Level 2 is **masked source PVOUT** for zonal summary statistics, **not an installed-MW density map**. The legend explicitly reads long-term average daily PVOUT, **kWh/kWp**.
- **Printed pp.12–15 (PDF pp.24–27) source rules:** Level 1 includes compact forests ≥50% tree cover, complex terrain, permanent water with a specific coastline buffer exception, distance >25 km from a population cluster and dense urban areas; Level 2 overlays selected possible regulatory restrictions (protected areas and cropland). These are explicitly *global modelling choices*. Even the study says detailed project financial decisions require site-specific analysis (PDF p.15).

**Decision for Kerala2040:** preserve the study TIFFs as ***study-derived resource and screening context***. Neither `Level-1` nor `Level-2` masks establish Kerala's notified forest/paddy/wetland/ESA/ESZ rules; likewise LCOE is a simplified study economic layer, not a modern Kerala tariff or investment forecast.

## 3. NIWE 120 m and 150 m: no transposing numbers

Official [NIWE 120 m atlas publisher page](https://niwe.res.in/Open_data_Set/technical_report/19/) describes **500 m spatial modelling, 406 measurement-site corroborations** and an illustrative land-exclusion/capacity assessment. The searchable official [77-page 120 m report](https://niwe.res.in/static/pdf/India%27s_Wind_Potential_Atlas_at_120m_agl.pdf) has Kerala **2,311 MW** in the **>25% CUF** state-wise atlas table, split by CUF band into **366 / 193 / 180 / 359 / 1,213 MW** (25–28 / 28–30 / 30–32 / 32–35 / >35%). **This is an attributed 2019 modelled 120 m planning estimate, not a new local reanalysis or allowed build-out.** The **visual page inspection is OPEN** until the original 77-page PDF is attached or the publisher PDF can be rendered.

The privately archived NIWE **150 m** resource ZIP, earlier local cell-clipping QA, and any unfiltered portal popup are a *different asset* with a different height and screening basis. Neither the **2,311 MW** 120 m figure nor a larger 150 m popup value can be substituted for the other, added, treated as observed MWh or admitted as approved projects. A preliminary offshore map in the 120 m report is not measured Kerala offshore resource.

## Decisions / follow-ups

1. **Preserve the source page citations and clearly attribute results** rather than rewriting NISE/World Bank assumptions as Kerala-specific engineering facts.
2. Resolve NISE annexure HydroLakes IDs **179964, 1403533, 15833, 15848/15850**, etc., with actual polygons, Kerala coast/inland classifications, reservoir operators, seasonal dry-area minimum, environmental/safety permits and grid capacity before local scenario aggregation.
3. Keep NISE 545 Wp potential sizing and 585 Wp SAM yield experiment distinct. Do not use +4.12% as a floating-PV production uplift for all Kerala.
4. Obtain *directly accessible* NIWE 120 m 77-page PDF (the private archive is verified but cannot be inspected page-by-page via the GitHub connector); inspect atlas maps, legend, exclusions and Kerala rows as actual page images. Do the same separately for a 150 m report, if claimed.
5. No `model_admitted` status changes; onshore and offshore, resource and buildable MW, publisher estimates and model scenarios remain separate.
