# Kerala2040 — journal publication, peer review and open-research pathway (2026–27)

**Status:** journal-selection and submission plan, **not** an article acceptance, journal endorsement, editor invitation, data-access permission or final venue choice.  
**Prepared:** 26 October 2026 · **Time cap:** protected 110-hour WP5 within the 400-focused-hour annual research programme.  
**Linked programme:** [research charter](RESEARCH_PROGRAMME_2026_2027_DRAFT.md) · [budget](RESEARCH_PROGRAMME_2026_2027_BUDGET.json) · [current public freeze](RESEARCH_FREEZE_2026-10-23.md).

## Executive publication decision

**One protected peer-reviewed research manuscript**, plus source-rights-aware reproducibility/technical archive. Do not submit the entire Kerala2040 2030/2040 platform as a single unvalidated paper, and do not confuse a GitHub repository, a preprint, a Zenodo DOI or a conference presentation with a peer-reviewed journal article.

- **Paper A, first choice if G2 succeeds:** *Weather-sensitive electricity consumption in Kerala: a source-audited multi-year retrospective evaluation*. Accepted claims would be limited to independently hash-verified ERA5 + qualified **daily Kerala SLDC operational consumption**; same-day realized reanalysis, chronological FY holdouts, simple registered baselines, error/uncertainty and negative years. Not a causal elasticity estimate, a day-ahead forecast or a measured hourly load forecast. The published FY2024–25 figures are exposed prior results, not untouched validation.
- **Paper A0, mandatory fallback if the 31 March 2027 data gate fails:** *Kerala electricity statistics across reporting boundaries: a reproducible public-data quality and completeness audit*. Needs a genuine generalizable methodological/empirical contribution, e.g. independently reconciled fiscal-year reporting boundaries, source revisions, cross-agency crosswalks and quantified missingness. **A descriptive inventory alone may not meet a research journal novelty threshold.** If sufficient novelty is absent, issue a titled, citable technical report with DOI without falsely declaring journal submission.
- **Paper B, optional post-2027 direction:** source-constrained hydro/import flexibility; requires defensible operating limits and independent observational checks. The original optimistically redispatched hydro cases are **not** suitable unqualified evidence of real reliability or investment benefits.
- **Software paper (separate and optional):** only if a reusable, original, maintained research **package** meets JOSS scope and actual usage criteria. A one-off portfolio dashboard or a pile of scripts is insufficient.

## 1. Journal shortlist by research product — journal selection is conditional

Read the **current official author guidelines, scope and latest 15–20 closely related articles** of a journal **before submission**. Every venue below is a possible target, not a promise of acceptance. Consider reader match and minimum novelty before metrics/impact factors.

| Venue (official page) | Appropriate Kerala2040 product | Fit / likely rejection risk | Publication model and status |
|---|---|---|---|
| [Energy Informatics — Springer Nature](https://link.springer.com/journal/42162/aims-and-scope) | **Paper A best initial scope match** where contribution is *transparent energy-data representation, source audit, leakage-safe multiyear weather/demand analysis* | Data management and energy modelling expressly in scope; risk if it is just a location-specific LightGBM leaderboard | Fully open access. Current posted APC **€1,240 / £990 / US$1,540**, plus applicable tax; fee is set by acceptance date. Case-by-case financial-need waiver request **at initial submission**, not later: [official fees](https://link.springer.com/journal/42162/how-to-publish-with-us) |
| [Sustainable Energy, Grids and Networks — Elsevier](https://shop.elsevier.com/journals/sustainable-energy-grids-and-networks/2352-4677) | Paper A **only** if power-system-level implications and methodological contribution are strong; Paper B if independently constrained and validated | Pure daily-statistical exercise may have weak network-system contribution | Check live subscription/OA options and any charges with the journal; do not treat mirrored APC listings as an invoice |
| [Electric Power Systems Research — Elsevier](https://shop.elsevier.com/journals/electric-power-systems-research/0378-7796) | **Paper B** for tested grid operations/hydro-import adequacy or dispatch contribution | Original grid operation impact required; documentation-only/source-audit Paper A0 is weak fit | Subscription journal with OA option where eligible; confirm the live author contract/charges |
| [Applied Energy — Elsevier](https://shop.elsevier.com/journals/applied-energy/0306-2619) | **Stretch** for unusually strong Paper A methodological/application insight or fully source-validated Paper B | High strength/novelty bar; current proxy-only simulations likely insufficient | Subscription/hybrid choice subject to live instructions; OA extra if selected |
| [Energy Policy — Elsevier](https://shop.elsevier.com/journals/energy-policy/0301-4215) | An eventual **policy-focused** paper evaluating defensible and balanced policy choices with broader significance | Not a generic modelling/data description; the journal explicitly requires policy questions/implications | Subscription/hybrid choice subject to live instructions |
| [Energy — Elsevier](https://shop.elsevier.com/journals/energy/0360-5442) | Only a compelling integrated energy/energy management contribution; lower near-term priority | Official journal scope gives priority to integrated/cross-sector studies, referring *purely electric* topics toward its sister *Smart Energy* | Subscription/hybrid choice subject to live instructions |
| [Scientific Data — Nature Portfolio](https://www.nature.com/sdata/publish/submission-guidelines) | **Only** a genuinely reusable, deposited, technically validated *dataset*, with rights to allow reviewer access and ultimately public availability | It is a **Data Descriptor**, not a venue for the primary ML hypothesis result. Public data sharing is generally required from second review round; currently restricted SLDC-derived records may fail | Open access APC: obtain live quote; no assumption of waiver |
| [Data in Brief — Elsevier](https://shop.elsevier.com/journals/data-in-brief/2352-3409) | A legally redistributable high-quality derived dataset and its documented creation/QA | Data articles describe accessible data; cannot turn private/unlicensed source rows into an open-data article | Fully open access, fee applies; confirm live APC. Not a zero-cost default |
| [Journal of Open Source Software (JOSS)](https://joss.readthedocs.io/en/latest/submitting.html) | Optional **software-only** paper after software package is independently reusable | Requires >6 months public active development, demonstrated research impact, complete package, tests/CI/docs, open source, contribution beyond one use case. Rejects papers whose focus is scientific results | **Diamond open access: no author fees**. Submission via paper.md, bibliography and public GitHub review |

**Default order for Paper A:** (a) assess against Energy Informatics' last 15–20 relevant papers, novelty and an acceptable **confirmed** APC funding plan; (b) consider a broader application/engineering venue **only if the completed analysis actually establishes broader methodological or operational insights**; (c) if funding is zero, prioritize an actually suitable subscription-enabled hybrid journal with a **no-APC subscription path**; this choice still requires strong scope fit. Do **not** pay an unaffordable APC, disguise fit, or move a paper to a predatory journal merely to obtain an acceptance.

**Default order for Paper B:** Electric Power Systems Research or Sustainable Energy, Grids and Networks **after source-backed operations validation**. Applied Energy is a stretch; Energy Policy requires a different, rigorous, balanced policy question.

**Paper A0:** first test whether there is novelty beyond a regional data audit, in energy-data representation or independent interagency consistency. If only a descriptive report remains, **Zenodo citable report > weak journal submission**. Scientific Data/Data in Brief are not fallback venues without a permitted, publicly accessible dataset.

### Four evidence-tied presubmission fit checks

1. **Scope** — Can an editor identify the article's generic research contribution from the abstract without knowing Kerala2040? 'We applied XGBoost in Kerala' is not a contribution by itself.
2. **Novelty** — Create a matrix against *at least* 15–20 recent closely related papers: region, target scope (metered consumption vs demand reconstruction), original data, chronology years, training/test separation, baselines, weather source, uncertainty, source-quality method, and contribution.
3. **Evidence** — No use of 354 source reports to claim a measured complete FY; no annual consumer-side versus SLDC daily boundary mixture; no unsupported import/LOLE/reliability or legal buildable-MW claims.
4. **Reproducibility and price** — Permissions, source transformations, independent numerical checks, journal-specific public-data rules, **author's budget/fee waiver**, and publisher policies for preprints/data/AI.

## 2. Author identity, eligibility and finances (critical if independent)

**No PhD is required.** An independent researcher can hold ORCID and submit to journals. Get ORCID free at https://orcid.org; ORCID explicitly states no university affiliation is needed: https://support.orcid.org/hc/en-us/articles/360006897334-What-is-an-ORCID-iD-and-how-do-I-use-it.

**Use a truthful present affiliation:** e.g. \`Independent Researcher, Stockholm, Sweden\`, corresponding email you control. Mention \`MSc, KTH Royal Institute of Technology\` as prior education **in biography or acknowledgments where appropriate**, *not* as a present KTH institutional appointment. If you later obtain a documented research affiliation, update identity/rights truthfully in the manuscript system according to the journal's requirements. Do not add a professor or KTH organization merely to obtain an APC discount.

**KTH APC arrangement:** https://www.kth.se/en/biblioteket/publicera-analysera/vagledning-for-publicering/publicera-oppet-till. As currently published, all corresponding authors seeking agreement coverage need an **active, formally documented KTH connection in HR/Ladok**, with KTH organisational affiliation and generally a KTH email. A past master's degree alone does not satisfy this published rule. Ask biblioteket@kth.se only if legitimate active eligibility arises. Graduated alumni should **plan as self-funded/unfunded** until institutional written confirmation.

**Publication fee hierarchy:**
1. No fee for an open archive/preprint, **JOSS** (if fully eligible), and the **subscription option of participating Elsevier hybrid journals**. Publisher states hybrid subscription articles incur **no publication fee**: https://www.elsevier.com/publishing/publish-in-a-journal/journal-selection. Still check optional colour/pages/supplements (rare but journal-dependent).
2. Fully OA journal fee/waiver: Energy Informatics currently €1,240 / US$1,540 / £990 + tax **at acceptance**, waiver request **during submission** if financial need, case by case; Indian citizenship is not the same as being based in a low-income waiver-eligible country, and Sweden residence does not guarantee subsidy.
3. For any venue, check the official journal **2027 acceptance-date APC**, whether a particular article type is eligible for institutional agreements, permitted licences and exact VAT before making binding selections. A journal's homepage estimate is not a payment request.
4. **No payment now:** submission fees and APCs are different. Review an actual invoice *only after acceptance* for fee-charging OA journals; never respond to unsolicited 'editorial invitation' payment emails.

**Preprint green-vs-gold distinction:** A preprint is **not** the final publisher PDF or an already peer-reviewed paper. Hybrid no-APC subscription may leave the final version behind a paywall; check which author-draft versions can remain public and relevant post-acceptance embargo. Elsevier official sharing policy: https://www.elsevier.com/about/policies-and-standards/sharing. Do not assume the accepted manuscript may be posted anywhere immediately under any licence. Keep a first author manuscript preprint separately archived and follow the selected journal's specific policy.

## 3. Publication route: from frozen question to indexed journal paper

1. **Register identity and bibliography (Nov 2026).** Create ORCID; choose a consistent author name and valid email; use Zotero/BibTeX with verified DOIs and full texts; export the novelty matrix; note all original observations already inspected and whether any true prospective evaluation period remains.
2. **Develop exactly one focused abstract (Jan 2027).** Formulate RQ, dataset and metering boundary, methods, deliberately simple baselines and 3 retrospective fiscal-year holdouts; *do not invent results or promise weather superiority*. Choose no final journal before seeing data/novelty.
3. **Execute preregistered source-admission and evaluation (Jan–June).** Hash original Copernicus assets; validate point/time/weather conversion; verify *private* daily SLDC original manifest and permissions; run simple Ridge vs weather comparison, missingness/exclusion report, per-year errors and diagnostics. Do not treat five-point complete normalized parquet as proof of original ERA5 provenance.
4. **March 31 fork.** If genuine multi-year ERA5 + measured **daily** target chain cannot be admitted, publish Paper A0 as data-source quality work **only if independent scholarly contribution remains**, otherwise use a transparent technical report. Do not rename the one-year experiment as multi-year.
5. **Draft with scientific architecture (April–August).** Title, abstract, contribution list, Introduction/literature, Materials and dataset definitions, Study design and split chronology, Models + leakage controls, Results with null/negative folds, limitations, conclusion, availability, conflicts/funding, author contributions and acknowledgments. Figures and tables described below. Target journal style only after the evidence and journal fit are decided.
6. **Full reproducibility and external critique (Jul–Sep).** Independent clean-install rerun, hash audit, pre-release data-rights review, errors/figures cross-check and at least 1 methods plus 1 Kerala operational expert *review request*. Do not claim either review occurred unless it did; be clear if no collaboration was secured.
7. **Determine public artifacts (Aug–Oct).** Freeze code/results to immutable git tag; pin original and transformed manifests; add clear README reproducer. Give publicly distributable code a source-release DOI (via Zenodo). Deposit a *paper preprint* separately only when the manuscript is genuinely ready and selected journal allows it; deposit any *dataset* separately only if licence allows. Never upload the raw private SLDC archive or confidential custodial records.
8. **Select journal and submit one manuscript (Sep–Oct if ready).** Read *current* guide; confirm article type/length, blind review handling, data availability, AI/ethics policies, cost/waiver, preprint policy and submission link from legitimate journal site. Prepare blinded PDF if required, separate title page, high-resolution original figures, supplementary files, funding/conflicts/authorship/AI statements, cover letter and recommended reviewer contacts if requested (no conflicts). Submit to **one journal at a time**. Record manuscript ID and exact date, not a guessed decision timeline.
9. **Editorial path:** admin check → desk decision or reviewers → decision letter (reject/minor/major/accept) → point-by-point response, tracked revisions, new analyses only when ethically justified, source evidence updated → acceptance or resubmission elsewhere sequentially. Editorial decisions/acceptance may run beyond October 2027, so **submitted/archived** is a viable year-one milestone. Record rejection without pretending it is publication failure: revise scope and aim appropriately.
10. **After publication:** link paper's official DOI, source-code DOI, dataset DOI (if any), ORCID and project's evidence website, preserve exact release versions, note errata and source-rights limitations, and do not silently move post-2027 numbers into frozen historical conclusions.

### Required article contents: practical acceptance package

**Cover/title:** \`Paper A\` author identity, corresponding contact, actual affiliation; 3–5 contribution bullets, concise honest novelty and no accuracy boast before completed multi-year study.

**Introduction:** why actual *daily operational consumption* is useful/limited in a monsoon-dependent electricity system; why reporting boundary and reanalysis quality influence quantitative inference; precise unanswered question and how this differs from CSTEP/CEA/WRI and the 15–20 nearest studies.

**Source/method:** source inventory and fidelity status; FY and IST definition, units MU/day, ERA5 variables and 5-point spatial method, UTC-hours to local day boundary with temporal support, source missingness/exclusions, predetermined train/test splits; original source and transformation checksums.

**Comparators:** seasonal naive, calendar-only fixed Ridge, calendar + weather fixed Ridge; optionally independent XGBoost/LightGBM with hyperparameter optimization strictly in past training folds and equal budgets. Comparisons on exactly matched held-out qualified SLDC dates. Clearly distinguish retrospective explanatory modelling from forecast available the day before.

**Error and uncertainty:** per FY MAE/RMSE, signed relative error, MASE if denominator justified, partial-year/missing-day sensitivity, high-demand-day errors, monsoon/dry months, dependence diagnostics and block-bootstrap sensitivity if defensible. Report years in which weather adds no value.

**Policy and operation:** no actual hourly peak, loss-of-load risk, causality, heat elasticity, economic investment conclusion or transferable storage/hydro MW inferred from the daily ML score.

**Figures, proposed only (no fabricated outputs):**
- Figure 1 — study boundary, source/provenance flow and observed/missing day calendar.
- Figure 2 — strict source/train/test fiscal-year time split, including exposed FY2024–25.
- Figure 3 — per-year RMSE/MAE calendar-only vs +weather with negative comparisons visible.
- Figure 4 — held-out residual time dependence and temperature/monsoon stratification.
- Figure 5 (optional) — sensitivity to point selection and model complexity.
- Table 1 — publisher, metering/accounting definition, dates, unit and source QA.
- Table 2 — per-FY coverage, baseline count and model/uncertainty output.
- Supplemental archive — executed run manifest, missingness decisions, original SHA lineage, code instructions, software versions, model data restrictions, additional negative folds/plots.

### Data Availability statement — adapt to what is true at submission

**Example structure only; not a claim that specific content is already deposited or permission secured:**

\`Source-level daily operational records were obtained from publicly attributed Kerala SLDC reports and are subject to their original provider's terms. The analysis uses a separately provenance-verified, qualified daily dataset and ERA5 reanalysis produced by the Copernicus Climate Change Service. Source retrieval dates, revision identifiers, units, geographic/temporal definitions and hashes are documented in the companion evidence manifest. Reproducible transformation and analysis code and legally shareable aggregate results are [planned URI/DOI]. Original records that cannot legally be redistributed are not republished; their custodian and access routes are described. Any review-specific access follows the journal's requirements and provider permissions.\`

Never insert a placeholder DOI as an actual DOI, or promise open replication from restricted material. If the intended journal requires public review-time data, and access cannot legally be arranged, **choose a different venue or obtain permission first**.

### Other mandatory integrity declarations

- Funding: \`This work received no specific external research funding\` **only if true**.
- Conflicts: actual author/employment relationship and materials disclosed, \`no competing interests\` **only if true**.
- Affiliation: independent researcher unless later formally appointed; KTH degree belongs in bio, not assumed current affiliation.
- CRediT contributions: actual named human work only; academic reviewers are acknowledged with consent, never listed as authors by courtesy.
- AI provenance: follow journal's **current** generative-AI publication policies. Keep a private tool/version/usage/review record; cite verified papers, do not list AI as an author; separate **AI-assisted software development, literature/code analysis or scientific methods** from mere copy-editing. Springer 2026 policy requires transparent declarations for substantively used AI: https://group.springernature.com/gp/group/ai/ai-guidance-for-researchers-editors-reviewers. JOSS likewise asks for distinct AI usage disclosure and human design/contributions. An undeclared unreviewed LLM-generated statistic or unverified citation cannot be published as independent scientific computation.
- Prior Kerala2040 website and published experiments: cite and differentiate old exploratory/source-frozen analyses. No salami slicing or concurrent publication of substantially identical scientific results. Elsevier: https://www.elsevier.com/en-in/editor/perk/multiple-duplicate-concurrent-publication-simultaneous-submission.

## 4. Open research, DOI/indexing and actual submission details

### The free citable route

1. Make the public **GitHub** software tag only after code/data-rights QA. Ensure \`LICENSE\`, \`CITATION.cff\`, \`README\`, exact environment requirements, checksums, reproduction script, test suite, relevant source manifest and legal exclusions. The public source tag must be unambiguously tied to paper figures.
2. Connect the **Zenodo** account to the public GitHub repository, enable the repo, and create a named GitHub **release**. Zenodo documents automatic ingestion of subsequent releases: https://help.zenodo.org/docs/github/enable-repository/. Zenodo assigns a persistent DOI on publication, and records have version identities: https://help.zenodo.org/docs/get-started/quickstart/ and https://help.zenodo.org/docs/deposit/manage-versions/.
3. For the *manuscript*, put a reviewable preprint PDF in a suitable *separate* preprint repository or Zenodo Publication record with an explicit \`Not peer reviewed\` status. **EarthArXiv** accepts Earth science and related scholarship but is not automatically suitable for every energy-load machine-learning paper; check topic fit: https://eartharxiv.org/repository/about/. arXiv categories and endorsement rules should be checked before attempting that route. A Zenodo Publication record can be a pragmatic generalist alternative.
4. For a *dataset*, separate \`Dataset\` DOI if provider terms permit raw/derived redistribution. Data-reuse rights are not automatically inherited from permission to **read** public dashboards. Deposit published code and original third-party agency material separately; never leak private archive records into ZIPs or journal supplements.
5. When submitting, include source software **version DOI** (fixed files for reviewer), manuscript preprint DOI if published, and final journal DOI when assigned. Distinguish paper DOI vs code DOI vs dataset DOI; do not cite a general latest repo URI as an immutable data snapshot.

**Zenodo does not perform journal-style peer review.** It confers a durable citable archived object, not journal acceptance. Its deposited files are not trivially editable once published; audit first.

### Editorial submission checklist

- [ ] Verified matched journal scope and *specific article type* from official site.
- [ ] Updated 15–20-paper literature gap matrix; strong clear methodological contribution.
- [ ] Known real ORCID, email, authorship, truthful affiliations, human contributors and consent.
- [ ] Full article + journal-specific anonymous/blinded version if requested.
- [ ] 4–6 original figures with legible axes, source definitions, correct target units and uncertainty.
- [ ] Data provenance, raw/derived licence position, reproduction instructions, SHA and open/restricted split.
- [ ] Source chronology, version and unmatched dates fully explained; original source chain verifiable.
- [ ] Preprint/journal copyright policy, embargo, accepted manuscript terms and chosen OA/subscription option checked.
- [ ] Funding, competing interests, human/AI contributions and any needed ethical statement.
- [ ] Cover letter with real problem, research contribution, why journal audience benefits, originality and non-concurrent submission.
- [ ] Suggested reviewer contacts if requested; no collaborators, institutionally related persons or obvious conflict.
- [ ] Confirmed financial plan (zero-APC subscription, funded APC, or waiver granted/eligible) *before committing*.
- [ ] One corresponding author owns response/revision log and proofs, versioned package pinned.
- [ ] No simultaneous submissions or misleading preprint indexing/status.

## 5. The publication schedule **within** the approved 110 WP5 hours

Do not allocate a *new* 100-hour publication project on top of the 400-hour charter. The table below exactly reuses the existing monthly WP5 hours; data extraction and model fitting remain charged to WP1/WP2 rather than silently double-counting.

| Window | WP5 focused hours | Publication-specific tangible output |
|---|---:|---|
| Nov 2026 | 2 | One-page Paper A problem, contribution hypothesis, authorship/affiliation/ORCID checklist |
| Dec 2026 | 3 | Provisional venue shortlist, fee and rights decision ledger |
| Jan 2027 | 2 | Registered abstract structure, section plan and citation matrix handoff from WP0 |
| Feb 2027 | 2 | Table/figure shells with no made-up numbers |
| Mar 2027 | 4 | Data gate fork A vs A0 and actual novelty matrix update |
| Apr 2027 | 8 | Draft reproducible data/methods section and limitations |
| May 2027 | 6 | First eligible results draft, baseline explanation and traceable captions |
| Jun 2027 | 6 | Paper A/A0 scope/title fixed; primary results freeze document |
| Jul 2027 | 6 | Initial full manuscript sections; independent repeatability checklist |
| Aug 2027 | 11 | Complete manuscript v1, final figures, data/code availability and journal choice |
| Sep 2027 | 26 | Source/figure audit, clean-environment reproduction, external critical review requests, reviewer-style rebuttal and revisions |
| Oct 1–26 2027 | 34 | Final polished manuscript, source-release DOI(s) where lawful, submission package, *submission or explicit not-ready verdict*, freeze evidence/website/tag |
| **Total** | **110** | |

**Milestones and decision points:**
- **Nov–Jan:** register question and ethics before additional model selection; don't commit to a fee.
- **31 March:** A or A0 selected from actual primary-source success; no made-up positive result.
- **30 June:** registered per-year results or documented no-go, with no post-hoc promotion.
- **31 August:** complete text and claim cutoff, journal's most relevant 15–20 prior papers checked.
- **30 September:** submit to journal *only if* reproducibility and source permissions have passed; otherwise strengthen manuscript for October.
- **26 October:** final first-year output = journal **submission if scientifically ready**, otherwise an accurately classified DOI-archived working paper/technical report and review-ready source bundle. Acceptance may take many additional months.

## 6. Submission/acceptance reality and options

**Do not optimize for speed, APC level or impact factor alone.** An editorial rejection is not proof that the research is worthless: common legitimate reasons are incomplete methodological novelty, weak data availability, wrong audience, inadequate control of biases or limitations. After a reject, revise to another journal **sequentially**, and write the response plan using the rejection specifics. A paid OA journal can reject a paper as quickly as a hybrid journal; payment does not secure peer review acceptance.

**If the main paper is accepted:** link official peer-reviewed DOI to the frozen Kerala2040 public site, and clearly label separate software DOI and dataset DOI. Only the *accepted final journal publication* gets the label \`peer-reviewed\`.

**If Paper A has insufficient eligible multiyear weather:** do **not** spend extra research hours trying to repair the headline. A robust dataset/official-boundary technical report with openly reviewable aggregate proofs and honest admissions is a strong contribution, albeit not an accepted journal article; later scientific progress can be published when new data arrive.

**If you want a software publication after the main research:** assess genuine general applicability of Kerala2040's source-audit algorithms and public package against JOSS 2026 updated criteria. It is entirely legitimate for a no-fee software paper to follow a scientific article with clear distinct contributions, but it is not a guaranteed low-effort shortcut.

## 6A. Conference proceedings vs journal articles: optional networking path

**IEEE PowerTech 2027** in Bruges, Belgium (5–9 September 2027), is a legitimate reviewed **electric-power-systems conference**, not a general Kerala policy exhibition: https://powertech2027.com/call-for-papers/. Official information available on 26 October 2026 says the **full six-page paper deadline is 28 February 2027**, author decision 23 April, and final paper due 23 May. Reviewed and accepted **presented** papers are submitted to proceedings subject to IEEE requirements and author registration. **Our Paper A data go/no-go is 31 March, one month AFTER this full-paper deadline**, so trying to send a new 'completed multi-year weather' result to PowerTech 2027 would violate the current evidence sequence. **Do not divert the 10-hour/week budget to that February deadline.** A separate genuinely completed, already-source-supported methods contribution could be evaluated independently but is not the default plan.

**Energy Informatics Academy Conference (EI.A)** is an established research venue focused on energy informatics, with reviewed papers and an LNCS proceedings track in its 2026 programme: https://www.energyinformatics.academy/2026-eia-conference. The 2026 edition has already happened by this charter date (14–17 October 2026); **a 2027 programme/deadline has not been verified here**. Revisit an actual new call in early 2027; only consider if Paper A already has admissible evidence and the proceedings rights/registration costs fit the budget.

**Conferences can create academic contacts faster than journal review**, but may demand travel/registration, presentation and separate submission effort. A peer-reviewed conference proceeding is a valid indexed research product when formally accepted/published, but not automatically equivalent to a journal article. A short non-archival abstract/poster can obtain feedback without consuming the same original research as a separate full proceedings paper. **Do not assume that an archival conference paper can be submitted unchanged to a journal.** Consult both venues and ensure a journal extension has substantial genuinely new research, acknowledges the conference version and complies with duplicate-publication policy.

**Default:** journal Paper A with invited pre-submission critique; conference presentation only if it does not pre-empt the protected manuscript milestones or add new speculative results.

## 7. Decisions still owned by the researcher

1. **Maximum personal APC budget:** default planning assumption = **€0 out-of-pocket** until explicitly changed. This makes fee-free public archiving + appropriate hybrid subscription publication the baseline; Energy Informatics requires institution/waiver/confirmed alternative funding if selected.
2. **Academic collaborator:** would an energy-systems/energy informatics researcher be willing to do substantial methods input, help access primary data or join authorship if warranted? Do not promise coauthorship for prestige/APC coverage.
3. **Original data sharing:** can SLDC daily source and aligned weather derived observations be shared with journal reviewers/public? This determines whether a Scientific Data or Data in Brief route is even possible, and may affect Paper A eligibility.
4. **Preprint timing:** publication before/after initial journal submission once manuscript is clean and venue preprint policy confirmed. Never call unreviewed material accepted.
5. **Which exact result is ready:** wait for independently acquired 2027 evidence before ranking a demanding application journal above a closer methodology/data journal.

**Do not update public Kerala2040 website claims or send agency letters on the authority of this planning document alone. The linked planning PR remains a draft until reviewed.**
