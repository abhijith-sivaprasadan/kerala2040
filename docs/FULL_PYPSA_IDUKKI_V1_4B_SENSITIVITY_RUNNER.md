# Full-PyPSA Idukki v1.4b — 60-case sensitivity runner

This layer connects the private v1.4b inflow scenarios to the existing stateful
Idukki PyPSA optimization. It does not change the strict v1.4 evidence gate.

## Matrix

The real private run contains **60 physical cases**:

- 5 v1.4b inflow scenarios for the unresolved 30 November 2024 inflow;
- 2 demand cases;
- 3 interstate transfer cases;
- 2 Idukki powerhouse-availability cases.

Each case uses the v1.4 lexicographic solve:

1. minimize unserved energy;
2. preserve minimum shortage and minimize candidate investment plus import cost;
3. preserve stage-2 system cost and minimize non-turbine water release.

The five inflow scenarios are:
`nov30_zero_lower`, `nov30_same_month_median`,
`nov30_same_month_p95`, `nov30_same_month_max`, and
`nov30_pilot_max_stress`.

## Private execution

The runner first rebuilds the five complete daily v1.4b inflow series from the
exact source-hashed private `reservoir_rows.csv`. It then feeds each daily
series to the stateful Idukki solver.

```bash
python scripts/run_full_pypsa_idukki_v1_4b_sensitivity.py \
  --private-reservoir-rows PRIVATE/reservoir_rows.csv \
  --private-work-dir PRIVATE/v1_4b_scenarios \
  --profile results/models/full_pypsa/era5_renewables_v0_6/statewide_equal_weight_profile.parquet \
  --acknowledge-source-informed-not-observed
```

The reconstructed daily inflow CSVs remain private. The public result may report
aggregate sensitivity ranges and case outputs subject to source-reuse review,
but it must not relabel the input series as observed.

## What the result will answer

For each fixed demand/transfer/Idukki-availability condition, the summary reports
the range across all five inflow assumptions for:

- unserved energy;
- Idukki generation;
- non-turbine release;
- solar build;
- wind build;
- BESS power.

If these ranges are negligible, the single unresolved 30 November inflow is not
material to the planning result. If they are material, the project must retain
the uncertainty bracket rather than selecting a preferred point estimate.

## Current release state

Public CI validates the matrix definition, private scenario loader and
sensitivity summarizer. It deliberately does **not** claim the real 60-case
private matrix has run.
