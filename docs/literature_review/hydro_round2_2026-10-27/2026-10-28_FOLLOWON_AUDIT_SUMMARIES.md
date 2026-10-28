# Kerala2040 — Follow-on hydropower and flood-management scientific reviews (28 October 2026)

**Scope:** Authored, source-critical *public summaries* of previously completed private full-evidence dossiers. This page does **not** reproduce the full audit PDFs, original copyrighted publications, page images, underlying model data, or all scientific findings. Audit artifacts remain preserved locally pending remote transfer to the separately private source-archive repository. Do not cite a GitHub commit of this summary as proof that binary source evidence was uploaded.

## HR07 — Suresh et al. (2024), satellite reservoir operations
- Original catalogue ID: **HR07**; DOI: 10.1016/j.rse.2024.114149; Kerala; priority A.
- Two separately examined versions: a 24-page published article and a 56-page accepted manuscript. The accepted manuscript has appendix figures and filtering sensitivity comparisons not reproduced as full figures in the shorter source version.
- Source-critical distinctions: reservoir water-surface area is not storage-volume fraction; satellite/model-estimated outflow is not a directly measured gate opening; flow-rate versus storage-change equations require consistent time units; more smoothed/filtered correlations can mask amplitude errors.
- Model decision: useful for reservoir filling chronology and hypotheses for monitoring, **not** direct calibration of individual turbine discharge, flood-control benefits, gate openings or reservoir dispatch. The RAT and underlying observations were not reproduced independently.
- Evidence location: private HR07 accepted-manuscript full page/figure audit and accompanying published-paper evidence (not a public binary archive).

## HR12 — Thomas et al. (2025), Kerala CMIP6–VIC hydrology
- Catalogue: **HR12**, priority A; DOI: 10.1016/j.jenvman.2025.125252; 20-page article, nine CMIP6 GCMs, 25 spatial grid cells (approximately 0.5-degree VIC model), SSP245 and SSP585.
- Reported broad direction: wetter monsoon/extreme runoff and possible near-future pre-monsoon runoff reductions in Western Ghats headwaters. The 2022–2047 scenario period includes 2040, but is not an individual-year prediction.
- **Direct table discrepancy, PDF p. 9:** CF = 1.01 in Table 2 for summer days indicates approximately a 1% relative increase, not the accompanying prose's approximately 10%.
- Cautions: a grid's total runoff is not observed dam inflow or dependable hydroelectric generation; one GCM realization each; raw CMIP6/VIC simulations and figures in the supplementary source were not independently reproduced.
- Admission: high-priority climate-scenario evidence, but apply uncertainty and spatial downscaling before reservoir-level parameterization.

## HR29 — Jin et al. (2024), hydro–wind–solar peak shaving
- Catalogue: **HR29**, priority A; DOI: 10.1016/j.energy.2024.132283; 16-page article, six Lancang River cascade hydroplants and two destination power grids in China.
- Method: chance-constrained hydro–wind–solar optimization; nested monthly/typical-day approach; mixed-integer linearized model with hydrological and transmission constraints.
- **Direct inconsistency, PDF p. 12:** reported 169,453.13 MW aggregate wind-plus-solar capacity in the 14-GW transmission scenario contrasts with the abstract's approximately 17,000 MW and model capacity-range specification; do not silently correct the printed value.
- **Independent Table 2 arithmetic, PDF p. 13:** 76,889 / 92,013 = approximately 0.836, which ordinarily rounds to 0.84, rather than the printed 0.83. Report may use underlying unprinted precision, but the published integers do not produce that value at two decimals.
- Model implication: generation can decrease when hydropower provides integration flexibility; installed MW alone is an unreliable measure of flexibility. Authors' MILP inputs and outcomes were not independently rerun.

## HR40 — Wang et al. (2021), forecast-reliability reservoir operations
- Catalogue: **HR40**, priority B; DOI: 10.1016/j.jhydrol.2021.126017; 13-page article, Wan'an Reservoir, China; 12 historical flood hydrographs; 24-hour baseline reliable forecast horizon.
- Reported 12-event simulations: releases exceeding 8,800 m³/s fall from an average 11.11% under the baseline rule to 0% under Three-OR; reported mean generation measure increases from 175.95 to 187.94 (approximately 6.81%). Four floods have lower generation individually.
- Audit cautions: 0% simulated exceedances across selected hydrographs is not zero prospective flood risk. The appendix's separate nonnegative second derivatives do not by themselves prove full joint convexity on an unrestricted domain. Flow-volume unit conversion and energy scale require confirmation from authors' model inputs.
- Admission: transferable algorithmic concept, not transferable numerical benefit or certified levee-protection result.

## EXT01 — Padikkal et al. (2020), Kerala flood governance
- Extra source outside the original 40-item HR catalogue; seven-page *short communication*, not an original hydrological model study.
- **Table 1, PDF p. 2:** sums of three printed monthly rows are 1,663.5 mm (normal) and 2,365.6 mm (actual), but printed total values are 1,649.5 mm and 2,346.6 mm, respectively. Percentage excess remains near 42% with either total pair, but rows and totals cannot both be correct.
- **Figure 1, PDF p. 2:** a bar chart displays rainfall in mm and percent departure on one numerical axis, reducing interpretability.
- The manuscript's categorical assertion that Kerala reservoir management did not worsen the 2018 flood cannot be established from aggregate inflow-minus-release volumes alone. Requires time-resolved releases, catchment routing and operating counterfactuals; treat competing analyses according to their publication/review status.
- Governance relevance: water data access, interagency data sharing, integrated basin-level planning, KWRIS proposal and uncertainty-aware operations.

## Cross-paper use in Kerala2040

1. Preserve **observed, simulated, remotely inferred, scenario-projected, and proposed policy** evidence as distinct types. Do not turn one type into another without a validation step.
2. For 2040, stress-test seasonality and reservoir-level inflow using climate ensembles, flood risk, minimum ecological flows and feasible generation constraints, not only net rainfall changes.
3. Separate forecast-informed flood operation (HR07/HR40/EXT01) from hydropower flexibility economics (HR29) and long-term climate hazard assessment (HR12).
4. Store and compare all audit versions without overwriting historical records. Fix numerical errors only in *our own derived calculations*, preserving the article's printed values and the discrepancy register.
5. Private evidence archive state as of this register: local ZIP integrity confirmed; binary uploads to private GitHub Release **not yet established**. Publicly committed summaries are not substitutes for the full evidence dossiers.
