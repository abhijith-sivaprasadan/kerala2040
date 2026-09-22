<div align="center">

![Kerala2040 — our land, our energy future](docs/assets/social-card.svg)

# Kerala2040

**കേരളത്തിന്റെ ഊർജഭാവി · Our land. Our energy future.**

*An open, evidence-first research project on Kerala’s electricity system, energy resilience and possible pathways to 2040.*

[Explore the website](https://kerala2040.github.io/) · [Methodology](docs/methodology.md) · [Evidence](docs/evidence_register.md) · [Next steps](docs/NEXT_STEPS.md)

</div>

---

## The question

**What would it take for Kerala to meet its future energy needs more reliably, affordably and sustainably—while remaining connected to India's grid, protecting land and water, and making investment financially credible?**

Kerala2040 investigates electricity demand, in-state generation, interstate imports, hydro and monsoon exposure, solar, wind, storage, grid flexibility, ecological constraints and financing. It starts with a defensible historical system account before comparing possible 2030–2040 pathways. Energy sovereignty here means *less forced dependence and more resilience*, **not** electricity autarky.

This is independent research by [Abhijith Sivaprasadan](https://github.com/abhijith-sivaprasadan). It is **not an official Government of Kerala, KSEBL or SLDC forecast, policy recommendation or approved development plan**.

## Explore the project

| Start here | What it answers |
|---|---|
| **[Public research experience](https://kerala2040.github.io/)** | A Kerala-rooted guide through the energy question, observed evidence, maps, scenarios and open questions. |
| **[Research methodology](docs/methodology.md)** | How sources become constraints, calibrated models and explicit scenario comparisons. |
| **[Evidence and provenance](docs/PROVENANCE_CORE_RULES.md)** | What counts as observed, reported, reanalysis, derived, proxy or external-study evidence. |
| **[Research plan](docs/research_plan.md)** | Work packages spanning demand, hydro, renewables, grid, ecology, circular industry and finance. |
| **[Readiness and missing inputs](docs/AUDIT_RELEASE_GATES.md)** | Why source acquisition or a solver run alone does not make a 2040 result defensible. |
| **[Release notes](docs/releases/v1.0.1.md)** | The historical-data publication and its precise limitations. |

The [website](https://kerala2040.github.io/) is a *published, pinned evidence snapshot*. The `main` branch is ongoing research and may contain newer analysis than the deployed website; the site's `SOURCE_COMMIT` and `RELEASE_MANIFEST.json` identify its exact source version. Do not mistake development-only results for published findings.

## Latest verified milestone · 22 September 2026

**The NIWE 150 m Kerala wind-resource × GLO-90 surface-terrain analysis has been executed on real, hash-verified inputs.** From 19,475,568 national atlas rows, the original NWIC Kerala polygon selects **200,692** onshore resource point centres; the modelled wind-speed median is **3.91 m/s at 150 m**. Sampling the independently derived 90 m GLO-90 DSM slope yields **199,853** finite slope results and **839** missing samples. The median sampled DSM slope is **4.96°**.

A 16-combination wind-speed × surface-slope matrix and point-count histogram are now documented in the [executed result](docs/NIWE_150M_KERALA_TERRAIN_REAL_DATA_RESULT_2026_09_22.md) and [machine-readable audit](data/evidence/gis/niwe_150m_kerala_real_wind_DSM_slope_2026_09_22.json), with a [reproducible original-source clip rebuild](scripts/rebuild_kerala_niwe_clip_from_originals.py). **These are modelled resource-point statistics—not legally eligible land, wind-farm layouts, actual generation, km² or MW.** Private source rows and NIWE-derived maps are not republished in this public repo.

**LRIS 2.0 reconnaissance** identified an all-district layer catalogue; browser-served district/block/local-body GeoJSON; Level 1/2 land-use, roads and slope *summary* JSON; and GeoServer WMS map images. The tested standard WFS endpoint returned **“Service WFS is disabled.”** This does not disprove other authorised GIS access; no underlying land-use polygons or notification-linked forest/paddy/ESZ exclusions have been acquired from LRIS. See [the source-scoped LRIS inventory](data/evidence/gis/lris_public_services_discovery_2026_09_22.json).

## What has actually been established?

*Research status: 22 September 2026. Source coverage and scientific model readiness are separate things.*

| Area | Current evidence | Not yet established |
|---|---|---|
| **Electricity baseline** | 354 observed SLDC daily dates in FY2024–25; observed-day source-attribution PyPSA replay. [Daily model](docs/OBSERVED_DAILY_PYPSA.md). | The 11 missing dates; measured continuous statewide hourly / 15-minute load and interchange; calibrated hourly dispatch. |
| **Weather** | ERA5 source/chronology QA for five representative locations × 8,760 UTC hours = 43,800 point-hours. [Source QA](data/evidence/weather/era5_fy2024_25_source_qa_2026_09_21.json). | Validated statewide weather-to-generation modelling. |
| **Solar** | Exact-boundary native-grid Kerala resource clips: 46,241 GSA PVOUT cell centres and 513,823 GHI cell centres. [Clip QA](data/evidence/solar/kerala_native_resource_clips_2026_09_22.json). | Measured FY2024–25 PV validation and rooftop/ground/floating buildable MW. |
| **Wind** | Completed real NIWE 150 m × GLO-90 DSM slope join: **200,692** Kerala resource centres, **199,853** valid slope samples, median modelled speed **3.91 m/s**. [Executed result](docs/NIWE_150M_KERALA_TERRAIN_REAL_DATA_RESULT_2026_09_22.md). | Legally eligible sites, turbine layout, actual hourly yield, buildable MW, grid evacuation and offshore resource assessment. |
| **Hydro, grid and land** | Source inventories, terrain/hazard QA and LRIS public-service discovery, including the tested disabled WFS route. [LRIS evidence](data/evidence/gis/lris_public_services_discovery_2026_09_22.json). | Verified reservoir cascades/operations, connection-point hosting capacity and notification-linked, technology-specific statutory GIS screens. |
| **2040 scenarios** | Source-labelled benchmark pathways and explicitly proxy-labelled PyPSA sensitivities. [Limitations](docs/PYPSA_2040_PROXY_SCREENING.md). | Calibrated least-cost, reliable or permitted 2040 build-out. |

**Available data are not automatically approved model inputs.** In the downloaded NWDP FY2024–25 solar series, **6,007 of 6,007 values were zero, including daytime**: it cannot validate PV output. Five-point ERA5-to-PV/wind hourly results are illustrative *proxies*, not measured generation or Kerala-wide predictions. No defensible buildable solar/wind MW is currently claimed. See the [renewables handoff](docs/RENEWABLE_FIVE_STEP_HANDOFF_2026_09_22.md) and [capacity gates](data/evidence/solar/solar_wind_feasible_capacity_gates_2026_09_22.json).

## How the research is designed

```text
Source files + source permissions + provenance
                    │
                    ▼
       Acquisition → byte/units/time QA
                    │
                    ▼
       Historical electricity reconciliation
                    │
         ┌──────────┴──────────┐
         ▼                     ▼
   Weather & resource     Hydro & land/grid
   conversion checks      spatial constraints
         └──────────┬──────────┘
                    ▼
          Calibrated system model
                    │
                    ▼
   2040 scenario, reliability & cost tests
                    │
                    ▼
     Ecological + fiscal trade-off reporting
```

The direction of travel is *evidence → validation → constraints → model → uncertainty*. Missing source fields stay missing; they are not silently replaced by convenient numbers. See the [provenance contract](docs/PROVENANCE_CORE_RULES.md) and [methodology](docs/methodology.md).

## Solar and wind: a dedicated research track

The September 2026 acquisition includes Global Solar Atlas India rasters, the NIWE wind atlas, solar studies and selected NWDP telemetry. The official NWIC Kerala state geometry is used for **descriptive native-grid, pixel-/point-centre clips**; clipping does not establish legal site eligibility. Five representative-point FY2024–25 ERA5 profiles are a **sensitivity exercise**, not validated generation.

Five downloaded source-folder trees have been uploaded to and independently SHA-256-restored from a **separate private archive**. A subsequent **26-layer India GSA PVOUT native-grid consistency audit passed across 8,796,068 valid-positive cells per comparison**; it verifies internal annual/monthly-versus-daily representation, **not** FY2024–25 PV generation or buildable capacity. The PDF inventory rendered all 2,945 pages, but page-by-page visual interpretation remains pending. Public records retain provenance and asset hashes, **not the third-party raw data**:

- [What is archived and what was verified](data/evidence/solar/renewable_five_folder_private_archive_2026_09_22.json)
- [Solar and wind source interpretation](docs/SOLAR_WIND_CONSOLIDATED_ANALYSIS_2026_09_22.md)
- [Kerala-native resource clipping](docs/KERALA_NATIVE_RENEWABLE_RESOURCE_CLIPS_2026_09_22.md)
- [Executed NIWE wind × DSM slope analysis](docs/NIWE_150M_KERALA_TERRAIN_REAL_DATA_RESULT_2026_09_22.md)
- [NIWE × slope public-safe aggregate results](data/evidence/gis/niwe_150m_kerala_real_wind_DSM_slope_2026_09_22.json)
- [LRIS 2.0 public-service discovery and disabled WFS record](data/evidence/gis/lris_public_services_discovery_2026_09_22.json)
- [Resource-to-capacity constraints](data/evidence/solar/solar_wind_feasible_capacity_gates_2026_09_22.json)
- [Reproducible five-folder archival workflow](scripts/archive_renewable_folders_private.py)
- [GeoTIFF pixel checks and every-page PDF visual review](docs/SOLAR_WIND_TIFF_PDF_REVIEW_2026_09_22.md)
- [Kerala SAC/NWDP wetlands × source GSA, NISE and NIWE crosswalk](docs/KERALA_WATERBODIES_SAC_NWDP_GSA_NISE_NIWE_2026_09_22.md)

Folder snapshots preserve nested *file bytes and hierarchy*. They do **not** prove that all 17 separately inventoried historic publisher-original ZIP/PDF byte streams were independently archived. The separate [exact-original manifest](data/evidence/solar/solar_batch_2026_09_21_originals_manifest.json) retains that distinction. Storage integrity does not grant redistribution rights or model admission.

## Run the research code

**Supported Python: 3.11–3.12.** These commands run from the public repository root; do not publish third-party source binaries or API tokens.

```powershell
git clone https://github.com/abhijith-sivaprasadan/kerala2040.git
cd kerala2040

py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"

python scripts/check_readiness.py
python scripts/build_site.py --check
python -m pytest
```

For GIS work, install the optional geospatial dependencies:

```powershell
python -m pip install -e ".[dev,geo]"
```

Build and preview the website:

```powershell
python scripts/build_site.py --output _site
python -m http.server 5173 --directory _site --bind 127.0.0.1
```

Open **http://127.0.0.1:5173/**, not `docs/index.html` as a file URL. For ingestion examples, see [next steps](docs/NEXT_STEPS.md) and [data connectivity](docs/data_connectivity_v1.md). Acquisition workflows may need network access, source permissions or local originals.

### Repository guide

| Location | Purpose |
|---|---|
| [`docs/`](docs/) | Public site source, methods, audits, figures and research handoffs |
| [`data/evidence/`](data/evidence/) | Versioned, source-qualified QA and evidence summaries |
| [`scripts/`](scripts/) | Acquisition, reconciliation, GIS, model and archive workflows |
| [`src/kerala2040/`](src/kerala2040/) | Reusable implementation |
| [`configs/`](configs/) | Source definitions, assumptions and release gates |
| [`tests/`](tests/) | Parser, integrity, scientific-contract and site checks |
| [`results/`](results/) | Locally generated model runs and figures; not automatically released |

## Contribute, cite, and reuse

Useful contributions include primary-source provenance, reproducible corrections, tests, Kerala-specific input data **with verified access terms**, and scrutiny of assumptions or units. Read [CONTRIBUTING.md](CONTRIBUTING.md) and [the decision log](docs/decision_log.md). Do not commit personal information, restricted network data or raw third-party files to the public repository.

Code is licensed under [MIT](LICENSE); **that licence does not relicense third-party datasets, imagery, reports or other attributed source material**. Cite the specific tagged research release using [CITATION.cff](CITATION.cff) and, where applicable, the upstream data publishers.

---

*Kerala2040 is built to make assumptions and unknowns inspectable—not to replace them with a single confident 2040 number.*
