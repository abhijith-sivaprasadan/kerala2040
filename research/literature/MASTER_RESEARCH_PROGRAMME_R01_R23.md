# Kerala2040 | Literature-gap master programme — Rounds 1–23

**Established 28 October 2026. Planning and discovery record; NOT 23 completed literature reviews, 808 publisher-verified articles, an exhaustive systematic search or 23 promised manuscripts.**

## Executive decision

Kerala2040 now has a **23-round evidence map**: 5 already established thematic workstreams (R1–R5) and 18 additional themed discovery collections (R6–R23). Each round has **20–40 current publication candidates**, one principal falsifiable gap question, explicit minimum original evidence and exclusion boundaries. All 23 appear in the machine-readable [ROUND_ROADMAP_R01_R23.csv](ROUND_ROADMAP_R01_R23.csv).

The programme-wide [MASTER_PAPERS_R01_R23.csv](MASTER_PAPERS_R01_R23.csv) contains **808 publication-candidate rows** (32 + 40 + 25 + 32 + 32 from R1–R5; R6–R21 each 36; R22 35; R23 36). **768 records carry a DOI, representing 766 distinct case-folded DOI identifiers**; **40 R2 scoping titles have no DOI in the version of its PDF available to the atlas** (the earlier Round 2 DOI matrix may have them). The two duplicated DOI identifiers occur in more than one round. Count signifies **database entries, not accepted scholarly evidence, total independent studies or reviewed full texts**.

### Where the bibliographies came from

- **R1**: Existing 44-source critical narrative literature matrix in stacked PR #138; 32 peer-reviewed-type records imported into the master papers chart. 12 other source categories remain only in the original R1 file. The R1 PDF/plan and original evidence boundaries remain unchanged.
- **R2**: The actual 40-paper user-authored scoping PDF, dated 27 October 2026, has been read directly; all 40 titles/years and A/B priorities are reconstructed in [round02_hydro_reference/ROUND2_SCOPING_TITLES_IMPORTED.csv](round02_hydro_reference/ROUND2_SCOPING_TITLES_IMPORTED.csv), *not invented*. This PDF does not expose an easily importable DOI column; **those 40 DOIs are explicitly left blank**, and a reconciliation to the original DOI-bearing source list remains needed. A later individual full-PDF analysis run is underway separately; this atlas does not reset or overwrite its audit statuses.
- **R3**: 25 screened research-paper candidates from draft PR #142; technical report and seven other institutional sources remain in the original R3 matrix, not counted toward 25 scholarly papers.
- **R4**: 32 screened journal candidates from draft PR #143; its distinct 2024 discussion preprint and nine institutional/operator records remain in the original matrix.
- **R5**: 32 screened journal candidates from draft PR #144; the ten regulator/institutional source records remain in the original matrix.
- **R6–R23**: Newly discovered **Semantic Scholar scholarly metadata** as of 28 October 2026, using a small set of documented topical natural-language queries; author/title/year/venue/DOI were supplied by the index, not publisher-by-publisher checked. Each of the 18 files is under `roundNN_<theme>/PAPER_CANDIDATES.csv`. **No new R6–R23 full PDF has been read or peer-reviewed by this work.** The index may include conference, non-peer-reviewed, peripheral or miscoded works; a DOI alone does not confer quality, license or relevance.

### Aggregated outcome — by research pillar

| Pillar | Rounds | Scientific focus |
| --- | --- | --- |
| A. Observability & historical physics | R1, R2, R3, R4 | Demand/weather, reservoir constraints, grid-delivered RE, real outages and restoration |
| B. Decision economics & society | R5, R12, R18 | Tariffs, accounts, market/interstate rules, participation and justice |
| C. End-use transition | R7, R8, R9, R21 | Cooling/building efficiency, e-mobility, process heat, agriculture/cold chain |
| D. Production, storage & resource limits | R6, R10, R11, R14, R15, R22 | Siting/biodiversity, hydrogen, batteries, bioenergy, coastal power, thermal retirement |
| E. Systems interactions and methods | R13, R16, R17, R19, R20, R23 | Digital/control, life-cycle externalities, water utility, climate futures, uncertainty, microgrids |

**Not assigned an automatic new round:** broad generic AI forecasting, solar irradiance modelling without verified electricity outcome, arbitrary hydrogen cost speculation, or extra GIS maps without owner/source access. They are already subordinate methods or scenario opportunities in the proposed rounds.

## Prioritisation, rather than treating all 23 as equal

**A — primary/near-primary scientific gates:** R1 (primary Paper A/A0), R2 (hydro physical data gate), R3 (RE network/source gate), R4 (outage-data gate), R5 (KSEB/KSERC/finance gate), R7 (measured cooling savings), R20 (validity of planning decisions). An A-tier classification expresses likely usefulness, not successful data access or a journal acceptance prediction.

**B — valuable conditional studies:** R6 spatial development feasibility, R8 transport charging, R9 industrial heat, R11 storage aging/circularity, R12 interstate markets, R13 sensing and protection, R16 lifecycle/emissions, R18 institutional legitimacy, R19 climate ensemble uncertainty, R21 agricultural/cold-chain loads, R22 firm generation/fossil transitions, R23 decentralized microgrids.

**C — source-limited or speculative options:** R10 hydrogen/ammonia, R14 waste-to-energy, R15 coastal/offshore/ports, R17 non-hydro water sector. These can move up only if original Kerala-specific data and a genuinely unmet research question materialize.

## Screening design: keep distinct metadata and science

Each source row is assigned independent status flags. Do **not** overwrite these with one ambiguous `reviewed` checkbox.

1. **Discovered** — S2/Crossref/DOI metadata candidate; title and venue not independently publisher validated.
2. **Bibliographically authenticated** — original publisher or Crossref confirmed exact title, authors, DOI, article type/year and non-retraction status.
3. **Title/abstract screened** — one or more explicit round RQ connections, disqualifying overlap and context exclusion recorded. Record source and date.
4. **Full text lawfully acquired** — article version, legal access, original-byte SHA256 and license/owner permissions logged. Access is not review.
5. **Full-text critically appraised** — complete methods, figures, tables, text, supplements where available, source owners, measurement units, bias and counterevidence logged with exact page/section references.
6. **Independent evidence checked** — cited original data/code/reproduction independently accessed and rerun where applicable. Decline this status when not performed.
7. **Kerala transfer/admission judged** — original Kerala observational boundary, physical constraints, time/legal/financial vintage and uncertain transfer explicitly assessed.
8. **Claim promoted** — independently reviewable, correctly classified finding enters a paper/website only under publication-evidence controls.

R1–R5 reflect independent prior screening processes; R6–R23 enter this atlas only at stage **1**. No new source is stage 4–8 by implication.

## Per-round methodology and 20–40 target

1. Before reading, set each round's **PICO/PECO-like focus**: geography, physical/financial target quantity, study methods, observation boundary and exclusion rules (not necessarily clinical PICO).
2. Treat **20–40 as a bounded included candidate range**, not a requirement to fill slots with irrelevant articles. The current 35–36 records in R6–R23 are an *initial over-inclusive discovery set*. During screening, delete/defer peripheral titles and backfill only with evidence-relevant records.
3. Prioritise Kerala and Indian empirical sources; use international studies for transferable **methods** but never import their effect sizes, tariffs or equipment failures to Kerala as observations.
4. Build a DOI-to-title verification ledger; casefold DOI; do not merge a preprint and its peer-reviewed successor without version logic. If the same paper genuinely supports multiple rounds, mark the primary round and secondary citation rather than double-counting unique studies.
5. For each critically appraised paper, extract: record ID, authors/title/DOI/year, original source, model or observation, time/space resolution, measured outcome and units, key method, validation design, error metrics, uncertainty, figures/page references, acknowledged limitations, nearest existing Kerala prior art, whether data/code are accessible, and at most three evidence-qualified design implications.
6. Report null studies and counterexamples, e.g. renewable congestion despite installed capacity, hydro flood-buffer compromises, tariff affordability distributional asymmetry, and uncalibrated energy system optimization.
7. A review round is **not** complete because 20–40 PDFs were downloaded. Require authentic full-text checks and an evidence-gap synthesis. A systematic/PRISMA label requires separate database exports, counts, registration/design and reporting safeguards that are currently absent.

## Research programme capacity and sequencing

The governing Kerala2040 publication plan remains **1 Nov 2026–26 Oct 2027, 10 h/week gross × 50 active weeks = 500 h; 400 committed + 100 contingency**, with **WP0 literature/protocol = 35 h** and a single primary Paper A or A0. It **does not** allocate time to run 23 full literature reviews or author 23 papers.

Recommended execution:
- **Now:** preserve R2 full-paper analysis and do not duplicate it; keep R3 downloaded files privately and ready. This master catalogue is a discovery and planning artefact.
- **Publication-critical 2026–27:** only R1 Paper A/A0's nearest 25–35, with targeted cross-references to R2/R3 where needed for the paper. Source recovery and validation take priority over more bibliographic breadth.
- **Sequential backlog:** R2 → R3 → R4 → R5, as already discussed, subject to actual scientific priority and capacity. Adding a later round should not interrupt the current review.
- **Post-primary-paper triage:** selectively screen R6–R23 by empirical opportunity. No obligation to read all 808.
- **New full-text research project:** reserve an explicit fresh budget and review protocol for the few selected themes; the current plan alone does not fund it.

As a scale check, reading and critically appraising 808 works at a hypothetical **1.5–3 hours per publication** would consume **1,212–2,424 hours**, excluding source verification, synthesis, coding and publication. At 8 planned focused hours per active week, this alone is multiple research years. Those figures are **illustrative planning arithmetic**, not time already spent or a forced research commitment.

## Key deliverable selection: gaps rather than bibliographies

A potential Kerala2040 manuscript or novel result must clear **all**:
- a precise unmet research question not already answered by near prior art;
- original, definitionally consistent Kerala empirical data or a scientifically useful transferable method;
- real testable assumptions, external validation and uncertainty;
- lawful data/code release or credible restricted reviewer-access path;
- a realistic paper type/journal and budget gate;
- a rigorous null-outcome interpretation.

If the relevant source data do not exist, the scientific output is an **observability ledger or transparent evidence atlas** rather than a simulated claim dressed as an observation.

### Citation and copyright rules

- Store DOI/URLs, short bibliographic metadata, original analysis notes and lawful code; **not third-party whole copyrighted PDFs or figures in public GitHub**.
- Use OA links as discovery hints only; inspect owner rights and original bytes before declaring an article full-text reviewed.
- Do not treat current or draft tariffs as legally effective without checking complete original orders and dates.
- Do not promote synthetic Kerala hourly load, actual feeder risk, LOLE, empirical hydro release freedom, measured curtailment, real land development MW or 2040 least-cost investments without original independent evidence.
- Explicitly record generative-AI-assisted literature search/drafting, source-check and human reviewer responsibilities before publication.

## File index

- [ROUND_ROADMAP_R01_R23.csv](ROUND_ROADMAP_R01_R23.csv) — 23 themes, exact current counts, priority, central questions and data gates.
- [MASTER_PAPERS_R01_R23.csv](MASTER_PAPERS_R01_R23.csv) — unified 808 candidate records, DOI pointers and status/provenance.
- [MASTER_CANDIDATES_R06_R23.csv](MASTER_CANDIDATES_R06_R23.csv) — 647 newly discovered paper records and inter-round DOI overlaps.
- [round02_hydro_reference/ROUND2_SCOPING_TITLES_IMPORTED.csv](round02_hydro_reference/ROUND2_SCOPING_TITLES_IMPORTED.csv) — authentic exact 40 paper titles from original user-authored scoping PDF, DOIs intentionally blank.
- `round06_*/...` through `round23_*/...` individual DOI candidate lists — each round's pre-screening bibliographic chart.
- [SOURCE_QUALITY_AND_NEXT_GATES.md](SOURCE_QUALITY_AND_NEXT_GATES.md) — integrity, screening failures, and next actions.

**Scientific status at creation:** an extensive *candidate literature map*, not 23 systematic reviews or 808 fully validated research claims. The 23 October 2026 public evidence freeze and all existing stacked publication PRs remain untouched.
