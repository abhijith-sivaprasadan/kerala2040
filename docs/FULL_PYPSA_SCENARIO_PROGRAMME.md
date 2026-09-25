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

## Implementation checkpoint 1 · scenario compiler

The first executable layer is now implemented in `src/kerala2040/scenario_compiler.py`.
It compiles all **6 scenarios × 3 model years = 18 base structural cases** and can add
each declared stress test without inventing its numerical severity. Every case reports
the exact evidence/input keys it requires and remains `UNSOLVED_SPECIFICATION` while
any requirement is missing. Supplying every requirement changes the structural state only
to `READY_TO_BUILD_NETWORK`; it still does not claim an optimisation result.

Run:

```bash
python scripts/compile_full_pypsa_scenarios.py
pytest -q tests/test_scenario_compiler.py
```

CI validates the same matrix and uploads it as a development artifact labelled
`NOT-optimised`. The next implementation checkpoint is the numerical input registry:
map admitted demand, technology-cost, resource, hydro, trade, storage, flexibility,
ecology, reliability and fiscal datasets into these requirement keys with explicit
source/assumption classifications.
## Implementation checkpoint 2 · data acquisition and evidence registry

The first major input-acquisition sprint is complete. It added a dated [Kerala energy asset/project register](../data/evidence/assets/kerala_energy_asset_register_2026_09_25.json), the official [generation Resource Adequacy benchmark](../data/evidence/demand/kerala_resource_adequacy_2025_2035_36_2026_09_25.json), a source-bounded [CEA transmission Resource Adequacy register](../data/evidence/grid/kerala_transmission_resource_adequacy_2034_35_2026_09_25.json), bounded [September-2026 system-stress evidence](../data/evidence/system/kerala_sep2026_power_stress_2026_09_25.json), and the [full-PyPSA input admission registry](../configs/full_pypsa_input_registry.yaml).

The acquisition resolved several previously ambiguous claims: CEA's 31-March-2026 **3,221.30 MW** installed-capacity number deliberately excludes **1,912.33 MW** of sub-1-MW solar reported separately; MNRE later reports **2,259.50 MW rooftop solar** at 31-August-2026; CEA's transmission plan uses **800 MW BESS by 2029-30** as a planning assumption rather than current installed storage; and conventional Idukki Extension hydro is distinct from THDCIL's Idukki/Pallivasal PSP PFRs and CEA's separate 2034-35 PSP planning portfolio.

The next checkpoint is therefore **base-year and input-selection reconciliation**. No capacity-expansion solve should begin by silently splicing the FY2024-25 Economic Review, March-2026 CEA and August-2026 MNRE boundaries. The model must choose a declared base date, reconcile every current asset into that boundary, preserve alternative official demand forecasts as named sensitivities, and only then map costs, chronology, reliability and physical constraints into PyPSA.

## Implementation checkpoint 3 · canonical March-2026 base system

The full model now has a declared **31 March 2026** structural base in
`configs/base_system_2026_03_31.yaml`. CEA's main installed-capacity population
reconciles to **3,221.30 MW**: 536.54 MW thermal, 2,284.42 MW hydro and 400.34 MW
wind/solar at or above 1 MW. The same source reports **1,912.33 MW of solar below
1 MW separately**, giving a purely arithmetic physical-capacity population of
**5,133.63 MW** when that separately reported solar is included.

This is a boundary reconciliation, not a dispatch-ready fleet. Existing sub-1-MW
solar is treated as **embedded in net-grid demand** by default; it may not also be
injected as a PyPSA generator until a gross-demand reconstruction with compatible
behind-the-meter generation is available. The MNRE 31-August-2026 renewable snapshot
is retained as an explicit later overlay and cannot silently mutate the March base.

The base validator and tests enforce ownership/technology arithmetic, keep unverified
operational BESS/PSP values null, prevent the August overlay from being silently
applied, and reject an explicit rooftop generator while the declared load boundary is
net-grid demand.

The scenario compiler now requires the reconciled base system, existing generation
and storage fleet evidence, demand chronology, renewable temporal profiles,
technology costs, transfer/price inputs and reliability definition for **every**
S0-S5 case. Fixed-existing technologies therefore no longer bypass their underlying
fleet evidence. S0-S5 public/config vocabulary is also synchronized, including the
S2 `legal_minimum` ecological rule and the common 2030/2035/2040 model years.

