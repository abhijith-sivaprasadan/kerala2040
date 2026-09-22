# Kerala2040 renewable workstream — five-step handoff, 22 September 2026

## Verified scope and permanent-storage truth

The NWIC official Kerala **state boundary** (original EPSG:7755; verified SHA256 `a932ea29e7afd0fea1e1068f3beeeadb760e6b2baae9783f5822bbefd4224ebd`) was recovered from the prior official-boundary GitHub Actions artifact and reprojected to EPSG:4326. The original source is [NWIC state boundary](https://nwdp.nwic.gov.in/dataset/state-boundary). The first native-resolution resource extract was generated locally from these user-supplied data:

- [NIWE official 150 m wind atlas](https://niwe.res.in/Open_data_Set/open_wind_dataset/11/), 19,475,568 national source rows, **200,692** original-coordinate centres strictly inside the state. Median mean wind speed **3.91 m/s at 150 m**. The source's CUF and offshore resource are **not in the seven-column original CSV**.
- [Global Solar Atlas 2.0 India](https://globalsolaratlas.info/download/india), Solargis for World Bank Group / ESMAP, long-term source vintage 1999–2018: **46,241** native annual-PVOUT pixel centres within Kerala, median **1,493.5 kWh/kWp/year**; **513,823** native GHI raster centres, median **1,856.6 kWh/m²/year**. No legal eligibility inferred.
- Annual/daily PVOUT comparison was checked over all **46,241** corresponding Kerala cells; source unit ratio near 365.25, not 2024–25 production.

**Committed evidence**: [clip QA ledger](../data/evidence/solar/kerala_boundary_resource_clips_2026_09_22.json). **Reproducible processing**: [exact NWIC Kerala clipping script](../scripts/build_kerala_onshore_resource_clips.py) requires the original ZIPs and boundary Actions artifact. **Local binary output**: `kerala2040_resource_clips_2026_09_22.zip` is in the conversation download only. It contains actual GeoTIFFs, Kerala NIWE CSV, boundary and PNG maps. **These GeoTIFF/PNG/ZIP bytes have NOT been uploaded into GitHub**: the available connected GitHub write actions support text, while this runtime cannot authenticate a binary upload. Do not link to a non-existent Release.

## Raw original archival — PRIVATE repository, user action required

The user chose a **private archive**, not public redistribution. The public
[17-file source manifest](../data/evidence/solar/solar_batch_2026_09_21_originals_manifest.json)
has original filenames, byte sizes, provenance and SHA256 only;
`release_uploaded` remains **false**. Separate original NIWE `Wind.zip` is
also SHA256-pinned. The proposed private destination is
[`abhijith-sivaprasadan/kerala2040-source-archive`](https://github.com/abhijith-sivaprasadan/kerala2040-source-archive), **verified PRIVATE with an initialized `main` branch and README on 22 September 2026**. No original binary assets have been uploaded yet. Do **not** upload raw originals
or derived source extracts to public `kerala2040` Releases.

**Private repository is created and its visibility and `main` README verified.** Keep its access limited to authorized people. Install and log in to [GitHub CLI](https://cli.github.com/) on the local machine. **The originals can stay in their existing nested folders**; pass their common parent to `--source-dir`. The uploader recursively locates all 17 original ZIP/PDF filenames and verifies each exact SHA256 and size before uploading. NIWE can be found recursively with `--wind-dir`. If you only have *extracted contents* and not the original ZIP bytes, the original manifest cannot be passed by re-zipping: use a separately identified folder snapshot and do not set `release_uploaded=true` for the absent originals.

Run from a current local checkout of public `kerala2040`:

```powershell
git pull
gh auth login
gh repo view abhijith-sivaprasadan/kerala2040-source-archive --json isPrivate

python scripts/publish_solar_source_release.py --source-dir "E:\Kerala2040"
python scripts/restore_solar_source_release.py --dest "E:\Kerala2040\solar-restore-test"

python scripts/publish_niwe_original_release.py --wind-dir "E:\Kerala2040"
python scripts/publish_niwe_original_release.py --verify --dest "E:\Kerala2040\wind-restore-test"
```

The uploader **aborts before upload if the destination is missing or public**.
Solar and NIWE uploads produce releases inside the separate PRIVATE repository;
a published release *inside a private repository* remains available only to
authorized repo viewers. Do not make this archive repository public or share
its access in violation of publisher terms. A private backup does not itself
override licence conditions. Upload checks exact local SHA256/bytes before
transfer and remote sizes; **the separate restore commands download all
originals again and verify their actual SHA256s**. Only after that real
remote check should `release_uploaded` be changed to true with the
private archive repo identity in the public manifest (never embed tokens
or signed download URLs). The private repo is a separate storage location:
the public research repo carries code, source links, hashes and reproducibility
instructions without exposing third-party raw bytes.

## Private archive completion — 22 September 2026

**Completed for the five-folder snapshot, not the 17 originally downloaded
provider ZIP/PDF byte streams.** The user ran the five-folder packager and
GitHub Release upload on their Windows computer, followed by an independent
download into a fresh restore directory. The final output was
`SUCCESS: all five PRIVATE folder snapshots and EVERY nested file SHA256 verified.`
GitHub's authenticated API independently confirms the destination repository
remains **private** and the release contains all **nine upload parts plus the
checksum manifest**, each in `uploaded` state with SHA256 metadata. See the
[public inventory of private release asset hashes and QA](
../data/evidence/solar/renewable_five_folder_private_archive_2026_09_22.json).

Private release tag: `renewable-five-folder-snapshot-2026-09-22`. This
privately stores all five extracted Downloads folder trees and their nested
files; files that are source ZIPs within those folders retain their bytes.
Repacked folder snapshots are not asserted to be byte-identical with all 17
original historical ZIP/PDF downloads. The separate `release_uploaded` flag
for those 17 specifically remains **false** until the exact provider-original
bytes are independently archived/restored. This storage milestone does not
change any solar/wind generation validation, buildable MW or 2040 model gate.

## Preferred archival path for the five extracted Downloads folders

The source owner has confirmed these **five existing folders**, not necessarily
the original 17 ZIP/PDF files:

```text
Downloads/
  global-pv-potential-study-raster-data-layers-globalsolaratlas/
  India_GISdata_LTAym_YearlyMonthlyTotals_GlobalSolarAtlas-v2_GEOTIFF/
  India_GISdata_LTAym_AvgDailyTotals_GlobalSolarAtlas-v2_GEOTIFF/
  Wind/
  Solar/
```

Use [the five-folder private archive script](../scripts/archive_renewable_folders_private.py).
It keeps every nested relative path; checks every file SHA256 and ZIP CRC;
packages the five folders independently into deterministic ZIP64 snapshots;
splits each snapshot into <=768 MiB upload parts; and uploads those parts plus
a private per-file checksum manifest to the verified **private** repository.
The `--verify` mode independently downloads the manifest and every part,
compares the remote manifest against the LOCAL preparation manifest, rebuilds
each ZIP and verifies every nested file's SHA256. The staging and restore
folders must be outside Downloads and preferably on a drive with ample free
space, as both compressed archives and their upload parts take disk space.

```powershell
# Run these from your local kerala2040 repository checkout.
git pull
gh auth login

$downloads = Join-Path $env:USERPROFILE 'Downloads'
$stage = Join-Path $env:USERPROFILE 'Kerala2040ArchiveStage'
$restore = Join-Path $env:USERPROFILE 'Kerala2040ArchiveRestore'

# Stage: requires the five named subfolders and a new EMPTY stage directory.
python scripts/archive_renewable_folders_private.py --source-root $downloads --staging-dir $stage

# Upload ONLY to the separately verified PRIVATE repository.
python scripts/archive_renewable_folders_private.py --staging-dir $stage --upload

# Fresh independent private download; verify ZIP + EVERY nested file checksum.
python scripts/archive_renewable_folders_private.py --staging-dir $restore --verify --reference-manifest (Join-Path $stage 'renewable-five-folders-manifest.json')
```

**Important identity distinction:** these are **content-preserving folder
snapshots**. Repacking extracted source files cannot reproduce the exact
bytes/SHA256 of an earlier provider archive. Therefore do NOT flip the
17-original `release_uploaded` manifest flag when this folder-snapshot
workflow succeeds; instead, record the separate private folder-snapshot
release and verified per-file manifest. If any of the original ZIP/PDF
files also remain nested inside the five folders, they are preserved as
files in the snapshots. The legacy exact-original uploader remains
available only for the exact, SHA-matching original files.

## Five-point FY2024–25 hourly sensitivities (calculated, not validated generation)

The earlier verified ERA5 source chronology is **20 original quarter artifacts, five grid points × 8,760 UTC hours** for 2024-04-01 through 2025-03-31; fields are `ssrd` (hourly J/m²), `u10`, `v10` (m/s) and `t2m` (K). The exact source artifacts were recovered locally from the two GitHub Actions source runs and processed with [hourly proxy script](../scripts/build_kerala_hourly_proxy.py); output is a **43,800 point-hour** `RESOURCE_PROXIES_NOT_VALIDATED.csv.gz` and `hourly_proxy_qa.json`, supplied in the conversation download. **The CSV binary has not been committed into GitHub.**

Numerical model choices are deliberately transparent **hypotheses**: hourly mean GHI = ERA5 SSRD/3600; PV PR=0.82, temperature coefficient -0.004/K and a simplified cell-temperature rise 0.025 K per W/m²; wind speed = ERA5 10 m vector speed × (150/10)^0.14, then scaled to NIWE long-term nearest-cell 150 m mean; generic wind curve cut-in/rated/cut-out 3/12/25 m/s. These are **not** measured height shear, manufacturer power curves, validated plane-of-array irradiance, actual plant availability or Kerala-wide 2040 generation. GSA long-term annual PVOUT is a **comparison only**: this FY profile is not arbitrarily scaled to equal the LTA yield. The source's FY2024–25 solar NWDP values are **6,007/6,007 zero** including daytime, so they cannot validate PV.

At illustrative locations, the local proxy script gave PV `kWh/kWp` per FY and wind generic full-load hours:

| Illustrative ERA5 point | PV FY proxy kWh/kWp | Wind FY *generic* proxy FLH |
|---|---:|---:|
| Kannur | 1,352.9 | 343.6 |
| Kozhikode | 1,308.5 | 290.3 |
| Kochi | 1,334.8 | 249.1 |
| Palakkad | 1,332.1 | 3,316.5 |
| Thiruvananthapuram | 1,424.5 | 978.4 |

**Neither the point-to-point comparison nor forced NIWE long-term wind-mean anchoring establishes forecast skill.** In particular Palakkad's 10 m source mean must be raised markedly to its selected long-term 150 m NIWE cell; that drives an illustrative FLH, not verified turbine yield.

## Feasible capacity by technology — fail closed

See [technology capacity gates](../data/evidence/solar/solar_wind_feasible_capacity_gates_2026_09_22.json). **No evidence-backed installable MW or range for rooftop PV, ground-mounted PV, floating PV, onshore wind or offshore wind can yet be calculated**, because technology-specific suitable-area geometry, genuine Kerala legal notifications, waterbody seasonality, grid interconnection, turbine/site design and/or offshore resource data are incomplete. The NISE **2.22 GWp** (20% surface) and **5.73 GWp** (broader area) are *alternative indicative published scenarios*, not an independently established feasible range. NIWE's user-buffered ~30.7 GW estimate is unscreened and NOT official-Kerala buildable capacity. We do not manufacture MW by multiplying atlas cell counts by 4.5 MW/km² or by PV kWh/kWp.

## Model admission

[Renewables admission gate](../scripts/gate_kerala_solar_wind_model_admission.py) intentionally fails until independent weather/generation validation, source storage, grid, legal ecology and technology-specific sites are verified **and** the existing project-wide historical and 2040 gates pass. No source-climatology TIFF, 5-site proxy CF or NISE paper estimate has been injected into the 2040 production optimisation as validated resource.

**User requests next:** (a) perform the one-time rights-reviewed authenticated binary upload on their machine (or authorize appropriate private storage, not unpermitted public redistribution); (b) obtain corrected FY solar irradiance or measured PV generation, wind mast sensor height, and eventually real site-specific KFD/NRSC/wetland, rooftop, reservoir and grid GIS from source agencies. The rest of the immediate model/screening implementation can progress without repeatedly downloading variants of GSA.
