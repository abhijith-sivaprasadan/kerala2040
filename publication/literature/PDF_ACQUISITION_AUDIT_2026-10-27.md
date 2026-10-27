# Kerala2040 — full-text PDF acquisition and validation audit

**Data/access status:** 27 October 2026. **Execution:** GitHub Actions with the user's stored \`OPENALEX_API_KEY\` secret; repository credentials never committed/exposed. **Public branch:** \`publication/oa-fulltext-discovery-2026\`, stacked on literature PR #138. No third-party PDF binaries, private SLDC rows, or copied full article texts are committed.

**Audited runs:**
- [Initial automated OpenAlex 14-PDF attempt (run 40442150229)](https://github.com/abhijith-sivaprasadan/kerala2040/actions/runs/40442150229) — metadata artifact [12707235851](https://github.com/abhijith-sivaprasadan/kerala2040/actions/runs/40442150229/artifacts/12707235851).
- [Extended 14 OpenAlex + 7 institutional candidates (run 40442388470)](https://github.com/abhijith-sivaprasadan/kerala2040/actions/runs/40442388470) — metadata artifact [12706786377](https://github.com/abhijith-sivaprasadan/kerala2040/actions/runs/40442388470/artifacts/12706786377).

## What was actually done

**36 DOI-bearing references** from the frozen 44-source curated review were resolved using live OpenAlex metadata. **14** received candidate PDF URL links; **22** did not receive a direct PDF URL from this provider. The 14 candidate links were attempted on an ephemeral GitHub Actions runner; a second, distinct manually researched batch of **seven** author/institutional candidates was attempted separately. PDF download status, SHA-256, file bytes, strict pypdf structure, page count, DOI presence in the first two pages, and title-token identity evidence were stored in **metadata-only** CSV artifacts.

| Intake/source | Candidate PDF URLs tested | PDFs actually saved | PDFs structurally parsed | Failed/non-PDF |
|---|---:|---:|---:|---:|
| OpenAlex-discovered candidate batch | 14 | **4** | **4** | **10** |
| Independent university/author candidate batch | 7 | **2** | **2** | **5** |
| **Distinct source IDs verified** | **21** | **6** | **6** | **15** |

**These six structurally validated PDF downloads are not six *scientifically reviewed* papers.** Structural checks verify parseability and screen paper identity; authors' methods, figures and results still need human critical reading. Same-source PDF editions must be compared with any manuscript/version already in the study.

### Verified PDF bytes and metadata (2026-10-27)

| ID | Scholarly paper | Source | Pages successfully parsed | Identity evidence |
|---|---|---|---:|---|
| D01 | Hunt & Bloomfield (2025), *Building and explaining data-driven energy demand models for Indian states* | University of Reading CentAUR repository | 29 | First-page title token coverage 1.000; DOI present in first two pages |
| W02 | Cucchi et al. (2020), *WFDE5: bias-adjusted ERA5 reanalysis data for impact studies* | Copernicus Earth System Science Data publisher | 24 | Title 1.000; DOI present |
| M04 | Pfenninger et al. (2018), *Opening the black box of energy modelling* | arXiv author preprint | 9 | Title 1.000; DOI present |
| M06 | Brown et al. (2018), *PyPSA: Python for Power System Analysis* | arXiv preprint | 10 | Title 1.000; DOI **not** found in first two pages; final-version match requires manual verification |
| M01 | Pfenninger, Hawkes & Keirstead (2014), *Energy systems modeling for twenty-first century energy challenges* | first author's hosted accepted manuscript | 29 | Title 1.000; DOI present |
| H01 | Vatanchi, Kiviluoma, Klöve & Patro (2026), *Short-term hydropower regulation through coupled hydrological and energy models* | University of Oulu repository | 15 | Title 1.000; DOI present; repository cites CC BY 4.0 licence |

**Version distinction:** the D01 university repository copy has 29 parsed PDF pages; the user-supplied published article in conversation had 27. Do **not** assume they're byte-identical or numerically different; check version/cover/supplement pages and compare actual content before interpreting any difference. M04/M06 are arXiv versions rather than guaranteed final publisher typesetting.

**Source-grade classification after this audit:** \`downloaded_pdf_structurally_validated\`, **not** \`critically_read_full_text\`. The research evidence matrix's scientific \`access_level\` must **not** silently change to “read in full” from these statuses.

### PDF candidates that failed automated retrieval

| ID | Method of initial retrieval | Observed outcome | Reading implications |
|---|---|---|---|
| D05 | SpringerOpen PDF redirect | HTML/non-PDF response | Publisher **HTML full text** is publicly readable; obtain PDF manually if needed |
| D06 | Taylor & Francis PDF | 403 | Use authorized journal/repository access |
| F03 | SpringerOpen PDF redirect | HTML/non-PDF response | Publisher HTML full text exists |
| V02 | Springer PDF | HTML/non-PDF response | Alternative author-hosted PDF: https://kt.ijs.si/igor_mozetic/papers/CerTorMoz-TimeSer-MACH-20.pdf |
| W01 | Wiley PDF | 403 | Browser/full text or institutional copy; no local PDF verified |
| M03 | Elsevier ScienceDirect PDF | 403 | Alternative first-author public PDF: https://www.pfenninger.org/publications-pdf/2017%20-%20Pfenninger%20et%20al%20-%20Importance%20of%20open%20data%20and%20software.pdf |
| P01 | Old White Rose institutional PDF | 404 | Official White Rose/Adelaide landing pages provide alternative manuscript access |
| P02 | BMJ PDF | 403 | Publisher's open HTML may be read directly |
| O08 | Elsevier PDF | 403 | First-author PDF: https://www.pfenninger.org/publications-pdf/Staffell%20and%20Pfenninger_2016_Bias-corrected%20reanalysis%20to%20simulate%20wind%20power.pdf |
| O09 | Elsevier PDF | 403 | First-author PDF: https://www.pfenninger.org/publications-pdf/Pfenninger%20and%20Staffell_2016_Long-term%20patterns%20of%20European%20PV%20output.pdf |
| F01 | Cardiff accepted manuscript | 403 on GitHub runner | Human browser/approved repository may reach https://orca.cardiff.ac.uk/id/eprint/103793/1/Manuscript.pdf |
| V01 | Legacy Swiss WSL hosted PDF | 404 on GitHub runner | Wiley publisher full article accessible; find official archived PDF or equivalent |
| V03 | Rob Hyndman hosted preprint | 403 on GitHub runner | Human/browser author PDF: https://robjhyndman.com/papers/cv-wp.pdf |
| V04 | Rob Hyndman hosted preprint | 403 on GitHub runner | Human/browser author PDF: https://robjhyndman.com/papers/mase.pdf |
| M02 | UCL accepted manuscript | 404 on GitHub runner | Oxford repository has manuscript https://ora.ox.ac.uk/objects/uuid:ba34d62e-2540-40c4-91f3-66ba0b14afe6 |

A **403 is host access control**, not proof of a closed-access published article; a **404** can indicate a retired/moved file even where another copy exists. An HTML response can be publisher landing-page content without a PDF file. All raw downloader outcomes are in the two workflow manifest artifacts; the table summarizes them without recasting failures as successful downloads.

## Unresolved critical source requests

| Priority | ID | Paper and legal route | Why manual access matters |
|---|---|---|---|
| **P0** | D03 | Porwal et al. (2026), IEEE [publisher abstract](https://ieeexplore.ieee.org/abstract/document/11468867/); request full text from the authors, eligible library or publisher | Highest immediate unknown in direct state weather-demand novelty; OpenAlex reports no direct OA PDF |
| **P0** | D02 | Harish, Singh & Tongia (2020), [published article](https://doi.org/10.1016/j.enpol.2020.111445); eligible library/author manuscript | Closest historical Indian-state temperature-load physical interpretation; rich publisher HTML snippets accessible but not all verified methods/appendices |
| **P1** | D04 | Babu et al. (2026), [Applied Energy DOI](https://doi.org/10.1016/j.apenergy.2026.128069); eligible library or author | Medium/long-term Indian demand and cooling/EV precedent |
| **P1** | F02 | Hong & Fan (2016), [DOI](https://doi.org/10.1016/j.ijforecast.2015.11.011) | Forecast probability vs retrospective explanatory association |
| **P1** | F05 | 2026 leakage-aware energy forecasting, [open publisher article](https://doi.org/10.1016/j.ecmx.2026.101791) | Strongest same-algorithm temporal preprocessing audit; HTML may be sufficient |
| **P1** | V01/V03/V04 | University/author manuscripts or publisher free HTML | Critical validation protocol nuances, already available to browser despite GitHub HTTP failures |

**No paywall circumvention or claim of automatic institutional subscription was attempted.** The user can download articles through normal authorized library or publisher routes and upload PDFs privately into the research conversation for actual paper-specific critical appraisal.

## Research and security constraints

- **Secrets:** OpenAlex key in GitHub Actions secret, scoped exclusively to the OpenAlex lookup step, not to PDF retrieval/verification. No key or token in code/artifacts.
- **Rights:** PDFs live temporarily on a GitHub-hosted runner and are **not** uploaded as public repository files or GitHub Actions artifacts. Artifacts contain CSV metadata: target DOI, candidate link, SHA, pages, error classification and bibliographic match screen only. Rights/CC licensing vary by file; no blanket permission asserted.
- **Identity:** title/DOI first-page checks are screening hints, not complete human verification of edition, figure integrity, supplementary material or actual printed final changes. PDFs with a missing title/DOI in extracted text might still be correct scanned manuscripts.
- **Scope:** 36 DOI records from 44 curated sources. The eight non-DOI official/resource records require separate primary-provider handling; this pipeline does not address them.
- **Publication:** nothing from this intake authorizes new Kerala2040 ML scores, causal temperature effects, operational flexibility claims, source-equivalence conclusions or manuscript novelty assertions. Those require independent field-level/record-level investigations.

**Next best scientific action:** the user obtains original Porwal (D03) and Harish (D02) complete papers through a lawful institutional or author route while we read high-priority available full texts; independently access Hunt & Bloomfield's **original-unit Zenodo dataset** and reconcile actual source definitions before running a new Kerala forecasting study.
