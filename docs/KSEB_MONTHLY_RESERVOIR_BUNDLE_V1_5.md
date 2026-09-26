# KSEB monthly reservoir bundle gate — v1.5

The official KSEB Dam Safety monthly-statistics index publishes one reservoir
file for every month of FY2024-25. This is the preferred route for building the
next full-year Idukki operations dataset because it avoids depending on hundreds
of intermittently reachable daily WordPress pages.

## Official FY2024-25 inventory

The project has verified that the official KSEB index lists all twelve files,
from April 2024 through March 2025. Their source inventory is stored in:

`data/evidence/hydro/kseb_monthly_inventory_fy2024_25_v1_5_2026_09_26.json`

At this checkpoint the KSEB index exposes the titles, listed file sizes and
publication dates, but the retrieval surface used during the audit collapses
the WordPress Download Manager buttons and does not expose the twelve unique
underlying file hrefs. The file bytes have therefore **not** been claimed as
acquired.

## Fail-closed bundle gate

`src/kerala2040/kseb_monthly_bundle_v1_5.py` and
`scripts/audit_kseb_monthly_source_bundle_v1_5.py` define the next admission
gate.

A local bundle is ready for content/schema audit only when:

- exactly one file is mapped to each of the 12 required months;
- no month is missing;
- no month has duplicate candidates;
- every file has a recognized container type; and
- every file is SHA-256 fingerprinted.

Passing this gate **does not** make the files model input. It only allows the
next content-level schema audit. Reservoir values remain unadmitted until the
actual monthly files are inspected for their headers, units, dates and Idukki
rows.

### Automatic filename mode

```bash
python scripts/audit_kseb_monthly_source_bundle_v1_5.py \
  --bundle-dir PRIVATE/kseb_monthly_fy2024_25 \
  --out results/hydro/kseb_monthly_bundle_gate_v1_5.json
```

The automatic mode maps month names and years from filenames.

### Explicit manifest mode

For generic download filenames, create a JSON manifest:

```json
[
  {"month": "2024-04", "path": "file_01.pdf"},
  {"month": "2024-05", "path": "file_02.pdf"}
]
```

and run:

```bash
python scripts/audit_kseb_monthly_source_bundle_v1_5.py \
  --bundle-dir PRIVATE/kseb_monthly_fy2024_25 \
  --manifest PRIVATE/kseb_monthly_fy2024_25/manifest.json
```

The manifest is intentionally path-only. Hashes are calculated from the actual
bytes by the gate rather than trusted from user-entered metadata.

## Daily anchor recovery

The six dates left unconstrained by the SLDC cumulative-accounting layer now
have exact official KSEB daily post URLs. Five have full indexed Idukki rows
verified; 30 November has its storage, inflow and powerhouse discharge
independently verified, while unverified tail fields remain null in the durable
evidence instead of being copied from the third-party mirror.

These KSEB rate observations are an independent operations layer. They do not
replace missing strict-v1.4 SLDC MCM/day observations.

## Next admission stage

Once the twelve official monthly files are acquired:

1. run the byte-level bundle gate;
2. inspect file formats and schemas;
3. build a header-driven monthly parser for the formats actually present;
4. extract the Idukki daily series with per-file hashes and row-level source
   provenance;
5. reconcile monthly-file rows with the already verified official daily
   anchors;
6. evaluate storage/inflow/discharge/spill closure;
7. only then create the next stateful Idukki optimization input.
