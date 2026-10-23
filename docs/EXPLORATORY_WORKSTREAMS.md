# Exploratory models retained outside the public findings

**Current classification:** research methods and sensitivity demonstrations. Retained for reproducibility; not promoted to conclusions about observed Kerala operations or optimal 2040 decisions.

| Workstream | Repositories / documentation | Blocking evidence for operational interpretation |
| --- | --- | --- |
| Hourly demand reconstruction | `src/kerala2040/chronological_screen.py`, `public/hourly-load-proxy.json` | Continuous, same-boundary metered Kerala demand |
| Hydro redispatch and interday water movements | `src/kerala2040/full_pypsa_hydro_flexibility.py`, `docs/FULL_PYPSA_SCENARIO_PROGRAMME.md` | Station dispatch, unit ramps, cascade state, inflow/release constraints |
| Seven-day clock-time stress experiments | `docs/HYDRO_CHRONOLOGY_SENSITIVITY_V0_1.md`, `docs/HYDRO_SUPPLY_TIMING_V0_2.md` | Measured hourly import capability and generation; experiment's evening derate and ramp are deliberately invented test inputs |
| Network congestion screening | `docs/KSEB_NETWORK_ROBUST_BOTTLENECKS_V1_0.md` | Calibrated topology, impedances, injections, thermal ratings, contingency states |
| 2040 investment planning and candidate capacity | `configs/scenarios_2040.yaml`, `docs/FULL_PYPSA_SCENARIO_PROGRAMME.md` | Reconciled future inputs, statutory constraints, validated economic and operational parameters |
| Renewable siting and storage | `configs/gis_inputs.yaml`, `docs/SOLAR_WIND_CONSOLIDATED_ANALYSIS_2026_09_22.md`, `configs/wp6_bess_psp_illustrative.yaml` | Statutory land and ecological layers, site-specific engineering and dispatch data |

**Evidence rule:** simulation results may verify an equation or illustrate conditional mechanisms. They do not constitute observed shortage, causal diagnosis, probabilistic adequacy, feasible generation, permitted siting or investment advice.

Public research companion pages may link to the underlying code for transparency but should not feature their numerical stress-test results as findings. Historical files are not retroactively deleted; Git history and document provenance remain part of the audit.
