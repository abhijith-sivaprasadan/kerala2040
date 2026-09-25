# Full Kerala2040 PyPSA scenario programme

**Status: implementation started — scenario specifications are not yet optimisation results.**

This workstream turns the public S0–S5 scenario specifications into one common,
auditable PyPSA capacity-expansion and chronological-dispatch model. Step 9 verified
that the PyPSA formulation plumbing reproduces the bounded SciPy balancing problem;
this work is the larger planning model.

## Scenario matrix

| Code | Scenario | Core test |
|---|---|---|
| S0 | Business As Usual | Structural import dependence, historical-like hydro, low flexibility |
| S1 | Maximum Local Generation | Aggressive local generation/storage expansion before stricter ecological constraints |
| S2 | Solar Storage | Expandable solar, BESS and pumped storage with hydro balancing |
| S3 | Integrated Sovereignty | Diversified RE, storage, strategic hydro, flexible demand, EV flexibility and trade |
| S4 | Ecological Sovereignty | S3 under strict spatial/ecological carrying-capacity constraints |
| S5 | Fiscal Conservative | Integrated portfolio under an explicit Kerala public-capital exposure constraint |

Every scenario remains an **UNSOLVED SPECIFICATION** until the numerical inputs
required by its dimensions are admitted and PyPSA has produced a reproducible result.

## Planned model years and outputs

The common runner will support 2030, 2035 and 2040 demand cases and report, without
collapsing them into a hidden score: installed capacity, generation, storage power and
energy, imports, peak import dependence, curtailment, unserved energy, system cost,
hydro use, emissions, ecological constraints and public fiscal exposure.

Stress/sensitivity dimensions already declared in the repository are dry hydro,
cloudy/low solar, heat wave, EV surge, high battery cost, import restriction,
high import price and extreme monsoon/flood.

## Admission rule

The engine has two evidence states:

1. **research/assumption runs** may use explicitly labelled published external
   benchmarks or declared sensitivity assumptions;
2. **validated runs** fail closed when mandatory physical/economic inputs remain
   unresolved.

No null in `configs/techno_economics.yaml`, missing GIS capacity ceiling, unverified
interstate transfer rating or unresolved hydro/storage constraint may be silently
replaced by an invented Kerala value.

## Implementation order

1. canonical scenario compiler: S0–S5 + stress dimensions;
2. common 2030/2035/2040 demand-case interface;
3. technology/cost input admission and annualisation;
4. extendable solar/wind/BESS plus fixed/extendable hydro, PSP and trade representation;
5. flexible-demand/EV/cooling/industry interfaces;
6. capacity-expansion solve and chronological dispatch;
7. scenario KPI/result schema and website integration;
8. sensitivity matrix and cross-scenario attribution;
9. independent OSeMOSYS benchmark.

Until steps 1–7 pass, the website must continue to call these **UNSOLVED
SPECIFICATIONS**, including the newly exposed S5.
