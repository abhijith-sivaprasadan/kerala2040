# Kerala2040 — next steps after the diagnostic modelling phase

**Updated:** 28 September 2026

## Current status

The project has enough modelling to support a defensible **public-data diagnostic and screening study** of Kerala's electricity system.

The scientific centre is now:

> **Why is Kerala susceptible to power-system stress, what structural weaknesses make that stress more likely, and which responses deserve deeper testing?**

The answer is not a single technology. Current evidence points to the interaction of:

- demand growth and weather-sensitive peaks;
- dependence on external electricity and transfer capability;
- hydropower timing and reservoir constraints;
- internal transmission deliverability;
- land/ecological constraints on new infrastructure.

See [POWER_SYSTEM_STRESS_SYNTHESIS_2026_09_28.md](POWER_SYSTEM_STRESS_SYNTHESIS_2026_09_28.md).

## Modelling freeze

**Do not add another model family before the CET/public release unless it uses genuinely new evidence or could change a material conclusion.**

The work now has more value from synthesis and communication than from another sensitivity layer.

### One technical closeout still in progress

PR #122 propagates the robust KSEBL network evidence into the current PyPSA and OSeMOSYS planning gates. Its final scientific content is already defined; remaining work is CI/integration closeout rather than new modelling.

Once that integration is green and merged, treat the current model stack as frozen for this release.

## Mandatory work before release

### 1. Align the public story

Update the README, website and poster around one sequence:

**Meet Kerala → understand the electricity system → diagnose stress → understand constraints → examine candidate responses → inspect the evidence.**

Avoid making KMML, storage pilots, solar/wind resources or individual model versions compete with the main research question on the homepage.

### 2. Publish the findings hierarchy

The public summary should make these distinctions obvious:

- **Observed:** official / SLDC records.
- **Derived:** calculations or reconstructed chronology tied to observed totals.
- **Screening result:** model mechanisms and sensitivities.
- **Candidate response:** educational interpretation that still needs validation.

### 3. Add accessible context

Use [KERALA_CONTEXT_FOR_SWEDISH_AUDIENCE_2026_09_28.md](KERALA_CONTEXT_FOR_SWEDISH_AUDIENCE_2026_09_28.md) to give unfamiliar readers scale without boasting or caricaturing India.

Useful context includes:

- population and land area;
- per-capita and total electricity use;
- Western Ghats, monsoon, coast/backwaters and dense settlement;
- monazite-bearing heavy-mineral sands as industrial-geology context;
- CIAL, Kochi Metro and Kochi Water Metro as transition examples;
- INR project budgets with dated SEK equivalents.

### 4. Explain "symptom management vs structural vulnerability"

Use neutral engineering language.

The research question is not whether emergency procurement or temporary operating measures are "bad." They can be rational. The question is:

> **When is a short-term response economical, and when does repeated dependence reveal a structural constraint that is better addressed through a durable investment or operating change?**

### 5. Present preliminary solutions carefully

The conclusion may say that early-stage work makes several directions worth deeper study:

- better hydro scheduling and forecasting;
- demand response and time-of-use signals;
- managed EV charging;
- cooling / thermal storage;
- BESS;
- pumped storage where project-specific civil/ecological conditions support it;
- targeted network reinforcement;
- selectively sited renewable generation;
- dependable interstate procurement and transfer capability.

Do not call these an optimal plan. Do not say storage creates or saves energy. Do not call pumped storage inherently low-cost.

### 6. Final QA and release

Before the final CET/public snapshot:

- run repository CI;
- run browser/site smoke tests;
- ensure all model and source guardrails still pass;
- check links and downloads;
- freeze a specific research commit;
- synchronize the public site deliberately;
- pin poster/website sources to the same evidence boundary where practical.

## What is explicitly not required before release

The following are valuable research extensions, but **not blockers** for the current diagnostic publication:

### Idukki Phase 5 physical hydrology

Continue only when the catchment is independently reconciled and the inflow boundary is defensible. Then connect catchment rainfall, observed inflow and reservoir operation.

### Official KSEB reservoir workbooks

Run the existing v1.5 pipeline if the exact FY2024–25 monthly source workbooks become accessible. Do not substitute synthetic inputs merely to make the workflow run.

### Calibrated AC / N-1 planning model

Requires stronger electrical parameters, operating states, outage assumptions and future corridor options/costs. The present public network screen is useful without pretending to be this model.

### Legally complete renewable siting

Requires notification-linked forest/wetland/ESZ/coastal/paddy constraints, validated hazard geometry, setbacks, connection rules and land/community feasibility.

### Full least-cost 2040 investment plan

This should come **after** the physical and spatial gates above, not before them.

### Future-climate ensemble

Use a multi-year / multi-model 2031–2050 climate framework rather than choosing one synthetic "2040 weather year."

## Closure rule

Before starting any new workstream, ask:

> **Will this new work change a material conclusion, resolve a known evidence gate, or make the existing result substantially more understandable?**

If the answer is no, it belongs after the current release.
