"""WDPA retrieval and official KFD area baseline regression contracts."""
from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
m = importlib.import_module("crosswalk_kerala_protected_areas")


def test_official_register_is_dated_and_not_spatial():
    data = yaml.safe_load((ROOT / m.CONFIG).read_text())
    assert len(data["protected_areas"]) == 25
    assert len(data["overlapping_designations"]) == 2
    lookup = {item["name"]: item for item in data["protected_areas"]}
    assert lookup["Silent Valley National Park"]["area_km2"] == 89.52
    assert lookup["Silent Valley National Park"]["prior_kfd_area_km2"] == 237.52
    assert lookup["Idukki Wildlife Sanctuary"]["area_km2"] == 105.364
    assert lookup["Shendurney Wildlife Sanctuary"]["area_km2"] == 172.403
    assert lookup["Chimmony Wildlife Sanctuary"]["area_km2"] == 114.6
    assert lookup["Wayanad Wildlife Sanctuary"]["area_km2"] == 344.479
    assert lookup["Kadalundi - Vallikunnu Community Reserve"]["area_km2"] == 1.538
    assert data["model_use"]["statutory_boundary_verified"] is False
    assert data["model_use"]["protected_area_union_sq_km"] is None


def test_curated_exact_name_not_broad_substring():
    entry = {"name": "Periyar National Park", "aliases": ["Periyar"]}
    assert m._candidate(entry, {"name_eng": "Periyar"})
    assert not m._candidate(entry, {"name_eng": "Great Periyar Hills Park"})


def point(oid, name):
    return {
        "type": "Feature",
        "properties": {"objectid": oid, "site_id": oid, "name_eng": name,
                       "iso3": "IND"},
        "geometry": {"type": "Point", "coordinates": [76.2, 10.2]},
    }


def polygon(oid, name):
    return {
        "type": "Feature",
        "properties": {"objectid": oid, "site_id": oid, "name_eng": name,
                       "iso3": "IND", "desig_eng": "National Park"},
        "geometry": {
            "type": "Polygon",
            "coordinates": [[[76, 10], [76.01, 10],
                             [76.01, 10.01], [76, 10.01], [76, 10]]],
        },
    }


class Response:
    def __init__(self, data):
        self.content = json.dumps(data).encode()

    def raise_for_status(self):
        pass

    def json(self):
        return json.loads(self.content)


class Session:
    def __init__(self, features, declared_count=None):
        self.features = features
        self.declared_count = declared_count

    def get(self, url, params, timeout):
        if params.get("returnCountOnly") == "true":
            return Response({"count": self.declared_count if (
                self.declared_count is not None
            ) else len(self.features)})
        if params.get("returnIdsOnly") == "true":
            return Response({
                "objectIdFieldName": "objectid",
                "objectIds": [f["properties"]["objectid"] for f in self.features],
            })
        requested = set(map(int, params["objectIds"].split(",")))
        return Response({
            "type": "FeatureCollection",
            "features": [
                f for f in self.features
                if f["properties"]["objectid"] in requested
            ],
        })


def test_id_reconciliation_and_raw_page_hash(tmp_path):
    layer = m.fetch_layer(Session([polygon(7, "Periyar National Park")]),
                          1, tmp_path)
    assert layer["server_spatial_count"] == 1
    assert layer["all_ids_reconciled"] is True
    assert len(layer["pages"][0]["sha256"]) == 64
    assert Path(layer["pages"][0]["file"]).is_file()


def test_reject_truncated_or_misreported_ids(tmp_path):
    with pytest.raises(ValueError, match="disagree"):
        m.fetch_layer(Session([polygon(7, "A")], declared_count=2),
                      1, tmp_path)


def test_point_is_never_a_polygon_or_area():
    official = [{"name": "Periyar National Park", "area_km2": 350,
                 "aliases": []}] * 25
    result = m.classify(official, [], [point(1, "Periyar National Park")])
    assert result["official_designations_uniquely_matched"] == 0
    assert result["official_designations_unresolved"][0][
        "point_candidates_NOT_polygons"
    ] == 1
    assert result["polygon_features"] == 0


def test_polygon_candidate_not_statutory_even_when_exact_name():
    official = [{"name": "Periyar National Park", "area_km2": 350,
                 "aliases": []}] * 25
    result = m.classify(
        official, [polygon(7, "Periyar National Park")], []
    )
    assert result["matches"][0]["statutory_boundary_verified"] is False
    assert result["matches"][0]["wdpa_diagnostic_area_km2"] > 0
