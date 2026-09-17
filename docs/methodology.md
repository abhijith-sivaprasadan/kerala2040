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
