# FY2024-25 Kerala generating-unit register — bounded reconciliation

Evidence review: 20 September 2026. Audit item: `generator_register` (P0).
**Status: partial / provisional, NOT a validated full fleet for a 2040 capacity-expansion model.**

## Distinguish three inventory boundaries

1. `public/kseb-projects.json` is an archived KSEB Project Management System **project explorer** extraction. It contains 70 named rows, while the explorer reports 87 items. The tracker has a **20 February 2023** data-as-of label. Its 59 `Completed` rows are **not** 59 verified FY2024-25 operating generating stations. Named rows may be planning initiatives, plant extensions, central/private assets, or missing/incorrect unit entries.
2. `configs/observed_2024_25.yaml` records Kerala Economic Review 2025's **all-owner Kerala** installed generation as **4,412.14 MW**, including **2,284.42 MW hydro** at FY end. This is not KSEBL-owned nameplate power or contracted import capacity.
3. The same official Economic Review, Chapter 11, printed p. 571, identifies **KSEBL-owned** capacity as approximately **2,409.8 MW** (including **2,196.4 MW hydel across 44 stations**) on 31 March 2025. Reported annual FY24-25 KSEBL generation **7,393.77 MU** is an annual *utility aggregate*, not a station-level observed profile, usable stored water, or guaranteed capacity.

The all-owner and KSEBL-only totals deliberately do not reconcile against the project explorer's unverified sum. Small and private/captive/distributed generators cannot be reverse-engineered from residual arithmetic.

## Two independently documented commissioning corrections

KSEB's archived project explorer still labels these rows `Ongoing`. The official Kerala Economic Review's FY2024-25 achievements and CEA's March 2025 installed-capacity report's *projects commissioned during FY2024-25* establish the following **bounded additions**:

| Project as named in the portal | Portal status | Source-confirmed unit additions | Evidence status |
|---|---|---|---|
| Thottiyar HEP | Ongoing | 10 MW 10 July 2024 + 30 MW 30 September 2024 = **40 MW** | Confirmed as FY2024-25 commissioned additions, **not verified hourly availability** |
| Pallivasal Extension Scheme | Ongoing | 30 MW + 30 MW **commissioned by 24 December 2024**, **60 MW** total | Confirmed as FY2024-25 commissioned additions; grid synchronisation and official commissioning date need not coincide |

The Economic Review records both schemes in its achievements; the CEA March 2025 final-page commissioned-project list records MW and dates. The KSEBL annual report also refers to grid synchronisation on 5 and 24 December for Pallivasal; our dated commissioning check uses the **CEA commissioning label** rather than silently substituting synchronisation.

**Do not add this 100 MW again** to the official 31 March 2025 capacity total: it is included there. Do not treat the 100 MW as a verified hour-by-hour available hydro dispatch resource.

Official source references:

- [Kerala Economic Review 2025, Volume I, Chapter 11, pp. 571–572](https://spb.kerala.gov.in/sites/default/files/2026-01/ER%202025%20Volume1%20Eng%20final.pdf)
- [CEA installed capacity as on 31 March 2025, commissioned-project list](https://cea.nic.in/wp-content/uploads/installed/2025/03/IC_March_2025_allocation_wise.pdf)
- [KSEB public project explorer](https://pms.kseb.in/explore-projects)

The crosscheck is source-keyed in `configs/generator_reconciliation_2024_25.yaml`; commissioning unit sums, dates, matching portal names, technology and statewide official totals are checked by the code.

## Project explorer problems found

- **Poringalkuthu Left Bank Project - Micro Screw Generator 1x11kW**: portal numeric capacity is **11 MW**, while its own name says **11 kW = 0.011 MW**. The original 11 remains visible in `capacity_mw`; `unit_label_capacity_mw` retains 0.011 and raises a conflict. The plant is not silently assigned corrected operational MW.
- **Agali -Chaliyur-96kW**: the project name implies **0.096 MW**, while the numeric portal field reports **0.96 MW**. Remains unresolved and non-validated.
- A `Completed` zero-MW Sabarigiri augmentation row is not a new dispatchable generating unit.
- Future `planned_commissioning` dates are not `commissioning_year`.
- 70 captured project records out of 87 reported entries leave **17 items not reconciled**. The portal count is not a completeness certificate.

Run:

```bash
python scripts/build_generator_database.py
```

Outputs: `results/inventory/generator_capacity_database.csv`, its Parquet analogue and `generator_capacity_summary.json`. Only the two sourced FY2024-25 additions receive `reconciled_commissioned_mw`; that field is not a full fleet tally. `capacity_mw` and `status` remain **raw portal fields** for inspection.

## Gate closure requirements

The `generator_assets` readiness check stays **partial** until there is a genuinely matched and bounded full fleet:

- dated **station/unit** commissioned and retired MW, unit IDs, fuel/technology, agency/owner, refurbishments, and non-KSEBL IPP/CPP/distributed generation;
- station- or unit-level FY2024-25 measured energy with compatible source naming/aliases, actual unit availability, outages/deratings;
- verified subaggregates KSEBL-only vs all-owner vs contracted/off-site capacity and no double counting of extensions or 2024-25 additions;
- validation of source units (MW vs kW), report revisions, capacity mismatches, missing records and station/daily SLDC account boundaries.

**A valid annual capacity sum, a project marked completed, and a source-labelled station-generation record are different facts.** They do not alone close this gate.
