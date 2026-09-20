"""Native LULC files require original raster/legend evidence, not rendered WMS."""

from __future__ import annotations

import copy
import hashlib
import shutil
from pathlib import Path

import pytest
import yaml

from kerala2040.lulc_evidence import audit_lulc

ROOT = Path(__file__).resolve().parents[1]


def _registry(tmp_path: Path) -> Path:
    path = tmp_path / "configs/lulc_native_acquisition_2024_25.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ROOT / "configs/lulc_native_acquisition_2024_25.yaml", path)
    return path


def test_no_fabricated_raster_is_admitted():
    result = audit_lulc(ROOT)
    assert result["products_catalogued"] == 4
    assert result["native_rasters_with_local_source_qa"] == 0
    assert not result["statewide_native_lulc_verified"]
    assert result["siting_eligible_area_sq_km"] is None
    assert result["capacity_ceiling_mw"] is None
    assert not result["audit_gate_closed"]


def test_catalogue_cannot_mark_source_as_fully_acquired(tmp_path):
    path = _registry(tmp_path)
    config = yaml.safe_load(path.read_text())
    config["model_use"]["ecological_exclusion_ready"] = True
    path.write_text(yaml.safe_dump(config))
    with pytest.raises(ValueError, match="cannot self-certify"):
        audit_lulc(tmp_path)


def test_styled_wms_png_and_unproved_raster_hash_fail(tmp_path):
    path = _registry(tmp_path)
    config = yaml.safe_load(path.read_text())
    item = config["products"][0]
    item["native_raster_path"] = "data/external/gis/bhuvan/lulc/rendered_wms.png"
    raster = tmp_path / item["native_raster_path"]
    raster.parent.mkdir(parents=True, exist_ok=True)
    raster.write_bytes(b"\x89PNG\r\n\x1a\nnot_an_original_lulc")
    path.write_text(yaml.safe_dump(config))
    with pytest.raises(ValueError, match="not a styled WMS"):
        audit_lulc(tmp_path)
    item["native_raster_path"] = "data/external/gis/bhuvan/lulc/claimed.tif"
    raster.with_name("claimed.tif").write_bytes(b"not geotiff")
    path.write_text(yaml.safe_dump(config))
    with pytest.raises(ValueError, match="source metadata"):
        audit_lulc(tmp_path)


def test_test_only_categorical_geotiff_is_preliminary_not_buildable_area(tmp_path):
    np = pytest.importorskip("numpy")
    rasterio = pytest.importorskip("rasterio")
    from rasterio.transform import from_origin

    path = _registry(tmp_path)
    config = yaml.safe_load(path.read_text())
    item = config["products"][0]
    raster = tmp_path / item["native_raster_path"]
    legend = tmp_path / item["class_legend_path"]
    raster.parent.mkdir(parents=True, exist_ok=True)
    with rasterio.open(
        raster, "w", driver="GTiff", height=4, width=4, count=1,
        dtype="uint8", crs="EPSG:4326", nodata=0,
        transform=from_origin(76.0, 11.0, 0.01, 0.01),
    ) as image:
        image.write(np.array([
            [1, 1, 2, 2], [1, 1, 2, 2],
            [3, 3, 1, 1], [3, 3, 1, 1],
        ], dtype="uint8"), 1)
    legend.write_text("code,label\n1,Agriculture\n2,Water\n3,Forest\n")
    digest = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    item["native_sha256"] = digest(raster)
    item["class_legend_sha256"] = digest(legend)
    item["original_crs"] = "EPSG:4326"
    item["nodata"] = 0
    item["redistribution_permission"] = "test_fixture_only"
    path.write_text(yaml.safe_dump(config))
    report = audit_lulc(tmp_path)
    assert report["native_rasters_with_local_source_qa"] == 1
    assert report["records"][0]["class_codes_found"] == [1, 2, 3]
    assert not report["statewide_native_lulc_verified"]
    assert report["capacity_ceiling_mw"] is None
    assert not report["audit_gate_closed"]
    wrong = copy.deepcopy(config)
    wrong["products"][0]["native_sha256"] = "0" * 64
    path.write_text(yaml.safe_dump(wrong))
    with pytest.raises(ValueError, match="SHA256 mismatch"):
        audit_lulc(tmp_path)
    wrong = copy.deepcopy(config)
    legend.write_text("code,label\n1,Agriculture\n2,Water\n")
    wrong["products"][0]["class_legend_sha256"] = digest(legend)
    path.write_text(yaml.safe_dump(wrong))
    with pytest.raises(ValueError, match="codes"):
        audit_lulc(tmp_path)
