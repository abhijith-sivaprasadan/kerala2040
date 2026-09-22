# Wind research phase 1 closeout — Kerala2040 (23 September 2026)

**Status: complete for the bounded descriptive wind-resource × terrain research question; not complete for wind-farm feasibility, annual generation or investable capacity.**

The poster-suitable question is: **How sensitive is the district distribution of modelled Kerala onshore wind-resource *point centres* to hypothetical terrain-slope limits?** This report adds district-normalized comparisons to the already completed [NIWE 150 m × DSM statewide analysis](NIWE_150M_KERALA_TERRAIN_REAL_DATA_RESULT_2026_09_22.md) and [14-district NWIC partition](NIWE_NWIC_DISTRICT_WIND_TERRAIN_RESULT_2026_09_22.md). All values originate from the committed [NWIC 14-district aggregate](../data/evidence/gis/niwe_nwic_district_wind_terrain_2026_09_22.json) and this report's [normalized derivative](../data/evidence/gis/niwe_nwic_district_normalized_wind_terrain_2026_09_23.json). No statistical interpolation, invented suitability class or conversion of point-centre counts into square kilometres is used.

## Frozen poster wording — research question and conclusion

**Research question (wind phase 1):**

> How sensitive is the spatial distribution of Kerala’s modelled 150 m onshore wind resource to surface-slope constraints, when evaluated across all 14 districts using consistent administrative boundaries?

**Conclusion (poster-ready):**

> Kerala’s modelled onshore wind-resource distribution is sensitive to the terrain threshold applied. Of 200,692 NIWE resource-point centres assigned uniquely to Kerala’s 14 NWIC districts, 199,853 had valid GLO-90 digital surface-slope samples. Under an illustrative threshold of wind speed ≥7 m/s and slope ≤10°, 8,637 centres matched statewide—4.32% of centres with valid slope. The corresponding within-district shares were 27.50% in Palakkad and 8.08% in Idukki. Tightening the slope limit from ≤20° to ≤5° retained 70.49% of Palakkad’s reference subset but 19.55% of Idukki’s. **Thus, wind-speed information alone does not capture the geographical sensitivity introduced by terrain.** These descriptive results do not establish legally eligible sites, developable area, electricity generation or feasible installed capacity.

**One-sentence poster takeaway:**

> Terrain assumptions materially change how Kerala’s modelled wind resource is distributed across districts, making wind-speed-only screening insufficient for interpreting spatial resource patterns.

*Scope:* the slope limits are **hypothetical descriptive sensitivities**, not legally or technically adopted siting constraints; the ≤5°/≤20° percentages each refer only to the district’s **≥7 m/s, ≤20° reference subset**, not every windy point. Keep `feasible_capacity_MW=null` and `model_admitted=false`.

## Research method and denominators

- Original NIWE national seven-column 150 m atlas → exact original NWIC Kerala state polygon → **200,692 NIWE source point centres**. Resource is *modelled* mean wind speed at 150 m, **not measured hourly wind or produced electricity**.
- Copernicus GLO-90 **digital surface model**, derived slope in degrees, sampled at NIWE centres. **199,853 finite slope samples; 839 missing**. A 90 m DSM does not measure bare-earth turbine pad slope.
- Original NWIC district GeoJSON (source CRS EPSG:7755) assigns **all 200,692 centres once** across 14 district polygons. The separate LRIS polygons left 330 unmatched, documented as a historic **cross-source geometry** finding; they are not the active NWIC district partition.
- The 4×4 *illustrative* matrix counts centres with source-modelled speed **≥5, 6, 7 or 8 m/s** and sampled DSM slope **≤5°, 10°, 15° or 20°**.
- **Within-district percentage** = threshold matching centres / centres in that district **with finite sampled slope**. This describes the source grid, not a district land percentage. **District share of statewide matching points** = district matching count / statewide matching count for the same setting. **≤5° / ≤20° reference percentage** = threshold count at 5° divided by its count at 20° for the *same* minimum speed. It is **not** a percentage of *all* windy centres; centres with DSM slope above 20° are outside the reference.
- Zero means zero points under the modelled setting. Undefined reference ratios are **null**, not 0%; missing-slope points remain excluded, never imputed. NIWE ~500 m horizontal resource spacing is not a turbine-spacing or area-conversion rule.

## Source-backed descriptive finding

| Source population / illustrative setting | Point centres | Percentage denominator |
|---|---:|---|
| Original NWIC Kerala NIWE centres | 200,692 | All NIWE centres |
| Finite DSM slope | 199,853 | 200,692 source centres |
| Missing DSM slope | 839 | 200,692 source centres |
| ≥7 m/s, ≤10° across Kerala | **8,637** | **4.3217% of 199,853** slope-available centres |
| Palakkad ≥7 m/s, ≤10° | **6,330** | **27.4978% of its 23,020** slope-available centres |
| Idukki ≥7 m/s, ≤10° | **1,804** | **8.0795% of its 22,328** slope-available centres |

Under that same single hypothetical setting, Palakkad accounts for **73.29%** of Kerala-wide matching point centres (6,330/8,637), Idukki **20.89%** (1,804/8,637) and the other 12 districts together **5.82%** (503/8,637). **These are source-point shares, not installed-capacity, developable-land or electricity shares.** They must not be presented as an overall district ranking or construction recommendation.

**Terrain-slope sensitivity, holding minimum modelled speed at ≥7 m/s:**

| NWIC district | ≤5° | ≤10° | ≤15° | ≤20° | ≤5° count / ≤20° count |
|---|---:|---:|---:|---:|---:|
| Palakkad | 5,465 | 6,330 | 7,072 | 7,753 | 70.49% |
| Idukki | 663 | 1,804 | 2,698 | 3,392 | 19.55% |
| Kerala, all districts | 6,263 | 8,637 | 10,757 | 12,710 | 49.28% |

The relative response differs strongly between these two district subsets. For instance, within the **≤20° reference**, the ≤5° subset contains **70.49%** of Palakkad's threshold-matching centres but **19.55%** of Idukki's. This does *not* mean that the other points are legally excluded or technically unbuildable, or that every retained point is suitable. It establishes why a statewide median or wind-speed-only reading of the atlas loses spatial and terrain context.

The wind-speed medians are **6.412 m/s** (Palakkad) and **5.5675 m/s** (Idukki); the sampled median DSM slopes are **4.2932°** and **12.7611°**, respectively. Those medians and the threshold matrix describe different statistical summaries and should not be combined as if they belonged to one representative wind site.

## Poster-ready results and figures

- [Figure 1 — district-normalized ≥7 m/s × ≤10° comparison](../docs/assets/wind-district-normalized-20260923.svg) includes all 14 districts, the **finite-slope denominator**, zeroes and source-limit footnote.
- [Figure 2 — terrain sensitivity at ≥7 m/s](../docs/assets/wind-terrain-sensitivity-20260923.svg) shows threshold response at 5°, 10°, 15° and 20° for Palakkad, Idukki and statewide, **normalized within the ≤20° reference subset** to avoid confusing different district sizes.
- Both figures are original vector graphics drawn exclusively from numerical aggregates—**no NIWE-derived geography, NWIC polygon coordinates, WMS tiles or restricted raw source maps**. Printer-compatible pale backgrounds and selectable text. The [district explorer](https://kerala2040.github.io/#atlas) remains a detailed interactive supplement, not the poster's evidentiary source of truth.

**Poster-ready conclusion:** *The spatial interpretation of Kerala's modelled 150 m wind atlas depends on both district boundary choice and hypothetical surface-slope assumptions; our NIWE–GLO-90–NWIC pipeline now reports this sensitivity with complete point accounting and explicit missing data. It does not establish where wind can legally or physically be built.*

## Phase 1 acceptance checklist

| Work item | Outcome |
|---|---|
| Original resource/terrain input provenance and full-state source population | Completed within documented hash/CRS limitations |
| Exactly one original NWIC district per source point | **200,692/200,692**, zero unassigned or overlapping |
| Statewide resource/slope/missing-data and 16 matrix reconciliations | Completed |
| District-normalized and threshold-relative sensitivity, with denominator QA | Completed; numerical audit committed |
| Poster-ready source-limited original vector figures and site interpretation | Completed for this bounded research question |
| Native class-coded land use, notification-linked protected/wetland/paddy/ESZ polygons | **Not done; a separate spatial-eligibility phase** |
| Turbine class, layout, measured wind chronology, yield, connection/grid hosting and feasible MW | **Not done; a separate wind-feasibility/model phase** |

**Release status:** `descriptive_wind_phase1_complete=true`; `source_reuse_rights_verified=false`; `eligible_area_km2=null`; `feasible_capacity_MW=null`; `hourly_generation_validated=false`; `model_admitted=false`. Completion of the bounded *data analysis* is not admission to the Kerala2040 dispatch/capacity model.

## Reproduce independently from repository-safe aggregates

Run `python scripts/derive_district_wind_sensitivity.py` from the repository root. It rejects source-count, slope-count, district and 16-cell inconsistencies and refuses any non-null eligible area/capacity or source marked model-admitted. The original-source GIS reproduction still requires private originals via [the pinned-input NWIC workflow](../scripts/rebuild_nwic_district_wind_aggregate.py); it is intentionally **not** available from the public aggregate alone.
