"""GSA annual/day/month source checks must preserve units and exact grids."""
from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/qa_gsa_pvout_full_raster.py"
spec = importlib.util.spec_from_file_location("gsa_pvout_full_raster_qa", SCRIPT)
assert spec is not None and spec.loader is not None
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def test_gsa_leap_day_climatology() -> None:
    assert module.MONTH_DAYS[1] == 28.25
    assert sum(module.MONTH_DAYS) == module.ANNUAL_DAYS == 365.25
    assert module.MONTH_DAYS[5] == 30


def test_exact_two_source_folders_and_all_26_tiffs(tmp_path: Path) -> None:
    for folder in module.FOLDERS.values():
        parent = tmp_path / folder / "nested"
        parent.mkdir(parents=True)
        (parent / "PVOUT.tif").write_bytes(b"example annual")
        monthly = parent / "monthly"
        monthly.mkdir()
        for month in range(1, 13):
            (monthly / f"PVOUT_{month:02d}.tif").write_bytes(b"month")
    found = module.find_layers(tmp_path)
    assert len(found) == 26
    assert found["period_totals_month_02"].name == "PVOUT_02.tif"
    assert found["average_daily_annual"].name == "PVOUT.tif"


def test_duplicate_months_fail_not_pick_random_file(tmp_path: Path) -> None:
    for folder in module.FOLDERS.values():
        parent = tmp_path / folder
        parent.mkdir()
        (parent / "PVOUT.tif").write_bytes(b"annual")
        for month in range(1, 13):
            (parent / f"PVOUT_{month:02d}.tif").write_bytes(b"month")
    extra = tmp_path / module.FOLDERS["average_daily"] / "extra"
    extra.mkdir()
    (extra / "PVOUT_01.tif").write_bytes(b"ambiguous")
    with pytest.raises(ValueError, match="Expected exactly one"):
        module.find_layers(tmp_path)


def test_ratio_accumulates_mismatched_mask_and_relative_error() -> None:
    metric = module.start_metric(28.25)
    month_total = np.array([28.25, 56.5, 100, 0], dtype=float)
    mean_day = np.array([1, 2, 2, 0], dtype=float)
    good_total = np.array([True, True, True, False])
    good_day = np.array([True, True, True, True])
    module.compare_arrays(
        metric, month_total, mean_day * 28.25,
        good_total, good_day, tolerance_pct=0.2,
    )
    assert metric["matched_positive_cells"] == 3
    assert metric["source_valid_mask_mismatches"] == 1
    assert metric["cells_exceeding_tolerance"] == 1
    assert metric["max_absolute_relative_error_pct"] > 40


def test_full_raster_synthetic_source_roundtrip(tmp_path: Path) -> None:
    rasterio = pytest.importorskip("rasterio")
    from rasterio.transform import from_origin

    source = tmp_path / "inputs"
    annual_day = np.array([[4.0, 5.0], [6.0, -9999.0]], dtype="float32")
    profile = {
        "driver": "GTiff", "width": 2, "height": 2, "count": 1,
        "dtype": "float32", "crs": "EPSG:4326",
        "transform": from_origin(74, 13, .01, .01), "nodata": -9999.0,
    }
    for kind, folder in module.FOLDERS.items():
        parent = source / folder
        parent.mkdir(parents=True)
        with rasterio.open(parent / "PVOUT.tif", "w", **profile) as dst:
            dst.write(
                np.where(
                    annual_day == -9999, -9999,
                    annual_day * (365.25 if kind == "period_totals" else 1),
                ), 1
            )
        for month in range(1, 13):
            with rasterio.open(
                parent / f"PVOUT_{month:02d}.tif", "w", **profile
            ) as dst:
                dst.write(
                    np.where(
                        annual_day == -9999, -9999,
                        annual_day * (
                            module.MONTH_DAYS[month - 1]
                            if kind == "period_totals" else 1
                        ),
                    ),
                    1,
                )
    result = module.audit(source, tmp_path / "qa.json", tolerance_pct=0.2)
    assert result["annual_valid_positive_cells"] == 3
    assert result["passed"] is True
    assert result["model_admitted"] is False
    assert (tmp_path / "qa.json").exists()
