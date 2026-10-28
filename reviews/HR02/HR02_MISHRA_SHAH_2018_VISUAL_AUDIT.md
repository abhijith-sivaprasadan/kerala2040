# HR02 — Mishra & Shah (2018): six-page visual and scientific audit

**Published source:** Vimal Mishra and Harsh L. Shah, *Hydroclimatological Perspective of the Kerala Flood of 2018*, *Journal of the Geological Society of India* **92**, 645–650 (November 2018). [DOI 10.1007/s12594-018-1079-3](https://doi.org/10.1007/s12594-018-1079-3).

**Review:** 28 October 2026. **Uploaded PDF:** 6 pages; every page individually rendered at 205 DPI, inspected visually in three readable two-page views with all five multi-panel figures and bibliography. Source SHA-256: `01195db217041c991f0db0abdb6ed89ca06c229a7ce141968e4a8e6e83a5769a`. **28 source findings, 28 numerical/evidence checks, and 12 Kerala2040 actions.** No independent replication of climate data, VIC simulation, spatial statistical inference or dam operations. A separate **8-page scientific audit PDF** and private source-image archive were generated; **they are not committed as binary files to GitHub**.

## Scientific interpretation

The paper shows the contrast between long-term **1951–2017** monsoon trends and unusually severe short-duration rainfall and **VIC-modelled runoff** during August 2018. It uses gridded daily IMD precipitation (native 0.25°), IMD temperature (native 0.5°, interpolated to 0.25°) and NCEP–NCAR wind, modelling grid-cell surface runoff and baseflow using **VIC** with parameters inherited from prior work rather than calibrated anew for Kerala.

Figure 1, PDF page 2, maps reported JJAS drying and warming and declining *modelled* runoff; black stippling shows pointwise Mann–Kendall 5% significance, not independently checked spatial field significance. Figure 2 on page 3 maps trends in annual one-/two-day maxima. Figure 3 on page 4 maps the highly uneven 2018 short-duration extremes and modelled runoff; Figure 4 shows 2018 monsoon precipitation near **2,000 mm** against an approximately **2,050 mm** 95th percentile, while short-period extremes are much more exceptional. Figure 5 on PDF page 5 displays 2018 one-/two-day state-average maxima above historical percentiles; authors state **~30 mm** (one-day) and **~75 mm** (two-day) exceedances.

**The most consequential limit:** lack of positive long-run rainfall trends alone does **not** identify whether natural variability or anthropogenic forcing caused a specific event. The paper does not perform preindustrial versus real-world climate counterfactuals. Nor does it simulate actual 2018 dam-gate operating histories, measured downstream inundation, hydropower generation or reservoir counterfactuals. Its suggestion that reservoir storage and releases might have exacerbated flooding is therefore a question requiring a different empirical test.

## Notable errors and qualifications

- **Historical period inconsistency:** introduction on p1 uses *1851–2017*, Results on p2 uses *1971–2017*, and methodology/figures use *1951–2017*. The intended study interval appears to be **1951–2017 (67 inclusive years)**. Several percentile baselines on pp3–4 instead specify **1951–2015**; the data calculation period needs clarification.
- **Runoff is not gauged discharge:** VIC total runoff is local simulated surface runoff plus baseflow, in equivalent depth (mm). River routing, reservoir diversions and observations are essential before translating it to actual m³/s.
- **Trends and attribution are different tests:** Mann–Kendall/Sen historical trends and maps do not quantify natural versus anthropogenic contributions to the 2018 event. Figure 1 spatial multiple-testing and serial-dependence controls are not detailed.
- **Definite reference error, p6:** Gupta and Nair (2011) urban-flood reference prints DOI `10.1016/j.ajodo.2005.02.022`; independent PubMed check identifies this as **Whetten et al. (2006), an orthodontics study**, not a flood research paper.
- **Other source reliance:** the 75-year and 200-year extreme-rainfall return periods and reservoir-storage commentary cite a **different Mishra et al. (2018)** paper, not calculations reproduced in this six-page text.
- **No independent runoff calibration:** the authors explicitly state that VIC was not calibrated for this Kerala study.

## Numerical reconciliation

| Published statement | Recomputed / qualified result | PDF page |
|---|---|---|
| Historical 1951–2017 | **67 inclusive calendar years**, 66 elapsed years | 1–3 |
| Alternate 1851–2017 | **167 calendar years** (incompatible with intended interval) | 1 |
| Alternate 1971–2017 | **47 calendar years** | 2 |
| 1951–2015 baseline | **65 calendar years** | 3–4 |
| 2018 mean monsoon vs reference p95 | **2,000 vs 2,050 mm**, ~**2.44% below** p95 | 4 |
| 2018 1-/2-day precipitation above p95 | **~30 mm and ~75 mm**, as stated by authors; original samples not reprocessed | 4–5 |
| Rain gauges vs runoff | **IMERG/IMD grid** observational-derived rain, **VIC model runoff**; different data statuses | 1–5 |
| Bibliographic DOI | Listed urban-flood DOI points to an unrelated dental article | 6 |

## Comparison with the five previously fully reviewed hydropower papers

| Paper | Primary aim | Difference from HR02 |
|---|---|---|
| HR01 Sudheer (2019) | HEC-HMS Periyar flood peak and reservoir storage counterfactuals | Actual dam policy scenarios, but no full hydropower accounting |
| HR04 Ryan (2020) | Kakki reservoir release policies | Single outlet rather than Kerala-wide climate trends |
| HR05 Singh (2022) | Periyar HEC hydrologic and inundation routing | Flood mapping, not attribution of climate forcing |
| HR07 Suresh (2024) | Satellite RAT inferred reservoir states and releases | Reservoir operating timing, with peak inflow biases |
| HR08 Das (2025) | Forecast-informed RAT operating scenarios | Different forecast-origin/benchmark and physical constraints |

A closer independent climate-attribution comparator is **HR03 Hunt & Menon (2020)**, *The 2018 Kerala floods: a climate change perspective* (DOI 10.1007/s00382-020-05123-7), which uses alternate-climate simulations. That paper is **not yet visually audited**; its publisher abstract was checked separately. The comparison here does not replace original source conclusions.

## Derived evidence files committed

- [Visual inspection ledger: six pages](HR02_6_page_visual_inspection_ledger.csv)
- [28 scientific findings](HR02_2018_scientific_findings.csv)
- [28 source checks](HR02_2018_numerical_evidence_checks.csv)
- [12 Kerala2040 actions](HR02_2018_Kerala2040_actions.csv)

**Status:** completed source review, not independent VIC or attribution reproduction. The original 1951–2018 gridded data, climate-model implementation, reservoir data and uncertainty studies are not supplied. The generated full scientific audit PDF and full-page source figures remain private conversation downloads; do not redistribute them in a public repo without permission.

