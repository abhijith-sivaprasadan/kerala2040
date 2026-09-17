# Kerala 2040 research plan

## Research question

How can Kerala substantially reduce structural energy/electricity import dependence and hydrological vulnerability by 2040 while remaining strongly interconnected with India, protecting ecological carrying capacity, staying within realistic state fiscal constraints, creating circular industrial value, and attracting viable public/private investment?

## Work packages

### WP0 — Baseline and provenance
Build a dated, auditable energy and grid baseline. This is the gate for every later result.

### WP1 — Demand and AI forecasting
Long-term 2030/2035/2040 demand pathways plus short-term load, solar, wind and hydro-inflow forecasting. Start with seasonal-naive/statistical baselines, then LightGBM/XGBoost. Deep models are permitted only if rolling-origin validation shows real improvement.

### WP2 — PyPSA energy-system model
First a one-bus historical model, then a reduced zonal Kerala network. Optimise generation, imports/exports, storage, hydro, flexible demand and candidate technologies.

### WP3 — Grid intelligence and resilience
Use pandapower for AC validation and N-1 checks when network parameters permit. Add OpenDSS only if feeder-level data is obtained. Study storage placement, grid-forming inverters, microgrids and critical-load islanding.

### WP4 — Hydro, climate and water
Use observed weather/reservoir data first. Post-CET, build SWAT+/QSWAT+ hydrology and 2031–2050 climate ensembles. Treat hydro as strategic flexibility, not automatically baseload. Keep Mullaperiyar as a factually careful water-governance risk case, not as Kerala-owned generation.

### WP5 — Ecology and land
Use QGIS/GeoPandas/Rasterio for hard and soft constraints. Post-CET use InVEST for ecosystem services and Marxan with Zones for conservation-compatible allocation. Feed realistic technology maxima back to PyPSA.

### WP6 — Storage and flexibility
Compare BESS durations/locations, pumped storage using suitable existing infrastructure, strategic reservoir operation, thermal storage, EV smart charging/V2G and industrial flexibility.

### WP7 — Circular industrial metabolism
Create a Kerala resource-recovery atlas. Start with KMML, TTPL and FACT. Enforce the hierarchy: prevention > reuse > material/chemical recovery > biological conversion > energy recovery > safe disposal.

### WP8 — Finance and federal value capture
Separate whole-system cost, Kerala-government fiscal exposure, KSEBL investment, Union/central-PSU support, private capital and green/development finance. Model financing cases rather than assuming the state pays everything.

### WP9 — Technology opportunity screen
Screen rooftop/floating/ground PV, wind, marine energy, CSP, biomass routes, storage, ports, grid services and conditional SMR/nuclear pathways. Technologies enter the model only after resource, grid, ecology, cost and regulatory screening.

## Government engagement

Use a staged approach:

1. independent baseline/prototype;
2. targeted data requests and technical validation;
3. post-CET briefings to relevant agencies/PSUs if the model is defensible;
4. collaboration/MoU only where deeper non-public data is needed.

Do not imply Government of Kerala endorsement without explicit permission. Separate public records from privileged/confidential material and document provenance.

## CET 2026 sprint gates

1. Repository and source manifest.
2. Historical power dataset and annual balance.
3. 8,760-hour PyPSA baseline passes calibration.
4. 2040 demand range and three first scenarios.
5. Grid-intelligent/flexibility scenario.
6. Initial ecological/resource map.
7. Common stress tests and transparent metrics.
8. Finance split + one circular-industry prototype.
9. Poster figures and source audit.
10. Reproducible release candidate.

Anything not validated by the poster freeze becomes explicitly labelled future work.
