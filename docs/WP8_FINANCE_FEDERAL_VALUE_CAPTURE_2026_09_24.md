# Kerala2040 WP8 — Who pays, who owns and who benefits?

**Executed independent public-record research, 24 September 2026.**  
**Classification:** preliminary source-scoped state/utility/public/private **finance architecture**; **not** a budget approved for Kerala2040, financial appraisal of a candidate project, fiscal-room estimate, tariff forecast or forecast of 2040 financing needs.

[Machine-readable finance evidence and boundary register](../data/evidence/finance/wp8_finance_source_ledger_2026_09_24.json) · [Original work-package plan](research_plan.md) · [Existing unselected techno-economic benchmarks](../configs/techno_economics.yaml) · [Finance-project row schema](../schemas/finance_projects.schema.json).

## Answer to the research question

**Kerala2040 must separately report (1) physical whole-system resource cost, (2) State Consolidated Fund flows, (3) KSEBL company cashflows and borrowing, (4) Union/central-PSU funding, (5) private/development capital and guarantees, and (6) consumers' costs and benefits.** They are neither one payer nor one balance sheet. A utility's own-fund investment, for example, can appear in an *agency plan outlay* without proving an equal government grant; Union grant to a state project should not be counted as an independent second project cost. For each proposal, identify **asset owner, cost bearer, revenue recipient, guarantor, repayment obligation, subsidy eligibility and marginal grid-service beneficiary** before quoting a state-budget share.

This first public research milestone establishes financing boundaries and **one verified state-wide audit context plus one publisher-extracted FY2025–26 energy-plan table**, not a Kerala2040 power-sector cost estimate. The latter table still needs visual PDF-page QA because the browser page-render service missed its cached file; its fields remain classified as **published plan proposals / visually unchecked transcription**, never actual State cash.

## Evidence A · an energy-plan proposal is not government expenditure

The Kerala State Planning Board's [Annual Plan Proposals 2025–26](https://spb.kerala.gov.in/sites/default/files/inline-files/Annual%20Plan%20Proposals%202025-26%20%282%29.pdf), **printed pp. 146–147 / PDF page indices 153–154**, contains the following **publisher PDF text-extracted** agency outlays, all in **₹ lakh**. They are **proposals**, not issued expenditure warrants, cash releases or CAG-certified actual payments:

| Agency | FY2025–26 *proposed* energy-plan outlay (₹ lakh) | Fiscal interpretation |
|---|---:|---|
| KSEBL | **108,880** | Its separately printed source components mix utility own fund / externally aided / State Plan |
| ANERT | **5,110** | Agency outlay; specific state/Union/other funding proportions must be verified |
| Electrical Inspectorate | **836** | Agency outlay; cash drawdown not established |
| EMC | **850** | Agency outlay; cash drawdown not established |
| **Energy sector total** | **115,676** | Sum of the four proposed entries, not “Kerala taxpayers paid this much” |

The proposal splits the KSEBL line into **₹104,218 lakh in “KSEBL’s own fund schemes”; ₹540 lakh “Externally Aided Project”; and ₹4,122 lakh “State Plan scheme of KSEBL.”** These components reconcile to **108,880 lakh**. The *text* directly supports this planned categorical separation but does not say that the State Plan number was actually released, that the external component is a grant rather than a loan, or that all agency outlays are fresh state budget payments. No inferences about current KSEBL financing practice follow automatically from this one proposal document.

**This budget proposal remains an unverified actual-expenditure input: the source is a plan document, not Treasury spending.**

**Outstanding document QA:** page-rendering/screenshot verification of the publisher PDF returned a cache miss; the supplied figures are **not promoted as visually authenticated tables** until the relevant pages can be checked against the original layout. Store the exact source and page location; do not misstate them as an expenditure account.

## Evidence B · statewide fiscal setting (FY2024–25, not a power-sector earmark)

The CAG's [Kerala State Finances Audit Report 2024–25, Chapter I](https://www.digitalreports.cag.gov.in/kerala/chapter/1), §§1.4.2 and 1.4.6, provides this distinct **whole-State** context:

| Item and date | State Finance Accounts | CAG post-audit | Boundary |
|---|---:|---:|---|
| FY2024–25 fiscal deficit, ₹ crore | **48,248.14** | **48,510.20** | Two accounting descriptions of one FY, **not additive** |
| FY2024–25 fiscal deficit, % GSDP | **3.86%** | **3.89%** | Neither is an energy-sector budget |
| State overall liabilities, **31 March 2025**, ₹ crore | **445,901.49** | **446,163.55** | State-wide year-end stock; **not project capital available** |
| State overall liabilities, % GSDP | **35.71%** | **35.74%** | Distinct from KSEBL obligations |
| State outstanding guarantees, **31 March 2025**, ₹ crore | **74,297.58** | Not separately assigned here | State-wide *contingent exposure*, **not paid debt, annual cost, KSEBL finance or capital commitment for the project** |

The CAG reports that delayed/non-furnished guarantees records hindered assurance on parts of guarantee management. The State government's January 2026 response said a Guarantee Redemption Fund was notified in August 2025 and that ₹1,250 crore was invested in FY2025–26, while audit queried the earlier absence; these are **attributed findings and response, not independent project funding data**. Do not multiply the state-wide guarantee total by an assumed “energy sector share”; request a named guarantee-by-beneficiary/loan register or verify public audited statements first.

**Factual interpretation:** the state-wide accounts establish that fiscal commitments and contingent risk matter when designing scenarios; they **do not** establish that a particular energy project is or is not fiscally possible, nor prescribe a political choice.

## Six funding structures to model, *not claims that a particular scheme is approved*

| Proposed finance case | Whose cash goes in? | Principal contractual question |
|---|---|---|
| F1 · State-grant asset | Kerala budget allocation **then actual release** | Is it capital grant, equity, a repayable advance or subsidy? Where is the asset held? |
| F2 · Utility asset | KSEBL own funds / documented KSEBL debt | Who carries debt service and what does KSERC permit in tariff recovery? |
| F3 · Union/central-PSU | Named central scheme or central-PSU balance sheet | Is the **asset and beneficiary** eligible and is there a sanction with matching-share conditions? |
| F4 · Private/PPA | Project sponsor equity and debt | Who bears construction, resource, curtailment, off-taker, land, payment and termination risk? |
| F5 · Prosumer/aggregator | Customer/aggregator own capital, conditional subsidy | Who receives tariff credits; how are distribution and vulnerable customers affected? |
| F6 · Blended | Non-overlapping contributions of the above | Is one project's cost or inter-agency transfer being entered more than once? |

**No assumption that all cases are equally available to every technology.** Separate ownership of a rooftop system from ownership of grid storage and from procurement of electricity. Never book **Union announced programme size** as Kerala-specific sanction. Do not book an uncalled guarantee at face value as current exchequer expenditure.

## Flow hierarchy and reproducible numerical intake

Project physical cost and money movements must be separate tables:

```text
 TECHNOLOGY / PHYSICAL ECONOMIC BOUNDARY
   Annual capex + O&M + fuel/power + replacement + end-of-life
                 │ (one project cost)
       ┌─────────┴─────────┐
       │ FINANCING / TRANSFERS / RISK  (not additional project costs)
       ├─ Kerala treasury: grant / equity / loan / subsidy / guarantee IF invoked
       ├─ KSEBL: own funds / utility borrowing / utility purchase contract
       ├─ Union / central PSU: actually approved scheme and asset ownership
       ├─ private / development: equity, loan, return and covenants
       └─ consumer: tariff / customer capex / avoided bill / resilience
                 │
          WHO PAYS  ≠  WHO OWNS  ≠  WHO BENEFITS
```

Every project requires `project_id`, technology, source vintage, price year, common period, unit, asset ownership, current/realised funding, planned **BE vs RE vs actual expenditure**, cash recipient, debtor, lender, guarantor, regulated recovery, operation and replacement responsibility, and publication rights. The new register lists mandatory fields; the existing [project schema](../schemas/finance_projects.schema.json) is only a permissive starting template, not proof those fields are populated.

Use these **non-numerical** accounting identities with a fixed period, currency, price basis and project boundary:

1. **Investment financing closure:** incremental capex = *disjoint* net paid-in state grants + Union grants + project equity + external debt + other **verified** project resources. Exclude an internal transfer from separately inflating both sides. Identical amounts appearing in State and recipient-utility accounts are the **same transfer**, not two external investments.
2. **Fiscal exposure:** State cash expenditure = actual grants/subsidies/paid equity + verified paid debt support + invoked guarantee payments – actual recoveries; show *outstanding uncalled guarantees as a separate stock and contingent risk*, not a paid expenditure.
3. **Utility finance:** KSEBL cash requirement = actual asset investment + procurement + O&M + debt service – utility revenues – truly received support; identify tariff/regulatory treatment. Do not infer tariff impacts from wholesale import MU alone.
4. **Economic vs financial value:** Whole-system NPV values actual incremental physical resources, while actor-level cashflow includes transfers. A grant may change the payer and project bankability **without reducing physical capex**.
5. **Avoided import spend:** needs a dated *counterfactual marginal procurement* source, matching MWh and contracts. The pre-existing [historical electricity study](CET_HISTORICAL_ELECTRICITY_STORY_2026_09_24.md) reports net-import *energy shares* and explicitly cannot supply the required procurement ₹/MWh.

## Where the original plan is still missing primary evidence

| Acquisition | Minimum authenticated fields | Why finance work stops here |
|---|---|---|
| Finance Department / published budget heads | Demand XXXIX Power, annual BE/RE/actual, state funding by account/scheme, sanction, release, utilisation and reappropriation; FY2020–21 onward | Reconstruct comparable **state treasury** time series |
| KSEBL audited annual accounts | FY and entity boundary, own-fund expenditure, capex, grants, equity, borrowing, power purchase costs, cash flow and audited revisions | Reconstruct **utility** cash and debt ledger |
| KSERC tariff/ARR/true-up and investment orders | Order date, petition vs approved vs actual cost, depreciation, regulated return, power purchase, tariffs and subsidies | Link project financing to **actual regulated recovery**, not simply announced cost |
| Government guarantee register and KSEBL-specific notes | Beneficiary, issue date, loan, outstanding, commission, invocation, risk rating where public | Assign *actual beneficiary-specific* contingent exposure |
| Union/central-PSU sanction records | Scheme, project, total amount, Kerala share, Union share, matched release, conditions and expiry | Avoid treating generic scheme availability as project finance |
| Technology-specific project estimates | Site and vintage, project ownership, source-approved costs, resource/grid/ecology eligibility, noncommercial benefits | Admit a project into priced 2040 scenarios |

**The request to the Secretariat should be for the right public demand/major heads and crosswalk between allocation, treasury release and booked actuals; no personal access to internal or confidential documents is needed.** Public audit, Economic Review and investor-finance sources remain independent source lines.

## Unresolved / next concrete task

1. Visually review the publisher's FY2025–26 plan table, then seek published BE/RE/actual against identical line heads.
2. Locate and review KSEBL **audited** FY2024–25 (or latest equivalent) finances and relevant **KSERC orders**, preserving petitioner claim vs regulatory allowance vs actual.
3. Populate **one** uniquely identified, sourced project financing record. If any cashflow or source boundary is unavailable, keep it null.
4. Only after price-year harmonisation, source-calibrated capex and validated technology/network limits should WP8 numerical stress tests be connected to PyPSA.

**CET-safe conclusion:** “Public planning documents distinguish utility own-fund proposals from State Plan and externally aided amounts. Kerala2040 treats State cash, KSEBL accounts, central support, private investment and consumer outcomes as separate ledgers. A public CAG audit establishes the statewide fiscal setting, but no 2040 energy-sector funding share or tariff/cost claim has been inferred from it.”