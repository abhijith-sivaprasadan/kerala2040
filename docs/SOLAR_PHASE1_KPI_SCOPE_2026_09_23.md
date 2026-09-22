# Solar phase 1 KPI scope — 23 September 2026

**Status: next research question and acceptance criteria, NOT a completed district analysis, site-eligibility screen or solar capacity estimate.** Wind phase 1 is frozen at [its poster research question and conclusion](WIND_PHASE1_DISTRICT_NORMALIZED_CLOSEOUT_2026_09_23.md).

## Proposed research question

**How does the modelled long-term solar PV resource and its seasonal variation differ across Kerala's 14 districts when original Global Solar Atlas pixels are assessed within consistent NWIC administrative boundaries?**

This is an explicitly **descriptive resource** question. Global Solar Atlas 2.0 long-term 1999–2018 PVOUT is for the publisher's assumed reference PV system, not measured FY2024–25 production, current Kerala PV fleet performance, roof availability or grid-connected output.

## Input evidence already acquired

The [exact original-source Kerala clip audit](../data/evidence/solar/kerala_native_resource_clips_2026_09_22.json) records **46,241** annual PVOUT pixel centres at native 30-arcsecond spacing; long-term annual PVOUT source-cell median **1,493.507 kWh/kWp/year**; mean-daily source-cell median **4.089 kWh/kWp/day**; independently reported February and July daily PVOUT medians **5.212** and **2.941 kWh/kWp/day**, respectively. The separate annual GHI 9-arcsecond native grid has **513,823** centres and an unweighted median **1,856.566 kWh/m²/year**. The 46,241 mutually finite annual/day PVOUT cells pass the publisher-source 365.25 ratio check. Original/derived raster bytes are not publicly redistributed.

These figures are **separate unweighted marginal medians**; February and July median values should not be divided and described as the seasonality of a representative common pixel. Do not mix GHI and PVOUT pixel denominators or treat PVOUT as installed MW or electricity delivered.

## Five acceptance gates for the solar KPI

1. **Source integrity and exact-boundary clip:** verify the original NWIC district CRS/source geometry and the private *native* GSA annual/daily and seasonal PVOUT rasters and metadata; use original pixel centres, not a resampled visual map. The public QA summary by itself does not recreate raw pixel locations.
2. **District partition:** assign every in-state mutually valid PVOUT pixel centre to exactly one NWIC district; explicitly report unmatched/multiple matches and keep an unassigned bucket until reconciled. Wind's complete partition does not prove the solar grid will also close.
3. **PVOUT accounting and seasonality:** report district count, finite/missing coverage, annual PVOUT distribution and *matched-cell* February/July change for each native PVOUT cell; if monthly rasters are available, show all 12 months. Do not compare independently selected pixel medians as though they form a paired time series.
4. **Spatial descriptive interpretation:** show district-normalized distribution/seasonality with denominator QA and at least one original vector poster figure. Identify that PVOUT represents publisher reference-PV-system climatology, not proposed plant performance or land capacity.
5. **Close phase 1, not the deployment model:** publish reproducible aggregate QA, a bounded question/conclusion and a website section only when the first four gates pass. Hold native land-cover/rooftop/floating suitability, statutory exclusions, real-year temperature- and technology-adjusted yield, grid hosting, installed MW and measured-generation validation in later phases.

**Current gates:** source clip evidenced; district PVOUT overlay **not yet completed**; paired seasonal cell statistics **not yet completed**; solar phase 1 **open**; `feasible_capacity_MW=null` and `model_admitted=false`.

## Immediate next computation

Recover the existing verified private GSA native clips (and original NWIC national district ZIP), independently check hashes/CRS, and run a fail-closed 14-district pixel-centre join. Report precise marginal versus paired statistics and missing-data denominators *before* choosing the solar poster message. Separately, Kerala2040's measured interval electricity chronology remains a higher-priority dependency for full 2040 model calibration; this solar work is the next **bounded renewable KPI** rather than a replacement for that system-level gap.
