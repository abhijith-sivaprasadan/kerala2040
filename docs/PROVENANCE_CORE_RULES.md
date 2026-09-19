# Kerala 2040 data provenance policy

This policy is mandatory for model inputs, intermediate datasets, figures and reported results.

## Core rule

No value may be presented without making clear whether it is observed, an official reference,
reanalysis, derived, proxy/synthetic, a scenario assumption, or an external study result.

### Required fields

Every model-facing dataset or machine-readable result must expose:

- `classification`
- `source_type`
- `source` when the value originates from an external/organic source
- a note when a proxy, synthetic value, or scenario assumption could be mistaken for measurement

## Classification meanings

| classification | Meaning |
|---|---|
| `observed` | Directly reported/measured operational data from a named primary source |
| `official_reference` | Official reported aggregate/reference value from a named authority |
| `reanalysis` | Model/reanalysis dataset such as ERA5 or NASA POWER; not plant telemetry |
| `derived` | Arithmetic/statistical transformation of identified source data |
| `proxy` | Reconstructed stand-in for unavailable data; never described as measured |
| `synthetic` | Artificially generated test/development data |
| `scenario_assumption` | Deliberately chosen future/stress-test assumption |
| `external_study_result` | Result copied from a published external study for benchmarking only |
| `catalogue_only` | A source/layer has been identified but the underlying model-ready data are not yet acquired |

## Naming rule

Proxy or synthetic files must include `proxy`, `synthetic`, or `dev` in their filename where practical.
Observed datasets must never reuse those labels.

## Reporting rule

When describing organic/source data in prose, name the source explicitly, for example:

- "Kerala SLDC observed daily system statistics"
- "Kerala State Planning Board / KSEBL Economic Review 2025 reference"
- "CEA Resource Adequacy Plan reference"
- "NASA POWER reanalysis/remote-sensing-derived weather"

When describing non-organic data, state the classification explicitly:

- "synthetic"
- "proxy reconstruction"
- "derived"
- "scenario assumption"

## Model rule

A model run must fail validation rather than silently filling a required field with a convenient number.

The FY2024-25 observed daily PyPSA replay must not consume the synthetic 8,760-hour load proxy.
The hourly load proxy remains a development-only reconstruction until authenticated Kerala hourly
or 15-minute telemetry is obtained.
