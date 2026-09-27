# KSEBL network screening closeout v0.1

## Purpose

This stage converts the public KSEBL topology skeleton into a **usable
transmission screening model** without presenting assumed electrical parameters
or reconstructed bus loads as operator measurements.

The source-backed topology remains the authority. The screening layer is a
separate, replaceable model-input layer.

## New official evidence source

KSEBL *Power System Statistics 2022-23* supplies the historical equipment
inventory, dated **31 March 2023**. The legacy KSEBL download endpoint is no
longer reliable from automated runners, so the repository carries a compact,
cryptographically pinned **110-kV+ source snapshot** of the model-relevant
Table 33/34 rows preserved from search-indexed text of the official KSEBL PDF.
No third-party values are used in that snapshot:

- **Table 33** — EHV and 33 kV substations, including transformer voltage
  ratios, unit MVA, transformer count and printed total MVA.
- **Table 34** — EHV and 33 kV transmission lines, including feeder code and
  conductor identity.

The 2023 evidence is not silently treated as proof that equipment remained
unchanged in 2026.

Table 34 snapshot rows are retained only where the normalised feeder code
crosswalks exactly to the newer public grid graph. Table 33 primary station
rows are admitted only when the station name maps uniquely to a public graph
site and the printed unit-MVA × transformer-count reconciles with printed total
MVA. Ambiguous and unmatched rows are exported for review rather than guessed.

The snapshot is deliberately **not a complete transcription** of the report. It
contains only evidence relevant to the 110-kV+ model. CI recomputes its canonical
SHA-256 and fails closed if the payload changes without an explicit source
refresh. The original KSEBL URL, report date, printed table-page ranges and
source-text line locators are preserved in the snapshot metadata. Because the
legacy live endpoint no longer yields the original PDF bytes reliably, no
source-PDF SHA-256 is invented.

## Line screening parameters

For every admitted topology segment, the output keeps separate provenance for:

1. the KSEBL/PSS feeder and conductor identity;
2. a KSEBL public-SLD conductor-current reference where repeated text evidence
   provides a stable value;
3. a derived three-phase screening MVA;
4. a conductor-specific 20 °C D.C. resistance reference where available;
5. an explicit generic voltage-class reactance assumption.

If conductor/current evidence is absent, a conservative voltage-class current
fallback is used only in the **screening** column and is labelled as an
assumption.

The resulting thermal MVA is not an operator emergency, seasonal, or dynamic
line rating.

## Transformer screening parameters

Printed Table 33 total MVA from the 2022-23 snapshot is used as historical transformer-capacity evidence
when the printed unit MVA × count reconciles with the printed total.

Table 33 may also add a voltage-specific bus/link that is absent from the
text-readable SLD evidence. These additions are labelled as 2023 PSS evidence;
they do not overwrite newer SLD evidence.

Transformer reactance remains a generic screening assumption. This stage does
not claim calibrated transformer impedances.

## Spatial load proxy

The existing FY2024-25 8,760-hour statewide load reconstruction remains the
temporal source. It is still classified as a proxy, not measured telemetry.

Statewide load is spatially allocated only to PSS-backed distribution
interfaces (low side <=33 kV), weighted by printed transformer MVA. The
allocation is normalised so every hourly bus-load sum exactly reproduces the
statewide hourly proxy.

This produces a **capacity-weighted spatial load proxy**, not measured
substation/bus demand.

## Readiness terminology

After this stage, the intended claims are:

- source-backed physical topology: **yes**
- thermal transport screening inputs: **yes**, with evidence/assumption tiers
- spatial 8,760-hour load proxy: **yes**
- DC screening inputs: **yes**, with generic reactance assumptions
- calibrated DC power flow: **no**
- AC power flow: **no**
- measured bus-load telemetry: **no**

The remaining calibrated-DC/AC gaps are therefore bounded data-quality gaps,
not unfinished model assembly.
