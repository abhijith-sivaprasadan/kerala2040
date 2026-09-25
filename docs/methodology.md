# Methodology contract

## Modelling hierarchy

```text
Official data + weather + finance + spatial layers
                  |
                  v
        Historical validation layer
                  |
       +----------+-----------+
       |                      |
       v                      v
Demand/RE forecasting     Hydro/climate
       |                      |
       +----------+-----------+
                  v
             PyPSA/HiGHS
                  |
        capacity + dispatch
                  |
        +---------+----------+
        |                    |
        v                    v
   pandapower         QGIS/ecology
        |                    |
        +---------+----------+
                  v
          finance/circularity
                  |
                  v
        scenario/Pareto outputs
```

## Calibration before prediction

The historical model must first reproduce official annual demand, internal generation, imports and peak demand within declared tolerances. A future scenario is not accepted merely because the optimiser solves.

## Core objective family

The project should not collapse everything into one hidden weighted score. Report Pareto trade-offs between at least:

- total system cost;
- structural imports;
- reliability/unserved energy;
- Kerala public fiscal exposure;
- ecological impact;
- lifecycle emissions;
- circular-resource value.

## Structural import metrics

Report both annual import energy share and peak-hour import dependence. Imports remain allowed because strategic interconnection is beneficial; the research target is reduced forced dependence, not autarky.

## Ecology

Legally unavailable/protected areas are hard exclusions. Other environmental burdens can be represented as constraints or explicit penalties, with assumptions visible and sensitivity-tested.

## Circularity

Every waste-to-value route needs a mass balance, composition/hazard evidence, a technically valid recovery route, market assumptions and avoided-disposal accounting. Hazardous/radioactive residues are not presumed reusable.

## Uncertainty

Separate:

- observed data uncertainty;
- forecast uncertainty;
- technology-cost uncertainty;
- climate/hydrology uncertainty;
- policy/finance eligibility uncertainty;
- model structural uncertainty.

Do not present a single 2040 number where a range or scenario family is more defensible.
## Step 9 cross-solver implementation verification · 25 September 2026

The bounded daily balancing formulation has now been reproduced independently in PyPSA/HiGHS and compared against the Step 8 SciPy/HiGHS reference over all 354 admitted FY2024–25 SLDC days, three synthetic quarter-hour demand shapes and three balancing cases. All **3,186** PyPSA LP solves were optimal. The maximum absolute daily unserved/surplus difference was **1.2732925824820995e-10 MWh**, versus the predeclared **0.001 MWh** tolerance. See [the executable Step 9 record](../research/step9_pypsa/README.md) and [machine-readable verification summary](../research/step9_pypsa/verification_summary.json).

This closes an **implementation-equivalence** gate only. It demonstrates that the independent PyPSA formulation reproduces the stated SciPy balancing problem to floating-point precision. It does not turn synthetic quarter-hour demand shapes into measured telemetry, validate the assumed hydro/import flexibility caps, calibrate Kerala's physical grid, or establish a least-cost 2040 build-out. The next independent modelling benchmark is an OSeMOSYS capacity-expansion formulation; empirical interval-data and physical-constraint gates remain separate.

