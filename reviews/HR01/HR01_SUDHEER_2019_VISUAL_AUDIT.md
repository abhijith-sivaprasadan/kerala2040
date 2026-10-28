# HR01 — Sudheer et al. (2019): 15-page individual visual/scientific audit

**Source:** K. P. Sudheer, S. Murty Bhallamudi, Balaji Narasimhan, Jobin Thomas, V. M. Bindhu, Vamsikrishna Vema and Cicily Kurian. *Role of dams on the floods of August 2018 in Periyar River Basin, Kerala*. **Current Science** 116(5), 780–794, 10 March 2019. DOI: https://doi.org/10.18520/cs/v116/i5/780-794.

**Full source reviewed 28 October 2026:** 15 original PDF pages; 175-DPI individual page renders, eight readable inspection sheets; technical hydrologic figures reopened individually; 12 figures, two tables, four numbered mathematical expressions, full references examined. Source PDF SHA-256: `8ad1fc11d238b076f4ba2c5258b8692f4ef4ef2ced39083766cc1931bee18777`.

**Deliverables generated:** separate 9-page source-critical PDF audit, 15 page records, **32 scientific findings**, **44 source-internal numerical/evidence checks**, **12 implementation actions**, and separate private page-image archive. **Public GitHub contains the derived Markdown and all four CSV evidence registers, not the third-party PDF or its copyrighted page images.** The original HEC-HMS, data and historical forecast series were **not independently reproduced**.

## Core results and qualified interpretation

| Source location | Reported quantity | Reconciliation |
| --- | --- | --- |
| PDF pp6–7 | Virgin simulated peaks L1 **8,224 m³/s**, L2 **11,990 m³/s** | No-reservoir *counterfactual*, not real observed flood |
| PDF pp8–9 | Baseline modeled Idukki inflow **2,763** vs measured **2,532 m³/s** | **+9.12%** vs observed; consistent with less-than-10% statement for **inflow** |
| PDF pp8–9 | Idukki release modeled **1,860** vs measured **1,614 m³/s** | **+15.24%** vs observed; **not consistent** with grouped <10% peak comparison |
| PDF pp8–9 | L2 Neeleswaram modeled **9,965** vs observed **8,800 m³/s** | **+13.24%** relative observed, **11.69%** relative modeled (source states ~12%) |
| PDF pp10–11 | Storage 75% at end July: L2 **8,340** vs baseline **9,965 m³/s** | **16.31%** modeled peak reduction |
| PDF pp10–11 | Storage 50% or 25% at end July: L2 **7,868** or **7,844 m³/s** | **21.04%** and **21.28%** modeled reduction; very small gain from 50% to 25% |
| PDF p13 | Neeleswaram bankfull approximately **4,200 m³/s** | Best shown **7,844 m³/s** remains **1.87×** threshold; reducing peak is not the same as avoiding inundation |
| PDF pp11–12 | Virgin to baseline regulation L1 ~33%, L2 ~17% peak attenuation | Different **no-dam** counterfactual from pre-emptying versus 85% baseline |

**Major scientific qualifications:** Basin-scale model was calibrated against Neeleswaram flow used in its retrospective fit; 2018 weather was known to the analyst; ratio-adjusted satellite rainfall is weakly constrained in mountainous extremes; assumed percent storage does not constitute a feasible pre-release trajectory; alternative operations have no measured MW/MWh opportunity-cost model; flood-damage reductions are not calculated; return periods are model-dependent and carry uncertainty.

**Review of perceived disagreement with later papers:** This paper's conclusion concerns the limited ability of certain modelled storage scenarios to keep **downstream Neeleswaram discharge below bankfull** under 2018 conditions. HR04 Ryan evaluates **a single Kakki reservoir outlet**; HR05 Singh models Periyar inundation; HR07 Suresh reconstructs satellite reservoir states; HR08 Das tests **forecast-informed hypothetical scenarios** with mostly satellite-nowcast evaluation. Their percentages have different locations, targets, assumptions and validation. Sudheer expressly recommends **improving weather forecasts, inflow forecasts and integrated reservoir rules**, not that information or advance warning could never reduce impacts.

## Scientific finding register (32 source-specific entries)

| ID | Priority | PDF pages | Finding |
| --- | --- | --- | --- |
| F01 | Critical | 8-9 | Idukki peak release bias; Simulated 1860 vs measured 1614 m3/s = +15.24%, despite a grouped <10% peak-error statement |
| F02 | High | 8-9 | L2 peak overprediction denominator; 9965 vs 8800 m3/s is +13.24% relative observed; +11.69% relative model; source says 12% |
| F03 | High | 11-14 | Attenuation does not eliminate overbank flow; Best end-July L2 ~7844 vs approximate bankfull 4200 m3/s |
| F04 | High | 7-11 | Storage drawdown is imposed counterfactual; Storage percentages are set for end-June/July without verified pre-release sequences |
| F05 | High | 8-9 | Calibration and evaluation independence; Neeleswaram flow used to fine tune model and later compare model fit |
| F06 | High | 5-8 | Rainfall bias adjustment limitation; 0.1-degree IMERG ratio corrected with limited gauges |
| F07 | High | 6-8 | Incomplete HEC model reproducibility; No complete HEC configurations, subbasin parameter sets, exact grids |
| F08 | High | 7-12 | No hydroelectric production cost quantified; No turbine head, generation, plant dispatch or dry-season MWh |
| F09 | High | 9 | Individual tributary peaks not necessarily synchronous; 3500, 2828, 2037 and 1860 m3/s at different branches |
| F10 | Medium | 9 | Reduction-to-2500 wording ambiguous; Paper mentions reducing peaks to ~2500 m3/s while L2 peak is 9965 m3/s |
| F11 | Medium | 3-5 | Dam inventory not complete in Table 1; 17 dams and two barrages broadly described, Table 1 contains 14 selected dams |
| F12 | High | 11-12 | June and July storage comparisons confounded; 85% end-June L1 6217 and L2 10375 vs 85% end-July 5523 and 9965 |
| F13 | High | 7-14 | No flood-damage outcome; Only modelled river discharges and approximate bankfull noted |
| F14 | Medium | 4,13 | Bankfull uncertainty unspecified; L1 ~3400 and L2 ~4200 m3/s thresholds from figures |
| F15 | High | 13-14 | Extreme return periods require probabilistic qualification; 145-year rain and 142-year river flood from different sample/definitions |
| F16 | Medium | 1,13 | Quoted 0.6% probability differs simple recurrence inversion; 100/145=0.69%; 100/142=0.70% |
| F17 | High | 13-14 | Forecasting conclusion must be interpreted narrowly; Authors warn of poor historical forecast quality but recommend improved reliable forecasts |
| F18 | Medium | 10 | AMC-II versus III differences nonzero; Shown July models vary around 7–8% |
| F19 | High | 7-11 | Storage fraction definitions underspecified; Gross versus live capacity and exact multi-dam water levels not established |
| F20 | Medium | 8 | Channel cross sections partly estimated; SRTM and Google Earth plus Neeleswaram check, not all sections measured |
| F21 | Medium | 8 | Idukki model-vs-measurement peak times differ; 15 Aug 20:00 model versus 22:00 measured |
| F22 | Medium | 4 | 2013 release-attribution chart annotation; Figure 2 labels 6324 m3/s 2013 as Idamalayar-related without modeled causal counterfactual |
| F23 | Medium | 6-7 | SCS initial abstraction assumption; Ia=0.2S used with CN and kinematic routing |
| F24 | Medium | 10-11 | Marginal benefit of additional drawdown weak; L2 50% 7868 vs 25% 7844 m3/s under AMC-III |
| F25 | Medium | 11-12 | End-June flood cushion may refill by July; Authors report refill under wet season |
| F26 | High | 9 | Tributary attribution based on modelled flows; No independent synchronized basin gauges shown for all peaks |
| F27 | Medium | 6-7 | No-dam counterfactual is synthetic; L1 8224 and L2 11990 m3/s are HEC model without reservoirs |
| F28 | Medium | 11-12 | Two attenuation baselines are distinct; 16-21% relative to 85% storage; 33%/17% relative to no-dam case |
| F29 | Medium | 13 | Forecast POD sourced externally; 20–30% storm-detection values from older referenced studies |
| F30 | Medium | 1-2,14 | Cannot-avoid-flood conclusion limited to modeled bankfull breach; Other interventions and loss reduction not simulated |
| F31 | Medium | 9-14 | Research question differs across HR04-HR08; Basin wide L2 peaks versus Kakki outlet versus inferred state and forecast scenarios |
| F32 | Low | 7-8 | 85% representative actual state not full observed series; Initial storage is a simplifying setup not complete measured state trace |

## Audit files

- [All 15 source-page visual observations](HR01_15_page_visual_inspection_ledger.csv)
- [32 scientific findings](HR01_2019_scientific_findings.csv)
- [44 numerical and evidence checks](HR01_2019_numerical_evidence_checks.csv)
- [12 Kerala2040 acceptance actions](HR01_2019_Kerala2040_actions.csv)

All four CSVs are **derived records**, not original measurements. All page references in this record are the uploaded PDF positions (PDF p1 corresponds to printed journal p780). Page-image SHA-256 provenance is held in the complete private audit package; it is not evidence of independent model reproduction.

**Acceptance gate:** Before any claim about improved flood-safety/electricity operation, obtain official dam and river data, a reproducible water balance, forecast-vintage information, physically feasible rule curves, turbine hydraulic head and unit limits, and calibrated downstream hydraulics.

**Copyright:** Do not commit source PDF or full-page renders as open-licence material without rights clearance. See [Round 2 index](README.md) and [HR08 audit](HR08_DAS_2025_VISUAL_AUDIT.md).
