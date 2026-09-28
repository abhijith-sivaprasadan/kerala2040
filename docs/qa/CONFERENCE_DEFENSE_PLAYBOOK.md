# CET 2026 conference defense playbook

This is not a script to memorize word-for-word. It is a set of **clean scientific answers** that keep evidence classes straight when an expert pushes on the project.

## The 30-second explanation

> “Kerala2040 is a public-data diagnostic of Kerala's electricity system. I first reconstructed the historical balance and a bounded hourly chronology, then tested three mechanisms that could make the system vulnerable: timing of demand and hydro, availability of interstate transfer, and internal transmission deliverability. I then treated land/ecology and economics as feasibility gates and used small synthetic experiments only to identify response mechanisms worth deeper study. The result is not a final 2040 plan; it is a structured diagnosis of what matters and what data are still needed before making one.”

## The one-sentence contribution

> “The contribution is not a new solver; it is a source-audited evidence chain that shows which conclusions survive fragmented public data and which conclusions must remain fail-closed.”

---

# Research design

### Q: What is your actual research question?

**Answer:**

> “Why is Kerala susceptible to electricity shortages and peak-hour supply restrictions, and what structural and operational factors determine whether the system can meet demand under stress? The 2040 question follows from that: once those vulnerabilities are identified, which interventions deserve deeper modelling?”

### Q: Isn't that too broad?

> “It would be too broad if every workstream were treated as an equal causal claim. I reduced it to a hierarchy. The core diagnosis is demand chronology, hydro flexibility, interstate transfer and internal deliverability. Ecology and finance constrain solutions. Industry and transport examples are context. The project explicitly does not claim to solve all of them at once.”

### Q: What is the hypothesis?

> “My working synthesis is that Kerala's susceptibility to stress is an interaction problem rather than a simple annual-energy deficit: weather-sensitive peak timing, hydropower timing and availability, external transfer, and internal network deliverability can all become binding under different conditions.”

Say **working synthesis / screening hypothesis**, not proven causal law.

### Q: What would falsify that hypothesis?

A good answer:

> “If measured interval data showed that restrictions consistently occurred while dependable generation, import capability and internal network headroom were all ample, then my current mechanism set would be incomplete. Likewise, if calibrated network studies showed none of the screened corridors were stressed, the spatial inference would have to be revised.”

---

# Data and historical baseline

### Q: Why trust the SLDC data?

> “I don't trust it blindly. I preserve the source date, section, missingness and accounting boundary. Contradictory dates are flagged or excluded. Daily generation plus imports matching consumption is only an accounting check, not independent validation. I also compare annual trends against separately published state statistics rather than forcing them to match.”

### Q: Why do your SLDC annual totals differ from Economic Review totals?

> “Because they are different accounting boundaries. Even a complete SLDC year can differ from state-consumer consumption. Rather than apply an unexplained correction factor, I keep the boundaries separate.”

### Q: Why not fill the 11 missing FY2024–25 days?

> “For observed analyses I don't. They stay missing. For the 8,760-hour model only, the missing daily totals are explicitly model-only/interpolated and flagged. That prevents the convenience of a complete simulation from rewriting the source record.”

---

# Hourly demand and weather

### Q: You do not have hourly telemetry. How can you run an 8,760-hour model?

> “It is a reconstruction, not telemetry. I conserve the observed daily MWh exactly on 354 days and only reconstruct the intraday shape using reported extrema, clock time, weekend structure and ERA5 weather. The distinction is explicit in the data classification.”

### Q: Then what does your 124.9 MW MAE mean?

> “It is the MAE on held-out reported intraday extrema, conditional on knowing that day's total energy. It validates the shape reconstruction, not a day-ahead hourly load forecast.”

This is one of the most important answers to get exactly right.

### Q: Is that data leakage because daily energy is known?

> “It would be leakage if I claimed to forecast daily demand. I don't. Daily energy is intentionally treated as an observed constraint; the validation target is intraday shape. The held-out extrema themselves were not used for fitting.”

### Q: Why ERA5 instead of weather stations?

> “ERA5 gives spatially and temporally complete, reproducible weather variables. It is reanalysis, not a station measurement. If a quality-controlled Kerala station network with consistent timestamps and coverage becomes available, it would be preferable for local validation.”

### Q: Your weather coefficients show temperature causes demand?

> “No. They are associational shape coefficients. I do not interpret them as causal elasticities because weather, season, behavior and clock time are correlated and the series is daily-normalized.”

### Q: Why not use machine learning / LSTM / XGBoost?

> “Those methods need a dense hourly target series to justify their complexity. I only have sparse extrema and daily energy. A complex supervised hourly model would give false precision. I used the simplest model compatible with the observations.”

---

# Future demand

### Q: Why are your 2030 scenarios so different?

> “Because the source studies are different. I keep CSTEP and CEA/KSERC trajectories separate instead of averaging them. Their disagreement is itself uncertainty.”

### Q: Why affine-morph the historical curve?

> “The official future studies provide annual energy and peak, not 8,760 values. The affine morph preserves chronology while exactly matching those two source anchors. It is a scenario transformation, not a forecast of future hourly behavior.”

### Q: What about EVs and air conditioning changing the shape?

> “Exactly. That is one reason the future chronology is a scenario, not a prediction. Structural load-shape change is future work and is partly why the WP6 flexibility pilots were kept separate.”

---

# PyPSA / OSeMOSYS / optimization

### Q: Why PyPSA?

> “It is open, transparent, chronological and reproducible. The problem did not require a proprietary solver; the limiting factor was evidence. I also reproduced the common formulation outside PyPSA to reduce framework-specific implementation risk.”

### Q: So OSeMOSYS validated PyPSA?

> “It verified implementation equivalence under shared assumptions. It did not validate Kerala. Both models can agree and still share the same wrong input.”

### Q: Why not use PLEXOS, TIMES or PSS/E?

> “Each is useful for a different question. PSS/E is appropriate for planning-grade AC/network studies and CEA itself uses it, but I did not have operator-grade bus injections and complete parameters. TIMES/OSeMOSYS are strong for energy-system planning but don't remove the input-evidence problem. I chose open tools and kept the model no more detailed than the data.”

### Q: Why no unit commitment?

> “I do not have reliable plant-level minimum output, ramping, startup, heat-rate and outage data for the whole Kerala-relevant fleet. Adding unit commitment with guessed parameters would look sophisticated while weakening provenance.”

### Q: Why no probabilistic reliability / LOLP?

> “The model is deterministic chronological screening. Proper LOLP needs distributions for forced outages, multiple weather years, hydro uncertainty and demand uncertainty. I report unserved MWh and shortage hours, not LOLP.”

### Q: Why minimize unserved energy before cost?

> “Because I did not have a Kerala-specific Value of Lost Load. A single monetary objective would make an arbitrary VOLL decide how much shortage is economically acceptable. I chose an explicit adequacy-first lexicographic objective and label the economics partial.”

### Q: Then this is not a least-cost plan?

> “Correct. It is a partial economic expansion screen, not a total-system least-cost plan.”

---

# Imports and transfer

### Q: Are electricity imports a weakness?

Best answer:

> “Not inherently. Interconnection is economically valuable and normal. The vulnerability is dependence on a quantity of external supply that may not always be available at the required hour or through the required transfer path. The question is dependable access, not autarky.”

### Q: Why use 4,455 MW?

> “CEA's dated 31 March 2026 transmission plan reports TTC 4,575 MW and ATC 4,455 MW for Kerala. I use 4,455 as a current screening reference, not as a guaranteed future capability.”

### Q: Why 80% and 60%?

> “They are transparent stress cases, not forecasts. I wanted to test how strongly adequacy conclusions depend on external transfer.”

### Q: Why not derive future ATC from planned transmission additions?

> “Because ATC is a simultaneous system property under topology, contingency and operating conditions. MVA additions or future import requirement cannot be added arithmetically to today's ATC.”

### Q: Are your import costs hourly market prices?

> “No. The current economics use source-derived flat benchmark cases: an annual KSEBL procurement cost, an IEX DAM benchmark and a higher delivered-cost stress case. That is why I call it partial economics.”

---

# Hydropower

### Q: Your 96.9% reduction from hydro flexibility sounds implausibly large.

> “It is large, and it should not be generalized. The experiment holds daily hydro energy fixed and asks what happens if its timing is optimized within the day. In the high-transfer reference case the shortage is predominantly a timing problem, so shifting the same MWh has high value. Under tighter transfer, the benefit collapses. That contrast is the scientific result.”

### Q: Does v1.1 mean KSEB can actually dispatch hydro that way?

> “No. v1.1 is an upper-bound timing sensitivity. It does not contain reservoir inflow, cascade routing, minimum releases, rule curves or head-dependent efficiency.”

### Q: Why use 3, 15 and 30-day windows?

> “They are synthetic temporal brackets. They test when additional interday freedom stops helping. They are not reservoir storage durations.”

### Q: Is v1.3 a real reservoir model?

> “It is a stateful reservoir pilot, but not a validated hydrology model. The water forcing is a reconstructed net balance from storage change and generation.”

### Q: But the v1.3 historical storage closes exactly. Isn't that validation?

This answer matters:

> “No. It closes algebraically by construction. The net-balance term is calculated from the same storage change and generation that are replayed. That check validates the state equation and date alignment, not the hydrology. I explicitly built v1.4/v1.5 gates to replace that term with direct inflow data.”

### Q: Why is 1,470 MWh/MCM used?

> “It is a source-derived energy-equivalent ratio from reported station generation capability and effective storage, used as a fixed conversion in the pilot. It is not a first-principles head/efficiency curve.”

### Q: Why haven't you modeled the Idukki catchment yet?

> “Because the geometry is not defensibly admitted. Several plausible reconstructions gave areas from roughly 350 to more than 1,300 km² against the independent 649.3 km² reference. Instead of tuning a polygon to the target area, I rejected them and kept Phase 5 closed.”

That answer will generally impress a hydrologist more than pretending the catchment is solved.

---

# Transmission

### Q: Why call it a network screen rather than a grid model?

> “I have source-backed topology and partial equipment evidence, but not measured bus loads, unit dispatch, complete source impedances, reactive-power data or N-1 operating states. So I use a linear screening model and deliberately avoid the term calibrated grid model.”

### Q: Why no AC power flow?

> “An AC solver with invented inputs would still converge. The limiting factor is data, not the nonlinear equations. CEA's official planning analysis uses PSS/E, N-1, voltage and short-circuit studies; my role is a reproducible public-data screen.”

### Q: Why generic reactance values?

> “Conductor identity alone does not determine positive-sequence reactance. Where source values were unavailable I used explicit voltage-class screening assumptions. That is one reason I interpret geography more strongly than exact loading magnitude.”

### Q: Why allocate load by transformer MVA?

> “There is no public hourly substation-load dataset. Distribution-interface transformer MVA is electrically grounded source evidence of connection scale. It is still only a proxy.”

### Q: Why not use population/nighttime lights instead?

> “Those would add a different proxy that can badly miss industrial/commercial loads. Transformer capacity has a direct electrical-system relationship. Ideally measured bus load would replace all of them.”

### Q: What does “21 robust lines” mean?

> “Only that the same 21 source-rating-backed lines exceed their screening rating in every one of eight boundary-injection allocation cases. It does not mean robust to every uncertainty in the model.”

### Q: Did you discover Shornur congestion independently?

The honest answer after QA:

> “My public-data screen independently highlighted Shornur geographically, but the original transformer magnitude used a 2023 100 MVA equipment snapshot. During QA I found the current 2026 CEA plan reports 200+100 MVA at Shoranur and independently identifies the station and nearby corridors as constrained. So I retain the hotspot conclusion but I do not defend my 100 MVA overload ratio as a current station-loading estimate.”

This is a very strong answer because it demonstrates actual scientific correction.

### Q: Doesn't that invalidate your network work?

> “It invalidates the current interpretation of one transformer rating, not the whole topology or line screen. More importantly, the independent CEA plan corroborates several hotspot locations. The QA result tells me which part to downgrade: magnitude, not the entire geographic signal.”

### Q: Can you say “grid stability”?

> “No. My model does not assess transient, small-signal, frequency or voltage stability. I use ‘network congestion/deliverability screening’ or ‘power-system stress.’”

---

# Ecology / GIS

### Q: Why include ecology in a power-system project?

> “Because a capacity result is not implementable if the site is legally or ecologically unavailable. Ecology is a feasibility gate on solutions.”

### Q: How many GW are actually buildable?

> “I do not claim a number yet. The statutory forest/wetland/hazard/setback stack is incomplete. Reporting a number now would be false precision.”

### Q: Isn't that unfinished work?

> “It is an intentionally closed release gate. The completed result is knowing which source layers are valid, which are not, and why the optimization cannot yet be promoted to a spatial investment plan.”

---

# Storage and flexibility

### Q: Does storage save electricity?

> “No. It generally loses energy. It can reduce stress by moving energy from one time to another.”

### Q: Is pumped storage cheap?

> “Not categorically. Kerala has early PSP estimates that are useful for scale, but civil works, tunnelling, environmental constraints and connection costs are project-specific. I call it a candidate flexibility option, not a cheap solution.”

### Q: What do the EV/TES/industry pilots prove?

> “They prove only the mechanism on authored profiles: the same service can sometimes be shifted away from stressed hours. They do not establish statewide Kerala potential.”

---

# Nuclear / thermal / technology choices

### Q: Why didn't you model nuclear or SMRs?

> “I did not exclude them ideologically. The current diagnostic asks what is causing near-term system stress and uses technologies for which I can build a defensible Kerala-relevant screening boundary. A nuclear/SMR pathway would require technology-specific capital cost, construction time, siting, cooling-water, regulatory/federal ownership, unit-size and grid-integration assumptions. Without a credible Kerala project definition, adding an SMR variable would be an invented scenario rather than evidence-based analysis.”

### Q: But nuclear could provide firm power.

> “Yes, firm low-carbon generation is a mechanism worth comparing in a properly defined long-term scenario. My present results do not establish whether nuclear is or is not the best Kerala option.”

### Q: Why not new coal/gas?

> “Same principle. A serious comparison needs fuel-delivery, emissions/policy, project-cost and operating assumptions. The diagnostic study does not need to preselect a technology to show that timing, transfer and network constraints matter.”

---

# Context / Kerala comparisons

### Q: Why compare Kerala with Sweden?

> “Only to make scale intuitive for the CET audience. It is not a performance ranking. Kerala has about 36.2 million projected residents in 2026 and a much smaller area, but very different climate, industry and heating demand. I state those differences explicitly.”

### Q: Why mention culture/landscape?

> “Because geography is part of the engineering boundary. The Western Ghats, monsoon, dense settlement, backwaters, forests and coast directly affect hydro, land availability, hazards and transmission. The cultural introduction is there to give an unfamiliar international audience a place context, not to claim superiority over other Indian states.”

---

# Budgets

### Q: Are those SEK figures project costs?

> “The INR source remains authoritative. SEK is only a dated audience conversion. I also label project stage: budget allocation, early estimate, sanction or completed cost.”

### Q: Are Kerala projects unusually cheap?

> “I don't make that claim. Some early estimates look modest in Swedish currency, but estimates can overrun and project scope differs. The defensible point is that capital constraints make prioritization important.”

---

# Causality and load shedding

### Q: So why did Kerala have load shedding in 2026?

Do not improvise.

> “My current model cannot reconstruct the exact operational cause of a specific 2026 event. I would need interval dispatch, unit outages, interface schedules/flows, market availability, reservoir constraints and internal telemetry. The event motivates the research; the public historical data let me test structural vulnerabilities that could make such an event more likely.”

### Q: Then isn't your title misleading?

> “The title is ‘power system under stress,’ not ‘the proven cause of the September event.’ The research question is susceptibility and structural vulnerability.”

---

# Scientific integrity / AI

### Q: Did you use AI to build this?

A clean answer:

> “Yes, AI tools assisted with coding, source discovery, QA and documentation. I do not use an AI answer as evidence. The evidence layer is primary documents, preserved data, explicit transformations and reproducible code/tests. I remain responsible for every claim, and this QA branch was specifically created to catch circular validation, stale sources and overstatement before presentation.”

Do not hide this if asked. The correct defense is provenance and reproducibility.

### Q: Was this peer reviewed?

> “No. It is an independent research project being presented for technical discussion, not a peer-reviewed system plan. That is why I distinguish screening evidence from validated planning claims and publish the limitations.”

---

# The strongest limitation answer

If an expert asks for “the biggest weakness,” don't give ten small things.

> “The biggest limitation is the lack of operator-grade interval and spatial data. That forces the hourly demand and bus allocation to be reconstructed. I try to make that limitation useful scientifically by testing what survives explicit sensitivity and by refusing AC/N-1 or event-causal claims.”

# The strongest future-work answer

> “The next major upgrade is not another solver. It is better physical evidence: measured interval demand and interface flows, direct Idukki inflow/storage with a verified catchment, current electrical parameters and bus loads, and statutory siting layers. With those, the existing framework can be promoted to probabilistic reliability, calibrated network and investment analysis.”

# What never to say

Avoid these phrases:

- “the model proves”
- “the grid is unstable”
- “Kerala imports X%” unless exact accounting boundary is stated
- “hourly forecast” for the reconstructed FY2024–25 chronology
- “validated by OSeMOSYS”
- “observed Idukki inflow” for the v1.3 net balance
- “Shornur is a 100 MVA station” as a current statement
- “17 MW solar installed at Water Metro”
- “buildable renewable potential”
- “optimal 2040 solution”
- “pumped storage is cheap”
- “storage saves electricity”
- “we found the cause of the 2026 load shedding”

# The sentence to use when you don't know

> “I don't have evidence to answer that at the required boundary, so I kept it outside the claim. The data I would need are …”

That is a better scientific answer than guessing.
