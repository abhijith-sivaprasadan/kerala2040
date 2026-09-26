# Full-PyPSA v1.4 — Idukki source-reported inflow gate

**Status:** code-complete source gate; physical reported-inflow run blocked until
the exact private Phase-4 SLDC `reservoir_rows.csv` is supplied.

v1.3 introduced a real reservoir storage state for Idukki, but its water input
was reconstructed from storage change and station generation. v1.4 removes that
shortcut. The intended state equation is:

```text
S[t+1] = S[t] + reported_inflow[t]
         - turbine_water_equivalent[t]
         - non_turbine_release[t]
```

The daily inflow must come directly from the audited `inflow_mcm_day` field in
the private Kerala SLDC archive. The expected `reservoir_rows.csv` SHA-256 is:

`b7d4439135edbe02d9e577892e090aafaf92f58606cdc04ee9b6d39e608036c9`

Phase 4 established 2,414 source-reported Idukki inflow days across
2019-08-06 to 2026-09-23. The public repository intentionally does not contain
the detailed daily rows pending source-redistribution review.

## Fail-closed rules

The physical v1.4 run requires all **364** inflow days from 2024-04-01 through
2025-03-30. Missing, nonnumeric, negative or >300 MCM/day values stop the run.
There is **no inflow interpolation**.

The model's `non_turbine_release` variable is an aggregate optimized water
outflow. It can represent spill and other non-generating releases, but it is
not an observed spill chronology. Historical

`reported inflow - storage change - turbine water equivalent`

is retained as a diagnostic residual. Negative values are reported as source,
timing or fixed-conversion inconsistency and are never clipped into invented
zero spill.

## Objective ordering

1. Minimize unserved energy.
2. Preserve minimum shortage and minimize candidate annualized investment plus
   import energy cost.
3. Preserve the stage-2 system cost and minimize non-turbine water release.

The third stage is only a deterministic tie-break. It does not assign an
economic water value.

## Running the gate

Without private data:

```bash
python scripts/run_full_pypsa_idukki_inflow_release_v1_4.py --gate-only
```

With the exact private source:

```bash
python scripts/run_full_pypsa_idukki_inflow_release_v1_4.py \
  --private-reservoir-rows PRIVATE/reservoir_rows.csv
```

If any of the 364 pilot inflow dates are absent, the command refuses the
physical run and reports the missing dates. Once the source gate passes, the
same 12 demand × transfer × Idukki-availability cases used by v1.3 are solved.

## What remains outside v1.4

- observed spill versus controlled downstream/environmental releases;
- head-dependent turbine efficiency and tailwater;
- rule curves and flood-control constraints;
- evaporation and diversion accounting as separately observed terms;
- cascade routing below Moolamattom;
- source-verified basin geometry and ERA5-Land catchment validation;
- a validated Kerala capacity plan.

The next data action is therefore not another synthetic hydro window. It is
recovery of the exact private daily inflow source into an execution environment,
followed by date-level coverage QA. If the source has pilot-period gaps, those
specific SLDC dates must be reacquired rather than interpolated.
