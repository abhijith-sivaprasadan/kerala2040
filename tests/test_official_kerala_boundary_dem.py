"""Source boundary acquisition must not certify ecological capacity."""

from __future__ import annotations

import io
import json
import sys
import zipfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from audit_official_kerala_boundary_dem import (
    _eligible_resource,
    _kerala_feature,
    _parse_geojson,
)

KERALA = {
    "type": "FeatureCollection",
    "features": [{
        "type": "Feature",
        "properties": {"STATE": "Kerala", "code": 32},
        "geometry": {
            "type": "Polygon",
            "coordinates": [[[75.0, 8.1], [77.0, 8.1],
                             [77.0, 12.8], [75.0, 12.8],
                             [75.0, 8.1]]],
        },
    }],
}


def test_only_government_state_geojson_resource_candidate():
    assert _eligible_resource({
        "name": "state_NWIC_GeoJSON.zip",
        "url": "https://nwdp.nwic.gov.in/files/state_NWIC_GeoJSON.zip",
        "format": "GeoJSON",
    })
    assert not _eligible_resource({
        "name": "district",
        "url": "http://example.com/district.zip",
        "format": "GeoJSON",
    })


def test_synthetic_kerala_polygon_has_valid_source_structure():
    geometry, props, area = _kerala_feature(KERALA)
    assert props["STATE"] == "Kerala"
    assert geometry.is_valid
    assert 25000 < area < 55000


def test_kerala_not_in_data_fails_closed():
    source = json.loads(json.dumps(KERALA))
    source["features"][0]["properties"]["STATE"] = "Karnataka"
    with pytest.raises(ValueError, match="exactly one Kerala"):
        _kerala_feature(source)


def test_geojson_zip_must_contain_exactly_one_data_resource():
    b = io.BytesIO()
    with zipfile.ZipFile(b, "w") as z:
        z.writestr("source/states.geojson", json.dumps(KERALA))
    assert len(_parse_geojson(b.getvalue())["features"]) == 1
    with zipfile.ZipFile(b, "a") as z:
        z.writestr("source/another.json", "{}")
    with pytest.raises(ValueError, match="one GeoJSON"):
        _parse_geojson(b.getvalue())
