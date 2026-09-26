# KSEB monthly reservoir source inventory — FY2024-25

The official KSEB Dam Safety Organisation **Monthly Statistics** page provides a
stronger acquisition route for Idukki v1.5 than enumerating hundreds of daily
WordPress posts.

The page describes its products as **"Daily Water levels of major reservoirs in
a month"** and lists one downloadable file for every month from April 2024
through March 2025.

## Official FY2024-25 inventory

| Month | Listed size | Publication date |
|---|---:|---|
| 2024-04 | 367.56 KB | 2024-04-30 |
| 2024-05 | 498.72 KB | 2024-05-31 |
| 2024-06 | 419.50 KB | 2024-07-02 |
| 2024-07 | 528.50 KB | 2024-07-31 |
| 2024-08 | 533.27 KB | 2024-08-31 |
| 2024-09 | 529.50 KB | 2024-09-30 |
| 2024-10 | 533.00 KB | 2024-11-01 |
| 2024-11 | 516.13 KB | 2024-12-02 |
| 2024-12 | 601.74 KB | 2024-12-31 |
| 2025-01 | 542.50 KB | 2025-01-31 |
| 2025-02 | 398.50 KB | 2025-03-03 |
| 2025-03 | 451.41 KB | 2025-04-04 |

Official index:
`https://dams.kseb.in/?p=329`

This is continuous monthly coverage of the full FY2024-25 year.

## Acquisition boundary

The WordPress Download Manager controls are visible on the public page, but the
current text retrieval does not expose distinct underlying package/file URLs.
The project therefore does **not** guess:

- WordPress package IDs;
- direct download URLs;
- file extensions;
- MIME/file types;
- hashes.

The listed file size is source metadata only. It is not a substitute for
fingerprinting the bytes.

## Local byte gate

`scripts/audit_kseb_monthly_reservoir_files_v1_5.py` accepts monthly files
once they have actually been downloaded. It records:

- SHA-256;
- exact byte count;
- detected container/file type from file signatures;
- supplied filename/extension;
- the corresponding official inventory record;
- a non-binding comparison against the rounded size shown on KSEB.

The detector can distinguish common PDF, XLS/OLE, XLSX/OpenXML, ODS, generic
ZIP, HTML, CSV/TSV/text and unknown binary containers. Detection is independent
of the filename extension.

No table parser is selected until the actual file type is known.

Example:

```bash
python scripts/audit_kseb_monthly_reservoir_files_v1_5.py \
  --month-file 2024-04=/path/to/downloaded_file \
  --month-file 2024-05=/path/to/another_file \
  --out results/hydro/kseb_monthly_file_audit_v1_5.json
```

## Scientific role

These monthly official files are now the preferred source-acquisition path for
v1.5 because they may provide a complete, agency-published FY2024-25 daily
reservoir record with only twelve source artifacts.

This inventory does **not** claim that the file bytes have been obtained or
that they contain inflow/discharge/spill fields. That will only be established
after each file is downloaded, fingerprinted, and inspected.

The strict v1.4 SLDC evidence remains unchanged and separate.
