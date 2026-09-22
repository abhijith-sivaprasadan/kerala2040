# Primary PDF page review: floating PV, onshore wind and global PV

**Review state (22 September 2026):** Primary report maps and tables reviewed
at their cited pages. NISE 2026 and NIWE 2019 reports are the uploaded user
PDFs; the ESMAP/World Bank 2020 source below is the publisher-hosted
public PDF, not an independently SHA-matched copy of the user's archived PDF.
Original TIFF and PDF/source collection stays private, and source-reported
numbers below are NOT Kerala2040 buildable capacity.

## NISE, `Solar PV Potential of India` (June 2026, 121-page PDF)

Source file in the five-folder archive:
`Solar/NISE_floating potential_report_2026.pdf`.

### What the maps and diagrams establish

- PDF pp. **62–68** (printed pp. 30–36): source assessment moves from
  identified hydro-lakes through seasonality (water present >11 months),
  bathymetry (3–30 m), daily GHI threshold **4.5 kWh/m²/day**, road
  proximity within 10 km while excluding a 2 km road buffer, and substation
  proximity within 10 km. The illustrated maps are largely India-wide roads/
  substations and a **Hirakud, Odisha** worked example, not a Kerala
  reservoir map or verified Kerala evacuation capacity.
- PDF pp. **69–72** (printed pp. 37–40): the four Hirakud maps progressively
  intersect water polygon, seasonality, bathymetry, road and substation
  proximity. The report gives 499.48 km² total water, 204.54 km² after
  seasonality-and-depth overlap, 187.91 km² after roads and
  **99.50 km²** after 10-km substation proximity. This is a worked
  method and not transferable as a Kerala reservoir yield.
- PDF pp. **53–55** (printed pp. 21–23): water-surface temperature adjustment
  is an analytical correction, not field-validated Kerala generation. For the
  Kerala representative case labelled `Nakshathra Kunnu`, Table 4
  reports **−0.38 to −0.40%** (Cases 1–3), **+3.71%** (Case 4) and
  **+4.12%** (Case 5). These depend on the defined, different comparator/
  tilt/soiling assumptions and are not generic floating-PV premiums.

### State totals and the actual Kerala waterbody rows

- PDF p. **73**, Table 6 (printed p. 41): Kerala waterbody area
  **219.02 km²**; study-filtered area **109.19 km²** or **5.73 GWp**;
  after maximum-20%-of-waterbody-area restriction, **42.29 km²** or
  **2.22 GWp**. These are *alternative scenarios*, not additive. The
  report assumes **0.019 km²/MWp**, 545-Wp modules, 21% efficiency,
  2.6-m² module area and 5° tilt (PDF p. 72).
- PDF pp. **99–101** (printed pp. 67–69) contain waterbody IDs, district,
  actual area, source-filtered area and 20%-restricted potential. As
  transcribed from the report, examples to GIS-verify individually are:
  `Ashtamudi Lake` Hylake **15848** (0.13 GW after cap) and
  **15850** (0.33 GW); `Idamalayar` **15828** (0.27 GW);
  `Mullaperiyar Reservoir` **15840** (0.15 GW);
  `Nakshathra Kunnu` **15833** (0.41 GW);
  `Thenmala Reservoir` **15849** (0.16 GW).
  They are *source-reported* figures, not independent GIS classifications.

### QA holds for the 2.22-GWp estimate

1. Annexure, PDF p. **99**, has TWO Kerala waterbody rows literally labelled
   `Arabian Sea` (Hylake IDs **179964, 1403533**) attributed to
   Thiruvananthapuram. The study says it uses HydroSHEDS/HydroLAKES
   inland waterbody polygons; these sea-labelled rows require independent
   geometry, provenance and polygon-type inspection. **Do not silently
   reclassify, discard, or include them in a Kerala reservoir subtotal.**
2. `Ashtamudi Lake` and several other labels occur against distinct
   Hylake IDs. Same name is NOT proof of duplication, and different IDs
   are NOT proof of distinct developable water surfaces. Check polygon
   overlap, tidal/brackish connectivity and real place names. Likewise
   verify `Nakshathra Kunnu` against hydrological site coordinates
   before attributing generation or land/water rights.
3. A HydroLAKES overlay and global GLOBathy depth estimate are not
   a site survey. Kerala needs up-to-date seasonal inundation,
   reservoir operations/flood drawdown, bathymetry, drinking-water/
   irrigation and hydro access, aquaculture/fisheries, biodiversity,
   land/water permissions, real substations and spare evacuation ratings.
   None of those are supplied at project level by the state table.
4. Reject treating Table 6's GWp as FY2024–25 metered MW or a
   Kerala2040 investment cap. Keep as external study scenarios only.

## NIWE, `India's Wind Potential Atlas at 120m agl` (October 2019, 77-page PDF)

Source file in the archive:
`Wind/India_Wind_Potential_Atlas_at_120m_agl.pdf`.

### Visual/map and table crosswalk

- PDF p. **24** / printed p. 13, methodology flowchart: 500-m
  meso–micro WRF, 10 years of **NCEP/CFSR 2005–2014**,
  Weibull distributions, 2-MW normalized turbine curve, P50 net
  CUF, land exclusions and 5 MW/km² under assumed 5D × 7D layout.
  PDF pp. **32–33** chart the seven original and normalized power
  curves: they are NOT a modern turbine-specific power curve
  suitable for direct use in a Kerala 2040 dispatch model.
- PDF pp. **28–29** / printed pp. 17–18: explicit *study*
  exclusions include >1500-m elevation, >20° slope, protected-area
  buffers, water, settlements, roads, rail and airports. Study base
  land availability is **80% wasteland / 30% cultivable / 5% forest**;
  keep forest's 5% as a historical modelling assumption, **not a
  recommendation or a legal right** to develop protected land.
- PDF pp. **37–38** / printed pp. 26–27: Figure 9 displays
  potential by CUF class *before* unsuitable-area exclusions,
  Figure 10 shows visibly reduced areas *after* exclusion.
  The remaining bright patches in south India must not be
  read from this national-scale PDF as geolocated Kerala parcels.
- PDF pp. **14, 34 and 39**: Kerala row is **2,311 MW**
  indicated 120-m potential above 25% P50 CUF. CUF bins:
  **366, 193, 180, 359, 1,213 MW** for 25–28%, 28–30%,
  30–32%, 32–35%, >35%, respectively. PDF p. **34** splits
  this into **474 MW wasteland, 1,495 MW cultivable, 342 MW
  forest**, with applied 80:30:5 land weights.
- PDF p. **43**, Table 7: **2,297 MW** indicative
  greenfield estimate after excluding then-existing turbine
  locations using 6D buffers (reference inventory through 2019),
  NOT a present-day subtraction of commissioned wind capacity.
- PDF pp. **48–49**: validation section cites **406** stations,
  5% overall wind-speed mean absolute percentage error;
  the scatterplot shows **R² = 0.7185** for the 406-point
  model vs observed wind-speed comparison. National-average
  agreement does NOT guarantee error bounds for a Kerala ridge
  or 2040 hub height.
- PDF pp. **50–52**: offshore maps are a **different**
  dataset: QuikSCAT 10-m monthly averages, 0.25° grid,
  November 1999–October 2009, extrapolated to 120 m with
  shear exponent 0.11, Weibull k=2. The atlas calls for
  fresh long-term measurements; **no Kerala offshore
  project estimate is adopted**.

### Do not mix atlas vintages

The user also archived separate **NIWE 150-m** GIS source layers. The
2019 **120-m report** has a different hub height, input period,
model, turbine assumptions and exclusion vintage. Its **2,311 MW**
and **2,297 MW** are source-attributed 2019 study estimates,
not independent verification or a conversion of the 150-m GIS
resource-point count. Store 120-m and 150-m products in separate
provenance records; compare only after unit, vintage and
height harmonization.

## ESMAP / World Bank, `Global Photovoltaic Power Potential by Country` (2020)

Publisher report:
https://documents1.worldbank.org/curated/en/466331592817725242/pdf/Global-Photovoltaic-Power-Potential-by-Country.pdf

**Provenance:** this linked 62-page publisher PDF was browsed, including
visual figures; it has **not** been SHA-matched to
`Solar/Global-Photovoltaic-Power-Potential-by-Country.pdf`
in the private folder snapshot. The user's 3-page India factsheet
has not yet been directly inspected.

- PDF p. **19**, Table 2.1: primary data include GHI, TEMP,
  PVOUT, seasonality, simplified LCOE and boundaries; native
  GHI/PVOUT statistical products here use nominal **30 arcsec**
  (~1 km), distinct from the separately archived finer GSA
  India **GHI** resource GeoTIFF product.
- PDF pp. **26–28**, Figures 2.3–2.7: explicit visual comparison
  of Ethiopia primary physical/technical masks versus
  secondary cropland/protected-area masks, then global mask
  composites, then Level 0 / Level 1 / Level 2 practical
  potential map panels. These maps are *Ethiopia/global
  demonstrations*, NOT Kerala-approved site maps.
  A Level 2 mask is a global approximation of possible
  regulatory constraints, not Kerala notification-linked law.
- PDF p. **28** explicitly applies area-aware zonal
  statistics: geographic cells change area with latitude.
  For Kerala2040, use geodesic/equal-area pixel
  area where converting surviving site polygons to km².
  A descriptive native cell-centre count by itself does not
  establish physical land area or MW.
- The report studies theoretical solar resource, practical
  PVOUT after generic constraints, and simplified economics.
  Its **LCOE**/CAPEX values are historical broad-screen
  comparisons, not a 2026 Kerala tariff, 2040 site LCOE or
  grid-connectability test.

## Admission decision and next reproducible action

**Pass as source-attributed background:** NISE's two alternative
Kerala floating-PV study scenarios, NIWE's 2019 120-m
study estimates, and World Bank resource-versus-generic-mask
method framework.

**Still blocked:** original polygon identity and duplicate checks
for Kerala NISE waters; current Kerala land/legal filters,
NIWE 150-m onshore source-specific CUF/Weibull reading,
actual site yield and 8,760-hour production calibration;
offshore wind; current substation transfer ratings; buildable
MW/GWp. The independent GSA TIFF consistency PASS is
source-unit QA, not corroboration of these other inputs.

**Next reproducible operation:** use the NISE Hylake IDs
to crosswalk actual HydroLAKES/GSW/GLOBathy polygons,
resolve sea-labelled/double-labelled entities, and separate
"source-assessed water" from "Kerala-verified candidate".
For onshore wind, report the NIWE 150-m native clipped
points by resource class, slope/altitude and data lineage,
without adopting the 120-m report's capacity or forest
availability fractions as modern legal siting. Do not put
raw third-party PDF maps or TIFFs into public Git history.
