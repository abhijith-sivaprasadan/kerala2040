# HR07 — Suresh et al. (2024): Published 24-page edition verification

**Reviewed on 28 October 2026.** This is an additional source-*version* audit of HR07, **not a new paper** and not a third completed Round 2 entry.

## Bibliographic and integrity record

- **Source:** Sarath Suresh et al., *Satellite-based tracking of reservoir operations for flood management during the 2018 extreme weather event in Kerala, India*, *Remote Sensing of Environment* **307** (2024), article **114149**.
- **DOI:** https://doi.org/10.1016/j.rse.2024.114149
- **Published edition:** 24 PDF pages, incorporating Appendix A, screenshots and references. Article dated online **11 April 2024**; accepted **3 April 2024**.
- **Uploaded published PDF SHA-256:** `5c30bd5c70c6818d1542a16edbc2434f94d36fb26a8b10937f842f5de3045836`.
- **Earlier HR07 version:** 56-page accepted manuscript, DOI identical. [Earlier full-source audit](HR07_SURESH_2024_VISUAL_AUDIT.md).
- **Visual method:** Every one of the 24 published PDF pages rendered independently at **175 DPI**; visually inspected in twelve readable paired-page sheets, including Figures 1–21, Tables 1–5, Table A.1, Appendix Figures A.1–A.5 and full bibliography.
- **Outputs completed:** 24 page-specific observations, crosswalk for **30 previously identified findings**, **38 evidence/numerical checks** (including 19 evaporation-table rows), and **12 research actions**.
- **Limits:** No independent rerun of VIC, RAT, ResORR, satellite classification or observed KSEB/CWC series. Claims of code-level errors are not warranted without execution.

## Published-version scientific interpretation

The published manuscript **retains the main reported conclusions and important scientific qualifications** of the reviewed accepted manuscript. Satellite-assisted RAT 3.0 is informative about *qualitative reservoir-state trends and approximate inflow/outflow event timing* across 19 selected Kerala reservoirs; it does **not independently establish** accurate 2018 extreme-flow magnitudes, physical gate opening, electricity turbine flow, MW, MWh or a flood-safe firm capacity product.

| Published PDF page(s) | Key result or issue | Scientific treatment |
| --- | --- | --- |
| **7, 14, 16** | Figure 6 and Figure 18 show large event inflow/outflow underprediction for some basins; authors describe Kakki/Idamalayaar peaks as 2–4 times below observations | Use for timing/trend methods with bias warnings; do not cite uncalibrated releases as known m³/s |
| **8** | Idukki regulated-inflow Table 5: RMSE **170.30 → 153.17 m³/s**, MAE **115.10 → 102.32 m³/s**, r **0.80 → 0.84** | Source-internal improvements **10.06%** RMSE and **11.10%** MAE; not independent field reproduction |
| **10, 22** | Aggressive BOT filtering r **0.92 → 0.94**, normalized RMSE **22.6% → 26.3%** | Better correlation can coincide with worse error and narrower apparent uncertainty |
| **11, 15** | 9/19 reservoirs by 25 July, 14/19 by 1 August, 16/19 by 8 August above **90% of nominal maximum surface area** | **Area fraction is not storage fraction**; reservoir-by-day source measurements not independently reprocessed |
| **10, 19** | Printed outflow formula **O = I - E - ΔS**; Appendix defines ΔS as volume | Rate/volume dimensions require **ΔS/Δt** or an explicit rate definition; original software not inspected |
| **13** | Narrative refers to **17 August 2023** in the 2018 flood investigation | Confirmed text error persists in published edition |
| **4** | Fig. 3 caption sends readers to **Table 4** for reservoir identity/location | Actual 19-row list is **Table 1**; definite cross-reference error |
| **20, 22** | Pekel water-occurrence threshold **greater than 15%** in text, but **greater than 10%** in Figure A.3 | Actual processing threshold unresolved until configuration/source inspection |
| **20–21** | Appendix surface-area methodology refers to **Fig. 6** as workflow | Appendix workflow appears as **Fig. A.1** |
| **13, 17** | Report associates normalized release heatmaps with 'all 19 dams opened fully' | Inferred total release does not identify spill gates, turbine release or gate-open status; no independent gate logs |
| **20** | Appendix Table A.1 provides 19 mean and peak evaporation estimates | Rate checks consistent with table rounding using **area[km²] × depth[mm/day] / 86.4 = m³/s** |
| **18–19** | Authors provide code portal and India-WRIS data links | Exact run commit/parameters/model input vintages not specified in the article |

The statement that all 19 dams opened fully is methodologically stronger than the displayed evidence: normalized inferred outflow is not a measurement of gates or spillway position. Also, a server update every day is not the same as a fresh independent satellite water-area observation every day (estimated 1–5 day imagery cadence).

## Source-version and article-count integrity

The earlier **56-page** accepted manuscript and this **24-page** journal PDF are the **same** study. The HR07 bibliographic register must contain one article and two source-version records. This review does not change Round 2 from **2 of 40 papers fully audited**: Ryan (HR04) and Suresh (HR07).

The available chat-generated audit bundle includes a **16-page scientific PDF**, full page ledger, finding crosswalk, numerical-check CSV, evaporation 19-row CSV, action register, checksum manifest, and private page-image ZIP. **Only the derived research records in this repository are public GitHub artifacts; the binary PDF and copyrighted page renders were not committed.** The user can retrieve them from the original conversation attachments.

## Published-page crosswalk (previous 30 findings)

| Finding | Published page(s) | Finding | Published page(s) |
| --- | --- | --- | --- |
| F01 | 10,19 | F16 | 4,20 |
| F02 | 7,12,14,16 | F17 | 5,8 |
| F03 | 11,15 | F18 | 20,22 |
| F04 | 13,17 | F19 | 20,22 |
| F05 | 13 | F20 | 6,7 |
| F06 | 4 | F21 | 11,15 |
| F07 | 19 | F22 | 5 |
| F08 | 14,18 | F23 | 12,17 |
| F09 | 10,22 | F24 | 18,19 |
| F10 | 8,9 | F25 | 11,15 |
| F11 | 14,15 | F26 | 20,21 |
| F12 | 17,18 | F27 | 16,19,20 |
| F13 | 7,8 | F28 | 8,18 |
| F14 | 10,12,19 | F29 | 7 |
| F15 | 11,20 | F30 | 17,18,19 |

## Next research gates

Preserve precise source-version provenance; verify RAT code units and thresholds; obtain in-situ KSEB/CWC stages/inflows/outflows and gate/turbine operation; validate 2018 peak bias against measured high-flow periods; reconcile SRTM surface-area/bathymetry with storage volume; then and only then model head-dependent hydroelectric production and integration with Kerala import capability.

See [the previously reviewed 56-page edition](HR07_SURESH_2024_VISUAL_AUDIT.md) and [Round 2 screening register](papers.csv).

**Copyright boundary:** Elsevier's published PDF notes all rights reserved. Do not commit or redistribute original full-page images and figure excerpts in the public repo without appropriate permission or a defined reuse basis.
