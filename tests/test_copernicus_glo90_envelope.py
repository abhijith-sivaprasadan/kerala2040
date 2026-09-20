"""Guard real Copernicus DSM tile acquisition and avoid false terrain readiness."""

from __future__ import annotations

import importlib
import sys
from pathlib import Path

import pytest

np = pytest.importorskip("numpy")
rasterio = pytest.importorskip("rasterio")
from_origin = rasterio.transform.from_origin

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
dem = importlib.import_module("acquire_copernicus_glo90_envelope")


def test_kerala_bbox_grid_and_verified_pilot_tile():
    assert len(dem.LATITUDES) * len(dem.LONGITUDES) == 20
    assert dem.tile_name(9, 76) == "Copernicus_DSM_COG_30_N09_00_E076_00_DEM"
    assert dem.tile_url(9, 76) == (
        "https://copernicus-dem-90m.s3.amazonaws.com/"
        "Copernicus_DSM_COG_30_N09_00_E076_00_DEM/"
        "Copernicus_DSM_COG_30_N09_00_E076_00_DEM.tif"
    )


def test_synthetic_tile_outside_source_vintage_never_becomes_bare_earth(tmp_path):
    target = tmp_path / "synthetic.tif"
    with rasterio.open(
        target, "w", driver="GTiff", width=1200, height=1200,
        count=1, dtype="float32", crs="EPSG:4326",
        transform=from_origin(75.99958333333333, 10.000416666666666,
                              1 / 1200, 1 / 1200),
    ) as dst:
        dst.write(np.zeros((1200, 1200), dtype="float32"), 1)
    info = dem.inspect_tile(target, 9, 76)
    assert info["source_nodata_metadata"] is None
    assert info["zero_sample_count_ambiguous_sea_or_terrain"] == 1_440_000
    assert info["bare_earth_elevation"] is False
    assert info["vertical_datum_independently_verified"] is False
    with pytest.raises(ValueError, match="geolocation"):
        dem.inspect_tile(target, 11, 76)


def test_bad_source_raster_is_not_accepted(tmp_path):
    target = tmp_path / "wrong_crs.tif"
    with rasterio.open(
        target, "w", driver="GTiff", width=1200, height=1200,
        count=1, dtype="float32", crs="EPSG:3857",
        transform=from_origin(76, 10, 1 / 1200, 1 / 1200),
    ) as dst:
        dst.write(np.zeros((1200, 1200), dtype="float32"), 1)
    with pytest.raises(ValueError, match="unexpected CRS"):
        dem.inspect_tile(target, 9, 76)
