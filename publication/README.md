# Scientific publication workspace — Kerala2040

**Working branch:** publication/literature-review-2026  
**Upstream:** research/paper-a-november-kickoff-20261026 (PR #136)  
**Proposed integration:** stacked review PR into the research branch first; after peer/source review, merge the earlier research PRs into main. The existing 23 October 2026 public evidence freeze remains unchanged.

This is a **dedicated working area inside the scientific project**, not a separate research institution, a new data source or an independent journal paper. Keeping the review adjacent to the original SLDC/ERA5 repository means readers can trace experiment decisions, versioned code and source-quality gates. A second GitHub repository would create unnecessary citation and provenance fragmentation while Paper A and A0 depend on the same source archive.

## Primary working documents

- **[Completed critical literature synthesis, v1.0 (27 Oct 2026)](literature/CRITICAL_LITERATURE_REVIEW_2026-10-27.md):** integrated six-question narrative, direct empirical competitors, original field definitions, methodological validity, ERA5 physical semantics and publication novelty decision. **Structured critical narrative; not systematic, PRISMA, an original empirical study or journal-reviewed.**
- [Earlier synthesis v0.1](literature/CRITICAL_LITERATURE_REVIEW_V0_1.md): historical ~6,600-word working review retained transparently for its detailed intermediate analysis; do not confuse this draft with the consolidated v1.0.
- [Twenty closest-source appraisals](literature/CLOSEST_STUDIES_CRITICAL_APPRAISALS.md): paper-by-paper source-level details with actual full-text/abstract/code access classification, evidence limits, and falsifiable study consequences.
- [Manuscript introduction and background draft](literature/MANUSCRIPT_INTRODUCTION_BACKGROUND_DRAFT.md): journal-style source-graded text with explicit gaps and placeholder results; not an accepted paper.
- [Curated evidence matrix](literature/EVIDENCE_MATRIX.csv): 44 records classified by exact DOI, peer-review status, source access, overlap and consequence. **44 records does not equal 44 full-text reviewed articles.**
- [Review protocol and search log](literature/REVIEW_PROTOCOL_AND_SEARCH_LOG.md): search terms, access/bias vocabulary, current methodological limitations and November/January audit commitments.
- [Novelty and reviewer-challenge decision brief](NOVELTY_AND_REVIEWER_CHALLENGES.md): separates legitimate new hypotheses from prior claims and desk-rejection risks.
- [BibTeX references](literature/verified_core_references.bib): initial bibliographic entries. All seven formerly provisional author-name records in the 44-record matrix were crosschecked against publisher or university information on 27 October; final formatted full names and metadata still require author-level proofreading.
- [Matrix validator](literature/validate.py): standard-library consistency checks; **not a substitute for source reading or DOI resolution**.

Related research-study files already on the upstream branch:
- Paper A draft protocol: studies/paper-a-2027/PROTOCOL_DRAFT_v0_1.md.
- Analytical exposure + source gate: studies/paper-a-2027/EXPOSURE_AND_SOURCE_REGISTER.md.
- Paper A0 alternative prospectus: studies/paper-a-2027/PAPER_A0_PROSPECTUS_DRAFT.md.
- Closest prior-art code/methods review: studies/paper-a-2027/HUNT_BLOOMFIELD_PRIOR_ART_REVIEW_2026-10-27.md.

## Scientific temperament is a workflow, not a brand

1. **Do not hunt only supporting citations.** For every proposed claim, identify its strongest existing competitor and a source-based way it could be wrong.
2. **Keep three statuses separate:** published literature findings, authenticated Kerala2040 observational facts, and planned but unexecuted experiments.
3. **No retroactive blind tests.** Prior FY2024–25 exploration must be disclosed; F1 and F2 also need a separate analyst-exposure audit.
4. **Report null/negative findings** and unsuitable source comparisons. Never move the primary target/metrics after seeing favourable values.
5. **Preserve original source chains, data rights and researcher accountability.** A GitHub commit, CI pass or Zenodo DOI is not independent peer review.
6. **Separate journal submissions from the research freeze.** A complete and transparent technical report is preferable to a rushed under-evidenced journal article.

## Minimum paper publishability gate

Paper A may advance only if (a) authentic daily source data and original weather are admitted; (b) the observed-variable comparison to prior state-level Grid-India work is physically and temporally coherent; (c) chronological versus random-split and preprocessing sensitivity constitutes an independently testable, actually novel question; (d) all negative FY tests and source exclusions are reported; (e) a qualified independent reader has been requested and all received criticisms are logged.

If this gate fails, prioritize A0's own source-accounting novelty test (not a replacement title with the same unsupported weather content). If neither manuscript demonstrates scientific novelty, release a labelled public technical study and limitations ledger, not a fabricated peer-reviewed result.

## How to use the workspace

Run the static check on a local clone:

    python publication/literature/validate.py

Review matrix references in a spreadsheet if useful; keep CSV under Git version control. Attach a reading note or correction for any newly acquired full text, update access grade, and amend the synthesis only with a cited reason. Track all actual literature work hours under WP0/WP5. The existing 400-hour annual programme is still the resource ceiling.

**Nov 30 2026:** evidence-backed Paper A novelty decision, with original Hunt/Bloomfield dataset and SLDC field availability recorded. **Jan 31 2027:** bibliographic metadata, critical closest-paper reads and methods protocol review. **Aug 31 2027:** source/claim admission cutoff. **Oct 26 2027:** scope-appropriate freeze.

## Clear current limitations

The v1.0 synthesis and its preserved v0.1 predecessor include official summaries and abstract-screened records; a source's place in the matrix is not evidence that its original complete full text has been reviewed. It has not run the authors' open models, retrieved all original public benchmark CSV bytes, inspected all CSTEP/CEA technical appendices, or independently verified all SLDC original private rows. It must not be presented as a systematic review with complete search hit counts.

**Publication identity:** Independent Researcher. Completed KTH MSc is education history, not a claim of current university appointment. AI-assisted research drafting must be substantively verified by the human author and disclosed according to the venue.
