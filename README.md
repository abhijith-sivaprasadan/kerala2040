# Kerala2040

**Public research record · evidence freeze: 23 October 2026**

An independent analysis of publicly available statistics on Kerala's electricity consumption, generation capacity, system-operation records and weather-related daily-demand variation. Source definitions, coverage and computational methods are documented so that results can be checked.

**Website:** https://kerala2040.github.io/  
**Scope and freeze:** [RESEARCH_FREEZE_2026-10-23.md](docs/RESEARCH_FREEZE_2026-10-23.md)  
**Source register:** [evidence_register.md](docs/evidence_register.md)  
**Reproduce source accounting:** [reproduce_daily_accounting.py](examples/reproduce_daily_accounting.py)

## Core research record

| Result | Source / method | Interpretation |
| --- | --- | --- |
| Annual reported electricity consumption increased from **22,540.32 MU** (FY2020–21) to **29,311.76 MU** (FY2024–25), approximately **30.0%** | Kerala State Planning Board, *Economic Review 2025* (KSEBL-attributed consumer-side series) | Official historical trend within one defined annual statistical series |
| Reported geographically installed generation capacity at 31 March 2025 was **4,412.14 MW** | Kerala State Planning Board, *Economic Review 2025*; [source reconciliation](data/evidence/generation/fy2024_25_generator_capacity_census.json) | Nameplate capacity, not hourly available generation; the published category sum differs by 0.01 MW through rounding |
| **354/365** FY2024–25 daily SLDC source reports available; **11** unavailable | [Daily SLDC QA](data/external/sldc_fy2024_25/qa_report.json) | Historical data completeness and source-accounting consistency, not hourly telemetry |
| **353** observed SLDC daily consumption targets matched with complete IST-day ERA5 reanalysis | [Rolling monthly study](docs/DAILY_DEMAND_ML_ROBUSTNESS_V0_2.md) | Retrospective same-day weather/demand association: 6/7 XGBoost and 5/7 LightGBM monthly comparisons favour added weather data; single-year evidence only |

**Boundary:** Official annual consumer-side electricity consumption and the SLDC daily operational consumption field have different definitions. The 354 source-observed SLDC days sum to 30,666.2569 MU under the latter boundary; this is not an alternative value for the annual 29,311.76 MU consumer-side series. See the [freeze record](docs/RESEARCH_FREEZE_2026-10-23.md).

## Evidence and open questions

The current package does not include continuous independently measured Kerala hourly/15-minute load, generation dispatch or exchange telemetry. Hourly electricity demand reconstructions, hydro redispatch, network loading, 2030/2040 scenarios and proposed interventions therefore remain **exploratory modelling**, not operational findings or investment conclusions.

They are retained in the repository, with their assumptions and source trails, under [Exploratory workstreams](docs/EXPLORATORY_WORKSTREAMS.md). No simulated shortage quantities appear in the public research findings.

### Reproduce the daily record audit

Python 3.11 standard library:

```bash
git clone https://github.com/abhijith-sivaprasadan/kerala2040.git
cd kerala2040
python examples/reproduce_daily_accounting.py --output results/examples/accounting_audit.json
```

This audits source-day completeness and preserves observed daily MWh in the **reconstructed**, not measured, hourly series. It is an arithmetic consistency test. For the broader codebase: `python -m pip install -e ".[dev]"` and `python -m pytest -q`.

Details: [Reproduction guidance](docs/REPRODUCE_AND_EXTEND.md) · [Source evidence](docs/evidence_register.md) · [Scientific provenance rules](docs/PROVENANCE_CORE_RULES.md) · [Contributions](CONTRIBUTING.md).

**Research and authorship:** Abhijith Sivaprasadan, independent project. KTH and the named public agencies are not publishers or endorsers of the project. Source data retain the rights of their respective publishers.
