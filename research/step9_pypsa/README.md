# Step 9: PyPSA reproduction of the SciPy balancing model

**Status: COMPLETE — full independent implementation comparison PASS (25 September 2026).**

Step 9 reproduces the Step 8 daily balancing LP in PyPSA/HiGHS without using SciPy for the comparison solve. `prepare_inputs.py` rebuilds the exact Step 7 synthetic quarter-hour inputs and Step 8 SciPy daily reference from the committed FY2024-25 SLDC evidence at `data/external/sldc_fy2024_25/daily_balance.csv`.

The reconstruction was checked against the original temporary Step 7/8 artifacts before publication: all 33,984 demand values in each of the three shapes matched exactly, and all 3,186 Step 8 daily unserved/surplus reference values matched exactly.

## Verification result

The full run covered:

- 354 observed SLDC days;
- 3 synthetic demand shapes: `flat`, `morning_evening`, `evening_stress`;
- 3 balancing cases: `diagnostic_fixed`, `hydro_flex_1p5`, and `hydro_flex_1p5_import_flex_1p25`;
- **3,186 PyPSA/HiGHS LP solves in total**.

The user-executed full comparison completed with:

```text
RESULT PASS solves 3186 max difference MWh 1.2732925824820995e-10
```

Acceptance was: every solve optimal; quarter-hour balance error < 0.0001 MW; daily hydro and import energy errors < 0.0001 MWh; and maximum daily unserved/surplus difference versus the SciPy reference < 0.001 MWh.

The observed maximum daily slack difference was **1.2732925824820995e-10 MWh**, about 7.85 million times smaller than the 0.001 MWh comparison tolerance. This is numerical agreement to floating-point precision for the comparison target.

## Reproduce locally

From the repository root:

```powershell
python .\research\step9_pypsa\prepare_inputs.py --root .
python .\research\step9_pypsa\run_pypsa_comparison.py --root . --days 354 --output .\research\step9_pypsa\full.json
```

For a quick two-day check:

```powershell
powershell -ExecutionPolicy Bypass -File .\research\step9_pypsa\run_smoke.ps1
```

The preparation step creates the local derived Step 7 and Step 8 inputs required by the comparison. `full.json` is a local run artifact and is not required to be committed; the compact frozen verification record is `verification_summary.json`.

## Interpretation

This result verifies **implementation equivalence**, not empirical validity.

The quarter-hour demand profiles remain synthetic daily-energy-anchored sensitivity shapes. The hydro/import flexibility caps are scenario assumptions rather than verified physical capacity limits. Agreement between SciPy and PyPSA therefore shows that two independent optimisation implementations solve the stated balancing formulation consistently; it does **not** establish that the formulation is a calibrated representation of Kerala's physical grid, nor does it validate a 2040 capacity-expansion pathway.

The next modelling benchmark is an independently formulated OSeMOSYS capacity-expansion experiment, kept separate from this implementation-equivalence test.
