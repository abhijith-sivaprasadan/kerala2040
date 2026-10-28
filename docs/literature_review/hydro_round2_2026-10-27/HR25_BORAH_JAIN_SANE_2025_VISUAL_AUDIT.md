# HR25 — Borah, Jain & Sane (2025): complete 32-page source audit

**Source:** Upasa Borah, Chitrakshi Jain and Renuka Sane (11 March 2025), *Pumped Storage Plants in India: Assessing Policies and Progress*, TrustBridge Rule of Law Foundation working paper. Source URL: https://trustbridge.in/publications/pumped-storage-plants-in-india-assessing-policies-and-progress/

**Scope:** 32/32 original PDF pages individually rendered at 180 DPI, visually inspected through 16 paired-page sheets. Two figures, 15 main tables, three appendix tables, Kaplan–Meier formula, title and policy footnotes examined. User PDF SHA-256: `34baf236c2752dffce3e31a77ce76771e09a9ef9994c509d2dde31a85598c774`. Source snapshot ends **31 December 2024**. Audit completed **28 October 2026**. **36 scientific findings, 50 source-internal checks, 12 actions, 32 source-page entries.**

**Boundary:** Visual and source-internal scientific audit, **not** original CMIE CapEx replication, independent survival-model rerun, up-to-date 2026 CEA inventory, or hydropower dispatch/PSP energy-output simulation. The 16-page full scientific review PDF, source page renders and original-source excerpts are separate conversation artifacts, **not committed to public Git history**.

## Main conclusion

The study is a useful **Indian pumped-storage project implementation-risk benchmark**. It identifies 91 matched/supplemented projects and 130.93 GW of cumulative nominal power capacity, but only six projects (3.31 GW) completed and 17 currently under implementation at the Dec2024 cutoff. A CMIE “Under Implementation” project may still be at ToR or survey stage in the CEA classification. The 6-, 12- and 24-year completion scenarios are deterministic all-eligible-project assumptions, **not statistically estimated delivery probabilities**.

## High-impact arithmetic reconciliation

| Source | Published inputs and issue | Independent source-internal check |
|---|---|---|
| PDF pp10–11 Table3 | 26.69 GW PSP, 47.24 GW BESS, 73.93 GW total; prose says 27% PSP | **26.69/73.93 = 36.10% PSP**; 27% inconsistent |
| p16 Table6 | 59 announced, 2 announced-stalled, 17 implementing, 6 complete, 7 no information | **91 projects**, **130.93 GW** total (incl 3.31 GW completed) |
| p21 Table9 | 1,251,450 public + 4,973,734 private shown as “Rs. trillion” | Sum **6,225,184** in raw units; **if** unit is INR million: **INR 6.225184 trillion**; source unit unresolved |
| p22 Table10 | Prose seven from 2011–2020, table eight | **8** in table; total historical ever implemented **23** incl six complete |
| pp22–23 Table11 | Prose mean and median 1.1 and 1.8 years | Table shows **mean 2.16; median 1.08 years** |
| p23 Table12 | Six completed units and time to build | Capacities sum **3.31 GW**, mean completion **13.14yr**, median **15.04yr** |
| p24 Table13 | 2032 6-year = 107.64 GW, 12-year = 21.36 GW, 24-year = 0 GW | Hypothetical **new** addition; if 3.31 already operational added, 12-year yields **24.67GW** vs national **26.69GW** installed target, conditional **2.02GW** shortfall |
| pp18,28,32 | Table15 “Others” completion 32.72%, Table8 total981, Appendix completed137 censored330 | **137/981=13.97%**, **137/467=29.34%**; printed 32.72% unsupported by either denominator |
| pp18,32 | Appendix survival population vs Table8 group | Missing **126 hydro,72 solar,33 wind,514 Others**; eligibility filters not shown |

## Scientific findings

| ID | Priority | Source PDF pages | Finding | Corrective action |
|---|---|---|---|---|
| F01 | Critical | 10-11 | 2031-32 PSP share: published 27%; actual 26.69/73.93=36.10% | Correct denominator and figure |
| F02 | Critical | 21 | Table9 investment column is labelled Rs trillion but values 1251450 and 4973734 | Check original units; likely Rs million |
| F03 | High | 22-23 | Prose mean/median 1.1 and 1.8 yrs; Table11 pooled mean 2.16 median 1.08 | Verify raw implementation dates |
| F04 | High | 22 | 2011-2020 implemented: Table10 eight versus prose seven | Use table provisionally |
| F05 | Critical | 28,32 | Others completion 32.72% but 137/981=13.97% or 137/467=29.34% | Reconcile group population |
| F06 | High | 18,32 | Survival rows omit 126 hydro 72 solar 33 wind 514 Others relative to Table8 | Disclose exclusions and eligibility |
| F07 | High | 27-31 | Stalled/no-information treated as censored despite potentially informative noncompletion | Competing risks sensitivity |
| F08 | High | 28 | Statistical significance asserted without p-value confidence bands or test output | Publish test statistics |
| F09 | High | 24-25 | 6/12/24-year all-complete capacity scenarios are deterministic ceilings not probabilities | Use stochastic completion |
| F10 | High | 16-17,30 | CMIE Under Implementation includes LoI and approvals while CEA remains ToR or survey | Split project phases |
| F11 | High | 16-17 | 156 initial keyword records but only 89 CEA matches and 2 supplemented; unmatched not explained | Reconcile exclusions |
| F12 | High | 16-17 | CEA eight operating including two dysfunctional vs CMIE four complete and two added | Version and reconcile operating units |
| F13 | High | 16 | 130.93GW includes nonimplemented and completed projects; 127.62GW excludes only completed | Use risk-weighted stage capacity |
| F14 | Medium | 2,16,21 | 102GW private headline not broken down by owner-and-stage capacity in supplied tables | Obtain source MW crosswalk |
| F15 | High | 21 | Public cost share 20% versus count share 34% cannot alone establish smaller MW/project | Show ownership capacities |
| F16 | High | 11,24-25 | CEA installed capacity stock and Table13 candidate additions compared without bridging existing capacity | Stock-flow reconciliation |
| F17 | Medium | 23-25 | Six completed PSPs do not provide representative delivery duration for recent vintages | Age-conditional modeling |
| F18 | Medium | 23 | Six recorded durations mean 13.14yr median 15.04yr | Historical completed-only comparison |
| F19 | Medium | 23 | Table11 N21 excludes two of 23 ever implemented projects for missing dates | Make missingness transparent |
| F20 | Medium | 22 | Projects identified since 2019 have limited follow-up through Dec2024 | Right censor by vintage |
| F21 | Medium | 28 | Hydro vs solar vs wind differ in size geography policy and age | Adjusted comparisons needed |
| F22 | High | 31 | Initiation/date-origin and last-update censoring rules not fully specified | Version project event dates |
| F23 | Medium | 31 | Shelved/abandoned competing events not addressed as outcomes in KM description | Competing-risk states |
| F24 | Medium | 19-20 | Figure2 state map does not furnish named Kerala scheme register | State inventory needed |
| F25 | Medium | 8-13 | Policies through August2024 do not establish legal settings in late2026 | Current verification |
| F26 | Medium | 9 | ESO 1-4% is on energy-consumption basis not installed GW | No power capacity conversion |
| F27 | High | 4,11 | PSP power GW without stored GWh duration or roundtrip efficiency | Model usable energy |
| F28 | High | 24-25 | No grid dispatch transmission limits or price/revenue validation | Separate execution and system value |
| F29 | Medium | 26 | 1250 months sum among twelve delayed CPSU schemes not individual PSP representative delay | Use project-specific timelines |
| F30 | Medium | 26,31 | Project delay causes gathered from mixed secondary reporting | Triangulate administrative evidence |
| F31 | Medium | 12-13 | DPR concurrence deadlines are policy timelines not realised commissioning times | Approval-event time series |
| F32 | High | 21 | Rs6.2tn announced plans and 55 recent private entries are not committed financing | Track financial close |
| F33 | Medium | 24-25 | 2032 twelve-year 21.36 new plus 3.31 existing yields 24.67 vs 26.69 target | Conditional shortfall 2.02GW |
| F34 | High | 16-17,30 | No estimated probability of ToR-to-DPR-to-build-to-operation transitions | Stage hazards and competing risks |
| F35 | Medium | 21,30-31 | Environmental land litigation and social obligations not operationalized | Feasibility restrictions |
| F36 | Medium | 1-32 | March2025 working paper with Dec2024 snapshot is not current CEA register | Date-tag all inputs |

## Interdependency with Kerala2040 research

Previous HR01–HR08 studies concern Kerala flood/dam hydrology and HR37 is a global conceptual water–power resilience framework. HR25 supplies **project stage, financing and execution risk**, not a Kerala hydrological operating curve or actual PSP dispatch. For the Kerala2040 model, stage-weighted commissioning dates and probabilities should gate inclusion of any future PSP plant; physical constraints require upper/lower reservoirs, active usable storage (GWh), plant MW, round-trip efficiency, charging-power source, operating rules and transmission deliverability. Announced GW is **not** a firm 2040 energy resource.

## Evidence datasets committed

- [32-page visual ledger](HR25_32_page_visual_inspection_ledger.csv)
- [36 source-scientific findings](HR25_2025_scientific_findings.csv)
- [50 source/evidence checks](HR25_2025_numerical_evidence_checks.csv)
- [12 prioritized Kerala2040 actions](HR25_2025_Kerala2040_actions.csv)

**Source rights:** The uploaded TrustBridge working paper did not establish an explicit open reuse licence. The original PDF and full-page image archives are **not** in the public repository. Source classifications and policy facts are dated; obtain later CEA and state records before using them as current policy statements.
