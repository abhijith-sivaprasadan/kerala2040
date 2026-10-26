# Paper A0 — early fallback prospectus v0.1 (DRAFT)

**Purpose:** make the alternative paper independently testable **before** the 31 March 2027 multiyear ERA5 decision. This is not a disguised negative-result ML paper or a guarantee of journal-level novelty. **Two-page prospectus target by 31 January 2027**, subject to full literature screening and feasible source rights.

## Working title

*What does Kerala's public electricity data actually measure? A reproducible audit of source boundaries, daily-record completeness and cross-publisher comparability.*

## Research problem

Kerala electricity discussions combine annual consumer-side electricity consumption, SLDC operational daily 'consumption', interstate scheduled procurement, actual drawal, observed installed capacity and future scenario load curves. They are **not interchangeable physical quantities**. A source audit can be scientifically useful if it establishes a *generalizable, independently tested methodology* that identifies non-comparable metrics, captures source versions, detects completeness/revision failures, and demonstrates where reconciliation **is and is not valid**.

**Main A0 question:** Can a reusable source-definition and provenance framework reliably classify which Kerala electricity statistics may be reconciled, quantify their original-date coverage and missingness, and demonstrate results that change relative to naïve cross-source comparisons?

**Null:** The framework does not uncover novel substantive source-definition errors or improve independent recoverability beyond existing reporting documentation; deliver a carefully citable **technical report**, not a forced journal claim.

## Proposed original contributions to test, not assert

1. **Machine-checkable ontology** for annual consumer energy sold, SLDC daily reported operational consumption, metered/actual interchange, scheduled drawal, installed capacity and energy-equivalent reservoir stock. Each field binds to product/edition, geography, temporal unit, revision and measurement definition.
2. **Versioned missingness and source quality** across multiple Indian FYs, with qualified vs unqualified SLDC target day, document fetch success, independently reproducible hashes and reasons. Calendar missingness is measured as an absence of source, *not* an observed zero-consumption or outage day.
3. **Cross-publisher admissibility tests**: determine which same-boundary daily/monthly/annual aggregates can be independently cross-checked, and where apparently conflicting annual numbers describe different scopes and must remain separate. Report unresolved cases, not forced matches.
4. **Independent extraction sensitivity**: second implementation or independently checked stratified sample of original source files, disagreement count, transparent adjudication. This is a human-external validation only if an actual outside reviewer performs it; otherwise call it independent-code-path *self-audit*.

## Datasets (data-rights aware)

- Kerala SLDC source-dated operational daily statements (private originals and compressed/hash-checked derived archive; original source rows restricted unless provider allows reuse).
- Kerala State Planning Board *Economic Review 2025*, explicitly *annual consumer-side* electricity consumption.
- SRPC/CEA operational and resource-adequacy sources as available and semantically reconciled, not substituted for SLDC original telemetry.
- Weather source provenance is optional to A0's core dataset-method contribution; multi-year ERA5 may fail independently without defeating A0.
- **No measured hourly or 15-minute statewide Kerala chronology is currently in the public evidence freeze.** Never present proxy hourly curves as measured.

## Study protocol and falsification criteria

**Study unit A:** (publisher, document date, version, field ID, physical boundary and original SHA). **Unit B:** (IST calendar date, SLDC day-file status, qualification status), aggregated to clearly defined financial years. **Unit C:** independently same-boundary comparative fields when such comparators exist.

Before extraction lock:
- Source inventory product IDs, vintage and original-file hashes; revision-selection rule; calendar coverage definition (leap days included).
- Definitions of 'missing', 'unparsable', 'zero energy', 'unqualified', 'duplicate' and 'not publicly observable' as **different** categories.
- At least two independently implemented arithmetic/integrity checks (e.g. daily reported supply/use signed balance; source-document-to-normalized field equivalence).
- Unresolved differences as a **first-class result**; cross-boundary subtractive or ratio comparisons disallowed unless measurement equivalence is independently established.
- A validation table reporting eligible records, sample sizes, source conflicts, field-level unresolved differences and adjudications; every research claim anchored to actual original bytes and provider terminology.
- Reusable approach demonstrated on more than a single cherry-picked document date; demonstrate change across dates, report all exclusions.

## Planned article figures and tables (blank shells, no invented findings)

1. **Figure A0-1 — source ontology**: sources → physical field definitions → admissible/nonadmissible joins.
2. **Figure A0-2 — financial-year day coverage**: observed, unavailable, superseded, parse-invalid, unqualified; no synthetic fills.
3. **Figure A0-3 — mismatch taxonomy**: revisions, units, accounting boundaries, timestamps, legal accessibility, numerical discrepancies; report actual evidence counts when obtained.
4. **Table A0-1 — source lineage**: publisher, product, reporting definition, granularity, geography, full-year eligibility, rights, source SHA.
5. **Table A0-2 — independent check**: predefined sample selection, two implementation results, disagreement, resolution and residual uncertainty.
6. **Table A0-3 — cross-source comparison**: allowed/disallowed equivalences; example values *only* when sources describe same boundary.

## Novelty gate before journal selection

Examine at least ten peer-reviewed data-quality/interoperability, statistical electricity-demand and reproducible-energy modelling papers; compare whether the proposed ontology, versioned coverage flags, independent checks and findings differ from established published practice. Include the Indian state-level weather-demand paper published in 2026 (IEEE Xplore document 11468867), which could undercut an overstated regional novelty claim. A0 **will not** be pitched as a new ML method, a validated energy system model or an official Kerala policy recommendation.

**Journal article decision:** only if the source-audit method/observations yield a transferable, nontrivial and independently supported scholarly contribution. Otherwise publish a rigorously labelled public methods/technical report (with code/manifests and DOI where licences permit). Data journals are not eligible without freely accessible lawful reusable data.

## First milestones and hours (already within WP0/WP1/WP5)

- **November 2026:** establish ontology v0.1, survey the nearest papers, complete this prospectus's study-unit definitions and figure shells.
- **31 January 2027:** sharpen into a two-page submission-concept note with novelty matrix and exact validation sample/rules.
- **31 March 2027:** accept or reject A0 as Paper A fallback on source gates *and* evidence of actual novelty.
- **30 June 2027:** results or documented scientific null and venue-fit assessment.
- **31 August 2027:** manuscript v1 *or* correctly classified technical report, no post-hoc reinterpretation.

**Owner decision still needed:** how far to pursue A0 as a publication if the journal novelty test is weak. Suggested default: a high-quality reproducible technical report rather than an unsuitable or fee-driven journal submission.
