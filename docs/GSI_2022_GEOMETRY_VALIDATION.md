# Original GSI (2022) Kerala district landslide geometry QA

**Scope:** The 13 KSDMA-published source archives, excluding Alappuzha. This is historical landslide **susceptibility**, not measured landslide events, parcel-level safety or a statutory exclusion. [Previous source-acquisition review](FOREST_DEM_WETLANDS_LANDSLIDE_GIS_AUDIT.md).

## Acquired, decoded and verified

On 20 September 2026 the [full-original geometry workflow](https://github.com/abhijith-sivaprasadan/kerala2040/actions/runs/35505867854) retrieved all 13 originals using the previously committed per-ZIP SHA256 and byte sizes, decoded each shapefile and read all features. See the [source ZIP manifest](../data/evidence/gis/official_gis_public_acquisition_2026_09_20.json) and the [reviewed raw geometry summary](../data/evidence/gis/gsi_2022_original_geometry_review_2026_09_20.json).

| Observed property | Result |
|---|---|
| Official source archives matching original hashes | 13/13 |
| Original shapefile features | 39 = 13 × 3 |
| Native CRS | EPSG:32643, all 13 |
| Original geometry type | MultiPolygon, all 39 |
| Original raw field | `Susceptibi` (shapefile-truncated name) |
| Original unique values, each district | `High`, `Moderate`, `Low` — one feature per class |
| Invalid original features | **39/39** |
| Original validity failure | **Ring Self-intersection** in all 39 |
| Alappuzha | No package in the official KSDMA 13-district publication; **unassessed**, not Low or zero hazard |

Original geometry extents are recorded in WGS84 for plausibility checks. A polygon extent overlapping Kerala is **not** a district boundary membership or coverage proof. All 39 shapes need explicit topology handling before ordinary spatial overlays. Raw original hashes and raw labels are never overwritten.

## Repair is a separate derivative, not a quiet source correction

The repair diagnostic script uses GEOS `make_valid(method="linework")`, records original invalidity, valid polygon parts, non-polygonal collapsed material and original-versus-repaired footprint area changes **for each of the three classes**. It also tests intersections among High/Moderate/Low within each district. It does **not** accept repaired geometry as an official replacement. Repair area versus an invalid original is a **diagnostic**, not an error estimate against ground truth; an agency or independent authoritative control would be needed for that.

```bash
PYTHONPATH=src python scripts/validate_gsi_2022_geometry.py --download
PYTHONPATH=src python scripts/assess_gsi_2022_repairs.py
```

The original ZIPs, full per-feature/source attribute report and repair diagnostic stay in the workflow artifact. The JSON summary contains original-file SHA256 to establish reproducibility without pretending the raw polygons were committed to Git. Do not redistribute source-derived geometries publicly until the source terms are verified.

**Still required for a genuinely usable spatial screening layer:** review repair extent, dropped linework and class-area effects; nonzero class overlaps and cross-district edge agreement; authoritative district boundaries, coverage gaps and district identity; consistent original 2022 class semantics, source projection, accuracy/scale and use terms; explicit unassessed geography (especially Alappuzha). A provisional GeoPackage, if produced, must be marked **topology-repaired derivative** and must retain source district, exact raw class, source ZIP hash and repair method. It is not a legal exclusion or a final statewide hazard ceiling.

**Model release:** ecological eligibility BLOCKED. No eligible land area or renewable capacity MW has been inferred from this GSI product.
