# Full-PyPSA v1.4b — source-cumulative Idukki inflow sensitivity

The strict v1.4 model remains blocked because 39 of 364 pilot-day Idukki
`inflow_mcm_day` cells are not directly source-reported. v1.4b does **not**
change that gate. It creates a separate sensitivity layer using only explicit
source conventions and cumulative-accounting constraints.

## What the uploaded archive establishes

The regenerated private `reservoir_rows.csv` exactly matches the Phase-4
SHA-256 required by v1.4.

Across the full Idukki archive there are **153** blank daily-inflow cells for
which a direct same-month cumulative change can be calculated. None has a
materially positive cumulative increment above **0.0011 MCM**:

- 101 are effectively unchanged within tolerance;
- 52 are negative cumulative corrections;
- 0 are materially positive.

That archive-wide pattern supports treating an accepted blank daily inflow as
**zero for sensitivity purposes**, while retaining negative cumulative changes
as source corrections rather than negative physical inflow.

This is a source-convention interpretation, not a raw observation.

## What this buys us

For the 364-day pilot:

- 325 daily inflows remain direct source observations;
- 28 accepted blank cells are normalized to zero in v1.4b;
- of the 11 rejected source dates, 10 can then be recovered by adjacent
  same-month cumulative conservation;
- only **2024-11-30** remains unconstrained because it is a missing month-end
  report with no following November cumulative observation.

The ten cumulative-derived rejected dates contribute **64.656 MCM in total**.
No date-level derived values are published in the repository.

## 30 November sensitivity

v1.4b brackets the single unresolved day with transparent empirical values from
the source archive:

| Case | 30 Nov inflow assumption | Pilot inflow total | Water-energy equivalent of unresolved day* |
|---|---:|---:|---:|
| lower | 0 MCM | 2525.925 MCM | 0 GWh |
| November median | 3.566 MCM | 2529.491 MCM | 5.242 GWh |
| November p95 | 9.5574 MCM | 2535.4824 MCM | 14.049 GWh |
| November max | 11.623 MCM | 2537.548 MCM | 17.086 GWh |
| pilot-max stress | 74.038 MCM | 2599.963 MCM | 108.836 GWh |

*Using the existing 1470 MWh/MCM source energy-equivalent conversion. This is
not guaranteed electrical generation.

The seasonal 0-to-November-max uncertainty changes total pilot inflow by only
11.623 MCM, about 0.46% of the lower-case pilot total. The extreme pilot-max
stress is intentionally much wider.

## Live source retry

A dedicated GitHub Actions run retried all eleven missing Storage dates and the
known-observed 2024-11-29 control. It recovered **0/11**, but the control also
failed. Therefore the result is an access/replay limitation, not evidence that
the eleven agency records do not exist.

## Usage

The builder requires the exact private Phase-4 `reservoir_rows.csv` and writes
complete daily v1.4b scenario series only to a private output directory:

```bash
python scripts/build_idukki_cumulative_inflow_v1_4b.py \
  --private-reservoir-rows PRIVATE/reservoir_rows.csv \
  --private-output-dir PRIVATE/v1_4b
```

Those daily reconstructed rows are not for public commit until source reuse
terms are resolved.

## Model status

This closes the **input-construction** problem for a source-informed sensitivity
matrix, but not the strict source-reported v1.4 gate. The next numerical step is
to feed these five private inflow scenarios into the existing stateful Idukki
PyPSA formulation and measure whether the single unresolved date materially
changes adequacy or capacity results.
