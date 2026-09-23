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

The P0 interval-data acquisition is supported by a
[private, fail-closed 8,760-hour / 35,040-block intake validator](MEASURED_INTERVAL_INTAKE.md).
It checks a future genuinely sourced export; no full FY2024-25 measured
interval source has arrived, and running the validator does not unlock the
historical-calibration or 2040 release gates.

## Renewable KPI handoff · 23 September 2026

**Wind phase 1 is frozen for the CET poster.** Its [research question, quantitative conclusion and takeaway](WIND_PHASE1_DISTRICT_NORMALIZED_CLOSEOUT_2026_09_23.md) are source-qualified; do not reopen the wind resource screen to invent capacity or legal eligibility. The next bounded renewable KPI is [solar phase 1](SOLAR_PHASE1_KPI_SCOPE_2026_09_23.md): verify the original long-term Global Solar Atlas PVOUT pixels and NWIC district boundaries; derive a complete 14-district source-pixel partition and **paired per-pixel** seasonal sensitivity with missing-cell accounting. The existing 46,241 native PVOUT centres and long-term unweighted annual median 1,493.507 kWh/kWp are source-clip evidence, not a completed district/monthly solar analysis or installed capacity.

This work runs **alongside**, rather than displaces, the P0 measured interval-demand and interchange acquisition needed for a validated 2040 model.

## Solar phase 1 source-verified result · 23 September 2026

The previously planned [solar phase 1](SOLAR_PHASE1_KPI_SCOPE_2026_09_23.md) has now been executed using all 14 native yearly/daily/monthly GSA PVOUT windows and the original NWIC district source: [audited 14-district matched-pixel report](SOLAR_PHASE1_NWIC_DISTRICT_SEASONALITY_RESULT_2026_09_23.md). The 46,241 Kerala native PVOUT pixels uniquely reconcile, all 12 months are available, and paired February→July percent change is derived for each pixel before district medians are taken. The statewide median paired decline is 43.60%; this is a source-climatology finding, not actual electricity generation, legal suitability or MW.

Wind and solar bounded *descriptive* resource phase 1 questions are both frozen for CET. The next genuinely open project KPI is the measured FY2024–25 **interval electricity chronology and import/solar generation validation**, followed by independent statutory land/roof/waterbody eligibility and grid constraints. Do not add nominal 2040 PV MW or convert original resource-grid pixel counts into area.

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
