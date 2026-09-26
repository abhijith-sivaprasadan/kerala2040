# KSEB monthly reservoir bundle gate — v1.5

The official KSEB Dam Safety monthly-statistics index publishes one reservoir
file for every month of FY2024-25. This is the preferred route for building the
next full-year Idukki operations dataset because it avoids depending on hundreds
of intermittently reachable daily WordPress pages.

## Official FY2024-25 inventory

The project has verified that the official KSEB index lists all twelve files,
from April 2024 through March 2025. Their source inventory is stored in:

`data/evidence/hydro/kseb_monthly_inventory_fy2024_25_v1_5_2026_09_26.json`

A preserved raw snapshot of the official KSEB Download Manager listing was
then located in `Am4l-babu/aqua-sync`. It retains the JavaScript download
targets that are stripped from the text-rendered KSEB page. This resolves all
twelve WordPress Download Manager package IDs and the file-type icons.

The FY2024-25 bundle is a real mixture of legacy `.xls` and `.xlsx` files:

- XLSX: April, May, August, November, December 2024 and March 2025;
- XLS: June, July, September, October 2024 and January, February 2025.

The exact package IDs and normalized official KSEB URLs are stored in the
inventory JSON. The current execution environment still cannot retrieve the
binary payloads from `dams.kseb.in`, so the file bytes have **not** been
claimed as acquired.

## Fail-closed bundle gate

`src/kerala2040/kseb_monthly_bundle_v1_5.py` and
`scripts/audit_kseb_monthly_source_bundle_v1_5.py` define the next admission
gate.

A local bundle is ready for content/schema audit only when:

- exactly one file is mapped to each of the 12 required months;
- no month is missing;
- no month has duplicate candidates;
- every file has the exact XLS/XLSX container type advertised by the preserved
  official KSEB listing; and
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


## Official downloader

The package IDs are sufficiently resolved to make acquisition reproducible:

```bash
python scripts/download_kseb_monthly_fy2024_25_v1_5.py \
  --out-dir PRIVATE/kseb_monthly_fy2024_25
```

The downloader uses the exact official package slug + `wpdmdl` pairs,
streams each response to a temporary file, checks its magic bytes against the
expected XLS/XLSX format, and only then renames it into the bundle. HTML error
pages or unexpected containers are rejected rather than saved as spreadsheets.

A successful run also writes `manifest.json` with the source URL, package ID,
byte size and SHA-256 for every downloaded workbook. That manifest can be fed
directly into the bundle gate.
