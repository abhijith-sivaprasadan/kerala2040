# Kerala 2040: data and modelling readiness roadmap

Prepared 18 September 2026 from the repository evidence bundle and official model documentation. This is a readiness assessment and proposed work sequence, not a claim that the models have been calibrated. Source connectivity results below are the stored 18 September audit, not fresh tests of every service.

## Scope and first deliverables

The electricity study covers all Kerala. A one-bus model aggregates the entire state; it does not represent Kochi alone. Later electrical zones should follow network connectivity and available data, rather than automatically assigning one bus per district. KMML, Chavara, is the selected industrial case within the statewide study.

First deliverables: a reconciled historical electricity balance; an hourly statewide operational model; a mapped ecological/resource screening; and a KMML material-energy-water baseline. Then compare 2040 pathways. Demonstration runs with assumed data can start earlier but must remain explicitly labelled demonstrations.

## Actual source gaps

| Dataset/source | Current evidence and problem | Required action |
|---|---|---|
| SLDC daily accounting | 354 of 365 days for FY2024-25; 11 missing days. The passed gate checks daily coverage/accounting only. | Recover missing records and reconcile annual totals. Observed-day totals are not complete-year totals. |
| SLDC interval electricity | No authenticated full-year Kerala demand and interchange chronology in the bundle. | Request interval demand, actual imports/exports and generation; keep scheduled interchange separate. Use the existing request draft. |
| ERA5 | Five January-March 2025 point files succeeded; five April-December 2024 requests failed with “cost limits exceeded / request too large.” | Split requests into smaller time windows, complete coverage, decode accumulated variables correctly, and build hourly generation profiles. Five point boxes do not establish statewide resource potential. |
| NASA POWER | Prior acquisition is recorded, but raw hourly series is not in the site. The bare-endpoint audit returned 422. | Recover/rebuild the artifact and validate a parameterised request. A bare endpoint error does not establish an outage. |
| GRID-INDIA | Stored API probe failed with connection reset; processed fiscal-year rows absent. | Recover official files through supported downloads and cross-check coverage. National daily/interval data cannot substitute for Kerala interval demand. |
| KSEB project portal | 70 distinct parsed project records versus 87 portal entries; tracker is not a validated commissioned asset register. | Reconcile omissions, duplicates, project status, commissioning dates and actual capacities with official station/planning records. |
| KSDMA | Six download links catalogued; no complete aligned analysis-ready GIS stack demonstrated. | Acquire rasters and district shapefiles, inventory actual spatial coverage and process metadata. Catalog count is not ecological completeness. |
| Bhuvan / Forest Department | Sources identified; authoritative boundaries and analytical layers still need acquisition. | Obtain actual data and usage terms. A web map or WMS image is not automatically an analytical dataset. |
| India-WRIS, NIWE, ICED, VAHAN | Stored connectivity audit failed; datasets are not established model-ready inputs. | Retry official download interfaces or request specific exports. Resolve access separately from data suitability. |
| data.gov.in | Restricted probe; required resource IDs not configured. | Identify individual datasets, resource IDs, dates, schemas and permitted downloads. An API key alone is insufficient. |
| Reservoir storage | Prior chronology recorded; usable local model inputs need recovery. | Add inflows, releases, spill, rule curves, head/storage relationships and constraints. Storage percentages are not inflow. |
| KMML / KSPCB | Public references are partial; no validated facility mass/energy balance. | Request production-aligned operating data, residual characterisation and environmental records. |
| KSERC / CEA / economic reports / PPAC | Useful reference sources, but no complete harmonised technology-cost and non-electric-energy dataset established. | Compile dated tables with consistent boundaries, currency year, units and scenario assumptions. |

Update after the historical rebuild: run 35389201853 completed successfully and its processed SLDC daily/storage, NASA POWER, calibration and hourly-proxy artifacts have been recovered locally. The public bundle now includes the full 8,760-hour reconstructed load series and diagnostics; it remains a proxy, not measured telemetry or independent validation. The bundle builder now records the actual Git revision. ERA5's revised three-month requests are still running in the extended refresh, so completion is not yet established. Earlier source-gap descriptions above describe the acquisition starting point; use the published layer status and run artifacts for the latest coverage.

## Inputs to the first statewide PyPSA model

Use FY2024-25 as the initial shared historical period: 8,760 hourly or 35,040 quarter-hour intervals. Store explicit timezone/interval semantics; hourly UTC weather must be aligned correctly to IST, including boundary periods.

1. **Demand:** interval average MW, timestamps, quality flags, measured/synthetic status and system boundary. Resolve whether rooftop PV, captive generation, losses and unserved demand are included. Obtain historical sectoral sales and drivers for future demand separately.
2. **Generation:** commissioned MW by plant/technology, fuel, availability/outages, operational limits and observed production for validation. Include retirement and candidate commissioning assumptions for future scenarios.
3. **Solar/wind:** synchronised hourly capacity factors by representative resource zone or candidate cluster. Convert weather using documented PV/turbine specifications and losses; validate against observations where possible. Use multiple historical weather years later.
4. **Hydro:** station MW, reservoir energy/water limits, inflows, releases/spill, initial and terminal storage, seasonal rules, cascade connectivity and competing water uses. If only monthly energy limits exist, use an explicitly simplified hydro model and report its limits.
5. **External system:** import/export capacity limits, contracted supply and market purchase assumptions, prices, availability and stress conditions. Historical interchange is a validation series; future interchange is an endogenous decision subject to constraints.
6. **Storage:** separate MW and MWh, charging/discharging efficiencies, self-discharge, lifetime/degradation/replacement assumptions, initial/final state of charge and costs. Storage discharge must not be counted as newly generated clean energy.
7. **Economics:** capital, fixed/variable operating and fuel costs, currency/base year, lifetime and discount assumptions. Apply annualisation exactly once using the pinned model version's conventions. Keep subsidies/transfers separate from real system resource costs.
8. **Constraints:** ecological capacity limits, build rates, emissions accounting boundary, reliability target, permitted load shedding, land/water limits and policy scenarios.

Start by reproducing historical energy, seasonal generation, peak demand, import dependence and reservoir behaviour. Report errors and missing-data treatment. A one-bus result cannot establish internal transmission congestion, site-specific connection feasibility or N-1 security. See [PyPSA documentation](https://docs.pypsa.org/latest/) and [generator inputs](https://docs.pypsa.org/latest/user-guide/components/generators/).

## KMML and HOMER Pro

Use HOMER Pro for a defined KMML electrical supply/reliability case, such as grid + PV + battery + backup generation. Select the actual metering boundary first: a whole-facility aggregate, process block or critical-load subsystem. Do not assume the entire industrial process can be interrupted or islanded.

Acquire a full year of interval load, monthly bills, tariff/time-of-use rules and demand charges, import/export restrictions, outage logs, critical/noncritical loads, existing backup equipment, fuel consumption curves/costs, available PV area, site weather, battery/converter specifications and financial assumptions. Check that the available HOMER edition/modules support the selected tariff and controls. Synthetic loads support early sensitivity work, not a validated facility baseline; see [HOMER's electric-load documentation](https://homerenergy.com/products/pro/docs/latest/electric_load.html).

The circular-industry study additionally needs throughput, feedstock/product quantities, residual chemistry and moisture, current treatment/disposal, reagent/heat/water use, measured emissions/effluents, recovery yields, transport, disposal costs and product specifications/offtake. Establish a functional unit, for example one tonne of a specified product, and consistent process boundaries. Compare prevention/reuse/recovery against the actual existing route; do not import TTPL process assumptions into KMML. HOMER does not replace this mass balance.

## Ecological data: minimum GIS package

| Layer group | Required data | Role and acquisition route |
|---|---|---|
| Geography | State/district boundaries, catchments, candidate sites and electrical zones | Common spatial IDs; watersheds may extend outside Kerala and must not be clipped at the state boundary for hydrology. |
| Land cover | Dated classified raster, class definitions and accuracy; historical/future alternatives when needed | Land availability and habitat baseline. Start with documented NRSC/Bhuvan products; record scale and acquisition year. |
| Terrain | DEM, slope, drainage and site-relevant elevation quality | Engineering screening, drainage and catchment delineation. Coarse maps cannot establish parcel-level buildability. |
| Forest/biodiversity | Authoritative forest/protected-area geometry, notified buffers where applicable, habitats, corridors and suitable species evidence | Seek Forest Department and biodiversity authority data; distinguish legal restrictions from ecological sensitivity. |
| Wetlands/coast | Wetlands, mangroves, waterbodies, applicable paddy/wetland records, shoreline and CZMP/CRZ mapping | Seek official wetland/revenue/coastal authority records. KCZMA publishes [CZMP 2019 map sheets](https://www.keralaczma.gov.in/index.php/zone-maps/coastal-zone-maps-2019); verify map status/date and obtain GIS geometry where possible. |
| Hazards | Flood depths/extents and return periods, landslide susceptibility, coastal hazards | [KSDMA](https://sdma.kerala.gov.in/hazard-maps/) provides flood raster downloads and GSI 2022 district landslide shapefiles. Historic and climate-scenario maps are separate inputs. |
| Water/soils | River network, soils, rainfall, evapotranspiration, streamflow, reservoir operations and competing withdrawals | Needed for water availability, erosion and hydrology; seek water-resource agencies and KSEBL. |
| Access/exposure | Roads, substations/lines with appropriate permissions, settlements, critical infrastructure and land tenure for shortlisted parcels | Connection costs, exposure and implementability. Community uses and livelihoods require consultation as well as maps. |
| Industrial environment | KMML emissions/effluent and residual monitoring, nearby receptors, water abstraction/discharge | Compare baseline and proposed recovery impacts using KMML/EHS and KSPCB records. |

For every layer retain custodian, dataset date, retrieval date, licence, legal status if relevant, CRS, resolution/scale, no-data definition, coverage and uncertainty. Check topology and raster alignment. Use appropriate projected coordinates for distances/areas and appropriate resampling for categorical versus continuous data. A missing tile must not become unrestricted land.

Produce three explicit classes: verified exclusions; conditional/penalised areas; and unknown areas needing evidence. Keep draft notifications separate from final legal layers. Do not invent universal buffers, assume every hazard implies a legal prohibition, or treat unprotected land as ecologically expendable. Screen each technology separately: rooftop PV, ground PV, wind, transmission, reservoirs and industrial reuse have different footprints and impacts.

## Which ecological models to use

- **QGIS + GeoPandas/Rasterio first:** inspect and harmonise layers; calculate excluded/conditional area, candidate capacity and connection-distance assumptions. This is the ecological minimum for the first energy scenarios.
- **InVEST Habitat Quality:** land-cover raster(s), threat rasters, threat weights/distances and habitat sensitivity table. These parameters need local justification and sensitivity analysis. Its outputs are habitat-quality proxies, not measured species counts or environmental clearance. [Official input guide](https://storage.googleapis.com/releases.naturalcapitalproject.org/invest-userguide/latest/en/habitat_quality.html).
- **InVEST sediment delivery, if relevant to reservoir catchments:** DEM, rainfall erosivity, soil erodibility, land cover, watershed boundaries and land-management factors. Add observed sediment evidence for evaluation. [Official SDR guide](https://storage.googleapis.com/releases.naturalcapitalproject.org/invest-userguide/latest/en/sdr.html).
- **SWAT+/QSWAT+ later:** DEM, soils, land use, daily meteorology, rivers/reservoirs, management/withdrawals and observed multi-year discharge; sediment observations if modelling sediment. Plan warm-up, calibration and independent validation periods. Start with a priority hydro catchment and expand; it is not necessary to calibrate all Kerala at once. [Official watershed workflow](https://docs.swat.tamu.edu/getting-started/first-watershed/).

Choose modelled ecological outcomes before choosing additional software: habitat fragmentation, sediment risk, water availability and land conversion are different questions. Neither a hazard overlay nor a single weighted ecological score covers them all. Annual ecosystem-service estimates must not be treated as hourly hydro inflow.

## Other modelling work, conditional on the question

| Workstream | Additional inputs / condition to start |
|---|---|
| Reduced zonal electricity model | Defensible regional load allocation and transfer limits; zones grounded in the network rather than weather-marker locations. |
| AC network validation | Bus voltages, line impedances/ratings, transformer data, active/reactive injections and credible topology; then use pandapower or equivalent for selected operating points/contingencies. |
| Distribution/feeder analysis | Actual feeder connectivity, phase data, conductor/transformer parameters, load profiles and controls before OpenDSS or equivalent is useful. |
| PV/wind performance detail | Site weather, equipment curves, geometry, temperature and system-loss assumptions; a dedicated performance tool can supply profiles if required. |
| Life-cycle assessment | Process inventories, consistent functional unit, allocation/substitution rules, background datasets and emission factors; useful for comparing KMML recovery pathways. |
| Long-term demand | Sectoral activity, efficiency, electrification, EV travel/charging, industrial growth and cooling; vehicle registration totals alone do not produce hourly charging demand. |
| Whole-energy balance | Kerala-specific petroleum, LPG, gas, biomass, transport and industrial-heat quantities; reconcile useful/final/primary energy and avoid double-counting electrification. |
| Finance | Whole-system resource costs, project cash flows, tariffs and separate Kerala-government/KSEBL/Union/private funding responsibilities. A least-cost system is not automatically a bankable project. |

These are conditional modules, not a requirement to install every modelling package now.

## Connect the workflow through shared inputs

Maintain a versioned data dictionary and stable IDs for sites, assets, catchments, resource zones and scenarios. Suggested logical tables (not necessarily native software import formats):

- `demand_hourly`, `generation_observed`, `interchange_observed`: timestamp, entity ID, value, unit, quality flag, source ID.
- `assets`, `technology_costs`, `grid_interfaces`: capacities, operational limits, dates and assumptions.
- `renewable_profiles`, `hydro_inflows`, `reservoir_rules`: synchronised temporal inputs with documented conversions.
- `ecology_layers`, `candidate_sites`, `capacity_limits`: geometry/rasters plus screening decisions and capacity assumptions.
- `kmml_flows`, `kmml_load`, `kmml_tariff`: consistent reporting boundary and period.
- `scenario_assumptions`, `validation_metrics`, `provenance`: reproducible differences between runs and evidence quality.

Connection order: GIS screening limits candidate capacities; weather produces generation profiles; observed or calibrated hydrology supplies hydro constraints; demand and costs enter PyPSA; selected electrical operating points go to network checks; KMML supply options go to the site model; material recovery changes the site's load and resource flows. Return grid/ecological infeasibilities to the planning model and rerun. Translate units explicitly: MW/MWh versus kW/kWh, and water flow versus hydroelectric energy. Keep investment costs and benefits from being counted twice across models.

## Next actions and completion gates

1. **Send the existing SLDC request** with genuine affiliation and purpose; request FY2024-25 first, additional years if available. Ask SLDC/KSEBL operational custodians first, using the Power Department for facilitation if needed. See [draft](SLDC_DATA_REQUEST_DRAFT.md). No email has been sent by this assessment.
2. **Request KMML data** through a technical/EHS contact: start with a defined boundary, interval load, production and residual ledger, then hold a short process clarification discussion. See [case plan](KMML_CASE_PLAN.md).
3. **Request KSEBL plant/hydro/planning inputs** with a precise field list. Seek aggregate/non-sensitive alternatives if detailed network data is unavailable.
4. **Acquire the GIS starter pack now:** KSDMA downloads, land cover, DEM and authoritative conservation/wetland/coastal layers; track inaccessible geometry explicitly.
5. **Repair internal acquisition:** smaller ERA5 requests, missing SLDC days, recovery of prior artifacts, proper NASA requests, and source-specific export fallbacks. A website outage is not the same problem as missing fields or unsuitable spatial resolution.
6. **Freeze the first research comparison:** baseline plus a small number of explicit 2040 demand/technology cases. Define metrics and validation tolerances before presenting results: cost, imports, unserved energy, emissions, land, water and ecological exposure.
7. **Pass model gates:** complete input manifest and units/time checks; historical electricity validation; ecological screening with unknown areas visible; KMML mass/energy closure; then scenario comparisons and dry-year/high-demand/import-disruption sensitivities.

The user-dependent priorities are agency/facility access, confirmation of the academic deliverable/deadline and review by an electricity-system expert plus a local ecology/hydrology expert. Data engineering, public GIS processing and labelled prototype models can proceed while those requests are pending.
