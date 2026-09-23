"""Offline checks for explicit CDS weather acquisition contracts."""

from __future__ import annotations

import importlib.util
from datetime import date
from pathlib import Path

import pytest

PATH = Path(__file__).resolve().parents[1] / "scripts" / "request_era5_land_hydro_monthly.py"
SPEC = importlib.util.spec_from_file_location("era5_land_hydro", PATH)
assert SPEC and SPEC.loader
mod = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(mod)


def test_month_boundary_and_no_future_dates():
    jobs = list(mod.plan([11, 76, 9, 78], date(2017, 12, 31), date(2018, 2, 2)))
    assert [x["request"]["month"] for x in jobs] == ["12", "01", "02"]
    assert jobs[0]["request"]["day"] == ["31"]
    assert jobs[1]["request"]["day"][-1] == "31"
    assert jobs[2]["request"]["day"] == ["01", "02"]
    assert all(x["spatial_status"] == "bbox_only_NOT_basin_mask" for x in jobs)


def test_invalid_or_inverted_bbox_rejected():
    with pytest.raises(ValueError):
        mod.validate_area([9, 78, 11, 76])
    with pytest.raises(ValueError):
        mod.validate_area([18, 70, 8, 80])


def test_detect_zip_disguised_as_grib(tmp_path):
    x = tmp_path / "sample.grib"
    x.write_bytes(b"PK\x03\x04trash")
    assert mod.magic(x) == "zip_wrong_extension_requires_separate_inspection"
