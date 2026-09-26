# Idukki v1.4 cumulative-accounting recovery audit

A second audit was run against the SHA-verified Phase-4 `reservoir_rows.csv`
after the real-source v1.4 gate found 325/364 directly reported pilot-day
Idukki inflows.

The source's cumulative monthly inflow field is internally useful: between
consecutive cumulative observations, the cumulative increase normally equals
the sum of daily inflows over that interval. The audit therefore admits a
missing daily value as **uniquely source-derived** only when:

1. both interval endpoints have source cumulative values;
2. all other daily inflows inside the interval are directly reported;
3. exactly one daily inflow is unknown; and
4. the resulting residual is non-negative.

No weather, storage interpolation, hydrology model or neighbouring-day
interpolation is used.

## Result

- Directly reported pilot inflow: **325/364 days**.
- Uniquely source-derived from cumulative accounting: **28 days**.
- Combined direct + source-derived coverage: **353/364 days (96.978%)**.
- Still unresolved: **11 days**.

The six non-zero recovered values from missing source-report dates are:

| Date | Derived inflow (MCM/day) |
|---|---:|
| 2024-08-12 | 13.286 |
| 2024-09-06 | 12.447 |
| 2024-09-20 | 4.636 |
| 2024-10-26 | 23.514 |
| 2024-11-17 | 2.479 |
| 2024-12-16 | 5.836 |

The other 22 uniquely recovered days are 0.0 MCM/day.

## Remaining 11

The unresolved dates are:

- 2024-04-01
- 2024-04-02
- 2024-04-09
- 2024-04-11
- 2024-05-04
- 2024-11-30
- 2025-02-19
- 2025-02-20
- 2025-03-01
- 2025-03-17
- 2025-03-18

They remain unresolved for three reasons:

- negative/corrected cumulative increments: 2024-04-02, 2024-04-09,
  2024-04-11, 2024-05-04;
- missing month-boundary/cumulative anchors: 2024-04-01, 2024-11-30,
  2025-03-01;
- two unknown days share only one aggregate cumulative increment:
  2025-02-19 + 2025-02-20 and 2025-03-17 + 2025-03-18.

## Scientific boundary

This audit does **not** change the strict Full-PyPSA v1.4 gate. The 28 values
are not relabelled as directly observed daily inflow.

They are suitable for a separately labelled source-derived sensitivity, and
they sharply reduce the unresolved evidence problem from 39 to 11 dates. The
next work should focus only on those 11 dates rather than reacquiring the full
year.
