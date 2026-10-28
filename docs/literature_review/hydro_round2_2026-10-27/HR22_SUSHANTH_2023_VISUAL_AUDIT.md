# HR22 — Sushanth et al. (2023): complete 14-page visual/scientific audit

**Paper:** Kallem Sushanth, Ashok Mishra, Parthasarathi Mukhopadhyay and Rajendra Singh, *Real-time streamflow forecasting in a reservoir-regulated river basin using explainable machine learning and conceptual reservoir module*, **Science of the Total Environment 861 (2023), 160680**. DOI: https://doi.org/10.1016/j.scitotenv.2022.160680.

**Audit completed 28 October 2026.** All **14 original publisher-PDF pages** separately rendered at **175 DPI** and individually visually examined in seven paired-page sheets. All Figures **1–15**, Tables **1–6**, Equations **1–7**, abstract, methods and bibliography inspected. Original PDF SHA256: `0f7b58246e1737f69fcf2e48455e7aafc6fa7db81159d321bb75735fb90c94af`. **32 source-critical scientific findings, 42 numerical/evidence checks, 12 prioritized Kerala2040 actions and a 14-page inspection ledger.**

**Method and boundary:** This is an original-source visual and arithmetic audit, **not** independent retraining of LSTM, rerunning SHAP, DVC reservoir observations, archived GFS model vintages or actual dam operation. The six-page illustrated PDF audit and 14 original source-page renders are separately downloadable private conversation artifacts, **not public GitHub files**. Original PDF copyright is ©2022 Elsevier B.V., all rights reserved.

## Principal contribution

This paper implements a genuinely useful **weather-forecast-informed hybrid model** for Jharkhand's Damodar basin: LSTM forecasts for upstream **Tenughat and Konar** inflows; **Concept of Storage Zoning (CSZ)** for their predicted releases; and a third LSTM for **downstream Panchet** inflows using forecast releases plus meteorological inputs. An additional SHAP analysis ranks predictors (not causal drivers). Thus generic combination of LSTM + SHAP + forecast rainfall + conceptual reservoir modules **was already demonstrated by 2023** in India; Kerala2040 cannot assert that as a novel invention.

### Forecast metrics (verbatim Table4 p9, Table5 p10, Table6 p12)

| Outcome | NSE day 1 | NSE day 3 | NSE day 5 | RMSE day 1 | RMSE day 5 |
|---|---:|---:|---:|---:|---:|
| Tenughat inflow | 0.918 | 0.878 | 0.844 | 66.32 | 91.59 |
| Konar inflow | 0.891 | 0.873 | 0.843 | 16.83 | 20.27 |
| Tenughat outflow | 0.926 | 0.886 | 0.848 | 69.00 | 100.87 |
| Konar outflow | 0.935 | 0.884 | 0.847 | 12.39 | 19.04 |
| **Panchet inflow** | **0.961** | **0.939** | **0.882** | **76.77** | **133.87** |

All RMSE values are in m³/s. Independently recomputed from printed values, Panchet 5-day error is **57.10 m³/s higher**, or **74.38% above** day one. That does **not** mean NSE or actual flood-control performance rises/falls proportionally. Figures 11–15 show individual high-flow under/overprediction despite strong aggregate NSE.

## High-priority scientific issues

1. **PDF p4, Equation 1:** The accompanying SHAP explanation defines coalition subset Z as containing feature i, yet the displayed equation adds i to Z. Standard Shapley coalition sums exclude the evaluated feature. SHAP signs do not mean active/inactive states; they increase/decrease prediction relative to baseline.
2. **PDF p4, Equation 2:** Reservoir water balance is correctly printed as a sum of daily input and loss volumes, but the implementation walkthrough incorrectly instructs readers to update storage using Equation **1**, which is the unrelated SHAP equation. This is a source cross-reference error, **not proven code error**.
3. **PDF p4, Figure 3:** Q in the flood-release branch `Q<Qc` is undefined, and a discharge capacity in m³/s requires timestep conversion to become m³. Whether emergency releases respect physical outlet, turbine and downstream limits is not demonstrated.
4. **PDF pp4–5:** The source describes min-max normalization **before** chronological division into 2000–2014 training and 2015–2018 testing; normalization over the complete period could leak future extrema. It also describes adjusting hyperparameters until **both** train and test performance was satisfactory. These are **potential** leakage and test-selection risks requiring original code, not proven contamination.
5. **PDF pp4–5,8–12:** For each multi-day issue date, the precise operational source of lagged inflows, forecast rainfall and upstream outflows is not shown. Future observed flows must not silently enter longer-lead forecasts. No definite look-ahead use has been proven.
6. **PDF p5:** SDM GFS bias correction has a **2000–2016** calibration and **2017–2018** validation; LSTM itself uses **2000–2014** training and **2015–2018** testing. These are different components and periods. Source does not identify all GFS original issue-time vintages.
7. **PDF pp6–13:** Largest floods are visibly less accurately predicted than the full-period NSE suggests. Evaluate rare-event flood peaks, early warning false alarms, threshold skill and causal downstream hydraulics independently.
8. **PDF pp7–8:** SHAP attribution is evidence of predictive dependence on past inflow and Tenughat releases, **not** proof of hydrological causation, physical controllability or conserved water.
9. **PDF pp10–13:** No new release schedule tested for avoided flood damage, no true gate or turbine dispatch, no flood maps and no hydropower MW/MWh trade-off quantified. Flood prevention is a motivation, not a measured result.
10. **PDF p13:** Authors acknowledge need for operational rule curves, improved forecast ensembles and reservoir-operation impact evaluation as future work; observed data and code are not publicly deposited.

## Research implications for Kerala2040

**HR22 belongs to the implemented Indian hybrid ML–reservoir forecasting literature.** HR08 Das (2025) also integrates weather forecasts and reservoir scenarios for Kerala; HR07 Suresh reconstructs reservoir operation using satellite data; HR01/HR05/HR06 examine flood hydrology and downstream impacts. The most defensible missing contribution is not generic coupling, but a **leakage-controlled, forecast-origin-verified, physically feasible, electricity-aware reservoir operation** tested against observed dam logs, downstream flood hazard and generation trade-offs.

## Derived source evidence in this folder

- [14-page visual inspection ledger](HR22_14_page_visual_inspection_ledger.csv)
- [32 scientific findings](HR22_2023_scientific_findings.csv)
- [42 source/arithmetic checks](HR22_2023_numerical_evidence_checks.csv)
- [12 Kerala2040 research actions](HR22_2023_Kerala2040_actions.csv)

**Interpretation:** The audit establishes claims and gaps visible in the uploaded source; it does not establish original-model software bugs, observational flood risk reductions, or verified operational benefits.
