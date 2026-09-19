# Audited scientific release gates (repo evidence)

This is the continuation of the 18 September 2026 scientific-readiness audit.
Do not equate completed acquisition code, successful optimisation, downloaded
archives, or external study results with verified model inputs.

## Reproduce the current audit

    python scripts/check_readiness.py

Outputs:
- results/audit/readiness.json: per-finding statuses and individual release-gate results;
- results/audit/readiness.md: acquisition table for researchers.

To require a specific gate in a release job:

    python scripts/check_readiness.py --require-gate daily_accounting
    python scripts/check_readiness.py --require-gate techno_economic_2040

A failed required gate exits **2**, while the default reporting-only command
returns zero if the evidence is internally consistent. A source QA
inconsistency is an error, not a "missing evidence" status.

The audit workflow uploads its report as a GitHub Actions artifact. The
v1.0.1 website remains pinned to its immutable source SHA; do not update its
SOURCE_COMMIT to a prototype/uncertified solver commit.

## Evidence versus implementation

The committed SLDC source QA reports 354 observed and 11 missing FY2024-25
dates. Its raw HTML hashes, report dates and observed-day daily accounting
pass the existing checks. The annual observed sum is **not** a 365-day annual
measurement. The 8,760-hour reconstructed chronology conserves source
daily energy but has no measured interval observations. It cannot promote
the "measured_interval" gate to passed.

The committed ERA5 manifest reports five of ten expected files; it does
not establish completed-year weather or verified power-generation profiles.
The GIS config is an acquisition *catalogue*. Earlier locally acquired
official flood archives require byte-level retrieval, licensing/CRS
inventory, overlay work and technology-specific capacity ceilings before
passing a GIS model-input gate. The research repo does not automatically
contain every local/CI raw artifact. Do not mark previously downloaded GIS
files "absent from the world" just because they are not committed.

The techno-economic registry preserves national CEA/CERC external
benchmarks and deliberately leaves unselected Kerala 2040 values null.
These are actual unresolved inputs, not software defaults. Daily import
MUs and the screened 6500 MW parameter are NOT actual interface transfer
capabilities. SLDC reservoir energy equivalents cannot be turned into
independent generators/stores without checking cascading water pathways.

The site/release can publish daily observed **evidence** with those
qualifications; a validated 2040 least-cost/adequacy result is blocked.
An explicitly proxy-labelled demand sensitivity is allowed only as a
research experiment, not a release-gated techno-economic conclusion.

## Closing a finding

Acquire primary files (privately where publication terms require it);
retain URLs, exact vintage, units, retrieval timestamp, checksum and
metering/geographic boundary. Implement the appropriate independent
validator **before** changing a gate from blocked to verified. Then
re-run the audit and check specific physical / accounting invariants.

Do not mark a finding closed by editing an audit status, inserting a
published scenario value in a null Kerala model field, or adding a
self-attested JSON manifest. Completion requires an actual validated
source and a check that examines the correct data. A real measured-hourly
validator should check 35,040 quarter-hour intervals (if at 15-min
resolution), IST boundaries, duplicates/gaps, average-MW semantics,
source hash, and aggregation against SLDC observed daily totals. Similar
independent validators will be needed for hydro, GIS, asset nameplates,
interconnection and financial assumptions.

The acquisition and evidence checklist is maintained in
configs/audit_findings.yaml. Audit-gate implementation is in
src/kerala2040/audit_readiness.py. If the first source retrieval remains
unavailable, mark the model with its limitation rather than fabricating
a result. The next defensible build is *input validation*, not merely
another unconstrained 2040 solver.
