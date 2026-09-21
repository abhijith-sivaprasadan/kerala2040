# Kerala2040 — consolidated NIWE and solar source analysis

**Review:** 22 September 2026. **Evidence class:** user-supplied originals and original publisher reports, with explicitly limited numerical cross-checks. **Neither a Kerala state-polygon zonal analysis nor an admitted electricity-generation model.**

Source of truth for the 17 solar original upload filenames, sizes, SHA256, provenance and local/not-archived status: [combined solar manifest](../data/evidence/solar/solar_batch_2026_09_21_originals_manifest.json). Original NIWE `Wind.zip` is separately identified in [NIWE source QA](../data/evidence/gis/niwe_150m_user_supplied_source_qa_2026_09_21.json), not counted among these 17 solar-batch originals. Numerical results, uncertainty/status and six sample coordinates are in [consolidated numeric evidence](../data/evidence/solar/solar_wind_consolidated_numeric_2026_09_22.json).

## 1. Executive conclusions

1. **Original acquisition is largely complete for onshore *modelled climatological resources*:** NIWE 150 m national source has 19,475,568 rows; Global Solar Atlas India 2.0 source layers include annual and monthly GHI/DNI/DIF/GTI/PVOUT, TEMP and OPTA, both day-normalised and period-total conventions, native GIS in ASCII grid and/or TIFF; World Bank 2020 Level 1/2 PV study rasters and screening masks are also available in uploaded originals. **Acquisition does not imply Kerala-only clipping, permission to mirror binaries publicly, or model admission.**
2. **Urgent correction to older source notes:** the FY2024–25 NWDP *solar* telemetry is **6,007/6,007 zero W/m²**, across Ambalapuzha (5,986) and Kulamavu (21), *including daytime*. **Reject it as baseline-year irradiance validation.** The 2021–22 portions of the original solar CSV contain nonzero readings; that does not validate FY2024–25. The FY2024–25 NWDP wind has 10,946 values from those two stations and can serve as *partial* meteorological comparison only after height/units/timescale checks. Both “hourly” products have predominantly **30-minute timestamps**.
3. **The GSA `AvgDailyTotals` versus `YearlyMonthlyTotals` ambiguity can be resolved at sampled locations:** for six named illustrative coordinates, yearly PVOUT-total / daily-average = **365.25**; February monthly-total / daily-average = **28.25**; other monthly ratios are 30 or 31. Summing the twelve monthly totals agrees with annual PVOUT total within **0.012%** at these points. February 28.25 is the 1999–2018 *climatological leap-day average*, not the 28-day February 2025. Full-raster numerical equivalence/edge checks are **not** yet done.
4. **NIWE spatial contrasts are material:** nearest 150 m atlas cell at a Palakkad illustrative coordinate has mean **7.879 m/s** and wind power density **420.53 W/m²**; near Kochi **3.193 m/s** and **36.858 W/m²**. These are **modelled long-term cells near chosen coordinates**, not measured project output or a state-level ranking. The NIWE CSV has no timestamps, map CUF, turbine generation or independently verified offshore resource.
5. **NISE 2026 floating-solar report supplies an important third solar pathway:** Kerala **5.73 GWp** for its broader feasible-area estimate; **2.22 GWp** for the report's 20% utilisation scenario. Annexure names include `Arabian Sea` under Kerala waterbody entries and repeated/unusual location labels. The published scenario is a **secondary planning benchmark with data QA requirements**, not an approved resource/build cap.
6. **The 17 original solar files plus separate NIWE upload are NOT yet remotely archived as binaries in this GitHub repo.** Text manifests, file hashes, study README, QA and the release upload/restore code are committed. Do not claim repeatable original-data retrieval from GitHub until real release assets have been uploaded and their hashes rechecked.

## 2. Source hierarchy and non-duplication

| Source family | Original publisher / source link | What it actually supports | Not evidence of |
|---|---|---|---|
| NIWE national 150 m CSV within `Wind.zip` | [NIWE 150 m wind-atlas download](https://niwe.res.in/Open_data_Set/open_wind_dataset/11/) | National 500 m nominal grid, 150 m mean wind speed, Weibull A/k, density, wind power density; 19,475,568 numeric rows | FY2024–25 wind chronology, map CUF, validated buildable MW, offshore wind, on-site mast measurements |
| GSA 2.0 India native annual/monthly AAIGRID ZIPs | [Global Solar Atlas India](https://globalsolaratlas.info/download/india) | Long-term irradiation and PV production climatology; underlying vintage largely 1999–2018; TEMP 1994–2018 | Actual FY2024–25 hourly conditions or independent observations |
| GSA India GeoTIFF monthly/annual pairs | Same publisher and dataset; [source batches 3 and 4](SOLAR_WIND_SOURCE_BATCH_2026_09_21.md) | GeoTIFF *alternative format and normalisation* of existing long-term source; 12 monthly period totals, 12 monthly mean daily totals, annual period totals and daily averages | Independent verification simply because format differs |
| World Bank 2020 PV global-derived study | [Global PV Power Potential by Country](https://globalsolaratlas.info/global-pv-potential-study), © 2020 World Bank, ESMAP-financed, Solargis data | Level 1/2 specific yield, seasonality and illustrative 25-year LCOE; ten raw masks incl. original README | Current Kerala legal permit areas, current Kerala/2040 costs, statutory protected boundaries |
| NWDP Kerala telemetry inside `Solar.zip` | [NWIC Kerala solar](https://nwdp.nwic.gov.in/dataset/solar-radiation-telemetry-hourly-kerala-surface-water-department), [NWIC Kerala wind](https://nwdp.nwic.gov.in/dataset/wind-speed-telemetry-hourly-kerala-surface-water-department) | Solar FY source **fails value QA**; wind FY remains partial instrument comparison | Complete statewide / full-year hourly weather or generation |
| NISE floating-solar 2026 report inside `Solar.zip` | NISE original report, `Solar/NISE_floating potential_report_2026.pdf` | Method-defined Kerala floating-PV water-area scenarios, annexure of listed waterbodies | Site entitlement, engineering study, guaranteed usable water area, electricity generated |
| NISE ground-mounted workbook and PV ageing, NREL/NISE, lead-acid studies | Originals retained in `Solar.zip` / standalone PDFs; details in [source inventory](SOLAR_WIND_SOURCE_BATCH_2026_09_21.md) | Historical resource-planning/reliability/degradation *context* | Current Kerala yield measurements, 2040 battery techno-economics or defensible universal degradation factors |

**Spreadsheet qualification:** the `Ground Mounted.xlsx`, `Hotandcoldprofile23062021_New.xlsx` and country-ranking workbooks were inventoried, but their full numerical tables were **not independently recalculated** in this review. Do not cite an unverified Kerala-specific row from those workbooks. Other ancillary hydrogen/EV/poster files in `Solar.zip` remain adjacent research, not resource time series.

## 3. Corrected FY2024–25 meteorological assessment

The timestamp window is **2024-04-01 inclusive to 2025-04-01 exclusive**; do not infer coverage from `2021_2025` or `1970_2025` filenames.

| FY source | FY rows | Station split | Actual value assessment |
|---|---:|---|---|
| Solar radiation, W/m² | **6,007** | Ambalapuzha **5,986**, Kulamavu **21** | **Every single value zero**, including records at 10:00, 12:00 etc. Unusable for real irradiance, model bias/RMSE, solar production/absence claims |
| Wind speed, km/h | **10,946** | Ambalapuzha **5,096**, Kulamavu **5,850** | Positive values present. Station medians **1.5** and **3.3 km/h**, maxima **12.7** and **21.0 km/h**, respectively. Insufficient temporal and height metadata for 150 m direct comparison |

Both datasets contain mostly minute `:00` and `:30` and mostly 30-minute intervals; there are gaps and only two FY stations. The useful solar 2021–22 segment contains 77,341 nonzero samples, but cannot be treated as actual 2024–25 measured solar. Solar all-zero issue could be sensor failure, reporting default, export error or other data-quality issue; **root cause unverified**. NWDP should be asked for corrected calibrated export, time zone, sensor characteristics, quality flags, and station maintenance history. Wind speeds require divide-by-3.6 to obtain m/s, and a justified 10 m/other sensor height to 150 m adjustment; never compare the two heights directly.

The original observations have user-provided coordinates; independently verify station identity, because unrelated river/basin metadata in the NWDP files can be inconsistent.

## 4. Reproducible GSA *point* calculations — not Kerala-wide statistics

**Method:** sample six approximate city coordinates from both original annual PVOUT GeoTIFFs and each of the 12 matched monthly-total and average-daily PVOUT TIFFs. Check exact unit ratios and annual–monthly consistency before model conversion; see numeric JSON for coordinates and ratios.

| Illustrative nearest raster cell | GSA PVOUT kWh/kWp/**year** | PVOUT kWh/kWp/**average day** | Max/min monthly average-daily PVOUT ratio |
|---|---:|---:|---:|
| Thiruvananthapuram | **1,582** | **4.332** | 1.427 |
| Kochi | **1,575** | **4.313** | 1.615 |
| Palakkad | **1,534** | **4.200** | 1.811 |
| Idukki | **1,473** | **4.032** | 2.042 |
| Kozhikode | **1,577** | **4.318** | 1.637 |
| Kannur | **1,581** | **4.329** | 1.700 |

At these coordinates, winter/pre-monsoon monthly average-daily PVOUT generally exceeds June–July PVOUT; e.g., **Idukki February 5.347, July 2.618 kWh/kWp/day** and **Palakkad February 5.334, July 2.945**. This is climatological modelled seasonality, **not** measured 2024 monsoon or statewide location averages. Rooftop orientation, shading, storage losses, floating-PV temperatures, installation tilt and new module performance may differ. Use GSA as a cross-check, not a historical dispatch profile.

The [2020 World Bank study provided in the upload](https://globalsolaratlas.info/global-pv-potential-study) specifies a *typical large-scale fixed optimum-tilt monofacial crystalline-silicon system* with **3.5% soiling loss, 7.5% other conversion losses and 100% availability**, with its own satellite-derived solar inputs. It is NOT a calibrated rooftop/agrivoltaic/floating/bifacial technology case. Its study LCOE draws on **2018 CAPEX** and illustrative country-group WACC assumptions; study degradation assumptions (**0.8% first year, 0.5% subsequent years**) are not default Kerala2040 projections.

**Critical different-area distinction:** GSA annual LTA PVOUT raster represents a *potential production per installed kWp*; its numeric values **must not be multiplied by all Kerala land pixels as though each is a buildable kWp**. Capacity must be established independently after technology-specific land/water/grid screening.

## 5. NIWE six-cell resource comparison

The complete supplied NIWE source was previously parsed as 19,475,568 national cells; for this review the full original CSV was streamed again to find the nearest 150 m data row at the same six approximate city coordinates (nearest distances about 0.07–0.26 km).

| Illustrative nearest NIWE atlas cell | Mean wind at 150 m (m/s) | Atlas wind power density (W/m²) |
|---|---:|---:|
| Thiruvananthapuram | **4.674** | **112.27** |
| Kochi | **3.193** | **36.86** |
| Palakkad | **7.879** | **420.53** |
| Idukki | **4.684** | **133.21** |
| Kozhikode | **3.336** | **45.12** |
| Kannur | **3.494** | **49.10** |

These are **long-term modelled point cells at 150 m**, not ten-minute mast records, plant-specific capacity factors or proof of developable wind at the exact urban coordinate. In particular, do not generalise an illustrative city-cell value to all of Palakkad Gap, Kerala or neighbouring Tamil Nadu.

The source has seven fields: lon, lat, mean speed, Weibull A, Weibull k, air density and wind-power density; **no timestamps, monthly direction, CUF, turbine model, forecast year or verified offshore data**. The NIWE map's user-selected **30,671.25 MW / 6,815.83 sq km** at CUF≥25% reflects an approximate **4.5 MW/sq km unscreened map assumption**, not a validated state polygon or project capacity. Offshore wind is a **separate** resource/acquisition workstream and is NOT implied by a buffered onshore NIWE polygon.

## 6. Why the study masks do not grant land eligibility

The [2020 World Bank global PV study](https://globalsolaratlas.info/global-pv-potential-study) defines its **Level 1 physical/technical screens** in part using within-cell elevation range >300 m or std >60 m, major waterbodies, forest cover ≥50%, remote land >25 km from population clusters and densely built-up areas. **Level 2 adds** global-study proxies for cropland and IUCN-classed protected areas. These are 30-arcsecond global/remote-sensing *research criteria*; they are **not** Kerala Forest Department notified boundaries, gazette status, wetland notifications, land-title evidence or KSEBL grid connection approval. They were set for large-scale ground-mounted PV and do not automatically prohibit rooftops, agrivoltaics or purpose-built floating PV.

The 2020 derived `PVOUT_level1` / `PVOUT_level2` and individual masks must be interpreted with exact pixel values, relevant mask inclusion semantics, nodata, grid alignment and actual Kerala geometry; do not merely count white/black colour categories as compliant land. The `PVOUT_seasonality_index` is a long-term ratio (max/min month) and provides **no hourly complementary dispatch guarantee**. The 25-year LCOE raster is **historic study economics**, not a Kerala 2040 tariff.

## 7. NISE floating solar: new quantifiable pathway, but not yet admitted

The user-supplied NISE `NISE_floating potential_report_2026.pdf` gives **Kerala** in Table 6 (printed p.41):

| NISE Kerala study scenario | Water area | Scenariowise area | Potential |
|---|---:|---:|---:|
| Broader feasible-area study | 219.02 km² initial waterbody area | 109.19 km² feasible | **5.73 GWp** |
| 20% surface-utilisation limit | Same source waterbody area | 42.29 km² | **2.22 GWp** |

Do not add both alternatives together; they are **alternative constraints on the same waterbody inventory**. Annexure (printed pp.67–70) has at least two entries labelled **Arabian Sea** as Kerala waterbodies and potentially questionable hill/place-name records; verify actual water polygons, hydropower operating levels, navigation/fishing/access, conservation, anchoring, reservoir operators and grid evacuation before claiming buildability. For hydro reservoirs, explicitly study PV output *alongside reservoir operations* rather than treating the surface as an always-free development parcel. These figures are not FY2024–25 installed floating PV or energy output.

## 8. What is ready for Kerala2040 now

**Admissible as properly labelled SOURCE or context evidence:** original NIWE national 150 m atlas; long-term GSA source rasters; exact source metadata/hashes; six illustrative GSA/NIWE cell QA; 2020 World Bank screening method and historic costs; NISE 2026 indicative floating-PV study; partial NWDP wind values.

**Reject as historical model validation:** all-zero NWDP FY2024–25 solar, NIWE map CUF colours as hourly observations, 2020 LCOE as 2040 Kerala cost, historical PV ageing figures as technology-universal performance, any blanket assumption that GSA masked cells are legally buildable, and any presentation of the buffered 30.7 GW NIWE map popup as a true Kerala capacity cap.

**Still to perform (separate scientific and acquisition gates):**

- Obtain **actual valid FY2024–25 Kerala irradiance observations or measured PV-plant generation**; query NWDP on its all-zero export. Obtain wind mast measurement height/time zone and site data, ideally genuine 150 m/multi-height observations at candidate corridors.
- Fix and verify NWIC Kerala boundary; clip native GSA and NIWE at original grids, handle coast/border properly, measure source nodata and nodata/coverage; separately define offshore study area with **actual offshore wind and marine/bathymetric data**.
- Build hourly PV/Wind conversion from already source-QA-passed FY2024–25 ERA5 for appropriately selected locations; compare climatology/observed periods without calling GSA or NIWE an hourly baseline. Model actual plant technical losses, Weibull/turbine curves, 150 m vertical profile, uncertainty, availability and curtailment explicitly.
- Obtain authoritative Kerala conservation/LRIS/NRSC, soil/terrain, reservoir and grid geometry; calculate scenario-specific eligible site/area/capacity ranges. Obtain updated technology and financing input data independently.
- **Archive actual binaries**: the 17 large solar original assets plus separate NIWE Wind original remain absent from remote GitHub. Manifest + restore scripts alone do **not** satisfy the user's requirement “we have data in repo rather than needing the source each time.” Use same-repo GitHub Release assets after per-original redistribution review, and remote-SHA validation; otherwise authorized private immutable storage with source hashes.

**Repository gate:** FY solar weather validation **FAIL**; source acquisition substantial but **binary archival OPEN**; exact Kerala wind/PV resource mapping and independently validated generation **OPEN**.
