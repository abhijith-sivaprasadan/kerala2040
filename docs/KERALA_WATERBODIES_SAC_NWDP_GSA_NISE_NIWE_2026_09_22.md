# Kerala2040 · Kerala waterbodies × archived GSA/NIWE and illustrated NISE/World Bank reports

**Reviewed 22 September 2026.** Sources: the user's new `wb_kl_geojson.zip`, the
previously uploaded Solar/Wind source ZIPs, full India GSA PVOUT/GHI TIFFs and the
NISE (2026), NIWE (2019) and World Bank/ESMAP (2020) PDFs. A detailed aggregate
[geometry/resource QA record](../data/evidence/solar/nwdp_sac_kerala_waterbodies_2026_09_22.json)
and a **private per-reservoir CSV** were produced from actual source binaries.
Neither a wetlands polygon nor a publisher potential number is admitted to a
buildable-capacity model by this assessment.

## A sixth source collection, NOT already on the private Release

The user attributes `wb_kl_geojson.zip` to the **National Water Data Portal**.
The sole member is `wb_sac_kl.GeoJSON`, whose own `src_agency` field is `SAC N`.
The exact NWDP dataset URL, revision/survey date, original licence and
redistribution terms have **not** been verified. Neither the original ZIP nor
the derived reservoir table was uploaded to the private GitHub archive in this
review. **Do not modify or overwrite the five previously SHA-256-restored folder
snapshots.** A sixth, separately tagged, original-byte private intake remains
pending.

| Byte identity | SHA-256 |
|---|---|
| `wb_kl_geojson.zip` (8,250,266 bytes) | `b9a7f5199ec235f96ca02a246c3530720a981b5e5fb1fa9fa6d0f759f6126324` |
| `wb_sac_kl.GeoJSON` (29,129,332 bytes) | `544145ff85cb422dbee867a84e38e695cf13de5f31f51f7f1cb4337cc73862f3` |

### Original geometry QA

**This is a wetland inventory, not 9,196 eligible floating-solar lakes.**
The ZIP contains 9,196 MultiPolygon features; unique numeric `id` matches
`objectid_1`. The source CRS is **EPSG:7755 (WGS 84 / India NSF LCC)**;
the projected coordinates look like millions of metres, **not lon/lat**.
A reproducible transformation to EPSG:4326 spans approximately
74.8703°–77.2884° E, 8.2955°–12.7764° N. The source `area_ha` equals
geometry area / 10,000 within numerical precision. Total area across *all*
classes is **939.0383 km²**, not a deployable area.

| Source `level_i / level_iii` | Polygons | Geometry area km² |
|---|---:|---:|
| “Costal” [source typo] / natural lagoon | 54 | 368.718 |
| Inland / man-made **Reservoir/Barrage** | **52** | **303.392** |
| “Costal” / aquaculture pond | 436 | 123.869 |
| Inland / natural waterlogged | 680 | 77.141 |
| Inland / man-made tank/pond | 7,822 | 43.740 |
| Other inland / coastal / unknown classes | 152 | 22.178 |

Only **164 features have nonempty names** (82 different name strings);
unlabelled small ponds must not be inferred to be named reservoirs.
**9,195/9,196 geometries are valid**. Source ID **9055, “Kavvayi Lagoon”**
contains a ring self-intersection. Preserve original bytes; any
`make_valid` version belongs in a separately documented *derived* file.
The spelling `Costal` is kept when quoting source classifications rather
than silently translating it to an official marine/legal designation.

## Resource overlay run against actual archived-source GIS

Only the **52 source-classified inland Reservoir/Barrage polygons** were
intersected with the actual long-term average-daily GSA India TIFFs.
The GSA PVOUT and GHI grids are **not interchangeable**:

| Field | Source-native grid | Unit and interpretation |
|---|---|---|
| PVOUT | 0.008333333° (~30 arcsec) | kWh/kWp/**average day**; source-fixed PV model |
| GHI | 0.0025° (~9 arcsec) | kWh/m²/**average day**; solar irradiation |

Polygons were transformed from EPSG:7755 to EPSG:4326 for source-grid
intersection. Each intersected cell's share of the waterbody was measured
back in source projected metres and used for a *fractional-cell,
surface-area-weighted resource mean*, retaining small polygons whose
centroids might miss a coarse cell. No interpolation or synthetic hourly
weather was added.

**All 52 reservoirs intersect positive PVOUT and GHI cells**. PVOUT varies
from **3.71849 to 4.26720 kWh/kWp per mean day** across their respective
polygon-weighted means; this is a *range over the 52 reservoirs*, not an
individual water body's pixel range or observed site-specific annual output.

Examples (source SAC polygon, **not approved projects**):

| SAC ID / source name | Source polygon km² | Mean-daily PVOUT kWh/kWp | Mean-daily GHI kWh/m² |
|---|---:|---:|---:|
| 9091 · Idukki Reservoir | 51.727 | 3.99220 | 4.93141 |
| 9094 · Idamalayar Reservoir | 31.547 | 3.84694 | 4.83850 |
| 9093 · Mullaperiyar Reservoir | 22.053 | 3.95899 | 4.88902 |
| 9007 · Malampuzha Reservoir | 18.611 | 4.06915 | 5.09289 |
| 9074 · Kakki Reservoir | 18.150 | 3.77785 | 4.62435 |

These values are **GSA long-term resource**, not FY2024–25 measured
generation; source polygon area is *water*, not floating array coverage
or permitted reservoir area. In particular, **PVOUT per kWp must never
be multiplied by all wetland hectares to invent MW or MWh**.
The per-reservoir working CSV is a separate user-facing, local/private
derived artifact, not a third-party geospatial data dump in public Git.

## Compare the illustrated reports without mixing source universes

### NISE floating PV (June 2026)

- PDF **p.63, Figure 6** visibly maps **GHI in kWh/m²/day**, while the
  resource overlay above uses different GHI and PVOUT measures.
- PDF **pp.70–72, Figures 10–14** show stepwise seasonality, bathymetry
  and road/substation access filtering for **Hirakud in Odisha**,
  not an official suitable-surface map for Idukki or Kerala.
- PDF **p.73, Table 6** gives Kerala **219.02 km² identified waterbody
  area; 109.19 km² filtered area; 5.73 GWp before the 20%-per-waterbody
  cap; 42.29 km² and 2.22 GWp after it**. These two GWp columns
  describe **alternative scenarios; do not add them**. The study uses
  **HydroLAKES**, JRC Global Surface Water, GLOBathy, OSM and GSA, not
  the newly provided SAC dataset.
- PDF **pp.99–101**, inspected as *rotated, image-backed annexure
  table pages*, show multiple Ashtamudi/HydroLAKES IDs, two
  `Arabian Sea` entries, and `Nakshathra Kunnu` (HydroLAKES 15833,
  reported 38.92 km²). Our SAC list names **Idukki Reservoir**
  (SAC 9091, 51.73 km²), but has **no name match to
  “Nakshathra Kunnu”**. Do not assert they are identical—or different
  physical reservoirs—without a verified HydroLAKES polygon/ID
  crosswalk. Likewise do not auto-deduplicate same-named lake records.

**Reason for 303.392 vs 219.02 km²:** they are *not the same population*.
303.392 km² is the entire SAC “Reservoir/Barrage” class; 219.02 km² is
NISE's identified **different-source HydroLAKES inventory** before its
further screens. Neither is an automatic contradiction or a statewide
20%-cap eligible base. Verify date, identity, outlines, hydraulic
operation and water persistence first.

### NIWE 120 m atlas (October 2019), separate from the archived 150 m atlas

**The user-supplied 77-page NIWE PDF was independently read as actual
page images, not OCR assumptions.** In particular:

- PDF **p.14 Table E.1 / pp.34 and 39**: **2,311 MW**
  *NIWE indicative Kerala 120 m potential*. PDF p.34 Table 5
  partitions it as **474 MW wasteland, 1,495 MW cultivable and
  342 MW “forest land”** under that study's assumptions.
  **Forest-class hectares are NOT approved Kerala development land**.
- PDF **pp.28–29**, Table 2 and methodology: settlement, waterways,
  roads, reservoirs and protected-area buffers, slope >20°, elevation
  >1,500 m; study factors of **80/30/5%** land-use availability and
  **5 MW/km²** with a CUF >25% screen. These are **NIWE's 2019
  scenario design**, not current official statutory clearances.
- PDF **pp.37–38, Figures 9–10** visually distinguish the wind
  climatology CUF map and the more restricted map *after unsuitable-area
  exclusion*. PDF **p.49, Figure 12** reports model-vs-406-station
  national comparison; this does **not** independently validate every
  Kerala 150 m pixel. PDF **p.52, Figures 13–14** are coarse offshore
  maps based on older satellite measurements—not Kerala offshore
  project eligibility.

The **NIWE 150 m national GIS atlas** previously clipped to Kerala is
a different height, model output and source vintage. Do not scale
2,311 MW between hub heights or add it to an unfiltered portal popup.

### World Bank / ESMAP ground-PV study (June 2020)

The uploaded PDF is **byte-identical** to the corresponding member of
the user's `Solar.zip`; likewise the local NISE and 120 m NIWE PDFs
match the PDF entries in `Solar.zip` / `Wind.zip` by SHA-256.
Actual PDF page images were inspected, especially World Bank PDF
**pp.27–29, Figures 2.3–2.7**, distinguishing global primary
physical/technical masks from secondary cropland/IUCN screening, and
PVOUT **Level 0 / Level 1 / Level 2**. These are **global study
screens**, not legal Kerala land- or water-eligibility polygons.
The study's simplified LCOE is not a site-specific cost assessment.

## Gates before a numerical capacity claim

**Floating PV:** vetted reservoir/candidate identities, seasonality
and minimum operating level, water-use and ecological restrictions,
operator permissions, engineering anchoring, road and substation
network *capacity* and access, protection/notified wetland geometry
and a versioned eligible-area rule.

**Wind:** 150 m wind resource joined to current statutory forest/
ecologically sensitive area and terrain constraints, plant access,
turbine-specific power curves, wake spacing, measured reference
series, and connection limits. Treat 2019 120 m NIWE scenarios only
as study context.

**Archive:** this sixth ZIP is **not yet included** in the
five-folder private Release. Archive it as a separately identified
original-byte collection with SHA-256 + independent restore; do not
replace the verified old assets. The public QA ledger does not
publish the raw SAC polygons.
