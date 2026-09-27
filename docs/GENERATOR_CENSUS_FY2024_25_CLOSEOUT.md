# FY2024-25 Kerala generator capacity census — reconciliation closeout

**Snapshot:** 31 March 2025  
**Status:** **installed-capacity accounting reconciled; dispatch/availability gate remains open**

This chapter supersedes the earlier use of the KSEB Project Management System
project list as the closest thing to a generator register. The PMS extract remains
useful audit history, but its 70 captured rows are stale/incomplete and contain
project-status and kW/MW conflicts. It is not the FY2024-25 operating fleet.

The new census starts from the official Kerala/KSEBL capacity anchors and uses a
station/farm/portfolio decomposition only where that decomposition can be checked
against those anchors.

## Official accounting boundary

Kerala State Planning Board's *Economic Review 2025*, based on KSEBL data, reports
the following installed capacity as at 31 March 2025:

| Technology | Official MW |
|---|---:|
| Hydel | 2,284.42 |
| Thermal | 536.54 |
| Solar | 1,519.66 |
| Wind | 71.53 |
| **Printed total** | **4,412.14** |

Appendix 11.2.4 provides a more detailed commercial/source split:

| Published source category | MW |
|---|---:|
| Hydel: KSEB | 2,196.36 |
| Thermal: KSEB | 159.96 |
| Wind: KSEB | 2.03 |
| Solar: KSEB | 51.43 |
| Solar other than KSEBL | 1,264.23 |
| Solar: IPP | 204.00 |
| NTPC thermal | 359.58 |
| Thermal: CPP | 17.00 |
| Hydel: CPP | 33.50 |
| Hydel: IPP | 54.56 |
| Wind: IPP | 58.50 |
| Wind: CPP | 11.00 |

Those printed category rows sum to **4,412.15 MW**, not the table's **4,412.14 MW**
printed total. This is a source-level 0.01 MW inconsistency, not a Kerala2040
calculation error. The Government of Kerala's *Carbon Neutral Kerala by 2050*
report explicitly notes the same correction: the bifurcated source rows produce
4,412.15 MW rather than the quoted 4,412.14 MW.

Kerala2040 therefore preserves both numbers. There is **no balancing generator** and
no arbitrary 0.01 MW adjustment.

## Bottom-up register

The machine-readable census contains **112 included rows**:

- **98 station/farm-level rows**;
- **14 aggregate/distributed buckets**, principally rooftop/prosumer/off-grid solar.

The detailed rows sum to **4,412.156 MW**. This is 0.016 MW above the printed
4,412.14 MW headline and 0.006 MW above the category-row arithmetic of
4,412.15 MW. The extra precision is completely traceable:

- KSEBL hydro station rows sum to **2,196.361 MW** versus the official rounded
  **2,196.36 MW**;
- KSEBL wind is **9 × 0.225 = 2.025 MW** versus the official rounded **2.03 MW**;
- the detailed non-KSEBL/non-IPP solar decomposition sums to **1,264.24 MW**
  versus the official category value **1,264.23 MW**.

All other commercial-category buckets reconcile exactly to the published anchors.

### KSEBL hydro

The census identifies **44 KSEBL hydel stations**, matching the official station
count. Their detailed capacities sum to 2,196.361 MW, which rounds to the official
2,196.36 MW. The set includes the FY2024-25 additions:

- Thottiyar HEP — 40 MW;
- Pallivasal Extension Scheme — 60 MW.

The Poringalkuthu micro unit is retained as **0.011 MW**, not the stale PMS numeric
field of 11 MW.

### Non-KSEBL hydro

The detailed technical list closes exactly to the official **88.06 MW**:

- captive/CPP: **33.50 MW**;
- IPP: **54.56 MW**.

This includes 15 station-level rows. No residual hydro plant is invented.

### Thermal

The capacity-accounting boundary includes:

- KSEBL BDPP: 63.96 MW;
- KSEBL KDPP: 96.00 MW;
- NTPC Kayamkulam: 359.58 MW;
- Phillips Carbon Black co-generation CPP: 17.00 MW.

These reproduce **536.54 MW** exactly.

The stale PMS BSES Kochi and Kasaragod Power/KPCL entries are retained as
**historical exclusions**, not silently deleted. They are not counted in the
31 March 2025 official installed-capacity accounting because the contemporary
technical source says BSES and KPCL are not considered after their PPAs expired.

This installed-capacity treatment does not imply that every included thermal MW was
economic, dispatched or available during FY2024-25.

### Wind

The register preserves the precise KSEBL Kanjikode value of **2.025 MW** and
69.50 MW of private/captive wind:

- IPP: **58.50 MW**;
- CPP: **11.00 MW**.

The private list includes the 0.25 MW RPPL addition commissioned in September 2024.

One technical-table inconsistency is deliberately visible: the RPPL captive row
prints a unit expression inconsistent with its 1.00 MW station-capacity field.
The 1.00 MW field is retained because it is also the value needed for the published
11.00 MW Wind:CPP category when combined with Malayala Manorama's 10 MW. The
unit-count text is not silently repaired.

### Solar

Solar is the one technology for which a complete physical asset-by-asset census is
not publicly available. The register therefore distinguishes named plants from
aggregate buckets instead of pretending every rooftop is a single generator.

KSEBL solar reconciles exactly to **51.43 MW**, including named ground/canal plants,
an explicit 10.92 MW small-installation aggregate, and a 23.26 MW SOURA aggregate.

The private/non-KSEBL decomposition includes named CPP/prosumer plants and five
named IPP blocks totalling **204 MW**, plus explicit distributed/utility-licensee
buckets. The detailed non-KSEBL/non-IPP rows sum to **1,264.24 MW**, 0.01 MW above
the Appendix 11.2.4 category value. That source/decomposition discrepancy is
preserved.

## What this closes

The following statement is now defensible:

> Kerala2040 has a source-bounded FY2024-25 installed-generation capacity register
> that reconciles the material station/farm assets and explicit distributed
> aggregates to the official Kerala/KSEBL capacity accounting boundary, with
> source rounding/revision discrepancies preserved rather than hidden.

This is substantially stronger than the old 70-row PMS project seed.

## What this does **not** close

Installed MW is still not operational MW. The following gates remain open:

- unit-level hourly/interval availability;
- outages and deratings;
- plant-level FY2024-25 measured generation reconciliation;
- PPA/contract status where it affects dispatch rather than geographic installed
  capacity;
- fuel availability and start/ramp/minimum-stable-output constraints for thermal;
- hydro head, reservoir/cascade and water constraints outside the separately
  modelled Idukki work;
- individual enumeration of every distributed rooftop/prosumer solar system.

Consequently, the census is suitable as the **capacity-accounting spine** for
PyPSA/OSeMOSYS asset mapping, but it must not be passed directly into either model
as fully available hourly capacity.

## Reproduce

```bash
python scripts/build_generator_census_fy2024_25.py
```

Outputs:

- `results/inventory/fy2024_25_generator_census/generator_census.csv`
- `results/inventory/fy2024_25_generator_census/generator_census.parquet`
- `results/inventory/fy2024_25_generator_census/generator_census_summary.json`

The CI gate checks all 44 KSEBL hydro stations, category/sector/technology
reconciliation, distributed-solar aggregation, historical exclusions and the
absence of a balancing/fudge row.

## Source hierarchy

1. Kerala State Planning Board, *Economic Review 2025*, Volumes I and II —
   official headline/category/sector anchors, underlying source KSEBL.
2. KSEBL, *14th Annual Report 2024-25* — official FY boundary and KSEBL source
   referenced by state publications.
3. Kerala State Electricity Board Engineers' Association technical document —
   station/farm/portfolio decomposition, admitted only under the official anchors.
4. Government of Kerala, *Carbon Neutral Kerala by 2050* — independent state
   publication explicitly documenting the 4,412.15 versus 4,412.14 arithmetic
   correction.
