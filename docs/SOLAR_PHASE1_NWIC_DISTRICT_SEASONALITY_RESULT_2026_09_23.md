# Solar phase 1 — original GSA2 PVOUT × 14 NWIC districts (23 September 2026)

**Bounded descriptive resource-and-seasonality research COMPLETE. Wind and solar remain unadmitted to the 2040 generation/capacity model.**

## Frozen research question

> How does the long-term modelled solar-PV resource and its seasonal variation differ across Kerala’s 14 NWIC districts when Global Solar Atlas 2.0 native pixel centres are assessed with consistent source boundaries?

## Poster-ready conclusion

> Kerala’s long-term modelled PV resource exhibits geographically uneven seasonality that is not apparent from annual PVOUT alone. All **46,241** native Global Solar Atlas 2.0 PVOUT pixel centres within the 14 original NWIC Kerala districts had complete annual, mean-daily and 12-month coverage. The statewide unweighted median annual reference-system PVOUT was **1,493.51 kWh/kWp/year**. Comparing February and July at the **same pixel** gives a median difference of **2.267 kWh/kWp/day** and median **43.60%** February-to-July decrease. The paired median decrease was **32.23% in Thiruvananthapuram** and **49.22% in Wayanad**, demonstrating why a single statewide seasonal factor would mask district-level variation. These are long-term source-climatology, publisher-reference-system resource summaries—not FY2024–25 generation measurements, buildable PV capacity or forecasts for selected PV modules.

**One-sentence takeaway:** Kerala’s modelled solar resource varies across both district and season, so annual PVOUT alone cannot represent district-level solar-generation chronology.

## Evidence and exact partition

[Public-safe aggregate and checks](../data/evidence/solar/gsa2_nwic_district_paired_seasonality_2026_09_23.json) derives from the user's verified 14-layer native-grid private source-window ZIP, SHA-256 `5902fe5ae618a050e7dfdf6d3f3730680514c94a7928450e3d911e4b01e925d3`, and original NWIC national district ZIP, SHA-256 `44c734cc72139f2447dcebfe2791cac862dc5ba265e158912d797cf3410d5c37`, member SHA-256 `2b27a478e24d8c51b0655e74ce3f4f880e75c752e4597550d6fc925ed06ac201`. Original EPSG:7755 administrative polygons are transformed with XY order into the native GSA EPSG:4326 30-arcsecond grid. **Source rasters and polygon coordinates are not committed.** Original India TIFF hashes come from the user's local transport manifest; this run verifies uploaded derived-window member SHA256s and the original NWIC archive, not a second fresh provider acquisition.

| Source-grid QA | Result |
|---|---:|
| Broad Kerala transport rectangle | 565 × 329 = 185,885 pixel centres |
| Finite PVOUT in the transport rectangle | 112,812 |
| Finite pixels outside all NWIC Kerala districts | 66,571 (correctly excluded; **not unassigned Kerala cells**) |
| All pixel centres inside 14 original NWIC districts | **46,241** |
| Inside-district missing in annual/daily/any monthly layer | **0** |
| Inside-district multiply assigned | **0** |
| Exact sum of 14 district source counts | **46,241** |
| Annual/mean-daily ratio expected | 365.25 |
| Maximum absolute observed ratio error | 0.000168 |
| Month-length-weighted 12-month annual reconstruction maximum absolute error | 0.1833 kWh/kWp/year |

**NoData handling:** the annual cropped TIFF's GDAL mask misleadingly labels all 185,885 rectangle pixels valid even where raster data are NaN. The 12 monthly rasters and daily mean share the **actual finite-positive mask of 112,812**. All fourteen layers have the same native grid; the analysis checks the actual values and verifies zero missing data at every NWIC district pixel. February has 28.25 days in the 1999–2018 20-year average; the small annual reconstruction difference is compatible with source monthly output rounded to 0.001 kWh/kWp/day.

## Long-term statewide month-by-month PVOUT

Unweighted **separate monthly source-pixel medians** (kWh/kWp/day), in calendar order: Jan 4.999 · Feb 5.212 · Mar 5.036 · Apr 4.363 · May 3.841 · Jun 3.035 · Jul 2.941 · Aug 3.270 · Sep 3.937 · Oct 3.870 · Nov 4.032 · Dec 4.562. February's separate median is 5.212, July's is 2.941; **neither their difference nor their quotient is the paired median statistic**. For the 46,241 *matched* source pixels, median(Feb−Jul) = **2.267 kWh/kWp/day**, and median(100×(Feb−Jul)/Feb) = **43.60289%**.

## District-normalized results

Alphabetical original NWIC districts, **not an energy-project or land-suitability ranking**. All statistics are unweighted source-pixel summaries; same pixel compared in February and July.

| District | Valid PVOUT pixels | Median annual PVOUT, kWh/kWp | Paired Feb−Jul median, kWh/kWp/day | Paired Feb→Jul median drop |
|---|---:|---:|---:|---:|
| Alappuzha | 1,695 | 1553.41 | 1.793 | 34.68% |
| Ernakulam | 3,635 | 1487.66 | 2.213 | 42.62% |
| Idukki | 5,168 | 1442.55 | 2.536 | 48.38% |
| Kannur | 3,532 | 1502.64 | 2.452 | 47.05% |
| Kasaragod | 2,382 | 1532.95 | 2.490 | 46.90% |
| Kollam | 2,955 | 1487.30 | 1.875 | 36.74% |
| Kottayam | 2,608 | 1475.97 | 1.997 | 39.32% |
| Kozhikode | 2,802 | 1488.58 | 2.267 | 44.15% |
| Malappuram | 4,235 | 1495.70 | 2.233 | 43.11% |
| Palakkad | 5,338 | 1510.31 | 2.319 | 43.94% |
| Pathanamthitta | 3,139 | 1458.81 | 2.092 | 41.19% |
| Thiruvananthapuram | 2,596 | 1498.26 | 1.635 | 32.23% |
| Thrissur | 3,608 | 1516.15 | 2.155 | 41.31% |
| Wayanad | 2,548 | 1504.46 | 2.616 | 49.22% |

## Print- and presentation-ready original figures

- [Twelve-month Kerala PVOUT](assets/solar-phase1-monthly-20260923.svg): individual source-grid marginal monthly medians, not a measured fleet profile.
- [Fourteen-district annual PVOUT](assets/solar-phase1-district-annual-20260923.svg): source-pixel medians, not buildable solar MW or district area.
- [Fourteen-district paired February–July decline](assets/solar-phase1-district-seasonality-20260923.svg): compute the percent change for each pixel, then take each district's median.

All figures are original vector graphics derived exclusively from aggregate values. No restricted geographic shape or original TIFF arrays are reproduced.

## Scope gates remain CLOSED

These publisher-reference-PV-system 1999–2018 source-climatology statistics do not establish permitted solar land/roof/waterbody area, legal exclusions, temperature/degradation/soiling effects on chosen modern PV modules, real Kerala plant production, FY2024–25 hourly generation, grid hosting, installed MW or optimized 2040 system capacity. Rights and specific source vintage remain subject to review. The user's 2018 IIT Bombay/NISE reliability report informs **a later degradation-sensitivity question**, not this GSA climatology calibration. Keep `eligible_area_km2=null`, `installed_capacity_MW=null`, `year_specific_hourly_generation_validated=false`, `model_admitted=false`.

The complete detailed QA report, private-input reproducer and expanded monthly per-district percentile dataset are available in the accompanying conversation's audited solar closeout package; only aggregate/no-geometry evidence belongs in the public repository.
