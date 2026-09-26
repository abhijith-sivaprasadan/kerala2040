# KSEB Idukki monthly-workbook source pipeline — v1.5

The v1.5 source pipeline is now designed around KSEB Dam Safety's official
monthly reservoir workbooks rather than the third-party fixed-column daily
mirror.

## One-command workflow

From the repository root:

```bash
python scripts/run_kseb_idukki_source_pipeline_v1_5.py
```

The command:

1. downloads the 12 FY2024-25 KSEB packages using their verified WordPress
   Download Manager IDs;
2. verifies XLS/XLSX binary signatures and SHA-256 fingerprints;
3. requires exactly one source workbook for every month April 2024–March 2025;
4. scans each workbook for daily sheets;
5. finds Idukki by reservoir name and fields by semantic header text;
6. preserves direct MCM and cumecs representations separately;
7. requires all 365 daily Idukki records;
8. runs ending-date water-balance QA;
9. flags source anomalies without altering them.

If the files have already been downloaded:

```bash
python scripts/run_kseb_idukki_source_pipeline_v1_5.py --skip-download
```

## Why the report-date convention is used

Two real KSEB workbook exemplars were inspected.

The modern July 2026 workbook contains direct daily MCM terms. On 29 of 30
consecutive transitions, applying each report date's inflow/outflow to the
preceding storage interval produces a residual clustered tightly around
**-0.155 MCM/day**.

The legacy November 2020 XLS reports flow terms in cumecs. After converting
cumecs to daily MCM, its normal transitions cluster around
**-0.145 MCM/day** under the same convention.

The residual is not labelled evaporation, seepage, diversion or measurement
error without a KSEB definition. It is retained as an unresolved balance term.

## Source-error handling

The real July 2026 source includes one striking value:

`Power House Discharge (MCM) = 1994` on 5 July.

That creates a roughly 1,992 MCM balance residual while neighboring days close
near -0.155 MCM. The pipeline does **not** rewrite it to 1.994. It records the
published value and flags the date for source review.

The same principle applies to FY2024-25: no decimal shifts, interpolation or
manual source repairs are silently introduced.

## Network boundary

GitHub-hosted runners resolve `dams.kseb.in` to `117.239.153.11` but
currently time out before establishing TCP connections on both ports 80 and
443. This has been tested directly against monthly package IDs 4421 and 5212.

Therefore source acquisition must run from a network that can reach KSEB.
The downstream bundle gate, parser and QA are deterministic and can run
anywhere after the bytes are acquired.
