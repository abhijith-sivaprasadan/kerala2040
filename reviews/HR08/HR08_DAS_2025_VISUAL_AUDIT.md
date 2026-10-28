# HR08 — Das et al. (2025): published-edition full visual and scientific audit

**Source:** Pritam Das, Sarath Suresh, Faisal Hossain and coauthors, *Forecast-Informed Reservoir Operations within a Satellite-Based Framework for Mountainous and High-Precipitation Regions: Case of the 2018 Kerala Floods*, Journal of Hydrologic Engineering **30(2)**, article 05025003 (2025). DOI: https://doi.org/10.1061/JHYEFF.HEENG-6276.

**Review date:** 28 October 2026. **Version:** 15-page published ASCE PDF downloaded via KTH library. Source SHA-256 `a1d88f8b572d8bd5ef1d8ae6415b41e353ff5a86570a864b034d7f12306eb287`. **Method:** all 15 PDF pages rasterised individually at 170 DPI; each visually viewed in seven paired sheets and a final individual sheet. All Figures **1–13**, equations, scenario maps, flow charts and bibliography reviewed. **28 source-critical findings**, **28 source-internal numerical/evidence checks**, **12 Kerala2040 actions**. Full audit PDF and source-page images were generated in the conversation but **are not uploaded to this public Git repository**.

## Executive assessment

This study is a **high-priority direct comparator** for weather-forecast-informed 2018 Kerala reservoir operation. It combines CHIRPS-GEFS meteorological forecasts and RAT 3.0 satellite hydrological nowcasts to generate possible inflow and **scenario-conditioned** release and water-level trajectories at **six selected Greater Periyar reservoirs**. It already addresses a major portion of the proposed Kerala2040 'novel' research direction; **do not claim first Kerala use of forecast-informed RAT or flood release scenarios**.

The strongest demonstrated value is **possible advance warning of the timing/rate of rise of an extreme event**, including roughly week-ahead indicators. **Observed Idukki peak magnitudes are substantially underestimated.** Importantly, forecast-skill scores (Figs. 7–8) are largely measured against **RAT satellite-derived nowcast**, whereas only the separate Idukki nowcast has a reported gauge comparison (**R² 0.61, NRMSE 40%**, p4). These are different evaluation targets.

## Highest-priority source issues

1. **Definite printed mass-balance sign inconsistency (pp5–6).** Text gives Delta S = O − I − E for a releasing reservoir, while Fig3 and the p6 rate formula O = (I − E − Delta S)/T imply Delta S = I − O − E. This is a manuscript problem, **not evidence that RAT executes incorrectly**. A dimensional check must distinguish accumulated volumes (m³) from outflow rates.
2. **Forecast information/time of issue:** the 2018 event is reconstructed with a subsequently published CHIRPS-GEFS/RAT workflow; this PDF does **not** independently demonstrate that each archived input was available operationally on each 2018 forecast origin.
3. **Observed versus modelled magnitude (pp7–8):** the paper reports actual Idukki inflows 1,440–2,000 m³/s and releases 1,100–1,460 m³/s during 15–17 August. The published observed peak (Fig6 orange) far exceeds satellite nowcast and scenario forecasts.
4. **Lead-time interpretation (pp8–9):** week-ahead timing information is not an independently validated week-ahead peak-flow magnitude. Lead R² values vary and Figure 8 displays only day 1–14 while the methods mention 1–15.
5. **Spatial rainfall bias:** the closest of three coastal CHIRPS-related gauges is about 75 km from Idukki, while Figure 5 shows substantial orographic-rainfall underestimation. Small average bias at Cochin (p6) does not establish extreme upper-catchment accuracy.
6. **Conditional scenarios, not actual forecast of operator action:** Figure 10 shows six-reservoir outflow and level trajectories under target stage, % storage change, rule curves and user-defined assumptions. There is no verified turbine/gate/ramp feasibility, MW/MWh value, flood-depth risk reduction or optimization of water–power trade-offs.
7. **Different flow units:** Fig10 gives millions of m³/day versus Fig6 m³/s; 1 million m³/day = 11.574074 m³/s.
8. **Data exception:** the paper states observed in-situ Idukki reservoir inflow data are not publicly accessible; RAT code and most weather inputs have cited online locations but immutable run hashes/configurations are not published in this PDF.

## Closest literature synthesis

| Source | Primary contribution | Still unresolved |
| --- | --- | --- |
| HR04 Ryan (2020) | Kakki simulated alternative reservoir release rules | Physical hydropower costs and observed release baseline |
| HR05 Singh (2022) | Periyar HEC-HMS/ResSim/RAS flood routing and inundation | Hindsight calibration and long return-period uncertainty |
| HR07 Suresh (2024) | Satellite-based reservoir area, inferred outflow and timing | Extreme flow magnitude bias and gate/turbine-state observations |
| **HR08 Das (2025)** | GEFS-based forecast signals and RAT conditional operating scenarios | Observed out-of-event forecast skill, physically feasible hydroelectric operation and downstream damages |

**Next scientific task:** source KSEB/CWC dam operating logs, independent streamflows, verified archive issue-time forecasts, reservoir head/storage curves, electrical generation observations and transmission transfer limits. Only then make a physically constrained hydro-flood-energy claim.

## Evidence and artefact boundaries

- All source PDF pages visually reviewed and figure/caption locations verified.
- Independently checked displayed sign algebra, volume-rate conversion, Sholayar level difference, lead-axis count and source numbers.
- No independent rerun of RAT, VIC, MetSim, GFS/GEFS, image classification or observed gauge series.
- Original ASCE PDF and source-page-image ZIP are excluded from public Git history pending redistribution clearance.
- Derived CSV files in this folder cover **15 inspected pages, 28 findings, 28 checks, 12 actions**.
