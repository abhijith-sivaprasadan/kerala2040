# Loose uploaded wind and wind–PV CSVs: source-scoped intake

**Reviewed 22 September 2026.** These 20 user-uploaded CSVs are supporting evidence, **not** the independently clipped `NIWE_150m_Kerala_NWIC_point_centres.csv.gz` needed by the onshore resource × terrain workflow. Do not publish original rows until redistribution permissions are checked. This note does not supersede the independently reviewed NIWE 2019 original PDF or the prior NWDP original-source assessment.

## 1. NWDP Kerala station telemetry: real records, not a complete hourly profile

| Supplied filename | Exact supplied bytes / SHA256 | Actual content |
|---|---|---|
| `wind_speed_tel_hr_kerala_sw_kl_1970_2025.csv` | 30,324,625 bytes; `0d4209be0f9984b20bb82457d03d5b8592d49eda10272d9e80c6ee72cd30b792` | 217,754 numeric wind-speed records, **13 stations / 11 district labels**, `Telemetry Hourly Wind Speed (Km/Hr)` |
| `wind_speed_tel_hr_kerala_sw_kl_2026_2030.csv` | 229 bytes; `f708788abf775dbefede5f03116a803a472124578eed021c59277c3e1890eeee` | Header only; **zero observations**, so no 2026–2030 profile or forecast |

Parse `Data Acquisition Time` as day-first. The actual timestamp range in the historical CSV is **2015-01-01 03:00 to 2025-03-10 02:30**, not the 1970–2025 filename window. Year counts are **2015: 13; 2017: 57; 2018: 45; 2021: 112,658; 2022: 94,035; 2024: 10,909; 2025: 37**; no records for 2023. Station plus exact timestamp has no duplicates. Wind-speed numeric cells are finite/non-null in this source inspection, with **0.0–22.0 km/h**, pooled median **1.5 km/h**, **not** wind speed at a turbine's 150-m hub height.

The previously documented FY2024–25 window (2024-04-01 inclusive through 2025-04-01 exclusive) contains **10,946 records from only AMBALAPUZHA (5,096) and KULAMAVU (5,850)**, consistent with [the previous consolidated numeric evidence](../data/evidence/solar/solar_wind_consolidated_numeric_2026_09_22.json). Most adjacent observations within most stations are **0.5 hours apart**, contrary to the `Hourly` field/filename; there are discontinuities. Timestamp timezone, instrument height/calibration, station representativeness and complete-year chronology are not proven. Convert km/h to m/s by 3.6 only for like-for-like units, **not** to infer turbine-hub wind.

Geography metadata merits **quarantine, not silent repair**: the `Achencoil` record carries a `Tapi` river/basin label despite Kollam location; `Marayoor` has district `KOZHIKODE` and an east-flowing-river basin description. Several fields use `-` placeholders. Treat the supplied coordinates as unconfirmed source observations; do not geocode them into official grid cells without independent station identity checks. Do not append 13 site records and call them statewide wind validation.

**Classification:** partially relevant station meteorological comparison only; `complete_FY_wind_observations=false`; `NIWE_150m_validated=false`; `model_ready=false`.

## 2. 2019 NIWE **120 m** study tables; do not conflate with 150 m national CSV

The following seven loose tables align by headings and Kerala rows with [the previously original-PDF-verified October 2019 NIWE 120-m atlas review](SOLAR_WIND_PRIMARY_PDF_PAGE_REVIEW_2026_09_22.md):

- `Table_1_Comparison_Indian_Wind_Atlas_2010_vs_Wind_Potent_ugbBI6o.csv`
- `Table_2_Area_Exclusion_Criteria.csv`
- `Table_5_State-wise_Installable_Wind_Potential_gt25pctCUF_SBx907B.csv`
- `Table_6_State-wise_Wind_Potential_WA120-80-30-5_by_CUF_Part1.csv`
- `Table_7_CUF_Matrix_for_Unexploited_Windy_Sites.csv`
- `Table_8_Sensitivity_of_Wind_Potential_gt35pctCUF_vs_Land_PTzS4e8.csv`
- `Table_9_Sensitivity_of_Wind_Potential_gt25pctCUF_Himalay_Xby79or.csv`

These source tables report **Kerala 2,311 MW** (>25% P50 CUF at 120 m) under historical siting, land availability and normalised-turbine assumptions: **474 MW wasteland + 1,495 MW cultivable + 342 MW forest** as study categories; the forest component is **not** a permit or a recommended developable allocation. CUF bins **366 / 193 / 180 / 359 / 1,213 MW** sum to 2,311 MW. The distinct **greenfield 2,297 MW** bins **366 / 193 / 180 / 358 / 1,200 MW** reflect the study's then-existing project exclusions; not today's operating installed capacity and not additional to the 2,311 MW. The study's **>20° slope, >1500 m height and buffered-feature exclusion parameters are historical scenario assumptions, not current Kerala statutory exclusions**. Table 8 is restricted to Andhra Pradesh, Gujarat, Karnataka, Maharashtra and Tamil Nadu; Table 9 addresses Himalayan states—neither provides a new Kerala result.

**Classification:** externally reported 2019 120-m planning benchmark; `NIWE_150m_capacity_from_this=false`; `legally_eligible_MW=false`.

## 3. Other 11 CSVs: method context, not Kerala source calibration

**Six Jafrabad/Gulf of Khambhat, Gujarat LiDAR/coastal-mast tables:** `Table_1_Site_Description_LIDAR.csv`, `Table_2_Site_Description_Jafrabad_Coastal_Mast.csv`, `Table_3_Lidar_Measurement_Characteristics.csv`, `Table_4_Correlation_Coefficient_Lidar_vs_Coastal_Mast.csv`, `Table_5_Wind_Speed_Nov2017_Nov2018_Validated_Synthesized.csv`, and `Table_6_Wind_Power_Density_Nov2017_Nov2018_Validated_Synthesized.csv`. The supplied site table explicitly says **Gujarat**; the LiDAR measurement period is November 2017–November 2018 with **10-minute** interval, but the supplied speed/WPD matrices are monthly summaries. They do **not** validate Kerala 150-m or offshore wind.

**Four bench-scale machine/PV experiments:** `Table_2_2_WRIG_SolarPV.csv`, `Table_2_3_Experimental_results_of_WRIG_system.csv`, `Table_2_4_Experimental_readings_for_solar_PV_system.csv`, `Table_3_1_Experimental_Results_WRIG_SCIG.csv`. These describe rpm, electrical power, power factor, converter losses, battery and PV readings for the respective experiments. No Kerala climatology, project power curve or statewide installed capacity follows.

**One unlabeled annual yield comparison:** `1_FN12iLV.csv` lists named stations and annual wind/solar/hybrid energy per MW, but no explicit Kerala location, original report identity, year/technology assumptions or calibrated hourly source. Keep out of Kerala2040 regional yield claims pending the associated publication/metadata.

## 4. Actual next execution gate

The **separate clipped NIWE 150-m Kerala resource** is still missing from this conversation's available files. Obtain the exact `NIWE_150m_Kerala_NWIC_point_centres.csv.gz`, documented SHA256 `364808dd40751bd5f3e131e86127dbdab73168d1830a682002de5a4c6fdd0dee`, from the user’s local private derived resource clip bundle. The separate **GLO-90 DSM degree-slope raster** is recovered and SHA256-verified as `72551921c99eb563abe37c9502d4e4c592c3be667f31459296c90e48be9436f7`. Run [the source-guarded wind × terrain script](../scripts/audit_kerala_niwe_resource.py) against both, then check point counts/missing-slope diagnostics and private maps. Until that real join succeeds, record zero **completed** new wind–terrain results and do not publish site eligibility, km², installable MW or wind hourly generation.
