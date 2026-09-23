# Kerala2040 · SLDC daily electricity system: advanced descriptive analysis, phase 2

**Frozen input:** 6 August 2019–23 September 2026, official Kerala SLDC five-section dated HTML archive; original ZIP SHA-256 `2d55fefdcbfcacf7f753cebb0c429479abb6ea5eedb2533297a455735b6bfc3f`. This is a new analysis of the previously source-audited daily archive, **not** a forecast, hourly data product, or installed/available capacity MW estimate. Reproduce with `analysis/analyze_sldc_2019_2026.py` and the private curated CSVs. See the separate source audit, which remains authoritative for source acceptance.

## Executive findings

1. **Longer-run rise, recent flattening.** Among **356 matched month/day observations** in FY2020–21 and FY2025–26, mean reported consumption increased **24.1%**, from **68.88 to 85.49 MU/day** (+16.61 MU/day). Relative to FY2023–24, FY2025–26 is **+1.17%** on 355 common month/days; relative to FY2024–25, **-1.28%** on 345 common month/days. No missing-day estimate enters these figures. FY2020–21 is a potentially atypical pandemic baseline; differences are descriptive, not projections or causal claims.
2. **Imports vary substantially with hydro and year.** On observed qualified days, the *energy-weighted reported net import share* is **60.4%** in FY2021–22, **78.8%** in FY2023–24 and **65.4%** in FY2025–26. Corresponding hydel/consumption shares are **37.5%**, **18.5%**, **31.7%**. Shares use summed MUs, not averages of percentages. These components are linked mechanically by the daily energy balance; **do not infer hydro's causal effect from their inverse movement**.
3. **Peak stress diverges from average energy.** The source Statistics table's recorded maximum Evening Peak is **4,349 MW** in FY2020–21 and **5,861 MW** in FY2025–26. The corresponding observed-evening-peak 95th percentiles are **4,044** and **5,177 MW**. The largest reported *Statistics Evening Peak* in the archive is **6,195 MW on 23 April 2026 at 22:30 IST**; 2026–27 is a partial period and must not be treated as a completed fiscal year.
4. **Idukki storage's seasonal cycle is conspicuous.** In the named Idukki reservoir rows (not statewide storage), the multi-year median reported storage is **34% in May, 33% in June**, and **77–78% in October–November**. FY2023–24's minimum Idukki report is **14% on 16 June 2023**, versus **30% on 21 May 2025** in FY2025–26. This is reservoir level/energy-context evidence, **not a dispatchable MW rating or proof of a weather cause**.
5. **A cross-section peak contradiction/definition problem needs resolution before merging tables:** on 23 April 2026, the Statistics Evening Peak is **6,195 MW** but Others' maximum evening consumption extrema is **5,950 MW**; across 2,574 paired dates, only 15 values are exactly equal. These are two source-labelled series, **not interchangeable duplicate measurements**.

## Daily electricity and peak indicators by fiscal year

Each `mean` is over the *qualified observed days*, not a gap-filled annual daily mean. `Import %` and `hydel %` are sums of observed energy divided by sum of observed qualified consumption. The peak P95 uses observed days where that peak field exists; the maximum is source-reported, not a continuous measured load-trace statistic.

| FY | Qualified days / date slots | Mean MU/day | Import energy % | Hydel energy % | Evening-peak P95 MW | Max evening peak MW |
|---|---:|---:|---:|---:|---:|---:|
| 2019-20 † | 237/239 | 69.77 | 76.1% | 22.5% | 3,958 | 4,249 |
| 2020-21 | 365/365 | 68.89 | 69.6% | 28.3% | 4,044 | 4,349 |
| 2021-22 | 362/365 | 72.86 | 60.4% | 37.5% | 4,173 | 4,406 |
| 2022-23 | 362/365 | 76.02 | 65.8% | 31.5% | 4,305 | 4,539 |
| 2023-24 | 365/366 | 84.57 | 78.8% | 18.5% | 5,015 | 5,303 |
| 2024-25 | 354/365 | 86.63 | 73.8% | 23.5% | 5,488 | 5,854 |
| 2025-26 | 356/365 | 85.49 | 65.4% | 31.7% | 5,177 | 5,861 |
| 2026-27 † | 174/176 | 93.08 | 76.9% | 20.4% | 5,892 | 6,195 |

† FY2019–20 covers 2019-08-06 onward; FY2026–27 ends 2026-09-23 and ends on an acquired-snapshot source gap on 23 September 2026. FY2024–25: **354/365** qualified days; **30,666.2569 MU is their sum, not an annual total**. Confirmed gaps are *not* set to zero or interpolated. The 5 December 2019 source balance contradiction is retained as a flagged record but excluded from qualified daily consumption.

## Like-for-like calendar dates: FY2020–21 versus FY2025–26

Only matched calendar month/day keys are compared, excluding FY2025–26 gaps; leap-day alignment is not fabricated. Changes compare means computed on the **same selected day keys**. Month-by-month change is descriptive and cannot be interpreted as a climate-controlled growth rate.

| Calendar month | Paired dates | FY2020–21 MU/day | FY2025–26 MU/day | Change |
|---|---:|---:|---:|---:|
| 1 | 30 | 70.2 | 84.3 | +20.1% |
| 2 | 27 | 74.8 | 90.5 | +21.0% |
| 3 | 31 | 82.4 | 98.8 | +19.8% |
| 4 | 29 | 68.2 | 94.8 | +39.0% |
| 5 | 28 | 70.8 | 88.8 | +25.4% |
| 6 | 29 | 64.1 | 80.7 | +25.9% |
| 7 | 30 | 62.4 | 76.4 | +22.3% |
| 8 | 31 | 62.6 | 80.0 | +27.8% |
| 9 | 30 | 63.7 | 83.2 | +30.7% |
| 10 | 31 | 67.0 | 84.6 | +26.2% |
| 11 | 29 | 70.6 | 83.8 | +18.7% |
| 12 | 31 | 70.1 | 80.8 | +15.3% |

Additional comparable-period checks: FY2023–24 → FY2025–26 is **+1.17%** (n=355); FY2024–25 → FY2025–26 **-1.28%** (n=345). The 2024–25 and 2025–26 *observed totals* should not be directly compared because they omit different days.

## Monsoon and import/hydro variability: source-reported energy

| Calendar year and season | Observed days | Mean consumption MU/day | Net import energy / consumption | Hydel energy / consumption |
|---|---:|---:|---:|---:|
| 2023 Mar–May | 92 | 90.39 | 76.2% | 21.4% |
| 2023 Jun–Sep | 121 | 79.51 | 78.2% | 18.4% |
| 2024 Mar–May | 92 | 98.85 | 80.3% | 17.7% |
| 2024 Jun–Sep | 119 | 80.08 | 61.9% | 34.6% |
| 2025 Mar–May | 85 | 93.67 | 76.9% | 20.9% |
| 2025 Jun–Sep | 120 | 80.07 | 47.6% | 48.8% |

**Interpretation boundary:** These contrasts show reported seasonal operations in years with different inflow, temperature, demand, generation and scheduling conditions. Since internal generation + net import ≈ consumption by construction, an inverse hydro/import share is not independent evidence of causality. A matched rainfall/ERA5/PV time-series and verified metered interval chronology are separate acquisition tasks.

## Peak events from the Statistics table

| Date | Source Evening Peak MW | Recorded peak time IST | Daily qualified energy MU |
|---|---:|---|---:|
| 2026-04-23 | 6,195 | 22:30 | 115.28 |
| 2026-04-26 | 6,093 | 22:29 | 109.10 |
| 2026-04-17 | 6,086 | 22:23 | 116.11 |
| 2026-04-22 | 6,054 | 22:30:12 | 112.07 |
| 2026-04-18 | 6,037 | 22:27 | 117.16 |
| 2026-04-14 | 6,016 | 22:54 | 112.52 |
| 2026-04-27 | 5,991 | 21:44 | 118.26 |

In the top-15 ranking (seven shown), all are reported Statistics metrics. On the 2,575 qualified energy dates, the archive contains a separate selection of morning and evening peaks; for dates with both fields the median *within-day* difference (evening minus morning) is **798.5 MW**, with evening exceeding morning on **99.84%** of paired dates. This is not a time-of-use energy or sub-hourly ramp estimate.

## Idukki reservoir: monthly reported storage

These are named Idukki-only percentage entries, including dates where shorter Storage reports lack other reservoirs. No arithmetic averaging across different reservoir capacities is used.

| Month | Source days | Median Idukki storage | 10th–90th percentile |
|---|---:|---:|---:|
| Jan | 216 | 70% | 59%–86% |
| Feb | 194 | 62% | 53%–74% |
| Mar | 213 | 51% | 45%–61% |
| Apr | 208 | 41% | 34%–50% |
| May | 214 | 34% | 24%–40% |
| Jun | 208 | 33% | 16%–47% |
| Jul | 215 | 39% | 26%–65% |
| Aug | 242 | 63% | 32%–79% |
| Sep | 230 | 69% | 36%–81% |
| Oct | 215 | 77% | 48%–90% |
| Nov | 206 | 78% | 54%–95% |
| Dec | 216 | 76% | 59%–95% |

**Station-granularity QA gate:** `Idukki` generation rows are present on 334 of the 356 qualified FY2025–26 days, while the aggregate `Hydel Total` is present on all 356. Missing station lines must not be treated as station zero generation; establish station-row completeness and plant naming before explaining aggregate hydro changes by individual projects.

**Separate reservoir QA flag:** `KUNDALA` reports **397% on 13 March 2026** in the curated table. I inspected the original dated HTML: its KUNDALA row itself contains `1589.5 | 30.9 | 397` after the reservoir name, whereas the adjacent days display ~98% and normal reservoir levels. This is a **source-report anomaly, not merely a normalization artefact**. Exclude 397% from percentage-based reservoir analysis pending a publisher correction; **do not silently clamp it to 100%**. This outlier does not affect the named Idukki analysis above.

## Priority 3: model-input closure checklist

- **Measured interval load:** Obtain separately; the daily peak and Others' selected 30-minute extrema do not specify the other 46/47/95 demand intervals per day.
- **Demand calibration:** Compare source-reported daily MU against CEA/KSEBL annual statistics only on a like-for-like fiscal year and population; resolve confirmed gaps via explicit sensitivity bounds, not zero-fill or claim a complete annual sum.
- **Hydro:** Link station-level daily MU to the corresponding reservoir and upstream/downstream topology; verify current plant and reservoir names, inflows, limits and restrictions before creating a dispatchable hydro MW or energy model.
- **Imports/grid:** Source-reported daily net import energy does not equal firm ATC/TTC MW, available transfer capability, contract rights or import price.
- **Peak schema crosswalk:** Investigate why Statistics evening peak and Others evening-extrema consumption diverge; inspect original source headings and timestamps before adopting a single peak KPI.
- **Data integrity:** Keep confirmed 29 all-section dates missing, partial 6 July 2022, excluded 5 December 2019 balance contradiction, duplicate Others event 9 December 2019 and Kundala outlier auditable. Data source is the archived HTML, not the derived report.

**Publication classification:** descriptive daily SLDC source-reported evidence, not full-year measured interval telemetry or a validated 2040 techno-economic result. Private original HTML and source-labelled daily row data are not public-licensed by their presence in a private GitHub repository.
