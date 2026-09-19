"""Observed figure builder must retain SLDC evidence coverage and provenance."""

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = spec_from_file_location("sldc_observed_figures", ROOT / "scripts/build_sldc_observed_figures.py")
assert SPEC and SPEC.loader
MODULE = module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_observed_figures(tmp_path):
    summary = MODULE.build_figures(ROOT, tmp_path)
    assert summary["observed_days"] == 354
    assert len(summary["missing_dates"]) == 11
    assert summary["classification"] == "derived_from_measured_daily_not_hourly"
    assert len(summary["figure_paths"]) == 4
    for name in summary["figure_paths"]:
        assert (tmp_path / name).stat().st_size > 1000
    assert (tmp_path / "evidence_manifest.json").exists()
