# Kerala2040 — illustrated-source evidence crosswalk: NISE, NIWE and World Bank

**Review date:** 2026-09-22. **Purpose:** distinguish what the actual reports' maps, diagrams, data tables, and image-based annexures demonstrate from what the Kerala2040 generation/siting model is authorized to claim. **No source raw PDF images are rehosted here.** Citations refer to PDF page number (physical PDF count, not printed internal numbering).

## Source and review-status ledger

| Source | Actual material reached | Visual status |
|---|---|---|
| NISE, *Solar PV Potential of India: Floating Solar* (June 2026) | User-attached original 121-page PDF; physical pages 53–55, 61–73 and 99–101 inspected in page-image view alongside extracted tables. | **Selected methodology, maps, tables, Kerala annexure visually inspected.** Not a declaration that all 121 pages were independently read. |
| ESMAP/World Bank, *Global Photovoltaic Power Potential by Country* (June 2020) | [Official public 62-page PDF](https://documents1.worldbank.org/curated/en/466331592817725242/pdf/Global-Photovoltaic-Power-Potential-by-Country.pdf), physically viewed figures/tables on PDF pp.20 and 27–29 (printed pp.7 and 14–16), and read associated methodology on printed pp.6–16. | **Relevant tables/masks/maps visually inspected.** Public PDF filename matches the locally catalogued report; byte-for-byte equality with the user's private copy was not tested. |
| NIWE, *India's Wind Potential Atlas at 120m agl* (October 2019) | User directly attached the 77-page original. Page images and text checked for PDF pp.14, 24, 28–29, 34–35, 37–39, 43, 48–49 and 50–52. | **Selected maps, legends, tables, restrictions and validation figures visually inspected.** No assertion of all 77 pages read or user-local TIFF/ZIP byte-identity independently compared. |
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

Official [NIWE 120 m atlas publisher page](https://niwe.res.in/Open_data_Set/technical_report/19/) describes **500 m spatial modelling, 406 measurement-site corroborations** and an illustrative land-exclusion/capacity assessment. The user-attached **77-page 120 m report** [NIWE publication page](https://niwe.res.in/Open_data_Set/technical_report/19/) has Kerala **2,311 MW** in the **>25% CUF** state-wise atlas table (PDF pp.14, 39), split by CUF band into **366 / 193 / 180 / 359 / 1,213 MW** (25–28 / 28–30 / 30–32 / 32–35 / >35%). **This is an attributed 2019 modelled 120 m planning estimate, not a new local reanalysis or allowed build-out.** The attached PDF's selected maps, table images and figures have now been inspected.

**What the actual PDF images establish:**

- **PDF p.14, Table E.1, and pp.39–40, Table 6:** Kerala's five CUF-band components total **2,311 MW**; p.43 Table 7 gives **2,297 MW greenfield** under the report's subtraction of turbine parcels then in service, **not** a current 2026 unused-land estimate. PDF pp.34–35, Table 5 supplies a different *land-class split of the same 2,311 MW*: **474 MW wasteland + 1,495 MW cultivable land + 342 MW forest land**. These are **non-additive cross-tabulations**. The presence of forest land in the study's capacity accounting must be flagged, not treated as approval to construct in forests.
- **PDF pp.24 and 28–29 (Figure 6; Tables 2–3):** its 120 m planning scenario selects modelled **P50 CUF >25%**, includes NRSC land weights **80% wasteland, 30% cultivable, 5% forest**, assumes **5 MW/km²** at **5D × 7D** turbine spacing, and excludes terrain >1,500 m or slope >20° with study-specific road, airport, settlement and protected-area buffers. Those 2019 *study assumptions* are not current Kerala statutory eligibility or a present-day OEM power-curve optimization.
- **PDF pp.37–38, Figures 9–10:** the **pre- and post-exclusion map panels visibly differ**; neither full-page India image is a parcel-level Kerala authorization map. Colour ranges show CUF classes rather than time-resolved output.
- **PDF pp.48–49, Figure 12:** the authors report comparison against **406 stations**, with **5% mean absolute percentage error of mean wind speed**, and the plotted relationship reads **y = 0.9788x, R² = 0.7185**. This is atlas wind-speed error, **not a 5% error bound on Kerala turbine power, capacity or monthly generation**.
- **PDF pp.50–52, Figures 13–14:** the offshore charts use **QuikSCAT 10 m November 1999–October 2009 monthly averages on 0.25° grid**, then a **0.11 power-law exponent to 120 m** and assumed Weibull k = 2. The report explicitly requires new long-term measurements. A coarse, dated national offshore illustration is **not verified Kerala offshore wind potential**, nor is it covered by the terrestrial 150 m ZIP.

The privately archived NIWE **150 m** resource ZIP, earlier local cell-clipping QA, and any unfiltered portal popup are a *different asset* with a different height and screening basis. Neither the **2,311 MW** 120 m figure nor a larger 150 m popup value can be substituted for the other, added, treated as observed MWh or admitted as approved projects. A preliminary offshore map in the 120 m report is not measured Kerala offshore resource.

## Additional direct-original visual and byte-identity review — 22 September 2026

The actual **user-provided** `Solar.zip` and `Wind.zip` were available for
independent local inspection in this review, in addition to the standalone NISE
and NIWE PDF uploads. The two standalone PDFs' SHA256 values matched the
corresponding member bytes inside those ZIPs; this establishes **identity of
those two PDF members only**, not completion of the separate 17 provider-original
archive checklist. The World Bank 2020 report and the India country factsheet
were extracted directly from the provided `Solar.zip` and inspected from
their actual PDF page renders, not inferred from filenames or OCR.

| Exact user-supplied PDF | SHA256 of PDF bytes | Page review |
|---|---|---|
| `Solar/NISE_floating potential_report_2026.pdf` | `d655be7999fe042162f1e46de7ad35b098d427f50b00f30d4e1ce069b8a026fd` | 121-page document; selected method/figure, Table 6 and Kerala annexure pages, not all pages |
| `Wind/India_Wind_Potential_Atlas_at_120m_agl.pdf` | `b717b017dfbb8cf5fcc068dcd73407baf06ae5277974d23b475d40edb130efdc` | 77-page document; selected Kerala tables, mapped exclusions, validation and offshore figures |
| `Solar/Global-Photovoltaic-Power-Potential-by-Country.pdf` | `56f7c6e9a7ee6c5083674f2a40f39a292d39c0325a892fad7787e29b9e566378` | 2020 ESMAP/World Bank 62-page study; PDF pp.20, 24–29 and associated methodology |
| `Solar/GSA_Global-PV-potential-study_Factsheet_India.pdf` | `cee6f7ef7224cff565929df84492d14fc052cfba0eae58c501d2f435715f75d1` | Three-page World Bank/Solargis country factsheet: all three page images examined |

**World Bank India factsheet nuance (PDF p.1):** its India country-average
practical potential at study Level 1 is **4.322 kWh/kWp/average day**,
theoretical GHI average is **5.098 kWh/m²/average day**, and PVOUT seasonality
index is **1.75**. Its legend explicitly distinguishes a *Level 0 solar
resource map* from the *Levels 0/1/2 land-zonation map*. The infographic's
25.1%/87.8%/100% distribution refers to its **national evaluated area** under
study masks, **not Kerala land availability**. Its human-development,
installed-capacity and electricity-access indicators use earlier years (for
example, 2018 PV capacity), even though the downloaded factsheet bears
**©2026**. Neither the country-average value nor these national map colours
replaces a Kerala cell- or site-specific quantity.

**NIWE provenance nuance:** PDF p.49's national **5%** MAPE comparison is for
*wind speed* at 406 sites; the scatter diagram also reads
`y=0.9788x`, `R²=0.7185`. It is not a 5% uncertainty
on Kerala wind-farm output or on the 150 m downloaded grid. NIWE's 120 m
2019 Kerala **2,311 MW** is a single scenario appearing under two
non-additive breakdowns: **366/193/180/359/1,213 MW by CUF band** (p.14,
pp.39–40), and **474/1,495/342 MW by study land class** (pp.34–35).
Its **2,297 MW greenfield** (p.43) subtracts the then-existing turbine
parcels; it is not a 2026 uncommitted land/capacity register. The 2019
study's **5% forest availability factor** produces the nominal 342 MW
forest-land component but gives no forest construction authorization.
The maps on pp.37–38 show resource versus *study-screened* land—not current
Kerala parcel/legal envelopes. Offshore p.52 is a coarse **India EEZ
illustration**, not a high-resolution measured map of Kerala's offshore sites.

**NISE visual interpretation nuance:** Hirakud's p.70–72 maps show
successive, visibly shrinking *Odisha* waterbody masks for seasonality,
depth, road and substation proximity, not a mapped Kerala site.
Table 6 p.73 and Kerala annexure pp.99–101 separately show
**5.73 GWp broader study** versus **2.22 GWp at its 20%-water-surface cap**.
The annexure contains two **`Arabian Sea`** HydroLakes-labelled records,
two Ashtamudi IDs, terrain-like lake names and the **`Nakshathra Kunnu`**
entry. These are source identity/geometry *verification flags*, **not**
proof that the rows are necessarily invalid. The source's p.54 Kerala
+3.71%/+4.12% values are **relative model cases**, not measured generation
or a universal floating-PV uplift.

**Resulting evidence status:** source figures and qualifying methods are
reviewed and may be cited as *publisher-attributed research benchmarks*.
No changed `model_admitted` gate, no inferred Kerala new buildable MW,
no present-day permit assertion, and no blanket claim to have read every
page of these reports. The source-media batch of 66 PDFs/2,945 pages was
**rendered** by the user; that is not equivalent to visually interpreting
all those pages.

## Decisions / follow-ups

1. **Preserve the source page citations and clearly attribute results** rather than rewriting NISE/World Bank assumptions as Kerala-specific engineering facts.
2. Resolve NISE annexure HydroLakes IDs **179964, 1403533, 15833, 15848/15850**, etc., with actual polygons, Kerala coast/inland classifications, reservoir operators, seasonal dry-area minimum, environmental/safety permits and grid capacity before local scenario aggregation.
3. Keep NISE 545 Wp potential sizing and 585 Wp SAM yield experiment distinct. Do not use +4.12% as a floating-PV production uplift for all Kerala.
4. The NIWE 120 m 77-page PDF was directly attached and its selected Kerala tables, maps, legends, exclusions, validation and offshore figures **have now been visually reviewed**. Remaining: retain the original file hash, check NIWE 150 m metadata separately and obtain present-day authenticated land/forest/terrain/grid screening inputs before computing a *new* buildable-MW estimate.
5. No `model_admitted` status changes; onshore and offshore, resource and buildable MW, publisher estimates and model scenarios remain separate.
