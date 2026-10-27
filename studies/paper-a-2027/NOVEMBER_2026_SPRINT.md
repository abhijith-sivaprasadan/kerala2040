# November 2026 — Paper A research start: four-week execution board

**Plan date:** 26 October 2026. **Status:** prospective; no hours have been logged as worked by creating this plan. Confirmed 10 h/week capacity; **8 focused hours/week scheduled, 2 h/week uncommitted**, approximately 32 focused hours in November. The draft October 2027 charter is [PR #135](https://github.com/abhijith-sivaprasadan/kerala2040/pull/135).

**One-month budget:** WP0 research questions/literature/protocol **22h**, WP1 source/provenance verification **8h**, WP5 manuscript concept **2h**. WP2 modelling **0h**; no unverified source has been admitted and no multi-year ML run should be interpreted as a fresh test now.

| Week | Dates | WP0 | WP1 | WP5 | Total | Verifiable completion evidence |
|---|---|---:|---:|---:|---:|---|
| W1 | 1–7 Nov | 6h | 2h | 0h | 8h | Read nearest 2026 IEEE Indian state-demand paper **full text if accessible**, compare exact target/split/method; check exposure ledger F1/F2/F3 assumptions and initial source manifest location |
| W2 | 8–14 Nov | 6h | 2h | 0h | 8h | Targeted literature matrix expanded toward 15 reviewed references; explicit dated protocol amendments; original source rights and retrieval SHA access log |
| W3 | 15–21 Nov | 5h | 2h | 1h | 8h | Paper A0 data ontology + scientific novelty questions + reproducibility figure/table shells; one-page Paper A outline; enumerate missing ERA5 location-quarter windows |
| W4 | 22–28 Nov | 5h | 2h | 1h | 8h | Literature matrix **at least 20 screened references** with source status; draft fixed RMSE comparison/temporal assumptions; November review meeting and December quarter-source pilot plan |
| **Total** | | **22** | **8** | **2** | **32** | |

29–30 Nov buffer is not extra planned research output. Tracking is based on **actual attention time**, not elapsed agency wait. Do not label these prospective hours as work already completed.

## 27 October prior-art gate amendment (no additional November hours)

[Hunt & Bloomfield (2025)](https://doi.org/10.1088/2753-3751/adc7bc) is a much stronger competitor than initially recognized: their Kerala-specific ERA5/XGBoost/SHAP test result is in the published paper; their openly listed [2014–2024 Grid-India/weather dataset](https://doi.org/10.5281/zenodo.14983362) may be an immediate independent comparator. The accepted fixed Ridge protocol is **not yet locked or run**. Before spending a material number of WP1 hours on additional original ERA5 downloads, try to obtain and hash the actual Zenodo Kerala and corrected-state daily CSV files, confirm licence/date range, and establish whether their `daily_energy_met_MU` and our private original SLDC qualified consumption have comparable observation scopes.

**Do not delay until March to ask whether Paper A is sufficiently novel.** By **30 November**, make a short accept/reframe/no-go decision on whether 'chronologically tested weather gain on original SLDC' offers more than already published work. If the benchmark cannot be downloaded, record that as a source-access blocker, do not substitute values from the literature, and prioritize A0 source-definition audit.

See [detailed critical prior-art assessment](HUNT_BLOOMFIELD_PRIOR_ART_REVIEW_2026-10-27.md).

## Immediate next four actions, in this order

1. **Prior-art overlap (highest ROI).** Review the now-accessible published methods/results of Hunt & Bloomfield (2025), obtain the actual Zenodo Kerala and corrected-energy CSV bytes and compare source definitions. Then acquire authorised full text of IEEE Xplore [document 11468867](https://ieeexplore.ieee.org/abstract/document/11468867/) and complete the comparison matrix in `LITERATURE_MATRIX_v0_1.md`. The 2025 full paper establishes a published Kerala-specific ERA5/XGBoost/SHAP predecessor, so any claim that Kerala2040 is the first must be withdrawn unless carefully narrowed and independently established.
2. **Training-vs-analyst exposure.** Audit past Kerala2040 GitHub history and dated research artifacts to establish if FY2022–23/FY2023–24 were inspected during feature/model development; record `YES / NO / UNKNOWN` with specific commits and dates. Do not upgrade `UNKNOWN` to `NO` by inference.
3. **Source availability snapshot, no downloads by assertion.** Privately verify `kerala2040-source-archive` original gzip and CSV manifest SHA-256, and list actual already-stored ERA5 pre-FY2024–25 sources; only then choose the **smallest missing bounded location-quarter** for a pilot. Keep records outside public CI and site.
4. **Sharpen Paper A0 immediately.** Develop source-field ontology and a two-page A0 prospectus with falsifiable results and a journal novelty threshold by January, so March go/no-go is a decision rather than crisis management.

## User-dependent approvals (not done)

- Sending the already-prepared Kerala SLDC/KSEBL draft to official recipients (requires explicit permission). This is high-upside **parallel** source outreach, not a dependency for daily Paper A.
- Access method for private original SLDC and actual ERA5 files: never commit restricted data to the public repo.
- Select a possible research mentor/expert for **future** methodological review. No person is currently enrolled as a collaborator or reader; do not invent commitments.

## Four-week exit gate — 30 November

Minimum defensible outputs:
- [ ] Paper A RQ and revised protocol v0.2 with all known exposure flags, exact target definition and declared daily-weather-only inference.
- [ ] At least 20 bibliographic screening records (including 2026 Indian states paper); at least 5 full-text methodological/nearest-subject critical annotations **if access possible**; explicitly mark inaccessible papers.
- [ ] A0 prospectus with an honest transferable novelty hypothesis and source-rights-aware tables.
- [ ] A source-availability ledger of the actually obtainable private SLDC and pre-2024 ERA5 original byte hashes, with unverified slots marked blocked.
- [ ] One-page Paper A introduction/problem/contribution sketch without invented numerical claims.
- [ ] Actual time log vs the 32 focused hours planned, and next-month scope if employment or access conditions change.

**Do not treat success as number of commits.** The scientific value is a narrower, falsifiable paper and an audited source route.
