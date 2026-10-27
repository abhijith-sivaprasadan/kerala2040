# Kerala2040 — Literature-review research package

**Status:** structured critical *narrative* review completed as a verifiable scholarly background, **27 October 2026**. **Not** systematic/PRISMA, not a peer-reviewed publication, not a new empirical Kerala electricity result. The publication research charter in [draft PR #135](https://github.com/abhijith-sivaprasadan/kerala2040/pull/135) remains separately governed.

## Start here

1. **[Critical literature review](CRITICAL_LITERATURE_REVIEW_2026-10-27.md)** — integrated research state of knowledge, six key review questions, source/validation/metering/ERA5/hydro limitations, experimental novelty gates and publication decision.
2. **[Twenty closest-source appraisals](CLOSEST_STUDIES_CRITICAL_APPRAISALS.md)** — detailed account of the nearest Indian demand, statistical, hydrological and Kerala contextual studies, including exactly what was and was *not* checked.
3. **[Manuscript background draft](MANUSCRIPT_INTRODUCTION_BACKGROUND_DRAFT.md)** — reusable but **not submission-ready** introduction text and citeable literature positioning with placeholders for as-yet-unperformed source comparisons and results.
4. **[Evidence matrix](EVIDENCE_MATRIX.csv)** — 44 curated source records with DOI, record type, explicit access level, relevance and concrete design implication. All seven previously provisional author fields have been resolved against publisher/university sources.
5. **[Protocol/search/QA log](REVIEW_PROTOCOL_AND_SEARCH_LOG.md)** — search queries and date, selection/access limits, statistical biases, future full-text needs and version-1.0 completion audit.
6. **[Previously established Hunt/Bloomfield novelty memo](../../studies/paper-a-2027/HUNT_BLOOMFIELD_PRIOR_ART_REVIEW_2026-10-27.md)** — published article's methods and Kerala-specific score, code inspection, untouched-data access gap and proposed original-unit benchmark.

## Key interpretation

Hunt & Bloomfield (2025) published Kerala-specific ERA5/XGBoost/SHAP demand research and a public dataset; we **cannot** claim this is the project's scientific first. A potentially original Kerala2040 result instead requires **original-source Kerala SLDC operational-consumption definitions, comparison to Grid-India reporting, fiscal-year chronology, preprocessing/analyst-exposure audit, and independently verified meteorology**. The nearest competing IEEE 2026 full text and original public/private comparative records remain a specific next-step gap. No quantitative source-equivalence or reproducibility claim has been promoted by this review.

## Scope and quality control

- The **44** records are an intentionally curated sample. **32** rows are labelled peer-reviewed scholarly articles/reviews/conference/data/software, and 12 are government, source-provider, formal method-guidance or other institutional records. The 32 are **not** all full-text-inspected: consult `access_level`.
- The review has 20 prioritized appraisals, **not** 20 full-text replications. Full article/code access is indicated only for actual verified sources. Porwal 2026 is abstract-level; direct Hunt model reproduction and Zenodo-vs-SLDC paired validation **not performed**.
- No duplicate independent screeners, full search denominators or systematic exclusion log were available; therefore **do not** describe the package as PRISMA systematic/scoping review.
- Source document authors retain copyrights and data rights; no copyrighted PDFs or private SLDC rows are copied into this branch. Only research notes/metadata and lawful short paraphrases are included.
- Manuscript-quality novelty remains conditional. Failure of the evidence gate should lead to Paper A0 source-accounting work or a transparent technical report rather than a forced journal article.

## What is completed and what continues

**Completed now:** critical secondary research *as a source-graded narrative synthesis*, current closest published rivals identified, seven source-author metadata gaps corrected, a candidate paper-background narrative written, clear research/provenance/validation null criteria.

**Not completed by a literature review:** authentication of original private SLDC bytes, independent run of Hunt's public model/dataset, comparison of actually equivalent Grid-India/SLDC fields, historical ERA5 source acquisition, future-year empirical regression results, verified causal/dispatch inferences, journal submission or outside human review. These remain tracked in the year-one execution plan.

**Highest next return:** source-audited accession of the freely published Hunt & Bloomfield `Kerala.csv` and `corrected_daily_energy_met_MU.csv`, precise original-field comparison with private SLDC data under authorised access, and a go/no-go manuscript novelty conclusion **before** spending substantial time on downloading/processing more ERA5.


## Open-access article discovery — Unpaywall / OpenAlex (27 October 2026)

**Goal:** help obtain legally accessible *full-text papers* for independent manual critical reading. OA metadata is not itself the full article, a verified read, redistribution permission or proof of original-source licensing.

**Sources:** [Unpaywall REST API](https://unpaywall.org/products/api), [OpenAlex API](https://help.openalex.org/api/), and the [shared Unpaywall/OpenAlex OA index](https://help.openalex.org/access/unpaywall/). Unpaywall \`/v2/search\` was retired in September 2026; Unpaywall's **single DOI** \`/v2/{doi}?email=...\` endpoint still works. OpenAlex supports single-work DOI resolution with \`open_access\` and \`best_oa_location\`. OpenAlex basic unauthenticated tests remain possible, but for 36 citations and repeatable usage, use a **free API key** obtained directly at [OpenAlex Settings](https://openalex.org/settings/api); October 2026 official docs describe limited anonymous usage and a free keyed daily allowance. Do not commit API keys or any personal contact email to source files.

### Easiest option without writing or running code

Open [Unpaywall Simple Query Tool](https://unpaywall.org/products/simple-query-tool) and paste the **36 DOI lines** from [DOIS_FOR_UNPAYWALL.txt](DOIS_FOR_UNPAYWALL.txt). The service can query up to 1,000 DOIs in a batch and return an open-access status/link report. This does not download journal PDFs; it helps locate legitimate free copies. Eight of the 44 curated records are **not DOI-identified** and belong in separate official/public-provider source acquisition.

### Reproducible script (standard-library Python, no pip installation)

In a local Kerala2040 checkout, from the repository root:

\`\`\`powershell
# Demo: look up the first three reference DOIs using limited anonymous access
python publication/literature/find_open_fulltexts.py --limit 3

# Recommended for all DOI records: obtain a free OpenAlex key yourself
$env:OPENALEX_API_KEY = Read-Host "Your OpenAlex API key"
python publication/literature/find_open_fulltexts.py --provider openalex

# Unpaywall fallback requires your own valid contact email
$env:UNPAYWALL_EMAIL = Read-Host "Your email for Unpaywall"
python publication/literature/find_open_fulltexts.py --provider both

# ONLY once you reviewed the candidate source and local copyright requirements:
python publication/literature/find_open_fulltexts.py --provider both --download
\`\`\`

**Expected output:** \`publication/literature/oa_discovery_results.csv\`, with record ID, original DOI, OA status, chosen repository/publisher PDF *candidate URL*, landing page, lookup outcome, optional PDF download status and verified SHA-256. Candidate status \`oa_pdf_candidate\` means the API *advertised a URL*, not that a file was downloaded or even reachable. Download status \`saved_pdf_signature_verified\` means an HTTPS response began with a PDF signature, passed the configured file-size bound and was SHA-256 hashed, **not** that scientific content was read/reviewed. If a source requires login or cannot serve an accessible PDF, it remains manual retrieval.

**Safety:** download is OFF by default, requires explicit \`--download\`; no paywalls are bypassed; only HTTPS URLs accepted. A publisher full-text URL can still lead to a login or HTML page and is rejected as PDF. Original third-party PDFs and automatically generated results are **excluded from Git commits** by \`.gitignore\`. Check publication/licence terms before distributing any PDF. Do not upload a restricted article or private Kerala SLDC original into a public repository or Zenodo without permission.

**Manual fallback:** use the DOI to request through an eligible library, permitted institutional repository, public preprint server or the paper's corresponding author. The Hunt/Bloomfield full 27-page paper has already been supplied in the conversation; its separate public Zenodo *data files* are a different scientific acquisition task and this DOI-to-PDF script does not perform that dataset fetch.

### Offline validation

\`\`\`powershell
python -m unittest discover -s publication/literature -p "test_find_open_fulltexts.py" -v
python publication/literature/validate.py
\`\`\`

**Known limitation of this session:** the authoring environment could not reach the OpenAlex/Unpaywall JSON APIs, so **none of the 36 DOIs has a newly live-verified OA link or downloaded PDF as a result of this commit**. Running the script on a network-enabled computer is required for live results. CI tests only deterministic local parsing, response-selection, HTTPS validation and fake PDF download checks.
