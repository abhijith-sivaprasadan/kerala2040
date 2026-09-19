# Chronological PyPSA: what can be solved now

This is a **developer/research screening experiment**, not a published calibrated hourly model or
an independently optimised 2040 pathway. The released v1.0.1 website continues to show
observed/derived daily evidence; this experimental hourly solver's plots and CSVs stay under
`results/models/hourly_proxy_screening/` and are **not** published on GitHub Pages.

## Two deliberately different models

1. `scripts/build_historical_model.py` reproduces observed 354-day energy accounting
   in a fixed-profile, 24-hour-weighted PyPSA network, with no filled days.
2. `scripts/run_hourly_screening.py` solves an LP on a *reconstructed*, 8,760-hour
   FY2024–25 demand chronology, with station-group hydro and nonhydro held at
   observed **daily-average MW**. The 11 missing SLDC days have explicit, **model-only**
   interpolated demand and generation; raw observations and published daily totals
   are never changed. Hourly import and storage dispatch are **model outcomes**.

PyPSA dispatch is genuine HiGHS optimisation; no measured hourly fit is claimed.

### Run (in repo root with `pip install -e '.[dev]'`)

```bash
# Observed-day historical replay (existing pipeline requires SLDC parquet):
python scripts/build_historical_model.py

# 48-hour solver smoke test using committed input data:
python scripts/run_hourly_screening.py --acknowledge-proxy

# Whole FY proxy screening — can take appreciably longer:
python scripts/run_hourly_screening.py --acknowledge-proxy --hours 8760

# Fixed additional PV/BESS sensitivity with EXPLICIT scenario settings:
# edit configs/pypsa_screening_example.yaml: additional_solar_mw, battery_power_mw
python scripts/run_hourly_screening.py --acknowledge-proxy --hours 168
```

The source for optional solar availability is the existing 5-point, equal-weight NASA POWER
`data/processed/renewable_availability_proxy.parquet`. If running from an isolated checkout,
produce that file through `scripts/build_renewable_profiles.py` and its weather inputs.
Solar is **additional** capacity only; do not add existing solar capacity again because
historical nonhydro internal generation already includes published internal generation.

Config `import_limit_mw: 6500` is a **deliberate experimental bound**, **not** Kerala's
actual interstate transfer capability. `objective_import_per_mwh: 1` and
`objective_unserved_per_mwh: 10000` are **abstract screening weights**, never
INR/MWh or project costs. Solar and battery capacities are manually specified sensitivities;
**the unresolved technology-cost grid does not permit capacity-expansion optimisation**.
For batteries, duration and round-trip efficiency are also explicit sensitivity parameters.

## Physical gates before a planning-grade model

- Real state 15-minute or hourly demand and interchange chronology, metering definitions.
- Reservoir-to-powerhouse topology, water balances, cascades, environmental releases,
  effective head, turbine limits and seasonally effective generation capacity.
- Authoritative interconnection transfer limits and independently sourced price series.
- Reconciled commissioned assets, representative resource siting/technology ceilings,
  price year, annualised capital costs, financing and O&M assumptions.

A fixed daily-average generator is **not** actual observed hourly hydro. Reservoir
`generation_capability_gross_mu` and `generation_capability_station_mu` from the new
SLDC archive are retained as observed *context*, but never double-counted or imposed
as a fictitious storage energy bound without an independently checked cascade map.

## Saved outputs

`summary.json` documents all assumptions, model-only imputed dates, observed-day totals,
solver status, 8760/partial-window status and derived outcome KPIs.
`dispatch_screening.csv` carries source classifications and missing-day flags on every row.
`figures/screening_dispatch.png` and `figures/screening_energy.png` are explicitly
labelled model screening figures, **not** publishable validated CET 2040 results.
`--export-network` optionally creates a PyPSA NetCDF network. A baseline with no new
capacity checks that modelled imports conserve **the original reported daily imports**
where observations exist; this checks accounting, not hourly accuracy.

## CET-ready observed-data figures

```bash
python scripts/build_sldc_observed_figures.py
```

This creates four *observed-daily*, non-optimisation figures from the new v1.0.1
station, import and reservoir CSVs. These may be reviewed for CET with the
recorded missing-date qualification. The reproducible manifest records the
source-archive SHA-256. Unlike hourly screening PNGs, these charts are derived
from official daily reports rather than a reconstructed hourly chronology.

GitHub Actions workflow `pypsa-chronological-screening.yml` tests HiGHS on a
short window and uploads the figures, summary and dispatch CSV as an artifact;
the annual proxy run is opt-in through the workflow's `hours=8760` input.
