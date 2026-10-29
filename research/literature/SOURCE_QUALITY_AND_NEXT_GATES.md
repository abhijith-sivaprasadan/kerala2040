# Master literature atlas — machine QA and evidence eligibility

**As-of:** 28 October 2026. This file is a programme integrity audit, **not** a human verification of all indexed paper identities or publisher DOI metadata.

## Machine checks performed on combined CSV

- Candidate rows: **808** across **23** rounds.
- Rows with a DOI: **768**.
- Unique case-insensitive DOI identifiers: **766**.
- Missing DOI: **40**; all imported from Round 2 titles in the user-authored scoping PDF. These are **not** proof that no DOI exists for those works.
- DOI syntax invalid: **0**.
- DOI strings found in multiple paper rows: **2** distinct DOI.
- Rounds with paper candidates outside 20–40 range: **0**.
- *DOI string identity* is not *publication identity*. Separate preprint/publisher versions, title variants, corrigenda, and identical studies reissued require original verification.

### Candidate counts by round

| Round | Candidate records |
| --- | ---: |
| R1 | 32 |
| R2 | 40 |
| R3 | 25 |
| R4 | 32 |
| R5 | 32 |
| R6 | 36 |
| R7 | 36 |
| R8 | 36 |
| R9 | 36 |
| R10 | 36 |
| R11 | 36 |
| R12 | 36 |
| R13 | 36 |
| R14 | 36 |
| R15 | 36 |
| R16 | 36 |
| R17 | 36 |
| R18 | 36 |
| R19 | 36 |
| R20 | 36 |
| R21 | 36 |
| R22 | 35 |
| R23 | 36 |

### Repeat DOI cases

- [10.1002/aenm.202200383](https://doi.org/10.1002/aenm.202200383) appears in rounds 8 and 11. Keep one unique-study reference and annotate legitimate secondary thematic use.
- [10.1088/1748-9326/ad472a](https://doi.org/10.1088/1748-9326/ad472a) appears in rounds 16 and 22. Keep one unique-study reference and annotate legitimate secondary thematic use.

## Four important source-quality uncertainties

1. **Broad search false positives:** R6–R23 were selected by keyword searches and automated title ranking. Some entries have only peripheral connection to the narrow research question, e.g. outdoor thermal comfort without energy-demand measurement, general environmental macroeconomic papers without power-plant boundaries, or wastewater chemistry with no measured electricity consumption. They **must be manually excluded or reclassified** before any paper is called *included* in a formal review. Do not pad a 20-paper target with irrelevant sources.
2. **Article type and publisher metadata:** Semantic Scholar supplies title/DOI/year/venue but may aggregate working papers, conferences, books or preprints, and those classifications were **not individually verified** in R6–R23. Check publisher/Crossref record, article type, publication and online date, retractions/corrections, and the DOI landing page.
3. **Full-text state:** The master R6–R23 `oa_pdf_candidate` URL is an index hint, not an acquired source hash or a legal/publication permission certificate. **Zero new complete-pdf appraisals** have been performed in those 18 rounds.
4. **Round 2 version reconciliation:** The 40 titles were recovered from *Kerala2040_Round2_Hydropower_40_Paper_Scoping_Synthesis.pdf* (27 Oct 2026) and are accurate as a source-title index. The PDF is not the original full DOI-bearing CSV. The separately ongoing Round 2 full-paper review must remain the source of truth for DOI, full-text progress and page-based critical appraisals.

## Required repair/backfill before any R6–R23 round is called screened

- Check all DOI links against original publisher pages or authoritative DOI metadata.
- Run title-and-abstract relevance adjudication, mark `include`, `exclude` or `defer`, and state a reason. Start by reviewing the top ~10 selected records of each round, then apply exclusion families to the whole list.
- Audit at least one **counterexample** and one high-quality **India/Kerala empirical work** for each round, rather than relying entirely on simulation literature.
- Resolve duplicated/versioned studies across all 23 rounds; keep secondary-topic references but avoid double counting.
- Distinguish source-reported original observations, model scenarios, policies and surveys. State temporal/spatial validity, meter and financial boundary.
- Track actual full-text dates and source SHA, source/data redistribution rights, key figures, uncertainty and limitations. `downloaded` never auto-sets `reviewed`.
- Report excluded-article counts. No claim of systematic PRISMA review absent database export, a comprehensive query log and independent/reporting controls.

## First real publication gate

The source-audited Kerala daily consumption/weather Paper A or fallback A0 remains the **one primary manuscript** under the 400-hour 2026–27 research budget. The master candidate literature atlas must not be treated as approval of extra empirical claims, extra manuscripts, unverified physical constraints or a new 2027 deliverable. Selection of any other research programme should be a separate explicit post-evidence budget and novelty decision.

**QA result:** machine-readable candidate index passes structural row/count/syntax checks; **human topic relevance, publication authenticity and full-paper scientific validity remain open**.
