# Kerala2040 — multi-round literature review programme

**Prepared 27 October 2026.** Derived from the 19-document / 520-PDF-page-position corpus and targeted public-source discovery. **Absence from the initial 19-document sample is not evidence of absence from scientific literature.** The existing [cross-paper synthesis](CROSS_PAPER_SYNTHESIS_2026-10-27.md) and [23 October evidence freeze](../RESEARCH_FREEZE_2026-10-23.md) remain valid.

## Three different uncertainties

- **Corpus gap:** specific literature, source reports or methods have not yet been included. Requires a scoping search.
- **Research gap:** a defensible unresolved question after the broader literature has been searched. Requires comparison with the closest methods and existing evidence, not merely a novel tool.
- **Evidence gap:** data or metadata needed to answer the question are missing, incompatible, inaccessible, not observed at the resolution required or lack validation. Requires acquisition and integrity work, possibly a reduced claim.

## Priority order for planned review rounds

| Round | Domain, research question | Initial 19 coverage | Review type | Expected output / evidence gate | Phase |
| --- | --- | --- | --- | --- | --- |
| 0 | Definitions, demand estimands and historical source accounting: which exact reported quantities are comparable? | Partial: CEA, CSTEP, WRI, Harish, Hunt | Source-critical + official-data scoping | Definitions/units/timezone/historical coverage matrix; served vs unrestricted; losses and imports; error flags | A / P0 |
| 1 | Primary Kerala daily/hourly load, generation and peak reconstruction: what can actually be measured and at which time resolution? | Weak despite planning reports | Evidence/data availability review | Verified actual vs reconstructed chronology, peak and grid accounting, permissions; retain 353 matched daily observed cohort | A / P0 |
| 2 | Weather-conditioned demand, forecast origin, causal data transformations, out-of-time validation: how much skill survives? | Strongest current category; Hunt, Harish, Babu, Sesay and forecasting reviews | Systematic methodological review + reproducibility | Split/feature-availability matrix; baseline definitions, leakage tests, reported metrics on comparable targets | A / P0 |
| 3 | Kerala hydro, reservoir physics, operating policies, floods, ecological obligations: what is flexible and on what timescale? | One generic systematic hydro review | State-specific hydrology/operations and modelling scoping | Reservoir/storage/inflow/head/power/release map; operating rules and 2018 disaster context; no fictitious dispatch | A / P0 |
| 4 | Transmission, interstate interfaces, import contracts, power transfers, N−1: what physically and contractually limits imports? | One two-node CEA generation RA study | Official network planning + power engineering | Locate/review CEA Kerala **transmission RA up to 2034–35**; transfer capability definitions and topology data; do not equate contracts with firm delivery | A / P0 |
| 5 | Solar/wind GIS viability, terrain and land/roof constraints, deliverability, weather profiles | Only three planning pathways and ERA5 methods | Geospatial scoping + technology evidence | Realizable-vs-theoretical resource hierarchy, masks, protected land, coastal/Western Ghats effects, connection constraints | B / P1 |
| 6 | Compound monsoon demand/solar/wind/hydro/import events: coincidence, chronology and tail dependence | Hunt national weather composites; conceptual methods | Weather–energy multi-hazard review | Event definition with common energy units, duration, joint probability, hydrology and dependencies; not z-score 'unserved MU' | B / P1 |
| 7 | Storage: batteries, pumped hydro, reservoir flexibility, duration, capacity credit and revenue stacking | CSTEP storage ambiguity, one hydro review, planning statements | Engineering/economics and current regulation | MW/MWh/efficiency/losses, alternatives, duration reliability, site constraints and cost assumptions; resolve CSTEP energy-unit discrepancy | B / P1 |
| 8 | Resource adequacy, dispatch modelling, stochastic stress testing, LOLE/EENS and import contingencies | CEA baseline + uncertainty/modelling reviews | Technical methodology + comparative study | Reliability metrics and reference systems; link hourly load, hydro, imports, unit constraints; current project remains exploratory | B / P1 |
| 9 | EV charging, residential cooling, electrification, rooftop PV/prosumers and structural load-shape change | Babu + Harish and Hunt; limited Kerala-specific high frequency | End-use and policy review | Separate adoption/usage assumptions, load-shape evidence, geography, equity and uptake uncertainty; 2023 profile scaling is not a future forecast | B / P1 |
| 10 | Distribution and consumer-side reliability, AT&C loss, outage burden, smart metering and demand response | Largely absent | Official performance data + engineering/social evidence | SAIDI/SAIFI/outage scope, feeder evidence and T&D loss boundaries; distinguish grid blackout from localized distribution interruption | B / P1 |
| 11 | Tariffs, procurement, PPA economics, market/ancillary services, import dependency and affordability | Very sparse | Regulatory/economic review | Current tariff orders, trading contracts, marginal/capacity cost, stranded contracts, risk and distributional effects | C / P2 |
| 12 | Climate-change adaptation, extreme rainfall, landslide/flood exposure, monsoon shifts and asset vulnerability | ERA5 plus a few weather-demand papers | Multi-hazard climate/engineering review | Failure pathways by generation/transmission/distribution, vulnerability and source-qualified climate scenarios | C / P2 |
| 13 | Long-horizon pathways, sector coupling, uncertainty, geospatial feasibility and 2040 claims | CSTEP/WRI/CEA + generic optimization | Integrated scenario-review | Cross-report harmonised assumptions; scenario families not a 'consensus forecast'; bounded claims until physical validation | C / P2 |
| 14 | Governance, land/forest/biodiversity constraints, equity, community response and just transition | Very weak | Interdisciplinary policy and environmental review | Social/land/legal constraints and beneficiary groups; source rights and consultation evidence | C / P2 |
| 15 | Open science, reproducibility, software QA and independent model assessment | Strong methodological foundations but local implementation needs | Protocol/standards review | Evidence manifest, code and model governance, data rights and independent replay, versioned DOI without implying scientific validation | Cross-cutting |

Phase A protects the current historical evidence study; Phase B prepares testable joint power-system research; Phase C supports policy and long-horizon claims only after data gates.

## Highest-value interfaces (potential specific original studies)

1. **Served load vs latent demand + measurement consistency + temporal split:** How do official source boundaries and preprocessing change the estimated weather association and out-of-time model performance?
2. **Monsoon reservoir state + hydro generation + firm import capability:** Which historical episodes constrain physically feasible balancing? Need observed inflow/storage, import and time-matched generation before adequacy language.
3. **GIS renewable availability + demand coincidence + connectability:** Can high-potential resource cells actually provide useful output during Kerala stress hours, under land and network constraints?
4. **Extreme weather + distribution/transmission vulnerability:** Distinguish demand-induced system stress from outages caused by flooding, equipment failures, distribution networks and restricted supplies.
5. **EV/cooling/rooftop PV + changed hourly peaks + storage value:** Test with measured profiles and scenario ranges, not a single scaled historical shape.

These are **research hypotheses**, not established claims of novelty or tested findings.

## Research workflow for every round

**Pass 1 — gap discovery.** Query scholarly databases/publishers plus CEA, CERC, KSERC, KSEB, SLDC, Grid-India, IMD, GSI and institutional publications as relevant; record exact queries, search date and hit counts; deduplicate titles/DOIs/reports. Search directly adjacent states/countries when transferable mechanisms are the real question. Seed from all relevant original corpus references.

**Pass 2 — screening.** Predefine research question, outcome and time resolution; include state/regional case studies, physical/econometric methods, source reports, contrasting findings and negative studies; record exclusion reasons. Peer-reviewed papers and regulatory reports are **different evidence classes**, not two versions of the same thing.

**Pass 3 — full-text technical audit.** Record PDF version/pages examined individually or by paired surveys, figure/table/equation/references inspected, source claim with exact page, numerical checks, code/data availability, limitations and unverified elements. Page rendering alone never counts as a completed individual inspection. Explicitly tag source-derived finding, external corroboration, and project hypothesis.

**Pass 4 — gap verification.** For each potential gap, identify at least its closest comparator, boundary, validated observations, conditions under which it is already solved, new contribution, data required, and a falsifying result. Then classify as **confirmed research gap**, **underreviewed corpus gap**, **data-limited**, **well covered**, or **out of scope**.

**Pass 5 — integration.** Update cross-paper matrix, source/rights and DOI registry, evidence gates, and Kerala2040 action register. No silent change to frozen reported figures or physical adequacy claims.

## Extraction columns for a shared evidence matrix

`paper_id, doi_or_official_url, source_type, version, publication_date, scope, Kerala_specific, geography, physical_boundary, target_definition, output_units, time_resolution, temporal_coverage, input_data_origin, validation_split, forecast_origin_information, modelling_method, assumptions, claimed_findings, numerical_check, causal_or_predictive, uncertainty, replication_material, source_rights, author_limitations, reviewer_qualifications, relevance, proposed_test, gap_status, original_page, confidence`.

## Initial external additions needing full review, not yet admitted as audited papers

- Central Electricity Authority, **Resource Adequacy Plan for Transmission System of Kerala up to 2034–35**, indexed on official transmission RA catalogue: https://cea.nic.in/transmission-resource-adequacy-report/
- CEA **National Generation Adequacy Plan (2026–27 to 2035–36)** from generation-RA catalogue: https://cea.nic.in/generation-resource-adequacy-study-reports/
- Kerala Electricity Regulatory Commission decision regarding KSEBL resource adequacy (verify official final versions and assumptions).
- **Granular Analysis of Weather-Influenced Electricity Demand in Indian States** (2026, IEEE); daily Grid-India data, April 2023–October 2025: https://ieeexplore.ieee.org/abstract/document/11468867/
- Babu et al., **Assessing climate change-induced variability in generation potential and droughts of renewable energy systems in India** (2026), Applied Energy 404, article 127173: https://doi.org/10.1016/j.apenergy.2025.127173
- Singh et al. (2025), **A critical review of flood risk assessment in Kerala Post-2018**, Journal of Hydrology: Regional Studies 58, article 102262: https://doi.org/10.1016/j.ejrh.2025.102262
- Forum of Regulators reports on **hydropower/pumped storage (2025)**, resource adequacy and discom finance: https://forumofregulators.gov.in/Study_Reports.html
- CEA **Report on Metering Status of Feeders, Distribution Transformers and Consumers (2026)**: https://cea.nic.in/report-on-feeders-dts-and-consumers-metering/
- Indian Ministry of Power July 2026 **Grid Stability and Energy Storage** release (current rules and national capacity outlook, not a Kerala feasibility proof): https://www.pib.gov.in/PressReleasePage.aspx?PRID=2290015
- Long-term load-forecasting uncertainty review (Journal of Forecasting, 2025; https://doi.org/10.1002/for.3248); and recent renewable weather-regime synthesis (Renewable and Sustainable Energy Reviews, 2026, https://doi.org/10.1016/j.rser.2026.117034).

**Suggested next action:** Execute *Round 0 + Round 1* as a combined source/measurement review, and in parallel begin *Round 4* with the newly discovered Kerala-specific CEA transmission document. Only then broaden the modelling research. 
