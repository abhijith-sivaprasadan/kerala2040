# Kerala Total Energy Atlas · first source-verified baseline

**Research closeout of first extraction, 24 September 2026.** Scope: **statewide final energy beyond electricity**. This is an authenticated historical baseline with a *separately dated provisional petroleum-sales slice*—**not** a complete reconstructed FY2024–25 Kerala energy balance.

[Machine-readable source register](../data/evidence/total_energy/kerala_total_energy_source_register_2026_09_24.json) · [Original research plan](research_plan.md) · [Existing PPAC dated infrastructure configuration](../configs/non_electric_energy_references.yaml).

## 1. What the original Kerala source actually measures

The [EMC Kerala/CII **State Energy Efficiency Action Plan**](https://keralaenergy.gov.in/files/PDF2023/State_energy_efficiency_action_plan.pdf), §1.4, printed **pp. 12–13 / PDF pages 12–13 (zero-based 11–12)**, defines **total final energy consumption (TFEC)** as energy used for end-use services across utility electricity, coal, petroleum products and gas. It reports a baseline **FY2019–20: 10.78 Mtoe**, and an original six-year total-energy chart. We visually verified the original chart, not merely search-result transcription. Chart labels `FY 2015` to `FY 2020` refer to **fiscal years ending** 2015–2020, not FY2015–16 to FY2020–21.

| Fiscal year | Source-figure labelled TFEC, Mtoe | Source type |
|---|---:|---|
| FY2014–15 | **9.18** | Report Figure 3, printed p. 13 |
| FY2015–16 | **9.35** | Same |
| FY2016–17 | **9.61** | Same |
| FY2017–18 | **10.17** | Same |
| FY2018–19 | **10.33** | Same |
| FY2019–20 | **10.78** | Same + section 1.4 prose |

**Original-source contradiction, preserved:** the same EMC action plan's §3 projection-method prose (printed **p. 19**) says the FY2015 actual TFEC was **9.81 Mtoe**, whereas its own Figure 3 on printed p. 13 visibly labels **FY2015 as 9.18 Mtoe**. The series above is explicitly **Figure-3-transcribed**, not a resolved source-level annual balance. Neither value is silently corrected or used to calibrate Kerala2040's demand trajectory. Obtain the author's workbook/corrigendum before independent statistical use of FY2014–15. This conflict is machine-recorded in the evidence JSON and displayed in the interactive chart's source note.

This six-point series is a **publisher's figure**, not a time series reconstructed or audited against original sector/fuel input spreadsheets. The report's separately stated **17.98 Mtoe FY2030** is *its projection* (printed p. 20), not a Kerala2040 observation or adopted forecast.

### Historical final-energy fuel mix—not electricity generation mix

In Figure 4 on printed p. 13 the publisher gives **integer-rounded** shares for its FY2019–20 final-energy baseline:

| Fuel/source category from publisher figure | Share of FY2019–20 TFEC |
|---|---:|
| Oil | **64%** |
| Electricity (utilities) | **19%** |
| Coal (imported) | **16%** |
| Gas | **1%** |
| Coal (non-power) | **0% displayed** |
| Coal (captive) | **No independently readable percentage in pie** |

**No exact fuel-specific Mtoe totals are published here.** The rounded percentages cannot be multiplied by 10.78 and relabelled measurements. A displayed 0% is not evidence of zero physical use. Coal “imported” is a supplier-category label in a published final-energy inventory, **not** a quantified Kerala border-import balance. Nor may a refinery's throughput, or the coal burned to produce a purchased unit of electricity, be counted a second time as Kerala end-use.

**Original plan implication:** our historical electricity chapters describe one final-energy carrier and its generation/imports. They do not explain the large oil category, the fossil-fuel uses driving it, the household cooking mix or the industrial heat supply. Kerala2040's statewide *energy* sovereignty, electrification and efficiency analyses must work with the other carriers too.

### Important quality flags in the action plan

The report calls FY2019–20 the baseline, while Figure 3 uses ending-year shorthand FY2020. Its electricity chapter uses different reporting conventions and has internal editorial artifacts (e.g. a missing reference in the Figure 7 introduction); it says domestic electricity is about 51%, commercial/industrial about 18% each, and open access about 3% **cross-sectoral**. These are **shares of the electricity sector only**, not shares of Kerala's TFEC. The percentages shown in its prose do not provide an exclusive complete end-use classification; municipality and bulk licensee definitions should not be naively added to customer end use. No new current sectoral total-energy split can be inferred from them.

## 2. New source slice: half-year petroleum-sales volumes

The [PPAC Ready Reckoner **H1 FY2024–25**, Table 6.3(A), printed p. 80](https://ppac.gov.in/download.php?file=rep_studies%2F1733114272_Ready+Reckoner_H1_FY+2024-25_Final.pdf) includes indexed publisher **Kerala** rows for selected products. **Caution: PPAC's PDF original did not open through the available page-image/download route on 24 September 2026; these are publisher-indexed text extractions awaiting original-page visual confirmation, and the report labels the data provisional.** They cover **1 April–30 September 2024**, not a complete financial year.

| Kerala product category, H1 FY2024–25 | Provisional sales, thousand metric tonnes |
|---|---:|
| Liquefied petroleum gas (LPG) | **579.0** |
| Motor spirit / petrol (MS) | **937.0** |
| High-speed diesel (HSD) | **1,169.5** |
| Aviation turbine fuel (ATF) | **283.7** |
| Superior kerosene oil (SKO) | **3.41** |
| Naphtha | **0.00** in the selected row |

**Crucial:** these are **selected product sales**, not a source-verified total of all petroleum sales. Other categories, including furnace oil/LSHS, petroleum coke and others, are not yet admitted; this table is not annual Kerala *final fuel consumption*. Some sales may support transport or industrial processes, some may be supplied onward across state boundaries; they cannot be assigned to end-use sectors without a documented allocation. Do **not** multiply any H1 value by two or convert fuel tonnes to Mtoe using undated generic factors and call the result measured demand. These are a separate source/time panel, *not data points on EMC's old historical TFEC trend*.

**PPAC discovery:** [statewise portal](https://ppac.gov.in/consumption/state-wise) advertises a download, but no authenticated complete fiscal-year, product-by-state bytes and product definitions have been admitted to this project in this sprint. The [PPAC Oil and Gas Snapshot of States (30 September 2024)](https://ppac.gov.in/download.php?file=rep_studies%2F1729769716_State_one_pager_Volume_2024-25_Edition_II_Apr_Sep.pdf) separately reports one Kerala refinery (15.5 MMTPA *capacity*), one LNG terminal (5 MMTPA *capacity*), 160 CNG stations, 2,859 retail outlets and 627 EV charging stations at retail outlets. These are **dated physical infrastructure counts/nameplate capacities**, not Kerala consumption or import volumes, and are recorded as a third independent layer.

## 3. Accounting architecture for the full atlas

```text
                 KERALA FINAL ENERGY / end-use boundary
                            │
   ┌────────────────────────┼─────────────────────────────┐
   │                        │                             │
 Utility/captive          Oil products                Coal/gas/other
  electricity           by distinct product             end-use fuel
   │                        │                             │
   └────────────────────────┼─────────────────────────────┘
                            ▼
           SECTORS / SERVICES (NOT YET ALL ALLOCATED)
   households: cooking, cooling, water, appliances, mobility
   transport: road, marine, rail, air  [fuel vs traction electricity]
   industry: heat, process fuel, motors, feedstocks separately
   commercial/public: cooling, buildings, water, essential services
   agriculture/fisheries: pumps, cold chain, diesel, other
                            │
               emissions / useful energy / finance
          only after matched factors, FY and source scopes
```

### Mandatory difference between four concepts

1. **TFEC:** energy delivered to final users. Do not add primary conversion fuel for a grid power plant to the electricity already bought by end users.
2. **Fuel sales:** PPAC product tonnes registered in a state. Not automatically energy finally burned in Kerala in that reporting period; sales include potential industrial feedstock and transport bunkering/aviation allocation questions.
3. **Supply/infrastructure:** refinery throughput capacity, LNG receiving nameplate, terminal locations, power-station MW. Cannot be promoted to Kerala end-use.
4. **Useful service:** vehicle-km, passenger-km, cooking meals, delivered cooling/heat. Not interchangeable with a kWh/mass fuel invoice; efficiency varies by technology.

**Join key:** `fiscal_year + exact dates + geographic boundary + physical quantity + sector/end-use + product + calorific standard + vintage/revision + source reference + rights`. Without these, each series remains separate and all cross-source total-energy computations remain unavailable.

### Cross-source reconciliation must not invent a current atlas total

EMC FY2019–20 TFEC and PPAC provisional April–September 2024 fuel sales have **different years and energy/mass units**. KSEBL/Economic Review FY2024–25 state-consumer electricity, SLDC operational energy and PPAC petroleum infrastructure also have **different perimeters**. The reported EMC baseline's 19% electricity share cannot substitute as the FY2024–25 electricity share. No fiscal-year fuel balance, petroleum import fraction, sectoral TFEC split, useful-energy output or 2040 system optimum is claimed here.

## 4. Immediate source acquisitions with concrete acceptance tests

| Rank | Source | Needed evidence and completion test |
|---|---|---|
| P0 | PPAC **full-year statewise product sales** and accompanying product-code legend | Authenticated 2019–20 and latest published FY (prefer FY2024–25) *same product definitions*, Kerala rows, original file/page visual, checksum; preserve provisional vs final. Check product subtotals versus “all POL products” and boundary of refinery transfer |
| P0 | EMC/SEEAP author calculation workbook or source table | Source by fuel × end-use sector for all six historical FY, heating values and baseline coverage, electricity/captive allocation and 2030 scenario assumptions; reconcile Fig. 3/4 rounding |
| P0 | Kerala gas supply/end-use and LNG supply source | PNG/CNG, industrial gas and feedstock distinguished; physical consumption ≠ pipeline capacity; period-specific Kerala split |
| P1 | Transport statistics and PPAC methodology | Two-/three-/four-wheelers, buses, trucks, marine, aviation and non-transport HSD; separately quantify freight/passenger service, refuelling/travel leakage and vehicle fuel intensity |
| P1 | Household energy survey (NSS/NSO/PLFS or Kerala surveys) | Rural/urban cooking-fuel shares and quantities, access, income, cooling saturation; never multiply household percentages by total statewide fuel tonnes without valid weights |
| P1 | Industry/FACT/KMML/TTPL measured materials and fuel | Separate chemical feedstocks, captive power fuel and useful process heat; ownership and product boundaries |
| P1 | KSEBL annual consumer categories | Allocate electricity only after same-FY and captive/open-access adjustment; no implicit combination with old EMC TFEC |

### Repository delivery

The [source register](../data/evidence/total_energy/kerala_total_energy_source_register_2026_09_24.json) contains 6 observed EMC annual source labels, five selectively transcribed provisional PPAC H1 product sales values plus reported zero naphtha, PPAC infrastructure and a full set of **explicit null current-period outputs**. Separate publisher-provenance and visual-QA flags reject mismatched dates, spurious annualisation and false project-wide totals in the public release.

**CET-safe statement:** “Kerala's EMC/CII historical study reports 10.78 Mtoe of final energy in FY2019–20, dominated by oil at a rounded 64%; utilities-supplied electricity represents 19% of that *historic energy* total. We are building a separate, source-dated petroleum/product series from PPAC without substituting sales and capacity for final consumption. A complete current statewide final-energy or fuel-import balance has not been published by Kerala2040.”
