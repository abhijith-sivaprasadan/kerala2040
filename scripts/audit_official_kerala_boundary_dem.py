"""Acquire government state polygons and screen GLO90 missing-tile footprints.

This is a *source-availability and coarse boundary intersection* check, not a
legal or pixel-wise completeness certificate, slope screen, or siting map.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import zipfile
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import urlparse

import requests
from pyproj import Transformer
from shapely.geometry import box, shape
from shapely.ops import transform, unary_union

DEM_MANIFEST = "data/evidence/gis/copernicus_glo90_envelope_2026_09_20.json"
DATASET = "https://nwdp.nwic.gov.in/dataset/state-boundary"
RESOURCE_ID = "f039e721-132c-4a24-9e5e-07af03064b4d"
CKAN_HOSTS = ("https://nwdp.nwic.gov.in", "https://www.nwdp.nwic.gov.in")
SOI = "https://onlinemaps.surveyofindia.gov.in/Digital_Products.aspx"
LIMIT_BYTES = 60_000_000


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _api_resources(session: requests.Session) -> tuple[list[dict], list[str]]:
    resources = []
    failures = []
    for host in CKAN_HOSTS:
        for action, args in (
            ("package_show", {"id": "state-boundary"}),
            ("resource_show", {"id": RESOURCE_ID}),
        ):
            url = f"{host}/api/3/action/{action}"
            try:
                response = session.get(url, params=args, timeout=(12, 35))
                response.raise_for_status()
                data = response.json()
                if data.get("success") is not True:
                    raise ValueError("CKAN success false")
                obj = data["result"]
                discovered = obj.get("resources", []) if action == "package_show" else [obj]
                resources.extend(discovered)
            except (requests.RequestException, ValueError, KeyError, TypeError) as exc:
                failures.append(f"{url}: {type(exc).__name__}: {str(exc)[:140]}")
    return resources, failures


def _eligible_resource(row: dict) -> bool:
    title = str(row.get("name") or row.get("description") or "").lower()
    link = str(row.get("url") or "")
    fmt = str(row.get("format") or "").lower()
    return bool(link.startswith("https://") and (
        "geojson" in title or "geojson" in fmt or "geojson" in link.lower()
    ) and ("state" in title or "state" in link.lower()))


def _safe_download(session: requests.Session, url: str) -> tuple[bytes, str]:
    parsed = urlparse(url)
    if parsed.scheme != "https":
        raise ValueError("Source file URL not HTTPS")
    total = 0
    chunks = []
    with session.get(url, stream=True, timeout=(15, 90)) as response:
        response.raise_for_status()
        actual = urlparse(response.url)
        if actual.scheme != "https":
            raise ValueError("Source download redirected away from HTTPS")
        declared = int(response.headers.get("Content-Length", "0") or "0")
        if declared > LIMIT_BYTES:
            raise ValueError("Original archive exceeds size cap")
        for chunk in response.iter_content(1024 * 1024):
            if not chunk:
                continue
            total += len(chunk)
            if total > LIMIT_BYTES:
                raise ValueError("Original archive exceeds streamed size cap")
            chunks.append(chunk)
        content_type = response.headers.get("Content-Type", "").lower()
        if "text/html" in content_type:
            raise ValueError("HTML landing page, not source GeoJSON archive")
        return b"".join(chunks), response.url


def _parse_geojson(original: bytes) -> dict:
    if zipfile.is_zipfile(io.BytesIO(original)):
        with zipfile.ZipFile(io.BytesIO(original)) as archive:
            files = [x for x in archive.infolist()
                     if x.filename.lower().endswith((".geojson", ".json"))
                     and not x.is_dir()]
            if len(files) != 1 or len(archive.infolist()) > 500:
                raise ValueError("Expected one GeoJSON source inside safe ZIP")
            member = files[0]
            if member.file_size > LIMIT_BYTES or member.filename.startswith(("/", "\\")) or ".." in Path(member.filename).parts:
                raise ValueError("Unsafe or excessive original archive member")
            return json.loads(archive.read(member))
    return json.loads(original)


def _kerala_feature(fc: dict):
    if fc.get("type") != "FeatureCollection":
        raise ValueError("State source is not a GeoJSON FeatureCollection")
    if fc.get("crs") and "4326" not in json.dumps(fc["crs"]):
        raise ValueError("Unknown non-WGS84 GeoJSON CRS")
    matches = []
    for feat in fc.get("features", []):
        props = feat.get("properties") or {}
        if any(str(value).strip().casefold() == "kerala" for value in props.values()):
            matches.append(feat)
    if len(matches) != 1:
        raise ValueError(f"Expected exactly one Kerala polygon, found {len(matches)}")
    geom = shape(matches[0]["geometry"])
    if geom.is_empty or not geom.is_valid or geom.geom_type not in ("Polygon", "MultiPolygon"):
        raise ValueError("Kerala source polygon not valid polygonal geometry")
    west, south, east, north = geom.bounds
    if not (73.5 <= west <= 78 and 7.5 <= south <= 10.5 and 75 <= east <= 80
            and 11 <= north <= 14):
        raise ValueError("Kerala administrative polygon bounding extent implausible")
    projected = transform(
        Transformer.from_crs("EPSG:4326", "EPSG:32643", always_xy=True).transform,
        geom,
    )
    area_sq_km = float(projected.area / 1_000_000)
    if not 25_000 < area_sq_km < 55_000:
        raise ValueError("Kerala administrative polygon area outside broad QA bounds")
    return geom, matches[0].get("properties", {}), area_sq_km


def inspect(root: Path, output: Path, raw_dir: Path) -> dict:
    baseline = json.loads((root / DEM_MANIFEST).read_text(encoding="utf-8"))
    if baseline.get("requested_envelope_tiles") != 20 or baseline.get("actual_original_tiles_acquired") != 14:
        raise ValueError("Copernicus original tile evidence changed; re-audit first")
    missing = [r for r in baseline["original_tiles_and_hashes"]
               if r["status"] == "tile_not_published_http_404"]
    if len(missing) != 6:
        raise ValueError("Original GLO90 missing tile list changed")
    result = {
        "classification": "official_boundary_download_probe_NOT_land_eligibility",
        "reviewed_at_utc": datetime.now(UTC).replace(microsecond=0).isoformat(),
        "official_boundary_candidate": DATASET,
        "nwic_resource_page": f"{DATASET}/resource/{RESOURCE_ID}",
        "survey_of_india_alternative": SOI,
        "source_data_producer_portal_claim": "GSI, via National Water Data Portal; provenance not independently checked",
        "source_license_portal_claim": "Other (Open); public derivative rights not independently assessed",
        "dem_source_evidence": DEM_MANIFEST,
        "downloaded_official_boundary": False,
        "kerala_boundary_validated_structurally": False,
        "missing_dem_envelope_tiles": len(missing),
        "missing_source_tile_intersection_with_official_kerala": None,
        "pixel_level_kerala_dsm_completeness_verified": False,
        "authoritative_survey_boundary_equivalence_verified": False,
        "wetland_or_forest_boundaries_verified": False,
        "ecological_capacity_ceiling_ready": False,
        "eligible_area_sq_km": None,
        "capacity_ceiling_mw": None,
        "probe_errors": [],
    }
    session = requests.Session()
    session.headers.update({"User-Agent": "Kerala2040Research/1.0 (+https://github.com/abhijith-sivaprasadan/kerala2040)"})
    try:
        found, errors = _api_resources(session)
        result["probe_errors"].extend(errors)
        candidates = [row for row in found if _eligible_resource(row)]
        result["resource_metadata_candidates"] = [
            {"id": r.get("id"), "name": r.get("name"), "format": r.get("format"),
             "url": r.get("url")} for r in candidates
        ]
        for row in candidates:
            try:
                original, resolved_url = _safe_download(session, str(row["url"]))
                fc = _parse_geojson(original)
                kerala, properties, area = _kerala_feature(fc)
                raw_dir.mkdir(parents=True, exist_ok=True)
                file = raw_dir / "nwic_original_state_boundary_download"
                file.write_bytes(original)
                to_meters = Transformer.from_crs("EPSG:4326", "EPSG:32643", always_xy=True).transform
                checks = []
                for source in baseline["original_tiles_and_hashes"]:
                    footprint = box(
                        float(source["longitude"]), float(source["latitude"]),
                        float(source["longitude"]) + 1, float(source["latitude"]) + 1,
                    )
                    intersection = kerala.intersection(footprint)
                    overlap_km2 = (float(transform(to_meters, intersection).area / 1e6)
                                   if not intersection.is_empty else 0.0)
                    checks.append({
                        "latitude": source["latitude"], "longitude": source["longitude"],
                        "source_status": source["status"],
                        "boundary_intersection_km2_approx": overlap_km2,
                        "boundary_intersects_missing_tile": (
                            source["status"] == "tile_not_published_http_404"
                            and overlap_km2 > 0
                        ),
                    })
                missing_intersections = [v for v in checks if v["boundary_intersects_missing_tile"]]
                result.update({
                    "downloaded_official_boundary": True,
                    "kerala_boundary_validated_structurally": True,
                    "original_source_url": resolved_url,
                    "original_sha256": digest(original),
                    "original_bytes": len(original),
                    "feature_collection_count": len(fc["features"]),
                    "kerala_source_properties": properties,
                    "kerala_bounds_wgs84": list(kerala.bounds),
                    "kerala_polygon_area_sq_km_approx_NOT_land_eligibility": area,
                    "source_crs": "GeoJSON WGS84/EPSG:4326",
                    "source_boundary_simplification_scale_unknown": True,
                    "source_tile_footprint_intersections": checks,
                    "missing_source_tile_intersection_with_official_kerala": {
                        "count": len(missing_intersections),
                        "tiles": missing_intersections,
                        "approximate_km2": sum(x["boundary_intersection_km2_approx"] for x in missing_intersections),
                    },
                    "original_source_redistribution_licence_review_pending": True,
                })
                break
            except (requests.RequestException, ValueError, KeyError, TypeError, OSError) as exc:
                result["probe_errors"].append(
                    f"{row.get('url')}: {type(exc).__name__}: {str(exc)[:220]}"
                )
    finally:
        session.close()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--output", type=Path, default=Path("results/gis/official_boundary_dem_source_intersections.json"))
    parser.add_argument("--raw-dir", type=Path, default=Path("results/gis/nwic_original"))
    args = parser.parse_args()
    r = inspect(args.root, args.output, args.raw_dir)
    print(json.dumps({
        "classification": r["classification"],
        "downloaded_official_boundary": r["downloaded_official_boundary"],
        "missing_dem_tile_intersections": r["missing_source_tile_intersection_with_official_kerala"],
        "probe_errors": r["probe_errors"],
        "artifact": str(args.output),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
