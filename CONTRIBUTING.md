# Contributing to Kerala2040

Kerala2040 is an independent public-data research project, not an operator-grade grid model. Useful contributions are those that improve the evidence, test a hypothesis, or make an existing result easier for someone else to reproduce.

## Good first contributions

1. **Reproduce a check.** Run \`python examples/reproduce_daily_accounting.py\` and confirm its source metadata, preserved observed-day MWh and missing-day status. Report your environment, commit SHA and any discrepancy.
2. **Audit source definitions.** Review the dated SLDC, CEA, KSEBL and other primary source boundaries in [docs/evidence_register.md](docs/evidence_register.md); open an issue for incompatible units, temporal boundaries or outdated technical context.
3. **Challenge an assumption.** Submit a controlled negative test or a physically justified alternative to an hourly demand reconstruction, import ceiling or hydro power limit. Clearly differentiate published observations from new sensitivity assumptions.
4. **Improve documentation.** Provide a step-by-step route to reproduce an existing released result on another machine. A small independent reference implementation is particularly valuable.

## Pull requests

Explain the research question and numerical change; cite primary data and publication date; document units and software versions; provide a small test; and show which source-validated quantities remain unchanged. Run \`python -m pytest -q\` and \`ruff check src tests scripts\` where dependencies permit, and allow repository CI to test the full supported stack. Link a reproducibility artifact, not a screenshot alone.

Never turn missing data into zeros, tune tolerances to make a preferred result pass, conflate solver agreement with physical validation, or publish third-party confidential, personal, sensitive or license-restricted raw data. For uncertain rights, contribute a link and an extraction script rather than copies.

**No endorsement is implied** by a passing CI check, a merged PR, project visibility, or a collaborator's participation. See [docs/PROVENANCE_CORE_RULES.md](docs/PROVENANCE_CORE_RULES.md).

For a first discussion, open a GitHub issue describing the evidence or methodological concern before proposing a substantial new model family.
