# Idukki v1.4 real-source gate execution — 26 September 2026

The uploaded raw Kerala SLDC five-section archive was re-normalized with the same
provenance-preserving storage-row logic used by the project. The regenerated
`reservoir_rows.csv` SHA-256 is:

`b7d4439135edbe02d9e577892e090aafaf92f58606cdc04ee9b6d39e608036c9`

This exactly matches the Phase-4-audited source required by Full-PyPSA v1.4.

## Strict pilot coverage

For the 364-day Idukki pilot period from 2024-04-01 through 2025-03-30:

- 325 days have valid source-reported Idukki `inflow_mcm_day`;
- 39 days do not;
- coverage is 89.285714%;
- the v1.4 physical matrix therefore remains blocked under the no-interpolation rule.

The 39 gaps split into two materially different classes:

- **28 accepted storage reports** where the Idukki row is present but the daily
  inflow cell itself is blank;
- **11 rejected storage reports**, exactly matching the already-known FY2024-25
  missing-report dates.

The 11 rejected dates are:
2024-08-12, 2024-09-06, 2024-09-20, 2024-10-26, 2024-11-17,
2024-11-30, 2024-12-16, 2025-02-19, 2025-03-05, 2025-03-10,
and 2025-03-17.

## Cumulative-inflow diagnostic

The accepted source also contains a cumulative monthly inflow field. Across
2,308 consecutive accepted Idukki day pairs, the absolute difference between
reported daily inflow and the day-to-day cumulative-field increment is within
0.01 MCM on 99.740035% of pairs. The median absolute difference is effectively
zero.

For 20 of the 28 accepted-but-blank pilot dates, the direct cumulative-field
difference is exactly 0.0 MCM. These are useful **source-derived candidates**,
but they are deliberately not admitted as observed daily inflow. The
archive-wide relationship is not exact on every day, and the v1.4 gate was
defined specifically around the source-reported daily inflow field.

## Decision

Do not weaken the v1.4 gate and do not interpolate the 39 dates.

The next evidence work is:

1. recover the eleven rejected SLDC storage reports from an authoritative
   original/revised source;
2. resolve the 28 accepted-source blank inflow cells using explicit agency
   revision/clarification or another independently authoritative inflow record;
3. rerun the 364-day source gate;
4. only when all 364 daily inflows are source-admitted, execute the 12-case
   v1.4 physical reservoir matrix.

This result is a successful source-authentication and coverage audit, not a
failed model run and not a completed inflow-driven reservoir simulation.
