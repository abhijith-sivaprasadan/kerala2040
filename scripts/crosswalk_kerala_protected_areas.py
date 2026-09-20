"""Bounded KFD/WDPA secondary-source crosswalk; never infer statutory boundaries.

Query point and polygon layers separately. Server-provided IDs/counts establish
retrieval completeness for the *search envelope*, not national or Kerala
protected-area completeness. A zero-match crosswalk is an audit finding.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import UTC, datetime
from pathlib import Path

import requests
import yaml
from pyproj import Transformer
from shapely.geometry import shape
from shapely.ops import transform

CONFIG = Path("configs/kerala_protected_area_crosswalk_2026.yaml")
BASE = (
    "https://data-gis.unep-wcmc.org/server/rest/services/"
    "ProtectedSites/The_World_Database_of_Protected_Areas/FeatureServer"
)
ENVELOPE = "74.75,8.15,77.55,12.9"
MAX_ENVELOPE_IDS = 5000
ID_PAGE_SIZE = 100
MAX_RESPONSE_BYTES = 60_000_000


def norm(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", str(value).casefold())


def digest(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def _get(session: requests.Session, url: str, params: dict) -> tuple[dict, bytes]:
    response = session.get(url, params=params, timeout=(20, 120))
    response.raise_for_status()
    if len(response.content) > MAX_RESPONSE_BYTES:
        raise ValueError("WDPA response exceeds research download cap")
    data = response.json()
    if not isinstance(data, dict) or data.get("error"):
        raise ValueError(f"WDPA ArcGIS error: {str(data.get('error'))[:200]}")
    return data, response.content


def _spatial() -> dict:
    return {
        "geometry": ENVELOPE,
        "geometryType": "esriGeometryEnvelope",
        "inSR": "4326",
        "spatialRel": "esriSpatialRelIntersects",
    }


def fetch_layer(session: requests.Session, layer: int, raw_dir: Path) -> dict:
    """Verify a complete, bounded ArcGIS envelope result using its own IDs."""
    url = f"{BASE}/{layer}/query"
    params = {"where": "1=1", "f": "json", **_spatial()}
    counts, counts_bytes = _get(
        session, url, {**params, "returnCountOnly": "true"}
    )
    ids_data, ids_bytes = _get(
        session, url, {**params, "returnIdsOnly": "true"}
    )
    count = counts.get("count")
    object_ids = ids_data.get("objectIds")
    if count is None or not isinstance(count, int) or count < 0:
        raise ValueError("WDPA missing server-reported spatial count")
    if object_ids is None:
        object_ids = []
    if not isinstance(object_ids, list) or any(
        not isinstance(oid, int) for oid in object_ids
    ):
        raise ValueError("WDPA objectIds response invalid")
    if len(object_ids) != count or len(set(object_ids)) != count:
        raise ValueError("WDPA ID list and server count disagree")
    if count > MAX_ENVELOPE_IDS:
        raise ValueError("WDPA envelope exceeds bounded retrieval cap")
    raw_dir.mkdir(parents=True, exist_ok=True)
    feature_by_id = {}
    pages = []
    for offset in range(0, count, ID_PAGE_SIZE):
        page_ids = sorted(object_ids)[offset:offset + ID_PAGE_SIZE]
        data, body = _get(session, url, {
            "where": "1=1",
            "objectIds": ",".join(map(str, page_ids)),
            "outFields": "*",
            "returnGeometry": "true",
            "outSR": "4326",
            "f": "geojson",
        })
        if data.get("type") != "FeatureCollection":
            raise ValueError("WDPA page is not GeoJSON FeatureCollection")
        if data.get("exceededTransferLimit"):
            raise ValueError("WDPA page truncated by server")
        page_no = offset // ID_PAGE_SIZE
        path = raw_dir / f"wdpa_layer{layer}_page{page_no:03}.geojson"
        path.write_bytes(body)
        seen = set()
        for feature in data.get("features", []):
            props = feature.get("properties") or {}
            oid = props.get("objectid")
            if oid is None:
                oid = props.get("OBJECTID")
            if not isinstance(oid, int) or oid not in page_ids or oid in seen:
                raise ValueError("WDPA page has missing, repeated or foreign OID")
            if feature.get("geometry") is None:
                raise ValueError("WDPA feature has no geometry")
            seen.add(oid)
            if oid in feature_by_id:
                raise ValueError("WDPA feature repeated across pages")
            feature_by_id[oid] = feature
        if seen != set(page_ids):
            raise ValueError("WDPA page failed complete ID reconciliation")
        pages.append({"file": str(path), "bytes": len(body),
                      "sha256": digest(body), "returned": len(seen)})
    if set(feature_by_id) != set(object_ids):
        raise ValueError("WDPA envelope retrieval incomplete")
    name = {0: "point", 1: "polygon"}[layer]
    features = [feature_by_id[k] for k in sorted(feature_by_id)]
    return {
        "name": name,
        "layer": layer,
        "source_url": url,
        "source_id_query_sha256": digest(ids_bytes),
        "source_count_query_sha256": digest(counts_bytes),
        "server_spatial_count": count,
        "retrieved_object_id_count": len(features),
        "all_ids_reconciled": True,
        "pages": pages,
        "features": features,
    }


def _candidate(entry: dict, properties: dict) -> bool:
    """Curated exact aliases only; broad substring matches cause false joins."""
    names = {
        norm(properties.get("name_eng") or ""),
        norm(properties.get("name") or ""),
    } - {""}
    aliases = {norm(entry["name"])} | {
        norm(value) for value in entry.get("aliases", [])
    }
    return bool(names & aliases)


def classify(primary: list[dict], polygon_features: list[dict],
             point_features: list[dict]) -> dict:
    if len(primary) != 25:
        raise ValueError("KFD protected-area register must contain 25 core entries")
    projected = Transformer.from_crs(
        "EPSG:4326", "EPSG:32643", always_xy=True
    ).transform
    polygon_rows = []
    for feature in polygon_features:
        geometry = shape(feature["geometry"])
        if geometry.geom_type not in {"Polygon", "MultiPolygon"}:
            raise ValueError("WDPA polygon layer returned a non-polygon")
        props = feature["properties"]
        if not geometry.is_empty and geometry.is_valid:
            area = float(transform(projected, geometry).area / 1_000_000)
        else:
            area = None
        polygon_rows.append({
            "objectid": props.get("objectid"),
            "site_id": props.get("site_id"),
            "name": props.get("name_eng") or props.get("name"),
            "iso3": props.get("iso3"),
            "designation": props.get("desig_eng") or props.get("desig"),
            "geometry_type": geometry.geom_type,
            "valid": bool(geometry.is_valid),
            "empty": bool(geometry.is_empty),
            "area_epsg32643_km2_diagnostic": area,
            "props": props,
        })
    point_rows = []
    for feature in point_features:
        geometry = shape(feature["geometry"])
        if geometry.geom_type not in {"Point", "MultiPoint"}:
            raise ValueError("WDPA point layer returned a non-point")
        props = feature["properties"]
        point_rows.append({
            "objectid": props.get("objectid"),
            "site_id": props.get("site_id"),
            "name": props.get("name_eng") or props.get("name"),
            "iso3": props.get("iso3"),
            "geometry_type": geometry.geom_type,
            "props": props,
        })
    matches, unresolved = [], []
    for entry in primary:
        poly = [
            row for row in polygon_rows if _candidate(entry, row["props"])
        ]
        points = [
            row for row in point_rows if _candidate(entry, row["props"])
        ]
        if len(poly) == 1 and poly[0]["valid"] and not poly[0]["empty"]:
            matched = poly[0]
            area = matched["area_epsg32643_km2_diagnostic"]
            matches.append({
                "official_name": entry["name"],
                "official_reference_area_km2": entry["area_km2"],
                "wdpa_name": matched["name"],
                "wdpa_site_id": matched["site_id"],
                "wdpa_objectid": matched["objectid"],
                "wdpa_designation": matched["designation"],
                "wdpa_diagnostic_area_km2": area,
                "wdpa_vs_official_area_pct_diagnostic": (
                    100 * (area - entry["area_km2"]) / entry["area_km2"]
                ) if area is not None and entry["area_km2"] > 0 else None,
                "statutory_boundary_verified": False,
            })
        else:
            unresolved.append({
                "official_name": entry["name"],
                "polygon_candidates": len(poly),
                "point_candidates_NOT_polygons": len(points),
                "polygon_candidate_names": [row["name"] for row in poly],
                "point_candidate_names": [row["name"] for row in points],
            })
    return {
        "polygon_features": len(polygon_rows),
        "point_features_NOT_polygon_boundaries": len(point_rows),
        "envelope_polygon_names": [row["name"] for row in polygon_rows],
        "envelope_point_names": [row["name"] for row in point_rows],
        "envelope_invalid_polygons": sum(not row["valid"] for row in polygon_rows),
        "official_designations_uniquely_matched": len(matches),
        "official_designations_unresolved": unresolved,
        "matches": matches,
    }


def run(root: Path, output: Path, raw_dir: Path) -> dict:
    config = yaml.safe_load((root / CONFIG).read_text())
    session = requests.Session()
    session.headers.update({
        "User-Agent": (
            "Kerala2040Research/1.0 "
            "(+https://github.com/abhijith-sivaprasadan/kerala2040)"
        )
    })
    try:
        points = fetch_layer(session, 0, raw_dir)
        polygons = fetch_layer(session, 1, raw_dir)
    finally:
        session.close()
    compared = classify(
        config["protected_areas"], polygons["features"], points["features"]
    )
    result = {
        "classification": (
            "KFD_register_WDPA_point_and_polygon_retrieval_audit_"
            "NOT_statutory_or_screening_ready"
        ),
        "reviewed_at_utc": datetime.now(UTC).replace(microsecond=0).isoformat(),
        "official_register_source": config["primary_register"],
        "secondary_source": config["secondary_geometry"],
        "query_envelope_wgs84": [74.75, 8.15, 77.55, 12.9],
        "query_is_Kerala_boundary_clip": False,
        "query_where": "1=1; counts and IDs scoped to envelope",
        "source_layers": [
            {key: value for key, value in layer.items() if key != "features"}
            for layer in (points, polygons)
        ],
        "official_core_designations_expected": len(config["protected_areas"]),
        **compared,
        "secondary_spatial_crosswalk_complete": (
            compared["official_designations_uniquely_matched"]
            == len(config["protected_areas"])
        ),
        "point_records_converted_to_polygons": False,
        "secondary_geometry_can_support_provisional_screening": False,
        "secondary_geometry_can_replace_KFD_statutory_boundaries": False,
        "reserve_forest_geometry_acquired": False,
        "eco_sensitive_zone_geometry_acquired": False,
        "legal_notification_geometry_linkage_verified": False,
        "eligible_area_sq_km": None,
        "capacity_ceiling_mw": None,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    print("WDPA_CROSSWALK_SUMMARY=" + json.dumps({
        "polygon_count": compared["polygon_features"],
        "point_count": compared["point_features_NOT_polygon_boundaries"],
        "matches": compared["official_designations_uniquely_matched"],
        "unresolved": len(compared["official_designations_unresolved"]),
        "polygon_names": compared["envelope_polygon_names"],
        "point_names": compared["envelope_point_names"],
        "screening_ready": False,
    }, separators=(",", ":")), flush=True)
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument(
        "--output", type=Path,
        default=Path("results/gis/kerala_protected_area_crosswalk.json")
    )
    parser.add_argument(
        "--raw-dir", type=Path, default=Path("results/gis/wdpa_raw")
    )
    args = parser.parse_args()
    run(args.root, args.output, args.raw_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
