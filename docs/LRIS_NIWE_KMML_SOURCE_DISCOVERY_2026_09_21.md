# LRIS, NIWE 150 m and KMML: acquisition-route discovery (21 September 2026)

**Classification: source-discovery note updated after user-provided NIWE original ZIP file QA.** NIWE raw *national source* is now user-supplied and independently hashed/parsed; no NIWE original bytes are committed to Git, no Kerala-only official-boundary clip or model-ready generation is established. LRIS native vector/raster and KMML measured operations data are not acquired.

## Kerala LRIS 2.0 — Land Use Department

- Portal: https://lris.kslub.kerala.gov.in/app/
- Agency information and catalogue: https://lris.kslub.kerala.gov.in/
- Official data-access FAQ: https://kslub.kerala.gov.in/?page_id=371&lang=en
- The interface displays local-body/district-scale thematic land use, paddy, forest, waterbody, wetland and wasteland classes, plus drainage, soil, slope, geomorphology, watersheds and other overlays. Its displayed chart/colours are **visual evidence, not native class-coded GIS**.
- The agency's FAQ explicitly offers land use, wetland/paddy maps, watershed, drainage, soils and related data. It instructs requesters to send a purpose-specific letter to the Land Use Commissioner; it describes an invoice at the government-fixed rate and delivery after payment. Data enquiry: landuseboard@yahoo.com, with luc.kslub@kerala.gov.in on the agency homepage.
- **Request:** full Kerala native class-coded land-use/paddy/wetland/waterbody layers (or clearly specified district/local-body subsets), boundary layers, class legend, mapping/survey dates, scale/resolution, source CRS, source accuracy, update/revision, geometry rights and research/derived-map/redistribution permissions. Confirm availability, quotation, geographic scope and fees **before** payment.
- LRIS complements but does **not** substitute for the dated FY2024–25 NRSC annual LULC product or notification-linked legal protected-area/wetland geometry. A class named `Forest` or `Wetlands` is not a gazette-defined legal boundary. No statewide or FY2024–25 mapping vintage has been verified from the shown map.

## NIWE 150 m wind atlas — actual downloadable dataset identified

- Map visualization: https://maps.niwe.res.in/resource_map/map/150m/
- Official dataset listing: https://niwe.res.in/Open_data_Set/open_wind_dataset/11/
- Dataset name: `India Wind Potentional 150m Map wind atlas Data` (publisher spelling). Download package: `150m_Map_Data_A_to_G.zip`, advertised 240.30 MB; CSV inside `150m_Map_Data_A_to_G.csv`, advertised 836.64 MB.
- Publisher describes **150 m above-ground height and 500 m model grid resolution** with mean wind speed, Weibull shape/scale, power density, temperature, pressure, density, wind direction and joint frequency distribution. A `Measurement Period` is not supplied; this is modelled wind climatology, not measured FY2024–25 hourly data.
- Access requires the publisher's named form, purpose statement and explicit academic/research/educational-use undertaking. User must review and accept the terms personally; do not bypass the form or publish/mirror the ZIP/CSV to our public repository without permission.
- On authorized receipt: preserve original ZIP and SHA256 privately; record actual columns, geometry/coordinates, CRS, source coverage/vintage/model reference, usage conditions, 500 m grid extent, missing/duplicate points, and source archive checksum. Extract Kerala cells using a documented boundary and reconcile border-adjacent high-resource pixels; do not attribute Tamil Nadu cells to Kerala. Do not claim CUF colours from a browser map are the downloaded CSV or legal siting feasibility.
- Separate roles: NIWE = spatial long-term wind resource screening; ERA5 FY2024–25 = hourly weather chronology. Neither is validated turbine generation or screened installable MW. Parameterise wind turbine curves and losses, and keep the two evidence streams independent.

### Source acquisition update — original received and inspected

On 21 September 2026 the user supplied `Wind.zip` (422,482,328 bytes).
It contains `Wind/150m_Map_Data_A_to_G.zip` (251,971,340 bytes),
whose NIWE metadata and 877,276,846-byte CSV are verified in
`data/evidence/gis/niwe_150m_user_supplied_source_qa_2026_09_21.json`.
The full national CSV has 19,475,568 rows, seven numeric columns and zero
non-numeric/missing values. **Only these actual CSV fields exist:** longitude,
latitude, wind speed, Weibull A, Weibull k, air density, wind power density.
Although the general metadata lists temperature, pressure, direction and
joint-frequency, these are **not delivered in this CSV**. No CUF or hourly
timestamps are in it. National source acquisition is now CLOSED; source
redistribution permission, dated source vintage, official Kerala polygon
clip and spatial/model admission remain OPEN. Neither the generic outer
collection nor a bounding rectangle can be counted as a Kerala wind raster.

### NIWE interactive-map user-selection result — NOT Kerala's installable capacity

A user-supplied 21 September 2026 screenshot from the NIWE 150 m map
shows a **blue selection polygon** which visibly extends offshore from the
west coast and does **not** trace Kerala's eastern administrative border.
The source screenshot alone does not supply original polygon vertices,
area-calculation rules, a geospatial mask or a downloadable cell-to-CUF table.
It cannot be treated as a Kerala-only or a legal land-eligible zone.

**Transcribed exactly as displayed by the portal, for that selection only:**

| Map CUF band (%) | Portal reported area (sq km) | Portal 'Installable Capacity' (MW) |
|---|---:|---:|
| 25–30 | 2,219.59 | 9,988.16 |
| 30–32 | 734.09 | 3,303.41 |
| 32–35 | 842.27 | 3,790.22 |
| 35–38 | 746.68 | 3,360.06 |
| 38–40 | 361.78 | 1,628.01 |
| >40 | 1,892.2 | 8,514.9 |
| **Overall portal selection** | **6,796.61** | **30,584.76** |

The popup itself says: **"The estimation is indicative and without
unsuitable area exclusion. Site specific studies are required to estimate the
actual installable potential."** Quotation from user-supplied screenshot;
not a statement of technical/economic/siting feasibility. Do **not** call
30,584.76 MW a verified Kerala potential, an approved 2040 capacity bound,
offshore potential, land-use ceiling or candidate build programme. Even an
exact Kerala clip of these resource pixels would not account for wind project
spacing, turbine technology/hub height, forest/ESA/wetland rules, slope,
settlements, land tenure, roads, substations, grid or other exclusions.

The user's original NIWE CSV does **not** contain this portal CUF or installable
capacity column. A reproducible reconciliation would need the actual portal
selection polygon and the map's turbine/area-density/CUF assumptions, followed
by a Kerala administrative clip and project-specific ecological/grid screening.
The visually selected coastal/offshore area particularly forbids interpreting
the output as wholly onshore Kerala.

### Revised 150 m CUF polygon — second user screenshot (21 September 2026)

The user supplied a **second NIWE selection and popup** after the original
6,796.61 sq km / 30,584.76 MW selection above. Preserve these as **two
different map-selection observations**; the newer screenshot does not
supersede or prove the precise coordinates of the earlier polygon.

| Map CUF band (%) | Revised selection area (sq km) | Portal indicative MW |
|---|---:|---:|
| 25–30 | 2,186.54 | 9,839.43 |
| 30–32 | 735.47 | 3,309.62 |
| 32–35 | 837.45 | 3,768.53 |
| 35–38 | 749.27 | 3,371.72 |
| 38–40 | 375.49 | 1,689.71 |
| >40 | 1,931.61 | 8,692.24 |
| **Overall revised selection** | **6,815.83** | **30,671.25** |

All displayed band capacities equal their band area **approximately multiplied
by 4.5 MW/sq km** (allowing two-decimal rounding). This is a *portal
implied uniform capacity density*, **not** established turbine spacing,
permitting, grid feasibility, area-use fraction or ecological eligibility.
The totals are for the displayed **CUF >=25% categories**, not the full
administrative area of Kerala or every square kilometre inside the polygon.

The new drawn western edge is still seaward of the Kerala coastline in
places; it should be retained as a user-drawn exploratory envelope, not
declared the statutory Kerala border, a legally permitted offshore zone
or a land-sea disaggregated geospatial result. **Including sea inside the
selection does not prove NIWE counted offshore wind resource pixels**:
the screenshot predominantly shows the coloured NIWE resource layer
on land and no separately validated offshore CUF resource. Conversely,
uncoloured sea does not prove offshore wind potential is zero.

The original national NIWE **150 m CSV has seven wind-climatology columns
but no portal CUF map layer, offshore study-area polygon or capacity field**.
Our scientifically auditable next deliverables are a coordinate-based NWIC
Kerala land clip, a *separately defined* offshore study polygon plus a
verified offshore resource dataset, and technology/constraint screening.
Neither popup's 30+ GW can be admitted as a Kerala2040 siting/capacity ceiling.

### Further NIWE map screenshots — hybrid, 20 m wind speed and terrain (21 September 2026)

- The user's hybrid-map screenshot displays **Wind Solar_Hybrid** classes
  `<50`, `50–75`, `75–80`, `80–85`, `85–90`, `>90`,
  with red patches in/near the Western Ghats and across the border in
  Tamil Nadu. NIWE describes its hybrid map as combining its wind resource
  and solar atlas in terms of CUF at 500 m resolution. **Do not equate a red
  >90 hybrid-map value to a measured single-plant annual 90% output
  factor**, nor count map colour as land feasibility. Original hybrid
  raster, its algorithm and effective-CUF/evacuation definition have not been
  acquired or independently implemented. Source:
  https://niwe.res.in/media/pdf/Issue_77.pdf .
- The wind-speed screenshot legend says `Wind Speed (%)` but uses bins
  `0–3, 3–4, 4–5, 5–6, >6`. NIWE's official **20 m map** text confirms
  those are **wind speed in m/s at 20 m**, not percentages and **not**
  the 150 m data height. Source:
  https://maps.niwe.res.in/resource_map/map/20m/ .
- The maps visually highlight Palakkad Gap/eastern Ghats and southern
  highland wind corridors, sometimes extending across Kerala–Tamil Nadu
  borders. Terrain panels show steep ridges and the gap. This is **only
  a shortlist for GIS and wind-resource analysis**: confirm each candidate's
  grid coordinates, slope, administrative classification, ecological/forest
  restrictions and grid access. NIWE's 150 m report uses a normalised
  turbine and assumptions for converting wind distribution into CUF;
  those are not measured site output.
  Source: https://maps.niwe.res.in/media/150m-report.pdf .
- The coastal/offshore area in the screenshots is largely uncoloured by
  NIWE wind-speed/hybrid overlays. **Absence of map colour is not zero
  offshore wind potential**, and the 150 m onshore atlas ZIP must not be
  represented as an offshore metocean/energy-yield dataset. Offshore is a
  distinct study area needing validated offshore wind, bathymetry, seabed,
  marine uses and cable-landfall constraints.
- Keep three distinct source IDs: `niwe_20m_visual`,
  `niwe_150m_original_national_csv`, and `niwe_hybrid_visual`. Do not
  merge values across heights, metrics or spatial footprints, or infer
  annual generation for Kerala from coloured tiles.

## KMML — process topology identified, mass/energy/water balance still missing

- Official main-process description: https://www.kmml.com/process-chart and https://www.kmml.com/manufacturing-facility
- Main TiO2 pigment chain: mineral separation -> ilmenite beneficiation -> chlorination/TiCl4 -> oxidation -> pigment finishing. Spent HCl regeneration and iron-oxide recovery are linked branches; oxygen, boilers, compressors and water treatment are utilities.
- The **Kroll-process** chart displayed alongside the pigment-process chart is a **separate titanium-sponge/metal branch**, with TiCl4 purification, magnesium reduction, vacuum distillation and sponge handling. It must not be merged into the main TiO2 pigment mass balance.
- The published chart documents unit operation connections and illustrative material labels, **not** FY2024–25 operational throughput, waste quantities, metered electricity/steam/water, measured recovery yields, emissions, treatment or true plant-wide annual mass balance. Preserve facility-provided values as design/description rather than observed historical time series until matched to the correct source and time period.
- First deliverable can now include a *qualitative official-process topology* with marked unknown flow rates and metering boundaries; the numerical KMML audit gate stays blocked.

## Model-admission rule

The 3 portals are legitimate leads, but screenshots, styled map tiles and website process charts must not be counted as original analytical datasets. Each acquired original requires date, exact provenance, checksum, units, full metadata and permission; all resource/land calculations need method-specific QA.
