# WP6 · Kerala grid integration: admission gate and experiment design

**24 September 2026 · evidence audit and implementation specification; NOT an executed statewide dispatch study.**

## Verified repository inputs and their limits

| Existing input | Admissible use | Not admissible |
|---|---|---|
| `data/external/sldc_fy2024_25/daily_balance.csv` | Date-labelled official daily consumption, internal generation, hydro and net-import **MU**, on observed dates only | Hourly MW, a full-year sum without gap handling, technology-specific renewables, import transfer capacity |
| `selected_intraday_extrema.csv` | Source-labelled selected extrema and their reported time windows | Complete chronological load, coincidence, hour-by-hour solar/wind or imports |
| Reconstructed 8,760-hour load proxy mentioned in `docs/MODELLING_DATA_ROADMAP.md` | Explicitly synthetic shape experiment, conditional on recovering the actual artifact and checking its energy reconciliation | Independently measured hourly telemetry, validated peak coincidence |
| Existing WP6 cooling, EV, industrial and BESS/PSP pilots | Physical constraints, service-preservation tests, unit-level counterfactuals | Direct statewide MW scaling or aggregation without participation and overlap evidence |
| `configs/hydro_topology_evidence_2024_25.yaml` | Qualitative water-system relationships and anti-double-counting rules | Two independent reservoirs, head/storage curves or dispatchable pumped-hydro MWh |

Daily MU = daily GWh; daily average MW = MU × 1000 / 24. This is a **daily mean**, not an observed hourly load or peak. Missing values are null, never zero. Any daily-derived dispatch experiment must say it is a synthetic disaggregation and must conserve each observed day's energy.

## First integration experiment: two distinct tracks

**Track A: synthetic, executable after input validation.** Choose an explicitly synthetic 24-hour normalized shape, reconcile its sum to a single *observed* SLDC day, and run (i) no flexibility, (ii) individually service-preserving EV/industrial/cooling cases, (iii) storage only, and (iv) combined cases with shared power ceilings. Cooling must preserve the same comfort bounds; EV and industry must preserve completion and deadlines. Storage must preserve its initial/terminal state and charge losses. Report site/net-grid energy, selected-evening and whole-day peaks, curtailed energy only if an explicit generation profile exists, unmet service and infeasibility. Do **not** add independently modelled site peaks or savings: recompute the aggregate hour by hour on one synchronized chronology. No measured coincident peak or statewide potential claim follows.

**Track B: observed Kerala chronology.** Block until independently source-traceable, timezone-aligned interval demand, generation by technology, actual interchange, rooftop/captive boundary and completeness QA are available. An hourly model requires timestamps, interval-average MW, local/UTC convention, quality flags and documented system boundary. Reconcile every observed day against SLDC MU, documenting any losses or boundary differences before calibration. Scheduled interchange is not actual interchange.

## Pumped-storage candidate evidence register

| Lead | Current source assurance | Missing before site admission |
|---|---|---|
| Idukki | May 2025 CEA profile text-indexed discovery only; original page image unverified in preceding WP6 audit | Updated CEA/KSEBL project-specific status; distinct upper/lower water bodies; surveyed head and level-volume curves; hydraulic route; water/land rights; environmental, forest and dam-safety status; grid point |
| Pallivasal | Same dated discovery-only status | Same evidence, independently verified for this proposal |

The August 2026 CEA monthly pumped-storage report was identified in the preceding WP6 chapter but **not reconciled project by project**. Neither lead is an approved buildable site or modelled MW/MWh capacity. An existing dam name is not proof of a pumped-storage scheme. Never derive pumped water volume from SLDC reservoir generation-equivalent MU or count cascade water twice.

## Release gates

1. Daily-source QA: actual observed/missing date counts, duplicate-date check, source hashes, balance residual and numeric units.
2. Hourly-source QA: complete timestamp grid, timezone and DST handling, observed-vs-proxy labels, daily MU reconciliation and explicit unknowns.
3. Dispatch QA: hourly conservation, power and energy limits, terminal SoC, matched energy services, joint peak recalculation and infeasible-case nulls.
4. Geographic admission: separately evidenced reservoir pair, elevation/volume geometry, environmental and operating restrictions, source vintage and uncertainty.
5. Publication: separate panels for **observed daily evidence**, **synthetic dispatch**, and **unadmitted project leads**; never promote one to another.

**Status:** this document establishes the auditable next model boundary. It does not claim an executed integrated dispatch, recovered hourly telemetry, current project permissions or a deployed website update.
