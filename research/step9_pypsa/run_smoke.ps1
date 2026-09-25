$ErrorActionPreference = "Stop"
$repo = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
Write-Host "Kerala2040 Step 9: rebuilding Step 7/8 from committed SLDC evidence..."
python (Join-Path $PSScriptRoot "prepare_inputs.py") --root $repo
Write-Host "Running 2-day PyPSA smoke comparison..."
python (Join-Path $PSScriptRoot "run_pypsa_comparison.py") --root $repo --days 2 --output (Join-Path $PSScriptRoot "smoke.json")
Write-Host "Smoke test completed. Inspect RESULT above and smoke.json before full run."
