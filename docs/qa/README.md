# Kerala2040 scientific QA and conference-defense audit

**Branch:** `qa/scientific-validation-conference-20260928`  
**Baseline:** main commit `e850576189bb3f2cd5a0fb092f4dc6f390d3c12f`  
**Audit started:** 28 September 2026  
**Purpose:** adversarial scientific review before CET 2026. This branch is deliberately separate from `main`.

## What this audit is

This is not an attempt to make every existing result look correct. It is a red-team pass designed to identify:

- source errors or stale source vintages;
- accounting-boundary mistakes;
- unsupported causal language;
- calibration/validation leakage;
- circular validation;
- tests that verify implementation but not physical truth;
- assumptions presented too strongly;
- model outputs whose precision exceeds the evidence;
- places where a current authoritative source changes an older interpretation;
- reproducibility gaps;
- claims that should be removed, downgraded or re-run.

A finding that fails this audit is preferable to a weak claim surviving into a conference presentation.

## Validation taxonomy

Every check in this audit must be labelled as one of the following. These are **not interchangeable**.

| Class | What it demonstrates | What it does not demonstrate |
|---|---|---|
| **S1 — source authenticity / provenance** | a value or record can be traced to a named source, date and boundary | that the source is physically correct or current |
| **S2 — arithmetic / conservation / invariant** | transformations conserve quantities or satisfy equations | that the input data or model physics are true |
| **S3 — code / implementation verification** | software implements the intended equations and guards | empirical validity |
| **S4 — independent implementation equivalence** | two implementations/frameworks solve the same mathematical problem consistently | independence of assumptions or physical validation |
| **S5 — statistical out-of-sample validation** | a model predicts/replicates held-out observations not used in fitting | causal identification or operation outside the validation population |
| **S6 — independent physical / external validation** | an independent dataset or engineering study supports the physical inference | proof that every model detail is correct |
| **S7 — planning-grade validation** | calibrated operational data, reliability criteria, contingencies, costs and physical constraints support a decision | currently not achieved by Kerala2040 |

The most important audit rule is:

> **Never describe an S2, S3 or S4 check as “validation” without naming what was actually validated.**

For example, PyPSA ↔ OSeMOSYS agreement is S4 implementation equivalence. It is not evidence that Kerala's future grid will behave like the model.

## Status legend

- **GREEN:** claim is supported for the stated boundary and can be used in the conference.
- **AMBER:** useful result, but only with an explicit qualification.
- **RED:** do not present as a scientific conclusion.
- **P1:** correct before public/conference use.
- **P2:** improve if time permits; does not invalidate the central study.

## Audit documents

1. [SCIENTIFIC_CLAIMS_AUDIT.md](SCIENTIFIC_CLAIMS_AUDIT.md) — claim-by-claim scientific status.
2. [SOURCE_VALIDATION_REGISTER.md](SOURCE_VALIDATION_REGISTER.md) — source, vintage, independence and verification status.
3. [METHODOLOGY_DEFENSE.md](METHODOLOGY_DEFENSE.md) — why each method was used and why common alternatives were not used.
4. [ASSUMPTIONS_AND_UNCERTAINTY_REGISTER.md](ASSUMPTIONS_AND_UNCERTAINTY_REGISTER.md) — explicit assumptions and likely bias directions.
5. [VALIDATION_INDEPENDENCE_AND_CIRCULARITY.md](VALIDATION_INDEPENDENCE_AND_CIRCULARITY.md) — calibration, holdout, leakage and circularity audit.
6. [RED_TEAM_FINDINGS.md](RED_TEAM_FINDINGS.md) — problems found and required corrections.
7. [CONFERENCE_DEFENSE_PLAYBOOK.md](CONFERENCE_DEFENSE_PLAYBOOK.md) — concise answers to likely expert questions.
8. [REPRODUCIBILITY_AUDIT.md](REPRODUCIBILITY_AUDIT.md) — what can be regenerated from the repository and what is only integrity-verifiable.
9. `claims_matrix.csv` — machine-readable claim/status register.

## Current high-level verdict

The project is scientifically defensible **as a public-data diagnostic and screening study** if its evidence classes are respected.

The strongest parts are:

- historical source/accounting discipline;
- preserving missingness and contradictory source records;
- separation of alternative official demand scenarios;
- fail-closed ecology/catchment admission;
- the finding that chronology and hydro timing matter in the model;
- sensitivity to interstate transfer assumptions;
- public-grid topology reconstruction;
- explicit separation of screening from calibrated AC/N-1 analysis.

The most important weaknesses are:

1. the ERA5-sensitive hourly load model is a **shape reconstruction conditional on known daily energy**, not an hourly load forecast;
2. the v1.3 Idukki historical storage replay closes **by construction**, not by independent hydrological validation;
3. renewable hourly profiles are screening proxies and contain calibrated/anchored assumptions;
4. cross-solver agreement is mathematical implementation evidence only;
5. network congestion magnitudes depend on spatial load/generation assumptions and screening electrical parameters;
6. the 2023 **100 MVA Shornur transformer evidence is stale for a current 2026 interpretation**: the 2026 CEA transmission plan reports 200 MVA + 100 MVA at Shoranur while independently identifying the station as constrained;
7. no result supports a validated least-cost 2040 investment portfolio or an event-level causal explanation of a specific 2026 load-shedding episode.

## Conference-safe one-sentence description

> **Kerala2040 is an evidence-first public-data screening study that reconstructs Kerala's recent electricity balance and chronology, stress-tests the roles of hydropower timing, interstate transfer and internal transmission, and uses those results to identify—not prescribe—candidate directions for deeper planning analysis.**

## Stop rule

No new scientific claim is admitted during QA merely because it makes the story stronger. New evidence may:

- confirm a claim;
- narrow it;
- invalidate it;
- or require a re-run.

The audit is complete only when every headline claim has a named evidence class, an independence assessment, a source vintage, and a safe conference wording.
