# WP6 · Cooling, pre-cooling and thermal storage: executable first experiment

**Kerala2040 independently authored engineering demonstration · 24 September 2026.** The original [WP6 research plan](research_plan.md) includes BESS, pumped storage, reservoirs, thermal storage, EV charging and industrial flexibility. This is the **first fully executed cooling-specific experiment**, not completion of all WP6 technologies.

[Versioned illustrative inputs](../configs/wp6_cooling_tes_illustrative.yaml) · [Auditable Python model](../src/kerala2040/flexibility_cooling.py) · [Tests](../tests/test_wp6_cooling.py) · [Interactive site comparison](https://kerala2040.github.io/#pathways).

## Research question and scope

Can **the same hypothetical cooling zone maintain the same 24–26 °C indoor comfort envelope** while moving electricity away from an **illustrative 17:00–21:00 peak window** through (A) a baseline AC thermostat, (B) early pre-cooling of the zone's thermal mass, and (C) a separately charged cold-water store? How do **total daily kWh, window-specific kW, whole-day maximum kW, zone temperature, cooling effort, state of charge and setpoint shortfall** differ?

**Nothing in the inputs is measured Kerala climate, a real building, ERA5 weather, SLDC hourly load, utility pricing or a proposed 2040 installation.** Only an explicit 24-hour synthetic outdoor-temperature array, one simple building and authored device characteristics enter this run. The site cannot convert these results into state-wide MW, MWh, CO₂, rupees or estimated annual savings. We compare **the same comfort requirement, not equal delivered thermal-cooling kWh**: pre-cooling intentionally adds cooling energy and can increase daytime or total electricity.

## Thermal and electrical model

This is a deterministic, 1-hour explicit-Euler **1R1C** single-zone balance, not EnergyPlus, calibrated building physics, operative-temperature or humidity control:

```text
C [kWh/K] × (T_next − T_now) =
  UA [kW/K] × (T_out − T_now) × 1h
  + Q_internal [kW] × 1h
  − Q_delivered_to_room [kWh_th]

Q_requested = max(0, C × (T_now − T_target) + Q_heat)
Q_room = min(Q_requested, AC_max_thermal × 1h)
T_next = T_now + (Q_heat − Q_room) / C

COP_direct(T_out) = clamp[3.90 − 0.09 × (T_out − 28°C), 2.3, 5.2]
Grid electricity = direct_room_cold / COP_direct
                 + storage_thermal_charge_input / (0.85 × COP_direct)
                 + storage_discharge_to_room × 0.045 kWh_e/kWh_th
```

This COP equation is **illustrative technology behaviour**, not an empirical performance curve from a selected product or site. The cold-storage plant and direct AC use the specified thermal rates; the charging chiller is a **separate asset** so electricity at off-peak charging is not assigned unlimited free grid capacity. Real coil/pump electrical power, sensible/latent allocation, dewpoint control, part-load COP and power limitations must eventually be replaced by measured performance.

The stored *cold-energy* state obeys, each hour and **on unrounded values**:

```text
stock_after = stock_before × (1 − 0.003)
            + 0.92 × charging_cold_input
            − cold_delivered_to_room / 0.94
```

Checks reject charge/discharge in the same hour, over-capacity, negative stock and double allocation of direct and stored cooling. The daily experiment **starts and ends with an empty cold store and the same 25.5°C zone state**: it cannot hide unpaid pre-cooling or unexplained stored energy at the 24-hour boundary. For a typical non-cyclic case, the end-state change would have to be priced explicitly rather than silently ignored.

## Experimental cases and assumptions

| Physical/control boundary | Authored example, NOT a Kerala statistic |
|---|---|
| Zone | 3.5 kWh_th/K effective thermal capacitance; 0.20 kW/K UA; 0.42 kW internal gains; 4.8 kW_th direct AC ceiling |
| Common comfort envelope | 24.0–26.0°C, initial and final state 25.5°C |
| Conventional | 25.5°C thermostat for all 24 hours, no store |
| Pre-cooling | 24.4°C target hours 13–16, then normal 25.5°C thermostat; no mechanical store |
| Chilled-water storage | 6 kWh_th; cold charge up to 1.15 kW_th in hours 00–06, deliver up to 1.6 kW_th in hours 17–21; hourly standing loss 0.3%; charging/discharging efficiencies 0.92/0.94; charging COP multiplier 0.85 |
| Score windows | Full-day maximum grid kW **separate from** maximum 17–21 grid kW; full-day grid kWh **separate from** 17–21 grid kWh |
| Sensitivity matrix | Cold-storage capacity 3/6/9 kWh_th × charging COP multiplier 0.75/0.85/1.0 = **nine reproducible variants** |

**Setpoint shortfall ≠ unmet occupant comfort.** At the first pre-cooling hour a 4.8 kW_th AC ceiling can prevent reaching the *early* 24.4°C target in a single hour. This is recorded as thermal **setpoint shortfall**; comfort violation is counted **only if the simulated room leaves 24–26°C**. An actual engineering design must use operative temperature, humidity and occupancy to validate comfort. A precooling "desired-load deficit" must not be casually described as occupants going without cooling.

**Peak-shaving caution.** With this particular synthetic profile, the hottest hours occur before 17:00. Reducing the **evening peak** does not necessarily lower the **maximum over the entire day**. The model publishes both metrics to prevent a false whole-system peak-shaving claim; an actual Kerala utility benefit requires coincident feeder or grid peak chronology, not a hand-selected tariff window.

## How to reproduce

```bash
uv run python scripts/run_wp6_cooling_pilot.py --output /tmp/wp6-pilot.json
uv run pytest tests/test_wp6_cooling.py -q
```

The website build regenerates `data/wp6-cooling-pilot.json` from the source configuration and model at build time; no externally downloaded hourly series or private acquisition is required. The source includes **all 24 hourly** electricity/cooling/temperature/state values in each of the three scenarios, the 9 sensitivity runs, and boolean source-release limits. Input files and output remain independently readable.

This is a **screening experiment**: no solver is used to optimise control, storage placement, seasonal COP, project economics, avoided emissions, or the statewide dispatch. Pre-cooling can shift cooling duty while **adding** total energy; storage can reduce a selected window's electric peak while **increasing** total kWh because of charge/discharge losses, auxiliary electricity and charging COP penalty. Whole-day peak and total energy must not be conflated with the window-only values.

## Extending the original WP6 after this bounded first pilot

1. **Calibrate the cooling service** using permissioned weather, building thermal response, indoor temperature/humidity and AC COP/part-load measurements; validate multiple day types and rebound.
2. Add **hourly Kerala grid peak coincidence and tariff** only after source-valid continuous records are admitted; compare unmet cooling, peak and real rupees against the *same* comfort constraint and terminal store conditions.
3. Extend to **EV charging**, with arrivals/departures, required state-of-charge, feeder limits and additional electricity from actual vehicle efficiency; do not label shifted charging as an energy saving.
4. Compare **industrial flexibility**, starting from source-approved KMML process schedules, without disrupting production or disclosing confidential setpoints.
5. Only after all physical, fiscal, resource and time boundaries are met, allow the flexible service to enter the 2040 optimisation.

**Publication gate:** **demonstration finished, Kerala-wide flexibility capacity, energy saving, annual emissions benefit and financial benefit not established**. No real-world ranking of technologies follows from a single synthetic weather/control day.
