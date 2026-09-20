# P0 — Kerala FY2024–25 interstate transfer and procurement audit

**Status: partial source reconnaissance and 354-day observed energy QA; the physical transfer and cost gate remains BLOCKED.** Reviewed 20 September 2026. The purpose is to separate dated *system transfer capability*, purchased or scheduled power, observed import/export energy and financial contracts; it is **not** a proposed Kerala ATC curve or new 2040 cost input.

## What the FY2024–25 record supports

The project's retained [Kerala SLDC system statistics](https://sldckerala.com/index.php?id=1) provide **2,832 official grouped import-interface energy rows**: eight labels for each of **354 genuinely observed days**, 11 days missing. The rows include grouped labels such as `400KV KOCHI+KOTTAYAM` and `220KV_KNPA+SBGR +PVUD+EDMN`. The source columns are **MU per day**, *not* independently operated physical line MW, hourly flows, transformer MVA or transfer rights. The sum of each observed day's eight energy rows is checked against the archived daily statewide net-import balance with a tolerance of 0.001 MU. Their observed-day net total is **22,635.0183 MU**, *not* a full-year import total.

The separately sourced [Kerala Economic Review 2025, Volume I](https://spb.kerala.gov.in/sites/default/files/2026-01/ER%202025%20Volume1%20Eng%20final.pdf), underlying KSEBL energy accounting, reports **FY2024–25 gross import 25,790.95 MU**, export **1,789.65 MU**, and total power purchase **26,286.30 MU**. These are *three distinct annual categories* and are not exactly interchangeable with 354-day SLDC net imports. In particular, the difference from the observed-day net total cannot be used to reconstruct the 11 missing daily values: coverage and accounting boundaries differ.

### Documented transfer snapshots, not an annual constraint

- **15 January 2025, SRPC special meeting with Kerala:** [record notes, section B item xxiii](https://www.srpc.kar.nic.in/website/2024/meetings/communication/rnkerala150125.pdf) report Kerala **TTC 4,350 MW** and a **90 MW reliability margin**. The corresponding **4,260 MW ATC is the arithmetic TTC-minus-margin for that reported snapshot**, not an 8,760-hour import capacity. The same meeting notes describe N−1 constraints at Kozhikode and Thrissur HVDC 400/220 kV interconnecting transformers; KSEBL requested studies for higher transfer capability. The meeting's demand for further studies is *not* approval of the requested 4,610 MW.
- **From 1 March 2025 (retrospective account):** KSEBL's *Fourteenth Annual Report FY2024–25*, Power System Engineering/System Operation, says joint studies raised import capability **from 4,260 MW to 4,455 MW** and describes an increase of approximately 200 MW from 1 March. [Third-party accessible copy of KSEBL-authored annual report](https://www.scribd.com/document/1022839813/14th-Annual-Report-2024-25-1770108815259021875); a versioned *first-party* KSEBL PDF and detailed revised SRLDC/SLDC ATC/TTC notices are not archived with the repo. The report calls 4,455 MW *import capability*; do not silently label it as a complete, unconditional TTC, ATC, N−1 limit, export capability or a 2040 forecast.

**The existing `configs/pypsa_screening_example.yaml` `import_limit_mw: 6500.0` remains only a scenario sensitivity.** It must never appear as FY24–25 measured/verified capacity or be overwritten with one January/March snapshot applied across all hours. Likewise, the fact that a line carried a given daily MU cannot certify its instantaneously available MW or residual ATC.

### Procurement is separate from grid permission

KSEBL's FY2024–25 annual report describes long-term PPAs, DEEP short-term transactions, banking/swaps, and power-exchange purchases/sales. A purchased MW contract may be unavailable at particular hours or not commissioned, and a firm grid path does not itself prove commercially available energy. A swap *import* may entail a later *export* or return obligation.

Two explicitly **non-historical** examples from the report are catalogued to prevent chronology errors: a **500 MW SECI solar-with-storage** agreement signed **12 September 2024** with future expected commissioning, and **50 MW West Kallada floating solar** dated **8 April 2025** (after FY2024–25). Neither is represented as FY24–25 deliverable power, delivered energy, or hourly dispatch. A quoted exchange ₹/kWh is not a Kerala periphery landed price including applicable transmission, losses, scheduling, DSM and other charges. Do not infer contracted MW from annual imports, or sum future PPA nameplates as ATC.

## Reproducible bounded audit

```bash
PYTHONPATH=src python scripts/audit_grid_transfer.py
```

Outputs `results/grid/transfer_contract_evidence.json`. The committed `configs/grid_transfer_contract_evidence_2024_25.yaml` preserves report scope and provenance. The executable checks SLDC source-day SHA, exactly eight grouped interface rows on each observed date, the 11 missing dates, each day's daily-import energy additivity, published observed-day totals and the annual reference categories; it checks January TTC less stated reliability margin, source IDs, contract date classification, and fails if evidence silently enables historical or future MW constraints. CI retains the JSON as **partial evidence**, not an approved 2040 grid input.

The 354 source-observed days are immutable historical accounting here. Modelling inputs are still **null/blocked** for:

1. Dated and revision-controlled import **and export** ATC/TTC/GNA or equivalent scheduled capability for FY2024–25; effective date, clock interval, topology, outage/contingency scenario, counterflow and N−1 assumptions.
2. Confirmed connection/transformer/HVDC corridor bottlenecks and applicable margins, so simultaneous corridor transfers are not summed as an unconstrained state import.
3. Actual versus *scheduled* 15-minute net import/export with compatible meter boundary, revisions, sign and daily reconciliation. SRPC DSM files can cross-check regional actual drawal; they do not replace Kerala's state demand series.
4. A dated, named PPA, central allocation, bilateral, DEEP, banking/swap and power-exchange contract register: source, start/end, MW, shape, must-run or take-or-pay, seasonal availability, force majeure and settlement/banking obligations.
5. Actual Kerala periphery *landed* import tariffs, power exchange procurement, network and transmission charges, losses, purchased quantities and currency/base year. Regulatory **approved** purchases/costs must be kept separate from actual procurement and from 2040 assumptions.
6. Forward 2040 transfer development commitments, commissioning dependencies and plausible corridor outages/deratings. FY24–25 capability is not automatically the 2040 capacity.

### Agency request addendum (not sent by this work)

For SLDC/KSEBL and SRLDC, request dated Kerala aggregate TTC, ATC, TRM/available margins, import/export direction, revision and effective timestamps for **1 April 2024–31 March 2025**; applicable interface-group definitions; binding N−1/ICT/HVDC constraints; and the official notice changing import capability around **1 March 2025**. Separately seek **contract-level**, commercially releasable start/end dates, MW/time blocks, actual scheduled/delivered energy, swap obligations and costs with confidentiality terms. These requests supplement the already-sent emails; there is no claim that this follow-up was sent.

**Gate status:** `grid_transfer = blocked_missing_verified_evidence`. Physical capacity and procurement economics are **different constraints**, and the 2040 techno-economic gate remains blocked.
