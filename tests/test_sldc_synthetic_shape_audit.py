"""Strict scenario QA from generated synthetic intervals."""
import csv
import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def load(relative):
    path = ROOT / relative
    spec = importlib.util.spec_from_file_location(path.stem, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_synthetic_shape_audit(tmp_path):
    generator = load("scripts/build_sldc_synthetic_15min.py")
    audit = load("analysis/audit_sldc_synthetic_shape_sensitivity.py")
    _, intervals, _ = generator.generate(generator.read_daily())
    path = tmp_path / "intervals.csv"
    generator.write(intervals, path)
    report = audit.audit(path)
    assert report["days"] == 365
    assert set(report["scenarios"]) == set(generator.METHODS)
    assert all(value["days"] == 365 for value in report["per_scenario"].values())


def test_synthetic_shape_audit_rejects_corruption(tmp_path):
    generator = load("scripts/build_sldc_synthetic_15min.py")
    audit = load("analysis/audit_sldc_synthetic_shape_sensitivity.py")
    _, intervals, _ = generator.generate(generator.read_daily()[:1])
    intervals[0]["demand_mw"] = 0
    path = tmp_path / "corrupt.csv"
    generator.write(intervals, path)
    with pytest.raises(ValueError, match="Invalid quarter-hour power"):
        audit.audit(path)
