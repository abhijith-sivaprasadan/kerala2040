# Kerala2040 renewable workstream — five-step handoff, 22 September 2026

## Verified scope and permanent-storage truth

The NWIC official Kerala **state boundary** (original EPSG:7755; verified SHA256 `a932ea29e7afd0fea1e1068f3beeeadb760e6b2baae9783f5822bbefd4224ebd`) was recovered from the prior official-boundary GitHub Actions artifact and reprojected to EPSG:4326. The original source is [NWIC state boundary](https://nwdp.nwic.gov.in/dataset/state-boundary). The first native-resolution resource extract was generated locally from these user-supplied data:

- [NIWE official 150 m wind atlas](https://niwe.res.in/Open_data_Set/open_wind_dataset/11/), 19,475,568 national source rows, **200,692** original-coordinate centres strictly inside the state. Median mean wind speed **3.91 m/s at 150 m**. The source's CUF and offshore resource are **not in the seven-column original CSV**.
- [Global Solar Atlas 2.0 India](https://globalsolaratlas.info/download/india), Solargis for World Bank Group / ESMAP, long-term source vintage 1999–2018: **46,241** native annual-PVOUT pixel centres within Kerala, median **1,493.5 kWh/kWp/year**; **513,823** native GHI raster centres, median **1,856.6 kWh/m²/year**. No legal eligibility inferred.
- Annual/daily PVOUT comparison was checked over all **46,241** corresponding Kerala cells; source unit ratio near 365.25, not 2024–25 production.

**Committed evidence**: [clip QA ledger](../data/evidence/solar/kerala_boundary_resource_clips_2026_09_22.json). **Reproducible processing**: [exact NWIC Kerala clipping script](../scripts/build_kerala_onshore_resource_clips.py) requires the original ZIPs and boundary Actions artifact. **Local binary output**: `kerala2040_resource_clips_2026_09_22.zip` is in the conversation download only. It contains actual GeoTIFFs, Kerala NIWE CSV, boundary and PNG maps. **These GeoTIFF/PNG/ZIP bytes have NOT been uploaded into GitHub**: the available connected GitHub write actions support text, while this runtime cannot authenticate a binary upload. Do not link to a non-existent Release.

## Raw original archival (user action required)

The committed [17-file solar manifest](../data/evidence/solar/solar_batch_2026_09_21_originals_manifest.json) has original user filenames/bytes/SHA256; **release_uploaded remains false**. Original NIWE `Wind.zip` has its own source QA. The original archives were available in the model's upload workspace for analysis, but the originals are *not permanently available from this repo*.

The permanent archival path is [solar Release uploader](../scripts/publish_solar_source_release.py) with its [SHA-checking restore script](../scripts/restore_solar_source_release.py). **Do not publish mixed-provider `Solar.zip`, third-party PDFs, NWDP data or NIWE restricted material solely because it was publicly downloadable.** For NIWE, a separate [rights-gated DRAFT publisher](../scripts/publish_niwe_original_release.py) exists. Source redistribution rights must be confirmed for each original; if rights are not granted, use a private immutable repository/store and a public SHA256-only metadata manifest, not a public GitHub Release.

On the user's Windows machine, after reviewing public redistribution permission, place all 17 original source files named in the manifest into one folder, install/authenticate `gh`, then run:

```powershell
git pull
gh auth login
python scripts/publish_solar_source_release.py --source-dir "E:\Kerala2040\solar-originals" --confirm-public-redistribution --publish
python scripts/restore_solar_source_release.py --dest "E:\Kerala2040\solar-restore-test"
```

The NIWE original needs an **independent** NIWE permission decision; only if publicly redistributable run:

```powershell
python scripts/publish_niwe_original_release.py --wind-zip "E:\Kerala2040\Wind.zip" --confirm-public-redistribution
```

NIWE uploader intentionally creates a **draft** release; do not publish before checking the rights. Verify *real* GitHub Release assets and restored SHA256, then update manifests; no manifest is auto-marked true merely because a script exists.

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
