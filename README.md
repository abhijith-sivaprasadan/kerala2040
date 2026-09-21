# Kerala 2040

**Energy Sovereignty, Ecological Resilience and Fiscal Feasibility**

> **v1.0.0 — Data Platform / Historical Foundation.** This release provides
> source-labelled historical evidence, reproducible ingestion and a public dashboard.
> It is **not** a validated 2040 capacity-expansion or policy model.
> See [release notes](docs/releases/v1.0.0.md) for the scope and limitations.

Kerala 2040 is an independent, reproducible energy-systems research project
asking how Kerala can reduce structural electricity-import dependence and
hydrological vulnerability while remaining strongly interconnected with India,
protecting ecological carrying capacity, staying within realistic fiscal
constraints, and creating value through storage, circular industry and
intelligent grids.

## Public dashboard

Dashboard source lives in `docs/` and deploys through GitHub Pages.

**https://kerala2040.github.io/**

See [next steps and the release workflow](docs/NEXT_STEPS.md).
For the P0 missing interval evidence, see the [private measured FY2024-25
interval intake and fail-closed validator](docs/MEASURED_INTERVAL_INTAKE.md).
The validator does **not** mean measured telemetry has been obtained.
The website release is built from an immutable research commit recorded in its
`SOURCE_COMMIT`. Its public `RELEASE_MANIFEST.json` identifies the research
commit and evidence snapshot; the website is not the source of truth for development-only data.

## v1.0 connected data layer

The first operational release connects:

- **Kerala SLDC** public system statistics, including historical dates through
  the site's date form;
- **NASA POWER Hourly API** with explicit UTC/India timestamps and missing-value
  handling;
- **data.gov.in OGD API** through a generic credentialed/paginated client;
- **NITI ICED** as a discovery/download layer without pretending an undocumented
  API exists.

See [`docs/data_connectivity_v1.md`](docs/data_connectivity_v1.md).

## Current modelling foundation

The repository now distinguishes an **observed daily replay** from provisional
chronological proxies. The FY2024-25 PyPSA replay uses Kerala SLDC observed daily
energy and Kerala State Planning Board/KSEBL installed-capacity references; it
does not consume the reconstructed 8,760-hour load proxy. Weather-derived solar
and wind availability are explicitly labelled proxy resource profiles, not
measured Kerala generation.

Hydro diagnostics, official-accounting reconciliation, the generator inventory,
2040 scenario dimensions, techno-economic source registry and GIS acquisition
manifest are reproducible workflows. Numerical 2040 optimisation remains blocked
until unresolved inputs are sourced.

See [`docs/PROVENANCE_CORE_RULES.md`](docs/PROVENANCE_CORE_RULES.md).

```bash
python -m venv .venv
# Linux/macOS
source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1

pip install -e ".[dev]"

# Live connectivity
python scripts/source_healthcheck.py --strict-core

# One known SLDC date
python scripts/ingest_sldc_daily.py --start 2026-09-16 --end 2026-09-16

# One day of historical weather at Kochi
python scripts/ingest_weather.py \
  --start 2025-04-01 --end 2025-04-01 \
  --lat 9.9312 --lon 76.2673 --name kochi
```

## CET 2026 MVP

The CET release path still targets:

- a calibrated historical Kerala electricity balance and 8,760-hour baseline;
- 2040 demand scenarios and uncertainty bounds;
- PyPSA + HiGHS capacity/dispatch scenarios;
- hydro/climate and import stress tests;
- storage and grid-flexibility analysis;
- initial GIS ecological constraints;
- explicit public-finance/federal/private financing splits;
- one circular-industry case study;
- reproducible poster figures.

## Scientific rules

1. No capacity without a resource constraint.
2. No resource without an ecological constraint.
3. No project without a grid constraint.
4. No grid solution without a reliability test.
5. No infrastructure pathway without a financing source.
6. No waste-to-value claim without a mass balance.
7. No 2040 conclusion without uncertainty analysis.
8. Interconnection is an asset; the project studies sovereignty and resilience, not autarky.
9. Observed data, sourced assumptions and scenario choices remain distinguishable.
10. No 2040 conclusion before the historical calibration gate passes.
11. Every model-facing dataset states its classification and source; proxy,
    synthetic, derived and scenario-assumption data are never presented as observations.

## Repository layout

```text
configs/        model, source and scenario configuration
data/           local/raw/processed data guidance (raw data mostly gitignored)
references/     source catalogue and provenance metadata
src/            reusable Python package
scripts/        command-line research workflows
tests/          deterministic parser/model tests
notebooks/      exploratory analysis only; production logic belongs in src/
results/        generated scenario outputs
figures/        generated publication/poster figures
reports/        CET poster and longer reports
docs/           methodology, source connectivity, decisions and assumptions
```

## Core stack

Python · pandas · xarray · DuckDB · PyArrow/Parquet · PyPSA · HiGHS ·
pandapower · GeoPandas · Rasterio · QGIS · scikit-learn · LightGBM/XGBoost ·
Optuna · SHAP.

Post-CET modules may add SWAT+, InVEST, Marxan, Brightway, LEAP, IDA ICE,
OpenDSS, SAM and WEC-Sim where their specific questions justify them.

## Solar and wind original source batch (September 2026)

The [source ledger](docs/SOLAR_WIND_SOURCE_BATCH_2026_09_21.md)
records original GSA GIS ZIPs, NWDP telemetry, PV studies and the separate
NIWE wind atlas. Exact original file sizes, SHA256s and publisher references
are in the [solar manifest](data/evidence/solar/solar_batch_2026_09_21_originals_manifest.json)
and [NIWE source QA](data/evidence/gis/niwe_150m_user_supplied_source_qa_2026_09_21.json).

**Private originals, public science:** the user chose a SEPARATE PRIVATE
`kerala2040-source-archive` repository for third-party binary ZIPs/PDFs.
The private repository is **created, initialized and verified private**; the
original binary files have **not yet been uploaded or restored remotely**. Upload and restore are privacy-checked and
SHA256-gated: [solar uploader](scripts/publish_solar_source_release.py),
[restore tool](scripts/restore_solar_source_release.py),
and [NIWE original uploader/restorer](scripts/publish_niwe_original_release.py).
See [one-time user setup](docs/RENEWABLE_FIVE_STEP_HANDOFF_2026_09_22.md).
If only the five extracted Downloads folders remain, use the
[private five-folder snapshot workflow](scripts/archive_renewable_folders_private.py):
it verifies every nested file, splits large ZIP64 snapshots into upload parts
and performs an independent SHA256 restore. Such snapshots are **not**
byte-identical to the earlier original provider ZIPs.
The public repository will retain source citations and hashes, not raw
third-party data; private access does not supersede publisher use conditions.

## September 2026 solar and wind progress

The [five-step renewable workstream handoff](docs/RENEWABLE_FIVE_STEP_HANDOFF_2026_09_22.md)
distinguishes exact Kerala-only descriptive clips, 43,800 site-hour
**UNVALIDATED** weather-to-generation sensitivity proxies, blocked
technology-specific buildable MW, model admission gates, and source binary
storage requiring an authenticated rights-reviewed upload. The original
datasets and derived ZIP/GeoTIFF/PNG bytes are **not yet hosted as verified
permanent PRIVATE GitHub Release assets**; manifests and processing code are committed.
No numerical Kerala buildable renewable MW or validated 2040 renewable
generation result is claimed.

## Reproducibility and data policy

Every model/data run should record git commit, config, source IDs and retrieval
dates, raw-response hashes where appropriate, solver/package versions, explicit
assumptions and output checks.

Do not commit confidential utility data, personal data, security-sensitive
network information, credentials, or third-party datasets whose licences forbid
redistribution. Commit acquisition code, metadata, schemas and derived results
instead.

## Immediate hard gate

Build an authoritative historical Kerala electricity dataset and reproduce
official demand/consumption, internal generation, imports and peak behaviour
before interpreting any 2040 optimisation.
