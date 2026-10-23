# When does clock-time alignment matter? Historical Kerala demand/supply screening v0.2

**Date:** 23 October 2026  
**Reproduced:** [passing public example and source-artifact run](https://github.com/abhijith-sivaprasadan/kerala2040/actions/runs/39951099440)  
**Executable:** [`examples/hydro_supply_timing_v0_2.py`](../examples/hydro_supply_timing_v0_2.py)  
**Model:** [`src/kerala2040/hydro_chronology_v0_2.py`](../src/kerala2040/hydro_chronology_v0_2.py)

## Research purpose

An earlier historical screening exercise produced **exactly identical** shortage estimates when its reconstructed hourly load was shifted two hours within each day. This was a property of the *model formulation*, not evidence that clock time is unimportant for power-system stress: imports and fixed nonhydro sources were constant every hour, and optimistic hydro could move freely across each day.

This follow-up is a **falsification-oriented method test**: intentionally introduce clearly labelled hourly supply asymmetry and a cross-midnight hydro ramp cap, then check if apparent invariance survives. It uses the same highest-seven-day-consumption window selected independently from the **observed daily SLDC records** (28 April–4 May 2024).

**All hourly demand remains reconstructed, not observed.** We have not acquired hourly dispatch, ramping, reservoir or import-availability telemetry. This is not a calibrated uncertainty ensemble, a causal study, or an event-attribution model.

## Experimental design

- Source-observed seven daily electricity and hydropower energy totals are preserved exactly. No imputed SLDC day enters the window.
- Five hypothetical within-day demand profiles: existing hourly reconstruction, ±2-hour within-day rotation, and ±10% relative amplification/attenuation of deviations from each day's mean. All preserve daily energy by construction.
- Fixed nonhydro output is replayed at its source-observed **daily average**, not mistaken for measured hourly plant operation.
- Two import-capacity envelopes: **4,455 MW** (dated external CEA planning reference) and **3,564 MW** (80%-of-reference stress). Each has either a uniform hourly limit or a purely *illustrative* 20% derating **18:00–22:00 India local time**. There is **no evidence this four-hour import restriction occurred in Kerala**.
- The fixed-hydro comparator supplies each day's hydro MWh at a constant 24-hour average. A seven-day 168-hour sparse linear programme instead reallocates the exact same MWh, with installed power ceiling **2,284.42 MW** from a separately dated March 2026 record.
- The flexible case runs without ramp constraints and with a **hypothetical** |hydro(t)−hydro(t−1)| ≤ **400 MW/h**, enforced across every hour including midnight. This number is *not* a measured Kerala fleet ramp. The selected source day's flat-hydro reference is feasible within it.
- Objective minimizes unserved energy. Explicit spill is allowed. No reservoir head/storage, cascade, minimum flow, plant commitment, network, solar hourly constraints, storage dispatch, cost or hydro interday MWh transfer is modelled.

This gives **40** tests (5 demand shapes × 2 import ceilings × 2 import availability schedules × 2 hydro ramp modes), with source SHA-256 digests and per-run conservation residuals saved by CI.

## Results (selected three demand shapes)

**Modelled unserved energy in GWh over seven days**, rounded from the generated GitHub Actions source-backed output.

| Import ceiling / stylised hourly availability | Hourly demand shape | Fixed average hydro | Free intraday hydro | Hydro with 400 MW/h ramp |
| --- | --- | ---: | ---: | ---: |
| 4,455 MW; **uniform** | Baseline / ±2-hour shift | 6.017 | 0.000 | 0.000 |
| 4,455 MW; 18–22 derated | Baseline | 10.580 | 0.000 | 0.000 |
| 4,455 MW; 18–22 derated | Shift 2h earlier | 20.713 | 0.000 | 0.000 |
| 4,455 MW; 18–22 derated | Shift 2h later | 18.091 | 0.000 | 0.000 |
| 3,564 MW; **uniform** | Baseline / ±2-hour shift | 58.630 | 31.624 | 31.624 |
| 3,564 MW; 18–22 derated | Baseline | 77.752 | 49.756 | 49.756 |
| 3,564 MW; 18–22 derated | Shift 2h earlier | 78.283 | 49.756 | **49.923** |
| 3,564 MW; 18–22 derated | Shift 2h later | 78.058 | 49.756 | 49.756 |

The latter 400-MW/h result increases constrained shortage **by ~0.168 GWh** relative to unconstrained hydro in that specific modelled combination. The other listed cases do not show an effect of the proposed hydro ramp at reporting precision. Daily hydro energy conservation, hourly nodal balance, and ramp constraints passed in the 40 test scenarios. The remaining flatten/amplify results are in the machine-readable workflow artifact and logs.

## What the experiment actually establishes

1. **Uniform temporal availability produces exact permutation invariance.** This is a mathematical control, independent of any empirical claim about demand clock time.
2. **Nonuniform supply availability makes timing identifiable in the formulation.** The fixed-hydro difference between 10.580 and 20.713 GWh under two alternative within-day rotations and a stylised evening import reduction is an illustration of the *conditional modelling mechanism*, **not** an estimate of real Kerala shortage.
3. **Unconstrained hydro can hide temporal differences.** In this window and envelope, flexible hydro often removes the differences completely. Imposing just one hypothetical 400-MW/h ramp causes a small but real difference in one case.
4. **Even this test still lacks realistic supply chronology.** Other-than-hydro output is flat within days, the import event is hypothetical, and hydro flexibility remains highly optimistic without reservoir/cascade and station-level operating constraints. The 2-hour shifts and ±10% profiles are scenario design choices, not uncertainty intervals.

**This does not validate the separate FY2030–31 result in the main planning model** (the reported 375.03→11.75 GWh reference case). The latter differs in demand, renewable profiles, candidate investments and the modelling assumptions.

## Reproduce and scrutinise

```bash
python -m pip install -e ".[dev]"
python -m pytest -q tests/test_hydro_chronology_uncertainty.py tests/test_hydro_chronology_v0_2.py
python examples/hydro_supply_timing_v0_2.py --output results/examples/hydro_supply_timing_v0_2.json
```

The independent example workflow checks (i) source completeness and preservation of daily MWh, (ii) exact 24-hour demand transforms, (iii) nodal balance, (iv) daily hydro MWh equalities and 168-hour hydro ramps, (v) solver comparisons against analytic un-ramped bounds, and (vi) restoration of shift invariance when the hourly source profile is uniform.

**Priority for improved external evidence:** actual 15-minute/hourly Kerala demand, source time-resolved nonhydro and import limits, plus hydro plant constraints and reservoir data. Those would allow external validation rather than more manipulation of the current unmeasured hourly curves.
