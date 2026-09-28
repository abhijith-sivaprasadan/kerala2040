# Methodology defense: why each choice was made

This is the document to study before the conference when someone asks:

- Why did you model it that way?
- Why not use a more sophisticated method?
- Why should I trust this result?
- What did you deliberately **not** do?

The general answer is:

> **Model sophistication was limited by evidence, not by software availability. Kerala2040 prefers a simpler model whose assumptions are visible over a sophisticated model populated with invented parameters.**

---

## 1. Why start with source/accounting reconstruction instead of immediately optimizing 2040?

### Choice

Build an audited historical baseline first.

### Reason

Capacity-expansion models can produce precise-looking results from inconsistent inputs. Kerala data are fragmented across:

- annual state statistics;
- daily SLDC reports;
- CEA planning studies;
- network maps/SLDs;
- weather products;
- project documents;
- resource atlases.

The first scientific task is therefore to establish which quantities share a boundary and date.

### Why not jump directly to a standard “least-cost 2040” model?

Because the result would be determined by unvalidated assumptions for:

- hourly demand;
- imports;
- hydro;
- renewable profiles;
- network;
- buildable land;
- project costs.

A detailed optimization does not compensate for weak input evidence.

---

## 2. Why retain conflicting accounting boundaries instead of reconciling everything to one number?

### Choice

Preserve broad consumption, category sales, periphery input, SLDC daily balance and import-energy statistics as separate series where definitions differ.

### Reason

A forced reconciliation would silently invent adjustments.

### Alternative rejected

**Single canonical historical energy number.**

Rejected because a number cannot be “corrected” across different system boundaries without source-supported loss, open-access, captive, export and accounting terms.

### Defense

> “I treat accounting boundaries as metadata, not noise.”

---

## 3. Why use an hourly reconstruction rather than actual hourly load?

Because public continuous hourly/15-minute Kerala state load telemetry was not available in the admitted evidence.

### Choice

Conserve observed daily energy and reconstruct only the within-day shape.

### Why this is preferable to inventing an hourly series

The strongest source information — the daily MWh total — remains exact on observed days.

Only the unobserved intraday distribution is modeled.

### Why not simply use a generic national load shape?

Kerala has a different climate, distributed solar penetration, household/service mix and peak timing. A Kerala-specific sparse-extrema/weather shape is more defensible.

### Why not train LSTM/XGBoost/Transformer forecasting?

Because the project does not possess a dense historical hourly target series.

Training a complex supervised hourly forecasting model without hourly labels would be pseudo-sophistication.

The problem is **reconstruction**, not forecasting.

### Why use ERA5?

ERA5-Land provides a complete, physically consistent weather chronology for:

- temperature;
- humidity/dewpoint-derived humid heat;
- shortwave radiation;
- rainfall;
- wind.

It can explain day-to-day differences in intraday shape without pretending the coefficients are causal.

---

## 4. Why renormalize every reconstructed day to the SLDC daily energy?

### Choice

After shape/weather perturbation, force 24-hour sum back to the observed daily MWh.

### Reason

Otherwise weather fitting would corrupt a quantity that is actually observed.

This intentionally separates:

- **daily quantity** — source observed;
- **intraday shape** — reconstructed.

### Cost

It means the model cannot be evaluated as a day-ahead total-load forecast. This limitation is accepted explicitly.

---

## 5. Why use held-out Jan–Mar extrema?

A chronological holdout is preferable to random splitting for time-dependent electricity data.

Random splits can leak seasonal/temporal structure.

January–March was withheld from coefficient fitting and used to assess intraday extrema.

### Why extrema instead of every hourly point?

Because extrema are what the public SLDC source provides.

The project refuses to manufacture hourly ground truth that does not exist.

---

## 6. Why not claim causality from weather coefficients?

Because:

- temperature, humidity, solar radiation and rainfall are correlated;
- behavior and clock time are confounders;
- daily normalization changes coefficient interpretation;
- no causal identification design exists.

The coefficients are predictive/associational shape terms.

---

## 7. Why use 8,760 hours?

### Choice

Full chronological year rather than representative days for the primary screening.

### Reason

Peak adequacy, storage and renewable coincidence depend on chronology.

Representative periods can under-represent rare stressful sequences unless carefully weighted/selected.

### Why FY2024–25?

It has the strongest near-complete daily SLDC evidence bundle and aligns with much of the current official baseline work.

### Limitation

The year is not automatically a climatological or reliability design year.

A multi-year stochastic study would be stronger later.

---

## 8. Why affine-morph the historical shape to official future energy + peak anchors?

### Choice

Preserve the reconstructed chronology rank/order while applying an affine transformation that hits each source scenario's annual energy and peak.

### Reason

Official future sources provide energy and peak but not a full 8,760-hour chronology.

The transform asks a controlled counterfactual:

> what if the observed shape evolves to this source-defined annual energy and peak?

### Why not independently forecast 2030 hourly demand?

There is insufficient sectoral/hourly evidence to estimate a defensible structural future load model.

### Limitation

Electrification may change load shape, not merely scale it. Therefore this is a scenario morph, not a forecast.

---

## 9. Why keep several future demand sources rather than average them?

### Choice

CSTEP lower, CEA/KSERC reference and CEA transmission high-case remain named source families.

### Reason

They arise from different assumptions and planning purposes.

Averaging them would create a new scenario with no source behind it.

### Defense

> “Disagreement between official studies is uncertainty evidence, not something to average away.”

---

## 10. Why use one-bus statewide adequacy models at all?

### Choice

Start with an aggregate Kerala balance for adequacy/expansion sensitivities.

### Reason

The aggregate model answers system-level questions cleanly:

- is there enough hourly supply?
- how sensitive is shortage to transfer?
- what is the value of hydro timing?
- when do candidate limits bind?

### Why not use the network model for everything?

Because a planning-grade spatial expansion model requires:

- future bus-level demand;
- candidate generator locations;
- future line capacities;
- upgrade options;
- upgrade costs;
- calibrated electrical parameters.

Those inputs are not all available.

The project therefore keeps statewide capacity economics and spatial network screening separate, then uses network evidence as a promotion gate.

---

## 11. Why PyPSA?

PyPSA provides transparent open-source linear power-system optimization with:

- chronological snapshots;
- generators;
- storage;
- links;
- network components;
- access to optimization variables/results.

It is well suited to reproducible research.

### Why not PSS/E?

PSS/E is industry-standard for many network studies, but:

- proprietary;
- public reproducibility is lower;
- the limiting factor here is not solver capability but missing operator-grade network data.

CEA's own planning study uses PSS/E and N-1 analysis. Kerala2040 does not pretend to replace that work.

### Why not pandapower for the whole project?

pandapower is appropriate for AC load-flow once calibrated bus injections, impedances and transformer data exist.

Using it with invented parameters would create false physical precision.

---

## 12. Why build a custom SciPy LP if PyPSA was already available?

### Purpose

The custom sparse LP gives a transparent mathematical checkpoint.

### Benefit

It reduces the risk that a surprising result comes from an unnoticed framework convention.

### Why then reproduce in direct PyPSA?

To show that the same mathematical contract behaves equivalently in the intended power-system framework.

### What this proves

Implementation consistency.

### What it does not prove

Physical accuracy.

---

## 13. Why OSeMOSYS as another framework?

OSeMOSYS provides a structurally different energy-system modeling environment.

The common-frontier exercise asks whether results depend on a framework-specific implementation.

Again, shared assumptions mean this is verification, not empirical validation.

---

## 14. Why lexicographic adequacy-first optimization instead of one monetary objective with VOLL?

### Choice

1. minimize unserved energy;
2. preserve that minimum and minimize candidate investment / partial import cost;
3. use later tie-break objectives where needed.

### Reason

A conventional least-cost model requires a Value of Lost Load (VOLL).

No Kerala-specific VOLL was admitted.

Inventing one could cause the monetary trade-off to determine how much load shedding the model “chooses.”

Lexicographic optimization makes the normative choice explicit:

> for this screening exercise, first ask what shortage can physically be avoided; then compare cost among equally adequate solutions.

### Trade-off

This is not a welfare-optimal market model.

It is an adequacy-first research screen.

---

## 15. Why freeze existing hydro/non-hydro generation in early expansion cases?

### Reason

Plant-level:

- heat rates;
- fuel costs;
- availability;
- minimum stable generation;
- maintenance;
- hydro inflow/rule curves

were not sufficiently evidenced.

Replaying the historical aggregate avoids inventing dispatch economics.

### Limitation

It can misrepresent future operating flexibility and retirement/addition behavior.

That is why outputs are not called least-cost plans.

---

## 16. Why use current ATC as a future sensitivity reference?

### Choice

Use source-valued 4,455 MW current ATC plus 80%/60% stress cases.

### Reason

No authoritative future ATC value was found.

CEA provides future import **requirements** and planned transmission additions, but those cannot be converted arithmetically into ATC.

### Why not increase ATC based on line-km/MVA additions?

ATC is a simultaneous system property constrained by:

- topology;
- contingencies;
- voltage;
- thermal limits;
- operating point.

It is not the sum of line ratings.

---

## 17. Why 80% and 60% transfer cases?

They are not predictions.

They are transparent stress factors selected to test whether conclusions depend strongly on transfer availability.

### Why not probabilistic outage distributions?

A probabilistic RA model requires source-supported:

- forced outage rates;
- correlated weather/renewable years;
- demand uncertainty;
- hydro uncertainty;
- transmission outage states.

Those are not admitted.

The deterministic stress cases are simpler and more honest.

---

## 18. Why not report LOLP?

LOLP is fundamentally probabilistic.

The model calculates deterministic chronological:

- unserved MWh;
- shortage hours;
- maximum shortage.

Calling shortage-hour fraction “LOLP” would be wrong.

---

## 19. Why model hydro first as timing windows?

Hydro's distinctive value is flexibility.

v1.1 asks the narrow question:

> If the same observed daily hydro MWh could be scheduled differently within a day, how much could adequacy improve?

This isolates timing from energy quantity.

### Why v1.2?

To test how the result changes when temporal freedom increases across 3/15/30-day windows.

### Why not call these reservoir models?

Because a timing window is not:

- storage volume;
- inflow;
- rule curve;
- head;
- cascade routing.

---

## 20. Why build v1.3 if its water balance is reconstructed?

Because v1.1/v1.2 had no state variable.

v1.3 was a methodological bridge:

- introduce state of charge/storage;
- impose initial/terminal storage;
- constrain power;
- learn how a stateful formulation behaves.

It was intentionally labelled as reconstructed net water balance, not catchment inflow.

### Why is this scientifically useful despite circular closure?

It verifies the stateful optimization machinery before inserting a stronger physical source.

The correct progression was:

**timing bound → stateful pilot → direct-inflow gate.**

---

## 21. Why v1.4/v1.5 fail closed instead of filling missing inflow?

Reservoir inflow is the physical forcing that the model is trying to test.

Interpolating missing inflow to make the model run would undermine the purpose of upgrading from v1.3.

Therefore missing required days stop the physical run.

---

## 22. Why not use the 649.3 km² Idukki catchment area to “fix” the polygon?

Because that would be circular geometry calibration.

A polygon can have the right area and the wrong boundary.

The area is retained as an independent validation target after topology/geography reconstruction.

Rejected candidate catchments are evidence of method failure, not inconveniences to hide.

---

## 23. Why a five-point renewable weather representation?

### Reason

It was a bounded way to introduce Kerala regional weather diversity when full capacity-weighted plant geography was unavailable.

### Why equal weight?

No defensible statewide capacity weighting for both current and candidate fleet was admitted.

Equal weight is explicit and reproducible.

### Why not claim statewide generation?

Because five points cannot capture:

- every microclimate;
- orographic wind;
- panel orientation;
- curtailment;
- technology-specific losses;
- actual fleet distribution.

---

## 24. Why use a generic wind curve?

Manufacturer/turbine fleet data were not available for a hypothetical future statewide portfolio.

A generic curve is suitable for sensitivity chronology, not generation prediction.

The model labels it accordingly.

---

## 25. Why DC/linear network screening instead of AC load flow?

### Available evidence

The project has:

- source-backed topology;
- partial conductor/current evidence;
- historical transformer capacities;
- derived resistance references;
- reconstructed statewide hourly load;
- no measured bus-load chronology;
- no full source-backed branch reactance/shunt set;
- no reactive power / voltage control / generator dispatch chronology.

### Choice

Use a transparent linear screen with explicit assumed X and proxy spatial allocation.

### Why this is scientifically preferable

An AC solve would converge even if the inputs were invented. Convergence is not validation.

### Correct output

“candidate stressed corridors under the public-data screen.”

### Incorrect output

“operator congestion” or “voltage stability.”

---

## 26. Why capacity-weight loads by distribution-transformer MVA?

Measured bus demand was unavailable.

Transformer MVA provides a source-backed proxy for where distribution demand can physically connect.

### Why not population density / nighttime lights?

Those introduce different proxy layers and mapping errors and may not represent industrial/commercial load.

Transformer capacity is directly connected to the electrical infrastructure.

### Limitation

Installed transformer MVA is not demand.

---

## 27. Why allocate unmapped generation without inventing plant locations?

Where generator location is unresolved, the model avoids assigning it to an arbitrary nearest bus.

This is a deliberate bias against false spatial precision.

---

## 28. Why test eight interstate-injection allocations?

Boundary injection location was uncertain.

The robustness envelope includes:

- screening-MVA weighted;
- equal;
- each admitted interface individually.

The single-interface cases are deliberately extreme.

### Why this is useful

A corridor that overloads regardless of where residual import enters is less likely to be an artifact of one chosen boundary split.

### Why it is not full robustness

Other uncertainty dimensions remain untested.

---

## 29. Why not convert line overload directly to upgrade MW?

The screening rating is not an operator emergency rating, and future flows depend on:

- topology upgrades;
- redispatch;
- new generation;
- new load;
- contingency criteria.

Required upgrade size is an optimization/planning problem, not:

```
observed overload - current rating
```

---

## 30. Why include ecology before final optimization?

A technically attractive capacity result is irrelevant if the land/water/site is legally or ecologically unavailable.

Ecology is therefore a **feasibility gate**, not post-processing decoration.

### Why not calculate buildable MW now?

The statutory exclusion stack is incomplete.

Fail closed.

---

## 31. Why use synthetic WP6 pilots?

They answer pedagogy/mechanism questions cheaply and transparently:

- can equal EV energy be moved?
- can industrial optional work be shifted?
- how does storage state evolve?
- how does TES affect cooling electricity timing?

They are not intended to estimate statewide potential.

### Why greedy scheduling instead of optimization?

For a mechanism demonstration, a simple transparent rule is easier to inspect and avoids presenting an artificial optimum from fictional data.

---

## 32. Why include CIAL / Metro / Water Metro?

They provide **real Kerala examples of mechanisms**:

- distributed solar;
- grid exchange;
- storage under development;
- electrified transport;
- high-power charging;
- future renewable integration.

They are not evidence of the cause of statewide stress.

---

## 33. Why translate budgets to SEK?

The intended CET audience may have no intuition for crore rupees.

The conversion is explanatory only.

Every figure should retain:

- INR original;
- project stage;
- source;
- FX date.

### Why not say “Kerala builds cheaply”?

Because early estimates and budget allocations do not prove final cost, speed or quality.

---

## 34. Why not explain the 2026 load-shedding event directly?

Because event attribution needs event data.

The study has enough evidence to ask whether structural vulnerabilities exist, but not enough to reconstruct the operational chain of a specific restriction episode.

### Defense

> “I would rather leave event attribution open than infer it from annual and proxy data.”

---

## 35. Why is the main conclusion phrased as interaction rather than one root cause?

Because the evidence shows several coupled constraints:

- demand timing;
- hydro timing;
- external supply;
- internal deliverability;
- spatial/ecological feasibility.

A single-cause narrative would be simpler but less supported.

---

# The methodological philosophy in one paragraph

Kerala2040 uses a **progressive evidence ladder**. Start with the strongest observable quantity; preserve its accounting boundary; use the simplest transparent model required to answer the next question; expose assumptions; test sensitivities; seek independent external corroboration; and refuse to promote a result when the data required for that promotion are missing. Sophistication is added only when the evidence can support it.
