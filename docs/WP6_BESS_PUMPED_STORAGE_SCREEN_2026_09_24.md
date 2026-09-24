# WP6 · Battery energy storage and pumped storage: fixed-service screening

**Executed engineering demonstration, 24 September 2026. This is not a pumped-storage site design or an investment recommendation.**

[Executable model](../src/kerala2040/flexibility_storage.py) · [Authored inputs](../configs/wp6_bess_psp_illustrative.yaml) · [Reproduction command](../scripts/run_wp6_storage_screen.py) · [Tests](../tests/test_wp6_storage.py) · [Pathways experience](https://kerala2040.github.io/#pathways).

## Scope and research question

The original WP6 plan asks about battery storage, pumped hydro, thermal storage and flexibility. The earlier three models cover cooling/TES, EV charging and noncritical industrial jobs. This fourth pilot addresses a **different service**: whether two deliberately hypothetical stores can move *exactly 2 kWh of electrical output per hour* into each of five authored evening hours while (a) observing power, energy, loss and charge windows, (b) starting and ending with **zero stored energy**, and (c) displaying the **charging energy and daily net loss**. This is not a forecast for any Kerala feeder, tariff, solar plant, reservoir or 2040 system.

A source-labelled 24-hour fictional site demand, with charging allowed at hours 00–06 and output at 17–21, is shared by both technologies and the unstored baseline. These are not observed SLDC interval values. The model reports *evening site peak separately from whole-day peak*, plus total site electricity. It does **not** assign free zero-emission charging electricity or assert availability of curtailed solar.

## Two illustrative physical boundaries, not a technology ranking

| Input or constraint | Hypothetical BESS | Hypothetical pumped-storage electrical analogue |
|---|---:|---:|
| Internal stored-energy capacity | 16 kWh | 16 kWh gravitational potential-energy equivalent |
| Charge input limit | 4 kW electric | 4 kW electric |
| Electrical discharge limit | 3 kW | 3 kW |
| Charge efficiency | 0.95 | 0.90 |
| Discharge efficiency | 0.95 | 0.88 |
| Hourly standing loss | 0.0005 | 0.0001 |
| Extra auxiliary grid energy per kWh discharged | 0.005 kWh | 0.02 kWh |
| Physical conversion | Simplified AC-bus battery store | A fictional *300 m constant head*, reference water density 1000 kg/m³ and gravity 9.81 m/s² |

**All inputs were authored for this code experiment.** They are neither vendor quotes nor performance measurements of a named BESS, nor verified Kerala head/flow/storage data. A 16 kWh modelled PSP is only a *small hydraulics unit cell*, not a meaningful utility-scale design. The two examples share **delivered electrical service**, *not* identical size, lifetimes, costs, controllability, material effects or physical feasibility. They should not be ranked as real technologies from this synthetic example.

## Exact electricity / energy accounting

Let `S_h` be electricity-equivalent energy internally stored at the beginning of hour `h`; `C_h` grid electricity used to charge; `D_h` electrical output delivered to site; `η_c, η_d` directional conversion efficiencies and `λ` a standing-loss fraction. The code enforces the **unrounded** conservation equations:

```text
S_(h+1) = (1 − λ) S_h + η_c C_h − D_h / η_d

site_import_h = background_h + C_h + auxiliary_h − D_h
auxiliary_h = D_h × technology_specific_auxiliary_factor

S_0 = 0; S_24 = 0;
0 ≤ S_h ≤ capacity; 0 ≤ C_h ≤ charge kW × 1h;
0 ≤ D_h ≤ discharge kW × 1h;
C_h × D_h = 0 within the same hour.
```

Charging is **back-solved latest-first** for exactly the requested evening service, including intervening standing loss, not optimised for a real electricity-price curve. A schedule is **infeasible** if sufficient capacity or hours are absent. Infeasible sensitivity entries remain null and labelled as such—**no partial service is presented as having succeeded**. This avoids both “free initial energy” and an end-of-day store credit that inflates apparent benefits.

The full-day net electricity change obeys: **extra site grid energy = charging grid kWh + auxiliaries − delivered kWh**. Because `η_c,η_d ≤ 1` and auxiliary demand is nonnegative, this screen cannot manufacture daily kWh savings. Evening net site load is reduced, but hours used to charge are **increased**. The actual whole-day maximum is measured over *all 24 hours*; no change in the hypothetical evening maximum is called a statewide or coincident grid benefit.

## Pumped-storage water volume: *hydraulic analogue only*

For a **constant, hypothetical** net head `H`, unit volume's potential energy is:

```text
stored_kWh_per_m³ = (ρ kg/m³ × g m/s² × H m) / (3.6 × 10⁶)
water_m³_in_upper_store = stored_kWh / stored_kWh_per_m³
```

This **does not** admit a real reservoir or infer water volume from an SLDC MU figure. Real pumped storage additionally needs *two uniquely identified interconnected reservoirs*, verified live-storage and water-level geometry, gross versus net head curves, head losses, pump/turbine performance, evaporation, seasonal inflows, environmental flows, downriver users, minimum storage and flood-rule constraints. Our existing [hydro topology configuration](../configs/hydro_topology_evidence_2024_25.yaml) explicitly prohibits treating a cascade's shared water as independent stores or translating SLDC generation-equivalent MU directly into m³. **No invented upper/lower reservoir pair is connected here.**

### Project-discovery sources, separately dated and not model capacity

The [CEA regular Hydro Planning and Investigation index](https://cea.nic.in/hpi-report/?lang=en) lists an **August 2026** monthly pumped-storage status report. A [dated May 2025 CEA Kerala state profile](https://cea.nic.in/wp-content/uploads/hpi/2025/04/All_India_Hydro_Potential_Profile_April_25-2.pdf), source page **PDF index 85**, lists Idukki and Pallivasal as proposed pumped-storage *leads*, not as operating store dispatch constraints. The accessible text indicates a planning/allotment context in 2025. **The original page-image viewer returned a cache miss on 24 September 2026**, so that PDF is a *text-indexed, page-image-unverified discovery source* and no project capacity is imported from it into this pilot. The August 2026 status PDF was **not independently downloaded and reconciled project by project** in this sprint; the report's index is not evidence of current Kerala site clearances or in-service capacity. Do not equate a named existing hydro dam with a permitted and hydraulically feasible reversible-powerhouse project.

**The project-specific research gate is separate from this complete physical toy experiment:** official updated project status and DPR or PFR, upper and lower storage curves, head and route geometry, separate water bodies and ownership, turbine/pump routing, operating rules, current environmental and forest consent, dam safety, land use, water rights, grid point/transfer limit, electrical ancillary-service specification and independently documented project financing.

## Sensitivity and reproducibility

For **each** technology, 3 capacities (8, 12, 16 kWh) × 3 charging efficiencies (0.80, 0.90, 0.95) yield **nine explicit model reruns**. Inadequate capacity remains an **infeasible** result with null energy and peak entries. The common required electrical output does not get reduced until a case “passes”; a sensitivity can fail rather than claim an equivalent service. Varying charge efficiency is applied only to the toy technology case, not to real procurement.

```bash
uv run python scripts/run_wp6_storage_screen.py --output outputs/wp6/wp6-storage.json
uv run pytest tests/test_wp6_storage.py -q
```

Site-build output is regenerated from the checked source config and exposed as `data/wp6-bess-psp.json`, including all 48 case-hour rows plus the 24-hour unstored baseline and 18 sensitivity cells. Python tests check charge/discharge windows, physical storage balance, input limits, zero terminal state, no fake electricity savings, hydraulic conversion consistency and strict source gates. Browser tests check the live comparisons, plots and downloadable file.

## Precisely what remains open

**Delivered:** executable, physically bounded illustrative electrical-storage screening for BESS and a pumped-hydro unit cell, with complete charge/discharge loss accounting, separate peak metrics, transparent source restrictions and sensitivity infeasibility.

**Not verified Kerala evidence:** measured coincidence and net-load chronology, actual battery procurement/site performance, real water-pair constraints or site clearances, economic and carbon value, annual cycling and degradation, reserve/ancillary-service feasibility, or any dispatchable Kerala 2040 MW/MWh recommendation. **Not verified Kerala data** is not the same as proof a technology cannot work. This work provides a reusable **model structure** for admitting future source-matched evidence rather than claiming it is already present.
