# PPAC Kerala full-fiscal-year petroleum sales: source and version audit

**Dated source extraction: 24 September 2026.** [Public-safe six-year source register](../data/evidence/total_energy/ppac_full_fy_kerala_source_audit_2026_09_24.json) · [Total Energy Atlas baseline](KERALA_TOTAL_ENERGY_ATLAS_BASELINE_2026_09_24.md).

**Finding:** Kerala's all-petroleum-product **sales** can be traced over six financial years using original publisher-indexed PPAC reports through FY2023–24 and an identifiable **secondary full-text reproduction of PPAC's FY2024–25 Ready Reckoner**. Neither source category is a verified state final-energy or imports balance. The publisher-original FY2024–25 PDF returns an unsupported binary content-type in this retrieval environment; it has **not** passed original page-image or PDF-byte comparison. All FY2024–25 figures are explicitly **secondary-transcribed, not officially visually verified**, even when the mirror names exact PPAC table and publication.

## Evidence-register table, Kerala, thousand metric tonnes

| FY | All POL products sold | Motor spirit (petrol) | High-speed diesel | Assurance for all-POL total |
|---|---:|---:|---:|---|
| 2019–20 | 6,533.5 | 1,558.8 | **not recovered** | Original PPAC indexed PDF text, unverified image |
| 2020–21 | 5,461.3 | 1,371.1 | 1,922.7 | All-POL original PPAC indexed; product cells newer mirrored edition |
| 2021–22 | 5,901.7 | 1,495.8 | 2,101.1 | Same |
| 2022–23 | 6,879.1 | 1,747.6 | 2,485.6 | Same; prior publication gives a **different** 6,882.6 total |
| 2023–24 | 6,891.7 | 1,791.5 | 2,413.3 | Same |
| 2024–25 | **6,939.7** | **1,879.4** | **2,419.3** | **Exact FY2024–25 publication's third-party text; primary page not verified** |

All-POL **includes** MS/HSD, LPG, ATF, kerosene and other petroleum product classes. MS and HSD in the table are *subsets of* the all-POL total, **not additional tonnes**. The original FY2019–20 HSD category has been left blank, not zero. A publisher's later restatement of FY2022–23 to 6,879.1 from the October 2023 edition's 6,882.6 is a **source-vintage difference**, not an arithmetic inconsistency for us to smooth.

**Sources and precise locators:** [PPAC H1 FY2024–25 Ready Reckoner](https://ppac.gov.in/download.php?file=rep_studies%2F1733114272_Ready+Reckoner_H1_FY+2024-25_Final.pdf), indexed Kerala annual historic row in state-wise total petroleum-products sales Table 6.3(A); [PPAC October 2023 edition](https://ppac.gov.in/uploads/rep_studies/1709718330_ready-recknor-2023_October.pdf), older row and original FY2019–20; [identified FY2024–25 PPAC original](https://ppac.gov.in/download.php?file=rep_studies%2F1751629660_Readt%20_Reckoner_FY_2024_25.pdf), original download blocked for PDF image inspection; [source-identifiable FY2024–25 text mirror](https://www.scribd.com/document/902986775/1751629660-Readt-Reckoner-FY-2024-25), Kerala rows Tables 6.4(A) all-POL, 6.4(B) petrol and 6.4(C) HSD. Re-check source pages and product headings against authoritative bytes before using mirror-only results as regulatory or statistical inputs.

### Scientific interpretation

- **Annual sales** do not prove the same amount of petroleum products was burned in Kerala by Kerala residents. Fuel tanks, intra-/interstate travel, aviation/marine bunkering, refinery-to-distributor movements, industrial petrochemical feedstocks and inventory changes can produce differing *sales versus final-use* boundaries.
- Do not compare FY2024–25 all-POL **thousand tonnes** with EMC FY2019–20 **Mtoe** as if they were the same fuel and time populations. Converting tonnes to energy requires **product-specific lower/net heating values and source period definitions**; inferring a current full energy balance additionally requires sector/captive/feedstock accounting.
- Neither national crude oil import percentage nor one refinery's installed capacity can be assigned to a Kerala **net petroleum-import share** without physical origin/destination and border transfer accounting.
- EMC's FY2019–20 **64% oil share** comes from a *different vintage and final-energy boundary*; it must not be portrayed as an observed FY2024–25 energy mix.
- The initial half-year product entries in the [first atlas register](../data/evidence/total_energy/kerala_total_energy_source_register_2026_09_24.json) remain April–September **2024** only, not an independently derived annual segment. No factor-of-two multiplication or cross-year “completion” is permitted.
- The source PPAC portal [state-wise sales](https://ppac.gov.in/consumption/state-wise) links to additional downloadable data; an authenticated complete original workbook with product legend was not obtained. This study uses a **bounded transcription** instead of pretending access to that file.

## Underlying EMC fuel × sector calculation workbook: result of the search

The public [EMC downloads directory](https://keralaenergy.gov.in/?p=2440) exposes the *report*, but I did **not locate an openly published spreadsheet or appendix with the full fuel × consuming-sector input matrix, conversion factors, monthly/annual allocation and audit corrections*. The report's FY2015 original Figure 3 and Section 3 prose conflict (9.18 vs 9.81 Mtoe) persists. A free-form reconstruction from rounded Figure 4 percentages would manufacture unobserved fuel-specific Mtoe.

**Request the original source tables rather than a new report**, ideally publication-approved aggregated CSV/XLSX containing: fiscal-year ending label, fuel product/code, rural/urban or district if available, final-consuming sector and service, source data institution and revision, calorific lower/net-heating-value factor, reported mass/volume and computed energy, captive-power conversion exclusion, feedstock vs burned fuel, state of sale vs state of final use, primary source checksum and workbook formula/correction of FY2015 discrepancy. Request a data dictionary and release permission. This is a *public or officially shareable academic data request*, never a request for restricted workplace access.

## Complete for this sprint versus remaining evidence

**Delivered:** independently dated original PPAC historical indexed rows, 6 full-FY sales totals, petrol and diesel subset transcriptions with cell-level assurance labels; recorded revision differences; full-year vs first-atlas half-year separation; explicit NULL source cells/undetermined current energy total; a versioned machine-readable register and public interactive plots.

**Remaining gate:** retrieve original PPAC FY2024–25 PDF bytes and visually compare Kerala's complete all-POL, MS, HSD rows and product legend; obtain full-year state×product native XLSX/CSV with published revisions; locate EMC author worksheet/sector allocation and heating-value source; extend from *product sales mass* to source-matched final-use energy only then. No Kerala FY2024–25 Mtoe, fuel import fraction, sectoral final-energy split or emissions calculation is admitted here.
