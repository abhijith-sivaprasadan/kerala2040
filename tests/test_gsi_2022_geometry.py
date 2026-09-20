"""Exercise source-true geometries and label retention without agency data."""

from __future__ import annotations

import hashlib
from pathlib import Path
import zipfile

import pytest

from kerala2040.gsi_2022_geometry import inspect_archive


def _sample(tmp_path: Path, *, bad_crs: bool = False):
    gpd = pytest.importorskip("geopandas")
    pytest.importorskip("pyogrio")
    from shapely.geometry import Polygon

    directory = tmp_path / "members"
    directory.mkdir()
    frame = gpd.GeoDataFrame(
        {"SUS_CLASS": ["source_raw_A", "source_raw_B"]},
        geometry=[
            Polygon([(76, 10), (76.01, 10), (76.01, 10.01), (76, 10.01)]),
            Polygon([(76.02, 10), (76.03, 10), (76.03, 10.01), (76.02, 10.01)]),
        ],
        crs=None if bad_crs else "EPSG:4326",
    )
    frame.to_file(directory / "example.shp", driver="ESRI Shapefile", engine="pyogrio")
    file = tmp_path / "official_test_only.zip"
    with zipfile.ZipFile(file, "w") as out:
        for part in directory.iterdir():
            out.write(part, "district/" + part.name)
    row = {
        "district": "Test district, not Kerala source",
        "source_url": "https://example.invalid/fixture.zip",
        "sha256": hashlib.sha256(file.read_bytes()).hexdigest(),
        "bytes": file.stat().st_size,
    }
    return file, row


def test_decodes_original_raw_class_values_and_crs(tmp_path):
    file, row = _sample(tmp_path)
    detail = inspect_archive(file, row)
    assert detail["feature_count"] == 2
    assert detail["all_features_read"]
    assert detail["original_crs"] == "EPSG:4326"
    assert detail["source_category_candidate_fields"] == ["SUS_CLASS"]
    assert detail["source_raw_category_profiles"][0]["raw_value_counts"] == {
        "source_raw_A": 1,
        "source_raw_B": 1,
    }
    assert detail["invalid_geometries"] == 0
    assert not detail["legal_buildability_verified"]
    assert detail["siting_capacity_mw"] is None
    assert not detail["district_membership_against_official_boundary_verified"]


def test_wrong_hash_rejected_before_decoding(tmp_path):
    file, row = _sample(tmp_path)
    row["sha256"] = "0" * 64
    with pytest.raises(ValueError, match="checksum"):
        inspect_archive(file, row)


def test_missing_source_crs_rejected(tmp_path):
    file, row = _sample(tmp_path, bad_crs=True)
    with pytest.raises(ValueError, match="CRS"):
        inspect_archive(file, row)
