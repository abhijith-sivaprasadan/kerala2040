# Renewable source-media review: GeoTIFF pixels and individual PDF pages

**State:** the user's five-folder TIFF inventory, PDF-page rendering, and
all-India 26-layer GSA PVOUT unit audit have completed. The uploaded JSON
reports have been reviewed and the GSA numerical QA committed. **Visual
interpretation of the rendered PDF pages, the inside-ZIP NIWE raster audit,
and scientific model admission remain outstanding.** Source storage was
already independently restored from the PRIVATE archive. This document
does not grant source licensing or admit data into the model.

## Local execution update — user report, 22 September 2026

The user ran the inspection workflows against the five downloaded folders in
a dedicated Python 3.11.9 environment. Terminal output reports:

| Local execution step | Reported result | What it establishes |
|---|---:|---|
| Source GeoTIFF media inspection | **52/52 TIFFs, 0 errors** | Source TIFFs opened and their sampled previews/metadata were written locally. Not all native pixels were scanned by this particular media-inspection script. |
| PDF rendering | **66/66 PDFs; 2,945 pages, 0 errors after TIFF-only rerun** | All report pages were rendered locally and retained in the page contact-sheet index. Pages have **not** thereby been visually interpreted. |
| GSA period-total versus mean-daily/full-month PVOUT native-raster audit | **PASS; 8,796,068 valid positive annual cells; 64 native raster windows** | The locally executed source consistency checks passed at the script's default 0.2% tolerance. This is GSA India raster QA, **not** a Kerala-only count, independent physical validation, model admission or eligible capacity. |

The user's two JSON reports were subsequently received and examined.
The exact GSA raster audit with provenance-context fields was committed
[here](../data/evidence/solar/gsa_pvout_full_raster_qa_2026_09_22.json),
and the source-media inventory was reviewed without publishing raw TIFF/PDF
data or any rendered contact sheets. The figures remain from the user's
local Windows execution; the private raster binaries were **not
independently reprocessed here**, and 2,945 rendered pages are **not**
2,945 visually interpreted pages. See the detailed report inspection below.

## Uploaded QA reports reviewed — 22 September 2026

Two completed local JSON reports were received and inspected:
[full GSA native-raster unit QA](../data/evidence/solar/gsa_pvout_full_raster_qa_2026_09_22.json)
and the private local `renewable_media_inventory.json`. The GSA report is
committed in full because it consists of provenance, source paths, TIFF hashes
and numerical QA only; the large private media inventory, page contact sheets
and underlying third-party source files are not committed.

**GSA PVOUT source consistency (all-India, NOT a Kerala-only calculation):**

| Check | Matched positive cells | Positive-cell mask disagreements | Cells above 0.2% tolerance | Largest absolute relative difference |
|---|---:|---:|---:|---:|
| Yearly PVOUT vs 365.25 × average-daily PVOUT | 8,796,068 | 0 | 0 | 0.000087799% |
| Yearly PVOUT vs sum of 12 monthly-total layers | 8,796,068 | 0 | 0 | 0.0293348% |
| Each monthly-total vs calendar-normalized daily PVOUT | 8,796,068 **per month** | 0 for every month | 0 for every month | 0.00297260% (February; other months ≤0.000011405%) |

These 26 annual/monthly PVOUT TIFFs are EPSG:4326, **3,840 × 3,840**,
native resolution **0.008333333°** (30 arcsec), bounds **66°–98° E,
6°–38° N**. The comparison applied no resampling. The full report
pins each source TIFF SHA256; it also preserves the stated long-term
1999–2018 source vintage, non-admission, and `feasible_capacity_MW=null`.
The 8,796,068 count is the *positive matched India pixel population for
each comparison*, **not** a count of independent measurement stations or
Kerala pixels. All checks passed the 0.2% source-internal tolerance.

**Important limitations identified on close inspection:**

- The two PVOUT representations use different nodata conventions:
  yearly/monthly-total files declare approximately
  `1.1754943508222875e-38`, average-daily files declare
  `NaN`. Rasterio masks both; zero mismatches in this script means
  **matched valid-positive cell support**, not proof that all raw
  nodata bytes or all zero-valued cells are equivalent.
- The 52 TIFF inventory divides into **19 average-daily India GSA,
  19 yearly/monthly-total India GSA and 14 world-study rasters**.
  The wind folder contains its important NIWE source *inside a ZIP*;
  `52/52 TIFFs` does **not** mean a NIWE wind raster was opened.
- GSA band-unit and band-description fields were **null** in the sampled
  TIFF inventory. The year/day and month/day numerical relationships
  are supported, but definitive publisher units/definitions must be
  checked against the GSA XML/PDF sidecars, including **PDF page 2**
  (image-heavy) and the source README before admitting values.
- Sampled **negative TEMP** values are physically plausible
  temperatures, not negative irradiance. The global study's binary
  masks normally contain many zero pixels. Neither is automatically
  a corrupt file. All 52 `source_meta_qa` flags remain
  `CHECK_REQUIRED`; 900 × 900 previews are not full-raster statistics.
- The PDF inventory reports **66/66 files, 2,945/2,945 pages
  rendered, no errors**, but each PDF has
  `visual_interpretation_completed=false`. The 121-page NISE
  floating-PV report has **41 low-text pages** and the low/moderate
  wind-blade report has **262/262 low-text pages**. Treat these as
  visual review priorities, not automatically readable extracted text.

**Source QA passed. Scientific admission remains blocked:** independent
Kerala PV production/irradiance checks, the wind source's actual
inside-ZIP raster review, GIS siting statutes, eligible area/roof/water
geometry, network connections and uncertainty are separate gates. Do not
promote the India GSA pixel count, study masks or floating-PV study scenarios
into installed generation, feasible capacity or a 2040 headline.

## Purpose

The GSA, NIWE, NISE and World Bank materials contain actual numerical rasters,
scanned report pages, diagrams, map legends, tables and possibly annexure images.
**PDF extracted text/OCR alone is not evidence that an image-based table has been
read.** Likewise a TIFF filename, sidecar or map thumbnail is not a pixel audit.
We maintain three different tests rather than conflating them.

| Test | Script | What is checked | What it does NOT prove |
|---|---|---|---|
| Full India GSA PVOUT unit audit | [qa_gsa_pvout_full_raster.py](../scripts/qa_gsa_pvout_full_raster.py) | Actual PVOUT TIFF pixels, EPSG:4326, identical native grids, annual/daily 365.25 factor, each monthly total/mean-day factor including February 28.25, yearly sum of 12 monthly totals, mask disagreement and relative error for every positive matched pixel | Independent validation, Kerala legal area, FY2024–25 PV, or a capacity estimate |
| TIFF source-media inventory | [inspect_renewable_source_media.py](../scripts/inspect_renewable_source_media.py) | Every on-disk TIFF inside the five folders: SHA256, CRS, shape, transform, band descriptions/tags, nodata, sampled numeric range, sampled missing/zero/negative counts and a visual PNG preview | Exact full-raster distribution; run the separate full audit above for 26 GSA PVOUT files |
| Page-by-page PDF visual preparation | [inspect_renewable_source_media.py](../scripts/inspect_renewable_source_media.py) | Every PDF in the five folders: source SHA256, number of pages; **renders every page** into labelled contact sheets even when native text is absent; records per-page native word count, embedded images and vector drawings and flags low-text pages | It does NOT OCR or automatically understand figures; images must actually be examined visually by a researcher |

The PDF contact sheets are a **review queue**, not automated scientific
interpretation. A page with no extractable words is neither a blank page nor
proof of a scanned document. A page with text can still have crucial chart
information only in a raster image. Low-text flags only help choose pages
needing closer high-resolution inspection; **all pages are rendered**.

## Run on the actual five Downloads folders

These folders were the inputs to the already verified private archive. Do not
upload their raw TIFFs, PDFs or contact sheets into public Git history.

From your Windows PowerShell research checkout on a branch containing both
scripts (for example the existing \`renewable-archive\` branch):

\`\`\`powershell
git fetch origin main
git switch renewable-archive
git pull --ff-only

python -m pip install -e ".[dev,geo]"
python -m pip install "pymupdf>=1.24,<2" "pillow>=10,<12"

$downloads = Join-Path $env:USERPROFILE 'Downloads'
$qa = 'E:\Kerala2040MediaQA'

# TIFF inspect + literally render each PDF page, no OCR.
python .\scripts\inspect_renewable_source_media.py --source-root $downloads --out-dir $qa

# Inspect actual pixels of both India GSA annual/monthly PVOUT families.
python .\scripts\qa_gsa_pvout_full_raster.py --source-root $downloads --out "E:\Kerala2040MediaQA\gsa_pvout_full_raster_qa.json"
\`\`\`

**If you are on the separate SLDC research branch and have untracked folders,
do not delete them.** Return to your previously created \`renewable-archive\`
branch; it does not require deleting the SLDC branch. Use a fresh output path
outside Downloads and sufficient E: free space.

The media inspector writes:

- \`E:\Kerala2040MediaQA\renewable_media_inventory.json\`
- \`E:\Kerala2040MediaQA\index.html\`, a local navigation page
- \`E:\Kerala2040MediaQA\tiff_previews\*.png\`
- \`E:\Kerala2040MediaQA\pdf_contact_sheets\*\pages_0001_0020.jpg\` etc.,
  with page numbers for **every single page**, not just OCR hits
- \`E:\Kerala2040MediaQA\gsa_pvout_full_raster_qa.json\`

Opening the local \`index.html\` in a browser works because the generated
contact sheets are static local images; this is not the public Kerala2040 site.

## Return an auditable review package

The source folders are private. Share only a *small* QA bundle with this
conversation; **do not commit raw PDF/TIFF content or generated page images
to the public research repository**.

For a first pass, provide the two generated JSON reports and the PDF
contact sheets for the most relevant NISE floating-PV report and World Bank
PV-potential study/README. Individual PDF pages with unclear annexure tables
or site geometry can then be viewed at their original render resolution.
The original PDFs/GeoTIFFs are necessary only when a contact sheet is too
small for a reliable judgement.

I can compare the numeric TIFF audit results, identify page numbers worth
full-resolution reading and build a page-cited, source-classified evidence
crosswalk. Until that review is completed, any scanned-page table not
independently read is **not** a verified model input.

## Scientific safeguards

- Annual GSA PVOUT is kWh/kWp/year; average daily PVOUT is kWh/kWp/day.
  Long-term climatology uses 365.25 days and February 28.25 days.
- GSA GeoTIFF folders are related representations of the same source, not two
  independent measurements. Matching all pixels tests internal units only.
- Study-derived global PV masks are not notifications of Kerala forest/paddy
  exclusions; apply land, ecology and grid screens separately.
- NWDP FY2024–25 solar telemetry contains 6,007/6,007 zero values and cannot
  validate PV. NIWE onshore 150 m climatology does not establish offshore
  wind or wind-farm generation.
- NISE floating-PV figures 2.22 and 5.73 GWp are *alternative* study
  scenarios, not additive capacities or validated site-level permissions.
