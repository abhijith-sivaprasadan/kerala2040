# Assumptions and uncertainty register

The purpose of this register is to prevent an assumption from being remembered later as a measurement.

## Scale

- **A — low-impact / bookkeeping:** unlikely to change a material conclusion.
- **B — material:** can change magnitudes or case rankings.
- **C — structural:** can change whether a headline conclusion holds.

“Bias direction” is stated only where it is reasonably predictable. Otherwise it is marked unknown.

| ID | Domain | Assumption / approximation | Why needed | Scale | Likely effect / bias | Current treatment |
|---|---|---|---|---|---|---|
| U01 | SLDC | 11 missing FY24–25 daily energy values interpolated for 8760 proxy only | full chronology needed | A/B | small annual effect; local dates uncertain | flagged model-only |
| U02 | load | daily total is exact on 354 observed days | preserve strongest source | — | none for daily energy | hard constraint |
| U03 | load | intraday clock-shape fitted from sparse extrema | no hourly telemetry | B | could miss non-extreme hourly structure | held-out extrema test |
| U04 | load | weather terms perturb within-day shape | capture weather variation | B | unknown | coefficients non-causal |
| U05 | load | every day renormalized to known daily MWh | protect observations | — | suppresses error in daily-energy prediction | explicit |
| U06 | future demand | historical shape rank/order retained under affine morph | future hourly chronology unavailable | C | may understate structural shape change from EV/cooling/solar | scenario, not forecast |
| U07 | demand | lower/reference source families used without averaging | preserve source identity | B | widens uncertainty instead of smoothing | explicit |
| U08 | renewables | five representative ERA5 cells | bounded spatial proxy | C for hourly fleet output | misses microclimate/capacity geography | screening only |
| U09 | renewables | equal weight across five points | no admitted capacity weights | C | direction unknown | not fleet generation |
| U10 | solar | PR=0.82 | generic PV conversion | B | project/fleet dependent | screening assumption |
| U11 | solar | simple cell-temperature rise 0.025 K/(W/m²) | no module model | B | uncertain | screening assumption |
| U12 | solar | no tilt/azimuth/inverter/soiling | data unavailable | B/C | likely distorts yield/shape | stated limitation |
| U13 | wind | shear exponent 0.14 | extrapolate ERA5 10 m to 150 m | C | site/season dependent | sensitivity assumption |
| U14 | wind | NIWE mean anchor | improve long-term magnitude | C | forces mean to external map | cannot validate against same mean |
| U15 | wind | generic 3/12/25 m/s turbine curve | future turbine unknown | C | technology dependent | screening only |
| U16 | renewable caps | study-based low/reference/high statewide envelopes | legal GIS ceilings unavailable | C | not buildable MW | scenario sensitivity |
| U17 | costs | real FY2021–22 common price basis | compare source costs | B | depends on deflator | CPI transparent, not sector index |
| U18 | costs | CEA v2 solar/wind/4h-BESS planning capex at 2021–22 cost level | no Kerala project-specific quotes | C for investment mix | can shift mix | primary-source units re-verified; research benchmark only |
| U19 | BESS | 4-hour duration | bounded technology case | C | favors 4h applications | explicit scenario |
| U20 | BESS | 88% round-trip efficiency | generic planning assumption | B | project dependent | sensitivity |
| U21 | finance | 9.08% CERC post-tax WACC-equivalent discount benchmark for non-SHP RE | annualization | C for economics | higher rate penalizes capex | primary-source formula re-verified; not Kerala project WACC |
| U22 | existing fleet | historical daily-average replay | plant dispatch data incomplete | C | suppresses real intra-day flexibility/constraints | not economic dispatch |
| U23 | adequacy | no forced outages in deterministic core | outage data unavailable | C | optimistic relative to reliability model | not LOLP |
| U24 | adequacy | current ATC 4455 used as future reference | no future ATC published | C | could over/understate future import capability | dated counterfactual |
| U25 | adequacy | 80%/60% ATC haircuts | stress testing | C | intentionally adverse | synthetic |
| U26 | economics | lexicographic adequacy-first objective | avoid invented VOLL | C | prioritizes shortage avoidance over welfare optimum | explicit |
| U27 | import cost | annual KSEBL cost used as flat price proxy | no hourly landed price | C for economics | erases price chronology | partial economics |
| U28 | hydro v1.1 | daily hydro MWh can move within day subject to power | isolate timing | C | optimistic if real constraints bind | sensitivity bound |
| U29 | hydro v1.2 | 3/15/30-day energy windows | bracket interday flexibility | C | intentionally synthetic | not storage duration |
| U30 | Idukki | 780 MW plant power | station representation | B | source/date dependent | explicit |
| U31 | Idukki | 1460 MCM effective full storage | stateful pilot | C | determines energy stock | requires source trace in QA |
| U32 | Idukki | 1470 MWh/MCM fixed equivalent | convert water-equivalent state | C | ignores head/efficiency variation | source-derived approximation |
| U33 | Idukki | storage gaps interpolated v1.3 | complete state series | B | smooths short gaps | pilot-only |
| U34 | Idukki | generation gaps interpolated v1.3 | complete pilot forcing | B | smooths short gaps | disclosed |
| U35 | Idukki | reconstructed net balance | introduce state before direct inflow | C | absorbs spill/release/diversion/error | never called inflow |
| U36 | Phase 4 | gauge rainfall ≠ catchment rainfall | source limitation | C | spatial mismatch | no basin causal claim |
| U37 | Phase 4 | complete-case regression | missing rainfall | B/C | sample-selection bias | population counts disclosed |
| U38 | Phase 5 | no catchment admitted until independent geometry | avoid area fitting | — | conservative/fail-closed | strong guardrail |
| U39 | network | 2026 public topology assumed usable with 2023 PSS equipment snapshot | source vintages differ | C | stale equipment possible | P1 Shornur example found |
| U40 | network | generic overhead X by voltage | no complete source X | C for flow distribution | can move modeled corridor flows | screening only |
| U41 | network | transformer X=0.10 pu where needed | incomplete impedances | C | affects flow distribution | screening assumption |
| U42 | network | thermal MVA from sqrt(3) V I and repeated SLD current | operator ratings unavailable | C | not seasonal/emergency rating | screening rating |
| U43 | network | fallback ampacity for unsupported conductors | maintain topology | C | conservative intent not guaranteed everywhere | excluded from primary source-backed claims |
| U44 | network | bus load ∝ low-side PSS transformer MVA | no bus telemetry | C | can distort geography | proxy |
| U45 | network | mapped generation ∝ installed MW share of technology daily energy | no unit dispatch | C | ignores unit-specific dispatch | proxy |
| U46 | network | unmapped generation netted at loads | avoid invented plant location | C | reduces spatial generation specificity | explicit |
| U47 | network | residual import split across six boundary interfaces | no interface telemetry | C | affects flows | 8-case sensitivity |
| U48 | network | single-interface cases | stress location uncertainty | C | deliberately extreme/unphysical | robustness only |
| U49 | network | no reactive power | DC/linear screen | C | cannot assess voltage | no voltage claim |
| U50 | network | no N-1 | outage states unavailable | C | cannot assess security | no N-1 claim |
| U51 | ecology | DEM is terrain/elevation evidence, not legal siting | source limitation | C for siting | none | no buildable-MW output |
| U52 | ecology | incomplete forest/wetland/hazard exclusions | source access | C | buildable area unknown | fail closed |
| U53 | WP6 | EV/industry/cooling profiles are authored | no measured Kerala pilot | C for scale | cannot estimate statewide MW | mechanism only |
| U54 | WP6 | greedy scheduling | interpretability | B | not optimal | deliberate |
| U55 | PSP pilot | hypothetical head/efficiencies | educational physics | C | no site feasibility inference | explicitly hypothetical |
| U56 | context | SEK conversion depends on FX date | audience scale | A | small conversion movement | dated |
| U57 | budgets | planning estimates ≠ final cost | project stage | C for “cheap” claim | likely under/overrun possible | stage labels mandatory |
| U58 | synthesis | interactions inferred from separate evidence strands | no event causal design | C | cannot allocate causal shares | hypothesis, not theorem |

## Assumptions that matter most

If an expert asks where the results are most fragile, the answer should be:

### 1. Future adequacy magnitude

Most sensitive to:

- future demand source;
- external transfer availability;
- renewable capacity envelope;
- fixed/replayed existing fleet behavior.

### 2. Renewable expansion mix

Most sensitive to:

- capex/finance assumptions;
- candidate capacity ceilings;
- hourly profiles;
- BESS costs/duration;
- import price.

### 3. Network overload magnitude

Most sensitive to:

- spatial load allocation;
- generator dispatch;
- branch ratings;
- reactances;
- current equipment configuration.

The **location** of some stressed corridors is stronger than their modeled loading magnitude because of independent CEA corroboration.

### 4. Hydro adequacy benefit

v1.1/v1.2 establish that timing can matter enormously, but real achievable benefit depends on:

- water availability;
- reservoir/cascade constraints;
- minimum releases;
- plant outages;
- head;
- operational rules.

### 5. Ecology/buildability

Still intentionally unresolved. No capacity plan should be promoted to “buildable” before statutory constraints are complete.

## How to talk about uncertainty

Prefer:

> “This is the parameter I assumed, this is why I needed it, and this is the conclusion it can affect.”

Avoid:

> “The model is robust because I tested many scenarios.”

Scenario count alone does not establish robustness if the dominant uncertain variable was not varied.
