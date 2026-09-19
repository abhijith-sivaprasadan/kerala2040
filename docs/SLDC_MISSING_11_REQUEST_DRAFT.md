# Draft — request for 11 missing FY2024–25 Kerala SLDC daily reports

**Status: NOT SENT.** Replace sender and affiliation details; do not imply an institutional endorsement. This supplements the separate [interval-demand request](SLDC_DATA_REQUEST_DRAFT.md). The missing daily reports and the full measured 15-minute chronology are distinct data needs.

To: ceso@kseb.in — Chief Engineer, Transmission–System Operation  
Cc: dcegrid.sldc@kseb.in — Deputy Chief Engineer, Grid  
Subject: Request for missing historical Kerala SLDC daily reports — 11 FY2024–25 dates

Dear Chief Engineer,

I am [name and genuine affiliation, if any], conducting an independent research project on Kerala's electricity system for Kerala 2040. We have preserved the publicly available dated Kerala SLDC system-statistics reports for 354 of the 365 days of FY2024–25. Our retained raw archive has SHA-256 `5c1bb8cbe67a9b3a9149080250b4bfcfbf2d30592f3f5afdb6248e2b25623101`, with per-report date and content hashes.

We have not been able to obtain the complete dated daily reports for these eleven dates:

| 2024 | 2025 |
|---|---|
| 12 August | 19 February |
| 6 September | 5 March |
| 20 September | 10 March |
| 26 October | 17 March |
| 17 November | |
| 30 November | |
| 16 December | |

A targeted recheck of the public historical date form on 19 September 2026 returned no verifiable dated statistics for these eleven dates. As a control, the same route successfully returned **13 August 2024**, and its energy-accounting values matched our previously archived observations. We do not infer that the missing official records do not exist: only that we could not recover them through those public form requests.

Could your office provide an electronic copy of the missing days' reports, or refer us to their custodian? We are looking for the five original public sections per date: **Generation, Imports, Storage, Availability / Merit Order, and Others / demand extrema**. Existing HTML/PDF, CSV or Excel copies would all be useful; the original as-issued versions, any revised versions and the correction/revision dates should be distinguished if available.

For scientific reconciliation, please identify the date/time convention and units of reported consumption, internal generation, net imports and hydro output. Our comparison uses the reported daily identity **internal generation + net imports = consumption**, with account boundaries kept as published. We will not replace missing observations with synthetic or interpolated values. Please also specify attribution, research use and republication conditions; an internal-use copy that we cannot republish is still useful for independent reconciliation subject to your terms.

The open research methodology and published missing-day limitation are available at https://github.com/abhijith-sivaprasadan/kerala2040 and https://kerala2040.github.io/#audit. We can provide the per-date retrieval report and hashes on request. Please let us know whether a formal application, institutional letter or data-use agreement is needed.

Regards,  
[Name]  
[Affiliation if applicable]  
[Email / contact details]  
[Actual send date]

## Retrieval evidence and editorial limits

- [Live retry workflow run 35469025134](https://github.com/abhijith-sivaprasadan/kerala2040/actions/runs/35469025134): all 11 targeted generation-date lookups unverified; 2024-08-13 known-observed control confirmed by independent comparison to `daily_balance.csv`. The workflow artifact is a **retrieval-attempt report, NOT observed data**.
- The original FY2024–25 QA report remains **354/365 observed**. Neither the returned HTTP 200 pages without dated statistics nor a matching control day closes the historical coverage gap.
- A verified future delivery must be reconciled by date, five-section coverage and raw-response provenance before revising the processed CSVs, station summaries, QA counts or website.
- Do not conflate this request with the separate FY2024–25 full hourly/15-minute demand and interchange acquisition.
