# P0 — FY2024–25 reservoir operations and cascade evidence

**Research status: partial qualitative topology; operating physics BLOCKED.** This is a dated source review and reproducible audit, not a hydro optimisation result or a complete Kerala hydraulic network.

## What is truly observed

The retained [Kerala SLDC storage reports](https://sldckerala.com/index.php?id=7) contain **5,664 reservoir rows**: sixteen named reservoir records for each of **354 observed dates** in FY2024–25. The separately dated [SLDC generation reports](https://sldckerala.com/index.php?id=1) contain **5,779 hydro station rows**; they report energy and selected maxima, not a continuous unit-dispatch record. Both are identified by daily raw-response SHA-256 within their respective report sections. The original raw ZIP has SHA-256 `5c1bb8cbe67a9b3a9149080250b4bfcfbf2d30592f3f5afdb6248e2b25623101`. The eleven missing dates remain missing. A station’s blank daily generation is **unknown, not zero**.

The storage CSV preserves source-provided *effective storage (mcm)*, *level (m)*, *storage percent*, *gross generation capability (MU)* and *station generation capability (MU)* as **different fields**. Its 1 April 2024 Kakki entry, for instance, reports positive effective storage (**219.925 mcm**) while the reported storage-percent field is **0**. This is flagged as a source-field conflict; do not quietly recompute and replace the published percentage. Pamba and Kakki also contribute to a shared hydro scheme; treating all reported “gross” MU as independent dispatchable stores risks recycling the same water more than once.

**“Inflow MU” is an energy-equivalent reported unit**, not a measured physical `mcm/day` reservoir water balance. Level changes are not net inflows: turbine releases, spill, evaporation, transfers, water use and non-linear stage–volume conversions affect them. Where the retained normalized CSV does not preserve reported spill or inflow quantities, the audit does not invent them from level differences. See `data/external/sldc_fy2024_25/README.md` and `qa_report.json`.

## Source-confirmed *selected* water relationships

This is not a claim to complete all 16 reservoir rows or the Kerala network. The source-keyed [topology file](../configs/hydro_topology_evidence_2024_25.yaml) records only clearly described qualitative edges.

| Officially described relationship | Consequence for eventual modelling |
|---|---|
| Idukki, Cheruthoni and Kulamavu dams form **one reservoir** feeding Idukki HEP (Moolamattom). [KSEBL dam details](https://dams.kseb.in/?p=108). | No three separate Idukki reservoir energy stores. |
| Pamba reservoir transfers to Kakki by tunnel; Kakki–Anathode is a common reservoir and conveys water to **Sabarigiri**. [Pamba](https://dams.kseb.in/?p=122), [Kakki](https://dams.kseb.in/?p=118). | Pamba and Kakki are connected water, not two independent unlinked 340 MW powerhouses. |
| Sabarigiri tailwater enters the Moozhiyar system, whose diversion contributes to **Kakkad HEP**. [KSEBL Pathanamthitta diversion structures](https://dams.kseb.in/?p=190). | A downstream Kakkad release is coupled to upstream operation and other local inflow. |
| Sholayar’s three dams form **one reservoir**, feeding Sholayar HEP; its tailwater contributes to Poringalkuthu, which supplies both Poringalkuthu and left-bank extension. [Sholayar](https://dams.kseb.in/?p=132), [Poringalkuthu](https://dams.kseb.in/?p=129). | Do not assign all upstream and downstream generation capabilities as separately available water. |

Those pages give **connectivity**, not daily discharge, flow time lags, control priorities, head-dependent efficiency or applicable FY2024–25 rule curves. A dam page’s project nameplate is also not a per-day dispatchable MW limit or available generation. The SLDC generation table groups **“Poringalkuthu, PLBE”**; that row is not independently split into plant-level daily MU.

## Executable audit, not an unconstrained model

Run:

```bash
PYTHONPATH=src python scripts/audit_hydro_operations.py
```

Output: `results/hydro/operations_evidence.json`. A dedicated CI job preserves this separately from any proxy-PyPSA output. The script checks QA day counts and missing dates; 16 distinct reservoir names per observed day; full station-row coverage and hashes within each source-day; exact SLDC source labels for mapped reservoirs/stations; documentary HTTPS source keys for each listed link; shared-storage complexes; directed edges and cycle rejection; and observed discrepancies between fields. A `gross` MU indicator, `station` MU indicator, and `inflow` MU indicator are **never added together, converted into mcm, or installed as PyPSA stores**.

The crosscheck is intentionally conservative. It does not assert that every named source station is physically connected to one of the 16 reported reservoirs. `Moozhiyar` is an explicitly *non-observed intermediate node*, not an invented 17th SLDC reservoir record.

## Requirements for closing the hydro physics gate

For each storage complex and turbine/plant path, obtain versioned official evidence on:

- usable stage–storage curves, initial/terminal storage and effective minimum drawdown, spillway/rule-curve limits;
- catchment inflow **in water-volume/flow units**, measured releases/spill/withdrawals and upstream-to-downstream transfer routing;
- net/gross **head**, turbine efficiency, plant/unit mapping, generation-to-water conversion and applicable dispatch/maintenance availability;
- downstream minimum/environmental flow, irrigation/water-supply commitments, flood operation and reservoir control objectives;
- complete source identity, FY2024–25 time bounds, data permission, unit and revision checks, and a coupled mass balance against measured observations.

No interpolation of missing dates; no assumption that observed reservoir percentage is an enforceable energy limit; no summation across upstream/downstream cascades. The existing `docs/OBSERVED_DAILY_PYPSA.md` continues to keep hydro stations as **fixed historical accounting attribution**, without physical reservoirs, until these constraints are reconciled.
