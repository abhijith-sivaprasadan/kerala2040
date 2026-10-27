# Independent methodological review response and risk corrections — 26 October 2026

**Status:** proposed correction protocol responding to a Claude critique of the 29-page Kerala2040 research master plan. Its factual statements concern the research *plan*, not a newly observed Kerala source, accepted journal publication, completed preregistration or independent expert review. It does **not** authorize sending any email or publishing restricted source material.

## Decision record: accept the substantive review and sharpen its weakest point

| Review claim | Adjudication | Required correction / measurable output |
|---|---|---|
| FY2024–25 (F3) is already inspected | **Accepted; even stronger caveat** | F3 is *analysis-exposed*. F1/F2 are chronological retrospective tests, **not automatically pristine confirmation**, because later-year exploration may already have informed feature/model choice. Maintain an exposure register for *all* FYs and model-development decisions. |
| 400 hours has little operational data slack | **Accepted as a scheduling risk** | Existing source-QA code and private SLDC archive mean we are **not building every pipeline from scratch**; nonetheless original ERA5 retrieval/rights are genuine dependencies. An asynchronous agency delay is calendar-time rather than researcher hours: work on permitted data now, track source response separately, and never make a custodian reply a prerequisite to the daily-weather paper. Preserve the 100h contingency but add triggered *scope cuts*. |
| Paper A0 is underdefined | **Accepted** | Write a two-page A0 prospectus, independent data/provenance methods novelty matrix, planned tables, admissibility rules and no-journal fallback **by 31 January 2027**, not only at the 31 March pivot. |
| No named second reader | **Partly correct** | Old charter says to **seek** a methods and Kerala operational reviewer but no specific reviewer is secured. Keep an outreach register of 4–6 prospective qualified readers, conflicts and a no-response fallback. Seek one methods reader and one regional source specialist. Do not falsely claim review happened. |
| Employment could absorb months | **Accepted** | Add 10h, 6h, and 3h/week schedules as *capacity states*; trigger cuts without slipping the 26 October freeze or misrepresenting outputs. |
| APC waiver has no financial fallback | **Accepted** | €0 out-of-pocket remains the base case. By 31 July shortlist at least two scope-compatible venues including one **confirmed** no-APC subscription path if such a journal fits; otherwise use a no-fee preprint/technical report. Springer waiver is requested at **initial submission**, with the separately issued form completed **within 14 days** per publisher. No guarantee of waiver or publication. |
| Keep KTH/AI/red-line science statements unchanged | **Accepted** | Continue to use truthful present affiliation, accurate human authorship, AI-assistance disclosure per journal, source/proxy partition and negative results. |

## R1 — Test-set exposure ledger: correct the inferential vocabulary

**Primary research design remains a retrospective expanding-origin experiment**, where each fold's fitted parameters come exclusively from past target dates. That protects against *within-fold training leakage*, not necessarily analyst research-design leakage.

Mandatory ledger for **F1 FY2022–23**, **F2 FY2023–24**, **F3 FY2024–25**:
- Date range and source vintage, original source receipt/hash and calendar/point coverage.
- Whether those observations, labels, residuals, feature group importances or evaluation metrics were previously inspected at any point in the project.
- Whether post-period information influenced feature definitions, model class, tuning ranges, missingness handling or fold choices.
- Whether data cleaning rules were frozen before inspection (or were amended with written reasons).
- Classification: *retrospective chronological, possibly analysis-exposed* / *analysis-exposed* / *genuinely not yet analysed when protocol locked*. The status is not inferred from chronological split dates alone.

The final Paper A must avoid phrases such as **three independent blind holdouts**, **confirmatory evidence from three folds**, **prospective performance**, or **unseen test years** unless a specific claim is demonstrably true. Treat F1/F2/F3 as **at most three retrospectively chronological fiscal-year evaluations**, with F3 explicitly pre-exposed and all other exposure logged. Three years cannot be assumed statistically independent replications; report between-year heterogeneity and data sensitivity rather than overconfident significance testing.

**Possible stronger validation**, not a promised result: pre-lock a later as-yet-unanalysed eligible period and evaluate *once* with frozen code; consider FY2026–27 (ends 31 March 2027) only if original daily target availability, rights, weather coverage, no development exposure, and the August claim-admission deadline permit. Do not relabel a previously studied year as blind. If no clean prospective case is possible, submit a rigorous **retrospective methods comparison** and keep claims proportionate.

Use *dated retrospective analysis protocol* rather than misleading *prospectively preregistered untouched holdout* to describe existing historical datasets. A legitimately future-independent test could be separately described as prospectively locked.

## R2 — Pre-build the fallback Paper A0 (by January 31, not March 31)

**Provisional alternative question:** Can a versioned and independently checkable source-boundary ontology for Kerala's electricity statistics identify noninterchangeable demand/consumption, import, generation and reservoir reporting quantities, quantify missingness, and permit limited cross-publisher checks without inventing a statewide interval chronology?

A0 is **not automatically journal-worthy**. An inventory of websites, numbers and missing days alone is a valuable technical report but may lack the novel method/result needed for peer review.

Minimum two-page A0 prospectus (WP0/WP1/WP5, not additional annual hours):
1. **Novelty hypothesis**: a reproducible *method* of source vintage, telemetry-field boundaries, fiscal-year calendar alignment, missingness, and independently falsifiable cross-agency QA, transferable beyond Kerala; test it against at least 10 relevant energy-data and reproducibility papers, not only local policy documents.
2. **Original research object**: audited multi-year Kerala SLDC source day catalogue (private raw bytes where rights require), boundary dictionary including annual KSEBL consumer-side and daily operational consumption, date-level original/revision flags and mismatch taxonomy.
3. **Metrics and figures**: per-FY original-source coverage, missingness by calendar/season and publisher, same-boundary reproducible energy consistency checks, mismatches and unresolved cases. Never convert source missingness into zero demand or a measured complete fiscal year.
4. **Validation**: second independent extraction/check on a predeclared sample of records, explicit disagree/adjudicate table; if no second reader, independent code path at a different time documented as *self-check*, not third-party validation. Limit publisher comparisons to equivalent measurement definitions.
5. **Rights**: legal review for releasing derived aggregate data, code and metadata; no raw archive release without licence.
6. **Journal fit test**: specific novelty against similar published methods; **if insufficient, pre-commit to DOI-archived technical report rather than unsuitable paid data journal**.

Milestones:
- **30 November 2026**: A0 title, two-page outline and three candidate genuinely testable data-accounting claims.
- **31 January 2027**: two-page prospectus + figure/table shells + 10-paper novelty matrix.
- **31 March 2027**: unambiguous A vs A0 choice using source availability and journal-method novelty.
- **30 June 2027**: tested A0 results and data-rights ledger if pivot happened.
- **31 August 2027**: full manuscript A or A0, or honest non-journal technical report v1.

## R3 — Source-dependency and employment shock resilience

**Separate labour time from outside calendar latency.** Send agency access requests only with explicit owner authorization; begin original CDS/ERA5 pilot and reproducible daily SLDC work without waiting for replies. Make each outreach an independent ticket with date contacted, reply date, written rights, source status and a fallback to already admissible data. An agency reply is *never* assumed in the baseline research schedule. A delayed request cannot defer the March scientific gate by itself.

**Capacity operating modes (do not retroactively invent hours worked):**
- **NORMAL**: sustainable **10 h/week** with 8h planned + 2h uncommitted reserve; planned annual ceiling 400 focused + 100 contingency. WIP ≤2 (one evidence task, one writing/reproduction task).
- **REDUCED**: sustained **6 h/week** for four weeks (new job/onboarding/family/health demands). Drop WP4 immediately and stop WP3 at documentary source triage. Reduce new complex boosted-tree work; protect original data, simple Ridge and paper writing. Set a *reforecasted* remaining-year budget from actual elapsed hours, never pretend the original 400h remains achievable.
- **MINIMUM / PAUSE**: sustained **≤3 h/week** for four weeks or **≥6 weeks** substantially unavailable. Freeze optional code and Paper B entirely. Use available time only for verified evidence, manuscript/report, and preserved source manifests. Publish a narrower 2027 technical release if journal requirements are unmet. Restart only via a new written task/gate, without moving or relabelling the 2026 evidentiary baseline.
- **EMPLOYMENT SHOCK**: starting a new full-time position triggers a forecast review **within four weeks**; long hours during initial onboarding do *not* create a debt of missed hours that must be repaid through weekend overwork.
- **Freeze**: the **26 October 2027** date becomes a *scope-appropriate public record freeze*, not an artificial complete-paper deadline. The article may remain under review in 2028 or be explicitly not ready. Never reduce scientific acceptance criteria in order to meet a date.

**Sample severe scenario (illustrative, not budget already spent):** if 10 weeks are lost to onboarding and research capacity subsequently falls to 5h/week, a 400-focused-hour research programme is infeasible. Rebaseline remaining *actual* available hours immediately; WP3/WP4 go to 0, not automatically into the statistical model. Announce which scientific deliverable is lost and update the JSON monthly budget with an explicit prospective version.

**Source risks are no longer hidden in general contingency.** At monthly reviews record: time already spent seeking sources, clock days awaiting external reply, hours of verified data/QA work remaining, total remaining capacity, and go/no-go. The **100h buffer remains uncommitted** and may absorb actual failures; it is **not** a required 100h of extra models.

## R4 — Named second-reader recruitment before September

**The manuscript needs an outside pair of eyes; ask early.** The existing plan proposed two methodological critiques but waited until near the end to seek them.

- **November–January:** identify **4–6 real prospective reviewers** with a documented domain (two statistical/ML methods, two power-system/India electricity data, one reproducibility/editorial if possible). Do not label any person as participating without their consent. Favor research mentors, faculty, qualified researchers or operations specialists; no courtesy authorships.
- **By 28 February 2027:** make at least two **individualized** requests for a 30–60-minute review/critique, with consent to share non-confidential outline/methods only.
- **By 31 July:** deliver methods, figure design and source-definitions brief to a confirmed available reader, and request a dated response.
- **August–September:** seek a full-manuscript critique by one competent external reader **before** journal submission. Record what was actually checked and which changes resulted; if none is available, declare external pre-submission review **not obtained**, and complete independent-code-path QA plus transparent self-review. Do not market this as independently reviewed.
- Review by a peer does **not** make a preprint peer-reviewed; only a venue's formal editorial process confers that label.

## R5 — No-surprises APC route before selecting a journal

**Current verified Springer Nature support process (16 October 2026 version):** discretionary open-access waivers are considered for financial need. A waiver interest checkbox/indication in the initial manuscript submission leads to an additional form; the author should **complete that form within 14 days of submission**. Simply checking interest is not the entire waiver request. See https://support.springernature.com/en/support/solutions/articles/6000227580-apc-waivers. The *Energy Informatics* APC is currently €1,240 excluding applicable tax, determined at **acceptance**, not the date of this plan: https://link.springer.com/journal/42162/how-to-publish-with-us.

Publication-fee milestones:
1. **January 2027:** write budget and affiliation truthfully: current plan assumes **€0 personal APC** and **no automatic KTH coverage** for a completed MSc.
2. **31 July 2027:** examine scope and live 2027 author policies of (a) *Energy Informatics* or another suitable fully OA candidate and its initial-submission financial-need waiver process; and (b) **at least one actually scope-matching hybrid journal which permits an author-fee-free subscription route**, if available. **No name is a committed fallback without checking its live model:** some energy journals have switched to fully gold OA.
3. **Before submission:** check whether a partial waiver would still exceed €0 budget; if so, do not commit to an APC. Apply in the prescribed process if selecting Springer; if waived only partially or declined, investigate a *different scientifically appropriate route* in accordance with journal withdrawal/contract rules. Submit to only one journal at a time.
4. **If no affordable and well-fitting venue:** publish a transparent preprint/technical report + versioned code DOI without calling it a peer-reviewed paper. Do not pay a predatory journal, misstate KTH status, or rely on hypothetical third-party funds.

## R6 — New freeze criteria from this review

Before a journal-submission claim, require:
- Exposure classification per FY and clear distinction between retrospective temporal backtests and genuine prospective tests.
- At least one independent reimplementation or source audit, with accurate reviewer attribution; no false claim of an outside reader.
- A/B or A0 decision made from actual data availability and target journal novelty, not March deadline pressure.
- Monthly tracking of *both* actual effort and calendar waiting for source access.
- Explicit capacity/shock mode and scope choice on any reduction in weekly availability.
- Proven venue fit and fee/waiver arrangement before submission.
- Original red-line claims, source rights and truthful current affiliation retained exactly.

**The review makes the plan more robust; it does not add another paper or change the base 400-hour workload.**
