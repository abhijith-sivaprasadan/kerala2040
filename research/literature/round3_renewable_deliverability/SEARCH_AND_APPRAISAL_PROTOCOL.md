# Round 3 — search, screening and critical-appraisal protocol
**Date searched:** 2026-10-28 (Europe/Stockholm). **Status:** exploratory transparent narrative/scoping search. Not a PRISMA-compliant systematic review, comprehensive bibliometric census or registered protocol. All 33 records are **candidate screening rows**, not 33 completed full-paper analyses.

## Separation from earlier literature rounds

- **Round 1:** Kerala/India demand weather models, energy statistics/accounting, temporal validation, general system methods and transition reports. Canonical 44-source matrix: `publication/literature/EVIDENCE_MATRIX.csv` on open PR #138 branch.
- **Round 2:** Kerala hydropower/reservoir operation, monsoon variability, flood-control against generation, physical flexibility and water/power interactions; 40 previously screened and full-paper appraisal still in progress at Round 3 creation. **No assumption the 40 are full-text reviewed.**
- **Round 3:** Solar/wind **deliverability**, PV feeder hosting capacity, **curtailment**, BESS/grid flexibility and transmission allocation. It may cite the Round 2 reservoir interface as background, but excludes reservoir operational physics as a screening objective.

## Search log (conducted on 2026-10-28)
Searches were exploratory public web/publisher discovery, not a reproducible Scopus or Web of Science export. Listed query-family examples are representative of searches actually used. Date and access limitations are recorded to prevent invented comprehensiveness.

| Query family | Queries / terms used | Intended population |
| --- | --- | --- |
| Kerala rooftop and network | `Kerala distribution grid rooftop solar hosting capacity study KSEB`; `Kerala renewable energy integration transmission bottleneck PV curtailment storage` | Kerala-specific field evidence and potential false positives |
| India curtailment | `India wind solar curtailment transmission congestion empirical 2021 2024 DOI`; `solar PV curtailment Karnataka economic dispatch` | Empirical policy and grid curtailment |
| India integration | `India power system renewable regional coordination transmission storage DOI`; `India southern region high resolution RE integration 15 minute` | Indian transmission/dispatch models |
| LV feeder methods | `distribution network PV hosting capacity probabilistic review`; `chance constrained hosting capacity real feeder` | Empirical feeders, voltage/ampacity and uncertainty |
| Regulatory / primary | `Kerala State Electricity Regulatory Commission renewable 2025 hosting capacity`; `KSEB eKiran rooftop metering`; `CEA transmission plan 500GW 2030` | Dated original policy/utility and transmission context |
| Recent literature | `renewable energy curtailment review 2026`; `India BESS distribution grid 2025 2026` | New methods and time-sensitive developments |

Source-site verification included **publisher article or DOI landing pages**, IEA, NREL, CEA/MoP/PIB, KSEB E-Kiran, Kerala State Planning Board, CEEW and Ember. Full PDF source-page and figure audits have **not** been undertaken in Round 3.

## Candidate inclusion

1. Direct Kerala or other Indian context for *generation delivery, curtailment, feeder hosting or power-network-constrained flexibility*; or internationally generalizable foundational methods that specify real-network tests and limitations.
2. Research article or structured methodological review with DOI from a credible journal/publisher, or clearly labelled official/regulatory/industry comparator.
3. A distinct causal/measurement/design contribution relevant to at least one of R3-Q1 through R3-Q4.
4. Publication dates primarily 2021–2026; earlier NREL/IEA reports retained intentionally as background benchmarks.
5. Keep rival explanations and negative cases (e.g. transmission overbuild) to mitigate intervention-favouring selection.

## Exclusion / deferral

- Studies about **hydro reservoir operation/flood-control physics** with no independent PV/grid deliverability result (Round 2).
- Generic optimisation algorithm competitions using synthetic buses only, when no physical operational/validation gate is documented; may be retained as low-priority methodology if clearly relevant.
- Forecasting accuracy / same-day weather–daily demand papers with no explicit RE integration constraint (Round 1).
- Marketing articles, journalism-as-primary-telemetry, unverified personal blog numbers and studies with undisclosed units.
- Numerical results duplicated across state or national studies under different targets treated as a cross-study performance leaderboard.
- **Legal draft text as effective regulation**: require actual Gazette notification and current court/order status.
- Older duplicate or reprinted versions: key on DOI, normalize title and check with Round 1 and Round 2 bibliographies before full-text acquisition. Round 2 identity-level deduplication remains *pending*.

## Access and evidence state (keep independent)

- `publisher_metadata_or_abstract`: bibliographic record and publisher abstract available (all Round 3 peer-reviewed entries currently).
- `official_web_summary_or_metadata`: official institutional policy/record listing or web summary available (Round 3 official entries currently).
- `fulltext_obtained`: original source bytes or publisher complete HTML actually retrieved; date, hash and legal access route recorded.
- `figure_methods_inspected`: numerical source tables, figure captions, source references, data model, inference and limitations checked.
- `critically_reviewed`: explicit claims, counterevidence, potential confounders, page references and reviewer uncertainties entered in an appraisal form.
- `independently_reproduced`: published code/data actually run and checked, never inferred from presence of GitHub URL.
- `field_validated_kerala`: original Kerala observations and independent calibration; cannot be conferred by literature.

Only the first two states are justified at this point. **Full-text appraisals completed this round: 0 / 33.**

## Full-text extraction sheet (one document per paper)

Required fields for each:
- Citation: complete authors, exact title, type, article version, DOI, permanent publisher URL, year, copyright/licence, access route, source-byte SHA if applicable.
- Study object: measurement site and geography, time period, sampling resolution, and all **observed** source variables/owners.
- Outcome definition: installed MW, available potential MWh, produced MWh, grid-exported MWh, curtailed MWh, voltage limit, probability of violation, etc.
- Technology and network: solar/wind nameplate AC/DC boundary, battery MW/MWh, feeder and corridor impedance/rating, time-varying dispatch and control.
- Empirical identification: genuine operator telemetry, metered plant data, utility operations, synthetic profile, source-linked proxy, calibrated model or pure hypothetical.
- Validation: actual versus scenario, chronological tests, held-out period, external feeder/corridor tests, calibration error and independent uncertainty.
- Distinguishing result: what is claimed in the authors' results, a page/table citation, what contradicts or narrows it, and **whether it is transferable to Kerala**.
- Red lines: no inferred load-shedding, true N-1 or LOLE from public mapping; no climate-resource profile called actual generation; no battery throughput called installed capacity.
- Publication status: included/rejected/deferred with dated reason; if insufficient access, mark *screening only*.

## Priority rubric (for queue management, not a quantitative quality or bias tool)
Use 0–2 points each: (a) direct India/Kerala scope, (b) real-world source transparency, (c) independently checked physical network constraint, (d) usable contrast/counterfactual, (e) replicable data/code availability. Record **unknown** where source unseen; never automatically score unknown as verified zero. Rank core papers partly by expected relevance until full-text values are extracted.

## Audit/reporting rules

1. Preserve publication bibliographies and file hashes; never commit copyrighted third-party full PDFs.
2. Do not derive new Kerala physical conclusions from screened abstracts.
3. Count searches, full text actually obtained, and fully appraised separately. No fictional PRISMA counts or double-blind review.
4. Record negative/contradictory evidence and sources requiring legal or data-quality verification.
5. Cross-round deduplication: compare DOI IDs against 44-entry Round 1 matrix and Round 2's 40-row table once accessible; mark overlap without deleting reference value.
6. Keep this branch separate from paper-analysis branches. A review PR does not modify the 23 October 2026 scientific freeze or add third-paper work.

## Intended gated output

Round 3 is complete as a **screening package** when matrix, protocol and critical scoping note are archived. A later **full-paper review** is complete only after originals are critically inspected and the nearest 8–12 have adequate methods/figure/source appraisals. Even then, this is literature groundwork, not permission to claim Kerala physical hosting capacity without admitted measured data.
