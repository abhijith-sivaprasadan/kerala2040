# Idukki v1.4 cumulative-accounting recovery audit

A second audit was run against the SHA-verified Phase-4 `reservoir_rows.csv`
after the real-source v1.4 gate found 325/364 directly reported pilot-day
Idukki inflows.

The source's cumulative monthly inflow field is internally useful: between
consecutive cumulative observations, the cumulative increase normally equals
the sum of daily inflows over that interval.

The audit admits a missing daily value as **uniquely source-derived** only when
the source accounting gives one non-negative solution. No weather, storage
interpolation, hydrology model or neighbouring-day interpolation is used.

## Month-start anchor

The source convention was checked independently across the full retained
archive. There are **78 Idukki first-of-month rows** where both direct daily
inflow and cumulative monthly inflow are present. In **78/78**, the two values
are exactly equal. This establishes an exact zero cumulative anchor at each
month boundary.

That rule resolves **2025-03-01 = 0.0 MCM**: on 2 March the cumulative monthly
value is 1.624 and the directly reported 2 March inflow is also 1.624, leaving
zero contribution for 1 March.

## Result

- Directly reported pilot inflow: **325/364 days**.
- Uniquely source-derived from cumulative accounting: **29 days**.
- Combined direct + source-derived coverage: **354/364 days (97.253%)**.
- Still unresolved after cumulative accounting: **10 days**.

The six non-zero recovered values from missing source-report dates are:

| Date | Derived inflow (MCM/day) |
|---|---:|
| 2024-08-12 | 13.286 |
| 2024-09-06 | 12.447 |
| 2024-09-20 | 4.636 |
| 2024-10-26 | 23.514 |
| 2024-11-17 | 2.479 |
| 2024-12-16 | 5.836 |

The other **23** uniquely recovered days are 0.0 MCM/day.

## Remaining 10

The unresolved dates are:

- 2024-04-01
- 2024-04-02
- 2024-04-09
- 2024-04-11
- 2024-05-04
- 2024-11-30
- 2025-02-19
- 2025-02-20
- 2025-03-17
- 2025-03-18

They remain unresolved because:

- the source cumulative series contains a negative/corrected increment around
  2024-04-02, 2024-04-09, 2024-04-11 and 2024-05-04;
- 2024-04-01 has an already-negative first-of-month cumulative value and
  2024-11-30 lacks a valid end-of-month source report;
- 2025-02-19 + 2025-02-20 and 2025-03-17 + 2025-03-18 each share an exact
  two-day cumulative total but cannot be separated using SLDC alone.

## Scientific boundary

This audit does **not** change the strict Full-PyPSA v1.4 gate. The 29 values
are not relabelled as directly observed daily inflow.

They are suitable for a separately labelled source-derived sensitivity. The
independent Dam Safety cross-check can then constrain timing inside the two
two-day aggregate intervals without changing their SLDC total volume.
