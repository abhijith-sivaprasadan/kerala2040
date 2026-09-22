# LRIS district partition × NIWE 150 m: real-data QA (22 September 2026)

**Status: incomplete descriptive district partition, not an accepted 14-district capacity or siting result.** This check joins the private original-verified NIWE 150 m NWIC-clipped Kerala resource centres with sampled GLO-90 DSM surface slope, using the public 14-district LRIS 2.0 GeoJSON as a separate administrative geometry source. [Machine-readable public-safe audit](../data/evidence/gis/niwe_lris_district_partition_qa_2026_09_22.json).

| Explicit point population | NIWE centres | Finite DSM slope | Missing DSM slope |
|---|---:|---:|---:|
| Uniquely contained in one LRIS district | 200,362 | 199,759 | 603 |
| Inside original NWIC Kerala clip but outside all LRIS districts | **330** | 94 | 236 |
| Ambiguous overlap | 0 | 0 | 0 |
| **Full original statewide dataset** | **200,692** | **199,853** | **839** |

Original LRIS response SHA-256: `8160600c7ac025574e32d636bd2aef81a4b6bc6225b55de8f6965953b6cb56fb`; source declares OGC CRS84 lon/lat, has 14 valid MultiPolygons and the district-name field `DISTRICT` (including source spelling `Kozhikkode`). NIWE deterministic clip and slope TIFF hashes agree with the [executed statewide audit](NIWE_150M_KERALA_TERRAIN_REAL_DATA_RESULT_2026_09_22.md). CRS declaration, valid geometry and visual website display **do not establish source vintage, legal boundaries or reuse rights**.

The residual 330 points remain explicit, **not allocated to the nearest district**. Their approximate nearest LRIS polygon distance under UTM 43 is median 37 m; 274 are within 100 m and 329 within 1 km. These distances suggest a source geometry mismatch worth investigating, but are not an accuracy correction. Adding the outside-LRIS bucket to the district-assigned bins reproduces all statewide speed/power/slope histograms and 16 threshold counts. Example: the ≥7 m/s and ≤10° *hypothetical* count is 8,637 statewide = 8,627 district-assigned + 10 unassigned. Those counts are not land area, usable sites, actual generation or MW.

**Release decision:** `complete_district_partition=false`, `ready_for_complete_district_publication=false`, `eligible_area_km2=null`, `feasible_capacity_MW=null`, `model_admitted=false`. The 14 provisional district-specific summaries exist only in the private analysis output pending source comparison and use-rights review. We will not put an apparently complete district ranking on the website while 330 original points are unassigned.

**Next:** acquire and validate the [NWIC District Boundary GeoJSON](https://www.nwdp.nwic.gov.in/dataset/district-boundary), a distinct dataset in the same portal family as our original NWIC state boundary. Extract the Kerala district features using its native state attribute; compare geometry and version with LRIS; redo the exact 200,692-point partition and fail closed if any centres remain unassigned or ambiguous. NWIC district acquisition does *not* itself guarantee that the partition will pass.

No original LRIS polygons, private NIWE rows, or raster bytes belong in the public repository without source-use review.
