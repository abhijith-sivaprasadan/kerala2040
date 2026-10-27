# Paper A — initial source, prior-exposure and eligibility register

**As of:** 26 October 2026. This is a **document inventory**, not direct independent reinspection of the restricted daily source archives or newly downloaded Copernicus data. Original-byte eligibility must be tested against the actual files before study admission. Public original scientific findings remain frozen at 23 October 2026.

## 1. Known data families and critical distinctions

| ID | Source and established evidence | Current status | Next check / prohibited inference |
|---|---|---|---|
| S1 | Kerala SLDC private `kerala2040-source-archive`; **2,606 dated original archive rows** reported in `docs/MULTIYEAR_DAILY_RESEARCH_GATE.md` | Private curated source, original and gzip SHA admission tool already implemented; actual original file access **not verified in this sprint** | Recompute SHA for real originals and accepted target count; 2,606 dates are **not** automatically all qualified values |
| S2 | Kerala SLDC FY2024–25: **354/365** daily reports observed, 11 unobserved; 353 dates matched with FY2024–25 complete IST-day weather | Source-audited within-year public 2026 freeze | Never use these daily rows as observed hourly/15-minute load or infer a complete annual observation |
| S3 | State Planning Board Economic Review 2025 annual **consumer-side** reported consumption, FY2024–25 29,311.76 MU | Official published annual metric under different system definition | Cannot be treated as the annual sum of SLDC daily operational consumption, nor subtraction used to infer imports |
| S4 | FY2024–25 **ERA5**: 5 points × 4 location-quarters = 20 source request windows; 8,760 UTC hours per representative location, 43,800 point-hours in previously verified source QA | Existing separately recorded original source QA; not an admitted future model or state-wide meteorological map | Check original ZIP/member bytes remain available, source hash lineage, representative point/grid geometry, accumulated-variable interpretation and IST day support |
| S5 | ERA5 for FY2020–21 to FY2023–24 inclusive, five points | **NOT_ADMITTED / not verified as a complete original-source multiyear weather input** | Nominal **80 location-quarter windows** beyond existing 20, not 80 guaranteed NetCDF files; respect CDS limits, provenance and archive retention |
| S6 | Existing ML v0.1/v0.2 FY2024–25 experimental targets and held-out monthly performance | **Previously seen** by project analyst; model choices may have been influenced by this period | Treat F3 as analysis-exposed and benchmark only; never assert newly untouched out-of-sample replication |
| S7 | Kerala measured state 15-minute or hourly load+actual interchange, complete FY2024–25 | **NOT_ADMITTED** (issue #130) | SLDC custodian data request exists **as a draft**, unsent; do not invent interval telemetry, hour-by-hour demand or true shortage outcomes |

## 2. Fiscal-year chronological split vs analyst exposure

**Key:** `TRAIN_PAST_ONLY` describes time order used to fit a particular model, not independent confirmation or absence of human reuse. `UNKNOWN` is not `NO_EXPOSURE`.

| Fold | Target test period | Training endpoint | Training split property | Analyst prior access/exposure | Eligible scientific interpretation |
|---|---|---|---|---|---|
| F1 | 2022-04-01..2023-03-31 | 2022-03-31 | `TRAIN_PAST_ONLY` by existing code, pending executed validation | **UNKNOWN:** past Kerala2040 feature/model choices may have been influenced by later data; no clean blind status verified | Conditional retrospective chronological result **if** original-source chain passes |
| F2 | 2023-04-01..2024-03-31 | 2023-03-31 | `TRAIN_PAST_ONLY` by existing code, pending executed validation | **UNKNOWN:** same concern; inspect project history and prior exploratory analyses | Conditional retrospective chronological result **if** source chain passes |
| F3 | 2024-04-01..2025-03-31 | 2024-03-31 | `TRAIN_PAST_ONLY` by existing code, pending executed validation | **YES — analysis exposed** by FY2024–25 v0.1/v0.2 tuning, ablations and rolling tests | Retrospective sensitivity/replication, **not** prospectively untouched confirmation |

**Reviewer action:** audit dated GitHub commits/previous notebooks/explorations, source-vintage dates, and prior test-variable choices. Log **specific** exposure evidence and code SHAs for F1/F2 instead of marking these 'clean' by assertion. If a genuinely untouched later test becomes available, lock its decision rules *before* analysis.

## 3. Original-file admission checklist for each independent dataset

- [ ] Exact author/publisher, provider record/product type, source URL and citation.
- [ ] Legal collection/access and rights to release original or derived rows; if unknown, private by default.
- [ ] Original response/file SHA-256, decompressed SHA-256 when relevant, retrieval timestamp, version/revision.
- [ ] Dates and hours in source timezone and mapped IST calendar with explicit interval-start/end semantics.
- [ ] Duplicate, missing or superseded records, invalid/zero source values and **no silent imputations**.
- [ ] Kerala/consumer/operational/regional geography and energy accounting boundary documented for each variable.
- [ ] SLDC original and processed energy-balance-qualified target restrictions enforceable by code.
- [ ] ERA5 full five-point panel and each hourly source member independently reverified; grid interpolation/selection documented (Kannur historical requests may return multiple source grid cells).
- [ ] Provenance linkage from model-ready normalized Parquet to original ZIP/NetCDF; hash of the Parquet alone is insufficient.
- [ ] Weather accumulation deconvolution / unit conversion / IST day integration verified; local-day timestamps alone insufficient.
- [ ] Artifact location, access constraints, validator version and signed admission decision.

**Evidence status now:** Paper A **data gate blocked** until S1 authentic private bytes are rechecked and S5 original multiyear ERA5 source files are verified. Code tests passing is software QA, not access to or validation of new observations.

## 4. Immediate acquisition routes and approvals

**Can proceed without authorization to contact third parties:** re-check public repository metadata, catalog original hashes and rights, research verified published papers, test synthetic validator logic, and identify required Copernicus quarter/point source windows. A CDS download requires a legitimate account/licence acceptance and quotas; do not assume successful request by writing a manifest.

**Requires explicit research-owner authorization before transmission:** the prepared SLDC/KSEBL request to `ceso@kseb.in` (cc `dcegrid.sldc@kseb.in`). Sending is *not* implied by saying 'start research work'. Original hourly load is a **parallel high-upside acquisition**; no SLDC reply is assumed in Paper A's daily-weather critical path.

**Initial external dependency calendar:** send requests only when authorized; record elapsed wait separately from researcher hours; after nonresponse pursue documented official data-access routes, no fake replies or source claims.

## 5. Immediate next provenance action

Locate the private original `daily_system.csv.gz`, its exact private manifest and authorised access path (without copying restricted rows to a public branch). Inspect SHA **locally or private-side**. Separately list which pre-2024-year ERA5 originals, if any, actually exist, with their original SHA, data licence, points and date windows. Only then schedule authenticated CDS retrieval for the genuinely missing windows.
