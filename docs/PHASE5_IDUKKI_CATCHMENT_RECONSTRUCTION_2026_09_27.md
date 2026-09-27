# Phase 5 Idukki catchment reconstruction gate — 27 September 2026

## Status

**The LRIS vector-access blocker is solved, but the Idukki catchment is still not admitted.**

LRIS 2.0's public WFS endpoint reports that WFS is disabled, but the public WMS service can return KML feature geometry. Three Idukki layers were recovered from the live LRIS GeoServer without inventing or tracing geometry:

- `LRIS_shp:watersheds_idukki`
- `LRIS_shp:drains_idukki`
- `LRIS_shp:waterbodies_idukki`

The source KMLs are retained privately. This repository records hashes, counts, methods and release gates only; redistribution rights for the raw LRIS geometry have not been reviewed.

## Recovered LRIS vector structure

| Layer | Source features | Source geometry QA |
|---|---:|---|
| watersheds | 853 | 852/853 valid before derived repair |
| drains | 30,429 | 30,429/30,429 valid |
| waterbodies | 268 | 267/268 valid before derived repair |

The watershed layer's basin labels partition the district-scale geometry into PERIYAR (559), MUVATTUPUZHA (144), PAMBAR (81), PAMBA (37), MANIMALA (24) and MINACHIL (8) source features. The full watershed layer covers about 4,547 km²; the LRIS PERIYAR union is about 3,187 km². **Neither is the Idukki reservoir catchment.**

The drains carry `fid_drains`, source-reported `length_km` and drainage order 1–8. Exploratory GLO-90 endpoint elevations indicate strong but not perfect upstream→downstream digitisation, especially in low-order streams.

## Idukki reservoir anchor

The waterbody layer identifies the reservoir directly:

- `fid_waterb = 743`
- name: **Idukki Reservoir (Cheruthoni_Kulamavu_Idukki Dam)**
- six administrative fragments
- dissolved geodesic area: **49.3982 km²**

The six reservoir fragments line up with six `code=WB` features in the LRIS watershed layer. This gives a source-defined common anchor between waterbodies and watersheds.

## Independent area evidence

CEA project documentation states **649.3 km²** for the catchment area up to the Idukki upper-dam site. FAO reservoir literature independently reports the same value.

**649.3 km² is used only as an external validation target.** No polygon is enlarged, clipped or tuned to make its area equal that number.

## Reconstruction attempts that failed the gate

The following are exploratory diagnostics and are explicitly **rejected**:

| Method | Approx. result | Decision |
|---|---:|---|
| directed LRIS drain endpoint graph | ~347 km² | reject: under-captures because network topology is incomplete across source/admin fragments |
| undirected drain graph, low-snap example | ~987 km² | reject: merges neighboring drainage systems |
| generic raw-DEM marker watershed | ~3,346 km² | reject: not routed reservoir hydrology |
| GLO-90 priority flood inside LRIS Periyar | ~1,281 km² | reject: over-captures |
| high-order LRIS drain burn + any reservoir target | ~1,316 km² | reject: over-captures |
| high-order LRIS drain burn + near-dam target | ~1,238 km² | reject: over-captures |

This disagreement is useful: it demonstrates why the district boundary, whole Periyar layer, a simple drainage graph, or an arbitrary DEM outlet cannot be promoted to the catchment.

## Natural catchment versus intercepted catchment

KSEB documents augmentation/diversion structures associated with Idukki, including Narakakkanam, Azhutha, Vazhikkadavu, Vadakkepuzha and Kuttiar; Kallar–Erattayar is also relevant diversion context.

Therefore two geometries must remain separate:

1. **natural topographic catchment** draining to the Idukki reservoir; and
2. **reservoir-intercepted catchment**, which may add independently verified augmentation/diversion catchments.

No diversion catchment is inferred from names alone.

## Next release gate

The next required independent geometry is the Government of India Hydrological Boundaries dataset from NWIC / India-WRIS:

- catalogue: https://www.data.gov.in/catalog/hydrological-boundaries
- required geometry: watershed/sub-basin coverage around Idukki
- preferred evidence: original official ZIP or byte-verifiable official source

A public GitHub release in `yashveeeeeeer/india-geodata` mirrors WRIS/SLUSI hydro-boundary data and is useful only as a secondary cross-check. It is **not** a substitute for original NWIC/WRIS provenance.

Once the independent WRIS/NWIC geometry is obtained, the admission test is:

1. identify the WRIS hydrological unit(s) containing the LRIS Idukki reservoir;
2. compare their boundaries against LRIS watersheds and mapped drains;
3. test topology and area without using 649.3 km² as a fitting parameter;
4. document any boundary disagreement;
5. separately add only source-verified augmentation catchments;
6. emit exactly one reviewed GeoJSON feature with SHA-256;
7. only then build ERA5-Land pixel-overlap weights.

## Release flags

- natural catchment ready: **NO**
- intercepted catchment ready: **NO**
- Phase 5 weights ready: **NO**
- ERA5 Phase 5 model run ready: **NO**

The project remains fail-closed: no rejected geometry enters the rainfall/inflow model.
