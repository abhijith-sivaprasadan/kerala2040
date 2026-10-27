# Review protocol and evidence search log — 27 October 2026

**Project:** Kerala2040 | **Document status:** structured critical narrative review, **v1.0 synthesis complete as an explicitly non-systematic review (27 October 2026)**. It is not an exhaustive review, a completed PRISMA-ScR exercise, an independent dual-screened corpus, or an approved peer-reviewed manuscript.

## Purpose

The review exists to decide whether Paper A (source-verified Kerala daily SLDC demand × ERA5 chronological evaluation) is original relative to directly competing Indian-state weather studies, or whether Paper A0 (source quality / operational-accounting comparability) is a stronger paper. It additionally bounds hydro/import research and journal claims.

## Questions

- LRQ1: What already-published Kerala/Indian-state daily demand/weather studies, methods, data and public results threaten the proposed novelty?
- LRQ2: Are Kerala SLDC operating consumption, Grid-India energy met, annual KSEBL consumer sales, actual imports and power schedules independently equivalent variables?
- LRQ3: How do chronological tests, researcher exposure, target preprocessing and operational-vs-retrospective weather change the estimand?
- LRQ4: How must original ERA5 hourly/accumulated data be interpreted when building complete IST daily features?
- LRQ5: What hydro, resource adequacy and 2040 transition work already exists; what original constraints are required to go beyond it?
- LRQ6: Which defensible finding maps to Paper A, A0 or a technical report?

## Search design and status

**Current design:** targeted iterative searching of scholarly/publisher, university repository, DOI, government, and original software/source locations. Access ranges from full publisher HTML and public code to abstract-only and official summaries; exact status is recorded per item in EVIDENCE_MATRIX.csv. Initial 44 curated records do NOT imply all 44 full texts were read.

**Initial search queries on 27 October 2026:** 
1. Indian states electricity demand weather ERA5 XGBoost Hunt Bloomfield; Kerala electricity weather SHAP climate.
2. Harish Singh Tongia electricity temperature Delhi states cooling; Indian residential AC electricity field studies; Babu Banerjee 2026 demand cooling EV.
3. Electricity load forecasting systematic review; chronological evaluation rolling-origin; time series researcher leakage; metrics and baselines.
4. ERA5 reanalysis hourly timestamp accumulation IST daily source documentation; bias-adjusted WFDE5.
5. CSTEP Kerala Energy Transition Roadmap 2040; CEA Kerala Resource Adequacy Plan 2035-36; WRI Kerala 2040 transition 2026.
6. Hydropower flexibility water-energy physical constraints short-term scheduling systematic review.
7. Open science in energy models; PRISMA-ScR; PRISMA 2020.

**Search-system limitation:** Public web search and publisher pages were used, rather than systematic Scopus/Web of Science exports. This run does not preserve an exhaustive hit count, excluded-result log, independent dual screening or reproducible PRISMA flow denominator. Do not invent one. User-sponsored paywall access and original PDF/method coverage are not assumed.

**Expansion protocol:** before January freeze, save exact database name, query, run date, search filter, results export if permitted, dedupe rule and exclusion reasons. Forward/backward chase citations of the 15 closest references. Flag papers not fully accessible and avoid study-specific method claims not seen in text. Label an actual scoping review as such only if procedures justify PRISMA-ScR standards (Tricco et al. 2018, DOI 10.7326/M18-0850). Reference Page et al. 2021 PRISMA 2020 only when genuinely undertaking a systematic evidence synthesis.

## Scope and relevance

**Include:** peer-reviewed demand and climate studies explicitly using Indian or Kerala observations; methodological work on temporal validation and weather provenance; rights/provenance-focused open energy research; peer-reviewed hydro operational-constraint studies; essential official Kerala and Indian system studies as context, not as peer reviewed papers.

**Prioritize:** exact Kerala overlap > India states > measurement-boundary comparability > time-series validity > ERA5 source integrity > hydro physical constraints > 2040 planning context.

**Do not silently promote:** a journal's abstract to full-methods inspection; a publisher DOI to file-byte validation; code existence to independent replication; official simulation to measured actual demand; a source-date report count to qualified daily target count.

## Matrix extraction standard

The matrix fields are: id; theme; authors; year; exact title; DOI if verified; source type (peer-reviewed vs institutional/provider); level of evidence personally accessed; relevance to Kerala2040; source contribution; concrete implication for our design.

For every top-priority full-text review add: study unit/field, data custodian, target definition, geography, date range, weather source and weighting, evaluation protocol, data preprocessing order, leakage and exposure concerns, baselines, metrics, code/data licence, comparator novelty challenge, limitations and an exact section/table where verified. Write unknown when unknown.

**Bias review flags:** (B1) non-equivalent targets; (B2) full-sample normalization/detrending pre-split; (B3) random split sold as forward forecasting; (B4) realized reanalysis sold as forecast; (B5) missing dates filled or omitted without accounting; (B6) untested weather spatial weighting; (B7) ecological correlation sold as causal heat effect; (B8) inappropriate data rights; (B9) physical dispatch inferred without actual plant/water/transfer constraints; (B10) established results pitched as first-ever novelty.

Each B flag must be evidenced, plausible, unknown or not applicable, with exact citation/code for anything called evidenced. Do not calculate a fabricated quality index.

## Initial screening audit

- **27 October 2026 / direct prior art:** Hunt & Bloomfield 2025 full text excerpts and released public training-code paths were reviewed in the earlier working research branch. Harish, Singh & Tongia 2020 and Porwal et al. 2026 were verified from publisher abstracts; the latter's complete article remains unavailable.
- **27 October 2026 / methodological studies:** Cerqueira et al., Roberts et al., Hyndman & Koehler, and load forecasting reviews were located; access varies by item (matrix).
- **27 October 2026 / ERA5:** Hersbach, Cucchi et al., ECMWF temporal/aggregation documentation were located; exact source-data applicability still depends on local bytes.
- **27 October 2026 / hydropower:** the 2026 coupled water-power systematic review and 2025 hydropower flexibility paper were located at publishers; Kerala operating parameters remain unknown.
- **27 October 2026 / official Kerala context:** CSTEP 2024, CEA Kerala RA 2025, WRI India Sep 2026, SLDC and State Planning Board sources were catalogued; official web summary is not a complete methods review.

**Current corpus:** 44 selected records, of which 32 are coded as peer-reviewed research/reviews (including some conference and data/software papers), plus government/institutional, weather product and method standards. Those counts describe what is in the curated matrix only, not an exhaustive published-literature sample.

## Publication gates from the review

**By 30 November 2026:** demonstrate novelty beyond the actual Hunt & Bloomfield Kerala-specific ERA5/XGBoost/SHAP paper; define original SLDC vs Grid-India metering boundaries and a defensible independent validation contrast. Obtain actual public benchmark files and original private-source hashes where access and rights permit. If novelty does not survive, pivot paper selection to A0 rather than increasing model complexity.

**By 31 January 2027:** maintain a screened 25–35+ focused bibliography, 15 closest-paper critical text comparisons, accurate reference file and prospective decision protocol. Do not arbitrarily count a paper as critically read because its abstract was opened.

**By March 31:** Paper A source feasibility gate remains binding. Neither models nor publication status are advanced in this literature branch; the October 2026 public research freeze remains intact.

**Review status:** research-planning material written with AI assistance and requiring human verification of paper metadata, science and citations before journal submission.


## New owner-provided complete PDFs — 27 October 2026

After v1.0 release, the study owner supplied publisher-layout PDFs of **D02 Harish et al. (2020), Energy Policy, 14 pages** and **D04 Babu et al. (2026), Applied Energy, 18 pages**. Both are now critically appraised in [the exact-source appraisal](FULLTEXT_D02_D04_APPRAISAL_2026-10-27.md) with original file hashes, observed-source definitions, figures/tables, model limitations and admission status. Source-matrix `access_level` was upgraded **only for these two records** from abstract to `owner_supplied_full_publisher_pdf_*_critically_reviewed`. Other abstract-only entries, particularly **D03 Porwal (2026)**, remain unchanged. No independent original numerical replication or Babu supplementary table acquisition is implied.

Primary novelty clarification: Harish Appendix Table A3 already publishes a **Kerala** 2009–13 temperature response (n=1,737); Babu p. 4 explicitly documents **actual GRID-INDIA state hourly 2021–23 source data** used as 2023 base templates for **simulated** future hourly load. These are documentary leads—not newly acquired Kerala2040 measured interval data. Add Grid-India/NLDC official custodian enquiries only with user authorisation; distinguish 5-minute historical measurements from hourly forecast/downscaled curves. 

## Version 1.0 review completion and integrity audit — 27 October 2026

This record preserves the honest distinction between **completion of the commissioned critical narrative-review deliverable** and **completion of full-text review for every possible relevant paper**. The source evidence is usable as a careful publication background, **not** a systematic evidence synthesis, or proof of Paper A's novelty.

**Delivered files:**
1. [CRITICAL_LITERATURE_REVIEW_2026-10-27.md](CRITICAL_LITERATURE_REVIEW_2026-10-27.md): integrated six-question narrative, contested originality, original-unit comparisons, methodological/physical/data-rights constraints and A/A0 gates.
2. [CLOSEST_STUDIES_CRITICAL_APPRAISALS.md](CLOSEST_STUDIES_CRITICAL_APPRAISALS.md): twenty high-priority source-specific notes with exact access limits, inference, gaps and action items. Not described as twenty fully obtained papers.
3. [MANUSCRIPT_INTRODUCTION_BACKGROUND_DRAFT.md](MANUSCRIPT_INTRODUCTION_BACKGROUND_DRAFT.md): manuscript-compatible narrative argument with final-research-only claim placeholders and citations to verify.
4. [EVIDENCE_MATRIX.csv](EVIDENCE_MATRIX.csv): the 44-row structured corpus with per-paper source type, actual access level, DOI, relevance and methods/design consequence; seven previously unverified author entries have now been checked against publisher or university metadata.
5. The earlier [Hunt & Bloomfield prior-art memo](../../studies/paper-a-2027/HUNT_BLOOMFIELD_PRIOR_ART_REVIEW_2026-10-27.md) continues to document code inspection, random-split and detrending distinctions, dataset-version publication metadata and unresolved accession.

**Matrix-format QA verified:** precisely 44 data records, exactly 11 declared fields per row, unique \`id\` values, 32 \`peer_reviewed*\` classification rows (including scholarly journal articles, one conference record, data and software papers), no missing DOI among those 32. The remaining 12 include three methodology guidance items as well as government/institutional, product and primary-operational source descriptions. These are **classification counts of a manually chosen corpus**, not systematic-search flow numbers. All seven old \`authors_to_verify\` placeholders were replaced from externally retrievable primary metadata; a final bibliography human metadata cross-check remains required.

**Access-level caveat:** exactly one direct comparator row includes inspected research code; many rows remain abstract, bibliographic or official-summary grades. Do not reclassify a source as full-text-inspected merely because this narrative review discusses its abstract or because someone else previously summarized it. Two major direct comparators are still not reproduced, and Porwal's conference manuscript was not accessible beyond its abstract.

**Newly clarified scientific issue:** later-year chronology, full-dataset target detrending and researcher exposure are separate dimensions. Hunt/Bloomfield's published Kerala R² is not a common-unit comparison; even a correct original Kerala daily demand study will require *matching original source, period, transformed vs untransformed target, and estimand* before asserting numerical superiority.

**Open research actions** that cannot honestly be marked 'complete literature findings': (a) obtain original Hunt/Bloomfield Zenodo files and check publisher hashes/rows; (b) obtain Porwal full article; (c) verify exact private original SLDC archive and actual historical ERA5 source bytes; (d) run source-boundary and strict year-forward matched experimental replication; (e) have a separate qualified human reader inspect the final manuscript. Those tasks belong in the scientific execution programme, not the description of this literature synthesis.

**Scope of final review:** citations and methodological assertions from publisher source body where accessible; explicit access grading for every other item. No invented PRISMA search denominators, dual screening, independent reanalysis, journal submission, acceptance, causal result or verified Kerala source data were added.
