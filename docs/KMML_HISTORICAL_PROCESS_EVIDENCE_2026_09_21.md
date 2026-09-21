# KMML source excerpts: historical process engineering and acquisition ledger

**Evidence date:** 21 September 2026 (user shared visible pages/screenshots and excerpts).  
**Classification:** secondary historical design/process information + official public qualitative process descriptions. **Not** authenticated FY2024–25 operational, financial, effluent or energy telemetry.  
**Principal user-supplied reference:** https://www.scribd.com/document/430627332/KMML . The supplied material includes an introductory KMML slide deck, scans of an acid regeneration/plant report, and pasted official KMML pages. Their document identities, authors, dates and mutual relationship have **not** been verified as a single publication. Do not cite them as one KMML-authored primary engineering report or reproduce their images in the public repo without permission.

Official background supplied by the user:
- https://www.kmml.com/process
- https://www.kmml.com/manufacturing-facility
- https://www.kmml.com/manufacturing-facility/2 (acid regeneration, navigation link)
- https://www.kmml.com/manufacturing-facility/5 (pigment plant)
- https://www.kmml.com/manufacturing-facility/6 (utilities)

## 1. Distinct plant branches

1. **Mineral separation (MS):** beach-sand mineral separation including ilmenite, rutile, leucoxene and others; physical/gravity/magnetic/electrostatic steps.
2. **Ilmenite beneficiation (IBP):** raw ilmenite -> beneficiated ilmenite, involving reduction/leaching and spent acid.
3. **Acid regeneration plant (ARP):** spent chloride liquor from IBP -> spray roasting/hydrolysis -> HCl recovery/absorption and iron oxide; a linked recovery unit, **not** the TiO2 pigment oxidation reactor.
4. **Pigment chain:** beneficiated ilmenite + chlorine/coke -> TiCl4 production and purification (**U200**) -> TiCl4 oxidation (**U300**) -> pigment treatment, filtering, drying, micronising and packing (**U400**). Oxygen and utilities have separate boundaries.
5. **Titanium sponge:** **separate Kroll branch** using TiCl4 purified to metal grade, magnesium reduction, vacuum distillation, sponge finishing. Do not add TiO2 pigment and Ti sponge nameplates as like-for-like output. TiCl4 transferred internally to the sponge branch must not be counted twice as externally sold TiCl4.

The screenshot with a Kroll-process flowchart adjacent to a pigment flowchart must not be taken to show a single sequential main pigment process.

## 2. Historical *nameplate/design* values visible in screenshots

| Item | Visible figure | Source type and qualification |
|---|---:|---|
| TiO2 pigment capacity | 40,000 tonnes/year | Introductory slide; **historical claim**, not actual FY2024–25 output or confirmed present capacity |
| TiCl4 capacity | 90,000 tonnes/year | Introductory slide; historical, ambiguous gross versus saleable output |
| Titanium sponge capacity | 500 tonnes/year | Slide says `to be commissioned in Feb 2010`: therefore pre-2010/planned at presentation time, **not** evidence of commissioning or 2024–25 production |
| Spray roaster nominal rate | 7.4 tonnes/hour | Separate equipment-design scan; material basis and current applicability unknown |
| Spray roaster dimensions | 2,430 mm diameter × 30 m length | Design scan; unusual dimensions require independent confirmation before equipment/energy modelling |
| Spray roaster residence time | 150 minutes | Design scan; do not assume consistent with feed/hold-up absent process boundary |
| Calciner nominal rate | 5,279 kg/hour | Equipment-design scan, material basis and unit location not independently verified |
| Calciner dimensions | 2.43 m internal diameter × 30 m length | Design scan; verify original |
| Digester nominal volume | 99 m³ | Equipment-design scan, no batch throughput or operating fill factor |
| Recycle pump | 60 m³/hour, 20.5 m head | Equipment-design scan; **not** measured pump power or operation |
| Slurry pump | 60 m³/hour, 37.12 m head | Same |
| Roaster feed pump | 10.5 m³/hour, 10.5 m head | Same |

**Prohibited inference:** convert the pump Q/H pairs or equipment nameplate to annual electricity using assumed 8,760 hours, default efficiencies, or an assumed acid density, then call it measured KMML energy. A scoped engineering sensitivity could use explicitly assumed density, efficiency, load fraction and duty schedule, but it must remain synthetic.

## 3. ARP and pollution control: *descriptive/historical* flows

The user-provided report excerpt describes spent liquor as `17–18% total chloride`, transfer via recycle, pre-concentrator and fine filter to a spray roaster, with steam/oxygen hydrolysis and oil burners. It gives indicative temperatures **400 °C** at reaction/roaster and **375 -> 96 °C** gas cooling before the absorber. It quotes **18.8% recovered HCl**. The `total chloride` figure and HCl product concentration have **different definitions and flow boundaries**; they cannot be substituted for each other.

The text gives schematic reactions:

`4 FeCl2 + 4 H2O + O2 -> 2 Fe2O3 + 8 HCl`  
`2 FeCl3 + 3 H2O -> Fe2O3 + 6 HCl`

These are illustrative balanced component reactions, **not** proven actual overall plant yields or a complete mass/heat balance. Need feed chloride/iron speciation, gas/liquid flow, HCl recovery fraction, Fe2O3 grade, fuel rates and measured residuals.

Historical effluent narrative: primary/secondary neutralisation (spent lime then fresh lime/caustic); settling pond cited **50,000 m³**, polishing pond **25,000 m³**; excerpt says clear treated water discharged to Arabian Sea. A separate excerpt describes two proposed secure landfills **36,000 m² each** (at the report's unspecified date). Those dimensions are historical design claims, **not** verified existing 2024–25 pond capacity, landfill commissioning, discharge quality, consent compliance or current disposal route. Report cites monthly stack analysis and an additional airflow of around **22,000 m³/hour**; that is not an emissions mass-flow measurement. Do not use the report's assurance that water meets standards as an independent compliance finding.

The user-shared report includes scanned flow sheets labelled **IBP**, **ARP**, **U-200** and **U-300**. Text is not reliably legible at the supplied raster resolution, and drawing revisions/dates are not established. Register them as *potential process-topology primary-document leads*, not validated P&IDs or digitised stream flow rates.

## 4. Oxidation, grades and chemistry QA

The official text the user supplied identifies U200 chlorination around **900 °C** (a separate pasted process page writes `9000C`, evidently a formatting issue), U300 oxidation, and U400 steam-heated drying/steam micronising. Neither textual temperature is verified actual operating history or a duty in MJ/t.

A simplified stoichiometric reaction is `TiCl4 + O2 -> TiO2 + 2 Cl2`. Website text appends heat on both sides, which is **not** a valid quantified net heat balance. Include actual heat demand/recovery only once measured or calculated with explicit enthalpies, conversions and boundaries.

The slide lists KEMOX grades RC 800, RC 800 PG, RC 813, RC 822 and RC 808; the supplied official U400 page also names RC 802 and RC 804. **Different-era product lists should not be interpreted as verified FY2024–25 sales/production mixes.**

A historical oxychloride-comparison slide lists KMML HCl 19–20%, TiOCl2 35–39% and water balance, without a dated product specification/method. Do not treat it as an analyzed plant stream, wastewater concentration or current saleable product.

Other nanopigment particle size, historic global production and 2004–2009 import/price slides are background unrelated to the FY2024–25 KMML material-energy-water gate; they are excluded from model input.

## 5. Explicit field-level primary data request

Obtain **FY2024–25** (or nearest fully stated, internally consistent period) data with source units, meter/process boundary, availability and redistribution terms:

| Process boundary | Essential measured data | Model purpose |
|---|---|---|
| MS / IBP | Ore and mineral input/output, ilmenite grade, ferric/ferrous chemistry, acid concentration and flow, wash-water streams | feed-to-product and chloride/iron balance |
| ARP | spent acid inflow tonnes and composition, recovered acid volume/concentration, iron oxide mass/chemistry/moisture, gas and liquid emissions, oil/fuel/steam/electricity, recycle and reject streams | actual acid loop and recovery route |
| U200 chlorination | BI tonnes/grade, coke, chlorine, impure/pure TiCl4, impurity chlorides, purge and stack streams, fuel/electricity | elemental and energy balance |
| U300 oxidation | TiCl4 and oxygen use, TiO2 output, recycled chlorine, steam/fuel, heat recovery, electricity | avoid double-counting chlorine and heat |
| U400 finishing | grades/output mass, additives, water, steam drying, electricity/microniser use, rejects, wastewater | product-weighted footprint |
| Sponge branch | actual TiCl4 allocation, Mg, Ti sponge, MgCl2, reprocessing and energy | distinct value-add branch |
| Utilities and ETP | time-aligned metered electricity, fuel, boilers, compressed air, cooling, raw water, recycle, treated effluent, sludge, landfill operations and monitored characteristics | whole-site closure and recovery options |

Prefer plant-confirmed aggregate monthly totals if line-level sensitive data cannot be released, with explicit uncertainty and scope. Annual capacity alone is neither annual output nor annual energy. KSPCB consent conditions, plant monitoring records and dated KMML annual reports may cross-check plant claims, but do not substitute for missing measurements.

## Gate

**`kmml_measured`: remains blocked.** This note improves the source and experimental boundary; it does not authenticate the screenshots' original reports, grant reproduction rights, establish 2024–25 production, or certify wastewater/emissions compliance.
