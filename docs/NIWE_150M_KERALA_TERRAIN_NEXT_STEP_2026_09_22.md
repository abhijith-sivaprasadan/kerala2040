# NIWE 150 m Kerala resource and terrain: next reproducible operation

**Status: audited workflow and private map generator added; NIWE × slope real-data run pending.** The original 150 m source QA already verified the nested ZIP and seven-column, 19,475,568-row national CSV. The exact NWIC Kerala polygon clip already yielded 200,692 point centres. This script takes that EXISTING clip rather than reading 19 million records again.

## Independent publisher checks, 22 September 2026

- GSA publisher FAQ: https://www.globalsolaratlas.info/support/faq states yearly total = average daily total × 365.25; the two temporal representations are equivalent; source CRS EPSG:4326; GHI and other irradiation layers 9 arcsec, PVOUT/TEMP 30 arcsec, OPTA 2 arcmin. This independently corroborates the existing full-raster PVOUT consistency result; it is NOT measured PV generation, nor a page-by-page review of each local PDF/XML sidecar.
- NIWE publisher source page: https://niwe.res.in/Open_data_Set/open_wind_dataset/11/ describes 150 m modelled resource with nominal 500 m horizontal resolution intended for preliminary site investigation. The page describes more parameter types than the seven columns in our separately verified CSV. Do not invent direction, CUF, turbine generation or temporal data from the CSV. Coordinate CRS is not independently certified merely by numeric lon/lat headers.

## Running the local resource classification

Use the already-generated `NIWE_150m_Kerala_NWIC_point_centres.csv.gz` from the private derived clip package, or a separately source-verified regenerated copy. Do not publish its raw NIWE rows.

```powershell
$py = '.\.venv-311-media\Scripts\python.exe'
& $py scripts/audit_kerala_niwe_resource.py --niwe-clip 'E:\path\to\NIWE_150m_Kerala_NWIC_point_centres.csv.gz' --out 'E:\Kerala2040MediaQA\niwe_150m_kerala_classes.json'
```

Optional: pass `--slope-degrees 'E:\path\to\slope.tif'` only after confirming the original raster units truly are degrees. Sampling is CRS-transformed; missing slope pixels remain missing. If using GLO-90-derived slope, it describes DSM surface terrain, not surveyed bare-earth DTM. `--allow-repacked-clip` explicitly permits a regenerated compressed CSV with a different hash *only after* separately checking its input provenance; its mismatch is recorded in the output. By default unexpected SHA256, wrong row count, column mismatch, invalid values or duplicate coordinates abort.

The local JSON provides wind-speed, power-density, Weibull and optional slope/joint classes, counting **point centres**, not geodesic land area. It deliberately records `candidate_area_km2: null`, `feasible_capacity_MW: null`, and `model_admitted: false`. No technology-specific turbine layout, forest/wetland notification, land rights, measured yield, actual network headroom, or capacity expansion follows from a histogram.

Do not alter the five verified private source snapshots, the published pinned website, or the 2040 model-admission flags. The PR contains code and synthetic tests, not results of a completed real NIWE/slope run.

## NIWE × GLO-90 sensitivity and private point maps

The independently derived 90 m **GLO-90 DSM surface-slope raster** is recoverable in the existing Actions artifact [Kerala GLO-90 boundary/DSM/slope, run 35523266172](https://github.com/abhijith-sivaprasadan/kerala2040/actions/runs/35523266172). Artifact ZIP member:

`kerala_glo90_boundary/kerala_boundary_GLO90_slope_degrees_90m.tif`

Its previously independently verified SHA256 is `72551921c99eb563abe37c9502d4e4c592c3be667f31459296c90e48be9436f7`, its coordinate reference system is EPSG:32643, its nominal grid resolution is 90 m, and its derivation uses central differences of bilinear-reprojected GLO-90 DSM. Do **not** substitute `kerala_boundary_GLO90_DSM_EPSG32643_90m.tif`: that is elevation, not slope.

Run the following after recovering the prior NIWE compressed point clip and the slope TIFF into your private workspace (no full India source reprocessing):

```powershell
$py = '.\\.venv-311-media\\Scripts\\python.exe'
$clip = 'E:\\path\\to\\NIWE_150m_Kerala_NWIC_point_centres.csv.gz'
$slope = 'E:\\path\\to\\kerala_boundary_GLO90_slope_degrees_90m.tif'
(Get-FileHash -Algorithm SHA256 $clip).Hash.ToLowerInvariant()
(Get-FileHash -Algorithm SHA256 $slope).Hash.ToLowerInvariant()
& $py scripts/audit_kerala_niwe_resource.py `
  --niwe-clip $clip `
  --slope-degrees $slope `
  --map-dir 'E:\\Kerala2040MediaQA\\NIWE_Terrain_Private_Maps' `
  --out 'E:\\Kerala2040MediaQA\\niwe_150m_kerala_slope_classes.json'
```

The NIWE compressed clip hash must equal `364808dd40751bd5f3e131e86127dbdab73168d1830a682002de5a4c6fdd0dee` by default; mismatch aborts. The 16 speed (≥5/6/7/8 m/s) × slope (≤5/10/15/20°) combinations count only matched **point centres with finite slope**. Every row also gives its percentage of *slope-available point centres*, not Kerala land area. They are an **assumption sensitivity**, not endorsed turbine screening rules. The JSON records slope missingness and full SHA256, and the PNGs have private/local-only filenames and hashes. Do not commit/distribute these NIWE-derived images before resolving source permissions. These thresholds cannot yield area or MW without spatial land accounting, legally grounded exclusions, layout, wind generation performance and transmission constraints.

If the compressed clip from the earlier local conversation container is unavailable, recover it from your locally saved `kerala2040_resource_clips_2026_09_22.zip` if present. This ZIP was **not** recorded as backed up to the remote public GitHub repo. Do not cite its output as an executed wind × slope run until the exact compressed clip is independently recovered and sampled.
