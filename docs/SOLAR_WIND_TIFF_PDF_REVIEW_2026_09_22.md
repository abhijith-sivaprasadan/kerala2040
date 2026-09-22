# Renewable source-media review: GeoTIFF pixels and individual PDF pages

**State:** reproducible QA tooling committed; full five-folder run and human
visual review of every PDF page are **not yet reported as complete**. Source
storage was already independently restored from the PRIVATE archive.
This document does not grant source licensing or admit data into the model.

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
