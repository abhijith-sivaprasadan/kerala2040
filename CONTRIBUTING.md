# Contributing to Kerala2040

The current public results are limited to source-backed historical descriptions, reproducible source-accounting checks and the retrospective observed-daily demand experiment. Read [the freeze and evidence classification](docs/RESEARCH_FREEZE_2026-10-23.md) before proposing changes to the public findings.

Contributions with the highest research value are original Kerala interval-demand or dispatch source records, corrections to numerical source extraction, source-definition reconciliation, independent reproductions of the daily demand experiment and independently checked data-quality tests.

For each proposed change include the primary source and publication date, source URL and permitted use, units, system boundary, temporal coverage, missingness, repeatable commands and at least one regression test. In particular, preserve the distinction between the KSEBL annual consumer-side series and the SLDC operational daily series.

The historical simulation modules remain inspectable, but additional hypothetical hydro/import/storage scenarios should **not** be proposed as evidence upgrades without independent primary observations.

Run `python -m pytest -q` and `ruff check src tests scripts` for relevant changes. [Data intake procedure](docs/MEASURED_INTERVAL_INTAKE.md) · [Open observational-data issue](https://github.com/abhijith-sivaprasadan/kerala2040/issues/130).
