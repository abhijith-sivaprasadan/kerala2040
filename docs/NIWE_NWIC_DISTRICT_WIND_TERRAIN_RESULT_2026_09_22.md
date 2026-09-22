# Completed NWIC district-level NIWE 150 m × GLO-90 DSM analysis — 22 September 2026

**Outcome: all 200,692 original NWIC-state-clipped NIWE centres uniquely assigned to the 14 original NWIC Kerala district polygons, with zero unassigned and zero multiply assigned.** This closes the *descriptive administrative partition*, not any land eligibility or capacity gate. [Public-safe aggregate](../data/evidence/gis/niwe_nwic_district_wind_terrain_2026_09_22.json).

## Reproducible source and CRS

- User-supplied original `district_nwic_geojson.zip`, SHA-256 `44c734cc72139f2447dcebfe2791cac862dc5ba265e158912d797cf3410d5c37`; GeoJSON member `district_nwic.GeoJSON`, SHA-256 `2b27a478e24d8c51b0655e74ce3f4f880e75c752e4597550d6fc925ed06ac201`. National collection: 733 district features; 14 identified by `state_name == Kerala` and `district` property, without a geographic-box shortcut. The declared source CRS is EPSG:7755, transformed with XY order to EPSG:4326 for source-point tests. The dataset has a `src_agency` field identifying Survey of India. The original source vintage and reuse rights are **not independently verified**.
- Original-NIWE-derived Kerala clip SHA-256 `dd9d00e67da0dac3a9258daad18c35f71075815f7b64cea4b290a36c6e9b9634`, original-derived Copernicus GLO-90 **surface** slope SHA-256 `72551921c99eb563abe37c9502d4e4c592c3be667f31459296c90e48be9436f7`. Input rows and source raster remain private.
- The original [statewide NIWE × DSM analysis](NIWE_150M_KERALA_TERRAIN_REAL_DATA_RESULT_2026_09_22.md) remains the independent numerical reference. All **17** existing district-workflow reconciliation checks pass, including the statewide wind-speed classes, finite/missing slope totals and every cell of the 4×4 hypothetical threshold matrix. No point locations or original NWIC polygon coordinates are published.

| Exactly source-defined population | Point centres |
|---|---:|
| Original NWIC Kerala NIWE population | **200,692** |
| Uniquely matched to one NWIC Kerala district | **200,692** |
| Outside all 14 NWIC districts | **0** |
| Overlap between districts at source centres | **0** |
| Finite sampled DSM slope | **199,853** |
| Missing sampled DSM slope | **839** |

The original LRIS 2.0 geometry [left 330 of the same 200,692 points unassigned](NIWE_LRIS_DISTRICT_PARTITION_QA_2026_09_22.md). The NWIC district polygons close that partition, but **differences are not limited to those 330 points**: relative to LRIS, Idukki's assigned count changes by −930, Ernakulam's by +708 and Pathanamthitta's by +254. The two sources draw different district boundaries; do not substitute one source's reported district counts for the other without naming the geometry used.

## District descriptive results

The source's **modelled mean wind speed at 150 m** and sampled **GLO-90 digital surface slope** are summarized by NIWE point centre, not by land parcel, grid MW, turbine pad or wind-farm area.

| District | NIWE centres | Valid slope | Median speed, m/s | Median DSM slope, ° |
|---|---:|---:|---:|---:|
| Alappuzha | 7,318 | 7,280 | 3.342 | 0.697 |
| Ernakulam | 15,770 | 15,735 | 2.961 | 3.193 |
| Idukki | 22,448 | 22,328 | 5.568 | 12.761 |
| Kannur | 15,358 | 15,280 | 3.321 | 4.982 |
| Kasaragod | 10,337 | 10,210 | 3.821 | 4.999 |
| Kollam | 12,818 | 12,771 | 4.892 | 4.646 |
| Kottayam | 11,358 | 11,358 | 3.004 | 4.183 |
| Kozhikode | 12,144 | 12,101 | 3.092 | 4.687 |
| Malappuram | 18,390 | 18,330 | 3.705 | 4.501 |
| Palakkad | 23,117 | 23,020 | 6.412 | 4.293 |
| Pathanamthitta | 13,637 | 13,619 | 3.734 | 9.521 |
| Thiruvananthapuram | 11,257 | 11,169 | 4.830 | 4.444 |
| Thrissur | 15,671 | 15,641 | 4.865 | 3.039 |
| Wayanad | 11,069 | 11,011 | 4.894 | 6.268 |

The public aggregate preserves each district's 4×4 counts for minimum modelled wind speeds 5, 6, 7, 8 m/s and maximum DSM surface slopes 5°, 10°, 15°, 20°. Their sum reproduces the statewide ≥7 m/s and ≤10° example **8,637 point centres**. Neither these counts nor the source nominal ~500 m resource spacing establish land area or installable power.

## What remains unresolved

An entirely assigned administrative point population does **not** verify notified forest, wildlife, paddy, wetland or ESZ geometry; class-coded land-cover vintage; access roads, slope at actual foundations, land rights, grid deliverability, measured wind chronology or turbine yield. Source-vintage and redistribution-rights review also remains open. Maintain `eligible_area_km2=null`, `feasible_capacity_MW=null`, `hourly_generation_validated=false` and `model_admitted=false`.

The earlier [LRIS partition QA](NIWE_LRIS_DISTRICT_PARTITION_QA_2026_09_22.md) remains as a historical cross-source finding, **not** an active unassigned-point issue in the NWIC-based analysis.
