# Step 9: PyPSA reproduction of SciPy balancing model

**Status: IMPLEMENTED, NOT EXECUTED OR VERIFIED IN THIS ENVIRONMENT.** PyPSA and highspy were unavailable and package installation failed because the package index could not be reached. Do not claim PyPSA equivalence until the script runs and its QA passes.

## Install and run

```bash
python -m pip install 'pypsa>=0.35' highspy pandas numpy
python run_pypsa_comparison.py --root /path/to/extracted/inputs --days 2 --output smoke.json
python run_pypsa_comparison.py --root /path/to/extracted/inputs --days 354 --output full.json
```

Extract the provided Step 7 and Step 8 ZIPs under `--root` as directories `kerala2040_integrated_step7` and `kerala2040_balancing_step8`. The Step 8 archive also contains `build_step8_balancing.py`; it is not called by the PyPSA script. The script compares each day's PyPSA slack energies with the saved SciPy CSV. It requires 3 shapes × 3 cases × 354 days = 3186 PyPSA LP solves and may take substantial time; run the 2-day smoke test first. It intentionally uses a single bus and a negative-sign generator for surplus, plus two explicit daily energy equality constraints. PyPSA version compatibility must be checked in the smoke test.

**Acceptance:** optimal status for every solve, quarter-hour balance <0.0001 MW, daily hydro and import energy errors <0.0001 MWh, and maximum daily unserved/surplus difference versus SciPy <0.001 MWh. This compares the optimal slack, not individual dispatch, which may be nonunique. Both implementations share input assumptions and therefore agreement is *implementation verification*, not empirical validation or independent-method OSeMOSYS validation.

**Known unresolved issue:** PyPSA's sign convention and variable API should be checked on the smoke test before running the full case. A failing smoke test is not a passing benchmark. This is a prepared implementation, not a verified result.
