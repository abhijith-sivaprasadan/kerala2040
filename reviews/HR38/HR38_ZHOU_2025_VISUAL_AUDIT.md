# HR38 — Zhou et al. (2025), source-critical visual and scientific audit

**Paper:** Yanlai Zhou, Zhihao Ning, Kangkang Huang, Shenglian Guo, Chong-Yu Xu, Fi-John Chang, *Sustainable energy integration: Enhancing the complementary operation of pumped-storage power and hydropower systems*, **Renewable and Sustainable Energy Reviews 210 (2025), article 115175**. DOI https://doi.org/10.1016/j.rser.2024.115175.

**Completed 28 October 2026:** Published 16-page Elsevier PDF, source SHA-256 `b59ba835b8c2f033d65786fcc1eab9519a484f7fad6b1540a7c0862f3d449606`; each of the 16 pages rendered individually at 180 DPI and visually inspected in eight readable paired-page sheets. Figures 1–7, Tables 1–4, all Equations 1–14, detailed figures, captions, data statement and all 47 bibliography references reviewed. **36 source-critical findings; 50 internal arithmetic/evidence checks; 12 Kerala2040 actions**.

**Scientific boundary:** This is a source-internal visual and numerical audit, **not** independent execution of the original MSSA solver, source Hunan grid time series, field PSP operations, or emissions dispatch. The downloadable, professionally rendered **11-page audit PDF**, source page images and private ZIP package were produced separately. Only derived text and CSV evidence is committed to this public Git repository. © Elsevier; no public redistribution of the original publisher pages.

## Central assessment

The study genuinely implements a multi-objective **model** coupling HMF **1.2 GW** off-river pumped storage and **396 conventional regulating hydropower stations (8.53 GW)** in Hunan. It selects **12 representative 15-minute daily residual-load scenarios** from 2022 observations and uses an MSSA optimizer to maximize hydropower benefit while minimizing residual-load fluctuations. The paper's reported maxima of **+26% output, -22% fluctuation, +26% money and +25% carbon equivalence** relative to practical operation are **model-derived**, not measured improved power-grid operation.

**The most serious barriers to direct reuse** are printed water-balance contradictions and dimensional omissions, impossible algorithm benchmark dispersions, and unresolved energy/financial/emissions accounting. These findings **do not prove incorrect source code**; no code or original observed dataset was available to check.

| Source PDF | Major issue | Reconciliation |
|---|---|---|
| p7 Eq7 | Flow m3/s times hours | Must multiply by **3600** to change reservoir m3 |
| p7 Eq10 | Both reservoirs end at **105% initial** | Contradicts Eq7 closed balance unless externally added water is modeled |
| p8 Eq11b | Branch `C3<0` though `C3∈[0,1]` | One movement branch unreachable |
| p9 Table2 | Thirty-run spring/summer/autumn/winter HB SD values | Printed **0.72/0.83/0.77/1.07** vs mathematically possible minima **4.434/14.711/5.825/14.243** |
| p9 text | 398 decisions x96=38,208, separately 3,456 per solution | Dimensional inconsistency |
| pp11,14 | 43.7 vs 46.8 TWh annual output under S3 | Unresolved differing reported output |
| pp8,13–14 | 46.8TWh x 785g/kWh vs 356.2 million kg carbon equivalent | Direct conversion would be **36,738 million kg**, factor **103.14** bigger; scope/weights unspecified |
| p12 Fig6 | Financial benefit 3.25bn vs 2.59bn USD | (3.25/2.59-1)*100=**25.48%**, consistent with headline rounding |
| p13 Table4 | 356.2 vs 285 million kg CO2 | **24.98%** increase in reported equivalence, but absolute emissions accounting unresolved |

## Findings by source page

- **F01 (Critical, PDF p7):** Eq7 multiplies flow m3/s by hours without 3600 factor
- **F02 (Critical, PDF p7):** Eq10 requires both reservoirs to end 105% initial while Eq7 conserves total volume
- **F03 (Critical, PDF p8):** Eq11b requires C3<0 but C3 defined as random uniform 0 to1
- **F04 (High, PDF p5,8):** Eq1a and Eq12 revenue in USD/MWh times kW omits interval and 1/1000 conversion
- **F05 (Critical, PDF p8,13-14):** 46.8TWh times 785gCO2/kWh implies 36738 million kg, versus printed 356.2 million kg
- **F06 (Critical, PDF p9):** Table2 mean/min/max incompatible with reported 30-run HB standard deviations
- **F07 (High, PDF p9):** Decision variables 398x96=38208 versus manuscript 3456 per solution
- **F08 (High, PDF p11,14):** Scenario S3 hydro output 43.7TWh results versus 46.8TWh conclusion
- **F09 (High, PDF p5,11-13):** 12 representative days are not transparently weighted to seasonal/annual totals
- **F10 (High, PDF p8-11):** Hundreds million USD HB totals cannot be single 24h at stated plant capacity and tariff; annualization undefined
- **F11 (High, PDF p8,13):** Single avoided emissions rate 785g/kWh omits marginal fossil dispatch
- **F12 (High, PDF p8,12-13):** No transparent emissions cost of PSP pumping electricity and storage losses
- **F13 (High, PDF p7):** Regional algebraic power balance does not check nodal congestion, ramps, frequency reserves or security
- **F14 (Medium, PDF p7):** Renewable inputs denoted demands but subtracted as supplies; biomass variable inconsistently included
- **F15 (High, PDF p7):** 396 hydropower stations constrained by generation bounds not individual hydrologic water balances
- **F16 (High, PDF p3,5,7):** Off-river rain replenishment mentioned while Eq7 includes transfer only
- **F17 (Medium, PDF p5,7):** Head/storage functions and loss curves not documented for replication
- **F18 (High, PDF p5,7):** Binary transition equations may permit one idle 15-min interval despite 30-min shutdown requirement
- **F19 (Medium, PDF p7-8):** Tolerance delta 5% modeled as exact storage increase not allowable interval
- **F20 (High, PDF p5,7):** Narrated flood-limit reservoir rules not explicitly coded for 396 plants
- **F21 (High, PDF p14):** Authors acknowledge hydrologic inflow forecasting absent
- **F22 (High, PDF p15):** Authors cannot share original Hunan project dataset or model implementation
- **F23 (Medium, PDF p5):** 12-day scenario reduction lacks probability weights and raw fidelity scores
- **F24 (High, PDF p4-5):** PSP installed GW without verified usable stored GWh or duration
- **F25 (Medium, PDF p7):** Detailed turbine/pump hydraulic ramp, start-stop losses, and head-dependent efficiency absent
- **F26 (High, PDF p10-12):** Generation at USD70/MWh and pumping USD17/MWh is fixed tariff not market-validated
- **F27 (High, PDF p7):** Provincial imports/exports allowed as scalar ranges without network deliverability
- **F28 (Medium, PDF p5,7-8):** Residual-load standard deviation ratio ignores ramp maxima, outage and flood risk
- **F29 (Low, PDF p13):** Table4 S3 carbon seasons sum356.1 vs annual356.2 million kg; rounding possible
- **F30 (High, PDF p1,11,14):** Percentage improvements are optimized model scenarios, not measured power system changes
- **F31 (Medium, PDF p9):** Algorithm benchmarks do not disclose original trials, feasibility violations and standardized objective scaling
- **F32 (High, PDF p5,15):** Scenario backward reduction cites ref35 salp swarm rather than ref37 scenario reduction
- **F33 (Medium, PDF p8,15):** Saremi origin incorrectly cross-referenced to derivative salp paper ref36
- **F34 (Medium, PDF p4):** Table1 capacity GW shares called energy-output shares
- **F35 (Medium, PDF p2-3):** 2022 cumulative installed capacities described as annual growth figures
- **F36 (High, PDF p1-16):** Hunan case has no Kerala dam flood safety, hydro network, local transfer or dispatch observations

## Evidence files

- [All 16 individual-page inspection observations](HR38_16_page_visual_inspection_ledger.csv)
- [36 scientific findings](HR38_2025_scientific_findings.csv)
- [50 source/arithmetic checks](HR38_2025_numerical_evidence_checks.csv)
- [12 Kerala2040 actions](HR38_2025_Kerala2040_actions.csv)

## Implications for Kerala2040

HR38 already demonstrates **multi-objective joint pumped-storage and conventional hydropower dispatch**, so generic 'we integrate hydro and pumped storage with renewables' would be an unsupported novelty claim. A more defensible contribution combines physically consistent reservoir hydrology, transmission deliverability, hydro head and unit constraints, actual forecast-information timing, flood-safe operation, realistic tariff and carbon accounting, **and** Indian PSP project-delivery risk. Compare HR25 (execution risk) and HR37 (conceptual water-power resilience) before defining integrated model scope.

**Data availability:** PDF p15 states the authors do not have permission to share data. Existing methods/benchmarks should be independently re-created on reproducible Kerala or surrogate datasets before results are claimed.
