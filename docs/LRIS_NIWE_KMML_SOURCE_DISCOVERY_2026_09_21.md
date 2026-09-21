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

## KMML — process topology identified, mass/energy/water balance still missing

- Official main-process description: https://www.kmml.com/process-chart and https://www.kmml.com/manufacturing-facility
- Main TiO2 pigment chain: mineral separation -> ilmenite beneficiation -> chlorination/TiCl4 -> oxidation -> pigment finishing. Spent HCl regeneration and iron-oxide recovery are linked branches; oxygen, boilers, compressors and water treatment are utilities.
- The **Kroll-process** chart displayed alongside the pigment-process chart is a **separate titanium-sponge/metal branch**, with TiCl4 purification, magnesium reduction, vacuum distillation and sponge handling. It must not be merged into the main TiO2 pigment mass balance.
- The published chart documents unit operation connections and illustrative material labels, **not** FY2024–25 operational throughput, waste quantities, metered electricity/steam/water, measured recovery yields, emissions, treatment or true plant-wide annual mass balance. Preserve facility-provided values as design/description rather than observed historical time series until matched to the correct source and time period.
- First deliverable can now include a *qualitative official-process topology* with marked unknown flow rates and metering boundaries; the numerical KMML audit gate stays blocked.

## Model-admission rule

The 3 portals are legitimate leads, but screenshots, styled map tiles and website process charts must not be counted as original analytical datasets. Each acquired original requires date, exact provenance, checksum, units, full metadata and permission; all resource/land calculations need method-specific QA.
