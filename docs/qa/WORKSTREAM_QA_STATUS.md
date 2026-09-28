# Workstream-by-workstream QA status

This document maps the accumulated Kerala2040 work to its scientific role and release status.

## A. Historical electricity / SLDC

### SLDC archive acquisition and five-section audit

**Artifacts:**  
- `SLDC_FIVE_SECTION_2019_2026_SOURCE_AUDIT_2026_09_23.md`
- daily source archives / QA manifests

**Scientific role:** source acquisition and provenance.

**QA verdict:** **GREEN.**

**Reason:** explicit requested-date population, source-date population, section-level presence, contradictions and missingness. Does not silently equate archive completeness with physical completeness.

### FY2024–25 daily balance

**Artifacts:**  
- `CET_HISTORICAL_ELECTRICITY_STORY_2026_09_24.md`
- `SLDC_ADVANCED_DAILY_ANALYSIS_2026_09_23.md`

**Scientific role:** observed daily accounting.

**QA verdict:** **GREEN with accounting-boundary caveat.**

**Defensible output:** observed-day consumption/import/internal-generation seasonality and missing-date coverage.

**Not defensible:** full measured 8,760 chronology or one universal “import dependence percentage.”

### Observed daily PyPSA

**Artifact:** `OBSERVED_DAILY_PYPSA.md`

**Scientific role:** formulation/replay QA.

**QA verdict:** **GREEN S2/S3.**

**Not empirical validation:** matching accounting inputs in an optimization does not independently validate the source data.

---

## B. Hourly demand reconstruction / ERA5

### Original fixed hourly proxy

**Role:** early baseline reconstruction.

**QA verdict:** **SUPERSEDED as preferred shape**, retained as baseline comparator.

### Sparse-extrema / ERA5-sensitive v2

**Artifacts:**  
- `ERA5_WEATHER_SENSITIVE_HOURLY_LOAD_PROXY_2026_09_27.md`
- checksummed v2 demand manifest
- `weather_load_proxy.py`

**QA verdict:** **AMBER / useful and defensible with precise wording.**

**Strengths:**
- preserves observed daily energy;
- chronological holdout of Jan–Mar extrema;
- explicit comparison to strong static shape;
- 11 source-gap dates remain identifiable;
- weather terms produce measurable held-out improvement.

**Weaknesses:**
- not measured hourly telemetry;
- validation conditional on known daily energy;
- fitting pipeline is not yet clearly identified as end-to-end reproducible from current public repo contents;
- coefficients are associational.

**Conference status:** use.

---

## C. Demand scenarios

### CSTEP / CEA / KSERC source families

**Artifacts:**  
- `research_input_selection_v0_2.yaml`
- adequacy evidence files

**QA verdict:** **GREEN.**

**Why:** source trajectories preserved separately; high-case peak-only source is not given invented annual energy.

### Future hourly morph

**QA verdict:** **AMBER scenario transformation.**

Use to test sensitivity, not forecast structural electrification shape.

---

## D. Generator census / installed capacity

**Artifacts:**  
- `GENERATOR_CENSUS_FY2024_25_CLOSEOUT.md`
- `GENERATOR_REGISTER_FY2024_25_RECONCILIATION.md`

**QA verdict:** **GREEN for dated accounting**, subject to category-definition caveats.

Distributed/small-RE reporting boundaries must remain separate.

---

## E. Renewable resource and generation profiles

### Solar/wind source acquisition and visual audits

**Artifacts:** multiple NIWE/NISE/GSA/TIFF/PDF review docs.

**QA verdict:** **GREEN source QA.**

### District solar/wind resource summaries

**QA verdict:** **GREEN as resource descriptors; RED as buildable sites/capacity.**

### ERA5 PV profile

**QA verdict:** **AMBER proxy.**

### ERA5/NIWE wind profile

**QA verdict:** **AMBER proxy with circular NIWE mean anchor.**

### Low/reference/high candidate renewable envelopes

**QA verdict:** **AMBER scenario ceilings.**

Never call them statutory buildable potential.

---

## F. Statewide PyPSA chronological adequacy

### Historical/no-additions baseline

**QA verdict:** **GREEN formulation screen.**

### Future adequacy / v0.8 expansion

**QA verdict:** **AMBER planning screen.**

**Strong inference:** chronology and transfer limits materially affect shortage.

**Weak inference:** exact future unserved GWh.

### Cost-finance layer

**QA verdict:** **AMBER.**

Common real price basis is methodologically good. Exact capex/finance source units still undergoing primary-source page pinning.

### Import economics v1.0

**QA verdict:** **AMBER partial economics.**

Not total-system cost.

---

## G. Cross-framework validation

### custom LP ↔ direct PyPSA

**QA verdict:** **GREEN S4 implementation equivalence.**

### PyPSA ↔ OSeMOSYS common frontier

**QA verdict:** **GREEN S4 implementation equivalence.**

**Explicitly not physical validation.**

---

## H. Hydro / Idukki

### Phase 4 source audit

**QA verdict:** **GREEN.**

Good distinction between reservoir gauge rainfall, reported inflow, generation and storage.

### Phase 4 rainfall–inflow ridge

**QA verdict:** **AMBER statistical diagnostic.**

Chronological holdout is valid, but same-day rainfall means retrospective diagnostic, not forecast. Complete-case sample.

### Hydro v1.1 daily timing

**QA verdict:** **GREEN model sensitivity.**

Very useful for the core argument.

### Hydro v1.2 interday windows

**QA verdict:** **GREEN model sensitivity.**

Useful because it shows where added timing freedom stops solving deeper deficits.

### Idukki v1.3 stateful pilot

**QA verdict:** **AMBER.**

Useful stateful model mechanics; historical closure is algebraic.

### v1.4 direct reported-inflow gate

**QA verdict:** **GREEN methodology, PHYSICAL RUN GATED.**

### v1.4b cumulative/source-informed sensitivity

**QA verdict:** **AMBER sensitivity**, not observed inflow.

### v1.5 official-KSEB source gate

**QA verdict:** **GREEN methodology, RUN GATED by exact source bundle.**

### Phase 5 catchment

**QA verdict:** **GREEN fail-closed research process; NO ADMITTED CATCHMENT.**

---

## I. Public KSEBL network

### public multibus skeleton

**QA verdict:** **GREEN topology/evidence graph.**

### transport-screening inputs

**QA verdict:** **AMBER electrical screen.**

Source-backed where possible; generic X and proxy loads are material assumptions.

### 8,760-hour network screen

**QA verdict:** **AMBER.**

Use for candidate corridor stress only.

### boundary-allocation robustness

**QA verdict:** **AMBER-to-GREEN for tested uncertainty dimension.**

The 21-line statement is numerically reproducible. “Robust” must always name the tested boundary-allocation envelope.

### Shornur transformer

**QA verdict:** **P1 CORRECTION.**

Historical 2023 100 MVA model link is stale as current station representation. 2026 CEA independently corroborates Shoranur as constrained but reports 200+100 MVA existing transformation.

### Shornur / Palakkad / Malappuram line geography

**QA verdict:** **STRENGTHENED by independent CEA corroboration.**

---

## J. GIS / ecology / terrain

### state boundary

**QA verdict:** **GREEN.**

### DEM

**QA verdict:** **GREEN as terrain/DSM.**

### landslide geometry

**QA verdict:** **GREEN QA result; INVALID/INCOMPLETE source layers remain blocked.**

### protected areas

**QA verdict:** **AMBER incomplete legal exclusion stack.**

### wetlands / waterbodies

**QA verdict:** **AMBER context/resource layers.**

### land-use

**QA verdict:** **AMBER historical evidence.**

### buildable renewable MW

**QA verdict:** **NOT RELEASED / RED if claimed.**

---

## K. WP6 flexibility

### EV charging

**QA verdict:** **GREEN synthetic mechanism test.**

### industrial scheduling

**QA verdict:** **GREEN synthetic mechanism test.**

### BESS

**QA verdict:** **GREEN synthetic mechanism test.**

### pumped-storage analogue

**QA verdict:** **GREEN educational physics only.**

### cooling / TES

**QA verdict:** **GREEN synthetic thermal mechanism test.**

### integrated dispatch

**QA verdict:** **GREEN synthetic integration demonstration.**

None supports statewide achievable MW.

---

## L. Total Energy Atlas

### historical final energy

**QA verdict:** **GREEN historical context, source discrepancy retained.**

### PPAC petroleum sales

**QA verdict:** **AMBER where FY2024–25 remained secondary transcription / page-image validation pending.**

### sector GHG context

**QA verdict:** **GREEN if exact inventory year/boundary remains visible.**

Do not merge different years into a single “current” energy balance.

---

## M. KMML / circular industry

### official qualitative process topology

**QA verdict:** **GREEN.**

### historical acid-regeneration / recovery leads

**QA verdict:** **GREEN as historical research leads.**

### current material/energy/water balance

**QA verdict:** **NOT AVAILABLE.**

### quantified current savings

**QA verdict:** **RED if claimed.**

KMML should remain a supporting case, not a headline quantitative result.

---

## N. Kerala context / international orientation

### area / population / per-capita electricity

**QA verdict:** **GREEN after projection vintage clarified.**

Use 2026 projected population 36.207m from the current Economic Review series.

### Sweden comparison

**QA verdict:** **GREEN context only.**

No development/efficiency ranking.

### heavy-mineral sands

**QA verdict:** **GREEN descriptive.**

Use “monazite-bearing heavy-mineral sands around Chavara,” not “Kerala's beaches are thorium beaches.”

---

## O. CIAL / Metro / Water Metro

### CIAL

**QA verdict:** **GREEN first-party case study.**

### Kochi Metro 5.389 MWp

**QA verdict:** **GREEN historical/documented project configuration; AMBER if presented as total current 2026 capacity.**

### Water Metro 17 MWp

**QA verdict:** **GREEN envisaged statement; RED installed-capacity claim.**

---

## P. Budgets / SEK orientation

### Kerala 2025–26 power outlay

**QA verdict:** **GREEN.**

### PSP ₹180/₹573 crore

**QA verdict:** **GREEN early estimates.**

### SEK equivalents

**QA verdict:** **GREEN contextual arithmetic if FX date shown.**

### “low-budget but high quality”

**QA verdict:** **RED as generalized claim.**

Use “capital-constrained / budget-conscious engineering” instead.

---

## Q. Main synthesis

### “Kerala's stress is an interaction of chronology, hydro, transfer and internal deliverability”

**QA verdict:** **AMBER but scientifically defensible as a synthesis hypothesis.**

It is stronger than any single model because:

- historical demand/import trends are source-based;
- chronology/weather has held-out shape evidence;
- hydro timing sensitivity is large and conditional;
- transfer sensitivity is clear;
- current CEA planning independently corroborates several transmission hotspots.

It is weaker than a causal event reconstruction because the evidence strands are not one synchronized operational dataset.

---

# Release recommendation

For CET 2026, the project should present only three evidence tiers visually:

1. **Observed / official**
2. **Reconstructed / screening**
3. **Future / needs validation**

Do not add more numerical detail merely because it exists in the repository. Expert confidence will come from clear boundaries, not from maximum chart density.
