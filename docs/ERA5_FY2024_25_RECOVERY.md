# ERA5 FY2024–25 source-gap recovery — 21 September 2026

**Acquisition status: NOT CLOSED.** The committed [ERA5 public manifest](../public/era5-daily-manifest.json) reflects a *legacy* acquisition plan: five January–March 2025 NetCDF files were recorded, while the five April–December 2024 **nine-month** requests failed with CDS `HTTP 403: cost limits exceeded — your request is too large`. These are request-cost failures, not evidence that Copernicus has no historical Kerala weather data.

The source code defines **5 Kerala representative locations × 4 three-month periods = 20 source-request windows**, not 20 guaranteed NetCDF files. This is a change of *request granularity*, not the discovery of another ten historical records; never add the legacy 5/10 record count to the new plan. The original five Jan–Mar NetCDF hashes are stored only in the existing public manifest. Their presence in a manifest does not prove the original raw bytes are still locally accessible.

## Recovery executed by the dedicated workflow

[ERA5 quarter recovery workflow](../.github/workflows/era5-quarter-recovery.yml) starts **15 independent location-quarter jobs** for the FY2024–25 missing quarters (maximum two concurrent CDS jobs). Every job retains its own manifest and source-data artifact, so one failure does not discard the other four locations:

| Period | Expected bounded location requests |
|---|---:|
| April–June 2024 | 5 |
| July–September 2024 | 5 |
| October–December 2024 | 5 |

The existing January–March 2025 evidence stays unchanged. Each job requires the repository's authorized `CDSAPI_KEY`, stores the **original provider response**, checks minimum size and member signatures, records SHA-256, area/point, date window and exact provider errors, and publishes **no new public evidence**. The manifest is an *attempt report*. A successful source download is not a validated full-year weather series or a derived PV/wind-power model.

**Verified CDS response behaviour (21 September 2026):** A successful Kochi April–June 2024 request returned a **ZIP**, despite requesting NetCDF and `download_format=unarchived`. Its separate NetCDF members were `data_stream-oper_stepType-instant.nc` (t2m, u10, v10) and `data_stream-oper_stepType-accum.nc` (ssrd, tp). The original downloader rejected/deleted this valid ZIP; the corrected downloader retains the original ZIP and extracts and separately hashes both components. The focused [live acquisition run](https://github.com/abhijith-sivaprasadan/kerala2040/actions/runs/35622367322) succeeded. Inspection of its source artifact showed **2,184 UTC hourly instants, no duplicates/missing hours, all five variables, and no nonfinite array values** for this single location-quarter. This result must not be extrapolated to the other 14 missing location-quarters or the legacy quarter.

The new manifest counts NetCDF *components* in `files_succeeded` and request windows separately in `source_windows_succeeded`/`windows_completed`. A two-member ZIP is one successful source window, not two weather coverage windows.

**Automatic fallback:** If a three-month request still exceeds the CDS request-cost limit, the retriever records the original error and retries the same location as three separate one-month requests. It checks each returned NetCDF signature, preserves each original SHA-256 and fails the quarter if any month is absent or invalid. Do not bypass provider quotas by inventing outputs or claiming API success. Copernicus login, dataset licence acceptance, API key validity, availability and quotas remain prerequisites.

## Before changing the public manifest

1. Verify **original bytes** for every new and legacy file against source hashes, not only the JSON manifest.
2. Open NetCDF data and check exact time coordinates in UTC, complete hour counts (FY2024–25 has **8,760 hours**), five variable identities and units, valid spatial location, duplicate/missing hours, and source revision/reanalysis identity.
3. Match chunks by point and time without overlaps or silent imputation; verify the 2025 Jan–Mar originals are still available, or reacquire them.
4. Verify reuse and republication conditions; then publish source provenance and coverage through a separate reviewed admission. Weather observation/reanalysis is not measured Kerala solar/wind generation, and representative point boxes do **not** demonstrate an eligible statewide renewable capacity.

The 17 research-audit findings and scientific release gates remain unchanged by a retrieval attempt.
