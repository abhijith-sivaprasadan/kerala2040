# Historical demand-shape / intraday-hydro screening: a bounded negative and positive result

**Experiment:** `historic_proxy_seven_day_demand_chronology_sensitivity_v0_1`  
**Computed:** 23 October 2026, [GitHub Actions verification](https://github.com/abhijith-sivaprasadan/kerala2040/actions/runs/39949432682).  
**Reproduce:** `python examples/hydro_chronology_sensitivity.py --output results/examples/hydro_chronology_sensitivity.json`  
**Status:** Historical **reconstructed-hour** sensitivity only; **not** measured-hour validation, a calibrated uncertainty distribution, or a rerun of the published FY2030–31 375.03→11.75 GWh result.

## Research question

How sensitive is the apparent adequacy benefit of **redispatching the same daily hydro MWh** to simple perturbations of the unmeasured within-day demand shape, at different fixed import ceilings?

### Inputs, selection and controls

- Input is the openly released FY2024–25 hourly **proxy** (`public/hourly-load-proxy.json`), not actual hourly telemetry, together with SLDC daily source balance (`data/external/sldc_fy2024_25/daily_balance.csv`) and its source QA report.
- Seven-day observation-only window selected **before modelling**: take the consecutive seven dates with maximum summed *source-observed* daily consumption, excluding any missing SLDC day; break ties by earliest date. The selected window is **28 April–4 May 2024**, with **780.9262 MU** of observed daily demand in total.
- Candidate daily shapes: original proxy; rotate each 24-hour shape two hours earlier or later; multiply deviations from each day's mean by 0.9 or 1.1. Every perturbation retains exactly that source-day MWh; the variants are controlled arithmetic sensitivities, **not percentiles of an empirically estimated uncertainty distribution**.
- Fixed per-day nonhydro generation is the source day's internal minus hydro energy divided by 24, rather than observed hourly plant operation.
- Every day has the same **source-reported hydro MWh** in both cases. Fixed hydro must produce its daily average every hour; flexible hydro is idealised and constrained only by a **2,284.42 MW aggregate power ceiling** (dated March 2026 source reference, not an observed FY2024–25 state) and exact daily MWh.
- Dispatchable import is capped at **4,455 MW** or a **2,673 MW (60%) stress**. These are model sensitivities based on the separately dated ATC planning reference, not measurements of hourly available imports.
- Single-node SciPy/HiGHS optimisation minimizes modelled unserved load. Explicit spill absorbs oversupply. There is **no reservoir state, water routing, hydro ramp, hourly nonhydro variation, hydro outage, transmission security, market model or storage**.

## Source-derived model results

**MWh of modelled unserved energy over the selected seven days.** The shift variants repeat the unshifted result to solver precision, so the following table presents all distinguishable outcomes:

| Import ceiling | Demand shape | Fixed daily-average hydro | Optimistic intra-day hydro | Modelled reduction |
| --- | --- | ---: | ---: | ---: |
| 4,455 MW | Baseline proxy | 6,017.43 | 0.00 | 6,017.43 |
| 4,455 MW | Mean-deviation scaled ×0.9 | 3,598.73 | 0.00 | 3,598.73 |
| 4,455 MW | Mean-deviation scaled ×1.1 | 8,703.60 | 0.00 | 8,703.60 |
| 2,673 MW | Baseline and all four variants | 179,485.30 | 179,485.30 | 0.00 |

Full ten-case numerical output (including both ±2h shifts) is generated as a **source-hashed CI artifact** by [the research-examples workflow](../.github/workflows/research-examples.yml). The verified job checks every per-hour balance, preserved daily hydro MWh, non-increase of unserved energy under relaxed hydro timing, and preservation of the explicit proxy classification.

### Interpretation: two genuine findings and one important blind spot

1. **At the higher import limit**, this selected historical week can be screened as sufficient under ideal within-day hydro redistribution, despite a modest shortage in the fixed daily-average replay. Sharpening the hourly demand swing increases fixed-hydro shortage; flattening it decreases shortage. This is an *optimistic mathematical timing bound*, not evidence of feasible reservoir control.
2. **At the stressed import limit**, total weekly supply plus fixed daily hydro MWh is insufficient under this model. Reallocation of hydro cannot compensate for the supply deficit. The **identical 179.4853 GWh** in every case reflects an energy-deficit-dominated bound, not proof about how Kerala operated.
3. **Clock-time shifts are exactly invariant** in this experiment. Both imports and nonhydro sources are temporally flat within a day and flexible hydro can be moved arbitrarily. Therefore rotating the whole demand profile by ±2h leaves the linear programme unchanged up to a permutation of hours. **The model is structurally unable to infer realistic clock-hour sensitivity** from these scenarios. This is a useful *negative* result: any future claims about evening peak timing require hourly source/dispatch availability, hydro operation constraints and stronger validation evidence.

The particular numerical range above must **not** be extrapolated to annual reliability, future climates or FY2030–31, nor described as a confidence interval. It also does not substantiate the 96.87% hydro sensitivity in the separate main modelling programme: that case uses a different year, demand target, renewable supply and capacity-expansion assumptions.

## Reproduction and independent check

```bash
python -m pip install -e ".[dev]"
python -m pytest -q tests/test_hydro_chronology_uncertainty.py
python examples/hydro_chronology_sensitivity.py --output results/examples/hydro_chronology_sensitivity.json
```

An independent analytic linear-programme reference applies in this simple single-node formulation. At each hour let `d_t=max(0, load_t - nonhydro_t - import_cap)`, `H` be fixed daily hydro energy (MWh) and `C` hydro peak MW, with 1h steps:

- Fixed hydro minimum shortage: `sum(max(0, d_t - H/24))`.
- Fully flexible daily hydro minimum shortage (with spill permitted): `max(sum(d_t)-H, sum(max(0, d_t-C)), 0)`.

The tests include an independent check of the optimisation result against these formulas for small synthetic days. This **verifies this optimisation formulation**, not the physical validity of reconstructed hourly input.

## Highest-value next validation work

Measured Kerala 15-minute/hourly load, time-resolved hydro/nonhydro dispatch, exchange by interval and station constraints would be more valuable than further perturbing reconstructed curves. If no such records become available, use physically constrained hydro profiles and externally supported renewable/weather availability profiles rather than declaring these five arithmetic shapes representative of forecast uncertainty.

**Original scientific context:** [Hydro flexibility and annual scenarios](FULL_PYPSA_SCENARIO_PROGRAMME.md), [source evidence](evidence_register.md), [reproducibility guide](REPRODUCE_AND_EXTEND.md).


**Subsequent method stress test:** [v0.2 — hypothetical time-varying import capacity and 168-hour hydro ramp](HYDRO_SUPPLY_TIMING_V0_2.md). This follow-up probes the mathematical invariance documented above; it does not retroactively validate operational shortage estimates.
