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



## Implementation checkpoint 4 · research input selection v0.2 and chronological proxy adequacy

The next admission layer is now explicit in
`configs/research_input_selection_v0_2.yaml`. It does **not** make the full model
validated or expansion-ready. It selects source families and a bounded research
screen so that chronology can be exercised without turning missing evidence into
assumed facts.

### Solar identity crosswalk

The March-2026 CEA >=1 MW solar ownership buckets remain canonical:
**22.715 MW state + 214.10 MW private + 92 MW central = 328.815 MW**.
The new
`data/evidence/assets/kerala_solar_ge1_identity_crosswalk_2026_03_31.json`
records what can actually be named.

KSEBL's 2021-22 station table gives a firm **14.50 MW** seed of individually named
state solar plants at or above 1 MW. Later KSEBL/INKEL evidence identifies
Brahmapuram, Nenmara, Mananthavady and another Kanjikode listing. If every later
listing were treated as distinct, the candidate arithmetic would be **22.75 MW**,
only 0.035 MW above CEA's 22.715 MW state bucket. That near-match is deliberately
**not patched**: MWp-versus-AC treatment, rounding and possible Kanjikode overlap
must be resolved first.

For private solar, KSEBL's FY2024-25 report provides a strong aggregate bridge of
**204 MW IPP solar** against CEA's later **214.10 MW** private >=1 MW solar bucket,
but the remaining 10.10 MW cannot be filled by cherry-picking captive/prosumer rows
because KSEBL and CEA classification boundaries have not been proven identical.
The 92 MW NTPC Kayamkulam floating-solar identity is already exact.

The alternate 31-March-2026 MNRE renewable boundary explored in superseded PR #72
is preserved in the crosswalk as an alternate accounting view; it does not replace
the CEA transmission-resource-adequacy base.

### Named demand cases

v0.2 selects, without averaging them:

- **lower:** CSTEP 2024 published pathway through FY2040;
- **reference:** CEA/KSERC generation Resource Adequacy trajectory through FY2035-36;
- **higher:** CEA transmission-RA/KSEBL load-flow case, currently **peak-only** in
  the admitted evidence.

The higher case therefore remains incomplete for annual-energy modelling. No hidden
energy series or post-source-horizon extrapolation is permitted.

### Reliability and interstate-transfer research bounds

KSERC's RA review direction uses **LOLP and NENS** as reliability metrics. For a
research benchmark, v0.2 records the **0.2% LOLP / 0.05% NENS** thresholds used in
a CEA state Resource Adequacy study, but labels them explicitly as a
**CEA state-RA benchmark, not a Kerala statutory threshold**.

The first deterministic screen cannot estimate LOLP. It reports unserved MWh,
unserved-energy percentage, hours with unserved load and maximum unserved MW.
Probabilistic adequacy remains blocked until forced-outage distributions and
stochastic demand/renewable sampling are admitted.

The CEA transmission study's dated **4,575 MW TTC / 4,455 MW ATC** snapshot is used
only as a screening bound. v0.2 adds explicit 80% and 60% ATC haircut sensitivities
(3,564 MW and 2,673 MW) plus a 6,500 MW replay-control bound. None is described as
a historical FY2024-25 hourly transfer series or an annual guarantee.

### First chronological PyPSA research screen

The repository already had a provenance-gated chronology engine in
`src/kerala2040/chronological_screen.py`. v0.2 reuses it rather than creating a
second model. The screen uses:

- the 8,760-hour FY2024-25 **reconstructed** load shape;
- 354 observed SLDC daily source-energy balances;
- model-only interpolation on the 11 dates without an SLDC daily report;
- observed daily hydro and residual internal generation replayed as flat daily
  averages;
- explicit import-cap sensitivities and an unserved-energy slack;
- no economic import price, no capacity expansion and no new storage/solar.

Run the full suite with:

```bash
python scripts/run_full_pypsa_proxy_adequacy_v0_2.py --acknowledge-proxy --hours 8760
```

The output is a **proxy adequacy sensitivity**, not measured hourly validation,
economic dispatch, probabilistic RA compliance, or an S0-S5 investment result.


## Implementation checkpoint 5 · intraday hydro-flexibility bracket v0.3

The first 8,760-hour v0.2 screen exposed a material modelling uncertainty: the
historical SLDC hydro evidence is daily energy, but v0.2 replayed that energy as a
flat 24-hour average. That is intentionally conservative about intraday flexibility
and is not how reservoir hydro is normally used for peak support.

v0.3 therefore adds a second, deliberately optimistic bound while preserving the
same source energy. For every modelled day it enforces:

```text
sum(hourly hydro MW × 1 h) = that day's SLDC hydro MWh
0 <= hourly aggregate hydro <= installed hydro MW
```

The optimizer may move the day's hydro energy among the 24 hours to reduce imports
and unserved load. It **cannot** move water across days. The flat replay and this
free intraday redispatch form a sensitivity bracket around hydro timing.

This is not a reservoir or cascade model. The upper bound does not yet include
station outages, reservoir level-volume curves, river/cascade travel times,
environmental releases, head-dependent efficiency, minimum output, ramp limits or
internal Kerala transmission constraints. A reduction in proxy shortage therefore
means “the result is sensitive to hydro timing,” not “Kerala can definitely dispatch
hydro this way.”

Run the full comparison with:

```bash
python scripts/run_full_pypsa_hydro_flexibility_v0_3.py \
  --acknowledge-proxy \
  --hours 8760
```

Capacity expansion remains blocked. The purpose of this checkpoint is to determine
whether the v0.2 ATC shortage signal survives a much more favourable treatment of
intraday hydro before we invest effort in expansion scenarios.
