# User-uploaded Anna University power-evacuation report and 19 extracted CSVs

**Intake:** 22 September 2026. **Evidence classification:** historical, geographically external grid-integration case and methodological source; **not a Kerala network, site entitlement, actual 2026 grid headroom, or 2040 result**.

## Original and reproduction status

- Original supplied `Power_Evacuation_Anna_University.pdf`: **2,510,894 bytes**, SHA256 `aad56609e7c9cb7cd214e54b42ae923097794c66689170ef9715d9ef5191c54b`, **104 PDF pages**.
- Title page: *Power Evacuation Studies for Grid Integrated Wind Energy Conversion System*, Anna University, March **2014**, project RD-RD-192-10. The terms of reference explicitly concern **Tirunelveli/Tamil Nadu**, not Kerala (PDF pp. 1 and 10).
- Notice on PDF p. 2 states that reproducing or otherwise using the report requires written C-WET/proponent permission. Retain supplied original privately and **do not mirror the PDF, extracted CSVs or figures in the public repository or website until rights are clarified**. The document below records facts, methodological comparisons, and aggregate QA, not original figures or full data.
- Source report's detailed engineering case reflects **2010-era field data and project-study scenarios**, not Kerala 2026 transmission-state evidence. No network topology, line rating, bus fault strength, load, cost or recommended technology is carried into our current Kerala model without independent Kerala-specific evidence.

## PDF crosswalk of extracted CSVs

| User file / family | Original PDF page or status | Interpretation |
|---|---|---|
| `Table_2.1_Tirunelveli_Generation_Details.csv` | p. 17, Table 2.1 | 1,608 MW conventional total in this historical **Tirunelveli study**, not Kerala generation. |
| `Table_2.2_Substation_Details.csv` | pp. 18–19, Table 2.2 | 44 listed substations, printed 5,106 WTGs and 2,857.70 MW wind capacity **up to September 2010**; supplied CSV row 17 is incorrect; see QA below. |
| `Overloaded_Transmission_Lines_at_70_Wind_Power_Penetration.csv` | p. 24, Table 3.2 | Nine listed >100%-loaded study branches in that simulated case. |
| `Table_3.3_Overloaded_Transmission_Lines_at_80_Wind_Power_ghhnkMg.csv` | pp. 24–25, Table 3.3 | 18 listed >100%-loaded study branches at 80% study wind scenario; note reported chapter-specific model-size variations rather than merging inconsistent denominators. |
| `Table_5.6_Results_from_power_flow_analysis_lines_overloading_100.csv` | pp. 54–55, Table 5.6 | 15 >100%-loaded entries **in the report's VSC-HVDC study case**. A VSC link is not shown to eliminate all constraints statewide. |
| `Table_5.7_Comparison_Between_Double_Circuit_AC_Link_vs_VSC-HVDC.csv` | p. 56, Table 5.7 | Six historical study line-loading comparisons under separate reinforcement options; e.g. Kayathar21–Ayyanaroothu: **44.5% with DC link vs 88.11% with double-circuit AC**, against a stated **176.22% prior scenario** (PDF pp. 55–56). Not a Kerala option ranking, cost comparison or modern network design. |
| `Table_5.8_AC_Line_Flow_with_DC_Ring.csv` | p. 57, Table 5.8 | Seven AC branch results when proposed MTDC ring is embedded, with P, Q and loading; source-specific case only. |
| `Table_5.9_Flows_in_DC_ring.csv` | p. 57, Table 5.9 | Five DC line-flow results, MW. Proposed network, not commissioned plant or Kerala transfer rating. |

**Important semantic qualification:** The report p. 23 says 80% of installed wind-study capacity for a case, but reports multiple network aggregate sizes, including a **156-bus, 210-line, 44-transformer, 5,106-WTG network** on PDF p. 20 and a **156-bus, 187-line, 22-transformer, 2,860-generator** test system in a later TCSC section (PDF p. 51). Do not assume all tables refer to a single harmonised current grid snapshot. Its p. 23 50%-penetration text reports wind injection of 672.20 MW, not simply 0.5×2,857.70 MW; treat labels/injections as source-specific and preserve this mismatch.

## Independent QA of the loose CSVs

**Substation Table 2.2: hard transcription mismatch.**

- Loose CSV row `Chenbagaramanputhoor 110/11 kV SS`: turbine count `-`, capacity **92.25 MW**; printed PDF p. 18 instead: **9 turbines, 2.25 MW**.
- Summing the **44 loose CSV branch capacity entries** gives **2,947.70 MW**, **90 MW above** the printed 2,857.70 MW total. Its valid numeric turbine counts sum to **5,097** vs printed 5,106 (missing nine). Replacing only that row's value and count *for a separately traced analytical copy* would reconcile both totals, but the original uploaded CSV remains untouched.
- QA status: `extracted_CSV_exact_PDF_match=false`. Do not use the loose CSV as an authoritative base-network inventory or upload it unchanged to the modelling dataset.

**Other orphan tables:** the remaining **11** extracted CSVs contain `Table_5.1_Feeder_Capacity_Wind_Farm.csv`, `Table_7.2_Load_Flow_Study_of_E2_Feeder.csv`, `Table_7.5_Grid_Bus_Voltage_Decrease.csv`, `Table_3.9_Flickering_Data.csv`, `Table_3.8_Wind_Velocity_Motor_Action.csv`, `Table_3.5_Grid_Frequency_Increase.csv`, `Table_3.5a_Grid_Frequency_Decrease.csv`, `Table_3.2_Grid_Bus_Voltage_Decrease.csv`, `Table_3.1_Grid_Bus_Voltage_Increase.csv`, `Table_6.3_Rotor_Natural_Frequency_Spinning_Rotor.csv`, `Table_6.4_Single_Blade_Vibration_Modes.csv`.

Those titles/values concern another wind-farm feeder/quality study and blade/rotor structural-frequency study, **not uniquely attributable to the uploaded Anna University 2014 PDF**. The report's own Table 5.1 concerns **worldwide VSC-HVDC installations**, not a feeder-capacity table. Do not cite Anna University for unrelated table 5.1 or assume all similarly numbered tables share a source. For the orphan feeder table alone, its 15 listed feeder capacities sum to **123.15 MW** versus printed **123.00 MW**; `E5` states 14×0.85 MW = **11.90 MW** but lists **12.00 MW**, leaving **123.05 MW** by simple unit-count multiplication. The 0.05-MW residual remains unexplained; don't repair it without the missing actual source publication.

## What the report can contribute to Kerala2040

The study separates the **power-flow, short-circuit, reactive-power and transient stability** questions (PDF pp. 12, 20–32, 59–80). It illustrates a *sensitivity design* that increases wind injections and observes congestion and voltage; AC reinforcement, TCSC, VSC link and MTDC ring are tested as **alternative grid interventions**, not universally valid solutions. Its LVRT results are tied to study assumptions and historical induction-generator models, not an assessment of modern Kerala turbines.

Translate this into **model requirements**, not a borrowed 2014 result:

1. Define Kerala-specific bus, branch, transformer, corridor and generation topology with custodians, effective date, kV/MVA limits, contingencies, verified spatial endpoints and transmission rights.
2. Test increasing actual/specified onshore renewable injection by corridor and season, while separating **MW injection from percentage of installed capacity**. Retain AC power-flow loss, reactive limits, bus-voltage and line/transformer-loading diagnostics.
3. Compare AC reinforcement and controllable transmission alternatives **only when justified by Kerala candidate corridors and contemporary cost, protection, reactive-power and grid-code data**; do not hard-code VSC-HVDC or TCSC as preferable.
4. Represent fault levels and LVRT as **separate follow-on AC/dynamic studies** if a validated model and generator parameters become available; a nodal PyPSA energy-balance model alone is insufficient to claim electrical stability.

**Admission:** `Kerala_grid_model_data=false`; `Kerala_transfer_limit_MW=null`; `2040_HVDC_build_choice=null`; `wind_feasible_capacity_MW=null`; `wind_terrain_150m_clip_not_supplied_by_this_batch=true`. This intake is a useful methods reference for the grid workstream, *not* a reason to alter historical baseline, spatial feasibility or website numerical claims.
