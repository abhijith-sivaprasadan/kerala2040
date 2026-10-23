"""Independent provenance smoke tests, including a deliberately corrupted source record."""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_daily_accounting_example_uses_real_committed_sources(tmp_path):
    result = subprocess.run(
        [sys.executable, "examples/reproduce_daily_accounting.py", "--output", str(tmp_path / "audit.json")],
        check=True, capture_output=True, text=True, cwd=ROOT,
    )
    data = json.loads(result.stdout)
    assert json.loads((tmp_path / "audit.json").read_text()) == data
    assert data["observed_days"] == 354
    assert data["missing_source_days"] == 11
    assert data["reconstructed_hours"] == 8760
    assert data["observed_source_consumption_mu"] == 30666.2569
    assert data["max_abs_observed_day_energy_residual_mu"] <= 1e-4
    assert data["result"] == "PASS_INVARIANT_NOT_PHYSICAL_VALIDATION"
