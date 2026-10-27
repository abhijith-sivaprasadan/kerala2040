# OpenAlex DOI literature lookup — verified first live GitHub Actions run

**Date:** 27 October 2026 UTC. **Execution:** [Publication OpenAlex OA full-text lookup, GitHub Actions run 40440934911](https://github.com/abhijith-sivaprasadan/kerala2040/actions/runs/40440934911) on `publication/oa-fulltext-discovery-2026` commit `da6a6347060d75e2f01836eb2446e94465dfd13f`.

This is a **real live provider API result**, not a manual bibliography estimate. The job used **anonymous OpenAlex** because `OPENALEX_API_KEY` was **not set**. The request did **not** invoke Unpaywall or download article PDF bytes.

## Metrics observed in workflow logs

| Category | Number | Interpreted correctly |
|---|---:|---|
| Distinct DOI records queried | **36** | All DOI-bearing rows of the existing 44-source evidence matrix |
| OpenAlex calls with an OA PDF candidate URL | **14** | Metadata indicates a possible downloadable source; accessibility, licence and content not yet verified |
| OA lookup records without a direct OA PDF URL | **22** | Does not mean paywalled; may have legal HTML, repository landing or author copies |
| Lookup failures | **0** | The OpenAlex API query itself succeeded for all 36 |
| PDFs actually downloaded and hash-verified | **0** | `--download` not requested |
| Papers critically read due to this workflow | **0** | Scientific review only begins once full texts are retrieved and inspected |

## Downloadable evidence manifest

- **Artifact:** [`kerala2040-openalex-oa-links-2`](https://github.com/abhijith-sivaprasadan/kerala2040/actions/runs/40440934911/artifacts/12706405892). Contains `oa_discovery_results.csv` with each DOI, OA status, candidate PDF URL, landing-page URL, provider, UTC query timestamp and retrieval status.
- **Run summary and console log:** [same GitHub Actions run](https://github.com/abhijith-sivaprasadan/kerala2040/actions/runs/40440934911).
- GitHub artifact default retention configured here: 30 days. The public DOI list remains versioned in `DOIS_FOR_UNPAYWALL.txt`; the direct result CSV intentionally remains a generated artifact rather than silently changing hand-reviewed source access grades.

### High-priority PDF candidate IDs, from workflow logs

`D01`, `D05`, `D06`, `F03`, `V02`, `W01`, `W02`, `M03`, `M04`, `M06`, `P01`, `P02`, `O08`, `O09`.

Critical comparator PDFs `D02` (Harish et al. 2020) and `D03` (Porwal et al. 2026) did **not** have direct OA PDF URLs in this OpenAlex response. These remain priority targets via a legal library copy, publisher abstract/full-text view or author manuscript request. `D01` (Hunt and Bloomfield) full paper was already supplied by the research owner; this run does not duplicate reading it.

## Security and action state

- `OPENALEX_API_KEY` **not present** at execution; the connected GitHub app cannot create or inspect Actions secrets.
- User must add the key in **Settings → Secrets and variables → Actions → Repository secrets** under exact name `OPENALEX_API_KEY`. Key is also an OpenAlex sign-in credential; do not share publicly.
- A future manual `workflow_dispatch` trigger appears in GitHub Actions only **after the workflow YAML exists on the repository default branch**, per GitHub's documented behavior. A push to this development branch has already demonstrated that the workflow works without the key on the anonymous budget.
- No research conclusions, source validity claims, or copyrighted PDF files were added to the public evidence freeze.

This run provides the **link-discovery layer**. Full-text retrieval, source/licence checks, exact document versions and a human scientific appraisal remain subsequent tasks.
