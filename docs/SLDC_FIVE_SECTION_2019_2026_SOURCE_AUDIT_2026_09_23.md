# Kerala SLDC 2019–2026 five-section archive: initial source audit

**Status:** dated daily observations curated; field-level evidence NOT continuous hourly demand, not a validated 2040 dispatch model.

Original user-supplied ZIP SHA-256: `2d55fefdcbfcacf7f753cebb0c429479abb6ea5eedb2533297a455735b6bfc3f`. Period 2019-08-06 through 2026-09-23 inclusive, 2,606 requested dates. Original HTML accepted only when requested date, source returned date and SHA-256 match the saved JSON. **Zero** accepted-file checksum/date mismatches; no fabricated daily values.

## Complete inventory

| Section | Verified source days | Rejected source days |
|---|---:|---:|
| statistics | 2,576 | 30 |
| imports | 2,576 | 30 |
| storage | 2,577 | 29 |
| availability | 2,577 | 29 |
| other_extrema | 2,577 | 29 |

One additional valid dated Storage, Availability and Others report is present on 2022-07-06 while Statistics and Imports are missing. Do not require complete five-section intersection for reservoir or extrema analysis. The 2026-09-23 response is absent/not final; 2019-08-06 is the user-selected starting point, not proven the earliest day at this site.

## Daily accounting source quality

Reports use 614 older 44-row Statistics layouts (`Generation`) and 1,962 later 73-row layouts (`Internal Generation`). The older source lacks many later accounting columns; they remain blank rather than zero. The Imports page from the later period also repeats generation stations; **do not add those station figures to Statistics generation**. Net Import in Statistics matches the Imports page for all 2,576 paired days.

**One source-level contradiction:** 2019-12-05 shows Generation = 15 MU, Net Import = 57.3783 MU and Consumption = 15 MU. The reported balance residual is **57.3783 MU**. The original three cells are preserved in `daily_system.csv` and flagged; this day is excluded from `consumption_qualified_mu` rather than silently corrected to a calculated 72.3783 MU. Remaining daily energy-balance residuals are within 0.02 MU.

## Observed fiscal-year statistics

The sum is **only over qualified observed days**, never a complete-FY total when reports are missing. The import share is the **median daily Net Import / Consumption ratio**.

| FY | Calendar days in scope | Qualified consumption days | Observed consumption MU (partial if gaps) | Median daily import share | Maximum reported evening peak MW |
|---|---:|---:|---:|---:|---:|
| 2019-20 | 239 | 237 | 16,536.4963 | 76.5% | 4,249 |
| 2020-21 | 365 | 365 | 25,145.0594 | 69.9% | 4,349 |
| 2021-22 | 365 | 362 | 26,375.1739 | 62.6% | 4,406 |
| 2022-23 | 365 | 362 | 27,518.0651 | 69.1% | 4,539 |
| 2023-24 | 366 | 365 | 30,868.1181 | 79.6% | 5,303 |
| 2024-25 | 365 | 354 | 30,666.2569 | 77.1% | 5,854 |
| 2025-26 | 365 | 356 | 30,436.1937 | 69.5% | 5,861 |
| 2026-27 | 176 | 174 | 16,195.2629 | 76.9% | 6,195 |

2024–25: **354/365** qualified daily observations, **30,666.2569 MU observed across those 354 days** (not a full FY annual total), median daily reported Net Import / Consumption **77.1%**, maximum reported Evening Peak **5,854 MW**. The archive-wide highest *Evening Peak* is **6,195 MW on 2026-04-23**, a source-specific statistic, not a matched half-hour demand interval.

## What is available in the curated ZIP

- `daily_system.csv`: all 2,606 calendar dates with section-by-section status, qualified and reported daily accounts, peak MW/times, frequency and reservoir total when reported.
- `source_calendar.csv`: 13,030 date-section status records and original HTML SHA256 references.
- `generation_rows.csv`: original source-labelled daily station and aggregate energy rows; `import_rows.csv`: report-labelled import/interface rows; both preserve source order.
- `reservoir_rows.csv`: level, storage, capability and inflow fields for named reservoirs; shortened eight-row source pages preserve only the five explicitly present reservoirs.
- `extrema_rows.csv`: selected maximum/minimum half-hour ranges with event, period and frequency; NOT every half-hour interval.
- `availability_rows.csv`: variable source-shaped, source-order-preserved schedule/availability lines; the source header is **Energy in MU**, not available MW.
- `monthly_summary.csv`, `financial_year_summary.csv`, `qa_manifest.json`, and the offline reproducer.

## Research gates

Source-to-model priority: (1) complete dated daily historical baseline and field coverage, (2) source-reconciliation against previously processed FY24–25 baseline, (3) demand-peak and imports by season, (4) hydro and availability-field QA, (5) separate acquisition of independently metered 15/30/60-minute demand and generation. Do not use daily reported peak times to reconstruct an unmeasured full-day load curve.

## GitHub and redistribution

Public repository: executable reproducer, summary QA and research result only. Original HTML, detailed source-labeled rows and derivative daily values are packaged for local analysis and should not be published to a public remote until original-source redistribution terms are verified. The nine compressed curated CSVs are stored in the user's separate **private** `kerala2040-source-archive` repository under `curated/sldc_2019_2026/`, pinned to original CSV and gzip SHA-256s. Original third-party source HTML is not stored in this public repository or in that private curated-table directory. Private GitHub access is not public redistribution permission.
