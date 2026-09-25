# Kerala2040 — full PyPSA data-acquisition sprint

**Date:** 25 September 2026  
**Status:** executed evidence acquisition; model inputs are still evidence-gated.  
**Purpose:** convert the asset/project claims collected during the audit into source-bounded records suitable for the full S0–S5 PyPSA programme.

This sprint deliberately separates **existing capacity**, **distributed generation**, **contracted/awarded pipeline**, **planning-study candidates**, **transmission capability**, **sector-coupling demand**, and **current stress evidence**. It does not promote a project because a search result, tender, PPA, planning table or AI summary mentions a MW figure.

## New canonical evidence files

- [Kerala energy asset and project register](../data/evidence/assets/kerala_energy_asset_register_2026_09_25.json)
- [CEA/KSERC generation resource-adequacy benchmark, 2025–36](../data/evidence/demand/kerala_resource_adequacy_2025_2035_36_2026_09_25.json)
- [CEA transmission resource-adequacy evidence, to 2034–35](../data/evidence/grid/kerala_transmission_resource_adequacy_2034_35_2026_09_25.json)
- [September 2026 Kerala power-stress evidence](../data/evidence/system/kerala_sep2026_power_stress_2026_09_25.json)
- [Full-PyPSA input admission registry](../configs/full_pypsa_input_registry.yaml)

## The most important correction: current capacity has multiple official boundaries

Kerala's **31 March 2025 Economic Review** total remains the correct FY2024–25 historical anchor: 4,412.14 MW, comprising 2,284.42 MW hydro, 536.54 MW thermal, 1,519.66 MW solar and 71.53 MW wind.

The newer **CEA transmission Resource Adequacy Plan** uses a different 31 March 2026 reporting boundary. It reports **3,221.30 MW** in its main table — 536.54 MW thermal + 2,284.42 MW hydro + 400.34 MW wind/solar — and reports **1,912.33 MW of solar below 1 MW separately**. Thus the frequently repeated “3,221 MW plus ~1,912 MW rooftop” formulation is a real CEA accounting convention, not an arithmetic mistake. It must not be mixed blindly with the older Economic Review or the later MNRE snapshot.

The **MNRE 31 August 2026 location-based renewable snapshot** is later again and reports **2,259.50 MW rooftop solar**, 342.27 MW ground-mounted solar and 2,626.84 MW total solar in Kerala. The change from 1,912.33 MW below-1-MW solar in March to 2,259.50 MW MNRE rooftop solar in August is not automatically a five-month capacity addition because the source definitions differ as well as the date.

**Model rule:** choose a base date and reconcile every technology/size/ownership boundary before constructing a current fleet.

## Demand benchmarks acquired

### Generation Resource Adequacy Plan

The KSERC/CEA Resource Adequacy Plan now gives an official benchmark from FY2025–26 through FY2035–36. Its peak-demand path rises from **6,204 MW** in FY2025–26 to **8,926 MW** in FY2035–36; FY2030–31 is **7,500 MW**. It also preserves annual energy forecasts, planned additions, RPO balances, contracted-resource requirements and ±10% demand sensitivity.

### Transmission Resource Adequacy Plan

CEA's separate transmission study uses a materially higher planning trajectory: **7,916 MW** in FY2029–30 and **9,780 MW** in FY2034–35. The transmission report explicitly notes that its 7,916 MW KSEBL case is above the revised 20th EPS 6,752 MW forecast and deliberately uses the higher case for network studies.

For FY2034–35, the generation RA benchmark gives **8,637 MW**, whereas the transmission RA study gives **9,780 MW** — a **1,143 MW difference**.

**Model rule:** these are named official sensitivities, not numbers to average. Kerala2040 must document which trajectory is its reference, lower and higher case.

## Existing and distributed generation acquired

The source-bounded asset register now distinguishes the major current assets and accounting buckets:

- NTPC Rajiv Gandhi CCPP/Kayamkulam: about 360 MW operator nameplate, 359.58 MW in Kerala's official capacity accounting.
- KSEBL Brahmapuram liquid-fuel station: 63.96 MW current FY2024–25 accounting.
- KSEBL Kozhikode liquid-fuel station: 96 MW current FY2024–25 accounting.
- NTPC Kayamkulam floating solar: 92 MW, with CEA-reported FY2024–25 generation of **203.07 MU**.
- Kasaragod Solar Park: the initial 200 MW concept was revised because of land availability; **100 MW is confirmed commissioned** across Ambalathara and Paivalike. Do not use 200 MW as current plant capacity.
- THDC Solar Kasaragod: 50 MW named component with CEA-reported FY2024–25 generation of **90.81 MU**; this is a component of the Kasaragod complex and is not added again on top of the confirmed park subtotal.
- CIAL: operator reports **50 MW** total installed solar portfolio plus a 4.5 MW Arippara small hydro plant; exact mapping into the statewide ownership buckets still needs reconciliation.
- KSEBL Kanjikode wind: ~2.03 MW. Agali/Ahalia and the rest of the private/CPP wind fleet remain an asset-level reconciliation task against the current **71.52 MW** MNRE wind total.

Historical plants such as BSES/Kochi are retained as historical records rather than silently reintroduced as current dispatchable MW.

## Battery storage: project-level evidence acquired

The storage story is now considerably stronger than the generic “800 MW BESS” claim.

### Mylatti

Official KSERC material establishes a **125 MW / 500 MWh (4 h)** project at Mylatti:

- SECI procurement / JSW Neo Energy project structure;
- LoA 20 March 2025;
- BESSA 10 April 2025;
- BESPA 29 April 2025;
- capacity charge ₹4.41 lakh/MW/month;
- ₹135 crore VGF;
- tender RTE benchmark 85%;
- annual capacity-degradation limit 2.5%.

This is project-specific evidence; commercial operation has **not** been promoted without COD evidence.

### Four-site NHPC procurement

Official KSERC material establishes another **125 MW / 500 MWh** across:

- Sreekantapuram 40 MW / 160 MWh;
- Mulleria 15 MW / 60 MWh;
- Areacode 30 MW / 120 MWh;
- Pothencode 40 MW / 160 MWh.

The register preserves project-specific capacity charges and cited connection arrangements. These remain pipeline assets until COD is independently verified.

### Planning-scale BESS

CEA's transmission plan assumes **800 MW BESS by 2029–30**. This explains the “800 MW BESS” figure found in secondary summaries. It is a **future transmission-planning assumption**, not proof of 800 MW currently installed and not proof that an 800 MW battery would eliminate a present 800 MW shortage.

CEA's current BESS-report index also publishes an August 2026 national status report. The Kerala projects have not been reclassified as operational from the index alone; the underlying project row/COD must be inspected before changing their status.

## Pumped storage: separate projects, no more conflation

The acquisition confirms several distinct concepts:

1. **Idukki Extension HEP** is conventional hydro peaking expansion, not inherently pumped storage. KSEBL's own scheme describes sharing daily drawal from the existing Idukki reservoir.
2. THDCIL separately prepared PFRs for **Idukki PSP 700 MW** and **Pallivasal PSP 600 MW**. THDCIL reported KSEBL acceptance of the PFRs and requested allocation for DPR/implementation. No later project allocation/COD is inferred.
3. CEA's transmission planning case for 2034–35 contains a different candidate PSP portfolio: **Mudirapuzha 100 MW, Kakkayam 800 MW, Poringalkuth 400 MW and Upper Chaliyar 360 MW**, total **1,660 MW**.

None is admitted as a buildable PyPSA Store until reservoir pairs, hydraulic route, head, level-volume curves, efficiencies, usable MWh, water-operation constraints, environmental status and site-specific project status are verified.

## Transmission evidence is now much deeper

CEA's current transmission RA report gives a usable structural starting point:

- current Kerala TTC **4,575 MW** and import ATC **4,455 MW** in the report's snapshot;
- 24,497 MVA existing intrastate transformation capacity;
- 10,561.83 circuit-km intrastate transmission lines across 400/220/110/66 kV;
- 4,965 MVA named ISTS transformation capacity;
- 1,813.87 circuit-km ISTS lines;
- nine named interstate corridors to Tamil Nadu and Karnataka;
- known bottlenecks at Kozhikode and Thrissur-HVDC ICTs;
- network reinforcement schedules;
- by 2029–30: 2,500 MVA / 474 ckm additional ISTS and 8,500 MVA / 492 ckm additional InSTS;
- by 2034–35: a further 1,000 MVA / 280 ckm ISTS and 2,560 MVA / 1,169 ckm InSTS.

The individual line MW ratings are **not added together** to create Kerala import capability. ATC/TTC remains a simultaneous network-security property.

The same study reports GEC-II **452 MW RE / 224 ckm / 620 MVA** under implementation and GEC-III **1,759 MW / 1,422 ckm / 1,973 MVA** planned.

## Hydrogen and new flexible load

ANERT's Kochi Green Hydrogen Valley roadmap is retained as **sector-coupling evidence**, not generation. It discusses aggregation/provision of roughly 200–300 MW renewable supply and transmission infrastructure for the valley. Kerala's draft hydrogen policy separately discusses support for the first 100 MW of electrolyser deployment.

These figures are not current electrolyser load. The final model needs electrolyser COD, utilisation, efficiency, compression/storage electricity and hydrogen end-use demand.

CIAL's BPCL hydrogen pilot is retained as a project lead because current source material uses both a 1,000 kW project label and a 500 kW electrolyser description; the engineering boundary needs confirmation before assigning one model MW value.

## September 2026 shortage: acquired as an event, not a permanent deficit

Current reporting shows the key modelling point: the shortage varies sharply with procurement and availability.

Secondary reports cite days with shortages of roughly 700–900+ MW, but another high-consumption day had only about **21 MW** of shortage at maximum demand. The event is therefore not a single fixed “Kerala deficit.” It involves demand, assured central/contracted supply, short-term market availability, hydro/weather, timing and transmission simultaneously.

The event register consequently leaves:

- permanent baseline deficit MW = **NULL**;
- “required BESS MW” = **NULL**.

The useful next acquisition is the matching 15-minute SLDC/KSEBL chronology for demand, interchange, scheduled/actual contracted supply, hydropower, exchange procurement/price and any load restriction.

## What is now substantially closed vs still open

**Substantially improved/available:** official 2026 renewable baseline; official current CEA capacity accounting boundary; official generation-demand RA trajectory; official transmission RA topology and reinforcement plan; major current thermal/solar assets; project-specific BESS awards; contracted solar/storage pipeline; current TTC/ATC snapshot; named interstate corridors; current/future network reinforcements; hydrogen roadmap context; bounded September-2026 stress evidence.

**Still blocks a defensible full expansion solve:** complete station/unit fleet and availability; measured interval system chronology; time-varying import capability and landed power cost; harmonised technology costs/finance; hydro/PSP physical constraints; statutory GIS capacity ceilings; a reliability criterion; distribution hosting constraints for the now very large rooftop-solar fleet; and calibrated EV/cooling/industrial/hydrogen flexibility.

The correct next step is **input selection and reconciliation**, not more blind data accumulation: choose the model base year/boundary, reconcile the fleet to it, and define research-assumption ranges for the remaining blocked quantities without promoting them to observed facts.
