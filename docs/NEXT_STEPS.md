# Kerala 2040: next research steps

## WP6 BESS/pumped-storage: bounded electrical service screen · 24 September 2026

The [BESS/PSP executable study](WP6_BESS_PUMPED_STORAGE_SCREEN_2026_09_24.md) runs two zero-initial/zero-terminal synthetic stores against a fictional site and fixed five-hour evening duty. Grid charging, stored-state losses, auxiliary power, round-trip ratio, separate whole-day/evening peaks and a hypothetical 300 m hydraulic m³ conversion are source-labelled. Nine capacity×efficiency combinations per store preserve infeasible cases as null. Neither actual Kerala pumping MW nor net import reduction is inferred. CEA's 2026 report index and dated 2025 Kerala project text are **discovery only** (original page-image check failed), not current approval.

**Next physical gates:** updated named project stage, distinct upper/lower reservoir and head/storage curves, flood and environmental rules, water rights, project-grid connection and independently dated BESS site/equipment/cost/market evidence. A 24-hour fictitious service cannot yield a Kerala 2040 storage capacity or compare environmental/financial merit.

## WP6 two new reproducible experiments: managed EV + noncritical industrial duty · 24 September 2026

[Technical model and public method chapter](WP6_EV_INDUSTRIAL_FLEXIBILITY_PILOTS_2026_09_24.md) and [shared constrained Python scheduler](../src/kerala2040/flexibility_dispatch.py) implement **two independent 24h** source-labelled illustrative examples. EV charger arrivals/departures, battery headroom, per-vehicle charging kW, conversion losses and shared circuit cap are enforced for BOTH earliest and managed policies; industrial optional jobs preserve exact due production/service duty and leave fictional critical/safety load untouched. Nine connection capacity × charging efficiency or duty-size sensitivities per pilot (18) regenerate both policies, with deadline checks and unchanged total electricity under fixed efficiency. The website exposes 48 hourly rows per pilot, two case comparisons, individual jobs and each sensitivity. Source-bounded industrial model is **not** a KMML metered/process-permission finding.

**Next true WP6 research phases:** obtain permitted vehicle arrival/departure/SoC or aggregated depot profiles, charging equipment/feeder limits and active tariff rules; industrial site-approved flexible process schedules, no-harm compliance, and independent electricity meters; then bring in validated hourly Kerala coincident grid observations. Separate BESS and pumped-storage screening can start without claiming any of these synthetic runs establish statewide MW or annual kWh.

## WP6 thermal storage and cooling: reproducible pilot complete · 24 September 2026

The [first executable WP6 engineering chapter](WP6_COOLING_THERMAL_STORAGE_PILOT_2026_09_24.md) compares conventional AC, 13–16 pre-cooling and night-charged chilled-water storage for **one explicitly synthetic 24-hour profile**, from a versioned [1R1C specification](../configs/wp6_cooling_tes_illustrative.yaml). Conservation and same end-state checks, common 24–26°C comfort, early setpoint shortfall vs discomfort, charging parasitics/COP derate and independent whole-day/evening peak definitions are enforced; all three hourly series, nine sensitivity reruns and dynamic Pathways figures build from source. No Kerala hourly/ERA5 climate, statewide MW, annual financial or carbon claim is admitted. This opens a new WP6 topic rather than revisiting data requests.

**WP6 next distinct tasks:** measured-building data and cooling/latent validation, demand-side EV charger availability and required terminal SoC, process-specific industrial flexible hours, BESS/pumped-storage technical options. Actual Kerala coincidence, tariffs and project economics remain gated until physically grounded source periods align.

## Total Energy Atlas: 2023 official sector emissions, heating-value method and source request pack · 24 September 2026

The [sector GHG and energy-methods chapter](KERALA_TOTAL_ENERGY_ATLAS_SECTOR_GHG_METHODS_2026_09_24.md) and [auditable source register](../data/evidence/total_energy/kerala_ghg_sector_bridge_2026_09_24.json) add the DoECC official **calendar-2023** 20.64 MtCO₂e energy-sector estimate and separate transport/residential/industrial emission categories, explicitly **not equivalent to fuel×sector energy consumed**. The earlier 2005–2021 published inventory's **2020 16.96** vs current portal **17.09 MtCO₂e** disagreement is kept as an inventory revision gate. The BEE/CII/EMC annex lists fuel-specific **GCV**, which cannot silently substitute NCV or prove modern fuel grade. A concrete, public/authorised PPAC, EMC and DoECC original-data/definition request pack is ready; no request has been sent.

**Only externally controlled gates now remain for the intended current all-fuel balance:** original PPAC native full-year state×product data and original FY2024–25 primary PDF page; EMC fuel×sector author table and FY2015 discrepancy resolution; dated NCV standards and attribution of industrial feedstock, captive power and interstate/aviation/marine use; DoECC inventory methodology/revision bridge and 2024–25 equivalent estimates. Do not claim current Mtoe, oil-import share or emissions calculated from unmatched tables.

## Kerala full-year petroleum sales · additional total-energy atlas analysis · 24 September 2026

The [PPAC annual publication audit](PPAC_KERALA_FULL_YEAR_SALES_SOURCE_AUDIT_2026_09_24.md) and [source-tier data register](../data/evidence/total_energy/ppac_full_fy_kerala_source_audit_2026_09_24.json) distinguish six full FY2019–20–2024–25 Kerala all-POL sales rows and petrol/diesel included subseries. FY2024–25 is transcribed from a precisely identified PPAC edition's **third-party text mirror**; original PPAC PDF image access remains blocked, so FY2024–25 annual sales is explicitly lower-assurance and not a measured in-state final-energy balance. No annualisation of the earlier H1 provisional products, and no inferred missing FY2019–20 diesel. Earlier PPAC FY2022–23 source reports disagree (6,882.6 vs later 6,879.1 thousand tonnes); vintages are preserved. The source register lists specific data fields/request needed from EMC because its fuel-by-consuming-sector input workbook was not found in public EMC downloads.

**Next actual evidence gates:** official FY2024–25 PDF bytes and Kerala row cross-check, original all-FY PPAC state×product workbook/data dictionary; EMC author workbook and conversion methods, ideally publication-cleared CSV. Never assume fuel sales, generation input, import share and Kerala final energy are equivalent.

## Kerala Total Energy Atlas: new original-plan dimension started · 24 September 2026

The [first source-qualified statewide TFEC research chapter](KERALA_TOTAL_ENERGY_ATLAS_BASELINE_2026_09_24.md) retrieves **six historical EMC final-energy totals (FY2014–15–FY2019–20)** and FY2019–20 publisher-rounded oil/electricity/coal/gas shares, with visually checked source Figure 3 and 4. Distinct PPAC **April–September 2024 provisional selected-product petroleum sales** have indexed publisher-text provenance but **original page-image QA still pending**. The [register](../data/evidence/total_energy/kerala_total_energy_source_register_2026_09_24.json), fail-closed validator and three interactive homepage charts prevent combining unlike years or mass/energy/nominal plant capacities. The PPAC 30 September 2024 infrastructure snapshot remains supply context, not consumed energy.

**True next source gate:** original PPAC full FY2019–20 and FY2024–25 (or latest) complete state × product reports and legends; original H1 PDF image; EMC original fuel×sector calculation spreadsheet/calorific standards; valid same-FY gas/transport/industry/household end-use allocation. Only then calculate a new statewide total final-energy, petroleum dependence and energy-service baseline. Existing electricity chapters are not a substitute for final energy.

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
