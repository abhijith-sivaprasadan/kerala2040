# Scientific poster draft 05: evidence and reading notes

Reviewed 27 September 2026. Output: `Kerala2040_CET2026_Scientific_Poster_v5.pdf`.
The main narrative follows the supplied A0 scientific-poster reference. Displayed output values use approximately two significant figures; plot coordinates and colour intensities retain unrounded source values. No research result has been recalculated or changed.

## Repository review

- Main: `49acde2877e4d58f91d471bacb82cc3dab7ca1f4` (KSEB monthly acquisition/parser/model-input pipeline v1.5). Earlier source-package gate: `022dfe24bdd71994bb2314ab05eb065a1c964701`.
- New source checkpoint, not merged at review: [PR105](https://github.com/abhijith-sivaprasadan/kerala2040/pull/105), head `3b3cda8ee69c5e4d14b173205ef0b2d53d433658`.
- [Acquisition workflow 36287336913](https://github.com/abhijith-sivaprasadan/kerala2040/actions/runs/36287336913) completed its diagnostic workflow, but workbook acquisition remained blocked. Its reports state `failed: 12` and `ready_for_content_schema_audit: false`; a successful Actions status is not successful data acquisition.
- V1.5 software implements acquisition, semantic XLS/XLSX parsing, a complete-source gate and a gated 12-case physical-model runner. It does not establish completed new model results. Official inputs require 365 unique storage/inflow records; optimisation uses 364 daily transitions.
- PR105 records recovered LRIS watershed, drainage and waterbody geometry. Natural/intercepted Idukki catchments, Phase-5 weights and the ERA5 Phase-5 run remain unadmitted. Rejected catchment reconstructions are not plotted as accepted geography.

The poster therefore retains the completed v1.3 numerical results and updates the research-status text. It does not claim a new physical run or a validated catchment.

## Figure provenance and scope

| Panel | Published input | Interpretation |
|---|---|---|
| A | `daily-balance.json`, `baseline-summary.json` | FY2024-25, 354 observed days, 11 missing. Monthly available-day averages; not reconstructed monthly totals. 73.8108% observed net-import share is displayed as 74%. |
| B | `research-ledger.json`, solar_phase1 aggregate | GSA2 1999-2018 monthly marginal source-pixel medians; not measured plant generation. |
| C | `wp6-ev-pilot.json` | Synthetic three-vehicle depot; stepwise hourly power for all 24 hours. Same service, deadlines met, 137.622222 kWh total site energy in each case. No statewide fleet claim. |
| D | `import-economics.json` | v1.0 lower FY2030 demand; full 4,455 MW transfer; high renewable envelope; low battery cost. Import-price proxies expressed in real FY2021-22 INR. Partial investment/import economics, not project finance or total system cost. |
| E | `idukki-reservoir.json` | v1.3, 364 days / 8,736 hours. Paired points compare the same-horizon 1-day timing case with the stateful Idukki case. The 30-day comparison remains available in the source, but is omitted from this simplified figure. |
| F | `hydro-interday.json` | v1.2, 365 days / 8,760 hours. Reference FY2030-31 demand, full available hydro, reference renewables, low battery cost, KSEBL import-price proxy. Nested synthetic windows preserve 7,430,719.8 MWh annual hydro energy. |

### Panel E exact source values (GWh)

| Transfer | Same-horizon 1-day | Same-horizon 30-day (not plotted) | Stateful Idukki |
|---|---:|---:|---:|
| 100% / 4,455 MW | 11.751 | 0.160 | 0.160 |
| 80% / 3,564 MW | 1,178.137 | 955.376 | 367.143 |
| 60% / 2,673 MW | 5,542.266 | 5,425.698 | 5,131.227 |

The 69% reduction uses unrounded values: `100 * (1 - 367.143 / 1178.137) = 68.837%` (approximately). All E cases share reference FY2030-31 demand, full Idukki availability, reference renewables, low battery cost and the KSEBL purchase-price proxy. Eleven generation gaps and eleven storage gaps are interpolated inside this pilot only. Its water input is a reconstructed net balance, not observed catchment inflow; non-turbine release is an endogenous slack, not observed spill. There is no validated head-dependent efficiency, cascade operation or final capacity plan.

Do not compare E and F as a controlled improvement across versions: their horizons and constraints differ. Plain study subtitles show the 364-day and 365-day horizons; paired points and a heatmap distinguish the experiments visually.

## Reproduction

Build the website data bundle with `scripts/build_site.py`, then run `scripts/build_cet_poster.py` with ReportLab and the configured Arial fonts. The PDF uses native vector marks and selectable text. QR integration and final conference print specifications remain for the later poster pass.
