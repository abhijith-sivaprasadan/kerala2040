# Kerala2040 · demand and electricity-accounting baseline · source review

**Status: 23 September 2026. Classification: official_reference for Economic Review/KSEBL annual figures; observed for the separate SLDC dated source reports; research interpretation for the proposed analytical scope.** This is a *sector-demand and accounting-boundary source review*, not an hourly load reconstruction, actual purchase-cost calculation or a 2040 forecast.

The first non-wind/solar/hydro research question is: **which Kerala electricity-demand quantities are actually comparable, how are energy and revenue distributed by customer class, and what metered data are required to connect annual customer use to time-of-day system loads and the cost of serving them?**

## Primary sources, exact FY2024–25 boundaries

**Kerala State Planning Board, Economic Review 2025 Volume I, chapter 11, pp. 568–569** (KSEBL attribution):
https://spb.kerala.gov.in/sites/default/files/2026-01/ER%202025%20Volume1%20Eng%20final.pdf

**Economic Review 2025 Volume II, Appendix 11.2.2 and 11.2.3, p. 449** (KSEBL attribution):
https://spb.kerala.gov.in/sites/default/files/2026-01/ER%202025%20Volume%202%20Eng%20final.pdf

These quantities MUST NOT be presented as four estimates of an identically defined 'Kerala demand' series:

| Value (MU) | Published wording / source boundary | Interpretative caution |
|---|---|---|
| **29,311.76** | 2024–25 electrical energy consumption in Kerala, *including open access consumers and consumption against captive generation*, Vol. I p. 569 | Annual reported consumer-side reference, not a measured continuous load curve. |
| **28,544.05** | KSEBL sale of power in Vol. I p. 569 and Vol. II Appendix 11.2.2, *including outside-state trading and sales to other bulk licensees* | Category-table sales total is not exactly Kerala final consumption. |
| **28,879.64** | Vol. II Appendix 11.2.3, *energy sold by KSEBL within State including energy adjusted against captive injection* | Different stated accounting boundary from Appendix 11.2.2. Do not overwrite one with the other. |
| **31,848.07** | Vol. II Appendix 11.2.3, *net energy generated and power purchased by KSEBL* | Utility-specific input for a loss table, not final demand. |
| **32,306.15** | Vol. I Table 11.2.3, *total energy input to Kerala periphery for meeting state consumption including open-access wheeling*, after the report's specified additions and deductions | Supply/input-side reference, not the same as end-use sales, and not a direct estimate of 'imports'. |
| **30,666.2569** | Kerala2040 previously audited SLDC Statistics qualified daily consumption summed over **354 of 365 FY2024–25 dates** | INCOMPLETE observed-date sum. Different SLDC boundary; NEVER annualize or compare as a full-year absolute residual. |

The last SLDC figure and day count are previously audited Kerala2040 research, not newly extracted from the Economic Review; see [SLDC source audit](SLDC_FIVE_SECTION_2019_2026_SOURCE_AUDIT_2026_09_23.md). Do not take differences between the figures above and relabel them as transmission loss, statistical error, unserved energy, net interstate imports or household load. This requires like-for-like metering point, inclusions, temporal completeness and adjustment metadata.

## FY2024–25 KSEBL category evidence

KSEBL's Appendix 11.2.2 labels each share against **its 28,544.05 MU category-table total**, which includes outside-state sale/trading. These category totals are *not* a decomposition of the 29,311.76 MU broad state-consumption reference. The HT & EHT class is not an independently established all-industrial class.

| Official category | Electricity (MU) | Published % of Appendix total | Revenue (Rs crore) |
|---|---:|---:|---:|
| Domestic LT | 13,873.78 | 48.60 | 7,916.84 |
| Commercial LT (includes LT General and LT EV charging) | 4,986.72 | 17.47 | 5,490.38 |
| Public lighting LT | 378.25 | 1.33 | 206.60 |
| Irrigation & Dewatering LT | 426.10 | 1.49 | 153.07 |
| Industrial LT | 1,319.45 | 4.62 | 1,059.51 |
| HT & EHT (source group, do not recode as all industry) | 6,077.97 | 21.29 | 4,902.39 |
| Railway traction (includes KMRL) | 477.26 | 1.67 | 324.03 |
| Licensees / bulk supply | 608.82 | 2.13 | 512.38 |
| Outside-state sale / trading | 395.70 | 1.39 | 296.01 |
| **Published total** | **28,544.05** | — | **20,861.21** |

**A planning interpretation, not an additional observation:** Domestic and commercial LT contribute substantial customer-class annual energy, making measured hourly cooling/household/commercial demand and its evening-peaking behaviour an important independent research stream. The category energy and revenue *cannot* reveal load shape, marginal electricity procurement costs, the welfare effect of tariffs or any customer's exact average bill.

## Concrete next analysis (cannot be completed from annual totals alone)

1. Preserve four separate nodes in the dataset schema: **periphery input**, **state consumer consumption**, **KSEBL in-state sales**, **KSEBL all-category sales/trading**, plus separately keyed SLDC *daily operational* reported consumption. Add owner, period, units, measurement boundary and publication vintage to each.
2. Establish annual category baselines from official appendices across years, keeping the same category taxonomy and explicitly recording reclassifications; do not fit 2040 sector trends on one year's shares.
3. Obtain actual statewide **15-minute/hourly load and import/export MW** for FY2024–25 using [existing SLDC data request](SLDC_DATA_REQUEST_DRAFT.md). This is the P0 prerequisite for timing of residential/commercial evening peaks, net-load and dispatch validation.
4. Use independent category/technology evidence to construct separate, **scenario-labelled** cooling, EV charging, commercial, industry and demand-response hypotheses, with units, uptake, rebound and seasonal constraints. ERA5-Land temperature and dewpoint can be covariates *once source-matched weather arrives*, not replacements for observed demand.
5. Acquire utility purchase-contract/actual settled power costs, annual true-up accounts, tariff categories and network/loss detail before claiming a **cost to serve** figure; sale revenue alone is not cost and category average revenue is not marginal cost.
6. Reconcile like-for-like published volumes, preserve unexplained residuals, and use rolling-origin validation for any predictive demand model. Avoid treating the partial SLDC daily sum as a full-year reference.

**CET use:** this report establishes an official customer-class and accounting baseline with precise limitations. It does NOT claim calibrated 2040 demand, attributable weather effects, measured 8,760-hour load or an affordability ranking.
