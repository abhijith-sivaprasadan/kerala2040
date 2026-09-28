# Reproducibility audit

**Audit date:** 28 September 2026

Reproducibility is evaluated separately from source quality and scientific validity.

## Levels

- **R0 — documented only:** prose/number exists but derivation cannot be regenerated from retained artifacts.
- **R1 — integrity reproducible:** released artifact can be byte/hash checked and consumed deterministically.
- **R2 — transformation reproducible:** retained inputs + code regenerate the derived artifact.
- **R3 — source-to-result reproducible:** public acquisition + transformation + model + tests reproduce the result.
- **R4 — independently reproducible:** a separate implementation reproduces the same mathematical result.

## Workstream status

| Workstream | Level | Audit |
|---|---:|---|
| SLDC archive parsing / daily balance | R2/R3 | source archive hashes, parsers and QA retained; upstream live availability can still change |
| annual historical accounting | R2 | calculations reproducible from retained/source tables |
| legacy fixed hourly load proxy | R2/R3 | builder exists |
| ERA5-sensitive hourly load v2 released chronology | **R1** | payload/parts/hash/loader fully integrity-reproducible |
| ERA5-sensitive v2 coefficient fitting and holdout scores | **R0/R1** | methodology + source fingerprints + fit results retained, but original end-to-end fitter is not committed |
| ERA5 renewable v0.6 | R2/R3 conditional on source artifacts | source-QA workflow and transformation code exist |
| PyPSA adequacy / expansion | R2/R3 | configs, source-bounded evidence and runners retained |
| PyPSA ↔ SciPy equivalence | R4 for common formulation | independent implementations agree under same assumptions |
| PyPSA ↔ OSeMOSYS common frontier | R4 for common formulation | independent frameworks agree under same assumptions |
| hydro v1.1 / v1.2 | R2/R3 | configs/runners/evidence retained |
| Idukki v1.3 | R2/R3 | source rows, state equation and artifact metadata retained |
| Idukki v1.4/v1.5 | R2 methodology / source-gated run | exact physical-source run intentionally blocked where inputs absent |
| network topology / screen | R2/R3 | topology/equipment parsers and screen retained; some upstream KSEBL source bytes not all locally archived |
| WP6 synthetic pilots | R2/R3 | authored profiles + code + invariants retained |
| GIS audits | mixed R1–R3 | depends on upstream data licensing/access; gates preserve unavailable layers |
| website / public synthesis | R2 | generated from repository evidence files |

## ERA5-sensitive v2 gap

The audit inspected:

- PR #110;
- PR #113;
- the final `hourly_load_proxy_era5_weather_sensitive_v2` manifest and seven payload parts;
- `src/kerala2040/weather_load_proxy.py`;
- `tests/test_weather_load_proxy.py`;
- current load-building scripts.

PR #110 introduced the compact v2 artifact, loader, tests and methodology note. PR #113 integrated the same artifact into chronological screening. Neither PR contains the original fitting script.

The repository therefore can verify:

- profile classification;
- exact 8,760 values;
- payload hashes;
- dates/timezone;
- 11 imputed-day flags;
- exact observed daily-energy conservation;
- downstream model use.

It **cannot currently regenerate from code in the repository**:

- the clock-time basis fit;
- weather coefficients;
- Jan–Mar holdout predictions/metrics;
- the compact v2 values from raw ERA5 + extrema.

The raw ERA5 GRIB/detailed hourly weather rows are also intentionally not committed, although their source archive SHA-256 is recorded.

### Scientific consequence

This is a **reproducibility gap, not evidence that the released chronology is false**.

The correct conference wording is:

> “The released v2 chronology is cryptographically pinned and its downstream use is reproducible. The original fitting pipeline and raw ERA5 archive are not currently public in the repository, so the coefficient fit itself is not end-to-end reproducible from a fresh clone.”

### Required future correction

If the original fitting code/source archive is recovered, add it with:

- exact source hashes;
- environment/dependencies;
- train/holdout date rule;
- objective function;
- feature construction;
- calibration constraints;
- deterministic seed/solver settings if applicable;
- regenerated payload hash comparison.

Do **not** write a new fitter after the fact and label it the original unless it reproduces the exact released coefficients, holdout metrics and payload from the pinned source archive.

## Reproducibility wording correction

The public project can safely say:

> “The repository makes the released evidence, transformations and model assumptions inspectable, and most model runs are reproducible from retained inputs. Some upstream or derived datasets remain source- or license-gated; the ERA5-sensitive v2 fitting stage is currently integrity-verifiable but not fully source-to-fit reproducible from the public repository.”

Avoid the blanket phrase:

> “Every result is fully reproducible from a fresh clone.”

## Why fail-closed workflows are still reproducible

A workflow that stops because its required source is absent can still be reproducible if the failure condition itself is deterministic and documented.

Examples:

- Idukki v1.5 exact KSEB monthly workbook gate;
- Phase 5 catchment geometry gate;
- statutory GIS layers.

The reproducible result can legitimately be **“not admitted because evidence X is missing.”**
