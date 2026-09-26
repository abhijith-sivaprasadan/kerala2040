# KSEB FY2024-25 acquisition → parse → model-input pipeline (v1.5)

The remaining v1.5 source work is now executable as a single fail-closed chain.

## 1. Acquire the exact official packages

The durable inventory contains the twelve audited KSEB WordPress Download
Manager package IDs and the XLS/XLSX format shown by KSEB's own listing.

```bash
python scripts/acquire_kseb_monthly_fy2024_25_v1_5.py \
  --out-dir PRIVATE/kseb_monthly_fy2024_25 \
  --report results/hydro/kseb_monthly_acquisition_v1_5.json
```

The downloader uses the short official `?wpdmdl=<ID>` URL first and the
full package URL as fallback, follows redirects, writes through a temporary
file, checks workbook magic bytes, records response metadata and SHA-256, and
then runs the existing twelve-month bundle gate.

An HTML error/login page cannot pass as a workbook.

## 2. Parse every daily sheet semantically

`kseb_monthly_parser_v1_5.py` supports both:

- OOXML `.xlsx` via openpyxl;
- legacy OLE `.xls` via xlrd.

It does not use fixed column positions. Each daily sheet is located by its date,
the header row is identified by reservoir/storage/inflow semantics, and exactly
one `IDUKKI` row is required.

Explicit source units are preserved:

- `Inflow (MCM)` → `inflow_mcm`;
- `Average Inflow (Cumec)` → `average_inflow_cumecs`;
- `Spill (MCM)` → `spill_mcm`;
- unitless release columns stay `*_raw` rather than being guessed.

The known KSEB Idukki elevation convention is also retained: when the row's
FRL/MWL establishes feet, dynamic Idukki level fields are stored as `*_ft`
even if the generic workbook header says metre.

## 3. Require a complete official daily series

```bash
python scripts/extract_kseb_idukki_monthly_v1_5.py \
  --bundle-dir PRIVATE/kseb_monthly_fy2024_25 \
  --out results/hydro/kseb_idukki_official_input_v1_5.json
```

The content gate requires:

- 365 unique dates from 2024-04-01 through 2025-03-31;
- valid direct KSEB live storage on every date;
- valid direct KSEB `Inflow (MCM)` on every date;
- no interpolation;
- no dates outside the requested FY;
- successful reconciliation against the separately recovered official daily
  KSEB anchor pages.

Only after those conditions pass is the 364-day dispatch inflow series
(2024-04-01 through 2025-03-30) exposed to the physical model.

## Current execution boundary

The software pipeline is complete, but the present execution environment cannot
establish a network connection to `dams.kseb.in`. GitHub-hosted runners show
the same source reachability problem. This is an external byte-acquisition
blocker, not a missing package identifier or parser/model-code blocker.

The exact packages are already known and pinned in the repository. Once a
network that can reach KSEB runs step 1, steps 2 and 3 are deterministic.
