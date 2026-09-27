# KSEBL public multi-bus skeleton v0.1

**Status:** structural topology handoff; **not** dispatch- or power-flow-ready  
**Evidence boundary:** KSEBL public Grid Map v3.2, public single-line diagrams, and the reconciled FY2024-25 generator census

## Purpose

The earlier Kerala2040 power-system models were deliberately statewide or reduced-zone abstractions because a source-backed sub-state network was not yet available. The public KSEBL Grid Map now provides a defensible physical 110/220/320/400-kV topology, and public SLDs provide partial station voltage/transformer evidence.

This stage converts those admitted evidence layers into a voltage-specific model-assembly skeleton without filling missing electrical data with generic assumptions.

## Structural construction

The builder:

1. requires unique physical node identities from the v0.2 public topology;
2. expands each active physical site into voltage-specific buses supported by at least one of:
   - an incident public feeder voltage,
   - the public station voltage class, or
   - active transformer voltage evidence from a public SLD;
3. maps each admitted feeder topology segment to buses at its published voltage;
4. creates structural voltage-bridge links only from admitted active transformer evidence;
5. attaches only generators already admitted by the FY2024-25 generator-to-public-bus crosswalk;
6. leaves unresolved generation, loads, ratings and impedances outside the model rather than allocating them heuristically.

Three-winding transformer evidence is represented only as adjacent voltage-level connectivity for topology assembly. It is **not** converted into an electrical three-winding equivalent.

## Expected v0.1 handoff

The current evidence produces approximately:

| Layer | Result |
|---|---:|
| Unique physical 110-kV+ graph nodes | 324 |
| Voltage-specific buses | 467 |
| Feeder topology segments | 561 |
| Structural transformer-connectivity links | 104 |
| Active SLD transformer evidence records | 226 |
| Active transformer evidence mapped to the 110-kV+ graph | 157 |
| Multi-voltage sites | 100 |
| Sites with incomplete transformer connectivity evidence | 37 |
| Generator rows attached to a voltage bus | 31 |
| Attached installed capacity | 2,718.43 MW |
| Unallocated generator rows | 81 |
| Unallocated installed capacity | 1,693.726 MW |

These counts are CI-gated against the live public-source rebuild; the workflow artifact is authoritative if the source changes.

## Why the skeleton is still not a network dispatch model

Every admitted feeder segment currently lacks a source-backed electrical constraint:

- branch thermal/MVA limit: unresolved;
- resistance/reactance/shunt parameters: unresolved;
- emergency/seasonal ratings: unresolved.

The structural transformer links likewise do not yet carry an admitted aggregate station transfer limit or impedance. A transformer MVA string in an SLD is retained as evidence, but repeated/unlabelled text cannot safely be converted into a complete equipment count.

There is also no admitted substation/bus load chronology. The load table is intentionally emitted as an empty schema template.

Consequently:

- **topology skeleton ready:** yes;
- **transport-constrained dispatch ready:** no;
- **DC power flow ready:** no;
- **AC power flow ready:** no.

## Generator attachment boundary

The FY2024-25 census contains 4,412.156 MW across 112 rows. Only assets with a defensible public generating-site and 110-kV+ bus relationship are attached.

Where a public generating-station node has no explicit voltage class but exactly one incident public feeder voltage, the skeleton may use that unique feeder voltage as the generator bus-voltage evidence. No nearest arbitrary voltage bus is used.

Distributed/aggregate generation remains unallocated unless a source-backed spatial allocation is available.

## Remaining high-value gates

The next useful network work is evidence acquisition, not solver tuning:

1. promote source-backed feeder/conductor thermal-rating evidence where SLD text is explicit and can be reconciled to a feeder;
2. obtain or derive defensible branch electrical parameters from conductor/circuit evidence, with assumptions separately labelled;
3. close the 37 multi-voltage station connectivity gaps from SLDs or other public station evidence;
4. find public substation/bus load statistics or a defensible load-allocation evidence source;
5. only then instantiate a constrained PyPSA network and compare it against the existing statewide/reduced-zone models.

Until those gates close, the multi-bus output should be treated as a reproducible network **schema and evidence crosswalk**, not as a validated Kerala grid simulation.
