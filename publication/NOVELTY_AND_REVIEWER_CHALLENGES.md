# Novelty decision, adversarial peer-review questions and study pivot criteria

**27 October 2026 | Draft research governance, not a scientific result or accepted submission**

## Desk-rejection test

A competent energy-data journal editor would reasonably ask:

1. Hunt and Bloomfield already modelled Indian states *including Kerala* with ERA5, XGBoost and SHAP in 2025. **What exactly is new besides choosing a different model or another dataset?**
2. Harish, Singh and Tongia already addressed temperature-related electricity demand across Indian states in 2020. **Are you making an ecological inference or claim of physical cooling demand without identification?**
3. You have a publicly audited FY2024–25 daily dataset but no independently admitted complete multi-year ERA5 source chain. **Is this a source-verified multiyear study, or a one-year model described ambitiously?**
4. The FY2024–25 outcomes have been inspected, and model design may reflect later-year information. **Which reported evaluations are truly untouched; what disclosure prevents retrospective method selection masquerading as registration?**
5. The two series both report daily MU. **Do the original national energy-met and Kerala SLDC operating-consumption variables actually differ in measurement boundary, or is that novelty based on an assumed difference?**
6. The existing 2025 paper's target is detrended/variance-adjusted and our target is original daily MU. **How can you compare scores or model explanations across fundamentally different dependent variables?**
7. Are full-history detrending or weather accumulation/time-zone treatment influencing results? **Can you identify which difference arises from evaluation protocol, transformations, source definition and weather geometry independently?**
8. If all three candidate FYs show little weather gain, **will the manuscript report the negative result and demonstrate why it changes knowledge, or simply move to an unrelated positive ML test?**
9. Are source data shareable enough for the chosen journal's reviewer-access expectations? **Is a no-APC scope-compatible publication venue available if fully OA waiver is denied?**
10. Does the manuscript use 'future prediction', 'causal temperature response', 'observed hourly load', 'load shedding prevented' or 'optimal 2040 mix' outside their measured or proved meaning? **Each unsupported phrase should block submission.**

## Four alternative paper questions (choose one protected contribution)

| Path | Genuine research question | Null that must be reported | Minimal evidence to proceed | Editorial chance before study |
|---|---|---|---|---|
| **A1: boundary + validation comparison** | How do original daily SLDC, national daily energy-met, and year-forward evaluation change weather-associated retrospective inference? | Reporting fields agree within scope and evaluation conclusions are stable or weather adds no transferable value | Both original datasets and source definitions admitted; matched FY tests, fixed baselines and exhaustive errors | Plausible only if comparison changes a broadly relevant reproducibility/inference issue |
| **A2: preprocessing design audit** | Does all-history detrending, source-date redefinition or time-split scheme change benchmark conclusions on original-unit daily demand? | No material difference after reproducing exact author code and data; competing method already reports it | Original Hunt/Bloomfield source and code replicated, mathematically matched estimand, honest author critique | Methodology angle potentially stronger, but danger of unfair comparison and replication effort |
| **A0: source-quality/ontology** | Can an independently checked field/vintage ontology identify non-equivalent electricity measures and quantitatively reproduce correction/coverage errors? | The ontology adds nothing novel beyond normal provider metadata and no important error/mismatch is found | Multi-year qualified original SLDC sources, field manual and comparable external fields, validation sample, source rights | Publication only if transferable methodology and nontrivial audit demonstrated; otherwise technical report |
| **B: hydro/import physical opportunity** | What provable operational flexibility remains under station water and metered interstate transfer limits? | Missing original constraints prevent any credible numeric operational improvement | Authentic 15-min/hourly load, station-unit availability/inflows/storage/releases, actual interchange and physical invariants | Future separate paper; currently blocked, do not raid year-one main manuscript budget |

**Working decision:** A1 + source-faithfulness is the leading scientific hypothesis *conditional on original data*. A2 is one bounded sensitivity/replication experiment, not a criticism of misconduct. A0 is prepared as a genuine alternate contribution and a technical-report route. Paper B remains held behind its June physical data gate.

## Minimal experiments needed to resolve 'novelty'

**E1, original-source accounting:** A paired table of native national daily energy-met and Kerala SLDC daily-consumption source records (same local date, native units, original versions, exact scope). State whether they are definitionally comparable, unavailable or incomparable and why. Do not compute an apparently interesting difference where physical boundaries disagree.

**E2, historical study coverage:** Per-FY counts of (original available, parsed, qualified, comparison field available, weather complete, in both series). Missing documents are not zero demand. If no original weather chain exists, stop and use source-only A0.

**E3, test-estimand isolation:** Same observed target/eligible dates, one fixed Ridge learner calendar-only versus same Ridge + realized ERA5, expanding earlier-to-later FY, both positive and negative RMSE skill. Historical random split/author-model outputs are reported as *separate benchmarks*, not a direct ranking, unless exact preprocessing, split and target are harmonized.

**E4, bound model design exposure:** Write a dated analysis-exposure ledger for F1/F2/F3 before running any new test. No claims of three independent confirmatory folds; obtain genuine untouched future periods only with evidence of analysis lock timing.

**E5, sensitivity:** train-only versus full-history target preprocessing if compatible and source audited; population-weighted vs five-point weather only if original field/method permit. Register sensitivity before inspecting it or label exploratory.

## Decision timeline inside existing 400-hour budget

- **30 Nov 2026:** Identify an honest potentially novel contribution beyond Hunt/Bloomfield with original source definitions and full-access prior art; otherwise redirect WP1 weather-download effort into A0.
- **31 Jan 2027:** finalize Paper A/A0 novelty and locked statistical/source QA choices, with no post-hoc favorable-result selection. Need at least one independent qualified person *invited* to critique; if none accepts, label as no external read obtained.
- **31 Mar 2027:** source availability go/no-go for year-forward ERA5/SLDC weather Paper A; no rescheduling based solely on hoped-for agency replies.
- **30 Jun 2027:** main empirical results or documented null/data-blocker; hydro stays independent and conditional.
- **31 Aug 2027:** final new empirical claims cutoff and complete manuscript/report v1.
- **26 Oct 2027:** verified reproducibility release, honest venue/preprint status and archived source rights, not a forced acceptance.

## A valid negative-result paper would say

'Across admitted financial years and fixed source-qualified daily targets, adding realized same-day reanalysis to the declared calendar model did not produce stable reductions in error. We document precisely which measurement boundaries, seasonal windows, preprocessing and prior-test exposure limit the generalizability of regional weather-associated forecasts. The comparison is retrospective and does not estimate operational day-ahead forecast skill or a causal response to heat.'

**Only write this as a result if the original multi-year source chain is actually admitted and these tests have been performed.** It is a proposed falsification outcome here.

## Publication standards

Reviewer transparency is not the same as submitting every draft to the public internet. Keep restricted source archives out of PRs; publish scripts, definitions, permitted evidence and exact software/data citations. Existing KTH master's education may be included biographically; current affiliation remains independent unless formally employed by KTH. No AI authorship. Any AI-generated research-writing passages and citation metadata remain the human author's responsibility.

**Current state:** literature-level hypothesis shaping only. No physical operation was newly inferred; the public 23 October 2026 evidence freeze stays untouched.
