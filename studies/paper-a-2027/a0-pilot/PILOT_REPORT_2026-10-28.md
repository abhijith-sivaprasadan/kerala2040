# Kerala2040 — Paper A0, first reproducible source-accounting pilot

**Research note v0.1, 28 October 2026**  
**Classification:** empirical recomputation from **existing public processed files**, not independently re-extracted original HTML and not a completed journal manuscript.  
**Source code:** `scripts/run_paper_a0_pilot.py`; conservative regression tests: `tests/test_paper_a0_pilot.py`.

## 1. Scientific question and working contribution

**Question:** Can a small, source-aware ledger explicitly distinguish annual consumer energy, utility sales, utility energy input and partial-day operational electricity totals, while reproducing actual reported-date coverage and enforcing arithmetic/error integrity?

**Hypothesis worth testing across the eventual dataset:** A version-aware measurement and source-admission method will find substantively different eligibility and reconciliation outcomes from a naïve approach that treats all entries labelled "Kerala electricity consumption" as the same complete-FY measurement.

**Null / failure mode:** A0 reproduces already-documented distinctions but cannot show an important new error, a reproducible new method or a transferable benefit relative to prior publication practice. In that event, a transparent technical report is more appropriate than a novel journal article.

## 2. Data and source provenance

We use an existing, **processed** FY2024–25 CSV checked into the public Kerala2040 repository:

- `data/external/sldc_fy2024_25/daily_balance.csv`, one row per date (including explicit `missing` status) from 1 April 2024 to 31 March 2025.
- `data/external/sldc_fy2024_25/qa_report.json` records the provenance of the earlier user-acquired SLDC HTML archive, per-response SHA references, original download coverage and source-date checks. That earlier review states **1,770 dated HTML responses (354 × five sections)**, zero raw checksum and date mismatch and no fabricated daily values; this pilot **does not independently re-open those HTML bytes**.
- `docs/DEMAND_SECTOR_ACCOUNTING_BASELINE_2026_09_23.md` independently identifies precise Kerala Economic Review 2025 Vol. I and II definitions and source pages. We transcribed its six source-specific values into [TABLE_A0_01_reporting_boundary_ledger.csv](TABLE_A0_01_reporting_boundary_ledger.csv). The original PDFs were **not page-visually rechecked in this pilot**.
- The complete five-section 2019–2026 source-audit document `docs/SLDC_FIVE_SECTION_2019_2026_SOURCE_AUDIT_2026_09_23.md` gives the longer-term schema and QA context, not independently checked new numerical outcomes here.

Original authority links as already recorded in the project:
[Kerala Economic Review 2025 Volume I](https://spb.kerala.gov.in/sites/default/files/2026-01/ER%202025%20Volume1%20Eng%20final.pdf);
[Kerala Economic Review 2025 Volume II](https://spb.kerala.gov.in/sites/default/files/2026-01/ER%202025%20Volume%202%20Eng%20final.pdf);
[Kerala SLDC dated public statistics](https://sldckerala.com/index.php?id=1).

**Caution:** The Economic Review transcriptions come from an existing project audit. The project has identified page locators, but this new computation is not a second independent transcription of those official PDFs.

## 3. Measurement ontology — first six cases

| Source ID | FY2024–25 value, MU | Reporting definition | Coverage |
| --- | ---: | --- | --- |
| A0-FY25-01 | 29,311.76 | Broad state consumption, including open-access/captive | Annual official |
| A0-FY25-02 | 28,544.05 | KSEBL all-category sales incl. outside-state trading / bulk licensees | Annual official |
| A0-FY25-03 | 28,879.64 | KSEBL within-state sales with captive adjustment | Annual official |
| A0-FY25-04 | 31,848.07 | KSEBL generation plus purchased energy, utility-side | Annual official |
| A0-FY25-05 | 32,306.15 | Total energy input to Kerala periphery incl. open-access wheeling adjustments | Annual official |
| A0-FY25-06 | 30,666.2569 | Sum of SLDC reported operational consumption on **354 observed dates** | Partial daily source |

These are **not** six estimates of a single common physical quantity. The ledger is the first version of a machine-readable measurement ontology, *not* a claim that publisher or operator reconciliations have been demonstrated.

Our admissibility rule is deliberately strict: same numerical units or financial-year names are insufficient for subtraction, ratio, trend or loss calculations. We require both (i) the same source-defined physical customer, geography, meter and accounting boundary, and (ii) the same qualified time coverage and revisions. Even then, independent source transformation and inclusions/exclusions must be checked.

[Table A0-03](TABLE_A0_03_comparison_admissibility.csv) blocks four high-risk direct comparisons: annual consumer-side vs incomplete daily SLDC, all-category utility sales vs adjusted in-state sales, consumer use vs periphery input, and in-state sales vs utility generation/purchases. **No ambiguous difference has been assigned a "transmission loss", "energy deficit" or "import gap" label.**

## 4. Recomputed pilot results — daily coverage and reported accounting

The new independent calculation *from the processed CSV* re-read 365 dated rows, confirmed 365 distinct calendar dates, and returned:

| Pilot metric | Recomputed result |
| --- | ---: |
| Qualified observed daily reports | **354** |
| Explicitly missing source-day reports | **11** |
| Coverage of FY2024–25 calendar days | **96.9863%** |
| Observed-day internal generation | **8,031.2393 MU** |
| Observed-day net imports | **22,635.0183 MU** |
| Observed-day reported consumption | **30,666.2569 MU** |
| Observed-day hydro generation, subset of internal generation | **7,214.4710 MU** |
| Largest absolute daily balance residual | **0.0001 MU** |
| Sum of daily rounded energy-balance residuals | **+0.0007 MU** |

The per-day signed check is `internal_generation_mu + net_import_mu - consumption_mu`. Differences up to 0.0001 MU are consistent with the processed file's displayed precision. The aggregate difference is not an unexplained full-year residual: it results from summed rounded daily fields. Hydro is a **subset** of internal generation; adding it again would double-count.

This arithmetic check tests whether processed values remain numerically internally consistent. **It does not verify that the original SLDC daily reports are free of all errors**, that net imports match settlement metering, or that the published numbers are on a common boundary with the Economic Review.

### Month-level completeness

| Month | Observed / expected days | Missing |
| --- | ---: | ---: |
| Apr 2024 | 30 / 30 | 0 |
| May 2024 | 31 / 31 | 0 |
| Jun 2024 | 30 / 30 | 0 |
| Jul 2024 | 31 / 31 | 0 |
| Aug 2024 | 30 / 31 | 1 |
| Sep 2024 | 28 / 30 | 2 |
| Oct 2024 | 30 / 31 | 1 |
| Nov 2024 | 28 / 30 | 2 |
| Dec 2024 | 30 / 31 | 1 |
| Jan 2025 | 31 / 31 | 0 |
| Feb 2025 | 27 / 28 | 1 |
| Mar 2025 | 28 / 31 | 3 |

The exact 11 absent dates, reproduced from the processed CSV, are 2024-08-12, 2024-09-06, 2024-09-20, 2024-10-26, 2024-11-17, 2024-11-30, 2024-12-16, 2025-02-19, 2025-03-05, 2025-03-10 and 2025-03-17.

**No replacement consumption is assigned to any missing day.** This pilot does not test missing-at-random assumptions or estimate a complete financial-year SLDC energy sum. The temporal pattern alone cannot establish a technical outage, source-publication reason or causal association with weather.

[Table A0-02](TABLE_A0_02_monthly_source_coverage.csv) provides a complete twelve-month machine-readable series including observed-day MU sums.

## 5. Additional prior source-level counterexamples (not newly verified in this pilot)

The *existing* 2019–2026 five-section audit records two substantive examples to include in future source-verification sampling:

1. **5 December 2019:** SLDC source reported generation = 15 MU, net imports = 57.3783 MU and consumption = 15 MU. Reported arithmetic contradiction = 57.3783 MU. The historic pipeline preserved all three source entries and **excluded** the day from its qualified response instead of silently replacing the source consumption by 72.3783 MU.
2. **13 March 2026:** original HTML reportedly showed Kundala reservoir storage = 397%; the existing project checked adjacent reports and preserved an original-source anomaly rather than changing the figure to a plausible value. This is an *asset/measurement-field* integrity example, not a valid observed operating storage level.

These will matter to A0 only after legitimate inspection of original files and clear field-level extraction provenance. They currently show evidence of already documented QA problems, **not independently reproduced source discoveries from this particular script**.

## 6. Scientific interpretation and novelty caution

The empirical result is a **constrained audit**: an exact observed-day operational sum, defined missingness, consistently applied arithmetic checks and a deliberately non-arithmetic boundary crosswalk. It directly prevents common but invalid statements, especially treating `30,666.2569 - 29,311.76` as a physical energy loss. No observed complete-day reconciliation between those figures is demonstrated.

This is not yet a novel methods paper. Research on Indian state electricity demand already addresses Kerala. Most relevant to the primary Paper A overlap, [Hunt & Bloomfield (2025)](https://doi.org/10.1088/2753-3751/adc7bc) use historical daily Grid-India reports, ERA5 and Kerala-specific modeling. The A0 claim is narrower: **original source version, metering definition, admissibility, missingness and independent replication** must show a nontrivial contribution beyond good documentation.

The 2026 IEEE Indian-state weather-demand proceedings work (DOI [10.1109/IC3ECSBHI67834.2026.11468867](https://doi.org/10.1109/IC3ECSBHI67834.2026.11468867)) is additional relevant prior art for broader daily-demand research. This pilot has **not** completed a systematic prior-art review of source-accounting methods, and should not state its method is unprecedented.

## 7. Falsifiable next experiment: independent original-byte extraction

To progress from reproducible processed-file arithmetic to an original research claim:

1. Pre-register a **stratified source-date sample**, sampling early and later Statistics layouts, known field anomalies, clean dates, source-missing dates and across financial years, with the RNG rule/selection frozen before comparison.
2. Independently obtain or inspect the **actual original source HTML bytes** within lawful access conditions. Verify original-source SHA256 and report dates; do not release restricted source rows.
3. Use a second, separately implemented extraction code path and compare each predeclared field to current `daily_system.csv`. Count exact agreement, unit/definition differences, missing vs absent fields, revision cases and adjudications.
4. Independently inspect original Economic Review pp.568–569 / Vol. II p.449 and confirm each annual figure and category wording. Record scan/page or publisher PDF SHA, revision date and extraction method.
5. Repeat over at least one more fiscal year and source publisher. A0 cannot claim generalizable revision-aware benefit based on 354 already processed rows in one FY.
6. Compare at least ten nearest original full-text methodological prior-art papers and ask whether the proposed ontology/QA rule actually improves on established solutions.

**Stop rule:** If those steps reveal only obvious, already published differences, downgrade A0 to an openly citable technical report rather than artificially presenting a new scientific-method result.

## 8. Reproduction instructions

From the repository root, with Python 3.11+ and no external packages:

```bash
python -m unittest discover -s tests -p 'test_paper_a0_pilot.py' -v
python scripts/run_paper_a0_pilot.py
```

The audit script writes the monthly coverage table, four forbidden comparisons and an input-SHA-linked JSON result under `studies/paper-a-2027/a0-pilot/reproduced/`. CI is configured to rerun the checks on the research PR and compare the deterministic generated CSVs against committed tables.

**This pilot makes no new claim about 2040 supply-demand adequacy, LOLE, hour-by-hour load, weather causality or Kerala's energy-policy cost.** The frozen 23 Oct 2026 project baseline and Paper A/A0 one-manuscript charter remain unchanged.
