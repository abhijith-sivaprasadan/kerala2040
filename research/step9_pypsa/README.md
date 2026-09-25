# Step 9: PyPSA reproduction of the SciPy balancing model

**Status: reproducible input chain implemented; PyPSA equivalence still awaiting execution.**

Step 9 no longer depends on temporary ZIP files. `prepare_inputs.py` rebuilds the exact Step 7 synthetic quarter-hour inputs and Step 8 SciPy daily reference from the committed FY2024-25 SLDC evidence at `data/external/sldc_fy2024_25/daily_balance.csv`.

The reconstruction was checked against the original temporary Step 7/8 artifacts before publication: all 33,984 demand values in each of the three shapes matched exactly, and all 3,186 Step 8 daily unserved/surplus reference values matched exactly.

## Windows: run the smoke test

From the repository root on branch `step9-pypsa-prepared`:

```powershell
git pull
powershell -ExecutionPolicy Bypass -File .\research\step9_pypsa\run_smoke.ps1
```

The wrapper first creates:
```text
kerala2040_integrated_step7/
  integrated_flat_15min.csv
  integrated_morning_evening_15min.csv
  integrated_evening_stress_15min.csv
  integrated_daily_accounting.csv
kerala2040_balancing_step8/
  balancing_daily.csv
```
Then it runs the 2-day PyPSA comparison.

## Full comparison

Only after the smoke test reports PASS:

```powershell
python .\research\step9_pypsa\run_pypsa_comparison.py --root . --days 354 --output .\research\step9_pypsa\full.json
```

This is 3 shapes × 3 cases × 354 days = 3,186 PyPSA LP solves.

**Acceptance:** optimal status for every solve, quarter-hour balance <0.0001 MW, daily hydro and import energy errors <0.0001 MWh, and maximum daily unserved/surplus difference versus SciPy <0.001 MWh.

Agreement is implementation verification, not empirical validation. The quarter-hour demand profiles are synthetic daily-energy-anchored sensitivity shapes, and the flexibility caps are scenario assumptions rather than verified physical capacity limits.
