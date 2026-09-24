# Kerala Total Energy Atlas · sectoral emissions bridge and fuel-accounting method

**Executed source integration: 24 September 2026.**  
**Classification:** `2023_OFFICIAL_MODELED_SECTOR_EMISSIONS_NOT_FY2024_25_FINAL_ENERGY`.

[Auditable source and unit register](../data/evidence/total_energy/kerala_ghg_sector_bridge_2026_09_24.json) · [Previous EMC final-energy source study](KERALA_TOTAL_ENERGY_ATLAS_BASELINE_2026_09_24.md) · [Full-year PPAC fuel-sales audit](PPAC_KERALA_FULL_YEAR_SALES_SOURCE_AUDIT_2026_09_24.md).

## A previously missing official sectoral dataset

Kerala's Directorate of Environment and Climate Change publishes a [state GHG Energy inventory with estimates through **calendar 2023**](https://climatechange.envt.kerala.gov.in/emissions-estimates/energy/). This is the most immediately usable **sector-sensitive** source found for the Total Energy Atlas. It is **an emissions inventory**, not a measured fuel×sector energy workbook and not an annual FY2024–25 PPAC sales record. Its source method uses national reference factors and some interpolated/allocated activity; neither its emissions nor its category shares should be back-converted into tonnes or Mtoe.

**Official 2023 energy-sector estimate: 20.64 MtCO₂e, roughly 80% of Kerala's gross GHG emissions excluding land-use, land-use change and forestry.**

| Calendar 2023 emissions category | Official MtCO₂e | Official share of energy-sector emissions | Interpretation |
|---|---:|---:|---|
| Transport | **13.59** | **65.87%** | Road component is **about 11.83 MtCO₂e**, approximately 87% *of transport*, not all Kerala emissions |
| Residential energy | **3.20** | **15.48%** | Official portal attributes about 99.6% *of residential-energy emissions* to LPG |
| Industrial energy | **1.89** | **9.16%** | Includes FO/LSHS **0.74 MtCO₂e** and natural gas **0.62 MtCO₂e** |
| **Energy-sector total** | **20.64** | **100%** | Includes more energy categories than these three; **do not normalize the three-category display to 100%** |

All displayed values and shares are **as rounded by the current official portal**, not recomputed for the project; component sums need not equal sector totals at rounded precision. These values do not establish that transport used 65.87% of Kerala's **energy**—only that it was assigned 65.87% of the **energy-sector emissions inventory**. The source does not establish that Kerala petroleum **imports** are 65.87%.

The current portal's 2023 estimate and the [June 2024 DoECC/Vasudha **2005–2021 report**](https://climatechange.envt.kerala.gov.in/wp-content/uploads/2024/06/Kerala-GHG-Inventory-Report_June24-1.pdf) are **not a single version-controlled timeseries**. The older report gives **2020 energy emissions of 16.96 MtCO₂e**; the 2023 portal discusses **17.09 MtCO₂e for 2020**. The difference is recorded as an inventory-vintage discrepancy requiring versioned methodology and raw/aggregated table clarification, not silently stitched into a trend. The old report's separate 2019 **20.05 MtCO₂e** also cannot be assumed to match the updated portal's revised vintage.

## Why the greenhouse-gas estimate does not resolve the underlying fuel balance

The [DoECC 2024 energy methodology](https://climatechange.envt.kerala.gov.in/methodology/energy/) says that petroleum ministry/PPAC data were used; underlying fuels reported as **financial years were converted to calendar years** for emissions accounting. Its [June 2024 report](https://climatechange.envt.kerala.gov.in/wp-content/uploads/2024/06/Kerala-GHG-Inventory-Report_June24-1.pdf), annexed energy methodology on pp. 60–87, describes applying **national petrol/diesel retail/transport shares** to Kerala activity data, interpolations for missing years and non-transport diesel allocation from dated PPAC studies. It identifies an opportunity to replace national proxy shares with year-specific state sector shares. The 2024 methodological PDF covers results through 2021; **we have not verified which specific revisions underlie the later 2023 portal**.

These are scientifically useful *modelled estimates*, distinct from a state fuel purchase, engine efficiency, consumed energy or measured refinery output. If we attempted to infer 'diesel tonnes used by Kerala transport' simply by dividing transport CO₂e by a generic emission factor, the inverse would be underdetermined because transport includes several fuels/modes and CH₄/N₂O. Likewise a 2023 transport-emissions figure cannot be paired with FY2024–25 diesel sales to claim a measured 2024–25 emission intensity.

## Separate fuel heating-value reference now recovered

The [BEE/CII/EMC State Energy Efficiency Action Plan, Annexure Table 25, printed p. 109](https://keralaenergy.gov.in/wp-content/uploads/2023/07/SEEAP-report_ready-to-print.pdf), publishes **gross calorific values in kcal/kg**. The following entries have been transcribed from the publisher PDF **text**, not from EMC's unpublished actual fuel-by-sector calculation workbook:

| Historical published fuel label | Gross kcal/kg |
|---|---:|
| Liquefied petroleum gas | 11,318 |
| Motor gasoline | 10,717 |
| Gas/diesel oil | 10,357 |
| Fuel oil | 9,866 |
| Kerosene | 10,467 |
| Kerosene-type jet fuel | 10,667 |
| Naphtha | 10,767 |

**Gross calorific value (GCV) is not net calorific value (NCV).** The PPAC oil-company sales cells in our [six-FY register](../data/evidence/total_energy/ppac_full_fy_kerala_source_audit_2026_09_24.json) are mass *sold* in Kerala by petroleum companies, with FY2024–25 still from a third-party reproduction awaiting original publisher PDF image comparison. The historical EMC GCV table is not a measurement of FY2024–25 supplied-fuel grade. We therefore do **not** publish a pseudo-precise Kerala FY2024–25 energy balance, carbon inventory or product-to-Mtoe conversion by merely multiplying those tables.

**Conversion template, not an estimated outcome:** for a *source-admitted, product-specific and period-matched* mass `m` in thousand metric tonnes and an appropriately documented energy content `h` in TJ per thousand tonnes, `energy_TJ = m × h`. An official toe convention and NCV/GCV basis are required before reporting Mtoe. Remove power-sector *transformation fuel*, non-energy feedstock, double-counted on-site/captive generation and inter-state turnover; account for stock changes and product/mode-specific end use. The sectoral classification must match the published EMC/DoECC definition before any comparison. Our original publisher's FY2015 energy chart/prose discrepancy (9.18 vs 9.81 Mtoe) remains unresolved.

## Coverage map: exactly what remains absent

| Layer | Confirmed public evidence | Missing before a valid Kerala-wide final-energy balance |
|---|---|---|
| Historical **total final energy** | EMC FY2014–15 to FY2019–20 figure, FY2019–20 **10.78 Mtoe**, rounded mix | Original workbook/author-approved FY × fuel × sector table and FY2015 correction |
| Annual **petroleum sales mass** | PPAC six FY rows, FY2024–25 named exact publication mirror | Publisher-original 2024–25 Kerala page and native full year × product XLSX/CSV with revisions and data dictionary |
| Fuel **quality / energy** | EMC historical GCV reference table | Source-consistent product/year NCVs (or documented GCV basis), conversion convention, non-energy fractions |
| **Sectoral use** | 2023 official DoECC emissions categories and earlier explicit proxy methods | 2024–25 measured/verified petrol/diesel/LPG/FO/gas splits across end users and date-aligned inventory data |
| Kerala **import dependence** | Fuel-sales and infrastructure indicators (different populations) | Physical origin → destination mass-energy balance incl. transit/re-export, refinery input/output and utilities |
| **Climate impacts** | 2023 official modelled emissions **on its own calendar-year boundary** | Matched 2024–25 scope, missing sector/captive/grid-import treatment and inventory revision bridge |

The [PPAC state-wise sales page](https://ppac.gov.in/consumption/state-wise) currently advertises an approximately **88 KB Statewise Sales file**, but the available retrieved page does not expose verifiable raw bytes or a clear file URL. **Do not report that the native workbook has been acquired.** The original FY2024–25 PPAC publication link responds with an `application/octet-stream` content type that the web PDF viewer does not admit; this is a *viewer/access limitation*, not proof the data are nonexistent.

## Source-data request pack (public or authorised academic release only)

**To PPAC:** "For an independent academic Kerala energy-systems evidence study, could you provide or point us to the publicly releasable native Statewise Sales workbook, years FY2019–20 onward including the final FY2024–25 edition, a product code and unit dictionary, source-revision dates, the Kerala all-POL/MS/HSD rows, and a public citation URL or release permission? We also seek confirmation of whether Statewise Sales includes sales to aviation, inter-state buyers, private imports and SEZs, and whether FY2022–23 figures were revised between the October 2023 and H1 FY2024–25 Reckoners. A pointer to a public download is sufficient."

**To EMC/CII/BEE:** "For a reproducible academic comparison of Kerala final energy beyond electricity, may we obtain the published or publication-cleared aggregate FY2014–15–FY2019–20 workbook behind SEEAP Figure 3 and Figure 4: original fuel-product, sector, input units, final-use adjustments, calorific basis, energy conversion, captive electricity handling and numerical denominators? Could you also clarify Figure 3 FY2015 **9.18** vs Section 3 prose **9.81 Mtoe**, and whether a subsequent Kerala final-energy update exists? Aggregated data with a dictionary are sufficient; no personal or confidential data are requested."

**To DoECC/Vasudha:** "Could you provide a public version/date and data dictionary for the 2023 Energy Sector GHG inventory (including transport/residential/industrial subcategories), the underlying *aggregated* activity table, year conversion, source-specific petrol/diesel sector shares, gas/FO/LPG accounting, and a version bridge explaining the **2020 16.96 vs 17.09 MtCO₂e** discrepancy between the June 2024 report and current portal? Please clarify imported-electricity emissions treatment and permission to publish aggregate indicators."

Nothing has been sent or requested on the user's behalf; this is the exact public-information acquisition specification. A family member working in a different department is not needed to access or obtain confidential data.

**Result:** A new official, calendar-2023 *sectoral emissions* lens and published heating-value method reference are integrated, and all remaining barriers to a **FY2024–25 fuel×sector final-energy balance** are individually defined. **Current total-final-energy Mtoe, all-sector fuel fractions, petroleum import share and modeled 2040 transition remain unverified.**
