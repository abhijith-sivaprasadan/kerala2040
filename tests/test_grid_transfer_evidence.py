"""Daily interchange evidence must not be promoted into a power/contract limit."""

from __future__ import annotations

import copy
import shutil
from pathlib import Path

import pytest
import yaml

from kerala2040.grid_transfer_evidence import audit_transfer_evidence

ROOT = Path(__file__).resolve().parents[1]
FILES = (
    "data/external/sldc_fy2024_25/qa_report.json",
    "data/external/sldc_fy2024_25/daily_balance.csv",
    "data/external/sldc_fy2024_25/import_interface_daily.csv",
    "configs/grid_transfer_contract_evidence_2024_25.yaml",
    "configs/observed_2024_25.yaml",
)


def _copy(tmp_path: Path) -> Path:
    for path in FILES:
        target = tmp_path / path
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / path, target)
    return tmp_path


def test_official_daily_imports_and_scope_are_not_mw_limits():
    report = audit_transfer_evidence(ROOT)
    assert report["observed_days"] == 354
    assert report["expected_days"] == 365
    assert len(report["missing_dates"]) == 11
    assert report["import_interface_rows"] == 2832
    assert report["reported_grouped_interfaces"] == 8
    assert report["dated_transfer_snapshot_count"] == 2
    assert report["max_daily_interface_reconciliation_residual_mu"] <= 0.001
    assert report["observed_days_only_net_import_mu"] == pytest.approx(22635.0183)
    assert not report["model_import_limit_verified"]
    assert not report["full_fy_atc_ttc_profile_verified"]
    assert not report["contract_deliverability_verified"]
    assert report["existing_6500_mw_is_only_scenario_assumption"]
    assert not report["audit_gate_closed"]


def test_atc_arithmetic_and_year_bounds_fail_closed(tmp_path):
    root = _copy(tmp_path)
    path = root / "configs/grid_transfer_contract_evidence_2024_25.yaml"
    baseline = yaml.safe_load(path.read_text())
    wrong = copy.deepcopy(baseline)
    wrong["transfer_snapshots"][0]["atc_mw"] = 6500
    path.write_text(yaml.safe_dump(wrong))
    with pytest.raises(ValueError, match="ATC inconsistent"):
        audit_transfer_evidence(root)
    wrong = copy.deepcopy(baseline)
    wrong["procurement_examples"][1]["classification"] = (
        "future_project_commitment_not_fy2024_25_available_supply"
    )
    path.write_text(yaml.safe_dump(wrong))
    with pytest.raises(ValueError, match="Post-year agreement"):
        audit_transfer_evidence(root)
    wrong = copy.deepcopy(baseline)
    wrong["model_use"]["can_apply_snapshot_as_full_year_import_limit"] = True
    path.write_text(yaml.safe_dump(wrong))
    with pytest.raises(ValueError, match="may not enable"):
        audit_transfer_evidence(root)


def test_daily_interface_energy_cannot_hide_missing_or_corrupted_day(tmp_path):
    root = _copy(tmp_path)
    path = root / "data/external/sldc_fy2024_25/import_interface_daily.csv"
    lines = path.read_text().splitlines()
    path.write_text("\n".join(lines[:-1]) + "\n")
    with pytest.raises(ValueError, match="count"):
        audit_transfer_evidence(root)
    original = (ROOT / "data/external/sldc_fy2024_25/import_interface_daily.csv").read_text().splitlines()
    fields = original[1].split(",")
    fields[2] = str(float(fields[2]) + 2.0)
    original[1] = ",".join(fields)
    path.write_text("\n".join(original) + "\n")
    with pytest.raises(ValueError, match="residual"):
        audit_transfer_evidence(root)
