# HR03 — Hunt & Menon (2020): full 14-page visual/scientific audit

**Document:** Kieran M. R. Hunt & Arathy Menon, *The 2018 Kerala floods: a climate change perspective*, *Climate Dynamics* (2020), DOI [10.1007/s00382-020-05123-7](https://doi.org/10.1007/s00382-020-05123-7).

**Completed:** 28 October 2026. Uploaded source PDF **14 pages**, SHA-256 `2b8c4e0d06b61030c7e862123228e7e2b7bce1a8a775eb905c009cabb5787ca7`. All pages individually rendered at **165 DPI** and visually inspected in seven readable two-page views. Figures **1–8**, Table 1, equations (1) and (2), reservoir and basin panels, references, publication licence and source-version metadata examined.

**Review evidence:** 32 scientific findings, 40 source-internal checks, 14 page-level visual observations and 12 Kerala2040 research actions. The downloadable full **14-page scientific audit PDF**, provenance images and ZIPs were generated in the conversation but **are not committed as binary files to GitHub**. This record and CSVs are derived reviews, not reproductions of WRF, WRF-Hydro, CMIP5 models, ERA-I forcing, measured reservoir discharge or actual flood impacts.

## Scientific interpretation

The authors conduct a pseudo-global-warming (PGW) experiment for the same August **2018** weather event under preindustrial, present/control and RCP8.5 (2075–2100 monthly CMIP5-delta) backgrounds. They use **WRF 4 km inner domain** and **WRF-Hydro 125 m routing**. Abstract and discussion give approx **+18% preindustrial** and **+36% RCP8.5** rainfall relative to control, and reported domain-mean routed streamflow is **+16% / +33%**. These results are an instructive **conditional single-event climate mechanism**: weakening monsoon circulation versus tropical humidity increase. They are **not unconditional Kerala flood-frequency estimates** or measurements of climate-attribution probability.

**Fundamental physical boundary:** the methods on PDF page 4 explicitly omit artificial reservoirs and dam-gate operations from WRF-Hydro. A fitted constant-evacuation storage proxy is used later. This proxy allows storage to exceed nominal capacity. The resulting excess is a hypothetical balance quantity, **not** an operationally attainable storage state, validated capacity prescription, flood-damage estimate or hydropower MW/MWh value.

## Critical presentation and scientific issues

- **p6 PI direction contradiction:** text states the preindustrial experiment was drier by 18%; source abstract p1, Figure 3 difference map p6, streamflow p9 and Discussion p12 instead indicate **preindustrial rain approximately 18% heavier than control**. This should be author-verified.
- **p3 vs p11 outer-domain resolution:** 36 km is printed in WRF methods; 20 km in Discussion. Full WRF namelist is not included.
- **pp1,10–12 capacity denominator confusion:** 4 calibrated reservoirs have modelled pseudo-storage exceedances of **34/43/54%** for control/PI/RCP8.5, while all **six** have **37/50/44%**; abstract cites **34%** current and **43%** future, not a single consistently defined set.
- **p1 economic loss typo:** prints **$3.8 million** instead of approximately **$3.8 billion** damage/loss supported by Kerala/UN post-disaster materials. This is not the separately estimated $4.4bn recovery-needs amount.
- **pp9–12 hydrological overclaim:** constant sluicing beyond FRL produces unphysical reservoir levels. Therefore 'no matter what approach was taken to opening the dams' and 'inevitable' are stronger than the tested counterfactuals allow.
- **p11 south Kerala flood footprint:** basin inflow increase is not an inundation/exposure/damage simulation.
- **p10 Fig 7 caption:** 'storage rates' whereas axes are stored **volumes (10^9 m³)**.
- **p13 references:** duplicates identical Mishra et al. (2018) source as 2018a/2018b.
- **p12 licence:** Springer published paper is **CC BY 4.0**; verify individual third-party figure credits if republishing.

## Verified source-internal calculations

| Location | Published inputs | Recomputed result |
| --- | --- | --- |
| p9 Idukki | Capacity **1.45e9 m³**, control model peak **2.04e9 m³** | **40.69%** nominal capacity exceedance |
| p9 Idukki | Future RCP8.5 model peak **2.30e9 m³** | **58.62%** nominal capacity exceedance |
| p9 Idukki | 2.30 vs 2.04 e9 m³ | **12.75%** higher peak |
| p9 Idukki | Source surplus **5.89e8** vs **8.52e8 m³** | **44.65%** higher notional surplus |
| p10 | Four-reservoir group | Control **34%**, PI **43%**, RCP8.5 **54%** |
| p11 | Six-reservoir group | Control **37%**, PI **50%**, RCP8.5 **44%** |
| p11 | Northern basin group **26.2→32.7 m³/s** | **24.81%** rise |
| p11 | Middle group **563→745 m³/s** | **32.33%** rise |
| p11 | Southern group **152→302 m³/s** | **98.68%** rise |

These arithmetic checks reproduce the numbers *printed in the paper* and do not validate model simulation inputs or flood impacts.

## Cross-paper synthesis

**HR02 Mishra & Shah (2018)** estimates historical 1951–2017 trends and a remarkable 2018 anomaly using gridded IMD observations and VIC-modelled runoff. **HR03 Hunt & Menon** asks a different conditional attribution question by rerunning the *same 2018 synoptic episode* under alternate climate backgrounds. Their findings do **not** directly conflict because historical mean trend and event-conditioned response are different estimands.

**HR01 Sudheer**, **HR04 Ryan**, **HR05 Singh**, **HR07 Suresh**, and **HR08 Das** address reservoir releases, flood routing, satellite reconstruction or forecast-informed operation. HR03 models *none* of those physical gate policies. Source percentages cannot be ranked as comparable flood damages avoided. The strongest next research direction is measured, conservative, physically capped reservoir water balances integrated with turbine generation constraints and weather/flow forecast uncertainty.

## Derived registers in GitHub

- [14-page individual visual inspection ledger](HR03_14_page_visual_inspection_ledger.csv)
- [32 scientific findings](HR03_2020_scientific_findings.csv)
- [40 source-internal checks](HR03_2020_numerical_evidence_checks.csv)
- [12 prioritized Kerala2040 actions](HR03_2020_Kerala2040_actions.csv)

**Verification boundary:** 14 original source pages inspected visually; original atmospheric/hydro models, flood extent, hydropower generation and published disaster data **not independently reproduced**. Full PDF review and image ZIPs are downloadable in the originating conversation, not in the public repository. The source's CC BY4.0 licence does not make generated evidence independent of physical data.
