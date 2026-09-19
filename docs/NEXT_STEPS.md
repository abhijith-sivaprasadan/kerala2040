# Kerala 2040: next research steps

## What now works

The research repository is the source of truth: `docs/` contains the interface and
`public/` contains the dated evidence snapshot. `scripts/build_site.py` validates
the manifest and packages both together. The website repository deploys that
package on push, manual dispatch and a six-hour schedule. Browsers need no API
keys and do not depend on raw.githubusercontent.com for research data.

Independent ingestion jobs preserve previously published layers, identify retained
evidence dates, validate the combined snapshot, and share one publishing lock.
The historical artifact recovery workflow requires explicit run IDs rather than
silently restoring a fixed old run. Full-year acquisition is manual because it is
slow and should not run whenever the interface changes.

The modelling foundation now includes an observed-day PyPSA replay, hydro/storage
diagnostics, official energy-accounting reconciliation, weather-derived renewable
availability proxies, a canonical generator inventory seed, structural 2040 scenario
dimensions, a sourced techno-economic benchmark registry and a GIS acquisition
manifest. These are foundations, not validated 2040 results.

The 8,760-hour load reconstruction remains **proxy data, not measured telemetry**.
See [the mandatory provenance policy](PROVENANCE_CORE_RULES.md).

## Your next actions, in order

1. **Confirm the CET submission date and freeze the scope.** Make the first release
   a defensible historical electricity balance, a constrained scenario design and
   one sourced circular-industry case. Do not promise optimised 2040 results yet.
2. **Obtain hourly or 15-minute demand and interchange for FY2024–25, and recover
   the CSTEP FY2016 15-minute source series.** Request timestamped Kerala demand,
   imports/exports, units, timezone, missing-data flags and revision history from
   SLDC/KSEBL. Separately, CSTEP's 2024 roadmap confirms that observed FY2016
   15-minute Kerala data existed and was used to derive its FY2022 load curve; request
   that raw series from CSTEP/EMC/KSEBL/SLDC as an independent historical validation
   dataset. See [the data specification](hourly_demand_gap.md). Do not digitise the
   CSTEP figure and call it measured data, and do not send secrets or confidential
   utility data to the public repository.
3. **Close the historical reconciliation.** The reconciliation workflow is now
   implemented and preserves SLDC, Economic Review/KSEBL and CEA accounting
   boundaries separately. The current snapshot still has 354/365 SLDC days, with
   11 dates explicitly missing; recover those dates or document their absence.
4. **Calibrate the chronological model.** The observed-day PyPSA replay is now
   implemented without using the synthetic hourly proxy. Next validate real hourly
   load, generation, imports,
   peak behaviour, hydro energy and storage against history. Passing a daily
   accounting identity does not satisfy this gate. The existing PyPSA model is
   only a smoke test, not a completed Kerala capacity-expansion model.
5. **Complete numerical constraints before solving scenarios.** Secure resource
   profiles, technology costs, grid limits, hydro/water constraints and licensed
   spatial exclusions. Hazard catalogues are not GIS overlays. Then implement
   S0/S2/S3 and compare reliability, imports, cost and sensitivity under common
   assumptions. Downloaded website specifications do not run the solver.
6. **Develop the selected KMML case and finance evidence.** KMML is confirmed;
   obtain quantities, chemistry, disposal costs, recovery costs and credible
   offtake. Separate commissioned recovery from planned projects. Specify Kerala,
   KSEBL, Union and private financing rather than assigning all costs to the state.

See the [SLDC request draft](SLDC_DATA_REQUEST_DRAFT.md),
[CSTEP FY2016 data request draft](CSTEP_FY2016_DATA_REQUEST_DRAFT.md),
[KMML case plan](KMML_CASE_PLAN.md) and [Energy Project review](ENERGYPROJECT_REVIEW.md).
The study covers all of Kerala; atlas markers are illustrative, not a complete grid.

## Working locally

Use Python 3.11 or 3.12. From the research repository:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
python scripts/build_site.py --check
python scripts/build_site.py --output _site
python -m http.server 5173 --directory _site --bind 127.0.0.1
```

Open http://127.0.0.1:5173. Do not open index.html directly as a file: browsers
restrict fetching JSON with file URLs. Edit the interface in the research repo,
not independently in the generated website copy.

Run `pytest`, `ruff check src tests scripts` and `node --test tests/web.test.cjs`
before publishing. Run the manual historical/extended ingestion workflows when
new acquisition is needed. External endpoint outages remain visible in source
audits; reachability never proves that a dataset has been validated.
