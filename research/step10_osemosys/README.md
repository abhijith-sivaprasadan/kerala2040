# Step 10 — independent OSeMOSYS capacity-expansion benchmark

**Status: implementation prepared; numerical cross-framework gate closes only after CI execution.**

Step 9 showed that PyPSA/HiGHS reproduces the bounded Step 8 daily balancing LP to
floating-point precision. Step 10 is deliberately different: it independently maps the
existing **Full-PyPSA v0.8 2030 proxy capacity-expansion counterfactual** into OSeMOSYS and
checks the resulting shortage floor, capacity build and minimum-import dispatch.

This is not a new 2030/2040 scenario and does not promote v0.8 into a validated capacity plan.
It inherits the same proxy demand chronology, five-point ERA5 renewable profiles, ATC
sensitivities, candidate capacity envelopes, frozen historical hydro/nonhydro replay and
unresolved landed import economics.

## Independent implementation

The benchmark uses TransitionZero's \`tz-osemosys\`, pinned to Git commit
\`2c95ef395858ad530fb38a0dfb5c142283964d24\`, with HiGHS. The model uses canonical
OSeMOSYS commodity, capacity-factor, capacity-investment, activity and storage equations.

Four explicit bridge constraints are added only to reproduce the exact v0.8 BESS definition:

1. storage energy capacity = four hours × BESS AC power capacity;
2. AC-side charging is capped at BESS power after charging efficiency;
3. AC-side discharging is capped at BESS power after discharge efficiency;
4. the storage chronology is cyclic, matching the v0.8 first/last-hour state equation.

Everything else remains in the OSeMOSYS formulation. If the independent model does not match
v0.8 inside the predeclared tolerances, the run is labelled \`STRUCTURAL_DIFFERENCE\`; the
workflow must not tune the model after seeing a result merely to obtain a pass.

## Objective mapping

The v0.8 lexicographic sequence is reproduced as three OSeMOSYS solves:

1. **Adequacy:** unserved electricity has unit variable cost; candidate capex is zero.
2. **Minimum build:** unserved annual activity is capped at the stage-1 optimum plus the
   existing tolerance; solar/wind/BESS capacity use the same annualized investment coefficients.
3. **Minimum imports:** stage-2 capacities are fixed, the shortage cap is retained, and imports
   receive unit variable cost for reporting dispatch.

A one-year operating life is used for candidate investment variables. With the model's positive
social discount rate, first-year discount factor and one-year CRF×PV-annuity reduce exactly to
one, so the supplied annualized v0.8 cost coefficient remains the objective coefficient.

## Acceptance

The machine-readable contract is \`configs/osemosys_capacity_benchmark_v0_1.yaml\`:

- stage-1/stage-2 unserved energy: absolute difference ≤ **0.01 MWh**;
- solar/wind/BESS power capacity: absolute difference ≤ **0.01 MW**;
- stage-3 import energy: absolute difference ≤ **0.1 MWh**.

The CI test suite also runs a synthetic 24-hour case directly against the SciPy/HiGHS v0.8
solver before touching the real proxy input chain.

## Reproduce

Install the project and the pinned independent framework:

\`\`\`bash
python -m pip install -e ".[dev,era5]"
python -m pip install \
  "tz-osemosys @ git+https://github.com/transition-zero/tz-osemosys.git@2c95ef395858ad530fb38a0dfb5c142283964d24"
\`\`\`

After rebuilding the verified v0.6 ERA5 screening profile, run a one-week sentinel case:

\`\`\`bash
python research/step10_osemosys/run_osemosys_benchmark.py \
  --hours 168 \
  --case reference_FY2030_31,atc_snapshot_reference,high,low
\`\`\`

A full-year benchmark uses \`--hours 8760\`. That is a heavier independent solver run and should
be executed only after the sentinel and synthetic equivalence gates pass.

## Interpretation boundary

A PASS means the two independently implemented optimisation frameworks agree on the stated
proxy problem. It does **not** validate Kerala's physical 2030 system, future demand, buildable
renewable MW, internal transmission, hydro operations, storage siting, import prices, outages,
project finance, environmental approval or a recommended capacity mix.
