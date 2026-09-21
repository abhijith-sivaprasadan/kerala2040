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
`abhijith-sivaprasadan/kerala2040-source-archive`, which does **not yet exist**
or has not been verified accessible/private. Do **not** upload raw originals
or derived source extracts to public `kerala2040` Releases.

**One-time user setup (GitHub UI):** create a **PRIVATE** repository named
`kerala2040-source-archive` under `abhijith-sivaprasadan`, initialize it
with a README so the default branch exists, and keep access limited to
authorized people. Install and log in to [GitHub CLI](https://cli.github.com/)
on the local machine; keep all 17 original solar-batch files together,
named exactly as in the manifest, plus original `Wind.zip` separately.

Run from a current local checkout of public `kerala2040`:

```powershell
git pull
gh auth login
gh repo view abhijith-sivaprasadan/kerala2040-source-archive --json isPrivate

python scripts/publish_solar_source_release.py --source-dir "E:\Kerala2040\solar-originals"
python scripts/restore_solar_source_release.py --dest "E:\Kerala2040\solar-restore-test"

python scripts/publish_niwe_original_release.py --wind-zip "E:\Kerala2040\Wind.zip"
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
