# Kerala2040 — public evidence freeze, 23 October 2026

**Status:** source-audited descriptive research and retrospective daily-demand analysis. The public presentation is frozen to a narrower scope pending independent hourly operational evidence.

## Scope of the public research record

| Component | Classification | Public use |
| --- | --- | --- |
| Kerala State Planning Board annual electricity-consumption series | Published official historical statistic | Report with exact year, consumer-side scope and source |
| SLDC dated daily generation, consumption and interchange records | Original source reports and audited parsed daily rows | Report observed dates, metadata and same-boundary accounting; never equate to annual consumer-side consumption |
| Installed generation as at 31 March 2025 | Published official stock statistic, including source rounding discrepancy | Report total and technology mix with date, distinguish power capacity from generation |
| Observed SLDC daily demand paired with same-day ERA5 | Retrospective explanatory/statistical exercise on 353 matched observed daily targets | Report held-out error as within-year statistical performance; no operational forecasting or causal attribution |
| Hourly demand curve reconstructed from daily totals | Model-derived synthetic chronology | Retain code and source accounting audit for inspection; do not present simulated hourly peaks or shortages as observed |
| Future load/renewable/interstate/hydro/networks/storages scenarios | Assumption-dependent models and methodological stress tests | Archive for methods inspection; exclude from featured findings, quantified causal attribution, reliability estimates and investment recommendations |
| GIS solar/wind masks, cost estimates and planning pathways | Dataset-specific extrapolations or hypothetical feasibility thresholds | Keep in source registers; do not label as buildable MW or selected projects |

**No measured complete Kerala 15-minute/hourly demand-and-dispatch series has been admitted into the current public evidence package.** The SLDC FY2024–25 day collection contains 354 observed days and 11 missing days. This is a data-quality statement, not a real-time claim about electricity supply.

## Fixed data references

- Research data commit used by the public companion: `4e16836c7201637ee4a065abe259c9a47e004332`.
- Main primary sources: [Kerala State Planning Board Economic Review 2025](https://spb.kerala.gov.in/sites/default/files/2026-01/ER%202025%20Volume1%20Eng%20final.pdf) and [Kerala SLDC daily records](https://sldckerala.com/index.php?id=1).
- Source-accounting audit: `data/external/sldc_fy2024_25/qa_report.json`.
- Annual consumption evidence: `docs/CET_HISTORICAL_ELECTRICITY_STORY_2026_09_24.md` (the archival filename refers to the original analysis, not a current conference presentation).
- Daily weather experiment: `docs/DAILY_DEMAND_ML_ROBUSTNESS_V0_2.md` and `data/evidence/daily_demand_ml_robustness_v0_2_2026_10_06.json`.
- Source register and data definitions: `docs/evidence_register.md`.

### Important difference between annual and operational consumption series

The State Planning Board's **29,311.76 MU in FY2024–25** is a KSEBL-attributed *annual consumer-side consumption* figure, including open-access and captive consumption under its own source boundary. The SLDC archive reports **30,666.2569 MU of daily "consumption" across the 354 observed dates** under the SLDC operating/accounting boundary. These totals are **not the same quantity**. They must not be compared directly, summed together, subtracted to infer net imports, or treated as alternative estimates of one series. Eleven SLDC source days remain unavailable.

## What remains in the codebase

Previously implemented PyPSA, OSeMOSYS, hydropower, network, storage, GIS and 2030/2040 modelling is preserved for reproducibility and audit, **not erased or represented as physically validated**. They are explicitly classified as exploratory or sensitivity work in [EXPLORATORY_WORKSTREAMS.md](EXPLORATORY_WORKSTREAMS.md).

The two recently executed seven-day hydro timing exercises show properties of simplified models using deliberately hypothetical constraints; they have **no role in the core public evidence conclusions**.

## Conditions to revise the freeze

Do not add new featured scientific results simply because a simulation passes tests. An upgrade requires one or more of:
1. A previously missing primary observation with proven source, resolution, timezone, system boundary and permitted use.
2. A reproducible correction to the existing official-source extraction or arithmetic, independently checked and documented.
3. A genuinely independent observational validation of an existing inference, with holdout design and uncertainty.
4. Explicit review and replacement of a frozen finding whose source or definition has changed.

For interval-demand admission see `docs/MEASURED_INTERVAL_INTAKE.md` and [tracking issue #130](https://github.com/abhijith-sivaprasadan/kerala2040/issues/130). For hydro operations see [issue #131](https://github.com/abhijith-sivaprasadan/kerala2040/issues/131).

This document records the evidence and presentation boundary. Passing CI is a software and consistency check, not independent physical validation.
