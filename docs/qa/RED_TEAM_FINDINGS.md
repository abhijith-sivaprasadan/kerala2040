# Red-team findings and required corrections

## P1 — Shornur transformer capacity: current interpretation must be corrected

### Existing Kerala2040 evidence

The frozen KSEBL *Power System Statistics 2022–23* indexed-text snapshot contains:

> Shornur, 220/110 kV, 100 MVA × 1 = 100 MVA.

The network robustness model consequently tested a 100 MVA historical PSS-backed transformer link and found it overloaded in all eight boundary-injection cases.

### New independent authoritative check

The CEA *Resource Adequacy Plan for Transmission System of Kerala up to 2034–35* describes **existing 2026 Shoranur 220-kV transformation as 200 MVA + 100 MVA**, identifies it as a present transmission constraint, and records a proposed additional 200 MVA transformer / load rearrangement.

The same CEA study independently identifies multiple lines in the Shornur / Palakkad / Malappuram area for reinforcement.

### Scientific consequence

The result must be split into two claims:

**Supported:**  
Shornur/Shoranur is a real current transmission-planning hotspot. This is independently corroborated by CEA, and the Kerala2040 line-screen geography overlaps several official reinforcement corridors.

**Not supported:**  
The 100 MVA model link is the full current 2026 Shornur station capacity, or its 1.356–2.670 pu modeled loading is a current operator loading estimate.

### Required action

Before conference/public reuse:

- downgrade all wording that treats 100 MVA as current whole-station capacity;
- identify it as **historical 2023 PSS equipment evidence**;
- cite the current CEA 200+100 MVA station description;
- use the CEA planning result as independent external corroboration of the **location**, not numerical validation of Kerala2040 loading;
- do not aggregate 200+100 into a synthetic 300 MVA model and claim the problem vanishes without verifying busbar/parallel-operation topology.

**Status: P1.**

---

## P1 — ERA5 load reconstruction must not be described as a forecast

The Jan–Mar extrema are a valid held-out shape test, but every day's total MWh is already known and enforced.

Required wording:

> “held-out intraday-shape reconstruction conditional on observed daily energy.”

Never:

> “hourly load forecast MAE = 124.9 MW.”

**Status: P1 wording correction.**

---

## P1 — v1.3 Idukki closure is algebraic

The v1.3 net-water-balance forcing is reconstructed from storage change and generation. Replaying those same terms necessarily closes the historical storage equation.

Required wording:

> “state-equation implementation / arithmetic closure.”

Never:

> “v1.3 reservoir hydrology was validated because storage closed.”

The physical-source gates v1.4/v1.5 should be described as the deliberate remedy.

**Status: P1 interpretation correction.**

---

## P1 — Cross-solver agreement is not physical validation

PyPSA, SciPy and OSeMOSYS comparisons establish formulation / implementation equivalence under common assumptions.

Never present numerical equivalence as independent evidence for Kerala's physical system.

**Status: P1 terminology correction.**

---

## P1 — Network “robust” has a narrow definition

The 21 robust lines are robust to eight **boundary-injection allocation cases**. They are not demonstrated robust to all spatial load, generator dispatch, impedance, rating or contingency uncertainty.

Required wording:

> “robust to the tested boundary-allocation envelope.”

**Status: P1 wording precision.**

---

## P1 — Exact 2026 load-shedding causality is not established

Current public evidence does not include a complete event-level set of:

- interval demand;
- unit dispatch;
- outages;
- interface schedules/actual flows;
- market availability/prices;
- reservoir constraints;
- internal bus/branch telemetry.

The 2026 episode can motivate the study, but the model cannot claim to have reconstructed its exact cause.

**Status: P1 guardrail; already mostly respected.**

---

## OPEN DISCLOSED LIMITATION — ERA5-sensitive v2 fit is not end-to-end public-repo reproducible

The audit checked PR #110 and PR #113 as well as the current tree. The repository contains the checksummed v2 compact chronology, loader, conservation/integrity tests, methodology note and source fingerprints, but **the original v2 fitting script was never committed in either integration PR**.

Therefore:

- released 8,760 values and downstream model use are **R1 integrity reproducible**;
- the older fixed-shape proxy is regenerable;
- the v2 clock/weather coefficient fit and Jan–Mar holdout metrics are **not source-to-fit reproducible from a fresh clone**;
- the raw ERA5 archive is also intentionally absent, though its SHA-256 is recorded.

This does not invalidate the released chronology, but it is a real reproducibility limitation. The public README has been narrowed accordingly.

Do not create a new fitter after the fact and call it the original unless it reproduces the pinned coefficients, metrics and payload from the recorded source archive.

**Status: OPEN but fully disclosed; non-blocking for conference screening claims, blocking for a “fully reproducible from clone” claim.**

---

## P2 — Wind annual “validation” is partly anchored

The wind chronology's long-term mean is forced to NIWE mean wind speed. NIWE cannot then be used as an independent validation of the annual mean.

Independent validation would require measured wind-farm/turbine generation or mast/LiDAR observations at compatible locations/heights.

**Status: P2; current proxy label is appropriate.**

---

## CLOSED — CEA cost and CERC finance source units independently re-verified

The exact cost/finance values used in v0.5 have now been re-checked against the primary documents.

CEA *Optimal Generation Capacity Mix for 2029–30, Version 2.0* states that the financial assumptions are at **2021–22 cost level**, with solar **₹4.5→4.1 Cr/MW**, onshore wind **₹6 Cr/MW**, and 4-hour BESS **₹8.22→4.72 Cr/MW**. These convert exactly to the repository's ₹41,000/kW solar, ₹60,000/kW wind and ₹47,200–82,200/kW BESS bracket. The technical table states **12% BESS round-trip losses**, matching 88% round-trip efficiency.

CERC Order **12/SM/2026 dated 23 August 2026** states 70:30 debt/equity, 10.71% loan interest, 14% post-tax RoE for non-small-hydro RE and explicitly derives a **9.08% post-tax WACC-equivalent discount factor** for non-SHP technologies.

These remain **national planning/regulatory benchmarks**, not realized Kerala project costs or a Kerala project-specific WACC.

**Status: CLOSED / GREEN source verification.**

---

## P2 — Import price cases are deliberately heterogeneous boundaries

The three v1.0 prices are not three observations of the same “Kerala import price”:

- KSEBL weighted purchase cost — annual procurement accounting;
- IEX DAM — exchange market-clearing benchmark;
- high delivered bulk case — a downstream Kerala licensee boundary.

They are valid as stress/reference cases if described that way.

Do not call the 7.13 ₹/kWh case the Kerala-border import tariff.

**Status: P2 wording.**

---

## P2 — Renewable candidate capacity envelopes are scenario ceilings, not buildable potential

Ground PV, floating PV and wind limits mix published technical/scenario studies with different methods and vintages.

The model correctly treats them as low/reference/high research envelopes.

Do not sum them and call the result “Kerala's renewable potential.”

**Status: P2 communication.**

---

## CLOSED WITH LIMITATION — 1,460 MCM / 1,470 MWh/MCM provenance

The retained SLDC source rows directly report Idukki full reservoir storage as **1,460 MCM** and full reported capability as **2,190 MU**, giving **1,500 MWh/MCM gross** by arithmetic.

The v1.3 code instead uses the median of source-reported **station generation capability / effective storage**. Independent QA recomputation across all 354 Idukki rows gives **1,470.00001987 MWh/MCM**, reproducing the configured 1,470 value.

The provenance is therefore sound. The physical interpretation remains limited: 1,470 is a source-derived **station energy-equivalent approximation**, not a derivation from head, turbine efficiency, tailwater or penstock losses.

**Status: CLOSED provenance / AMBER physical approximation.**

---

## Items that passed the red-team review well

### Accounting boundaries

The project repeatedly refuses to divide or merge values from different official accounting boundaries. This is good practice.

### Missingness

Missing days remain explicit; contradictory dates can be excluded rather than forced into the record.

### Catchment reconstruction

Multiple geometries were rejected rather than tuned to a desired 649.3 km² target.

### GIS

No incomplete protected-area / forest / wetland layer is converted into a legal buildable-MW result.

### Future ATC

The project refuses to treat future import requirement or added MVA/circuit-km as future ATC.

### WP6

Synthetic flexibility experiments are clearly identified as mechanism demonstrations.

### Storage language

The revised public story states correctly that storage shifts energy and incurs losses; it does not “create” electricity.
