# Idukki v1.4 — KSEB Dam Safety cross-check

The cumulative-accounting audit reduced the 39 missing direct SLDC inflow days
to 11 unresolved dates. A separate KSEB Dam Safety Organisation series was then
reviewed as an independent hydro-operations source.

The historical mirror used here is
`amith-vp/Kerala-Dam-Water-Levels/historic_data/Idukki.json`. Its README and
collector code state that it scrapes KSEB Dam Safety Organisation and Kerala
SDMA data. The mirror explicitly warns that parsing/source errors remain
possible, so it is not treated as authoritative by itself.

For 17 and 18 March 2025, the mirror was checked against the directly retrieved
official KSEB pages and matched Idukki inflow, storage, powerhouse discharge,
spillway release and rainfall.

## Important unit result

KSEB Dam Safety reports Idukki **inflow as a rate in cumecs**. The SLDC Phase-4
archive contains a different daily inflow field used as MCM/day.

A 23-day spread of directly observed SLDC dates was compared with Dam Safety
inflow converted as `cumecs × 0.0864` MCM/day. The series correlate strongly
(r ≈ **0.970**) but do **not** agree closely in magnitude:

- mean absolute difference: **1.750 MCM/day**
- median absolute difference: **1.753 MCM/day**
- median SLDC / converted-Dam-Safety ratio: **1.347**
- only **1/23** sample days is within 0.1 MCM/day

Therefore Dam Safety rate values must **not** be substituted directly for
missing SLDC daily inflow volumes.

## What Dam Safety can still resolve

Two unresolved SLDC intervals have an exact cumulative two-day volume but no
unique daily split:

- 19–20 February 2025: **0.698 MCM total**
- 17–18 March 2025: **1.760 MCM total**

For a separately labelled timing sensitivity only, the exact SLDC interval
volume can be preserved while allocating it in proportion to the independent
Dam Safety rate on each day:

| Date | Timing-sensitivity allocation (MCM) |
|---|---:|
| 2025-02-19 | 0.231523 |
| 2025-02-20 | 0.466477 |
| 2025-03-17 | 0.267826 |
| 2025-03-18 | 1.492174 |

This does not change monthly water volume and is not labelled as observed daily
SLDC inflow.

After combining the 28 unique cumulative recoveries with these two interval
timing allocations, only **7 dates** remain unconstrained:

2024-04-01, 2024-04-02, 2024-04-09, 2024-04-11, 2024-05-04,
2024-11-30 and 2025-03-01.

The strict v1.4 gate remains unchanged. The 7-day residual uncertainty should
now be handled as an explicit sensitivity/bound rather than silently filled.
