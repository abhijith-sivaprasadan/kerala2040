# Reproduce and extend — reader's entry point

## Reproducible example A: observed daily energy vs reconstructed hours

**Inputs (committed, with provenance):**
- `data/external/sldc_fy2024_25/daily_balance.csv` — source-reported daily records (354 observed, 11 missing), generated from the SLDC archive.
- `data/external/sldc_fy2024_25/qa_report.json` — source SHA-256, missing-date mask, 354-day accounting totals.
- `public/hourly-load-proxy.json` — 8,760 **modelled** hourly values, not observed hourly telemetry.

**Run (Python 3.11, no third-party dependencies):**

```bash
python examples/reproduce_daily_accounting.py \
  --output results/examples/accounting_audit.json
```

On Windows PowerShell, use the command on one line. The output is a source-hashed JSON audit; it contains no hidden raw input. Expected invariant values from the published source register: 365 daily rows, 354 observed, 11 missing, 8,760 hourly proxy points, 30666.2569 MU of observed-day consumption. The code re-checks, rather than assuming, those counts and the per-day MWh equality.

The source hour records are **not measurement data**. A valid daily-energy sum does not prove that the reconstructed intraday shape happened in the grid.

## Reproducible example B: uncertainty in within-day demand chronology

The experimental `examples/hydro_chronology_sensitivity.py` is a *new bounded historical sensitivity*, **not** a replay of the published FY2030–31 375.03 → 11.75 GWh result. It uses a predeclared seven-consecutive-day window selected by the greatest **source-observed** daily consumption with no missing dates. It compares the original hourly proxy with within-day temporal shifts and ±10% intraday-deviation scaling, preserving every daily MWh exactly. For each case it compares fixed daily-average hydro against a mathematically optimistic per-day flexible hydro allocation under the same hydro energy, hydro capacity and two hypothetical import ceilings.

```bash
python -m pip install -e .
python examples/hydro_chronology_sensitivity.py \
  --output results/examples/hydro_chronology_sensitivity.json
```

**Interpretation:** all derived outputs depend on a reconstructed historical hourly load; import capacity is a stated sensitivity, and the ideal daily hydro allocation omits reservoir, ramping and cascade constraints. The five shapes are controlled perturbations, **not calibrated uncertainty quantiles**. Their spread cannot establish statistical confidence or validate the original 2030–31 result. No new figure is promoted to the main website until its executed result, source hashes and limits are inspected.

## Reproducible example C: hydro timing with explicit supply chronology

`python examples/hydro_supply_timing_v0_2.py --output results/examples/hydro_supply_timing_v0_2.json` generates 40 tightly controlled historical-screening scenarios and publishes the evidence input SHA-256 checksums alongside all solver residuals. In contrast to the 24-hour v0.1 model, it allows an *illustrative* 18:00–22:00 import derate and an *illustrative* 400 MW/h aggregate hydro ramp across midnight. Neither parameter is an observed historical dispatch condition.

See [the research note, results and negative controls](HYDRO_SUPPLY_TIMING_V0_2.md). These scenarios **do not constitute validation of the separate FY2030–31 headline result**.

## Full repository

Install `python -m pip install -e ".[dev]"`, then run `python -m pytest -q`. Some tests use PyPSA/HiGHS; the repository hosts many distinct scenarios and substantial external data workflows. For detailed code and evidence paths consult [README](../README.md), [source register](evidence_register.md), [provenance rules](PROVENANCE_CORE_RULES.md), [original hydro programme](FULL_PYPSA_SCENARIO_PROGRAMME.md).

## Contribute

A pull request that reproduces a finding or falsifies an assumption is more useful than a second website. See [CONTRIBUTING](../CONTRIBUTING.md). Reuse datasets only within source terms; do not rehost raw restricted rasters or archived SLDC HTML pages.
