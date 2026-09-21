# Measured interval intake — the historical calibration blocker

**Status, 21 September 2026: NO FY2024–25 measured 8,760-hour or
35,040-block Kerala load plus actual-interchange dataset has been acquired by
this repository. The historical-interval and 2040 model release gates remain
BLOCKED.** This is a private admission and QA tool for when the custodian
provides authentic records, not a claim that the records have arrived.

## Why this task, and why the current public files do not suffice

The observed Kerala SLDC FY2024–25 archive has 354 of 365 original five-section
daily reports and 11 unresolved dates. A verified **daily energy** balance is
not a measured demand shape or a 15-minute dispatch chronology. The CEA Kerala
resource-adequacy work analyses FY2024–25 hourly demand, but its published
figures and frequency summaries are not a released full hourly CSV; a graph
digitisation would not be measurement. SRPC DSM weekly statements include
official **scheduled versus actual drawal** and are useful for an independent
interchange check, but DSM drawal is not total Kerala demand, and its
revisions/settlement boundary cannot silently replace SLDC `Net Import`.
The original eleven SLDC reports are a **separate** outstanding request.

Sources and acquisition records:

- [Kerala SLDC statistics](https://sldckerala.com/index.php?id=1);
  [official office directory](https://sldckerala.com/index.php?id=3).
- [CEA Kerala resource adequacy report](https://cea.nic.in/resource_adequacy_st/report-on-resource-adequacy-plan-for-kerala-up-to-2035-36/).
- [SRPC example, 17–23 February 2025 DSM weekly statement](https://www.srpc.kar.nic.in/website/2024/commercial/dsm17-23feb25.pdf):
  an independent **daily** actual-drawal reference, not our source of measured
  Kerala state load or accepted full-year interchange series.
- [Detailed primary-source review](INTERVAL_ELECTRICITY_SOURCE_REVIEW.md),
  [unsent SLDC interval-data request](SLDC_DATA_REQUEST_DRAFT.md) and
  [unsent eleven-day report request](SLDC_MISSING_11_REQUEST_DRAFT.md).
  Do not present either request draft as delivered correspondence.

## Private source intake contract

The original custodian should provide the state-level **actual demand met**
and **actual net import** (positive import, negative export), both as interval
average MW on one interval-start IST clock and the same explicit system
boundary. Do **not** map schedule, regional DSM actual drawal, hourly national
PSP, peak snapshots, interval MWh or daily SLDC MU into these fields just
because units can be made numerically similar.

Prepare the source-supplied CSV privately with **exactly** this header:

```csv
timestamp_ist,demand_mw,actual_net_import_mw
```

The first timestamp must be `2024-04-01T00:00:00+05:30`; timestamps advance
by exactly 15 or 60 minutes, ending at `2025-03-31T23:45:00+05:30` or
`2025-03-31T23:00:00+05:30`. India Standard Time has no DST gap.
A full ordinary FY2024–25 is 365 days / 35,040 blocks or 8,760 hours.
Blank demand/interchange cells must stay missing and **fail** admission,
never become zero. Actual net interchange may be negative when exporting.

The companion JSON records the original filename, a SHA-256 of the **exact
CSV bytes being inspected**, original HTTPS source URL, original custodian,
real retrieval time, exact agency revision/version, time interval and units,
demand met and actual interchange boundaries, sign convention and explicit
reuse/redistribution terms. Example **structure only**—do not use these
values to claim a source has been obtained:

```json
{
  "classification": "observed",
  "source_type": "kerala_sldc",
  "source_url": "https://sldckerala.com/REPLACE_WITH_ACTUAL_SOURCE",
  "source_sha256": "REPLACE_WITH_SHA256_OF_THE_EXACT_INPUT_CSV",
  "obtained_at_utc": "REPLACE_WITH_REAL_UTC_TIME",
  "original_filename": "REPLACE_WITH_REAL_FILENAME",
  "revision_id": "REPLACE_WITH_AGENCY_REVISION_OR_AS_ISSUED_ID",
  "interval_minutes": 15,
  "timestamp_semantics": "interval_start",
  "timezone": "Asia/Kolkata",
  "demand_scope": "kerala_state_demand_met_mw",
  "interchange_scope": "kerala_actual_net_interchange_mw",
  "interchange_sign_convention": "positive_import_negative_export",
  "reuse_terms": "REPLACE_WITH_ACTUAL_DATA_USE_AND_REPUBLICATION_TERMS"
}
```

If the two series arrive from different custodians, retain their original
files, hashes, units and revisions separately: this single-CSV check **does
not** authenticate an analyst-made merge. Reconcile the two inputs first;
only a provenance-reviewed normalized dataset should be inspected here.
Hashing a transformed CSV authenticates its *bytes*, not the source authority.

Local execution (never use GitHub Actions for confidential agency files):

```bash
python scripts/admit_measured_intervals.py \
  --csv data/raw/kerala_fy2024_25_measured_private.csv \
  --source-manifest data/raw/kerala_fy2024_25_source_private.json \
  --report data/processed/kerala_fy2024_25_interval_qa_private.json
```

The normal `data/raw/` and `data/processed/` directories are gitignored.
The tool returns exit code **2** for a rejected source. An accepted input
writes only a private QA JSON report (source hash, 365 daily energy sums,
scope, interval count and explicit release blockers). It does **not** copy
the original CSV into public directories, modify a published manifest,
replace the old 8,760-hour proxy, generate a new public webpage result,
or flip either audit gate. Test data under `tests/` are **synthetic only**.

## Admission still requires independent human/source review

1. Verify original agency transmission, original raw hash if different from
   the normalized CSV, original revision precedence, permissions and that
   the scope was actual Kerala state demand met plus actual net interchange.
2. Check official FY energy and coincident peaks against the measured
   chronology, with explicit treatment of gross imports, exports, rooftop
   generation, transmission losses and metering boundaries.
3. Reconcile overlap days with the 354 daily SLDC balances and compare
   independent SRPC settlement records without assuming exact boundary
   equality. Investigate residuals; do not force them to zero by rescaling.
4. Preserve 11 missing daily SLDC reports as missing even if separate
   interval observations are subsequently obtained.
5. Review source-use permission. Only then add independently reviewed
   evidence and change the committed scientific gate rules in a **separate**
   source-admission PR. A self-declared manifest or green CI is not a
   scientific validation certificate.

**No model-facing measured chronologies or derived results are newly
published by this work.**
