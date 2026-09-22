# Solar / wind original-source batch — 21 September 2026

**Acquisition:** user uploaded five GIS/source ZIPs and five standalone PDF studies. An additional 18 files are nested inside `Solar.zip`. **Original bytes are presently in the chat upload workspace, not in the GitHub repository or its Releases.** The raw originals' exact SHA256s, sizes, nested member hashes and publisher information are pinned in [the machine-readable manifest](../data/evidence/solar/solar_batch_2026_09_21_originals_manifest.json). **Do not claim “archived in GitHub” until the Release asset upload and remote verification succeed.**

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

For both datasets records cluster May–Oct 2024 and March 2025, with no observations in many intervening months. The solar rows do not represent usable irradiance even within these months: all values are zero. Unit is **W/m²** for the solar file; **km/h** for wind. Publisher CSV time format `dd-mm-YYYY HH:MM` is parsed as written. **Timezone, sensor height and interval regularity have not been independently verified**. The `2026_2030` files in the archive contain headers only. The solar `1991_2020` named CSV contains 2017 samples; don't infer 30 years of observations. Some geographic/river columns appear inconsistent (e.g. Achencoil marked as Tapi basin); check instrument coordinates and administrative attribution independently before modelling.

**Critical numeric correction (22 September 2026): EVERY FY2024–25 solar-radiation value is zero (6,007/6,007, including daytime), so the FY solar CSV is NOT a usable irradiance-validation source, regardless of its timestamp coverage.** The same original contains 77,341 nonzero historical values in 2021–22, but those are not baseline-year validation. Wind has positive observed values in FY2024–25 and remains an incomplete, height/time-zone-unverified comparison source. Despite 'hourly' labels, both FY station exports predominantly use a **30-minute timestamp cadence**. Treat zero solar as instrument/export/quality failure until verified with NWIC, not evidence that there was no sunlight. See the [consolidated analysis](SOLAR_WIND_CONSOLIDATED_ANALYSIS_2026_09_22.md). Neither dataset is statewide energy-generation measurement.

## Original GIS packages

- `India_GISdata_LTAym_YearlyMonthlyTotals_GlobalSolarAtlas-v2_AAIGRID.zip`: **272,539,134 bytes; 97 members; approximately 5.27 GB uncompressed**.
- `India_GISdata_LTAym_AvgDailyTotals_GlobalSolarAtlas-v2_AAIGRID.zip`: **317,301,351 bytes; 97 members; approximately 4.26 GB uncompressed**.
- Packages contain `GHI`, `DNI`, `DIF`, `GTI`, `TEMP`, `OPTA`, `PVOUT` ASCII rasters, `monthly/PVOUT_01..12.asc`, plus per-raster WGS84 `.prj`, PDF/XML metadata. Their source archives have SHA256 checksums, but **all raster cells have not been numerically validated or clipped to Kerala**. The archives were inventoried, not fully CRC-decompressed. Choose the correct *yearly/monthly totals* versus *average daily totals* before interpreting a number; the two packages are not duplicate byte-identical copies.


## Additional original study layers — 21 September 2026, second batch

Two further original ZIPs from **[Global Photovoltaic Power Potential by Country](https://globalsolaratlas.info/global-pv-potential-study)**, © 2020 World Bank, financed by ESMAP, provided by Solargis, have been received as distinct sources:

| Original ZIP | Content | Archived GitHub binary? |
|---|---|---|
| `global-PVRASTER-DATA-LAYERS--GlobalSol derived 1(1).zip` | `PVOUT_level2.tif`, `PVOUT_seasonality_index.tif` | **No: local upload only** |
| `global-PVRASTER-DATA-LAYERS--GlobalSol derived 2(1).zip` | `PVOUT_level1.tif`, publisher's original `README.txt`, `LCOE-PVOUT-25years.tif` | **No: local upload only** |

Full ZIP CRC passed for **every member of both archives**. Original ZIP and each five inner files' exact sizes/SHA256s, raster CRS/shape/nodata, licence and bounded sampling results are preserved in [the derived-layer QA manifest](../data/evidence/solar/global_pv_derived_source_qa_2026_09_21.json). The new ZIPs were appended to the common source-archive manifest and therefore the checksum-gated release uploader/restorer now expects **ten originals** (earlier eight plus these two). The release status remains explicitly *not uploaded*.

The TIFFs are **global EPSG:4326, 30 arcsecond (approximately 1 km, latitude-dependent) raster cells**, dimensions 13,800 × 43,200, not Kerala-specific extracts. Their study meanings:

- **PVOUT Level 1:** long-term average specific PV yield screened for the original study's physical and technical constraints. In that study this includes complex terrain, water bodies, dense forests, remoteness and heavily urbanised land. This is a *global proxy*, not a validated Kerala siting decision.
- **PVOUT Level 2:** additionally applies study-scale potential soft land-use/regulatory screens such as cropland and protected-area proxies. **It is not a notified forest/wetland polygon or a Kerala statutory ban.**
- **PVOUT seasonality index:** ratio of highest to lowest monthly-average PVOUT, dimensionless; cannot reconstruct 8,760-hour variability.
- **LCOE-PVOUT-25years:** study-specific simplified 25-year LCOE **not** a current Kerala financing or 2040 electricity-cost estimate. It inherits 2020 study assumptions and then-published historical cost estimates. Do not treat raster values as new CAPEX, tariff or bankable cost evidence.

**Units caveat:** the TIFF metadata identifies the source study but does not declare per-band units. The *source study* expresses the practical PVOUT comparison as average daily kWh/kWp and the simplified LCOE as USD/kWh; verify the exact layer convention against the original study/metadata before processing. The two files are not independent measurements of PV generation.

A deliberately broad **74–78°E × 8–13°N** sampling window reads sensibly, but it includes sea, Tamil Nadu, Karnataka and parts of neighbouring geography. The finite-cell counts and observed ranges recorded in the QA JSON **must never be labelled Kerala statistics**. Next scientific step is source-grid QA and masking using the correctly reprojected original NWIC state polygon and an explicit onshore/coastal/offshore scenario mask, then comparison with country-scale GSA and time-resolved ERA5 inputs. Screens created by the original global study must not be silently reused as Kerala legal exclusions.

Publisher's **original README.txt** states CC BY 4.0 with an additional mandatory mediation/arbitration clause. Preserve it when distributing and check the [current terms of use](https://globalsolaratlas.info/support/terms-of-use). Attribution: **© 2020 The World Bank; data provided by Solargis, financed by ESMAP.**

## Third source batch — World Bank masks + additional India GeoTIFFs (21 September 2026)

Four further ZIPs were received, all individually SHA256-pinned and **all ZIP members CRC-tested**. Their source raster hashes, exact sizes, geospatial metadata and source links are preserved in [third-batch QA](../data/evidence/solar/solar_batch_3_2026_09_21_source_qa.json). They are added to the same release manifest; it now records **14 solar-source files**. Original ZIP bytes are still **local conversation uploads, NOT hosted in GitHub or Releases**.

| Original user-uploaded file | What is genuinely inside | Publisher / significance |
|---|---|---|
| `global-PV-RASTER-DATA-LAYERS--GlobalSol masks(1).zip` | Ten global binary GeoTIFF masks, original README | **© 2020 The World Bank; financed by ESMAP; Solargis data**, [Global PV Potential by Country](https://globalsolaratlas.info/global-pv-potential-study). Physical, land-cover, population and composite screened-area *proxies*, not legal Kerala exclusions. |
| `monthlyIndia_GISdata_LTAy_YearlyMonthlyTotals_GlobalSolarAtla(1).zip` | Twelve monthly PVOUT GeoTIFFs and 36 original PDF/XML/aux metadata sidecars | [Global Solar Atlas India](https://globalsolaratlas.info/download/india), © 2019 Solargis; **1999–2018** reference; 30 arcsecond pixels. Monthly PVOUT = **kWh/kWp in that named calendar month**, not kWh/kWp/day or a measured 2024–25 month. |
| `New folder(1).zip` | Annual India `DIF`, `GHI`, `OPTA`, `TEMP` TIFFs, plus original sidecars for the annual layers | User-packaged original GSA TIFFs; file title is **not a publisher product name**. |
| `New folder (2)(1).zip` | Companion annual India `DNI`, `GTI`, `PVOUT` TIFFs | Completes seven-layer annual GeoTIFF set with the preceding ZIP. |

**Grid fidelity:** the World Bank composite masks are global EPSG:4326 30 arcsecond GeoTIFFs, 43,200 columns × 15,000 rows (to 70°N); individual mask components extend farther north (21,600 rows). The original India GSA TIFFs are EPSG:4326 within 66–98°E and 6–38°N: `GHI/DNI/DIF/GTI` approximately **9 arcseconds**, `PVOUT/TEMP` **30 arcseconds**, and `OPTA` **120 arcseconds**. Monthly PVOUT is 30 arcseconds. Irradiation/PVOUT source years are **1999–2018**, while temperature metadata states **1994–2018**. **Do not resample all layers as though identical pixel sizes.**

**Relationship to previous uploads:** these GeoTIFFs overlap the science content of the earlier India **AAIGRID** downloads; alternative format is valuable for reproducibility but does not constitute independent solar validation. The World Bank masking files are new original layers relative to previous downloads. They are useful for illustrating the difference between unscreened resource potential and globally screened resource, but no `MASK_level1`, `MASK_level2`, forest, population, or protected-areas map can substitute for actual current Kerala land-use, notification-linked conservation boundaries, land rights or grid connection feasibility.

The global-masks publisher **original README is copied verbatim** under [original source READMEs](../references/source_originals/global_pv_potential_by_country_2020_MASKS_README.txt). It includes CC BY 4.0 attribution and an additional required mediation/arbitration provision. Data model admission remains blocked pending exact Kerala-boundary clipping, full nodata/geometry checks, external validation, technology and legal screens and suitable weather chronology.

## Fourth source batch — average-daily GSA India GeoTIFFs (21 September 2026)

Three additional Solargis / Global Solar Atlas 2.0 India archives were uploaded, and **all ZIP entries passed CRC**. Raw archive and TIFF member SHA256s, exact byte sizes, layer grid properties and XML caveats are in [batch-four source QA](../data/evidence/solar/solar_batch_4_2026_09_21_avg_daily_geotiff_qa.json). The common inventory now pins **17** source archives/files; GitHub Release binary archival remains *not completed*.

| Original archive | Content | What is new relative to prior batches |
|---|---|---|
| `monthlyIndia_GISdata_LTAy_AvgDailyTotals_GlobalSolarAtlas-v2_GEOTIFF(1).zip` | `PVOUT_01..12.tif` and monthly PDF/XML/aux sidecars | Long-term **average-daily** PV yield for each calendar month; previous monthly GeoTIFF batch was monthly **totals**. |
| `India_GISdata_LTAy_AvgDailyTotals_GlobalSolarAtlas-v2_GEOTIFF2(1).zip` | `DNI.tif`, `OPTA.tif`, `TEMP.tif` and annual sidecars for the seven layer names | DNI daily-average values; **OPTA and TEMP files are exact SHA256 byte duplicates** of batch-three TIFFs, not new observations. |
| `India_GISdata_LTAy_AvgDailyTotals_GlobalSolarAtlas-v2_GEOTIFF.zip` | `DIF.tif`, `GHI.tif`, `GTI.tif`, `PVOUT.tif` | Long-term annual-mean *daily-average* irradiation/PV output counterparts to prior yearly-total TIFFs. |

**Semantics caveat that must survive normalization:** ZIP names explicitly say `AvgDailyTotals`; observed values near Kerala in a non-Kerala-only rectangle are ~3–6 PVOUT kWh/kWp/day and ~3–6 irradiation kWh/m²/day, whereas previously acquired yearly/monthly totals use the corresponding full-period convention. However, the ZIP's original ISO19139 XML still describes monthly PVOUT as “longterm monthly average ... in kWh/kWp” and annual GHI/DNI/PVOUT as “longterm yearly average ... in kWh/m² or kWh/kWp,” **without explicitly writing “per day”**. Thus **daily normalization is supported by the product filenames and numerical magnitude, but needs direct matching-cell numerical confirmation against the yearly/monthly-total originals before model use**. Do not silently use the XML's bare yearly/monthly wording as a per-calendar-month total for this distinct dataset. The PDF/XML sidecars are preserved in the originals.

All rasters are **EPSG:4326, India 66–98°E and 6–38°N**. Irradiation has 9-arcsecond grid resolution; PVOUT and TEMP 30 arcsecond, OPTA 120 arcsecond. Irradiation/PVOUT long-term period is **1999–2018**; temperature **1994–2018**. A broad 74–78°E × 8–13°N QA window includes land outside Kerala and the sea, so its numeric sample must not be presented as statewide metrics.

**Source:** [Global Solar Atlas 2.0 India download](https://globalsolaratlas.info/download/india) — Solargis, World Bank Group / ESMAP; original files dated October 2019. Attribution and usage conditions remain attached to the original ISO19139 metadata. This is an **alternative format/normalisation of previously supplied Global Solar Atlas climatology**, *not* independently measured FY2024–25 PV production, a new station series, or a commissioned project capacity estimate.

## Permanent raw source storage — PRIVATE archive only

**User decision (22 September 2026): private, not public.** The public
`kerala2040` repository contains source provenance, attribution, SHA256
and transformation code; original third-party ZIP/PDF bytes must go to a
**separate PRIVATE** GitHub repository, tentatively
`abhijith-sivaprasadan/kerala2040-source-archive`. This private repository
is **created, verified PRIVATE, and initialized on `main` with a README**.
On 22 September, the **five extracted Downloads folder snapshots** were
uploaded to its private Release, downloaded to a separate local restore folder,
and passed each part, ZIP and nested-file SHA256 check. The verified
[private archive asset inventory](../data/evidence/solar/renewable_five_folder_private_archive_2026_09_22.json)
contains nine upload parts and one checksum manifest. **This is not a claim
that the 17 byte-identical original solar ZIP/PDF files and separate original
NIWE `Wind.zip` were independently archived.** Their exact-original manifest
still has `release_uploaded=false`. Do not point to the old planned public
GitHub Release.

Use the private-only
[solar uploader](../scripts/publish_solar_source_release.py),
[NIWE uploader and SHA256 restore](../scripts/publish_niwe_original_release.py),
and [solar SHA256 restore](../scripts/restore_solar_source_release.py).
Each refuses a public/missing destination. The accompanying
[handoff guide](RENEWABLE_FIVE_STEP_HANDOFF_2026_09_22.md)
contains private-repository setup and commands.

A public landing page does not authorize public re-hosting. A private
archive also remains subject to source access/use terms. Keep it restricted
to authorized users; never add account tokens or signed access URLs to
this source manifest. GitHub private Release assets are hosted with the
**separate private repository**, not tracked as Git blobs in public
`kerala2040`. A local hash or matching remote size is insufficient:
**download and verify the remote asset SHA256**, then change
`release_uploaded` to true only after all 17 originals pass.

## After archiving

1. Verify the private repository really is private and initialized.
2. Upload each SHA256-pinned original to its appropriate private Release.
3. Restore and SHA256-verify every solar asset and NIWE `Wind.zip`.
4. Produce additional exact NWIC Kerala polygon clips and refine
   technology-specific and legal siting constraints.
5. Compare available ERA5 profiles against valid independent observations;
   the FY2024–25 all-zero NWDP solar series is not validation.
