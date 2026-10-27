# HR07 — Suresh et al. (2024): complete 56-page visual/scientific audit

**Source:** Sarath Suresh et al., *Satellite-based Tracking of Reservoir Operations for Flood Management during the 2018 Extreme Weather Event in Kerala, India*, Remote Sensing of Environment (2024). DOI: [10.1016/j.rse.2024.114149](https://doi.org/10.1016/j.rse.2024.114149).

**Uploaded version:** accepted manuscript of **56 PDF pages**, including appendices A.1–A.9. **SHA-256:** `d0563a32c641a4284666ffb7eed801eb2b0121395bd9338b7456d092f6bc07f9`. **Reviewed:** 27 October 2026.

**Inspection protocol:** all 56 pages individually rendered at 170 DPI, and all pages individually examined within 28 readable two-page inspection sheets; inspected main figures 1–21, Tables 1–5, appendix math/evaporation table and Figures A.1–A.9. Scientific findings: **30**; numerical/internal checks: **30**; actions: **12**. The full 12-page scientific report, two ZIP evidence packages, individual page ledger, findings/arithmetical CSVs and 19-row evaporation cross-check exist as separately generated conversation artifacts. **They are not present in this Git commit.** Source PDF/reproduced page images are third-party materials and not included in public git history. The underlying VIC, RAT, ResORR, IMERG and KSEB experiments have **not** been independently rerun.

## Why this matters

RAT 3.0 combines VIC 5.0 meteorology-driven reservoir inflow, Sentinel-1/2 and Landsat-8 satellite-derived water area, SRTM area-elevation relationships, evaporation, and mass balance inferred outflow. It studies **19 reservoirs** during the 2018 Kerala floods, with selected in-situ validation data for Banasurasagar, Idamalayaar, Idukki and Kakki. It provides useful **timing/trend** reconstruction; it **does not directly observe gate opening or separate spillway/turbine discharge**, and flood peaks are materially underestimated.

## Quantitative results checked

| Original PDF source | Published values | Independent check / interpretation |
| --- | --- | --- |
| p18 Table 4 | Inflow RMSE: Banasurasagar 31.81, Kakki 83.54, Idamalayaar 135.29, Idukki 217.94 m3/s | Reproduced as written; no raw-hydrograph recomputation |
| pp20–21 Table 5 (Idukki May–Oct 2018) | With upstream ResORR: RMSE 170.30 → 153.17 m3/s, MAE 115.10 → 102.32 m3/s | **10.06% RMSE** and **11.10% MAE** reduction; correlation 0.80→0.84, KGE 0.59→0.63, NSE 0.603→0.680 |
| pp23,52–53 Fig 10 and appendix | Correlation 0.92→0.94 with aggressive filters, normalized RMSE 22.6%→26.3% | Higher correlation but **3.7 percentage-point worse NRMSE**; smooth filtering reduces useful uncertainty |
| pp27–28 | 9/19, 14/19, 16/19 reservoirs with >90% maximum water **surface area** on July 25, Aug 1, Aug 8 | 47.37%, 73.68%, 84.21%; **not** the percent of reservoir storage volume |
| pp47–48 Table A.1 | Idukki area 50.13 km2, 4.59 mm/day, evap 2.66 m3/s | Recalculation 50.13×4.59/86.4 = 2.663 m3/s, matches rounding |
| pp47–48 Table A.1 | Kakki area 19.25 km2, 4.85 mm/day, evap 1.08 m3/s | Recalculation 1.081 m3/s, matches rounding |
| p12 | Dam ownership 33 KSEB + 20 irrigation + 2 water authority + 4 TN PWD + 2 others | Total 61, checks out |

## High-priority scientific findings and source corrections

| ID | PDF page(s) | Finding and consequence |
| --- | --- | --- |
| F01 | 26, 46 | **Printed water-balance dimensions:** O=I-E-ΔS subtracts reported storage **volume** (Appendix p46) from flow **rates** (m3/s), unless ΔS is converted to ΔS/Δt. Verify time conversion in RAT code before alleging an implementation bug. |
| F02 | 18, 29–34 | **Peak bias:** RAT modeled inflow peaks for Kakki/Idamalayaar can be **2–4 times below observed**, making some inferred release peaks disappear. Trend monitoring does not validate quantitative flood magnitudes. |
| F03 | 27–28 | Above-90%-of-maximum *area* does not equal above-90%-of-full storage volume. |
| F04 | 31–32 | “All 19 dams opened fully” is **not identified by an inferred outflow heatmap**; water release could flow through spillways, turbines, other diversions. Gate-state logs required. |
| F05 | 31 | **Definite year typo:** the paper gives peak around 17 August **2023** despite studying July–August **2018**. |
| F06 | 10 | Figure 3 caption says reservoir details are in Table 4, but the dam list is Table **1**. |
| F07 | 45 | VIC manually calibrated to Idamalayaar; independence of its reported validation needs clarification. |
| F08 | 35–36 | ~0.0625° VIC (~7 km) has known routing/terrain issues for small catchments near basin boundaries. |
| F09 | 22–23, 52–55 | Aggressive SAR-based filter introduces smoothing bias and artificially narrow uncertainty; r improves even when NRMSE worsens. |
| F10 | 19–21 | ResORR modestly improves Idukki comparison; it is not a jointly optimized hydro-flood-electricity operation model. |
| F11 | 35–36 | Uncertainty bands emphasize water area, while precipitation and routing bias, seepage, irrigation diversion and bed topography uncertainties also affect flows. |
| F12 | 38–40 | A daily-updated web product with 1–5-day satellite surface-area observations is not equivalent to a new actual observation daily. |
| F13 | 18, 20–21 | Idukki inflow correlations from Table 4 and Table 5 use different time windows (June–August vs May–October), so their difference alone does not prove a contradictory result. |
| F14 | 23–25, 46 | SRTM captured exposed DEM in 2000, not full bathymetry; correlation in area-elevation does not automatically validate absolute volume. |
| F15 | 27, 47–48 | Evaporation was found small in the flood period, but cannot be omitted without checking dry-season/multi-year water accounting. |
| F16 | 11, 47–48 | Main reservoir inventory areas and appendix mean surface areas differ; neither should be assumed a universal constant. |
| F17 | 14–15 | Generic meteorological provenance wording points to NOAA/NCEP while Table 3 correctly identifies NASA GPM IMERG for precipitation. |
| F18 | 48–50 | Historical water occurrence is substituted for cloudy image regions; interpolation can substitute climatological footprint during extremes. |
| F19 | 49, 52 | **Threshold mismatch:** methods give Pekel occurrence threshold >15%; Fig A.3 panel visibly labels >10%. Check config before replication. |
| F20 | 17–18 | IMERG/IMD rainfall differences and VIC underpredicted peaks require high-quantile precipitation bias diagnostics, not just trend similarity. |
| F21 | 28–29 | Labeling the area decline as intentionally operated “flood cushioning” requires operator decisions, not only water-area curves. |
| F22 | 9, 13 | Hydro dams supplying “>80% of Kerala's energy needs” lacks defined denominator/period; distinguish historical hydropower or Periyar share from total supplied electricity. |
| F23 | 31–32 | Per-reservoir 0–1 heatmaps are suitable for peak timing, not absolute flow volume or electricity value comparisons. |
| F24 | 40–41 | Public RAT code and India-WRIS pointers do not pin the exact code version, calibration parameters, KSEB input series and datasets used in this manuscript. |
| F25 | 27–28 | The 9→14→16 reported counts require per-date source-level re-computation before reuse as validated raw measurements. |
| F26 | 48, 51 | Appendix's surface-processing workflow points to Figure 6 even though the appendix figure is A.1. |
| F27 | 29–30, 45, 48 | Stated spin-up and run periods (2015–17/2017–18) do not fully explain the 2016–2020 comparison and 2017–19 plot ranges. |
| F28 | 38–40 | IMERG Final and retrospectively processed inputs are not ahead-of-time forecast vintages; actual forecast skill remains untested here. |
| F29 | 18, 20 | Table 4 NRMSE denominator not explicitly specified; avoid unsupported cross-study comparisons. |
| F30 | 33–40 | No Kerala reservoir electricity-head/MW/MWh dispatch, turbine releases, firm capacity, or grid reliability evidence is produced. |

## Required new Kerala2040 research evidence

**P0:** precise water balance with storage unit/time step; ground-truth KSEB/CWC storage/inflow/outflow; station provenance; distinguish recorded and inferred data; flood operating rules and turbine/spillway separation.

**P1:** bias-corrected precipitation/inflows and holdout periods; area-elevation and reservoir storage calibration; surface-area filtering robustness; upstream regulation (Mullaperiyar–Idukki); forecast vintage/latency data.

**P2:** physics-constrained hydro-to-electricity conversion with head, efficiency, MW and MWh; hydro scheduling with demand and interstate capacity; only then reliable system flexibility/adequacy claims.

## Source inspection boundaries

- **Visual review completed:** all 56 original page positions rendered individually and viewed in paired inspection sheets.
- **Quantitative source-internal checks:** 30 calculations/consistency tests, including Table 5 improvements and evaporation unit conversion.
- **Not independently reproduced:** third-party original study models, in-situ data, daily weather data, satellite image classification, flood inundation or operational forecast experiments.
- **Permissions:** PDF/page-image redistribution to any public repository must be confirmed separately.

Related: [Round 2 index](README.md), [full-text acquisition register](FULL_TEXT_ACQUISITION_2026-10-27.md), [Paper 20 CEA transmission review](../CEA_TRANSMISSION_2034-35_PAPER20_AUDIT_2026-10-27.md).
