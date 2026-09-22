# Executed NIWE 150 m × GLO-90 Kerala resource analysis — 22 September 2026

**Status:** REAL-DATA source-hash-verified *descriptive* spatial join complete. Onshore generation/capacity and statutory site screening **remain blocked**; this report supersedes the earlier “missing NIWE point clip” blocker. Machine-readable aggregate: [NIWE × DSM slope evidence](../data/evidence/gis/niwe_150m_kerala_real_wind_DSM_slope_2026_09_22.json).

## Recovered original inputs and fidelity

1. User-uploaded inner NIWE national `150m_Map_Data_A_to_G.zip` SHA256 `f166450c3ea591b5b346f9cd27899b10b6f18ce9cf441c98388c6f0e98d44b38` **matches** the independently logged member from the earlier `Wind.zip`. Its uncompressed seven-column CSV SHA256 `88a1071e6226bdaeda59dcdc459528fb82ff6f8c4770138b479f56ccd97c7a57`; exactly **19,475,568** national points. No hourly wind, actual power curve or source CUF columns.
2. Recovered the ORIGINAL official NWIC state-boundary source from [existing boundary Actions artifact, run 35517474497](https://github.com/abhijith-sivaprasadan/kerala2040/actions/runs/35517474497); original ZIP SHA256 `a932ea29e7afd0fea1e1068f3beeeadb760e6b2baae9783f5822bbefd4224ebd`. Select the sole Kerala geometry in EPSG:**7755**, transform to EPSG:**4326**, test all resource-point coordinates against that actual polygon—not a rectangular envelope or slope-raster footprint.
3. Exact original NWIC clipping recovered **200,692** Kerala source point centres, median 150 m resource-speed **3.91 m/s**. Deterministic regenerated private `NIWE_150m_Kerala_NWIC_point_centres.csv.gz` SHA256 `dd9d00e67da0dac3a9258daad18c35f71075815f7b64cea4b290a36c6e9b9634`; decompressed CSV SHA256 `7c299f7c0cc1dfd08355d39c3d283bf88cfbf0ed8c10cddf6789a26e24800d4e`. The prior gzip hash `364808dd40751bd5f3e131e86127dbdab73168d1830a682002de5a4c6fdd0dee` is **not identical**. Do not claim byte identity to the inaccessible earlier compressed file; gzip headers can vary with time/filename. The actual inner NIWE input, NWIC boundary, all-point polygon check, row count and median match. New rebuild uses gzip `mtime=0`, blank filename, compression level 7 for stable bytes.
4. The independently recovered **90 m GLO-90 DSM degree-slope raster** SHA256 `72551921c99eb563abe37c9502d4e4c592c3be667f31459296c90e48be9436f7` has EPSG:32643. The NIWE lat/lon columns imply geographical degrees for sampling, but independently authoritative source CRS certification remains pending. Raster sampling was checked against Rasterio's direct sampler at **64/64 sampled point centres**.
5. Source originals and all derived NIWE rows and PNG maps remain **PRIVATE**, off the public GitHub repo. The public report contains only hashes and aggregate diagnostics, subject to a final terms review; no user-provided source PDFs/images are mirrored.

## Observed resource and terrain — never interpret point counts as km²

| Statistic | Real Kerala source-point result |
|---|---:|
| NIWE resource points inside NWIC geometry | **200,692** |
| 150 m modelled mean wind speed, median | **3.910 m/s** |
| 150 m modelled wind-speed p05 / p95 | 2.414 / 7.766 m/s |
| 150 m modelled wind power density, median | **78.9255 W/m²** |
| wind power density p05 / p95 | 24.269 / 511.4345 W/m² |
| sampled DSM degree-slope present / missing | **199,853 / 839 points** |
| sampled DSM slope median / p95 | **4.961° / 26.201°** |

A *descriptive sensitivity matrix* gives the number of resource centres satisfying both a hypothetical minimum 150 m wind speed and maximum DSM surface slope. Columns are **slope ≤ degrees**, rows are **speed ≥ m/s**. A number is a point count, **not area, available land, turbine sites, grid-transfer MW or generation**.

| ≥ m/s / ≤ slope | 5° | 10° | 15° | 20° |
|---|---:|---:|---:|---:|
| 5 | 22,279 | 34,290 | 41,980 | 47,959 |
| 6 | 9,684 | 14,642 | 18,971 | 22,625 |
| 7 | 6,263 | 8,637 | 10,757 | 12,710 |
| 8 | 3,593 | 4,691 | 5,654 | 6,554 |

Denominator for sensitivity percentages is **199,853 slope-available points**, not all of Kerala's area or even all clipped wind points. Do not present threshold combinations as recommended legal/engineering turbine selection criteria; the 90 m surface-slope DSM does not resolve a turbine-pad footprint, ridgeline access, landslide stability or subpixel terrain. Original resource nominal horizontal grid ~500 m differs from terrain ~90 m; point counts cannot simply be multiplied by a nominal grid-cell area.

## Reproduction and quality assurance

[Rebuild the clip directly from the pinned original NIWE and NWIC ZIPs](../scripts/rebuild_kerala_niwe_clip_from_originals.py), then [run the wind × slope code](../scripts/audit_kerala_niwe_resource.py).

```powershell
$py = '.\.venv-311-media\Scripts\python.exe'
& $py scripts/rebuild_kerala_niwe_clip_from_originals.py `
    --source-inner-zip 'E:\path\to\150m_Map_Data_A_to_G.zip' `
    --nwic-artifact 'E:\path\to\official-Kerala-boundary-probe-NOT-capacity-eligibility.zip' `
    --out-dir 'E:\Kerala2040MediaQA\NIWE_Terrain_Private'

& $py scripts/audit_kerala_niwe_resource.py `
    --niwe-clip 'E:\Kerala2040MediaQA\NIWE_Terrain_Private\NIWE_150m_Kerala_NWIC_point_centres.csv.gz' `
    --allow-repacked-clip `
    --slope-degrees 'E:\path\to\kerala_boundary_GLO90_slope_degrees_90m.tif' `
    --map-dir 'E:\Kerala2040MediaQA\NIWE_Terrain_Private_Maps' `
    --out 'E:\Kerala2040MediaQA\NIWE_Terrain_Private\NIWE_terrain_aggregate.json'
```

`--allow-repacked-clip` is used **only** because the original-source-verified deterministic gzip does not match the earlier archive's gzip header/hash; do not use this switch for unknown downloaded data. The output map directory must not be the clipped CSV's parent. The revised sampler reads the pinned slope once and vectorizes indices/missing-mask checks (the original per-point `rasterio.sample` took over 200 seconds for this workload).

**Conclusion at this gate:** resource assessment plus descriptive terrain interaction COMPLETE. `candidate_area_km2=null`, `feasible_capacity_MW=null`, `hourly_wind_generation_validated=false`, `model_admitted=false`. Next work: legally grounded land and ecological exclusion GIS, road/laydown constraints, and grid connection/evacuation evidence. The newly acquired 2014 Tirunelveli network is **not** a Kerala network substitute.
