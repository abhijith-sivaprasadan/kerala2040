# Data policy and folder contract

The repository should remain reproducible without illegally redistributing third-party data.

## Local folders

- `data/raw/`: immutable source downloads; normally gitignored.
- `data/interim/`: cleaned but not model-ready data; gitignored.
- `data/processed/`: model-ready datasets. Commit only when licence, sensitivity and size permit.
- `data/external/`: manually supplied or restricted inputs; gitignored unless explicitly cleared.
- `data/metadata/`: source records, retrieval dates, units, hashes and licences; commit these.

## Canonical principles

1. Raw files are immutable.
2. Every processed column has a unit.
3. Asia/Kolkata is the operational timezone; preserve UTC where available.
4. Imputed values are explicitly flagged.
5. Confidential utility data and security-sensitive network data are never committed.
6. Bhuvan/NRSC and other licence-restricted raw layers should be acquired by scripts or documented procedures, not mirrored automatically.
7. Model outputs must reference the exact source manifest used.

## First data products

The CET MVP should prioritise:

- hourly Kerala demand;
- internal generation by major technology/station;
- net/interface imports where available;
- installed/available capacity;
- hydro/reservoir indicators;
- weather series;
- official annual totals for calibration;
- project/technology cost assumptions with provenance.
