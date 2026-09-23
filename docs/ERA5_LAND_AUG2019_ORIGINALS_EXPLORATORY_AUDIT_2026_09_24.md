# ERA5-Land real-original August 2019 exploratory weather pilot

**Evidence date: 24 September 2026. Source period: 2019-08-01–2019-08-31 IST.** This is an **executed source-GRIB reanalysis pilot**, NOT completed Phase 5 Idukki catchment rainfall, an official Kerala-state rainfall statistic, flood causality or an SLDC-inflow forecast. The privately prepared 31-day pixel/daily files, QA and reproducer are supplied in the research conversation, **not committed as raw rows or original user uploads**.

**Source:** Copernicus Climate Change Service/ECMWF, *ERA5-Land hourly data from 1950 to present*, DOI [10.24381/cds.e2161bac](https://doi.org/10.24381/cds.e2161bac), [dataset licence / citation](https://cds.climate.copernicus.eu/datasets/reanalysis-era5-land). Results contain modified Copernicus information; neither the European Commission nor ECMWF is responsible for these derived findings. Downloaded original GRIB supplied by the user.

## Originals audited

| Original user-provided file | Dates (UTC) | Fields | Bands | SHA-256 |
|---|---|---:|---:|---|
| Core August | 1–31 Aug 2019 | 14 | 10,416 | `856ba5e4774b0f92d5c9292be850e496a9fac492389adbab751bc3f32e6bf6af` |
| Core July boundary | 31 Jul 2019 | 14 | 336 | `18dd382e62e423017ce42e5acb123d09e808713eb1056edeb88fcbf1767cabef` |
| Extended August | 1–31 Aug 2019 | 10 | 7,440 | `e6d8474aca546e266dfea29b8d23355915ccfac3cfe1a6f0dcabd07d7b9e726a` |
| Redundant extended 31 Aug | 31 Aug 2019 | 10 | 240 | `14c8e647627859c384589475037596f0b1b446cd372123d2970d044817f4dab5` |

The 240 standalone 31 August bands matched corresponding full-month extended source arrays **exactly**. The source grid is **51×41** centres at **0.1°**, bounding box **N13 S8 W74 E78**. Of 2,091 cells, **1,034** carry valid source land values and **1,057** are masked. **That land mask includes adjoining states; it is not a polygon for Kerala's 14 districts or Idukki reservoir.** The extended GRIB's GDAL-undefined `var251 of table 228 of center ECMWF` corresponds to [ECMWF parameter 228251, potential evaporation](https://codes.ecmwf.int/grib/param-db/228251), with signed accumulated metre units. Source numerical temperature fields are in kelvin despite the GDAL band's erroneous '[C]' description; convert numerically **K−273.15** once.

## Conversion: fail closed

Original precipitation, surface/subsurface runoff and solar/radiation/flux terms were **deaccumulated**, not summed as raw accumulations. The UTC **00:00** record is the preceding day's step 24; **01:00** is step 1 of the new forecast day. For a 00 UTC interval, subtract the immediately preceding 23 UTC accumulated value. Thirty independent UTC forecast-day precipitation telescope checks matched each raw 24-hour accumulated field at **zero numerical residual**.

An IST civil day begins/ends at **18:30 UTC**; the UTC hour ending **19:00** crosses local midnight. The algorithm assigns **50% of that hourly increment to each local day**: an explicit uniform-within-hour temporal-allocation assumption, not observed half-hour weather. A complete IST calendar day requires **25 source intervals at every selected cell** (23 full + 2 half). Core source's 31 July input makes **31/31 August 2019 IST precipitation dates complete at all 1,034 land cells**. Extended fields lack their corresponding 31 July originals, so **1 August IST extended values remain absent**. On some additional days there are isolated variable-specific missing pixels (e.g., 15 August downward solar radiation: **1 of 1,034 missing**); all-land complete-case means remain null, never zero-filled.

## Exploratory numeric results — NOT Kerala or Idukki administrative means

Area-weighted averages below use cos(latitude) weighting across **all 1,034 ERA5-Land valid grid centres in the whole bounding box**, including parts of adjoining states. The separately shown region **N9.5–10.3 E76.6–77.5**, 90 valid centres, is an **illustrative Idukki-vicinity rectangle**, not a verified reservoir-intercepted catchment and not Idukki district.

| Derived reanalysis metric | Aug 2019 |
|---|---:|
| Full-bbox land-pixel monthly mean rainfall, summed complete IST dates | **380.65 mm** |
| Idukki-vicinity rectangle monthly mean rainfall, NOT basin | **537.73 mm** |
| Full-bbox highest daily area-mean rainfall | **33.68 mm, 8 Aug IST** |
| Example rectangle highest daily area-mean rainfall | **85.59 mm, 13 Aug IST** |
| Highest single valid source-grid-cell rainfall on 8 Aug IST | **115.96 mm/day** |
| Full-bbox rain summed 6–14 Aug (nine days) | **184.41 mm** |
| Example rectangle rain summed 6–14 Aug | **281.32 mm** |
| Bbox-land mean surface runoff, modelled | **1.27 mm/day** |
| Bbox-land mean sub-surface runoff, modelled | **6.32 mm/day** |
| Bbox-land mean 2 m air temperature | **23.74 °C** |
| Bbox-land mean downward solar radiation | **3.55 kWh/m²/day** over **30 fully complete** pixel-days |

The largest overall land-bbox area-mean rain day is **8 Aug**, whereas the example central rectangle's largest mean is **13 Aug**. Spatial selection materially changes event patterns and totals. The values above **must not be cross-compared as Kerala IMD gauge totals or Idukki catchment inflow**. Modelled surface/subsurface runoff is not measured reservoir discharge, station generation or flood spill.

## Remaining research gates

**Now achieved:** real original hourly August 2019 GRIB decoded for **24 selected parameters**, daily original-timestamp audit, 31 complete August IST core rainfall dates, independently checked source duplicate, valid-land-mask retention and July boundary handling.

**Still missing:** NWIC source-matched official Kerala administrative polygon for a *true statewide statistic*; an independently verified **Idukki reservoir-intercepted contributing catchment** with diversions; all-hour 31 July **extended** fields; source-matched private SLDC reservoir inflow joins; multiple-year meteorological coverage; observed hourly system demand. Hence **zero verified Idukki-basin ERA5 precipitation days** and **no Phase 5 gauge-versus-basin model score** enter the historical conclusions.

The standalone private reproducer and source-derived daily/pixel exports accompany the research-conversation result. This public report intentionally contains only attributable aggregate findings, file hashes, method, scope and unsatisfied gates.
