# WP6 · Managed EV charging and noncritical industrial flexibility

**Executed research chapter, 24 September 2026.** Two independent **illustrative engineering counterfactuals**, both 24 hours and 1-hour dispatch resolution. This builds on [the cooling/TES pilot](WP6_COOLING_THERMAL_STORAGE_PILOT_2026_09_24.md), and implements more of the [original WP6 work package](research_plan.md), but **does not establish Kerala fleet or actual KMML process flexibility**.

[Reusable constrained scheduling model](../src/kerala2040/flexibility_dispatch.py) · [EV input specification](../configs/wp6_ev_charging_illustrative.yaml) · [Industrial input specification](../configs/wp6_industrial_illustrative.yaml) · [Reproduction script](../scripts/run_wp6_flexibility_pilots.py).

## Two *service-equivalent* comparisons

| Service | Unmanaged counterfactual | Managed counterfactual | Hard invariant |
|---|---|---|---|
| EV depot: three hypothetical vehicles | Charge as soon as each car plugs in | Prioritise scarce non-evening charging opportunities and lower background-load hours | Every vehicle receives **the same battery kWh before its departure**; arrival, charger kW, charging loss and shared circuit capacity are identical |
| Industrial process-support: three hypothetical noncritical auxiliary duties | Run each permitted duty as soon as available | Shift noncritical duties into lower-load eligible hours | **Exactly the same scheduled duty kWh by the same deadline**; nonshiftable safety/production-critical load remains unchanged |

Both comparisons share the original, explicit **17:00–21:00 illustrative evening window**, but this is **not** sourced as an actual Kerala grid, feeder or site peak. Each output separately reports whole-day maximum site kW, evening maximum site kW, electricity delivered over the entire day, evening load, completed service and missing deadlines. They are **not independently optimised systems**, cost/CO₂ forecasts, or 2040 outputs.

### 1. Managed EV charging

The EV configuration contains three *authored* arrivals/departures, charger ratings, battery headroom, required **battery-side delivered** charge and AC-to-battery efficiency. The simulator schedules **grid-side** charging energy `E_grid = E_battery / efficiency`; an earlier/later schedule does not create EV traction energy. Every vehicle's terminal battery level is explicitly checked against its starting level, delivered requirement, nameplate headroom and departure hour.

The **same shared 8 kW electrical charging limit** applies to the arrival-order and managed pilot. Managed dispatch orders workloads with the least usable non-evening charging slack first, then prefers non-evening hours of lower already-scheduled site background. This is a transparent **greedy illustrative rule**, *not* an optimal power-flow, MILP, smart-charging product algorithm or forecast. A late-arriving EV has some unavoidable evening charging under the authored depot constraints; the code is not allowed to hide that requirement or assume future charging after departure. The prior 2023 GHG transport statistic concerns emissions; it is **not** used as a direct Kerala EV fleet adoption, utilisation, charging pattern or kWh per vehicle input.

**Sensitivity:** shared EV charger allocation 7.2 / 8.0 / 10.8 kW × efficiency 0.85 / 0.90 / 0.95, each rerunning the **same baseline and managed duties**, all vehicle deadlines. Do not treat changing charging efficiency as an operational outcome of shift scheduling; it is an explicitly changed hypothetical device parameter applied to **both** policies.

### 2. Industrial load shifting

The public [KMML case](KMML_CIRCULAR_INDUSTRY_CASE_2026_09_24.md) identifies utilities, processing units, material links and unresolved measured balances. **It provides neither a verified flexible-kW allocation nor permission to interrupt a plant unit.** The industrial experiment therefore deliberately uses **a generic fictional site**, three optional process-support jobs and a separately recorded **nonshiftable background including safety/critical production loads**. The jobs are called optional batch preparation, optional packaging and noncritical utility recharge *only as modelling roles*, **not as claims about KMML's actual operating timetable, product constraints or accepted industrial energy savings**.

For each authored duty `j`: `availability_start ≤ h < completion_deadline`, `0 ≤ P[j,h] ≤ job_power_limit`, `Σ(P[j,h] × 1h × conversion_efficiency) = same_required_service`. All jobs share the same illustrative 8 kW flexible-load connection ceiling. Site consumption equals *unchanged critical background + scheduled optional duty*. Nothing in this model re-labels ARP, chlorine circuits, boilers, oxygen systems, wastewater treatment, plant instrumentation, statutory environmental compliance or any actual utility as interruptible. The pre-existing KMML case keeps current process meters, recovery credits and industrial-symbiosis benefits **null**.

**Sensitivity:** hypothetical flexible connection 6 / 8 / 10 kW × uniformly required optional job duty 0.8 / 1.0 / 1.2; both dispatch policies execute the **same required duty within each sensitivity**. These variations describe physical feasibility of fictional loads, not annual Kerala or KMML potential.

## The core invariants and method

```text
For each job:
    eligible hours = [arrival, departure/deadline)
    required grid kWh = fixed useful battery / process service kWh ÷ efficiency
    any hour charging/job kW <= individual equipment kW
    sum of simultaneously flexible kW <= same shared connection limit
    useful service received by deadline == useful service requested
    no negative, surplus or post-departure delivered service

Facility = unchanged background + flexible dispatch
Evaluate: daily total energy, full-day max site kW,
          illustrative 17–21 max site kW, evening kWh, missed deadlines
```

The first counterfactual uses **arrival-order earliest eligible hours**. The managed counterfactual schedules the **least off-peak-slack** job first, choosing non-evening hours then minimum background+already-assigned site demand. If the remaining required service cannot be delivered before its deadline, **both cases fail closed**; no unrealised duty is counted as “saved energy.” The simulator enforces shared infrastructure for **both** policies, not only the managed case. It does *not* assert greedy optimality, V2G exports, EV degradation cost, industrial production safety validation, grid-congestion relief or carbon avoided.

Crucially, **the two policies use the same total electricity in each comparison** under fixed conversion efficiencies; the simulation can shift hourly power but may not fabricate reduced useful energy or kWh savings. A system with price- or temperature-dependent charger/process efficiency could produce different daily kWh, but that effect is *not* represented in the current model.

## Reproducibility, publication and how to build on it

```bash
uv run python scripts/run_wp6_flexibility_pilots.py --kind both --out-dir outputs/wp6
uv run pytest tests/test_wp6_ev_industry.py -q
```

The website **regenerates both datasets at publication build time** and exposes 24 hourly records for unmanaged and managed EV, 24 for unmanaged and managed industry, each job's full service accounting, nine independently recalculated sensitivity pairs for each sector, input files, code and full scientific-gate records. The browser runs on the same artefacts.

**Evidence needed to graduate:** independent public or permissioned arrival/departure/SoC and depot feeder measurements for EV charging, charging equipment efficiencies and actual distribution constraints; for industry, plant-approved metering, process scheduling eligibility, no-harm/safety sign-off, tariffs/contracts, measured service/product quotas and confidentiality clearance. Then match a source-valid **Kerala hourly grid chronology** if claiming grid benefit. Neither a 24-hour illustrative shift nor a generic industrial job is permission to report statewide Kerala MW, annual emissions, utility expenditure, company production improvement or an optimised 2040 pathway.

**State of WP6:** all three illustrative executable demonstrations—cooling/TES, EV charging and optional industrial flexibility—are implemented. Measured Kerala calibration, BESS/pumped storage, grid services, pilot operator validation and numerical 2040 scenario admission remain separate, open tasks.
