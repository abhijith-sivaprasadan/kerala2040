"""Regression tests for statewide boundary-clipped DSM/slope QA."""

from __future__ import annotations

import importlib
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
m = importlib.import_module("build_kerala_glo90_boundary_dsm")


def test_slope_requires_valid_cross_neighbours():
    data = np.array([
        [0, 0, 0, 0, 0],
        [0, 1, 2, 3, 0],
        [0, 2, 4, 6, 0],
        [0, 3, 6, 9, 0],
        [0, 0, 0, 0, 0],
    ], dtype="float32")
    slope, valid = m._slope_from_projected_dsm(data, 1.0)
    assert np.count_nonzero(valid) == 9
    assert np.isfinite(slope[2, 2])
    expected = np.degrees(np.arctan(np.sqrt(2**2 + 2**2)))
    assert slope[2, 2] == pytest.approx(expected, rel=1e-6)


def test_slope_drops_pixel_with_missing_neighbour():
    data = np.ones((5, 5), dtype="float32")
    data[2, 1] = np.nan
    slope, _ = m._slope_from_projected_dsm(data, 90)
    assert np.isnan(slope[2, 2])


def test_summary_rejects_all_nan():
    with pytest.raises(ValueError, match="No finite values"):
        m._summary(np.full((2, 2), np.nan, dtype="float32"))


def test_source_tiles_are_exactly_fourteen(tmp_path):
    import json

    source = {
        "original_tiles_and_hashes": [
            {
                "status": "original_tif_downloaded",
                "latitude": 8 + i // 4,
                "longitude": 74 + i % 4,
                "url": f"https://example.test/{i}.tif",
                "sha256": "a" * 64,
            }
            for i in range(14)
        ]
    }
    path = tmp_path / m.DEM_MANIFEST
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(source))
    rows = m._source_tiles(tmp_path)
    assert len(rows) == 14
    source["original_tiles_and_hashes"].append({
        "status": "original_tif_downloaded",
        "latitude": 12, "longitude": 77,
        "url": "https://example.test/x.tif",
        "sha256": "b" * 64,
    })
    path.write_text(json.dumps(source))
    with pytest.raises(ValueError, match="Expected 14"):
        m._source_tiles(tmp_path)
