# KSEBL robust bottleneck shortlist v1.0

**Status:** public-data **screening evidence**, not calibrated operator congestion and not an approved transmission plan.

This note freezes the robust subset from PR #121. The FY2024-25 8,760-hour public-network model was rerun under eight different allocations of the same statewide boundary accounting residual across six admitted interstate interfaces. A line is called **robust** only when it exceeds its source-backed screening MVA in every allocation case.

## Result

- 233 primary lines had KSEBL conductor/current-backed screening ratings.
- 21 lines were overloaded in all eight boundary-allocation cases.
- Those 21 line segments form 12 connected robust subgraphs.
- 34 independent PSS-backed transformers were testable.
- One transformer, **Shornur 220/110 kV, 100 MVA**, was overloaded in all eight cases.
- Every sensitivity case remained topologically closed with no diagnostic gap supply.

## Robust source-backed lines

| Line | kV | District(s) | Screening MVA | Minimum peak loading across cases | Minimum overloaded hours |
|---|---:|---|---:|---:|---:|
| Malapparamba–Shornur | 110 | Malappuram / Palakkad | 56.40 | 2.177 pu | 8,297 |
| Malapparamba–Koppam | 110 | Malappuram / Palakkad | 56.40 | 2.170 pu | 8,272 |
| Shornur–Koppam | 110 | Palakkad | 56.40 | 2.170 pu | 8,272 |
| Pallom–Pampady | 110 | Kottayam | 65.35 | 2.145 pu | 8,064 |
| Shornur–Areacode | 220 | Palakkad / Malappuram | 276.64 | 1.803 pu | 4,528 |
| Malapparamba–Perinthalmanna | 110 | Malappuram | 65.35 | 1.798 pu | 5,116 |
| Kunnamangalam–Kuttikatoor | 110 | Kozhikode | 65.35 | 1.695 pu | 4,270 |
| TERLS–Veli | 110 | Thiruvananthapuram | 65.35 | 1.695 pu | 4,270 |
| Elankur–Areacode | 220 | Malappuram | 276.64 | 1.523 pu | 2,069 |
| CIAL–Carborandum | 110 | Ernakulam / Thrissur | 65.35 | 1.419 pu | 2,164 |
| Madakkathara–Athani | 110 | Thrissur | 65.35 | 1.405 pu | 1,333 |
| Vennakkara–Malampuzha | 110 | Palakkad | 65.35 | 1.378 pu | 1,054 |
| Chalakudy–Kodakara | 110 | Thrissur | 65.35 | 1.268 pu | 826 |
| Malapparamba–Mankada | 110 | Malappuram | 65.35 | 1.254 pu | 511 |
| Mankada tap–Melattur | 110 | Malappuram | 65.35 | 1.254 pu | 511 |
| Edappal–Kuttipuram | 110 | Malappuram | 65.35 | 1.128 pu | 180 |
| Pampady–Kanjirapally | 110 | Kottayam | 65.35 | 1.086 pu | 84 |
| Kalamassery–Edayar I, segment 2 | 110 | Ernakulam | 65.35 | 1.069 pu | 55 |
| Kalamassery–Edayar I, segment 1 | 110 | Ernakulam | 65.35 | 1.069 pu | 55 |
| Kundara–Perinad | 110 | Kollam | 65.35 | 1.060 pu | 40 |
| Kalamassery–Edayar II | 110 | Ernakulam | 65.35 | 1.049 pu | 21 |

The strongest geographic concentration is the **Malappuram–Palakkad/Shornur** area, including both 110-kV subgraphs and the 220-kV Shornur–Areacode–Elankur chain. Kottayam also has a persistent Pallom–Pampady–Kanjirapally signal. Other robust local signals occur in Kozhikode, Thiruvananthapuram, Thrissur/Ernakulam, Palakkad, Kollam and the Kalamassery–Edayar industrial area.

## Robust corridor groups

The 21 robust lines resolve into 12 connected screening corridors when grouped by shared bus endpoints:

| ID | Corridor | kV | Robust lines | Strongest minimum peak | Strongest minimum overloaded hours |
|---|---|---:|---:|---:|---:|
| C01 | Malapparamba–Shornur–Koppam–Perinthalmanna–Melattur | 110 | 6 | 2.177 pu | 8,297 h |
| C02 | Kalamassery–Edayar | 110 | 3 | 1.069 pu | 55 h |
| C03 | Pallom–Pampady–Kanjirappally | 110 | 2 | 2.145 pu | 8,064 h |
| C04 | Shornur–Areacode–Elankur | 220 | 2 | 1.803 pu | 4,528 h |
| C05 | Kunnamangalam–Kuttikattoor | 110 | 1 | 1.695 pu | 4,270 h |
| C06 | TERLS–Veli | 110 | 1 | 1.695 pu | 4,270 h |
| C07 | CIAL–Carborandum | 110 | 1 | 1.419 pu | 2,164 h |
| C08 | Madakkathara–Athani | 110 | 1 | 1.405 pu | 1,333 h |
| C09 | Vennakkara–Malampuzha | 110 | 1 | 1.378 pu | 1,054 h |
| C10 | Chalakudy–Kodakara | 110 | 1 | 1.268 pu | 826 h |
| C11 | Edappal–Kuttippuram | 110 | 1 | 1.128 pu | 180 h |
| C12 | Kundara–Perinadu | 110 | 1 | 1.060 pu | 40 h |

The strongest multi-voltage screening hotspot is **Shornur**. C01 includes Shornur in the dominant 110-kV robust subgraph, C04 begins at Shornur on the 220-kV network, and the sole robust independent transformer is the Shornur 220/110-kV unit. That coincidence is stronger evidence than any one branch overload alone, but it remains public-data screening evidence rather than validated operator congestion.

## Robust transformer

**Shornur 220/110 kV — historical PSS capacity 100 MVA**

- minimum peak loading across the eight cases: **1.356 pu**
- median case peak loading: **2.281 pu**
- maximum case peak loading: **2.670 pu**
- minimum overloaded hours: **890 h**
- maximum overloaded hours: **8,375 h**

This transformer is independent of the transformer-capacity values used to create the spatial load weights, so it is a stronger screening signal than the excluded load-allocation transformers.

## PyPSA and OSeMOSYS treatment

The 559-bus PyPSA linear network screen **does internalize** the public network topology and screening branch parameters.

The Full-PyPSA capacity-expansion programme and the TZ-OSeMOSYS benchmark/common frontier remain statewide/single-region planning models. They now load this robust-network evidence as an explicit **planning gate**, but do not convert it into transmission investment constraints. Doing so would require future corridor capacities, candidate upgrades, upgrade costs, and a validated spatial/zonal allocation of future generation and demand.

Therefore a PyPSA/OSeMOSYS capacity result can pass cross-framework numerical equivalence while still being **network-unvalidated**. Network feasibility becomes a separate mandatory promotion gate before any result is described as a validated Kerala capacity plan.

Source: PR #121, merged commit `2c6f88a396d2ba2bf8683d33c5e7a7fdf563209b`, eight FY2024-25 boundary-allocation cases.
