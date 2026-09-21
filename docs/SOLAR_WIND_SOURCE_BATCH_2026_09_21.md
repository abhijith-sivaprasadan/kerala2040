# Solar / wind original-source batch — 21 September 2026

**Acquisition:** user uploaded three GIS/source ZIPs and five standalone PDF studies. An additional 18 files are nested inside `Solar.zip`. **Original bytes are presently in the chat upload workspace, not in the GitHub repository or its Releases.** The raw originals' exact SHA256s, sizes, nested member hashes and publisher information are pinned in [the machine-readable manifest](../data/evidence/solar/solar_batch_2026_09_21_originals_manifest.json). **Do not claim “archived in GitHub” until the Release asset upload and remote verification succeed.**

## Original provider references and reuse

| Acquisition | First-party publisher / landing page | Evidence type and scope |
|---|---|---|
| Kerala solar-radiation hourly telemetry (nested in `Solar.zip`) | [NWIC National Water Data Portal, Kerala Surface Water](https://nwdp.nwic.gov.in/dataset/solar-radiation-telemetry-hourly-kerala-surface-water-department) | Station observations, W/m², irregular coverage; not a full FY or statewide spatial atlas. |
| Kerala wind-speed hourly telemetry (nested) | [NWIC National Water Data Portal, Kerala Surface Water](https://nwdp.nwic.gov.in/dataset/wind-speed-telemetry-hourly-kerala-surface-water-department) | Station observations, **km/h**; do not confuse with NIWE **150 m m/s**. |
| Two original India ASCII GRID packages | [Global Solar Atlas India](https://globalsolaratlas.info/download/india), produced by Solargis for World Bank/ESMAP | Long-term averaged yearly/monthly and average-daily data. **Not actual FY2024–25 gridded time series.** The 2019-era country products and individual raster PDFs/XML metadata establish vintage/units; do not infer the data were updated in 2026 from the date of download. |
| `Ground Mounted.xlsx`, floating-solar June 2026 report, 2018 PV reliability report, other studies nested in `Solar.zip` | [NISE](https://nise.res.in/) plus original files' title/publisher pages | Land/reservoir potential benchmarks and reliability engineering; not measured generation. Exact original publication URLs should be added once verified per document. |
| 2013 / 2014 / 2016 PV survey PDFs | NCPRE, IIT Bombay and Solar Energy Centre/NISE, as identified on the originals' title pages | Historical field reliability/ageing evidence, **not current Kerala 2040 degradation constants**. |
| NREL/NISE thin-film study | [NREL/TP-5J00-66963, Aug 2016](https://www.nrel.gov/docs/fy16osti/66963.pdf) | 2014–15 module-level thin-film comparison (not a Kerala utility-scale AC yield curve). |
| June 2012 PV-battery report | CSIR-CECRI / MNRE Solar Energy Centre (title page in original) | Primarily lead-acid stand-alone PV-battery research; not contemporary grid-scale lithium-ion cost/lifetime evidence. |

**Global Solar Atlas attribution:** credit Global Solar Atlas 2.0, Solargis, World Bank Group and ESMAP as prescribed by its [terms](https://globalsolaratlas.info/support/terms-of-use); its downloadable works are [described as CC BY 4.0](https://globalsolaratlas.info/support/faq). Review the original raster's own PDF/XML metadata for units, dates, resolution, acknowledgement and use rights. **NWDP licence and mixed-archive PDF redistribution rights must be reviewed separately before mirroring originals publicly**; a publisher's public download page does not by itself establish unrestricted public re-hosting.

## Raw telemetry QA — avoid claiming full coverage from filenames

The complete supplied NWDP CSVs parsed with no malformed timestamps and no duplicate station/time keys. Their date-range filenames **overstate actual observations for our base year**:

| FY2024–25 subset | All-file rows | In-FY rows | In-FY stations | Dates within FY |
|---|---:|---:|---|---|
| Solar radiation | 181,115 | **6,007** | **Ambalapuzha 5,986; Kulamavu 21** | 2024-05-19 to 2025-03-10 |
| Wind speed | 217,754 | **10,946** | **Kulamavu 5,850; Ambalapuzha 5,096** | 2024-05-19 to 2025-03-10 |

For both datasets records cluster May–Oct 2024 and March 2025, with no observations in many intervening months. Unit is **W/m²** for the solar file; **km/h** for wind. Publisher CSV time format `dd-mm-YYYY HH:MM` is parsed as written. **Timezone, sensor height and interval regularity have not been independently verified**. The `2026_2030` files in the archive contain headers only. The solar `1991_2020` named CSV contains 2017 samples; don't infer 30 years of observations. Some geographic/river columns appear inconsistent (e.g. Achencoil marked as Tapi basin); check instrument coordinates and administrative attribution independently before modelling.

These observations can validate selected points when temporal alignment and sensor metadata have been resolved. They are **not** statewide demand/generation measurements and cannot substitute for fully observed hourly irradiance/wind fields.

## Original GIS packages

- `India_GISdata_LTAym_YearlyMonthlyTotals_GlobalSolarAtlas-v2_AAIGRID.zip`: **272,539,134 bytes; 97 members; approximately 5.27 GB uncompressed**.
- `India_GISdata_LTAym_AvgDailyTotals_GlobalSolarAtlas-v2_AAIGRID.zip`: **317,301,351 bytes; 97 members; approximately 4.26 GB uncompressed**.
- Packages contain `GHI`, `DNI`, `DIF`, `GTI`, `TEMP`, `OPTA`, `PVOUT` ASCII rasters, `monthly/PVOUT_01..12.asc`, plus per-raster WGS84 `.prj`, PDF/XML metadata. Their source archives have SHA256 checksums, but **all raster cells have not been numerically validated or clipped to Kerala**. The archives were inventoried, not fully CRC-decompressed. Choose the correct *yearly/monthly totals* versus *average daily totals* before interpreting a number; the two packages are not duplicate byte-identical copies.

## Storage in THIS repository, not another transient chat upload

Standard GitHub file history is **not** a safe target for 317 MB and 272 MB originals (GitHub rejects normal >100 MB blobs). Do not commit these or 10 GB of unpacked `.asc` to Git history.

The project now includes:

- `data/evidence/solar/solar_batch_2026_09_21_originals_manifest.json` — provider, SHA256, bytes, internal members and QA classification;
- `scripts/publish_solar_source_release.ps1` — Windows/PowerShell checksum-gated upload to this repo's permanent Release asset storage **after public redistribution rights review**;
- `scripts/restore_solar_source_release.py` — fetch every exact original from that same release, verify hashes and restore into ignored `data/external/raw/solar/source_2026_09_21`.

Once uploaded and published, the project assets live under
`https://github.com/abhijith-sivaprasadan/kerala2040/releases/tag/solar-source-2026-09-21`.
**As of this note that link is only the intended destination; don't treat it as an available binary download or cite its assets until verified.** Release assets are hosted *with* the repository but are not versioned Git files; the manifest fixes identity independently of release tag/name.

## After archiving

1. Confirm remote Release assets' names/sizes and restore SHA256 before switching `release_uploaded` to true.
2. Create a Kerala polygon clip from **the exact original GSA rasters** and document CRS/nodata/resolution/units and coast/border handling.
3. Compare overlapping station periods against ERA5 with explicit time-zone and height conversions; avoid extrapolating two stations to statewide validation.
4. Keep PV historical module-degradation sensitivity separate from measured solar resource, contemporary module classes and future battery technology assumptions.
