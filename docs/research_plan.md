# Kerala2040 research plan

## Research identity

Kerala2040 is now organised as a **diagnosis-first study of Kerala's electricity system under stress**.

The project begins with the present system rather than a preferred 2040 technology mix:

> **Why is Kerala susceptible to electricity shortages and peak-hour supply restrictions, and what structural and operational factors determine whether the system can meet demand during stressed periods?**

The future question follows from the diagnosis:

> **Given the vulnerabilities identified in the present system, what changes should be tested to make Kerala's electricity supply more resilient as demand grows toward 2040?**

The project therefore separates three things that were previously too easy to mix:

1. **diagnostic evidence** — what the historical data and screening models support now;
2. **candidate responses** — mechanisms that early experiments suggest are worth testing;
3. **future recommendations** — decisions that require deeper physical, economic, ecological and reliability validation.

See [the 28 September synthesis](POWER_SYSTEM_STRESS_SYNTHESIS_2026_09_28.md).

## Research questions

### RQ1 — Electricity balance and structural dependence

How has Kerala's electricity balance changed, and how important is electricity arriving from outside the state?

Primary evidence: KSEBL / Kerala State Planning Board annual statistics, audited SLDC daily history, import and transfer documents.

### RQ2 — Chronology, peaks and weather

Is supply stress mainly an annual-energy problem, or does it arise because demand and available supply do not coincide in time?

Primary evidence: 354 observed FY2024–25 SLDC days, ERA5-sensitive 8,760-hour demand reconstruction, chronological adequacy screens.

### RQ3 — Hydropower flexibility

How much adequacy value comes from the **timing** of Kerala's existing hydropower rather than simply its annual MWh?

Primary evidence: daily-energy-constrained hydro sensitivity, interday timing brackets, stateful Idukki pilot and reservoir observations.

### RQ4 — Interstate electricity and transfer capability

How vulnerable is Kerala to the availability, transfer capability and cost of external electricity?

Primary evidence: dated ATC/TTC documents, import-price sensitivities and future adequacy screens.

### RQ5 — Internal deliverability

Can the statewide balance look adequate while internal lines or transformers remain stressed?

Primary evidence: public KSEBL multibus reconstruction, 8,760-hour network screen and eight-case boundary-allocation robustness test.

### RQ6 — What should be tested as a response?

Which combinations of better operation, demand flexibility, storage, grid reinforcement and additional supply address the diagnosed constraints most effectively?

This remains a **screening / future-work question**, not a completed investment recommendation.

## Causal frame

The research treats Kerala as a coupled system:

- **weather / heat / humidity → demand timing and cooling load**
- **rainfall / monsoon → reservoir conditions and hydro opportunity**
- **local generation + hydro flexibility + external electricity → statewide supply balance**
- **interstate interfaces + internal network → physical deliverability**
- **land + ecology + hazards + communities → where infrastructure can fit**
- **cost + public/private finance → what can actually be delivered**

The study distinguishes:

- annual energy sufficiency from hourly adequacy;
- resource availability from network deliverability;
- structural vulnerability from the trigger of a particular event;
- a promising mechanism from a validated investment decision.

## Work packages under the revised framing

The existing work is retained, but each work package now serves the research questions instead of competing for equal prominence.

### Core diagnosis

**WP0 — Baseline and provenance**  
Historical electricity accounting, source boundaries, release gates and reproducibility.

**WP1 — Demand, weather and chronology**  
Observed daily demand, ERA5-sensitive hourly reconstruction, peak timing and future demand sensitivities.

**WP2 — Statewide adequacy and imports**  
PyPSA / OSeMOSYS screening of chronology, candidate resources, import cost and transfer constraints.

**WP3 — Internal network deliverability**  
Public KSEBL network reconstruction and screening of persistent line/transformer stress. AC/N-1 validation remains future work.

**WP4 — Hydro, water and climate**  
Observed reservoir/station data, hydro timing sensitivities and the Idukki pilot. Catchment hydrology and climate ensembles remain later validation.

### Feasibility boundary

**WP5 — Ecology, land and hazards**  
Terrain, protected-area, wetland, waterbody and hazard evidence constrains where future assets can plausibly be considered. No legal buildable-MW ceiling is claimed yet.

### Candidate responses

**WP6 — Storage and demand-side flexibility**  
Cooling/TES, managed EV charging, industrial scheduling, BESS and pumped-storage analogues. These are mechanism tests, not statewide savings estimates.

### Supporting system context

**WP7 — Circular industry and wider energy use**  
KMML first case, Total Energy Atlas, fuels and emissions. This broadens the long-term transition picture without being presented as a root cause of present electricity stress.

**WP8 — Finance and delivery**  
Separate whole-system economics, KSEBL/state fiscal exposure, Union/central-PSU support, private capital and green/development finance. Use project-specific official budgets where possible and label SEK conversions by FX date.

**WP9 — Technology and Kerala case studies**  
CIAL, Kochi Metro, Kochi Water Metro and other existing examples show pieces of the transition in practice. They are contextual precedents, not causal evidence for statewide restrictions.

## Evidence hierarchy

Results are presented in four levels:

1. **Observed / source reported** — the strongest class;
2. **derived from observed data** — arithmetic or reconstruction with explicit rules;
3. **screening model / sensitivity** — useful for mechanisms and bounds;
4. **educational hypothesis / candidate response** — plausible next step requiring further validation.

No result is promoted to a stronger class merely because it appears on the website or poster.

## Current release boundary

The CET/public release is now in **modelling freeze**.

No new model family should be added unless it:

- uses genuinely new evidence that is not already represented; or
- has a realistic chance of changing a material conclusion.

The release can already support a defensible public-data diagnostic story. Remaining mandatory work is synthesis, website/README alignment, final QA and release packaging.

### Optional post-release evidence upgrades

1. independently validated Idukki catchment → ERA5 rainfall → observed inflow work;
2. official KSEB FY2024–25 reservoir/inflow model run if the required source workbooks become accessible;
3. calibrated AC/N-1 network assessment if sufficient impedances, operating states and outage data become available;
4. legally complete ecological/siting constraints and project-specific reinforcement costs;
5. full least-cost / reliability optimisation after those physical gates are resolved.

## Government and stakeholder engagement

Use a staged approach:

1. independent public-data diagnosis;
2. targeted requests for missing telemetry, hydrology, network and project-cost evidence;
3. technical review with relevant agencies/PSUs where useful;
4. deeper collaboration only when non-public data are required.

Do not imply Government of Kerala, KSEBL, KTH or any other organisation endorses the study unless explicit permission is obtained.
