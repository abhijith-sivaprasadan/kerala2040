# Kerala2040 — power-system stress, chronology and grid deliverability

**Independent, ongoing research** into why Kerala's electricity system may face peak-hour stress even when annual energy appears sufficient. Built in public with source-audited data, open-source modelling and explicit limits on what the results can establish.

[Research website](https://kerala2040.github.io/) · [Current findings](https://kerala2040.github.io/findings.html) · [Methods](https://kerala2040.github.io/methodology.html) · [Validation & limits](https://kerala2040.github.io/qa.html) · [Sources](https://kerala2040.github.io/sources.html) · [Start reproducing](docs/REPRODUCE_AND_EXTEND.md)

**Research question.** How do demand timing, hydropower flexibility, external supply and internal transmission interact to create vulnerabilities at stressful hours? Which responses merit further testing as demand grows toward 2040?

This is a **diagnostic and screening** study. It is not a reconstruction of a particular outage, an operationally calibrated electricity-system model, or a validated investment plan. It is not submitted or peer-reviewed research. The project does not claim current independent access to continuous Kerala hourly demand, dispatch or flow telemetry.

## Evidence-backed findings and limits

| Study component | Current evidence | What this does **not** prove |
| --- | --- | --- |
| Historical electricity | Published broad electricity use: 22.54 TWh in FY2020–21 and 29.31 TWh in FY2024–25; 354 of 365 FY2024–25 daily SLDC records remain observed, 11 missing days remain marked model-only. | A measured hourly chronology or an interchangeable “import share” across incompatible accounting boundaries. |
| Weather and demand | Seven rolling monthly tests on **353 observed daily SLDC demand targets** matched to complete same-day ERA5 reanalysis: XGBoost weather features improved 6/7 holdouts, LightGBM 5/7; pooled XGBoost RMSE decreased ~37.1% against its separately tuned calendar-only baseline. | Day-ahead operational forecast skill, a causal temperature effect or multi-year robustness. The ML target is **observed daily consumption**, not reconstructed hourly data. |
| Hourly adequacy | 8,760-hour **reconstructed** FY2024–25 demand chronology conserves each observed daily electricity total. Test scenarios vary transfer limits and hydro scheduling. | Measured 15-minute/hourly load, individual outages or probabilistic reliability. |
| Intraday hydro timing | In the FY2030–31 reference-demand screening case with **4,455 MW** assumed transfer capability, modelled unserved energy changes **375.03 → 11.75 GWh** when the same daily hydro MWh can move freely within each day (96.87% reduction). | Feasible reservoir operations, station-level generation schedules, causal attribution, or an independently validated 2040 scenario. The flexible case is an optimistic bound. |
| Internal network | Public 110-kV+ network screen identifies **21 source-backed lines** exceeding screening ratings across **eight tested import-allocation cases** (12 corridor groups), with separately dated CEA planning evidence for the Shoranur geography. | AC/N-1 security, present-day exact transformer overload magnitude or operator-endorsed upgrade needs. |
| Numerical consistency | 36 benchmark PyPSA ↔ independent SciPy/HiGHS formulation checks and 12 controlled PyPSA ↔ OSeMOSYS capacity-planning comparisons. | Physical calibration; matching mathematical formulations can share the same modelling assumptions. |

**Source trails:** [research synthesis](docs/POWER_SYSTEM_STRESS_SYNTHESIS_2026_09_28.md), [observed-daily ML robustness](docs/DAILY_DEMAND_ML_ROBUSTNESS_V0_2.md), [hydro flexibility programme](docs/FULL_PYPSA_SCENARIO_PROGRAMME.md), [network bottleneck screening](docs/KSEB_NETWORK_ROBUST_BOTTLENECKS_V1_0.md), [source register](docs/evidence_register.md).

The website is a presentation layer, not an independent source of scientific truth. Please trace consequential numbers to the linked evidence files, dates, assumptions and tests.

## Reproduce one real-data check in minutes

The smallest reproducibility example audits the actual repository-committed **daily SLDC balance and reconstructed hourly load** using only Python 3.11's standard library. It checks observed daily energy conservation without installing the modelling stack:

```bash
git clone https://github.com/abhijith-sivaprasadan/kerala2040.git
cd kerala2040
python examples/reproduce_daily_accounting.py --output results/examples/accounting_audit.json
```

You should obtain **354 observed / 11 missing days**, exactly **8,760 reconstructed hourly values**, and no observed-day energy-conservation residual above 0.0001 MU. Missing records must remain explicitly missing, not zero. The script fails if these contracts do not hold. See [the worked example and its limitations](docs/REPRODUCE_AND_EXTEND.md).

## Reproduce the modelling code

Reference Python: **3.11**. For full scientific modules, source tests, and all optional model dependencies:

```bash
python -m venv .venv
# Linux/macOS: source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
python -m pytest -q
```

Some optional workflows require \`.[ml]\`, \`.[geo]\`, \`.[era5]\` and separately licensed or very large weather/GIS inputs. **A passing unit test does not mean every external data acquisition or fitting step is fully reproducible from a fresh clone.** In particular, the original ERA5-sensitive hourly-load coefficient fit still needs its source archive and fitting script, although the released proxy, hashes and downstream tests are inspectable. See [provenance](docs/PROVENANCE_CORE_RULES.md), [readiness gates](docs/AUDIT_RELEASE_GATES.md) and [reproduction routes](docs/REPRODUCE_AND_EXTEND.md).

## Reuse, review and contribution

We particularly welcome reproducibility checks, dated official data and corrected units/metadata, tests that challenge physical assumptions, and evidence for or against key conclusions. Start with [CONTRIBUTING.md](CONTRIBUTING.md); do not commit confidential or license-restricted sources. The project is **not affiliated with or endorsed by KTH, KSEBL, SLDC or an electricity system operator**.

**Highest-priority evidence gap:** continuous measured Kerala 15-minute/hourly demand and associated dispatch and exchange data. More sophisticated models cannot substitute for missing validation observations.

**Research materials:** [current research plan](docs/research_plan.md) · [full evidence register](docs/evidence_register.md) · [research synthesis](docs/POWER_SYSTEM_STRESS_SYNTHESIS_2026_09_28.md) · [historical modelling programme and limits](docs/FULL_PYPSA_SCENARIO_PROGRAMME.md).

© 2026 Abhijith Sivaprasadan. Original code is licensed under [LICENSE](LICENSE); upstream data retain their own terms.
