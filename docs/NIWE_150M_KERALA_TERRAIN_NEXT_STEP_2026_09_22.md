# NIWE 150 m Kerala resource and terrain: next reproducible operation

**Status: workflow added; real-data run pending.** The original 150 m source QA already verified the nested ZIP and seven-column, 19,475,568-row national CSV. The exact NWIC Kerala polygon clip already yielded 200,692 point centres. This script takes that EXISTING clip rather than reading 19 million records again.

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
