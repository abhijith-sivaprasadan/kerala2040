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

## Repair review of all 39 original polygons

The [separate complete repair workflow](https://github.com/abhijith-sivaprasadan/kerala2040/actions/runs/35506022989) ran GEOS `make_valid(method="linework")` on all 39 original MultiPolygons **without replacing their original ZIPs**. The [committed diagnostic summary](../data/evidence/gis/gsi_2022_repair_diagnostics_2026_09_20.json) records:

- 13/13 districts completed, all 39 resulting polygonal candidates valid;
- maximum absolute relative area difference from the *invalid original geometries*: **1.5225046130514917 × 10⁻¹⁴**;
- **zero positive-area High/Moderate/Low overlaps within every district**, across all 39 tested within-district class pairs.

These are computational repair checks, not positional accuracy against ground truth or official GSI approval of altered polygons. The exact geometry/linework implications and cross-district boundary/coverage remain separately unresolved.

A gated generator may write a `GSI2022_REPAIRED_PROVISIONAL_NOT_LEGAL` GeoPackage using the 39 repaired polygons with the original source district, unchanged raw High/Moderate/Low class, original ZIP SHA256 and repair method in feature attributes. It is a **research screening candidate only**. The producer refuses the GeoPackage unless all 13 districts have three valid, zero-overlap classes and area-change tolerances are met. The file, where generated, is deliberately **not committed as a public, licensed, legally authoritative spatial layer**.

## Repair is a separate derivative, not a quiet source correction

The repair diagnostic script uses GEOS `make_valid(method="linework")`, records original invalidity, valid polygon parts, non-polygonal collapsed material and original-versus-repaired footprint area changes **for each of the three classes**. It also tests intersections among High/Moderate/Low within each district. It does **not** accept repaired geometry as an official replacement. Repair area versus an invalid original is a **diagnostic**, not an error estimate against ground truth; an agency or independent authoritative control would be needed for that.

```bash
PYTHONPATH=src python scripts/validate_gsi_2022_geometry.py --download
PYTHONPATH=src python scripts/assess_gsi_2022_repairs.py \\
  --provisional-gpkg results/gis/gsi_2022_topology_REPAIRED_NOT_OFFICIAL.gpkg
```

The original ZIPs, full per-feature/source attribute report and repair diagnostic stay in the workflow artifact. The JSON summary contains original-file SHA256 to establish reproducibility without pretending the raw polygons were committed to Git. Do not redistribute source-derived geometries publicly until the source terms are verified.

**Still required for a genuinely usable spatial screening layer:** review repair extent, dropped linework and class-area effects; nonzero class overlaps and cross-district edge agreement; authoritative district boundaries, coverage gaps and district identity; consistent original 2022 class semantics, source projection, accuracy/scale and use terms; explicit unassessed geography (especially Alappuzha). A provisional GeoPackage, if produced, must be marked **topology-repaired derivative** and must retain source district, exact raw class, source ZIP hash and repair method. It is not a legal exclusion or a final statewide hazard ceiling.

**Model release:** ecological eligibility BLOCKED. No eligible land area or renewable capacity MW has been inferred from this GSI product.
