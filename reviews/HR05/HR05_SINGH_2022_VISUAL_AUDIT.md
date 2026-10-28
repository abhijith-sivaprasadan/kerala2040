# HR05 — Singh, Lohani & Jain (2022): 31-page visual and scientific audit

**Verified source:** Vishal Singh, Anil Kumar Lohani and Sanjay Kumar Jain, *Reconstruction of extreme flood events by performing integrated real-time and probabilistic flood modeling in the Periyar river basin, Southern India*, **Natural Hazards** 112:2433–2463 (2022), [DOI 10.1007/s11069-022-05272-4](https://doi.org/10.1007/s11069-022-05272-4).

**Review completed:** 28 October 2026. Published PDF: **31 pages**. Uploaded source SHA-256: `889b0ea4c805a03735541c0674e18d1b001cb6c5bf5aa300cf5eef3c21e131dd`. All 31 pages individually rendered at 165 DPI and viewed in **16 readable paired/individual sheets**; technical pages 11, 20, 22 and 23 additionally reopened at full page. All Figures **1–13**, Tables **1–5**, main equations and bibliography examined. **30 documented scientific findings**, **39 evidence/numerical checks** (including each of 23 rows in Table 5, 69 reported MSE–RMSE relationships) and **12 Kerala2040 actions**.

**Scientific boundary:** This is a source-internal visual/critical review. It is **not** an independent rerun of the original HEC-HMS, HEC-ResSim, HEC-RAS, precipitation, reservoir, gauged river or satellite flood-inundation data. Online supplementary ST/SF model files were referenced but **not included** in the provided PDF. Full locally generated visual audit PDF, source-page images and CSV packages are **not part of this Git commit**; public Git holds only the source-critical derivative record. The original source publication is copyright protected.

## Executive judgment

This study is a **high-priority direct hydrological and flood-inundation comparator** for Kerala2040, more complete geographically than HR04 Ryan’s Kakki-only counterfactual and different from HR07 Suresh’s satellite reconstruction. It analyses seven historical Kerala/Periyar flood events, a 2002–2018 unregulated streamflow series, reservoir operations for Mullaperiyar–Idukki and 1D downstream inundation maps. Reported fits at Neeleswaram are **R² = 0.8022** for 2018 Figure 6b and **R² = 0.6755** for monthly 2007–2010 continuous modelling Figure 6c.

The largest scientific concerns are **hindsight-dependent rule specification, model-calibration/validation non-independence, long flood-frequency extrapolation with severe model-choice spread, lack of spatial flood-map overlap scores and absence of any hydropower MW/MWh modelling**. The paper does not establish operational forecast accuracy or Kerala’s physically deliverable generation flexibility.

## Source-specific numerical evidence

| Original PDF page | Reported result | Audit interpretation |
| --- | --- | --- |
| 1, 20 | HE_7 flood R² **0.80** (Fig. 6b label **0.8022**) | Internal precision consistent; gauge was also calibration target |
| 1, 20 | Continuous R² **0.67** in abstract, Fig. 6c **0.6755** | Rounds to 0.68; minor presentation precision discrepancy |
| 17 | Modelled peak **~9,800 m³/s** vs CWC **~9,000 m³/s** | About **+8.9%** relative to CWC (source’s approximate maxima) |
| 13, 22–23 | Annual maxima years 2002–2018, return periods to **200/500 years** | 17 maxima for tails 11.76x/29.41x sample duration, with material extrapolation uncertainty |
| 23, Fig. 8 | RP200 maximum ~**6,000 m³/s (Gumbel)** vs ~**22,000 m³/s (Log Pearson III)** | **3.67x** author-quoted difference, not a directly matched location/independent observation |
| 22, Table 5 | 23 named grid rows with MSE and RMSE for Lognormal, Gumbel and Log Pearson III | All **69 reported RMSE ≈ sqrt(MSE)** within rounding. LP3 lowest error in **23/23 rows**. This is internal table consistency, **not** validation of high-return-period floods |
| 11, Table 3 | Mullaperiyar flood-control max **50 m³/s** on Aug 6; storage-zone min **100 m³/s** same date | Conditional: min exceeds max numerically, **but zones differ**. Actual HEC-ResSim rule priority must be inspected |
| 20, Fig. 6d | “Water Yield (mm)” y-axis to **250,000 mm** | Implausible as a *daily basin depth* as presented; missing aggregation/unit conversion cannot be resolved from this PDF |
| 25, Fig. 9 | Hydraulic elevations around **−110 to +20 m** | Vertical datum/georeferencing not documented sufficiently for physical reuse |
| 26, Fig. 11 | Maps compared against Sentinel-1 and Dartmouth | Visual agreement only; no map-overlap / depth-error statistics |
| 26–27, Fig. 12 | Dated maps for Aug 8–25, 2018 | Some narrative descriptions differ from panel-date labels; consult visual panels directly |

## Complete 30-finding register (short form)

| ID | Priority | PDF page(s) | Finding / required handling |
| --- | --- | --- | --- |
| F01 | High | 5–6,10,15–17 | Retrospective 2018 rainfall and gauge flows used to tune rules; not tested as a forecast at genuinely available issue times |
| F02 | High | 5,12–13,20 | Neeleswaram used for calibration and presented for accuracy; no separately established independent holdout |
| F03 | High | 13,22–23 | Just 17 annual maxima used for 200/500-year flood return periods |
| F04 | High | 23 | Large RP200 Gumbel vs LP3 extreme difference (~6000 vs 22000 m³/s) |
| F05 | High | 25 | Similarity of 2018 unsteady stage to 200-year Gumbel stage does not independently establish a 200-year event |
| F06 | Medium | 11 | Table 3 FCZ max sometimes below SZ min; these belong to **different zones**, inspect rule logic |
| F07 | High | 10–12,15–19 | Complete storage trajectories, operating-priority constraints and original reservoir model unavailable |
| F08 | High | 9–12,15–18,29 | No turbine-head, energy generation MWh or dispatchable MW model |
| F09 | Medium | 5–8,28 | 3-hourly 2018 vs daily historical forcings confound apparent differences |
| F10 | Medium | 6 | Bias correction redistributes daily data to 3-hourly rainfall; weights and vintage not archived here |
| F11 | Medium | 5,22 | 14 TRMM/GPM + 16 IMDAA grid counts versus 23 Grid IDs in Table 5 require crosswalk |
| F12 | High | 20–21 | Figure 6d water-yield scale to 250,000 mm requires unit/aggregation verification |
| F13 | Low | 19 | Figure 5 caption repeats Mullaperiyar where text identifies Idukki in later plot group |
| F14 | Medium | 24–25 | Unexplained negative elevation reference in hydraulic profile |
| F15 | Low | 25 | Figure 6d mis-cited where Figure **9d** is intended |
| F16 | High | 26 | Flood-map “validation” lacks spatial overlap scores and aligned mask documentation |
| F17 | Medium | 27 | Figure 12 exact panel dates differ from some dates in narrative |
| F18 | Medium | 22 | Log Pearson lowest table fit errors in all rows, yet both Gumbel and LP3 carried forward with limited selection justification |
| F19 | Medium | 22 | Square-root consistency of MSE/RMSE does not establish robust fit/out-of-sample skill |
| F20 | Medium | 7–8,13 | Seven selected events cannot establish hydrology over all climate regimes |
| F21 | Medium | 5,17–18 | 56 subbasins and 12.5m DEM use need vertical accuracy/hydro-conditioning checks |
| F22 | High | 11–12 | Only eight surveyed cross-sections for extensive 1D flood geometry |
| F23 | Medium | 12 | Unmeasured downstream normal-depth slope 0.001; test lower boundary effects |
| F24 | High | 17–18 | Muskingum routing x=0.5 corresponds to no attenuation in source explanation |
| F25 | Low | 18 | Description repeats x=0 for both storage and pure transmission; suspect x=0.5 typo |
| F26 | Medium | 17 | Modelled ~9800 vs ~9000 observed peak is ~8.9% higher |
| F27 | High | 26–28 | Colored inundation maps cannot substitute for quantitative flood-depth and geospatial validation |
| F28 | Medium | 23 | Method-of-moments tail fits not sensitivity-tested versus L-moments/ML |
| F29 | Medium | 25 | Comparison of unsteady 2018 and steady RP200 water stage conflates distinct design assumptions |
| F30 | High | 28–29 | Full supplementary ST/SF input files and runnable HEC configuration are required for reproduction |

## Visual inspection index for all 31 PDF pages

| PDF page | Visually inspected content |
| --- | --- |
| 1–3 | Abstract, study introduction, historical-event and virgin-flow framing |
| 4 | Figure 1 basin DEM/TIN, soils, land use and CN maps |
| 5–6 | Observational sources, rainfall bias correction, construction of HEC-RTS workflow |
| 7 | Figure 2 integration diagram, Table 1 seven events and continuous virgin series |
| 8–10 | HEC-HMS loss, Muskingum routing, Table 2 parameter bounds and retrospective limits |
| 11–12 | Tables 3–4 exact reservoir zone/release schedules, eight surveyed river cross-sections and HEC-RAS boundary condition |
| 13–14 | Extreme-value sample and Eqs. 1–5 for Gumbel / Log Pearson III |
| 15–16 | 2018 retrospective rule setting and Figure 3 three-panel flow reconstruction |
| 17–18 | Flow totals and routing sensitivity, Figure 4 inflow/outflow/storage graphs |
| 19–20 | Figure 5 all HE1–6 flow/storage subplots, Figure 6 observed-vs-modelled validation and water yield |
| 21–23 | Figure 7 event comparisons, all Table 5 fit rows and Figure 8 return-period boxplots |
| 24–25 | Figure 9 hydraulic cross-section geometry, negative elevation axes; Figure 10 RP200 map comparisons |
| 26–28 | Figure 11 Sentinel/Dartmouth visual map comparison, Figure 12 dated maps and Figure 13 four-event maps |
| 29–31 | Conclusions, supplementary material notice and full references |

## Cross-review implications for Kerala2040

| Study | Scope | Scientific gap left open |
| --- | --- | --- |
| **HR04 Ryan (2020)** | Kakki release-rule counterfactuals | Unverified physical storage trajectories and energy effects |
| **HR07 Suresh (2024)** | RAT 3.0 satellite reservoir timing/state reconstruction | Peak inflow bias; no observed gate/turbine split |
| **HR05 Singh (2022)** | Periyar hydrologic + reservoir + 1D inundation modelling | Hindsight rules; long-tail and flood-map uncertainties; no hydro MW/MWh |

**Highest-value research hypothesis:** reconcile actual KSEB/CWC reservoir storage, inflows, turbine and spill releases with historical forecast vintages and safety constraints, then estimate feasible head-dependent electricity flexibility and interactions with Kerala transmission/import constraints. That hypothesis is **not established as new research** until a further closest-comparator search is completed.

### Prioritized acceptance actions

1. P0 — Acquire official ST/SF supplement and versioned HEC-DSS, HEC-HMS, HEC-ResSim and HEC-RAS cases.
2. P0 — Independent Neeleswaram validation using truly held-out observations or gauges.
3. P0 — Time-stamped archived rainfall forecast vintages instead of post-event corrected meteorology.
4. P0 — KSEB/CWC in-situ time series for storage, inflow, and separated spillway/turbine releases.
5. P0 — Resolve reservoir maximum/minimum rule priorities and physical storage constraints.
6. P1 — Repeat flood frequency analysis with explicit uncertainty bands and multiple fitting methods.
7. P1 — Reconcile Fig. 6d water-yield units and Fig. 9 vertical datum.
8. P1 — Quantitative geospatial inundation validation and matched dates.
9. P1 — Hydraulic cross-section/downstream and Muskingum parameter sensitivity.
10. P1 — Match HR04/HR05/HR07 observations on common locations and times.
11. P2 — Couple reservoir operation to head-dependent hydroelectric energy, non-energy water needs and flood safety.
12. P2 — Test interaction with actual constrained, sourced Kerala electricity transfer and generation observations.

**Data rights:** Do not upload source-page image ZIPs or full Springer PDF as open-source repo assets without checking permissions. The original journal PDF states exclusive Springer licensing. This Markdown is a derived critique, not a third-party paper copy.

[Round 2 register](papers.csv) · [HR04 Ryan](HR04_RYAN_2020_VISUAL_AUDIT.md) · [HR07 Suresh](HR07_SURESH_2024_VISUAL_AUDIT.md)
