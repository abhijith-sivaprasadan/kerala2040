"""Synthetic regression checks; not Kerala evidence."""
from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "audit_kerala_niwe_resource.py"
SPEC = importlib.util.spec_from_file_location("audit_kerala_niwe_resource", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
FIELDS = MODULE.FIELDS
analyze = MODULE.analyze
histogram = MODULE.histogram
read_clip = MODULE.read_clip


def sample_clip(tmp_path):
    path = tmp_path / "clip.csv.gz"
    pd.DataFrame([
        [76.1, 10.1, 3.5, 4.0, 2.0, 1.0, 50.0],
        [76.2, 10.2, 7.5, 8.4, 2.2, 1.1, 410.0],
        [76.3, 10.3, 10.5, 11.8, 2.5, 1.0, 850.0],
    ], columns=FIELDS).to_csv(path, index=False)
    return path


def test_binning_edges():
    bins = histogram(np.array([0., 3., 4., 9., 10.]),
                     (0., 3., 4., 10., float("inf")))
    assert [b["point_centres"] for b in bins] == [1, 1, 2, 1]
    assert bins[-1]["maximum_exclusive"] is None


def test_pinned_hash_and_descriptive_result(tmp_path):
    path = sample_clip(tmp_path)
    with pytest.raises(ValueError, match="SHA256"):
        analyze(path, expected_rows=3)
    report = analyze(path, expected_rows=3, allow_repacked_clip=True)
    assert report["point_centres"] == 3
    assert report["wind_speed_m_s"]["median"] == 7.5
    assert report["feasible_capacity_MW"] is None
    assert report["model_admitted"] is False


def test_invalid_or_duplicate_coordinates(tmp_path):
    path = sample_clip(tmp_path)
    frame = pd.read_csv(path)
    frame.loc[0, "Longitude (E)"] = 100.0
    frame.to_csv(path, index=False)
    with pytest.raises(ValueError, match="outside Kerala"):
        read_clip(path, 3)
    frame.loc[0, "Longitude (E)"] = frame.loc[1, "Longitude (E)"]
    frame.loc[0, "Latitude (N)"] = frame.loc[1, "Latitude (N)"]
    frame.to_csv(path, index=False)
    with pytest.raises(ValueError, match="Duplicate"):
        read_clip(path, 3)


def test_slope_sampling_and_thresholds_with_real_geo_tiff_fixture(tmp_path):
    """Synthetic raster tests CRS sampling, missing data and denominator accounting."""
    import rasterio
    from rasterio.transform import from_origin

    path = sample_clip(tmp_path)
    frame = read_clip(path, 3)
    slope_path = tmp_path / "degrees.tif"
    raster = np.full((3, 3), 4.0, dtype=np.float32)
    raster[1, 1] = 12.0
    raster[0, 2] = -9999.0
    with rasterio.open(
        slope_path, "w", driver="GTiff", height=3, width=3,
        count=1, dtype="float32", crs="EPSG:4326",
        transform=from_origin(76.05, 10.35, 0.1, 0.1),
        nodata=-9999.0,
    ) as dst:
        dst.write(raster, 1)

    sampled = MODULE.sample_slope(slope_path, frame)
    assert np.allclose(sampled[:2], [4.0, 12.0])
    assert np.isnan(sampled[2])
    with pytest.raises(ValueError, match="Slope SHA256"):
        analyze(path, expected_rows=3, allow_repacked_clip=True, slope=slope_path)
    report = analyze(path, expected_rows=3, allow_repacked_clip=True,
                     slope=slope_path, allow_unpinned_slope=True)
    terrain = report["terrain"]
    assert terrain["matches_verified_2026_09_20_GLO90_slope_tiff"] is False
    assert terrain["non_pinned_slope_explicitly_allowed"] is True
    assert terrain["available_point_centres"] == 2
    assert terrain["missing_point_centres"] == 1
    assert sum(row["point_centres"] for row in terrain["slope_classes_degrees"]) == 2
    assert sum(sum(row) for row in terrain["joint_speed_by_slope_point_counts"]) == 2
    rows = terrain["wind_speed_slope_threshold_sensitivity"]
    assert len(rows) == 16
    assert next(
        row for row in rows
        if row["minimum_150m_wind_speed_m_s_inclusive"] == 7
        and row["maximum_DSM_surface_slope_degrees_inclusive"] == 15
    )["matching_point_centres"] == 1
    assert report["candidate_area_km2"] is None
    assert report["feasible_capacity_MW"] is None


def test_private_point_maps_are_created_but_not_admitted(tmp_path):
    path = sample_clip(tmp_path)
    frame = read_clip(path, 3)
    manifest = MODULE.render_private_maps(
        frame, np.array([4.0, 12.0, np.nan]), tmp_path / "private_media"
    )
    assert manifest["derived_maps_local_private_only"]
    assert manifest["public_redistribution_rights_verified"] is False
    assert len(manifest["files"]) == 3
    for name, item in manifest["files"].items():
        assert (tmp_path / "private_media" / name).read_bytes()[:8] == (
            bytes([137, 80, 78, 71, 13, 10])
        )
        assert len(item["sha256"]) == 64
    assert (tmp_path / "private_media" /
            "NIWE_150m_kerala_DSM_slope_PRIVATE.png").exists()
