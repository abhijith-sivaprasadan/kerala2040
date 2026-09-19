# Observed-detail PyPSA baseline

This is the next modelling layer after the v1.0.1 SLDC evidence integration.

## What it does

`scripts/build_observed_daily_network.py` builds a PyPSA network directly from the
FY2024-25 public Kerala SLDC evidence already committed under
`data/external/sldc_fy2024_25/`.

The network has **354 observed daily snapshots**, each weighted by 24 hours. It
contains:

- one Kerala electricity bus;
- the published statewide daily consumption as the fixed load;
- individually named hydro-station generators for station rows that were actually reported;
- an explicit `hydro_unallocated` generator for the difference between the published
  statewide hydro total and the sum of named station rows;
- one fixed generator for each of the eight reported interstate import interfaces;
- one residual non-hydro internal generator equal to internal generation minus hydro.

This gives us a reproducible source-attribution network without inventing hourly
dispatch or filling the eleven missing days.

## Why the hydro residual is required

The station table does not allocate the complete statewide hydro total to named
stations on every observed day. Some generation is reported in aggregate groups
and some station cells are blank. A blank cell is not evidence of zero output.

For that reason a missing station cell receives no named-station attribution in
PyPSA. The published aggregate hydro total remains authoritative, and its
unallocated remainder is assigned to `hydro_unallocated`. This prevents the model
from silently converting missing observations into measured zeros.

## Why reservoir stores are not yet connected

The archive contains daily reservoir levels, effective storage, storage percentage,
and reported generation-capability quantities. Those observations are valuable for
validation and future constraints, but they are not yet used as PyPSA `Store` or
`StorageUnit` energy bounds.

The reason is physical rather than software-related: we do not yet have a fully
verified reservoir-to-powerhouse/cascade map, mandatory releases, head-dependent
conversion factors, spill routing, or FY2024-25 operating rules. Imposing the
reported reservoir MU values before resolving those relationships could double-count
the same water in cascaded stations.

## Why interfaces are not transmission lines

The eight import rows are daily imported **energy**, not thermal line ratings, ATC,
TTC, or N-1 transfer limits. They therefore remain fixed source-attribution
generators connected to the Kerala bus. Their `p_nom` values are only profile
normalisers and must not be interpreted as physical interface capacity.

## Run

```bash
pip install -e ".[dev]"
python scripts/build_observed_daily_network.py
```

Outputs:

```text
results/models/observed_daily_detail/
├── kerala_fy2024_25_observed_detail.nc
└── summary.json
```

The summary records model classification, carrier and generator energy, source
archive identity, missing-date handling, and the fact that no hourly telemetry or
reservoir operating constraints were used.

## Next gates

This observed-detail network is the historical accounting foundation for later
chronological and 2040 models. The remaining gates are:

1. measured 15-minute/hourly Kerala demand and actual interchange;
2. verified reservoir-powerhouse-cascade relationships and operating limits;
3. authoritative interstate transfer capability;
4. reconciled plant nameplates/availability;
5. model-ready renewable siting limits and hourly weather;
6. harmonised 2040 technology costs and finance assumptions.

Until those are resolved, the proxy-hourly screening remains a sensitivity model,
not a calibrated chronological representation.
