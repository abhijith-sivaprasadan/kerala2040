# Kerala 2040: next research steps

## CET 2026 KMML circular-process case: bounded chapter complete · 24 September 2026

The [completed KMML source-audited chapter](KMML_CIRCULAR_INDUSTRY_CASE_2026_09_24.md) now reconciles official KMML process branches (9 named units), the FY2022–23 company report and the user-shared historical references into 10 distinctly classified residual/recovery streams with source-dated status. Existing ARP acid regeneration is separated from historical oxide bricks, documented 2022–23 **trials** for oxide-to-sponge-iron, U400 fines and filter-backwash reuse, and hypothetical heat integration. A separate Ti-sponge product branch and the report's non-verified regulatory classification are explicit. The [public-safe case register](../data/evidence/industry/kmml_source_bounded_case_2026_09_24.json) contains **null** annual recovery, heat and emissions outcomes. The website Industry page displays the process nodes and filters interactively.

**Still open:** aligned contemporary site meters, compositions, actual trial commissioning, water and heat balances, accepted offtake/disposal, as-issued regulator records and capex/opex before *numerical* circularity/2040 industrial claims. Finish CET poster using bounded evidence rather than waiting for facility data. ERA5 acquisition is independent.

## CET 2026 historical electricity story: bounded chapter complete · 24 September 2026

[Executed source-audited historical chapter](CET_HISTORICAL_ELECTRICITY_STORY_2026_09_24.md) combines separately attributed **official annual Kerala consumption (FY2020–21–FY2024–25)** and **qualified SLDC operational daily reports (2019–2026)**. It adds four poster-oriented SVGs—official consumption, matched-day daily changes, observed-day import/hydel shares and separately labelled Statistics evening peaks—plus [validated input/denominator registry](../data/evidence/sldc/cet_historical_electricity_story_2026_09_24.json). The multi-year **descriptive** question is answered without ERA5 and without inventing annual sums, correcting missing days, or treating hydro/import accounting co-movement as causal.

**Still open, deliberately not rebranded complete:** (1) retrieve 11 missing FY2024–25 SLDC qualified dates or leave absent; (2) obtain data dictionaries to reconcile operational daily and annual consumer-side boundaries, which differ even for 365/365 FY2020–21; (3) acquire and validate measured interval demand/interchange; (4) bound plant-level hydro operating and import-capacity/price parameters before claiming 2040 scenario outcomes. The research chapter on `main` is distinct from the immutable public website evidence snapshot.

## August 2019 real-original ERA5-Land pilot: processed, spatial admission still open

[Executed original-GRIB August audit](ERA5_LAND_AUG2019_ORIGINALS_EXPLORATORY_AUDIT_2026_09_24.md): 24 ERA5-Land parameters parsed from user-provided acquisition-envelope GRIB; July 31 core boundary hours retained; **31 complete August IST rainfall dates**, 1,034 source-valid land pixels, original forecast-step/duplicate checks. July 31 extended fields are missing, so 1 Aug IST is incomplete for that second variable batch. **The 380.65 mm bbox-land-pixel mean and 537.73 mm example-rectangle mean must not be labelled Kerala or Idukki catchment rain**. Official state and source-verified reservoir-intercepted watershed polygons, and source-matched private SLDC inflow observations, remain separate gates; 2018 SLDC electricity is still missing.

## Electricity demand and annual accounting: parallel non-renewable workstream

[The FY2024–25 official demand-sector and accounting-boundary review](DEMAND_SECTOR_ACCOUNTING_BASELINE_2026_09_23.md) now records KSEBL's nine customer/sales categories and disambiguates consumer electricity use, KSEBL all-category sales (including trading), in-state sales, net utility input, periphery supply input, and Kerala2040's 354-day incomplete operational SLDC sum. These are **not the same annual demand definition**, and no difference may be assigned to losses or imports without matching the scope and year. This annual review is **not** a measured hourly load or cost model.

Next: harmonize **multiple years** of official sector baselines; obtain FY2024–25 measured hourly/15-minute statewide demand and interchange; source actual procurement/true-up/contract cost if studying affordability; join ERA5-Land temperature/dewpoint after arrival to a *measured*, calendar-matched load before attempting weather-driven demand inference. Keep projected EV, air-conditioning, industry and flexible demand explicitly labelled scenarios.

## Hydro Phase 5 (23 September 2026): pipeline ready, original basin data still gated

The executed [Phase 4 Idukki reservoir and station pilot](PHASE4_IDUKKI_HYDRO_ENERGY_RESEARCH_2026_09_23.md) remains the latest observational result. The [Phase 5 ERA5-Land research pipeline](PHASE5_IDUKKI_ERA5_BASIN_WEATHER_2026_09_23.md) now includes original-GRIB parsing, independently source-reviewed catchment overlap weights, original hourly cumulative tp deaccumulation with an explicit 50:50 allocation across IST midnight, complete-pixel/day QA, and common-date chronological comparisons with Idukki SLDC-gauge rain and persistence. **This branch has no real selected catchment weather rows and no Phase 5 skill number.**

**Action order:** (1) source/verify the reservoir-intercepted Idukki catchment polygon and upstream diversion treatment; (2) dry-run and authenticate the monthly 2017-12-31–2026-09-23 ERA5-Land acquisition over its reviewed bbox; (3) privately extract original GRIB and construct reviewed weights; (4) run the Phase 5 weather and paired-model QA against privately held SLDC CSVs; (5) independently review holdout coverage/extremes before any public numerical result. The full Periyar basin and five representative ERA5 points are not substitutes.

Phase 5 does **not** close the separate P0 measured hourly/15-minute electricity acquisition gate, recover 2018 SLDC daily rows, identify physical spill or qualify project-specific pumped-storage MW.

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

## Observed SLDC archive: full-history acquisition & first analytical pass · 23 September 2026

The bounded five-section [2019–2026 source audit](SLDC_FIVE_SECTION_2019_2026_SOURCE_AUDIT_2026_09_23.md) has been completed on the user's uploaded source ZIP. 2,606 calendar days were audited across Statistics, Imports, Storage, Availability and Other Extrema; 2,576 Statistics/Imports and 2,577 other-section reports passed independent saved-HTML hash and returned-date checks. One 2019-12-05 internal balance contradiction is preserved and excluded from qualified reported consumption. Older 44-row and newer 73-row source schemas remain distinct. FY2024–25 has 354/365 qualified observed days; incomplete sums must not be relabelled annual production or load.

**Next:** (1) resolve source-field missingness and flag anomalies in multi-year analysis, (2) compare matched daily 2024–25 records against the earlier standalone FY historical dataset, (3) quantify seasonality of daily consumption, import dependence, hydropower storage and observed peak timing, and (4) separately obtain genuinely metered interval chronology, generator dispatch and operational MW availability. The SLDC Availability section reports scheduled *energy in MU*, not spare MW.

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
