# HR04 — Ryan et al. (2020): Kakki reservoir management — full 11-page visual/scientific audit

**Publication:** Ciarán Ryan, Mark A. Trigg, Adarsh S. (2020), *An investigation into the impact of reservoir management Kerala floods 2018: A case study of the Kakki reservoir*, IOP Conference Series: Earth and Environmental Science 491, 012005. DOI: [10.1088/1755-1315/491/1/012005](https://doi.org/10.1088/1755-1315/491/1/012005). **CC BY 3.0** as printed on PDF p2.

**Review date:** 27 October 2026. **Uploaded PDF:** 11 pages, one cover + 10 journal pages. **Source SHA256:** `1444cc7a1301cc659ebe87bd343c1870e5b70cc5f72364716fcc2f5074a113fc`. Every page independently opened and visually inspected at 185 DPI. Visual evidence covers Figures 1–7, Table 1, equations and 17 printed references. **28 source findings, 25 numerical/evidence checks, and 12 implementation actions.** This is a visual source audit, **not** an independent HEC model rerun or actual release/damages validation.

**Storage disclosure:** The full 11-page scientific audit PDF, 11 rendered source pages, page ledger, findings CSV, numerical-check CSV, action CSV and two ZIP evidence packages were generated in the conversation. **Their binary files and detailed source-image ZIP are not in this GitHub commit.** This Markdown records their supported conclusions with exact source locations. CC BY reuse must retain attribution.

## Main result and its strict interpretation

The paper uses **NASA GPM rainfall -> HEC-HMS catchment inflow -> HEC-ResSim reservoir outflow**, evaluating **six long-term, two seven-day and two one-day** counterfactual strategies for Kakki reservoir. The baseline flood-event peak is described as **492 m3/s** (p7), and **493 m3/s** (p10); the most constrained long-run LRS6 reaches **50 m3/s**. Relative to 492, this is a **simulated 89.84% reduction in the modelled Kakki outlet flow peak**. It is **not** an observed outflow decline, a measured 89.84% decrease in downstream flood damage, or proof of no hydroelectric generation penalty.

### Source-internal numerical reconciliation

| PDF source | Calculation or quoted model setting | Verified status / boundary |
|---|---|---|
| p4 | The rainfall proxy is scaled **3.73** to meet an **1762.7 mm** IMD reference total | Original proxy = **472.57 mm**, 273% uplift; no independent check that gauges/catchment footprints agree |
| p4 | Catchment 219.8 km2, lag 1.66 h, CN 71.75 in lag derivation but CN 77 for runoff losses | 1.66 h = 99.6 min, versus source 99.9 min (rounding/precision); CN roles need reconciliation |
| p5 | S = 1e-22 * exp(0.0505 E) BCM, maximum elevation E=981.45 m | Printed formula implies **0.33499 BCM** at maximum; actual observed curve not independently checked |
| p5 | **A = exp(0.0404 E) km2** | At E=981.45m this implies **1.66e17 km2** — clearly wrong as a physical area *as printed*. Likely missing factor/notation; **do not infer the run used that exact expression** |
| p5 | Area-elevation DEM fitting for **990–1040 m** vs quoted maximum water elevation **981.45 m** | Unexplained apparent datum/range contradiction |
| p6 | Inferred minimum release = **7.99 m3/s** | Equivalent to 690,336 m3/day; not demonstrated turbine power or minimum service |
| p6 Fig. 5 | Reconstructed reservoir outflow dips below **0 m3/s** | Physically inadmissible as a true release; source water-balance/model discrepancy to investigate |
| pp7–8 | LRS1/2 model peak = **465 m3/s** | (492–465)/492 = **5.49%**, consistent with source ~5% |
| p8 | LRS3 artificially caps at **200 m3/s**; LRS4 at **100 m3/s** | Full stage-storage trajectories and realistic operation constraints are not published |
| pp8–10 | LRS6 cap **50 m3/s** | (492–50)/492 = **89.84%** modelled flood-event peak reduction; does not establish actual flood damages or output |
| p9 Fig. 7 | SRS2 cap **200 m3/s** from Aug 7 | (492–200)/492 = **59.35%** simulated decline; water-level trajectory and forecast vintage unavailable |
| p9 | IRS1 **475 m3/s** | (492–475)/492 = **3.46%**, source calls this small |
| p9 | IRS2 **400 m3/s** | Paper explicitly reports resulting level above **981.45 m**; **unsafe / infeasible as modelled** |
| pp2,7–9 | Six long, two short, two immediate cases | 10 alternatives, plus a simulated baseline |

## High-priority methodological findings

1. **Hydrological input bias is consequential (p4):** The uncorrected GPM rainfall is less than one-third of the adjusted target total. A uniform scalar may not preserve peak timing, spatial rainfall gradients or runoff nonlinearity. No independently validated flood hydrograph is published.
2. **Two curve-number values (p4):** The article computes CN=71.75 and later uses CN=77. These may pertain to lag versus loss models, but the distinction and sensitivity require explicit confirmation.
3. **Printed area-elevation expression is impossible (p5):** Reconstruct from the authoritative stage-area-storage relation, MERIT DEM, vertical datum and the actual model input rather than silently 'fixing' the paper.
4. **DEM elevation interval (p5):** The stated 990–1040m fitting range exceeds the 981.45m maximum quoted for the reservoir. This is unresolved.
5. **Physically negative inferred release (p6 Fig. 5):** This is direct visual evidence of water-balance inconsistency in the estimated flow series, not an observed reservoir release. Do not use the negative periods as actual gate/turbine discharge.
6. **2018 comparison curve is not an independent control (pp5–6):** The supposedly average guide curve uses 2014–2018, including the flood year being evaluated.
7. **Model baseline is not independent ground truth (p7):** A historical monthly guide curve is used to simulate a 492 m3/s baseline; observational release-flow and stage error metrics are not reported.
8. **Artificial flow cap and water balance (pp7–9):** Different 50/100/200 m3/s caps can move discharge earlier, but their flood safety requires stage-storage trajectories and validated rules. The only unsafe case explicitly identified is immediate IRS2.
9. **No hydropower energy verification (pp6,9–10):** A constant minimum 7.99 m3/s does not determine H(t), turbine efficiency, dispatchable MW or total MWh. Therefore the claim that the 50 m3/s strategy has virtually no disadvantages is not demonstrated.
10. **Hindsight forecast information (pp8–10):** The guide curve is altered around the realised August 14 storm and the paper assumes lead times of 1, 7 or >30 days. There is no archived operational forecast-vintage evaluation showing that decision makers could identify actual inflows in advance.
11. **Flood losses are not modelled (pp9–10):** Peak outlet Q is an input to hydrodynamic risk, not a flood-level, inundation extent, exposure or damage calculation.
12. **Study geographic scope (pp3–4):** One Kakki reservoir and its 219.8 km2 modelled catchment do not establish impacts across all the 2018 Kerala basins.
13. **Incomplete replication package (pp4–11):** Complete HEC-HMS/ResSim configuration, hydrograph validation records, observed storage/release, calibrated GPM bias criteria and uncertainty ensembles are not available within the article.
14. **Several assumptions lack case-specific evidence (pp6–7):** Buffer storage 20%, inactive 5%, seepage 8mm/day and minimum turbine-service flow are assumed or inferred without demonstrating operator rules or opportunity costs.
15. **'Optimal' means best among tested runs (p7):** Six manually designed long-run cases do not constitute proof of globally optimal releases under physical constraints.

## Comparison with HR07 — Suresh et al. (2024)

| Topic | Ryan (2020) | Suresh (2024) |
|---|---|---|
| Main question | Could different 2018 Kakki release rules lower a *modelled* flood peak? | Can RAT 3.0 reconstruct 2018 reservoir area, storage trends and release timing? |
| Weather/hydrology | GPM proxy adjusted by 3.73; HEC-HMS | IMERG/VIC5; satellite SAR and optical surface area; SRTM A-E |
| Geographic scope | Kakki only | 19 Kerala reservoirs; Kakki has source comparison |
| Critical limit | No validated flood release baseline, dam-safety trajectories or MW/MWh comparison | Peak inflow magnitudes substantially underestimated in selected cases; inferred releases can lose their peak |
| Common gap | **Verified Kakki stage-storage, measured inflow and outlet flow, operating constraints and physical electricity production** before co-optimizing safety and hydropower |

This is a comparison of **different tasks** rather than a direct contradiction. The first is a release-policy counterfactual; the second is event monitoring and reconstructed hydrology. Neither establishes independent Kerala electricity adequacy.

## Kerala2040 acceptance actions (12)

1. **P0:** Source a versioned and rights-reviewed Kakki water level, storage, inflow, turbine and spillway-release dataset from KSEB/CWC/WRIS.
2. **P0:** Reconstruct physically consistent stage-area-storage curves with documented datum and coefficients.
3. **P0:** Resolve negative modelled releases with a complete, time-step-correct water balance.
4. **P0:** Independently validate GPM/IMERG/IMD rainfall inputs, bias correction and extreme peaks.
5. **P0:** Place Ryan and Suresh on a matched Kakki date/measurement comparison.
6. **P1:** Reproduce HEC-HMS/ResSim only after obtaining sufficient actual input files/parameters.
7. **P1:** Test rainfall forecast **vintages available before each decision**, not later reanalysis.
8. **P1:** Reject or modify any rule that violates storage, outlet or environmental constraints.
9. **P1:** Include head-dependent turbine water-to-electricity MW/MWh and water-service tradeoffs.
10. **P1:** Couple feasible outlet flows to downstream flood-routing/damage where data permit.
11. **P1:** Perform explicit uncertainty, sensitivity and independent holdouts for hydrologic assumptions.
12. **P2:** Only after validation, connect constrained hydro flexibility to time-matched Kerala demand and transfer capability.

## Inspection and claim boundary

- **Completed:** all 11 source-page images visually opened individually; Figures 1–7, Table 1 and printed bibliography inspected; 28 documented findings and 25 evidence/math checks.
- **Not completed:** independently rerunning HEC-HMS or HEC-ResSim, validating observed reservoir flows, producing a hydrodynamic flood-risk model, reconstructing hydropower production or establishing reliable deliverable electricity capacity.
- **Source licence:** CC BY 3.0 as printed, with attribution. The full source images and audit package are separate downloadable conversation artifacts, not committed to this repo.

Related: [Round 2 bibliography](papers.csv), [HR07 Suresh audit](HR07_SURESH_2024_VISUAL_AUDIT.md), [Kerala transmission Paper 20](../CEA_TRANSMISSION_2034-35_PAPER20_AUDIT_2026-10-27.md).
