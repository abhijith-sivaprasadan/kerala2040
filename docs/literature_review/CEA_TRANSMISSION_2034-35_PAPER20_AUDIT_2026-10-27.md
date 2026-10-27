# Paper 20 — CEA Resource Adequacy Plan for Transmission System of Kerala up to 2034–35

**Document:** Central Electricity Authority, Ministry of Power, Government of India, *Resource Adequacy Plan for Transmission System of Kerala up to the year 2034–35*.

**Review completed:** 27 October 2026. **Uploaded source:** 46 pages. **Source SHA-256:** `44367b990cb6eb3a760af40f0235799d055a606b9aa5fd5196642f793bab436c`. Two copies supplied in chat were byte-identical. The report's cover does not specify a publication date; its current-system figures refer to 31 March 2026.

**Review method:** Each of 46 source pages independently rendered at approximately 166 DPI; all opened visually in 23 legible paired-page images at approximately 133 DPI equivalent, with selected critical annex diagrams reopened individually. All pages have individual page records. Review identified **28 scientific/source findings, 35 independent source-internal numerical and evidence checks, and 12 research actions**. Full audit PDF, CSVs and page-image archives were delivered in the conversation; **not included in this Git commit** because of third-party document rights and large image files.

## Why this differs from Paper 1

Paper 1 was CEA's generation resource adequacy plan with a highly aggregated Kerala/rest-of-India transmission boundary. The transmission report separately inventories 220/400 kV Kerala nodes and interstate corridors and reports PSS/E load-flow, N-1 and short-circuit studies. The network map (PDF p12) and evacuation diagrams (pp32–46) offer candidate topology, but they are **not** a machine-readable PSS/E case.

## Reported planning quantities

| Source location | Reported value | Caution |
| --- | ---: | --- |
| p10 | 4,575 MW TTC, 4,455 MW ATC | Existing capability under unspecified snapshot/conditions |
| pp18–19 | FY2029–30 KSEBL peak 7,916 MW | Revised EPS alternative 6,752 MW; difference 1,164 MW (17.24% of EPS) |
| pp18–19 | Available peak resources 5,220 MW; additional imports 2,696 MW | The LGB sums; contracts, import availability and capacity credits require reconciliation |
| pp19–22 | InSTS additions by 2029–30: 8,500 MVA and 492 circuit-km | 3,000 MVA/20 ckm at 400 kV and 5,500 MVA/472 ckm at 220 kV |
| pp21–22 | ISTS additions by 2029–30: 2,500 MVA and 474 circuit-km | Project schedules are not commissioning evidence |
| pp23–24 | FY2034–35 peak 9,780 MW; availability 7,760 MW; extra imports 2,020 MW | Includes fully rated 1,660 MW pumped storage and 800 MW BESS |
| pp25–27 | 2030–35 InSTS 2,560 MVA/1,169 ckm; ISTS 1,000 MVA/280 ckm | Planning quantities, not measured deliverable transfer capability |
| pp28–29 | GEC-II 452 MW/224 ckm/620 MVA; GEC-III 1,759 MW/1,422 ckm/1,973 MVA | Grid evacuation potential and status are not measured power generation |

## Scientific qualifications and corrections

1. **Conditional import/ATC accounting (pp10,18–19):** existing import-related CGS 1,600 + LTA 600 + MTOA 80 + REMC 20 = 2,300 MW. If *all* apply simultaneously as interstate supply, plus 2,696 MW new import implies 4,996 MW, **541 MW above published present ATC**. This is *not* a proved infeasibility; it requires reconciliation of contract categories and future transmission expansion.
2. **Different demand vintages (p18):** selected KSEBL peak is 1,164 MW above revised EPS; demand sensitivity should be reviewed before asserting necessary capacity.
3. **Availability assumptions (pp17–19):** March-night hydro 75%, wind 80%, solar 0% are separately stated, but proposed 120 MW hydro and 300 MW wind are credited at full power in the LGB. Under a *hypothetical* consistent 75%/80% treatment, the listed supply would fall from 5,220 to 5,130 MW, lifting extra imports from 2,696 to 2,786 MW.
4. **Storage firmness (pp19,23–24):** BESS 800 MW and PSP 1,660 MW lack MWh/SOC/duration/charging constraints; full rated MW alone cannot demonstrate multi-hour adequacy.
5. **Independent model results missing (p17):** no PSS/E cases, solved branch flows, bus voltage profiles, contingencies or fault-duty matrices. Named N-1 criterion does not certify every line or case independently.
6. **Source document error (p36):** Chinnar hydro text identifies 11 kV LILO while the same sentence refers to 110 kV cable and the single-line diagram shows 110 kV buses; mark voltage unresolved rather than silently changing the source.
7. **Duplicate constraint (pp14–15):** Areakode 220 kV 160 MVA >60% loading listed twice, rows 8 and 15; deduplicate before counting bottlenecks.
8. **Terminology (p3):** 'Intra-State Transmission System (ISTS)' conflicts with the report's tables using ISTS for inter-state and InSTS for intra-state.
9. **Boundary mismatch (pp5–6,23):** 3,221.30 MW installed excludes separately listed 1,912.33 MW rooftop PV under 1 MW; the pie chart includes it, as does the future solar scenario.
10. **Charts and plan status (pp7–8,31):** unverified causal description of elections/solar flare; intraday 'typical day' not defined; 2026–35 completion dates explicitly subject to re-planning and should not be labelled completed without a dated record.
11. **Annex limitations (pp32–46):** single-line diagrams establish proposed buses and routes but do not establish thermal ratings, delivery under N-1 or actual observed benefits.
12. **Other source qualifications:** constraint entries with 60–80% loading lack explicit thermal/N-1 thresholds, line constraint row 3 lacks remedies/status, compensation data lacks bus placement, and circuit-km vs route-km requires clarification on some annexes.

**Source-internal arithmetic verified:** FY2026 capacity subtotals; 24,497 MVA internal transformation; 10,561.83 InSTS ckm; 4,965 MVA listed ISTS substations; 1,813.87 ISTS ckm; 2029 six hydro project sum 120 MW; 5,220 + 2,696 = 7,916 MW; 2029 6,000+2,500 = 8,500 MVA; 2029 interstate 220+250+4 = 474 ckm; 2034 880 MW hydro + 1,660 MW PSP = 2,540 MW; generation total 11,040 MW; 7,760 + 2,020 = 9,780 MW; 2030–35 2,000+560=2,560 MVA and 19 line rows = 1,169 ckm. Passing arithmetic does not validate PSS/E results.

## Kerala2040 next research gates

- Get case-level CEA/KSEB **topology, line parameters, thermal ratings, transformer ratings, PSS/E base and N-1 outputs** before any detailed physical network adequacy claim.
- Reconcile CGS/LTA/MTOA/REMC, planned extra imports, present vs future ATC and dates.
- Track every major substation/line project's **planned/under construction/commissioned** status using dated primary sources.
- Build a **typed candidate asset list** (MW, MVA, MWh, ckm, route km, voltage, bus, technology, commissioning year) with evidence levels; don't infer unsupported impedances.
- Compare this source with the earlier CEA generation adequacy source under matched demand/weather/hydro/storage assumptions.
- Preserve Kerala2040's public evidence freeze: this adds reference scenarios and topology **not independently reproduced new physical system results**.

See [19-paper synthesis](CROSS_PAPER_SYNTHESIS_2026-10-27.md) and [literature-review programme](NEXT_REVIEW_ROUNDS_2026-10-27.md). This report is **Paper 20 supplement**; the original 19-paper count remains the defined initial corpus.