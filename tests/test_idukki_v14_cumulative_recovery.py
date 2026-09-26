from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/audit_idukki_v14_cumulative_recovery.py"
SPEC = spec_from_file_location("audit_idukki_v14_cumulative_recovery", SCRIPT)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Cannot import audit module from {SCRIPT}")
MODULE = module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
audit = MODULE.audit
sha256 = MODULE.sha256


def test_sha256_round_trip(tmp_path: Path):
    p = tmp_path / "x"
    p.write_bytes(b"abc")
    assert sha256(p) == (
        "ba7816bf8f01cfea414140de5dae2223"
        "b00361a396177a9cb410ff61f20015ad"
    )


def test_audit_rejects_wrong_source(tmp_path: Path):
    p = tmp_path / "reservoir_rows.csv"
    pd.DataFrame(
        {
            "date": ["2024-04-01"],
            "reservoir": ["IDUKKI"],
            "inflow_mcm_day": [1.0],
            "month_inflow_mu": [1.0],
        }
    ).to_csv(p, index=False)
    with pytest.raises(ValueError, match="Unexpected reservoir_rows.csv SHA256"):
        audit(p)
