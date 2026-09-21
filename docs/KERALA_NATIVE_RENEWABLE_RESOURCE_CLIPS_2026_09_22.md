# Kerala-only NIWE and solar native-grid source clips (22 September 2026)

**Source QA and numerical results:** [committed QA summary](../data/evidence/solar/kerala_native_resource_clips_2026_09_22.json). **Original data and the derived GeoTIFF/CSV/PNG bundle are not in GitHub**. The derived ZIP was created in the user conversation workspace and supplied separately; its byte size and SHA256 are pinned in the committed QA. This document does not pretend that the source ZIPs or resulting maps have been pushed to the public repo.

## Completed, using actual original bytes

- Recovered the previously acquired original NWIC **36-state boundary source** from [the GitHub Actions source-probe run](https://github.com/abhijith-sivaprasadan/kerala2040/actions/runs/35517474497) (artifact `official-Kerala-boundary-probe-NOT-capacity-eligibility`). Reverified exact **20,809,092-byte original ZIP SHA256 `a932ea29e7afd0fea1e1068f3beeeadb760e6b2baae9783f5822bbefd4224ebd`**, extracted the sole Kerala feature and transformed original **EPSG:7755** to WGS84 EPSG:4326. Original page: [NWIC state boundary](https://nwdp.nwic.gov.in/dataset/state-boundary). User-provided third-party originals and the administrative boundary have **unreviewed public derivative/re-hosting rights**: don't commit their bytes or a proprietary resource layer to public Git without confirmation.
- Clipped the original [Global Solar Atlas 2.0 India](https://globalsolaratlas.info/download/india) **annual PVOUT**, average-daily PVOUT, February/July average-daily PVOUT, and **annual GHI** to **exact NWIC Kerala pixel centres at each original source resolution**. Credits: **Solargis, World Bank Group, ESMAP / Global Solar Atlas 2.0**. PVOUT reference 1999–2018, not FY2024–25. Native PVOUT grid 30 arcseconds; GHI 9 arcseconds. No resampling/false uniform grid.
- Clipped the **original NIWE national 150 m CSV** within the exact Kerala polygon using **source point centres** (not the prior 818,936-point multi-state rectangle and not the user-drawn 30.7 GW NIWE popup envelope). Source [NIWE 150 m atlas](https://niwe.res.in/Open_data_Set/open_wind_dataset/11/); 150 m height, stated 500 m model grid, mean speed/Weibull/density/WPD, no hourly generation or map CUF. Source SHA pinned in [NIWE QA](../data/evidence/gis/niwe_150m_user_supplied_source_qa_2026_09_21.json). Kept offshore separate; no offshore resource attributed from this onshore atlas.

| Descriptive exact Kerala onshore result | Value | Interpretation |
|---|---:|---|
| NIWE 150 m source points inside NWIC polygon | **200,692** | Native point-centre inclusion; not MW or turbine sites |
| NIWE median source mean wind speed | **3.91 m/s at 150 m** | Unweighted source point median; 95th percentile **7.766 m/s** |
| NIWE median source wind-power density | **78.93 W/m²** | 95th percentile **511.43 W/m²**, not electrical generation |
| GSA 30 arcsecond PVOUT valid pixel centres | **46,241** | Native raster cell-centre sample count, not PV installation area |
| GSA annual PVOUT source-cell median | **1,493.51 kWh/kWp/year** | Publisher's standard long-term source PV system, not current Kerala generation |
| GSA mean daily PVOUT source-cell median | **4.089 kWh/kWp/day** | Climatology, not an observed FY |
| GSA February / July daily source-cell medians | **5.212 / 2.941 kWh/kWp/day** | Spatially independent unweighted medians |
| GSA annual GHI 9 arcsecond valid pixel centres | **513,823** | Unweighted source mean annual surface irradiation, median **1,856.57 kWh/m²/year** |

**Unit test across all 46,241 mutually finite Kerala PVOUT cells:** annual total divided by long-term mean-day output = **365.25** (max absolute difference 0.000183 days). This confirms annual/day-file unit reconciliation at all matching clipped cells. It does not prove FY2024–25 measured solar availability.

## Derived outputs

The verified user-workspace archive `kerala2040_resource_clips_2026_09_22.zip` contains five solar GeoTIFFs, the gzip-compressed original-column NIWE Kerala-only point table, the NWIC-derived state geometry, illustrative resource PNG maps, README and complete per-layer QA. SHA256: `c387752ba391494c83fb407b67ee25699d197ae7c08fae47ba281d14f43d3652`. The ZIP's own CRC integrity test passed. **This is available as a download in the conversation, not as a repo asset.**

These are **descriptive resource statistics**, not an installable wind-capacity estimate, a statutory eligibility screen, hourly 2024–25 generation, an offshore resource assessment, or a validated economic potential. Study-scale Level 1/2 World Bank PV masks, notified Kerala forest/wetland and marine exclusions, grid access, 150 m turbine curves, PV temperature and all siting constraints remain separate. All-zero NWDP solar FY2024–25 readings cannot validate the PV output.

## Reproduce without re-downloading publisher sources

After the original source ZIPs have been properly archived, the repo includes [a source-checking clip builder](../scripts/build_kerala_renewable_resource_clips.py). The script accepts either the `Wind.zip` original user bundle or NIWE's **unmixed original** `150m_Map_Data_A_to_G.zip`; do not upload the user's mixed Wind.zip to a public release. The NWIC original can be reacquired by re-running the source-probe workflow if the current artifact expires.

Example for a Windows PowerShell workstation with the 17 original solar files in `E:\\Kerala2040\\SolarSources`:

```powershell
gh run download 35517474497 --repo abhijith-sivaprasadan/kerala2040 --name official-Kerala-boundary-probe-NOT-capacity-eligibility --dir .\\nwic_source
python scripts/build_kerala_renewable_resource_clips.py --sources "E:\\Kerala2040\\SolarSources" --wind "E:\\Kerala2040\\Wind.zip" --boundary-artifact ".\\nwic_source" --output "results\\gis\\kerala_renewables"
```

Install `numpy pandas rasterio shapely pyproj` if the selected Python environment does not already include the GIS stack. The repo builder generates native clip rasters, NIWE CSV and QA, while the user-workspace derived ZIP also includes presentation PNG maps. Rerunning the builder will hash-verify its original-source inputs.

## Binary archive: still blocked on actual transfer and licensing review

The [solar batch manifest](../data/evidence/solar/solar_batch_2026_09_21_originals_manifest.json) records **17 originals but `release_uploaded=false`**. Text manifests/hashes/scripts are not the raw ZIP bytes. There is no authenticated GitHub release-asset binary upload endpoint available through this chat's connector, and this model's runtime cannot connect directly to GitHub. Nothing has been marked remotely archived.

The existing [solar source uploader](../scripts/publish_solar_source_release.py) handles the 17 original solar files once public redistribution is reviewed; [the separate NIWE uploader](../scripts/publish_niwe_source_release.py) extracts **only NIWE's 251,971,340-byte original ZIP** from `Wind.zip`, avoiding unrelated third-party files, hash-checks it and verifies the remote download before publishing. **Only pass public-redistribution confirmation if actual publisher permissions permit rehosting.** Otherwise keep original data in authorised private storage, and commit only the hashes and derived public data permitted by the licence. Neither script's existence satisfies archival until the release bytes have been uploaded and verified.
