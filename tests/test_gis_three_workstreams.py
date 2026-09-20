"""GIS source routes and sample assets cannot pass ecological site eligibility."""

from __future__ import annotations

import copy
import shutil
import zipfile
from pathlib import Path

import pytest
import yaml

from kerala2040.gis_three_workstreams import (
    audit_gis,
    check_raster,
    check_shapefile_zip,
)

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = "configs/gis_forest_dem_wetlands_hazards_2026.yaml"


def _copy(tmp_path: Path) -> tuple[Path, dict]:
    path = tmp_path / REGISTRY
    path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ROOT / REGISTRY, path)
    acquisition = "data/evidence/gis/official_gis_public_acquisition_2026_09_20.json"
    archived = tmp_path / acquisition
    archived.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ROOT / acquisition, archived)
    return path, yaml.safe_load(path.read_text())


def test_three_official_workstreams_are_distinct_and_not_eligible():
    result = audit_gis(ROOT)
    assert len(result["workstreams"]) == 3
    forest = result["workstreams"]["forest_protected_areas"]
    assert forest["official_boundary_layers_reported"]
    assert not forest["source_geometry_verified_in_committed_repo"]
    terrain = result["workstreams"]["elevation_dem"]
    assert terrain["dsm_is_not_bare_earth"]
    assert terrain["glo90_sample_tile_retrieved_in_workflow_artifact"]
    assert not terrain["statewide_dem_raster_verified_in_committed_repo"]
    hazards = result["workstreams"]["wetlands_waterbodies_landslide"]
    assert hazards["published_gsi_2022_district_download_labels"] == 13
    assert hazards["gsi_original_zips_downloaded_to_workflow_artifact"] == 13
    assert hazards["gsi_shapefile_bundles_verified_in_committed_repo"] == 0
    assert not result["ecological_eligibility_established"]
    assert result["eligible_area_sq_km"] is None
    assert result["capacity_ceiling_mw"] is None
    assert not result["audit_gate_closed"]


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("ecological_capacity_ceiling_ready", True, "self-certify"),
        ("potential_mw", 1_000_000, "invent eligible"),
    ],
)
def test_catalogue_cannot_promote_missing_geometries(tmp_path, field, value, message):
    path, registry = _copy(tmp_path)
    registry["model_use"][field] = value
    path.write_text(yaml.safe_dump(registry))
    with pytest.raises(ValueError, match=message):
        audit_gis(tmp_path)


def test_draft_wetland_and_forest_cannot_be_marked_verified(tmp_path):
    path, baseline = _copy(tmp_path)
    data = copy.deepcopy(baseline)
    data["workstreams"]["wetlands_waterbodies_landslide"]["final_notifications_mapped"] = True
    path.write_text(yaml.safe_dump(data))
    with pytest.raises(ValueError, match="Draft wetland"):
        audit_gis(tmp_path)
    data = copy.deepcopy(baseline)
    data["workstreams"]["forest_protected_areas"]["confirmed_geometry_acquired"] = True
    path.write_text(yaml.safe_dump(data))
    with pytest.raises(ValueError, match="Forest data"):
        audit_gis(tmp_path)


def test_gsi_zip_requires_all_four_shapefile_components(tmp_path):
    file = tmp_path / "gsi.zip"
    with zipfile.ZipFile(file, "w") as z:
        z.writestr("district/a.shp", b"not real polygons")
        z.writestr("district/a.dbf", b"not a valid table")
    with pytest.raises(ValueError, match="missing shp/shx/dbf/prj"):
        check_shapefile_zip(file)
    with zipfile.ZipFile(file, "w") as z:
        for ext in ("shp", "shx", "dbf", "prj"):
            z.writestr(f"district/a.{ext}", b"fixture only")
    result = check_shapefile_zip(file)
    assert result["complete_shapefile_groups"] == ["district/a"]
    assert not result["geometry_count_verified"]
    assert not result["kerala_coverage_verified"]


def test_small_synthetic_height_raster_not_statewide_or_bare_earth(tmp_path):
    np = pytest.importorskip("numpy")
    rasterio = pytest.importorskip("rasterio")
    from rasterio.transform import from_origin

    file = tmp_path / "fictional.tif"
    with rasterio.open(
        file, "w", driver="GTiff", count=1, dtype="float32",
        width=4, height=4, crs="EPSG:4326", nodata=-9999,
        transform=from_origin(76.0, 11.0, 0.01, 0.01),
    ) as src:
        src.write(np.ones((4, 4), dtype="float32"), 1)
    result = check_raster(file)
    assert result["valid_pixels_in_this_file"] == 16
    assert not result["statewide_coverage_verified"]
    assert not result["slope_threshold_validated"]
    assert result["surface_type"] == "not_established_by_raster_structure"
    with pytest.raises(ValueError, match="not an original TIFF"):
        check_raster(tmp_path / "rendered.png")


def test_source_hash_archive_tampering_fails_closed(tmp_path):
    import json

    _copy(tmp_path)
    file = tmp_path / "data/evidence/gis/official_gis_public_acquisition_2026_09_20.json"
    data = json.loads(file.read_text())
    data["gsi_2022"]["per_district"][0]["sha256"] = ""
    file.write_text(json.dumps(data))
    with pytest.raises(ValueError, match="archive hashes"):
        audit_gis(tmp_path)
