# Kerala2040 — Idukki hydro–electricity pilot, Phase 4

**Evidence cutoff:** the user's collected Kerala SLDC daily reports for 2019-08-06 through 2026-09-23. **Execution:** offline against privately held, source-hashed curated CSVs. **Classification:** source-observed, retrospective, descriptive; **not** an externally calibrated basin hydrology model, a flood-causal estimate, an hourly dispatch reconstruction, a 2018 electricity record or a pumped-storage feasibility result.

## Executed source joins

One calendar row is retained for each of **2,606 days**. Idukki is joined by `date` and exact source label in **both** the reservoir and station-generation tables. Aggregate Kerala hydel generation remains a separate column; it is never substituted for Idukki-station output.

| Source observation | Valid dated observations |
|---|---:|
| Idukki daily reservoir rainfall | 1,359 |
| Idukki daily reservoir inflow | 2,414 |
| Idukki named-station actual daily energy | 2,546 |
| Idukki effective reservoir storage volume | 2,577 |
| Consecutive-day inflow-minus-storage-change residual | 2,388 |

The rainfall record has reporting gaps and is **not** established as area-weighted catchment precipitation. The `net_depletion_residual_mcm = reported_inflow_mcm_day - Δreported_storage_mcm` is a balance **residual**; it is **not observed turbine discharge, non-power release, spill, pumping, or a flood-control operation**. Station energy MU cannot convert that residual to discharge without validated plant head, energy conversion, water routing and loss data. `generation_capability_mu` is not station day generation and is not used as such.

## Lagged rainfall–inflow association

The following lag-`k` compares rainfall on **actual calendar day `t-k`** to inflow on `t`. A missing day stays missing; shifting only available rows would create fictitious time intervals.

| Rain lag | Paired days | Pearson r | After year-month demeaning |
|---|---:|---:|---:|
| 0 days | 1,344 | +0.627 | +0.598 |
| 1 day | 1,319 | +0.651 | +0.619 |
| 2 days | 1,320 | +0.558 | +0.488 |
| 3 days | 1,320 | +0.513 | +0.415 |
| 4 days | 1,321 | +0.436 | +0.307 |
| 5 days | 1,323 | +0.360 | +0.202 |
| 6 days | 1,324 | +0.288 | +0.101 |
| 7 days | 1,324 | +0.223 | +0.015 |

This is a **different matched-date population for each lag**. An apparent maximum at one day is a hypothesis for later proper basin-rainfall evaluation, not an identified physical catchment travel time or a causal effect.

## Station-specific relationship (not statewide hydro)

| Same-day Idukki gauge/reservoir variable vs Idukki station MU | Paired days | Pearson r | Year-month demeaned r |
|---|---:|---:|---:|
| Gauge rainfall | 1,345 | −0.010 | −0.131 |
| Reported inflow | 2,387 | +0.122 | −0.054 |
| Effective stored volume | 2,546 | +0.157 | +0.073 |

These associations show why generation cannot be deduced from same-day rainfall. The station is dispatchable, drawdown and operating constraints matter, and even the matched source station is not by itself a complete water balance.

## Strictly chronological holdout diagnostic

A **retrospective same-day** ridge regression uses observed rainfall for `t, t−1, …, t−7`, plus *reported* previous-calendar-day inflow. Days without all these values are **excluded, not filled**. Train through 2024-12-31 (**434 complete-case days**), test 2025-01-01 through 2026-09-23 (**158 complete-case days**). Persistence compares the observed inflow on the previous *calendar* day, on those exact same test dates.

| Method on same 158 held-out days | MAE (MCM/day) | RMSE (MCM/day) |
|---|---:|---:|
| Previous-day inflow persistence | 5.3616 | 8.6479 |
| Rain lags + previous inflow, standardized ridge | 3.3650 | 5.3450 |

The model has **37.24% lower MAE** than persistence *on this selected complete-case holdout only*. It is **not** a forecast (rain at `t` is included), it is not established as robust across extreme floods, and cannot claim year-round generalization because gauge rainfall is missing for many days. In particular, the 2018 event has **zero** source-matched electricity days.

## Event review: comparison is descriptive, not an event-effect estimate

Numbers below compare **event-day means with nearby ±45-day non-event dates** in this SLDC archive. They are unadjusted for weekday, temperature, changing demand baselines, COVID-era activity, reservoir operating decisions, affected network footprint or other weather. They are therefore *not estimated flood impacts*.

| Event | Idukki-gauge rain, event vs flank (mm/day) | Idukki inflow, event vs flank (MCM/day) | Idukki station, event vs flank (MU/day) |
|---|---:|---:|---:|
| Aug 2019 flood review | 58.81 vs 20.05 | 65.23 vs 16.28 | 1.51 vs 3.00 |
| Pettimudi Aug 2020 landslide | 89.07 vs 21.78 | 75.27 vs 12.46 | 3.55 vs 4.43 |
| Oct 2021 flood window | 46.53 vs 16.48 | 46.59 vs 17.35 | 11.97 vs 11.45 |
| Wayanad 2024 landslide | 35.23 vs 21.20 | 38.40 vs 15.08 | 10.66 vs 7.59 |
| Nilambur 2026 flash flood | 19.53 vs 19.43 | 11.28 vs 12.67 | 8.28 vs 5.62 |

The Nilambur event is in **another catchment**, so Idukki-gauge conditions do **not** measure its local severity. The 2018 flood window is outside the SLDC archive, and unrelated landslides are not silently relabelled basin floods. Only verified KSDMA/IMD geographic event footprints can turn the event labels into basin exposure variables.

## Illustrative PSP physics only

A transparent **hypothetical** calculation for 1 MCM shifted across a **500 m assumed** head, at assumed generation/pump efficiencies 90%/85%, gives 1.3625 GWh gross, **1.22625 GWh** generated, **1.60294 GWh** pump input, 76.5% assumed round-trip efficiency. This **is not** the Idukki 600 MW PSP proposal, an operating scheme, 1 MCM of usable water, a verified head or evidence of safe flood-season pumpability. Storage must reserve flood headroom and honor rule curves, downstream releases, ecological and grid constraints. The other 800 MW Idukki extension proposal must not be conflated with a pumped-storage plant.

## Still gated; do not mark the full digital twin complete

1. **ERA5-Land 2018–2026 catchment series:** not provided or downloaded in this execution. An existing FY2024–25 five-point ERA5 series does not establish basin-average rain. Acquire audited drainage polygons and 2018–2026 subregional hourly `tp` and `t2m`, handle **ERA5-Land** accumulation conventions, compute IST daily increments and source-pixel catchment weights. Distinguish preliminary 2026 near-real-time data from consolidated vintages. The script's `--weather-daily` gate requires explicit `source_id`, `spatial_support` and `precipitation_processing` per daily record; it does **not** accept an unqualified daily CSV.
2. **2018:** independent flood/rainfall/hydro and KSEBL/CEA dated electricity data must be recovered separately. No extrapolation of SLDC dates before 2019-08-06.
3. **Metered Energy Atlas:** still **zero rows admitted**. A sandbox demand `modeled` response is not metered. Acquire a Kerala-only, source-identified, time/unit-boundary-defined sample and match to the private SLDC source chronology before integration.
4. **Water balance:** acquire actual turbine discharge/plant generation, non-power releases, spill, diversion, evaporation/loss and calibrated active storage–elevation curves to constrain hydrology and flood operations.
5. **PSP:** verify upper/lower-reservoir topology, hydraulic head, acceptable operating window, 15-minute metered load/renewables, capex and transmission. The engineering example is not a site capacity estimate.

**Reproduce:** `python analysis/idukki_hydro_energy_phase4.py --curated PRIVATE_CURATED_DIR --out PRIVATE_OUTPUT_DIR`. See the machine-readable QA for pinned source-file hashes and monthly observed-only aggregate. Never upload the detailed date-level output to the public repo without an explicit third-party redistribution decision.

**Method reference for future ERA5 ingestion:** [ECMWF ERA5-Land accumulation documentation](https://confluence.ecmwf.int/pages/viewpage.action?pageId=402639006) and [ECMWF ERA5-Land hourly time-series user guide](https://confluence.ecmwf.int/pages/viewpage.action?pageId=576394633). Source flood-event scope and PSP project distinctions are documented in the [Phase 3 audit](SLDC_FLOOD_HYDRO_WEATHER_ATLAS_PHASE3_2026_09_23.md).

### Prepared CDS acquisition without fabricating spatial support

`python scripts/request_era5_land_hydro_monthly.py --area NORTH WEST SOUTH EAST --out PRIVATE_DIR` writes the **dry-run monthly request plan** by default (2017-12-31 to 2026-09-22, with early boundary context for the 2018 flood and IST date conversion). `--execute` is opt-in and requires the user's own local `cdsapi` credentials. The area is deliberately required; no guessed Idukki catchment polygon is embedded in the script. GRIB magic and SHA-256s are checked, and unexpected ZIP/download responses stop rather than masquerading as valid original data. The downloader acquires originals only: **it does not deaccumulate rainfall, geospatially mask a basin, or complete the observed-weather join.**
