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


## Implementation checkpoint 6 · future-demand adequacy counterfactual v0.4

After the v0.3 hydro-flexibility bracket, the programme now adds a first
forward-looking chronological stress screen in
`src/kerala2040/full_pypsa_future_adequacy.py`.

The runner preserves the ordering of the FY2024-25 reconstructed 8,760-hour load
shape and uses an affine transformation to hit each published future annual-energy
and peak-demand anchor exactly. It currently admits five source-bounded cases:

- CSTEP lower: FY2030, FY2035 and FY2040;
- CEA/KSERC generation-RA reference: FY2030-31 and FY2034-35.

The CEA transmission-RA higher case remains excluded because the admitted evidence
contains peak anchors but no matching annual-energy series. No energy trajectory is
invented for it.

For each demand case, v0.4 deliberately freezes FY2024-25 daily-average internal
generation and tests the 4,455 MW dated ATC snapshot plus 80% and 60% transfer
haircuts. This is a harsh **no-expansion counterfactual**: it asks how much pressure
appears if demand follows a published future anchor while today's source-energy
replay does not grow.

It is not a future hourly demand forecast, future generation forecast, future ATC
commitment, economic dispatch or capacity recommendation.

Run:

```bash
python scripts/run_full_pypsa_future_adequacy_v0_4.py \
  --acknowledge-counterfactual \
  --hours 8760
```

The result reports imports, unserved energy, affected hours, maximum unserved MW and
the exact demand-morph parameters for every demand × transfer case. The next gate is
cost/finance harmonisation and candidate renewable/storage physics before any
least-cost capacity-expansion solve is admitted.


## Implementation checkpoint 7 · 2030 research cost/finance harmonisation v0.5

The programme now has a bounded economic-assumption layer in
`configs/full_pypsa_cost_finance_v0_5.yaml`. Its purpose is to remove hidden
price-basis and annualisation ambiguity before any investment solve is attempted;
it does **not** assert that national CEA/CERC benchmarks are realised Kerala project
costs.

v0.5 keeps all admitted investment values on a **real 2021-22 INR** basis. For
annualisation it uses the current CERC generic-RE post-tax WACC-equivalent discount
rate of **9.08%** as a transparent research benchmark, together with the regulatory
70:30 debt/equity structure. The package admits only the source-bounded 2030
candidate economics:

- solar PV: **₹41,000/kW**, 1% fixed O&M, 25-year life;
- onshore wind: **₹60,000/kW**, 1% fixed O&M, 25-year life;
- four-hour BESS: **₹47,200-82,200/kW** published CEA cost bracket, 1% fixed O&M,
  14-year life and **88% round-trip efficiency**.

No midpoint is invented for the BESS bracket. The PyPSA charge/discharge efficiency
split is symmetric, `sqrt(0.88)` on each side, so the product remains exactly the
source round-trip efficiency.

Pumped storage stays deliberately blocked for expansion: the CEA capex range is
project-specific and cannot substitute for Kerala reservoir-pair, hydraulic-MWh and
site-cost evidence. The same fail-closed rule applies to 2035 and 2040 costs: v0.5
does not extrapolate beyond the admitted CEA planning horizon.

Validate the layer with:

```bash
python scripts/validate_full_pypsa_cost_finance_v0_5.py
pytest -q tests/test_full_pypsa_cost_finance_v0_5.py
```

This checkpoint makes **2030 cost annualisation and four-hour BESS research physics
available**, but capacity expansion remains disabled. The next gate is candidate
renewable temporal profiles and buildable-capacity bounds, followed by import
economics and the remaining operational constraints needed for a meaningful
least-cost solve.


## Implementation checkpoint 8 · verified ERA5 renewable screening profiles v0.6

The retained FY2024-25 ERA5 source artifacts are now exercised directly inside CI
rather than existing only as source-QA evidence. The v0.6 workflow downloads the
same **20 location-quarter artifacts**, re-runs byte/hash/chronology/unit/grid QA,
and reconstructs **8,760 UTC hours at each of five representative locations
(43,800 point-hours)**.

A previously unresolved spatial ambiguity is now explicit. Where an ERA5 request
box contains multiple source cells, v0.6 selects the **nearest returned grid cell to
the representative coordinate**. This matters for Kannur, whose source box is 2x2;
the selected cell is 11.75 N, 75.25 E. No request-box average is silently applied.

The PV proxy reproduces the previously documented five-site sensitivity method:
hourly ERA5 SSRD, PR 0.82, -0.004/K temperature coefficient and a simplified
0.025 K per W/m2 cell-temperature rise. Wind preserves the ERA5 hourly 10 m shape,
applies a 0.14 shear exponent to 150 m, then mean-anchors each point to the public
NIWE nearest-cell long-term 150 m mean before applying the generic 3/12/25 m/s
turbine proxy.

The artifact-backed run produced the following research-screening diagnostics:

| Point | PV proxy kWh/kW-yr | NIWE-anchored wind FLH |
|---|---:|---:|
| Kannur | 1,393.0 | 344.1 |
| Kochi | 1,334.8 | 249.1 |
| Kozhikode | 1,308.5 | 290.3 |
| Palakkad | 1,332.1 | 3,316.5 |
| Thiruvananthapuram | 1,424.5 | 978.4 |

The equal-weight five-point profile has **1,358.6 kWh/kW-year PV** (15.51% proxy
capacity factor) and **11.82% NIWE-anchored wind proxy capacity factor**. The PV
specific yield is about **9.03% below** the GSA long-term statewide median
1,493.5 kWh/kWp/year. This difference is retained rather than calibrated away.

The source-to-profile implementation also reproduces the earlier local proxy results
for the four unchanged single-cell sites to within 0.04 kWh/kW-year for PV and
0.05 full-load hours for wind. Kannur is intentionally not forced to its earlier PV
value because v0.6 corrects the old implicit [0,0] multi-cell selection.

These profiles remain **research screening inputs, not expansion-ready resource
profiles**. Five equal-weight locations are not a statewide capacity-weighted fleet;
the PV transform omits project tilt/inverter/soiling effects; the wind transform is
mean-anchored climatology with a generic turbine curve; annual measured solar
generation cannot validate hourly shape; and no legal/ecological/grid buildable-MW
ceiling has been admitted.

The durable evidence summary is
`data/evidence/weather/era5_renewable_profiles_v0_6_2026_09_25.json`.
Capacity expansion therefore remains disabled. The next gate is now narrower:
derive defensible **buildable renewable capacity bounds and spatial weights**, while
separately pursuing measured hourly generation for profile validation.


## Implementation checkpoint 9 · source-bounded renewable capacity envelope v0.7

v0.7 separates **published research-potential scenarios** from **statutory/site-level
buildable capacity**. The latter remains fail-closed. The former is now explicit
enough to support a tightly labelled statewide proxy expansion sensitivity.

For ground/utility PV, the envelope retains CSTEP 2024's **2,423 MW** usable
ground-mounted scenario as the low/reference case and WRI India's 2025 synthesis of
the DoECC estimate, **6,110 MW**, as a broader high case. The same-date March-2026
MNRE accounting view preserved in the solar crosswalk reports **340.26 MW**
ground-mounted solar. Subtracting that whole category yields conservative new-build
headroom of **2,082.74 MW** in the CSTEP case and **5,769.74 MW** in the broader
case. This is deliberately conservative because MNRE's category may contain
floating/mixed project classifications.

For floating PV, three alternative published scenarios are kept separate:

- **920 MW** CSTEP usable-potential case (10% of 9.2 GW gross);
- **2,220 MW** NISE 2026 20%-surface case;
- **5,730 MW** NISE broader feasible-area case.

The verified 92 MW NTPC Kayamkulam floating plant is subtracted only for additional
headroom, giving **828 / 2,128 / 5,638 MW**. The NISE alternatives are not added
together and are not treated as reservoir/operator permits.

For onshore wind, v0.7 packages:

- **2,311 MW** older NIWE 2019 120 m scenario;
- **2,621 MW** WRI 2025 / NIWE benchmark;
- **2,993 MW** CSTEP 2024 GIS scenario.

Against the canonical March-2026 **71.525 MW** wind decomposition, the corresponding
new-build headroom is **2,239.475 / 2,549.475 / 2,921.475 MW**.

Rooftop PV is intentionally different. August-2026 MNRE evidence already shows
**2,259.5 MW installed**, while the CEA/KSERC RA evidence contains **3,698 MW** of
planned rooftop-DRE additions over FY2025-26 to FY2035-36. These are retained as
deployment/planning evidence, but no numeric technical ceiling is invented: WRI
2025 explicitly notes that more studies are required to determine Kerala's rooftop
potential. Rooftop therefore stays **exogenous**, not an unconstrained PyPSA
investment variable.

The packaged v0.7 low/reference/high cases are statewide total-potential scenarios:

| Case | Ground/utility PV MW | Floating PV MW | Onshore wind MW | Rooftop |
|---|---:|---:|---:|---|
| Low | 2,423 | 920 | 2,311 | exogenous |
| Reference | 2,423 | 2,220 | 2,621 | exogenous |
| High | 6,110 | 5,730 | 2,993 | exogenous |

These values are suitable only for a **proxy capacity-expansion sensitivity**.
They do not provide legal forest/wetland/paddy/ESZ clearance, reservoir operating
permission, road/setback/access checks, candidate-site grid hosting or district
capacity allocation. Full least-cost capacity expansion and validated S0-S5
investment results therefore remain blocked.

Validate the checkpoint with:

```bash
python scripts/validate_full_pypsa_renewable_capacity_v0_7.py
pytest -q tests/test_full_pypsa_renewable_capacity_v0_7.py
```

The next implementation step can now be a first **2030 proxy expansion
counterfactual** combining v0.4 demand, v0.5 costs, v0.6 hourly profiles and v0.7
candidate limits, while retaining explicit slack/import/hydro caveats.


## Implementation checkpoint 10 · 2030 adequacy-first proxy expansion v0.8

v0.8 combines the source-bounded layers assembled in v0.4-v0.7 into the first
full-year capacity-expansion counterfactual. It is **not** a total-system least-cost
plan because landed Kerala import prices remain unresolved.

The v0.8 numerical kernel is implemented with `scipy.optimize.linprog` using the
HiGHS backend and a custom sparse LP. It consumes the Full-PyPSA programme's admitted
v0.4-v0.7 inputs, but this checkpoint is **not** a direct
`PyPSA Network.optimize()` expansion solve. Direct formulation equivalence is a
separate verification step.

The solve is lexicographic:

1. minimize unserved energy;
2. preserve that minimum shortage and minimize annualized solar/wind/4-hour-BESS
   investment cost;
3. hold the selected investment capacities fixed within numerical tolerance and
   minimize import MWh for a non-degenerate reporting dispatch.

The model runs the CSTEP lower FY2030 and CEA/KSERC reference FY2030-31 demand
anchors against 4,455 / 3,564 / 2,673 MW transfer sensitivities, the v0.7
low/reference/high renewable envelopes, and the v0.5 low/high four-hour BESS cost
bracket. Four-hour BESS is capped at **250 MW**, matching the admitted RA planning
additions through 2030.

### ERA5 / IST chronology correction

The v0.6 ERA5 source is hourly in UTC, which maps to :30 local time in India.
v0.8 therefore interpolates the screening profiles from :30 IST onto the model's
:00 IST clock hours. The first six local hours use an explicit one-year cyclic
boundary wrap from the tail of the same representative-year profile. This avoids
silently shifting the solar day by 5.5 hours.

The interpolation preserves annual full-load hours exactly in this run:
**1,358.583 solar FLH** and **1,035.679 wind FLH**, both with 0.0% annual change.

### Main results

For the **lower FY2030 demand case with the full 4,455 MW ATC sensitivity**, the
stage-1 minimum shortage is zero. The least-investment mix depends on the BESS cost
bracket:

- low BESS cost: **126.619 MW / 506.475 MWh** four-hour BESS, with no new solar or wind;
- high BESS cost: **223.694 MW solar + 9.036 MW / 36.143 MWh BESS**, with no new wind.

This is the only non-cap-binding family. It should be read as a lower-bound
adequacy result under favourable, unpriced imports—not as a preferred investment
mix.

With the **80% ATC stress (3,564 MW)**, even the lower-demand case retains a small
shortage after optimization. Under the high renewable envelope it is **22.583 GWh
(0.068%)**, across **136 hours**, with **515.6 MW** maximum hourly shortage.
The optimizer uses **2,921.475 MW wind, 250 MW BESS and 1,072.466 MW solar**.
The fact that solar does not hit its very large high-envelope cap shows that these
remaining shortages occur at times when more solar alone cannot resolve them under
the admitted storage/firm-capacity assumptions.

At the **60% ATC stress (2,673 MW)**, the lower-demand high-envelope case reaches
all candidate limits and still leaves **740.128 GWh (2.244%)** unserved across
**1,683 hours**.

The stronger result is the CEA/KSERC **reference FY2030-31** demand case. Even with
the full 4,455 MW ATC sensitivity and the high renewable envelope, the proxy model
hits **11,407.74 MW combined solar headroom, 2,921.475 MW wind and 250 MW BESS**
and still leaves **357.113 GWh (0.798%)** unserved across **822 hours**, with a
maximum hourly shortage of **1,636.7 MW**.

Reference-demand shortage worsens sharply with transfer stress:

| ATC sensitivity | Low envelope | Reference envelope | High envelope |
|---|---:|---:|---:|
| 4,455 MW | 0.891% | 0.839% | **0.798%** |
| 3,564 MW | 5.795% | 5.146% | **4.539%** |
| 2,673 MW | 16.935% | 14.757% | **12.230%** |

The high-envelope 3,564 MW case still leaves **2.030 TWh** unserved; the high-envelope
2,673 MW case leaves **5.470 TWh**.

Large renewable spill and shortage can coexist in high-envelope cases. That is an
important chronology signal: under the current proxy assumptions, the problem is
not simply annual renewable energy. It is the coincidence of demand, renewable
availability, import capability, only 250 MW / 1 GWh of candidate BESS, and the
deliberately frozen daily-average historical hydro/nonhydro replay.

The BESS cost bracket changes the investment composition only in the unconstrained
lower-demand/full-ATC case. Once the adequacy limits bind, the optimizer reaches the
same candidate MW limits regardless of whether the low or high BESS cost benchmark
is used.

Durable evidence is recorded in
`data/evidence/models/full_pypsa_proxy_expansion_v0_8_2026_09_25.json`.

These results do **not** establish that Kerala needs the reported MW. They establish
that, under this deliberately bounded single-bus counterfactual, the admitted
renewable/storage envelopes are insufficient for the reference-demand case even
under the dated 4,455 MW transfer sensitivity. The next high-value blockers are
therefore import economics/forward transfer assumptions and a more realistic
firm/flexible supply representation—especially hydro operation, outages and
additional storage/flexibility—before any economic capacity recommendation is
defensible.


## Implementation checkpoint 11 · direct PyPSA formulation equivalence v0.9

v0.9 closes the numerical-engine gap left deliberately explicit in v0.8. The v0.8
capacity-expansion counterfactual was implemented as a custom sparse
`scipy.optimize.linprog` model using HiGHS. v0.9 rebuilds the same admitted
single-bus formulation as an actual **PyPSA Network**, uses PyPSA's Linopy model,
and resolves the same three lexicographic stages through the HiGHS backend.

The PyPSA network represents:

- extendable combined solar with the v0.6 hourly screening profile and v0.7 bound;
- extendable onshore wind with the v0.6 NIWE-anchored screening profile and v0.7 bound;
- extendable four-hour `StorageUnit` using the v0.5 charge/discharge efficiencies,
  annualized research costs and 250 MW candidate cap;
- a fixed import generator at each v0.4 ATC sensitivity;
- an unserved-load generator;
- an explicit negative-dispatch spill sink matching the v0.8 feasibility slack.

For each case PyPSA first minimizes unserved MWh. The resulting minimum-shortage
constraint is then added to the same Linopy model and the objective is replaced by
annualized candidate investment cost. Finally, the selected solar/wind/BESS
capacities are fixed within the same numerical tolerance used by v0.8 and the
reporting dispatch minimizes import MWh.

The artifact-backed full-year run compared **all 36 cases × 8,760 hours** against
the SciPy/HiGHS reference and every declared equivalence check passed. Maximum
absolute differences were:

| Metric | Maximum absolute difference |
|---|---:|
| Stage-1 unserved energy | 1.86e-9 MWh |
| Stage-2 unserved energy | 4.66e-8 MWh |
| Stage-3 reporting unserved energy | 1.00e-6 MWh |
| Solar capacity | 1.86e-9 MW |
| Wind capacity | 2.59e-11 MW |
| 4-hour BESS power | 1.03e-11 MW |
| Annualized candidate investment | 8.57e-9 million INR/year |
| Stage-3 imports | 1.87e-6 MWh |

These differences are effectively numerical solver precision and are far below the
declared v0.9 tolerances. The result therefore verifies that the central v0.8
adequacy-first expansion results are not an artefact of the custom SciPy matrix
construction; the direct PyPSA/Linopy formulation reproduces them.

Durable evidence is recorded in
`data/evidence/models/full_pypsa_pypsa_equivalence_v0_9_2026_09_25.json`.

This remains **formulation verification, not capacity-plan validation**. v0.9 does
not resolve landed import prices, future transfer capability, existing-fleet
economic dispatch and forced outages, reservoir/cascade hydro operation, statutory
renewable siting, site-level grid hosting, fleet-weighted renewable profiles or
probabilistic reliability.

With the optimization engine now independently reproduced, the next high-value
checkpoint should move from numerical plumbing to the largest physical/economic
blockers: first a source-bounded **import-price / forward-transfer package**, then
a materially better **hydro/flexible-supply representation**.
