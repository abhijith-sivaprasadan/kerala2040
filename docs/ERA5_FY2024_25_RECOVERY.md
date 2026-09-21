# ERA5 FY2024–25 source-gap recovery — 21 September 2026

**Acquisition status: NOT CLOSED.** The committed [ERA5 public manifest](../public/era5-daily-manifest.json) reflects a *legacy* acquisition plan: five January–March 2025 NetCDF files were recorded, while the five April–December 2024 **nine-month** requests failed with CDS `HTTP 403: cost limits exceeded — your request is too large`. These are request-cost failures, not evidence that Copernicus has no historical Kerala weather data.

The source code now defines a more granular plan: **5 Kerala representative locations × 4 three-month periods = 20 potential files**. This is a change of *request granularity*, not the discovery of another ten historical records; never add the old 5/10 and new 20-file plan. The original five NetCDF hashes are stored only in the existing public manifest. Their presence in a manifest does not prove the original raw bytes are still locally accessible.

## Recovery executed by the dedicated workflow

[ERA5 quarter recovery workflow](../.github/workflows/era5-quarter-recovery.yml) starts three independent jobs for the FY2024–25 missing quarters:

| Period | Expected bounded location requests |
|---|---:|
| April–June 2024 | 5 |
| July–September 2024 | 5 |
| October–December 2024 | 5 |

The existing January–March 2025 evidence stays unchanged. Each job requires the repository's existing authorized `CDSAPI_KEY`, downloads source NetCDFs into an Actions artifact, checks minimum size/file signature, records SHA-256, area/point, date window and any exact provider error, and publishes **no new public evidence**. The manifest is an *attempt report*. A successful source download is not a validated full-year weather series or a derived PV/wind-power model.

**Potential CDS follow-up:** If a three-month request is still over CDS's request-cost limit, reduce further to monthly windows (or shrink the spatial sample subject to research scope), retaining separate source hashes and failed attempts. Do not route around request quotas by fabricating outputs or claiming API success. Copernicus login, dataset licence acceptance, API key validity, availability and quotas remain prerequisites.

## Before changing the public manifest

1. Verify **original bytes** for every new and legacy file against source hashes, not only the JSON manifest.
2. Open NetCDF data and check exact time coordinates in UTC, complete hour counts (FY2024–25 has **8,760 hours**), five variable identities and units, valid spatial location, duplicate/missing hours, and source revision/reanalysis identity.
3. Match chunks by point and time without overlaps or silent imputation; verify the 2025 Jan–Mar originals are still available, or reacquire them.
4. Verify reuse and republication conditions; then publish source provenance and coverage through a separate reviewed admission. Weather observation/reanalysis is not measured Kerala solar/wind generation, and representative point boxes do **not** demonstrate an eligible statewide renewable capacity.

The 17 research-audit findings and scientific release gates remain unchanged by a retrieval attempt.
