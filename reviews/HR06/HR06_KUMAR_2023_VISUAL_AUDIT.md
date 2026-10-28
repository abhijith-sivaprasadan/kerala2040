# HR06 — Kumar, Khosa & Gosian (2023): complete 23-page visual/scientific audit

**Article:** Anil Kumar, Rakesh Khosa & Ashwin Kumar Gosian, *A Framework for Assessment of Flood Conditions Using Hydrological and Hydrodynamic Modeling Approach*, *Water* 15(7), 1371 (2023). DOI [10.3390/w15071371](https://doi.org/10.3390/w15071371).

**Reviewed 28 October 2026.** User-uploaded published PDF, **23 pages**, SHA-256 `d44ddb1ffc94774a6eb43a3f804d122ba78ec566a5cf2465fe8cf67caf496ee8`. Individually rasterised every page at **175 DPI**; visually viewed all **12 two-page/single-page inspection sheets**, with individual full-resolution reinspection of key maps, equations and figures. Examined all Figures 1–14, Tables 1–2, equations, all 37 references, data availability and licence. **32 scientific findings**, **42 source/numerical checks**, **11 worked calculations**, and **12 Kerala2040 actions**.

**Boundaries:** These are critical **source-internal visual and arithmetic checks**. The original SWAT 2012 model, Nays2DFlood/iRIC runs, primary hydrometric observations, georeferenced flood extent masks, land-use data and 2018 flood inundation have **not** been independently rerun or verified. Do not promote text/figure assertions to reproducible physical causal evidence. The separately generated 14-page scientific audit PDF and full page-image ZIP remain outside public Git history. The published article is **CC BY 4.0**, as labelled on PDF page 1.

## Executive scientific conclusion

The paper connects a semi-distributed **ArcSWAT 2012** watershed model to **iRIC/Nays2DFlood** two-dimensional floodplain mapping of Periyar and Kochi, considering Idukki/Idamalayar reservoir rules. It contributes Kerala-specific hydrological maps, a reservoir stage–storage/rule-curve summary, and long-term streamflow NSE/PBIAS comparisons. However, its **three inundation scenarios are not a controlled experiment of dam-operation impacts**:

1. S1 includes reservoir operations and releases.
2. S2 is described as natural flow / no reservoir operation.
3. S3 **adds downstream 15–18 August rainfall** to the controlled setup.

Because rainfall inputs and potentially several boundary conditions change, differences in modelled depth cannot be assigned solely to release decisions. **Even the published depth maxima disagree across the discussion, conclusions and map legends.**

## Primary source-level contradictions and tests

| Source PDF | Exact published result | Audit interpretation |
|---|---|---|
| pp17,19–21 Fig13/14 | Combined reservoir + rainfall gives Kochi **0.011–11 m** in Section 5.4.3 and conclusions, whereas p19 says **17–20.12 m** and Fig13b legend reaches **20.12 m** | Critical numerical-reporting mismatch. Determine actual occupied maximum depth from model raster; a legend's largest class does not by itself prove a pixel reaches its upper bound. |
| pp15–16,19–20 Fig9/10/14 | Reservoir-only Kochi text **0.12–3m**, while Kochi map legends extend to **6.02m** | Clarify area/date and whether upper bins have occupied pixels. Basin Fig9 legend also extends to **19.993m** although p15 says basin depth up to 3m. |
| pp16–17,19–20 Fig11/14 | Natural Kochi described as up to **1.5m**, then maximum **3.096m** in p19 with map legends extending to 3.096m | Reconcile statistics and exact model extent. |
| p5 Eq2 | Runoff printed as `(Rday−0.2S)^2/(Rday+0.8S)` without zero-runoff condition | With `CN=80`, `S=63.5 mm`, and `Rday=5mm`, unconditionally evaluating printed expression gives **1.063mm** instead of **0mm** below the 12.7mm initial-abstraction threshold. This is a **presentation omission unless actual SWAT implementation tested**. |
| p5 Eq2 prose | Retention `S` defined in **m** while rain and standard retention form are in **mm** | Dimensional reporting inconsistency, not proven model bug. |
| p6 Eq9 | `exp(−13.86·slp)` but slope described as a percentage | Entering `5` vs `0.05` produces different curve numbers; establish actual input convention. |
| p8 Eq16 | `ν = k/6` and `k` is the dimensionless Kármán constant | Cannot represent kinematic eddy viscosity in m²/s without additional dimensional factors; check actual solver formulation. |
| p8 | NSE claimed to vary **0 to 1** | Mathematically NSE is unbounded below and can be negative. |
| pp14–15 | Manning’s `n = 0.086` for iRIC; Figure 8 visually compares a few simulated and observed water levels | No 2D independent depth/extent IoU/CSI or event-wide spatial error; strong model-accuracy claim is unsupported by numeric spatial validation in source. |
| pp13–14 Fig7 | Idukki and Idamalayar daily releases plotted generally in tens of m³/s | Source does not reconcile turbine, spill, flood-discharge and diversion branches with field flood peaks; avoid interpreting one plotted series as the entire release. |
| pp12–13 Fig5 | Idukki gross reservoir capacity **1,996 Mm³**, Idamalayar **1,089.90 Mm³** | Do not compare Idukki 1.996bn gross with HR03 Hunt’s 1.45bn nominal without aligning gross/live/FRL boundaries. |
| p13 | Idukki Moolamattom diversion up to **147 m³/s** into **Muvattupuzha basin** | Essential hydrological cross-basin and power-system accounting issue. |
| p22 refs 22,26 | Reference 22 is marine carbon/nitrogen chemistry, reference 26 is psychology **Parenting Scale** | Clearly unrelated to the SWAT slope and groundwater methodology for which cited; verify source references. |

### Streamflow performance reproduced from Table 2 (PDF p11)

| Station | Daily NSE calibration → validation | Monthly NSE calibration → validation | Key limitation |
|---|---|---|---|
| Neeleswaram | 0.588 → **0.514** | 0.767 → **0.632** | Long-term flow agreement is not an independent 2018 extreme-flood depth score |
| Kalady | 0.538 → **0.619** | 0.642 → **0.752** | Need flood peak/timing, volume and spatial map skill |

A 0.514 daily NSE is only moderate historical fit. The paper's 2018 iRIC depth comparison in Figure 8 uses a few gauge readings and does not quantify event-wide error. Its conclusion that the reservoir operation was "well managed" is stronger than its evidence.

### Resource quantities and arithmetic

- Idamalayar **75 MW**, gross storage **1,089.90 Mm³**; reported 2018 releases **998,954,208 m³** equal about **31.68 m³/s** if spread over 365 days.
- Idukki **780 MW**, gross storage **1,996 Mm³**, Moolamattom diversion upper rate **147 m³/s**; reported **1,182,194,784 m³** annual releases average **37.49 m³/s**.
- These averages do **not** establish observed flood-day release hydrographs or turbine/spill splits. The implied combined gross storage is **3,085.90 Mm³**.
- 2018 statewide precipitation 2,346.6 mm described as 42% above normal implies normal **1,652.54 mm**; Idukki 3,555 vs 1,852 mm is **91.95% higher**.
- Main study makes **no** head-dependent electricity production (MW/MWh), usable flood-storage opportunity-cost or dispatchable-firm-capacity calculation.

## Cross-paper context

HR06 adds city-scale two-dimensional flood hazard to the first seven full Round 2 audits: **HR01 Sudheer** basin peak attenuation, **HR02 Mishra** historic climate anomalies, **HR03 Hunt** event-conditioned PGW climate response, **HR04 Ryan** Kakki counterfactuals, **HR05 Singh** integrated Periyar hydrology/inundation, **HR07 Suresh** reservoir satellite reconstruction and **HR08 Das** forecast-conditioned scenario operation.

Its contribution must not be described as proof that dam operation **caused** the difference in Kochi inundation or that later forecast-informed operation would avert damage. The essential gap is a matched, mass-conserving dam-operation, rainfall, tide, flood-routing and turbine-electricity experiment with independent observational validation.

## Derived records in GitHub

- [23-page individually inspected evidence ledger](HR06_23_page_visual_inspection_ledger.csv)
- [32 source-critical scientific findings](HR06_2023_scientific_findings.csv)
- [42 numerical and source consistency checks](HR06_2023_numerical_evidence_checks.csv)
- [11 independently worked arithmetic/units calculations](HR06_2023_independent_calculations.csv)
- [12 Kerala2040 research actions](HR06_2023_Kerala2040_actions.csv)

These are published **derived research records**. The original source PDF and all rendered-page images are *not* deposited in the public repository in this update. Full PDF audit and the individual source-page image archive are available as conversation artifacts. Redistribution of the original source or figures must satisfy the source CC BY licence and any figure-specific credits.

**Review status:** **Full visual/source-scientific audit complete**, **original model replication incomplete**.
