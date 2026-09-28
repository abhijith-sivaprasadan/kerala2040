# Validation independence, leakage and circularity audit

## Why this document exists

Kerala2040 uses many internal QA checks. A model can pass every unit test and still be physically wrong. This document separates **verification** from **validation**, and identifies where an apparent validation target is mathematically or statistically dependent on the model input.

## 1. Historical daily electricity balance

### Check

For qualified SLDC dates:

```
internal generation + net imports ≈ consumption
```

### Classification

**S2 — accounting conservation.**

### Independence

Low. All terms originate within the same daily reporting/accounting system.

### Correct use

- detect transcription and parsing errors;
- detect dates whose reported tables do not reconcile;
- reproduce daily accounting.

### Incorrect use

Do not say:

> “Imports are independently validated because imports plus generation equal consumption.”

That equation is the accounting definition of the daily balance. It is not an independent measurement validation.

## 2. ERA5-sensitive hourly load reconstruction

### Construction

The released FY2024–25 hourly chronology:

1. uses SLDC daily consumption totals;
2. fits clock-time structure from selected April–December 2024 SLDC extrema;
3. adds weekend and ERA5 weather terms;
4. renormalizes each day to its known daily energy;
5. uses January–March 2025 reported extrema as the held-out shape test;
6. separately compares the reconstructed annual peak with a CEA peak reference.

### What the Jan–Mar holdout validates

The 430 held-out extrema are not used to fit the intraday coefficients, so the comparison is a legitimate **S5 out-of-sample validation of intraday shape conditional on each day's total energy**.

It is not a load forecast.

The daily total for each held-out date remains known and enforced by construction. Therefore the model is answering:

> Given the day's total electricity use, how well can clock-time + weather reconstruct where within the day the reported extrema occurred in MW?

It is **not** answering:

> Could we have forecast tomorrow's 24 hourly MW values without knowing tomorrow's total consumption?

### Leakage/circularity assessment

- **Daily energy:** fully constrained by the target source. Cannot be used as independent validation.
- **Apr–Dec extrema:** fitting/calibration data.
- **Jan–Mar extrema:** valid temporal holdout for shape, provided no Jan–Mar extrema entered feature fitting.
- **CEA annual peak:** external aggregate check, but if peak was itself used as a calibration constraint in the fit it is not an independent validation metric for the same model.
- **ERA5:** independent weather input, but associations are not causal coefficients.

### Conference wording

Safe:

> “We reconstructed an hourly shape while conserving observed daily energy. On held-out Jan–Mar reported extrema, adding ERA5 weather improved RMSE by about 4% relative to an already strong clock-time-only reconstruction.”

Unsafe:

> “The model predicts hourly Kerala demand with 125 MW MAE.”

## 3. ERA5 solar profile

### Construction dependence

The PV proxy uses ERA5 shortwave radiation, a fixed performance ratio, a simple cell-temperature relationship and temperature coefficient.

### Validation anchors

- Global Solar Atlas annual PV yield is an independent modeled climatology, not a plant measurement.
- Annual energy from named solar plants is an empirical annual sanity check when source boundaries are compatible.
- No hourly plant-generation validation exists.

### Circularity status

GSA is not used to force the ERA5 annual PV energy in the current documented method, so comparison to GSA is not strictly circular. However, both are weather/resource models and therefore not equivalent to empirical plant validation.

## 4. ERA5 / NIWE wind profile

### Construction dependence

ERA5 10 m wind is extrapolated to 150 m with assumed shear and then **mean-anchored to the NIWE 150 m long-term mean** at each representative location before applying a generic turbine curve.

### Consequence

Any comparison of the resulting annual mean wind speed back to the same NIWE mean is circular.

The NIWE value is a calibration/anchor input, not an independent validation target.

No measured turbine/farm hourly generation is available in the admitted evidence.

### Conference wording

Safe:

> “The wind chronology is a NIWE-anchored ERA5 screening shape with a generic turbine curve.”

Unsafe:

> “ERA5 wind was validated against NIWE.”

## 5. PyPSA no-additions daily replay

If daily source energy is imposed and the model is required to reproduce the same daily balance, exact reproduction verifies the model formulation and data alignment.

Classification: **S2/S3**, not independent physical validation.

It demonstrates that the solver does not lose or create energy in the accounting formulation.

## 6. PyPSA ↔ SciPy equivalence

The custom LP and direct PyPSA implementation share:

- the same load chronology;
- the same candidate constraints;
- the same cost assumptions;
- the same transfer assumptions;
- the same optimization objective family;
- the HiGHS solver family.

Agreement therefore demonstrates **S4 independent-framework implementation equivalence**.

It is useful because a framework-specific coding mistake becomes less likely.

It does not provide independent evidence for:

- demand;
- renewable availability;
- storage costs;
- import capability;
- physical reliability.

## 7. PyPSA ↔ OSeMOSYS equivalence

The same principle applies.

OSeMOSYS and PyPSA are distinct modelling frameworks, but if both are deliberately constrained to the same common mathematical contract and both use HiGHS, close agreement is evidence that the contract was implemented consistently.

It is not model validation in the empirical sense.

## 8. Hydro v1.1 and v1.2

These are counterfactual timing experiments.

- v1.1 preserves each day's hydro energy exactly and redistributes it within the day.
- v1.2 preserves hydro energy over progressively longer synthetic windows.

The results are valid answers to:

> “Under these energy and power constraints, how much does additional temporal freedom reduce shortage in this model?”

They do not validate:

- reservoir hydrology;
- rule curves;
- water-value economics;
- cascading reservoirs;
- flood control;
- actual operator feasibility.

There is no circular “validation” problem because they are explicitly sensitivities, not attempts to reproduce observed dispatch.

## 9. Idukki v1.3 — the most important circularity case

The v1.3 water forcing is constructed as:

```
B[t] = S[t+1] - S[t] + G[t] / c
```

where:

- `S` is the storage series;
- `G` is Idukki generation;
- `c` is a fixed MWh/MCM conversion;
- `B` is the reconstructed net non-generation water-balance term.

Historical replay then computes:

```
S[t+1] = S[t] + B[t] - G[t] / c
```

Substitution makes the observed storage change reappear algebraically.

Therefore the near-zero terminal replay residual is **guaranteed by construction**, apart from interpolation/numerical error.

### What it verifies

- date alignment;
- arithmetic;
- state-equation coding;
- storage-unit implementation.

### What it does not verify

- catchment inflow;
- spill;
- downstream releases;
- evaporation/diversion;
- hydraulic head;
- turbine efficiency;
- reservoir operating policy.

This is why v1.4 and v1.5 were designed to replace the reconstructed forcing with source-reported inflow/storage data.

### Conference wording

Safe:

> “v1.3 was a stateful reservoir pilot using a reconstructed net balance. Its historical closure is an algebraic verification, not hydrological validation. I therefore built v1.4/v1.5 gates specifically to require direct inflow data before making a physical reservoir claim.”

That is a strong scientific answer because it shows the limitation was recognized and the methodology evolved to remove it.

## 10. Idukki Phase 4 regression

The Phase 4 ridge model uses same-day rainfall `t`, rainfall lags and previous-day reported inflow.

Therefore:

- the chronological 2025–2026 holdout is a real temporal holdout;
- comparison against persistence is fair on the same complete-case dates;
- using rainfall at `t` makes it a **retrospective diagnostic**, not a one-day-ahead forecast;
- missing gauge data create complete-case selection bias.

The reported 37.24% MAE reduction is valid only for that selected retrospective held-out sample.

## 11. Phase 5 catchment reconstruction

The external 649.3 km² catchment figure is explicitly used as a validation target and **not** as a fitting parameter. Multiple candidate geometries that disagree are rejected rather than tuned.

This is good anti-circular methodology.

No basin-average ERA5 analysis should proceed until an independently sourced catchment geometry passes the gate.

## 12. Network topology and bottleneck robustness

The eight boundary-allocation cases vary only the location of the residual interstate injection.

A line overloaded in all eight cases is robust to **that uncertainty dimension only**.

It is not robust to all of:

- bus-load allocation;
- generator dispatch;
- line ampacity error;
- branch reactance;
- network topology errors;
- station configuration;
- contingency outages;
- reactive power / voltage.

The phrase “robust bottleneck” must always be understood as:

> “robust to the tested boundary-injection allocation envelope under the public screening model.”

## 13. Shornur transformer

The model's historical PSS evidence used a 31 March 2023 snapshot containing a 100 MVA Shornur 220/110-kV transformer entry.

The 2026 CEA transmission resource-adequacy plan reports current Shoranur 220-kV substation transformation as **200 MVA + 100 MVA**, identifies transformer loading as a constraint, and proposes an additional 200 MVA transformer.

Therefore:

- CEA independently corroborates **Shoranur as a constrained location**;
- the Kerala2040 quantitative 100 MVA overload ratio is not a current station-capacity validation;
- it is unsafe to call the 100 MVA link “the current Shornur station capacity.”

This is an example where independent external validation strengthens the geographic conclusion while invalidating an overly literal interpretation of the model rating.

## 14. WP6 storage / EV / industry / cooling

These use authored synthetic profiles.

Internal invariants such as “same EV energy delivered” or “same industrial work completed” verify service conservation.

They do not validate statewide peak reduction.

Correct class: **mechanism demonstration / synthetic experiment**.

## 15. General rule for conference answers

When asked “How did you validate this?” answer with the exact class:

- “I verified the source and hash.”
- “I checked conservation.”
- “I reproduced the result in a second implementation.”
- “I tested it out of sample.”
- “I cross-checked it against an independent CEA engineering study.”

Avoid the single unqualified word **validated**.
