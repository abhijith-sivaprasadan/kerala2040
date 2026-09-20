"""Cross-check official Kerala protected-area register against current WDPA polygons.

The Kerala Forest Department list is the primary legal/name register here.
WDPA geometry is a secondary spatial reference, not a statutory boundary source.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import UTC, datetime
from pathlib import Path

import geopandas as gpd
import requests
import yaml

CONFIG = Path("configs/kerala_protected_area_crosswalk_2026.yaml")
QUERY_URL = (
    "https://data-gis.unep-wcmc.org/server/rest/services/"
    "ProtectedSites/The_World_Database_of_Protected_Areas/MapServer/1/query"
)
KERALA_ENVELOPE = "74.75,8.15,77.55,12.9"


def norm(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", value.casefold())


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _query(session: requests.Session, raw: Path) -> dict:
    params = {
        "where": "iso3='IND'",
        "geometry": KERALA_ENVELOPE,
        "geometryType": "esriGeometryEnvelope",
        "inSR": "4326",
        "spatialRel": "esriSpatialRelIntersects",
        "outFields": "*",
        "returnGeometry": "true",
        "outSR": "4326",
        "f": "geojson",
    }
    response = session.get(QUERY_URL, params=params, timeout=(20, 120))
    response.raise_for_status()
    if "json" not in response.headers.get("content-type", "").lower():
        raise ValueError("WDPA query did not return JSON")
    raw.parent.mkdir(parents=True, exist_ok=True)
    raw.write_bytes(response.content)
    data = response.json()
    if data.get("type") != "FeatureCollection":
        raise ValueError("WDPA response is not GeoJSON FeatureCollection")
    return data


def _candidate_names(props: dict) -> list[str]:
    return [
        str(props.get("name_eng") or ""),
        str(props.get("name") or ""),
    ]


def _matches(entry: dict, props: dict) -> bool:
    targets = {norm(entry["name"]), *(norm(x) for x in entry.get("aliases", []))}
    names = {norm(x) for x in _candidate_names(props) if x}
    # Exact normalized names first, then a conservative contained alias.
    if targets & names:
        return True
    return any(len(t) >= 7 and (t in n or n in t) for t in targets for n in names if len(n) >= 7)


def _area_km2(gdf: gpd.GeoDataFrame) -> list[float]:
    # Use Kerala UTM zone for a diagnostic only; WDPA geometry is not statutory truth.
    projected = gdf.to_crs("EPSG:32643")
    return [float(a / 1_000_000) for a in projected.geometry.area]


def run(root: Path, output: Path, raw: Path) -> dict:
    config = yaml.safe_load((root / CONFIG).read_text())
    primary = config["protected_areas"]
    if len(primary) != 25:
        raise ValueError("Expected 25 core Kerala protected-area designations")
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Kerala2040Research/1.0 (+https://github.com/abhijith-sivaprasadan/kerala2040)"
    })
    try:
        fc = _query(session, raw)
    finally:
        session.close()
    frame = gpd.GeoDataFrame.from_features(fc["features"], crs="EPSG:4326")
    if frame.empty:
        raise ValueError("No WDPA polygon features returned for Kerala envelope")
    if "iso3" not in frame or not (frame["iso3"] == "IND").all():
        raise ValueError("WDPA query contains non-India polygons")
    if frame.geometry.isna().any() or frame.geometry.is_empty.any():
        raise ValueError("WDPA returned null/empty polygon")
    if not set(frame.geometry.geom_type) <= {"Polygon", "MultiPolygon"}:
        raise ValueError("Unexpected WDPA geometry types")

    diagnostic_areas = _area_km2(frame)
    matches = []
    unmatched = []
    used_indexes: set[int] = set()
    for entry in primary:
        candidates = []
        for idx, row in frame.iterrows():
            props = row.drop(labels=[frame.geometry.name]).to_dict()
            if _matches(entry, props):
                candidates.append((idx, props))
        if len(candidates) == 1:
            idx, props = candidates[0]
            used_indexes.add(int(idx))
            reported = float(entry["area_km2"])
            wdpa_reported = props.get("rep_area")
            wdpa_gis = props.get("gis_area")
            geometry_area = diagnostic_areas[frame.index.get_loc(idx)]
            matches.append({
                "official_name": entry["name"],
                "official_type": entry["type"],
                "official_reported_area_km2": reported,
                "wdpa_name": props.get("name_eng") or props.get("name"),
                "wdpa_site_id": props.get("site_id"),
                "wdpa_designation": props.get("desig_eng") or props.get("desig"),
                "wdpa_status": props.get("status"),
                "wdpa_status_year": props.get("status_yr"),
                "wdpa_management_authority": props.get("mang_auth"),
                "wdpa_reported_area_km2": wdpa_reported,
                "wdpa_gis_area_km2": wdpa_gis,
                "diagnostic_geometry_area_epsg32643_km2": geometry_area,
                "geometry_valid": bool(frame.loc[idx].geometry.is_valid),
                "area_difference_vs_official_pct": (
                    100 * (geometry_area - reported) / reported if reported > 0 else None
                ),
                "statutory_boundary_verified": False,
            })
        else:
            unmatched.append({
                "official_name": entry["name"],
                "candidate_count": len(candidates),
                "candidate_names": [
                    props.get("name_eng") or props.get("name") for _, props in candidates
                ],
            })

    matched_frame = frame.loc[sorted(used_indexes)] if used_indexes else frame.iloc[0:0]
    invalid = int((~matched_frame.geometry.is_valid).sum()) if not matched_frame.empty else 0
    duplicate_site_ids = (
        int(matched_frame["site_id"].duplicated().sum())
        if not matched_frame.empty and "site_id" in matched_frame else 0
    )
    result = {
        "classification": "official_KFD_register_crosschecked_to_WDPA_secondary_geometry_NOT_statutory_boundary",
        "reviewed_at_utc": datetime.now(UTC).replace(microsecond=0).isoformat(),
        "primary_register": config["primary_register"],
        "secondary_geometry": config["secondary_geometry"],
        "query_url": QUERY_URL,
        "query_envelope_wgs84": [74.75, 8.15, 77.55, 12.9],
        "raw_geojson_sha256": sha256(raw),
        "raw_geojson_bytes": raw.stat().st_size,
        "wdpa_features_returned_in_envelope": len(frame),
        "official_core_designations_expected": len(primary),
        "official_designations_uniquely_matched": len(matches),
        "official_designations_unresolved": unmatched,
        "matched_polygons_invalid": invalid,
        "duplicate_matched_site_ids": duplicate_site_ids,
        "matches": matches,
        "tiger_reserves_kept_as_overlapping_designations": config["overlapping_designations"],
        "secondary_geometry_can_support_provisional_screening": (
            len(matches) == len(primary) and invalid == 0 and duplicate_site_ids == 0
        ),
        "secondary_geometry_can_replace_KFD_statutory_boundaries": False,
        "reserve_forest_geometry_acquired": False,
        "eco_sensitive_zone_geometry_acquired": False,
        "legal_notification_geometry_linkage_verified": False,
        "eligible_area_sq_km": None,
        "capacity_ceiling_mw": None,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    print(json.dumps({
        "wdpa_features_returned": len(frame),
        "official_expected": len(primary),
        "unique_matches": len(matches),
        "unresolved": len(unmatched),
        "invalid_matched": invalid,
        "secondary_screening_candidate": result[
            "secondary_geometry_can_support_provisional_screening"
        ],
    }, indent=2))
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument(
        "--output", type=Path,
        default=Path("results/gis/kerala_protected_area_crosswalk.json"),
    )
    parser.add_argument(
        "--raw", type=Path,
        default=Path("results/gis/wdpa_kerala_envelope_raw.geojson"),
    )
    args = parser.parse_args()
    run(args.root, args.output, args.raw)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
