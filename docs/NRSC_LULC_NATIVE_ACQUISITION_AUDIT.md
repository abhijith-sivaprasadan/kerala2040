# P0 — Kerala NRSC/Bhuvan LULC: native georeferenced acquisition review

**Reviewed 20 September 2026. Status: no verified native Kerala class-coded raster or matching class legend in the research repository.** This is a source and data-admission deliverable, **not** a land-availability or renewable-capacity result. Do not represent the NRSC map selection or a styled WMS image as an acquired original categorical raster.

## Reconcile the official products and access

| Product | Officially documented period / scale | Access and modelling decision |
|---|---|---|
| Annual NRSC LULC250K | Annual national AWiFS assessment; *2024–25 option is visible* on Bhuvan's environmental portal | Preferred period for FY24–25 background, **native Kerala class-coded file not yet acquired**; ISRO describes original/native data requested through a Head-of-Department/Organisation-signed MoU. |
| NRSC LULC250K download catalogue | Bhuvan Store lists 1:250,000 data-for-download through **2022–23** | Earlier download-listing does not prove 2024–25 native data availability. Validate the latest selectable native package/date rather than implying that a displayed map is downloadable. |
| NRSC LULC50K | 2005–06, 2011–12, 2015–16 | 54-level classification documented, but stale for FY24–25 and described by ISRO as available through **OGC viewing**, not ordinary public native-format access. Use as historic context only. |
| SISDP LULC10K | District-level, phase-2 Bhuvan Store 2018–23 | Bhuvan Panchayat advertises a request/download route. Confirm actual Kerala district tiles, survey vintage, class-code legend, geometry and permission for each supplied product. **Do not assume newer than its documented year or statewide coverage.** |

Sources: [NRSC LULC product overview](https://www.nrsc.gov.in/nrscnew/Apps_LULC.php), [Bhuvan Store](https://bhuvan-app1.nrsc.gov.in/2dresources/bhuvanstore2.php), [Bhuvan 2024–25 selectable visualization](https://bhuvan-app1.nrsc.gov.in/moef/), [ISRO's explicit native-data access terms](https://www.isro.gov.in/SpaceBasedEarthObservationServices.html), and [Bhuvan Panchayat SISDP download/request announcement](https://bhuvan-panchayat3.nrsc.gov.in/). All are source discovery, not proof of delivered datasets or licence grant to this project.

**Important spatial scale boundary:** 1:250,000 is a *map scale*, not a 250,000 m cell size. NRSC describes its national annual LULC at roughly **56 m** geospatial resolution; inspect the actual raster transform to establish native pixel dimensions and projection. A regional-scale thematic layer does not, on its own, decide wetland, forest-notification, coastal, setback, parcel or grid-access permissions. <https://www.nrsc.gov.in/nrscnew/resources_atlas_LULC.php>

## Exact acquisition request (NOT sent)

> I am developing an independent statewide Kerala energy and ecological siting study for historical FY2024–25 and later 2040 scenarios. Could NRSC provide or confirm the approved download/request process for the **2024–25 Kerala LULC at 1:250,000** in its **original georeferenced, class-coded analytical format** (GeoTIFF or native vector), including the complete code-to-class legend, mapping period/sensor, spatial reference and pixel size/scale, nodata value, spatial accuracy, dataset revision, and use/redistribution conditions? We understand the map layer alone may not permit native extraction and that a Head-of-Organisation MoU may be needed. Please advise whether a genuinely independent researcher can request the data, or whether a qualifying institutional partner and formal application are required. We would also appreciate the closest suitable Kerala SISDP **1:10,000** district-level LULC availability and acquisition procedure; please identify which districts and actual observation dates are covered. A written data-use agreement and citation/credit requirements will be respected. We seek georeferenced data for research, not legal certification of parcels.

Do not assert KTH, NRSC, Kerala Government, or any other institution endorses the project. An affiliation or MoU signatory must be genuine. The previously sent SLDC power-system emails are separate and are not evidence that this NRSC request was sent.

## Data admission once the original bytes are received

Record original publisher, product ID, actual coverage dates, retrieval timestamp and route, original URL or formal transfer record, SHA256 of the **source raster AND code legend**, source CRS, transform and nodata, valid classes, spatial footprint and usage/redistribution terms. Retain an original copy privately if terms prevent redistribution; commit source metadata and reproducible transformations instead. Do **not** mirror restricted data publicly without permission.

The source registry is [`configs/lulc_native_acquisition_2024_25.yaml`](../configs/lulc_native_acquisition_2024_25.yaml). Run:

```bash
PYTHONPATH=src python scripts/audit_lulc_native.py
```

Its current expected report is **four product candidates; zero independently admitted native rasters**. If an authentic file is placed at the registry's expected path with its true checksum/CRS/nodata/permission and original legend, the executable checks a single-band categorical GeoTIFF, identical source SHA256, unique legend codes, all observed raster codes contained in the legend, CRS, transform, Kerala approximate *overlap* and valid pixel size. A styled PNG is rejected, and missing source metadata fails closed. The test suite contains a **tiny explicitly synthetic TIFF**, which checks the validator but cannot appear as an NRSC Kerala acquisition.

These checks are **only preliminary source-file QA**. Bounding-box overlap does not establish statewide coverage. Full admission still requires authoritative Kerala state/district mask; no-data/missing-tile percentages; terrain/coast and class-level alignment; product-source accuracy review; harmonized projection/nearest-neighbor resampling for categorical codes; and independently verified protected forests, CRZ/CZMP, wetlands, paddy/wetland legal records, settlements and grid access. Unmapped or ambiguous classes remain `unknown`, **not available land**.

**Ecological-capacity release gate: BLOCKED.** Never invent km² of sitable land or MW from a catalogue, a 1:250K map, colour pixels or an unmatched class legend.
