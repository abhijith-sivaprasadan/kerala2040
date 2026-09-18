# Kerala 2040 evidence register

This file records what the currently verified public sources can support and, equally important,
what they cannot support. It is intended to prevent a convenient secondary dataset or published
scenario from silently becoming model truth.

## Operational baseline sources

| Source | What is usable now | Resolution | Role | Limitation |
|---|---|---:|---|---|
| Kerala SLDC system statistics | Internal generation, hydro/thermal/IPP totals, interface net imports, consumption, schedules and related accounting labels | Daily | Primary historical balance | Public page does not expose a complete historical state 15-minute load series through the interface currently used |
| Kerala SLDC storage statistics | Reservoir level/storage, energy-equivalent capability, inflow, rainfall/spill and station rows | Daily | Hydrology/storage state | Needs climate/hydrology modelling for future inflow, not simple extrapolation |
| Grid-India Daily PSP / MOP_E | State daily energy met, peak demand met, shortage and schedule fields | Daily | Independent official cross-check | Workbook TimeSeries is national; it is not a Kerala 15-minute load series |
| NASA POWER | Temperature, humidity, solar radiation, wind and precipitation at selected points | Hourly | Weather covariates / initial resource screening | Point samples are not statewide renewable-potential estimates |
| data.gov.in OGD | Resource-specific public APIs | Dataset-dependent | Additional official series | Some endpoints require an API key and resource IDs must be verified rather than guessed |
| NITI ICED | Dataset discovery/cross-checking | Dataset-dependent | Discovery | No stable undocumented API is assumed by this project |

## Published Kerala planning studies

### CSTEP — *Kerala Energy Transition Roadmap 2040* (2024)
Primary publication: https://cstep.in/publication/kerala-energy-transition-roadmap-2040/
Government-hosted PDF: https://keralaenergy.gov.in/wp-content/uploads/2023/12/CSTEP_KL_Roadmap_2040_01Feb24-1-4.pdf

The study projects FY2040 final electricity requirement of 45,519 MU including T&D losses and
7,594 MW peak demand. Its FY22 load curve was derived from FY16 15-minute observations and
extrapolated. We retain these values as a published benchmark, not as our calibrated 2040 answer.

A machine-readable extraction is maintained in `data/external/cstep_2024/`. It includes the
published FY2016-FY2022 category consumption table, FY2023-FY2040 demand pathway, EV and
peak-demand milestones, BAU and High-RE capacity-addition paths, CSTEP GIS/resource-potential
benchmarks, supply-model assumptions and storage results. Projected values are classified
`published_external_scenario`; historical values reproduced from KSEB are classified
`official_observed_reference` with CSTEP as the immediate source and KSEB retained as the
upstream source named by CSTEP.

CSTEP's GIS results (for example 10,953 MW usable solar and 2,993 MW wind potential) are
validation benchmarks, not this project's GIS capacity ceilings. CSTEP's reported storage
power/energy pairs are preserved exactly as published; their implied durations are unusually long,
so the underlying storage-calculation definition must be verified before using them as model targets.

The FY2016 15-minute series itself is **not** present in the report. Recovering that underlying
dataset from CSTEP/EMC/KSEBL/SLDC is now a priority acquisition task. Figure digitisation must
not be presented as measured telemetry.

### DoECC / Vasudha Foundation — *Carbon Neutral Kerala by 2050* (2026)
Primary report: https://climatechange.envt.kerala.gov.in/wp-content/uploads/2026/06/Carbon-Neutral-Kerala-by-2050-Report.pdf

The newer pathway reports combined in-state renewable potential of about 18.92 GW, treats
interstate procurement as a flexible system option and states that in-state resource potential is
insufficient for its projected supply requirement beyond 2030. It reports 2040 net-grid demand of
65.98 TWh in BAU and 88.56 TWh in CN50. These are much higher than the 2024 CSTEP pathway
because the studies have different scopes and electrification assumptions; the values must not be
averaged or blended.

### EMC / KPMG — ESS viability work (2025)
Report catalogue: https://keralaenergy.gov.in/?p=2951

The public presentation analyses Kerala hourly-demand growth and storage viability. It is useful
for checking load-shape assumptions and storage framing, but it does not replace measured
historical telemetry.

## Hourly-demand gap

A robust public 8,760-hour Kerala state-demand series for the selected calibration year has not yet
been secured. This is an explicit data gap, not a reason to fabricate a curve.

Evidence that the underlying data exist is strong: Kerala resource-adequacy studies analyse FY2022-23
hourly demand, the 2024 CSTEP roadmap refers to block-wise load data, and Kerala planning rules
require hourly/sub-hourly demand databases and forecasts. Public availability of the raw historical
series is a separate question.

Until a primary hourly series is secured, the project will:

1. calibrate annual and daily energy balances from SLDC;
2. validate daily energy and peak metrics against Grid-India;
3. use published hourly profiles only as labelled reference/proxy cases if required;
4. never describe a reconstructed proxy as measured Kerala telemetry.

## Source hierarchy

For a contested number, prefer: primary Kerala/India operational source → regulator/government
report → official commissioned study → research publication → secondary aggregation. Each
processed dataset retains source identifiers and retrieval hashes where the upstream format permits.
