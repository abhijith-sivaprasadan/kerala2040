# Paper A0 — manuscript seed v0.1

**Drafted 28 October 2026 · exploratory research draft, not submission-ready.**  
**Candidate type:** original reproducible-data-methods article *if* novelty and original-source independent validation are established; otherwise technical methods report.  
**Publication programme:** fallback alternative to Paper A, **not** a second simultaneous manuscript commitment.

## Working title

**What Do Kerala's Electricity Statistics Measure? An Audit of Reporting Boundaries, Daily Source Completeness, and Reproducible Energy Accounting**

## Structured abstract — provisional, not peer-reviewed

**Background.** Subnational electricity-system studies frequently combine annually published consumer statistics, utility transactions and dated power-system operation reports. Because their accounting boundaries and temporal coverage differ, numerical comparison can imply inconsistencies that are not physically interpretable.

**Methods.** As an initial feasibility exercise, we constructed a six-variable source ontology from Kerala's *Economic Review 2025* as previously transcribed in the project and existing Kerala State Load Despatch Centre (SLDC) dated statistics. We independently recomputed completeness and an internal daily accounting identity from the repository's processed FY2024–25 CSV, preserving explicitly missing days and rejecting unsupported cross-boundary subtraction.

**Pilot results.** Of 365 FY2024–25 calendar dates, 354 contain processed observed daily reports (96.9863%) and 11 are explicitly missing. The observed-day operational-consumption sum is 30,666.2569 MU, with 8,031.2393 MU internal generation and 22,635.0183 MU net imports; daily arithmetic residuals are within 0.0001 MU. Annual published energy quantities have materially different original reporting definitions and cannot presently be reconciled as one common demand measure.

**Limitations and implications.** This computation does not independently authenticate original daily HTML responses or reproduce page-level original Economic Review transcriptions. It demonstrates a reproducible pilot for source eligibility, not validated statewide losses, causally attributable discrepancy, universal source-audit methodology or new forecasting skill. A broader original-byte, independent-extraction and nearest-literature comparison is essential before a scholarly novelty claim.

**Keywords (provisional):** Kerala; electricity statistics; reproducibility; data provenance; reporting boundary; source completeness; energy accounting.

## 1. Introduction (working draft)

The credibility of electricity-transition modelling depends in part on whether the underlying demand, supply and interchange observations refer to the same physical quantity. Published electricity statistics may describe energy consumed by customers, energy sold by a licensed utility, energy delivered at the system boundary, contracted or scheduled procurement, or operationally reported consumption. Such measurements are not necessarily interchangeable, even when expressed in million units (MU) for the same financial year. Differences may arise from customer coverage, open-access and captive-generation adjustments, utility and state boundaries, system losses, revision rules and temporal completeness. These possibilities require a definition-level comparison before numerical discrepancies are interpreted as energy shortages or measurement errors.

Kerala offers a useful case because the Kerala State Planning Board's *Economic Review 2025* reports multiple FY2024–25 annual electricity quantities with different labels and accounting inclusions, while Kerala SLDC publishes dated operational summaries. The existing Kerala2040 source audits identify both these annual quantities and a curated series of daily reports covering 2019–2026. In particular, eleven FY2024–25 report dates were not observed in the previously processed daily series. As a result, its observed-day operational-consumption sum cannot be treated as an independently observed complete-financial-year consumption total.

Prior energy-demand research has already modelled Kerala alongside other Indian states using daily Grid-India supply data and weather reanalysis, including Hunt and Bloomfield (2025). The present prospective study therefore does not seek to establish that Kerala was previously unstudied or that ERA5 modelling itself is new. Its narrower potential contribution is an explicitly testable source-eligibility and extraction-verification procedure for electricity-system evidence. Whether such a procedure offers transferable scientific value beyond existing documentation and data-validation practice remains an open question.

We first present a limited feasibility pilot to determine whether existing processed daily records can be rechecked without imputation, whether financial-year coverage can be represented precisely, and whether a source ontology can prevent misleading cross-boundary comparisons. This pilot is followed in the planned full study by independent original-document extraction and predeclared error-adjudication tests, which have **not yet been performed**.

## 2. Data and methods (pilot)

### 2.1 Source inventory and accounting definitions

Six reported FY2024–25 electricity quantities were registered independently rather than merged into a canonical statewide "demand" number. The first five come from the previously authored Economic Review source audit, which identifies the official reporting institution, volume, section/appendix and published metric. The sixth comes from the processed SLDC daily operational Statistics data.

Each source register entry contains an identifier, financial-year label, publication or reporting body, original locator, numeric amount (MU), variable definition, customer/physical boundary, source coverage and current assurance grade. Entries are admissible for direct physical subtraction only if geography, measurement target, actual period, adjustments and revision status are shown to match. Neither common units nor common financial-year labels prove admissibility.

### 2.2 Daily completeness

The processable unit is a calendar day with an explicit source status of `observed` or `missing`. The analysis checks that the source contains each day of the financial year exactly once. Missing-source dates are retained as missing, without assigning zero consumption or extrapolating total annual MU. Monthly completeness is the ratio of observed source-day counts to calendar-day counts.

### 2.3 Daily internal-accounting verification

For each observed day we re-evaluate the signed identity

```text
residual_mu = internal_generation_mu + net_import_mu - consumption_mu
```

using decimal arithmetic and a prespecified tolerance of 0.00011 MU for the processed file's displayed precision. `hydro_mu` is tracked as a component of internal generation and is not double-counted. The script checks that each day's stored residual is consistent with recalculation, that no observed record has a missing source-hash reference, and that missing calendar days are not silently filled.

This is **a processed-data reproducibility test**. The original HTML SHA and source-date verification was undertaken in earlier Kerala2040 work and must be replicated from actual original source bytes in the full A0 investigation.

### 2.4 Deliberately blocked comparisons

We mark four source pairs as ineligible for direct differences: broad annual state consumption versus incomplete SLDC daily operations; all-category KSEBL sales versus within-state adjusted sales; consumer consumption versus Kerala-periphery input; and within-state utility sales versus generation plus purchases. Blocked comparisons have no numerical "difference MU" result, precisely because such a derived figure could falsely appear meaningful.

## 3. Pilot results (processed CSV recomputation)

The public FY2024–25 processed input contains 365 unique financial-year dates, of which 354 are observed and 11 missing (96.9863% coverage). The first four months, April–July 2024, contain no missing reports in the processed calendar; the remaining missing dates are distributed across August 2024–March 2025, with the largest count (three) in March 2025.

The observed-source daily series sums to 30,666.2569 MU reported operational consumption, 8,031.2393 MU internal generation and 22,635.0183 MU net import. The maximum daily signed residual is 0.0001 MU in absolute value. The aggregate of displayed rounded daily values yields a +0.0007 MU difference between the generation-plus-import sum and reported operational consumption; this is arithmetic at reported precision, **not** a cross-publisher energy-loss estimate.

In the separate annual source register, five other published FY2024–25 amounts are assigned to consumer-side, utility sales and system-input categories. The analysis does **not** infer that any of these figures is inaccurate merely because they differ from the partial SLDC sum. In the absence of a complete, verified boundary transformation, our proposed framework rejects the subtraction as an interpretive operation.

See [pilot source ledger](TABLE_A0_01_reporting_boundary_ledger.csv), [monthly table](TABLE_A0_02_monthly_source_coverage.csv), and [admissibility matrix](TABLE_A0_03_comparison_admissibility.csv). Methodological qualifiers and additional source-level anomalies are detailed in [the pilot report](PILOT_REPORT_2026-10-28.md).

## 4. Discussion and limitations (to be expanded only after original-source work)

The exercise illustrates the importance of distinguishing *internal consistency* from *cross-source comparability*. The very small daily balance residuals suggest stable arithmetic within the existing processed source representation, while the large differences between differently labelled published annual quantities remain uninterpretable as common-boundary residuals. Neither fact establishes the accuracy of every original SLDC report or the exact reconciliation between Kerala's consumption and utility supply.

The main methodological limitations are explicit. First, a second independent original-source extraction has not been undertaken, so extraction error cannot be ruled out. Second, the Economic Review numbers originate here from a prior source-review transcription, not a new original PDF inspection. Third, only one fiscal-year processed public daily file has undergone this new arithmetic calculation, which does not demonstrate generalization to evolving source schemas or publisher revisions. Fourth, the scientific novelty of the approach has not been compared against a sufficiently broad set of full-text source-quality and data-interoperability studies.

The planned full study must distinguish original publisher error, digitization/parsing error, missing publication, genuinely changed scope, rounding, subsequent revision and lawful inability to inspect or redistribute source bytes. A valid null result—in which all detected boundaries and errors are already documented and the method adds little independently verifiable information—should lead to a well-labelled technical report rather than a claim of novel research.

## References and verification to complete

1. Kerala State Planning Board. *Economic Review 2025*, Volumes I and II, electricity chapter and appendices identified in the existing Kerala2040 audit. **Pages and source edition need independent original-PDF verification for manuscript claims.**
2. Kerala SLDC. Daily operational statistics, FY2024–25 source dates. **Earlier archive hashes and source-date evidence exist; original HTML not re-opened in this pilot.**
3. Hunt, K. M. R. & Bloomfield, H. C. (2025). *Building and explaining data-driven energy demand models for Indian states.* *Environmental Research: Energy*, 2(2), 025003. https://doi.org/10.1088/2753-3751/adc7bc. **Direct prior-art work, not independent replication in this pilot.**
4. Porwal et al. (2026). *Granular Analysis of Weather-Influenced Electricity Demand in Indian States*. IEEE IC3ECSBHI proceedings. https://doi.org/10.1109/IC3ECSBHI67834.2026.11468867. **Full methods pending legitimate access.**
5. Methods/data-provenance literature **to be added after minimum ten fully critically reviewed relevant papers**; do not fabricate bibliographic support.

*This is the beginning of manuscript text, not a validated independent A0 paper or a submitted research result.*
