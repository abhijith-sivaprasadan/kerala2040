# Kerala2040 — Phase 5 Idukki ERA5-Land basin weather

**Status (23 September 2026): offline pipeline implemented, NOT real-data-executed.** The source-verified 2018–2026 ERA5-Land originals and an independently validated Idukki reservoir catchment polygon have NOT been supplied. **Zero real basin-weather days processed here; no new model-skill result.** The existing Phase 4 SLDC/Idukki gauge analysis remains the last executed observed result.

## Research question and admission gates

Can area-weighted reanalysis rain over the *actual reservoir-intercepted Idukki drainage area* improve the model of source-reported reservoir inflow compared to the SLDC single Idukki rain gauge, evaluated on identical held-out dates?

The official [NWIC CWC basin inventory](https://nwdp.nwic.gov.in/dataset/basin-cwc) and [India hydrological boundary catalogue](https://www.data.gov.in/catalog/hydrological-boundaries) offer basin/sub-basin/watershed acquisition routes. These **do not establish** an Idukki reservoir-intercepted catchment polygon, source-vintage match or upstream Mullaperiyar/diversion handling. A broad Periyar basin, administrative district, hypothetical bbox or five ERA5 locations is **not** the required rainfall support. Select and independently review one original WGS84 catchment feature; verify outlet connectivity, source area and source-use conditions. Never republish original polygons without a reuse decision.

## Offline processing sequence

**1. CDS request, locally and opt-in.** Existing script:

    python scripts/request_era5_land_hydro_monthly.py --area N W S E --out PRIVATE_DIR

The dry-run plan requests original ERA5-Land total precipitation and 2m temperature in monthly GRIB from **2017-12-31 through 2026-09-23** (first day provides IST boundary context). Inspect source-verified bbox, availability, CDS terms, credentials and planned time coverage before adding **--execute**. The script does not invent a basin polygon or claim a complete data download. Account for preliminary 2026 versus consolidated reanalysis.

**2. Inspect/extract original GRIB.** Use a local Python environment with cfgrib/eccodes; original GRIB remains private. Example for one monthly file (the source tp and 2m temperature may be in the same GRIB):

    python scripts/extract_idukki_era5_land_grib.py --tp-grib PRIVATE/2018_01.grib --t2m-grib PRIVATE/2018_01.grib --out PRIVATE/hourly.csv --grid-out PRIVATE/grid.csv

Expand BOTH source file lists in corresponding month order for the historical archive. This stage checks units (tp metres, temperature kelvin), original accumulated tp, pixel/hour uniqueness and consistent grids, and emits an input SHA-256 manifest; it does not derive daily rainfall.

**3. Independently review catchment and generate weights.** Install shapely and pyproj or the project's geo extras, then supply source-area, reviewed polygon, metadata and *actual* original grid spacing:

    python scripts/build_idukki_phase5_weights.py --geometry PRIVATE/idukki_intercepted_catchment.geojson --grid-csv PRIVATE/grid.csv --grid-spacing-deg 0.1 --source-id VERIFIED_SOURCE_ID --source-url https://SOURCE --reviewer YOUR_NAME --expected-area-km2 SOURCE_AREA --out PRIVATE/weights.csv

Cell-overlap weights use EPSG:6933 equal-area intersections. The source area and intercepted-catchment identity are independent hydrological review inputs, not invented defaults. The script can validate geometry and area but cannot prove the source polygon represents the correct reservoir. Re-extract original GRIB with **--weights-csv PRIVATE/weights.csv** and a NEW private hourly output, then use that selected-cell output below.

**4. Derive IST weather and compare with actual private SLDC data.**

    python analysis/idukki_phase5_weather.py --hourly-csv PRIVATE/selected_hourly.csv --weights-csv PRIVATE/weights.csv --curated PRIVATE/SLDC --out PRIVATE/phase5

Every source pixel needs 25 nonmissing original hourly increments per IST date: 23 full hours and the two UTC hours crossing local midnight, each allocated 50% to the adjacent dates. Because ERA5-Land is hourly and IST is UTC+05:30, this half-hour split is an **explicit within-hour uniform-rate assumption**, not observed 30-minute rainfall. ERA5-Land timestamp 00 UTC represents the previous day's step 24: its hourly increment needs previous 23 UTC; timestamp 01 UTC is the new day's step 1. Local-day assignment uses UTC interval end +05:30 and an explicit 50:50 split of hours ending at 00:30 IST. Incomplete days and grid mismatches fail closed instead of producing partial sums or treating missing weather as zero. See [ECMWF accumulation guidance](https://confluence.ecmwf.int/spaces/CKB/pages/462888259/ERA5+family+post-processed+daily+statistics+documentation).

The processor writes the source-dated *private* weather daily CSV and QA JSON to the PRIVATE output directory. Do not commit any detailed daily rows, source GRIB, unreleased source polygons or unapproved source data into the public repo.

## Chronological, genuinely paired evaluation

Phase 5 trains through 2024-12-31 and tests from 2025-01-01, using identical complete-case training and test dates for the source Idukki rain gauge, ERA5 basin rain, and observed previous-day-inflow persistence. At least **100 train and 50 test days** are required to score each separate experiment:

- **Antecedent only:** precipitation at t−1 to t−7 plus observed inflow t−1. No rainfall at t, but operational real-time skill is still not established.
- **Same-day retrospective diagnostic:** rain t to t−7 plus reported inflow t−1. Do NOT label as a forecast.

The output reports paired population counts and holdout MAE/RMSE only when actual source data are supplied. Source reanalysis is a modelled weather history, not an observed catchment rain gauge. No flood causality or 2018 electricity is inferred from weather. The 2018 SLDC daily electricity population remains **zero**.

## Still closed

| Evidence/model gate | Status in this branch |
|---|---|
| Original source-verified 2018–2026 ERA5-Land hourly files | Not acquired or processed |
| Reviewed intercepted-reservoir polygon and diversion scope | Not supplied |
| Completed real basin-weighted IST daily weather | Zero real rows |
| Actual paired Phase 5 holdout scores | None |
| 2018 dated SLDC electricity or hourly load | None |
| Spill, turbine release, reservoir rule curves, PSP site constraints | Not established |

No new quantitative basin-weather/forecast finding should enter the public site until the original source execution and audit pass. Synthetic tests verify programming conventions, **not** weather accuracy or basin polygon provenance.
