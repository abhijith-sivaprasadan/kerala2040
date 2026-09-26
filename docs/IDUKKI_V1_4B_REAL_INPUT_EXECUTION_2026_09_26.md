# Real private-source execution of the v1.4b input builder

The v1.4b inflow builder has now been executed against the exact Phase-4
private `reservoir_rows.csv`, SHA-256:

`b7d4439135edbe02d9e577892e090aafaf92f58606cdc04ee9b6d39e608036c9`

Only aggregate QA is committed. The reconstructed daily scenario CSVs remain
private.

## Result

The real source reproduces the v1.4b design assumptions exactly:

- 325 directly reported pilot-day inflows;
- 28 accepted blank inflow cells normalized to zero for sensitivity only;
- 11 rejected source rows;
- 10 rejected dates uniquely recovered by adjacent cumulative conservation;
- those ten dates contribute 64.656 MCM in aggregate;
- only **30 November 2024** remains source-unconstrained.

Archive-wide blank-field evidence is also reproduced:

- 153 direct blank/cumulative pairs;
- 101 zeroish within 0.0011 MCM;
- 52 negative source corrections;
- zero materially positive increments above tolerance.

## Five 30-November scenarios

| Scenario | 30-Nov inflow (MCM) | Pilot total (MCM) |
|---|---:|---:|
| zero lower | 0.0000 | 2525.9250 |
| November median | 3.5660 | 2529.4910 |
| November p95 | 9.5574 | 2535.4824 |
| November observed max | 11.6230 | 2537.5480 |
| pilot-max stress | 74.0380 | 2599.9630 |

The ordinary seasonal bracket from zero through November observed maximum
changes annual-pilot inflow by only 11.623 MCM. The pilot-max case is a
deliberately extreme stress.

## Execution boundary

This is a **real execution of the private input builder**, not the 60-case
PyPSA matrix. The current local runtime lacks PyPSA/Linopy/HiGHS and cannot
install them because package-network access is unavailable. The public
60-case runner remains ready and the private daily scenarios can be regenerated
from the source when run in an environment containing those dependencies.

Strict v1.4 remains fail-closed and is not promoted by this result.
