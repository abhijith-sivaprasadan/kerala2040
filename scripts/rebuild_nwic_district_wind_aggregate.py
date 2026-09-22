"""Rebuild private NIWE × NWIC district aggregates without publishing source geometry.

Run with the original NWIC national district ZIP, deterministic private NIWE
Kerala clip and original-derived GLO-90 degree-slope TIFF. No raw polygons or
NIWE point coordinates are written. Counts are descriptive, never eligible MW.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import zipfile
from pathlib import Path

import numpy as np
from audit_kerala_niwe_resource import (
    FIELDS,
    PINNED_GLO90_SLOPE_SHA256,
    read_clip,
    sample_slope,
    stats,
)
from pyproj import Transformer
from shapely import contains_xy, intersects_xy, prepare
from shapely.geometry import shape
from shapely.ops import transform

ZIP_SHA256 = "44c734cc72139f2447dcebfe2791cac862dc5ba265e158912d797cf3410d5c37"
MEMBER = "district_nwic.GeoJSON"
MEMBER_SHA256 = "2b27a478e24d8c51b0655e74ce3f4f880e75c752e4597550d6fc925ed06ac201"
CLIP_SHA256 = "dd9d00e67da0dac3a9258daad18c35f71075815f7b64cea4b290a36c6e9b9634"
EXPECTED = 200_692
SPEEDS = (5, 6, 7, 8)
SLOPES = (5, 10, 15, 20)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for block in iter(lambda: file.read(4 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def source_districts(source_zip: Path) -> dict:
    if sha256(source_zip) != ZIP_SHA256:
        raise ValueError("NWIC original district ZIP is not the pinned source")
    with zipfile.ZipFile(source_zip) as archive:
        raw = archive.read(MEMBER)
    if hashlib.sha256(raw).hexdigest() != MEMBER_SHA256:
        raise ValueError("NWIC original district GeoJSON differs from pinned member")
    source = json.loads(raw)
    if "7755" not in json.dumps(source.get("crs")):
        raise ValueError("NWIC source CRS declaration is not EPSG:7755")
    features = source["features"]
    if len(features) != 733:
        raise ValueError("NWIC national district count changed")
    kerala = [feature for feature in features
              if feature.get("properties", {}).get("state_name") == "Kerala"]
    if len(kerala) != 14:
        raise ValueError("Expected exactly 14 Kerala features by state_name")
    converter = Transformer.from_crs(7755, 4326, always_xy=True).transform
    districts = {}
    for feature in kerala:
        name = feature["properties"]["district"]
        if name in districts or feature.get("geometry") is None:
            raise ValueError("Duplicate district or missing source geometry")
        polygon = shape(feature["geometry"])
        if polygon.is_empty or not polygon.is_valid:
            raise ValueError(f"Invalid NWIC source geometry: {name}")
        polygon = transform(converter, polygon)
        if polygon.is_empty or not polygon.is_valid:
            raise ValueError(f"Invalid reprojected NWIC geometry: {name}")
        prepare(polygon)
        districts[name] = polygon
    return dict(sorted(districts.items()))


def matrix(speed: np.ndarray, slope: np.ndarray) -> list[list[int]]:
    finite = np.isfinite(slope)
    return [
        [int(np.count_nonzero(finite & (speed >= minimum)
                              & (slope <= maximum)))
         for maximum in SLOPES]
        for minimum in SPEEDS
    ]


def run(source_zip: Path, clip: Path, raster: Path, out: Path,
        statewide: Path, lris_aggregate: Path | None = None) -> dict:
    if sha256(clip) != CLIP_SHA256:
        raise ValueError("NIWE deterministic private clip SHA256 differs")
    if sha256(raster) != PINNED_GLO90_SLOPE_SHA256:
        raise ValueError("GLO-90 original-derived slope TIFF SHA256 differs")
    polygons = source_districts(source_zip)
    frame = read_clip(clip, EXPECTED)
    degree = sample_slope(raster, frame)
    speed = frame["Wind Speed (m/s)"].to_numpy(dtype="float64")
    longitude = frame[FIELDS[0]].to_numpy(dtype="float64")
    latitude = frame[FIELDS[1]].to_numpy(dtype="float64")
    assignment = np.full(EXPECTED, -1, dtype="int16")
    membership = np.zeros(EXPECTED, dtype="uint8")
    names = tuple(polygons)
    for index, district in enumerate(names):
        polygon = polygons[district]
        w, south, east, north = polygon.bounds
        inside_box = np.flatnonzero(
            (longitude >= w) & (longitude <= east)
            & (latitude >= south) & (latitude <= north)
        )
        hits = inside_box[contains_xy(
            polygon, longitude[inside_box], latitude[inside_box]
        )]
        assignment[hits] = index
        membership[hits] += 1
    # Only use intersects for points on an actual district border.
    misses = np.flatnonzero(membership == 0)
    for index, district in enumerate(names):
        polygon = polygons[district]
        w, south, east, north = polygon.bounds
        candidate = misses[
            (longitude[misses] >= w) & (longitude[misses] <= east)
            & (latitude[misses] >= south) & (latitude[misses] <= north)
        ]
        hits = candidate[intersects_xy(
            polygon, longitude[candidate], latitude[candidate]
        )]
        assignment[hits] = index
        membership[hits] += 1
    if not np.all(membership == 1):
        raise ValueError(
            f"Partition failed: unmatched={(membership == 0).sum()}, "
            f"multiply assigned={(membership > 1).sum()}"
        )
    if not np.isfinite(speed).all():
        raise ValueError("Nonfinite source wind speed")
    reference = json.loads(statewide.read_text(encoding="utf8"))
    if reference["Kerala_point_centres"] != EXPECTED:
        raise ValueError("Statewide reference population disagrees")
    lris = None
    if lris_aggregate:
        prior = json.loads(lris_aggregate.read_text(encoding="utf8"))
        lris = {r["district"]: r["niwe_resource_point_centres"]
                for r in prior["districts"]}
    rows = []
    for index, name in enumerate(names):
        selected = assignment == index
        speeds = speed[selected]
        slopes = degree[selected]
        finite = np.isfinite(slopes)
        record = {
            "district": name,
            "point_centres": int(selected.sum()),
            "slope_finite": int(finite.sum()),
            "slope_missing": int((~finite).sum()),
            "wind_speed_median_m_s": round(stats(speeds)["median"], 4),
            "wind_speed_p95_m_s": round(stats(speeds)["p95"], 4),
            "slope_median_degrees": round(stats(slopes[finite])["median"], 4),
            "delta_point_centres_vs_LRIS": (
                int(selected.sum()) - lris[name] if lris else None
            ),
            "threshold_matrix": matrix(speeds, slopes),
        }
        rows.append(record)
    total_matrix = matrix(speed, degree)
    checks = {
        "districts": len(rows) == 14,
        "points": sum(r["point_centres"] for r in rows) == EXPECTED,
        "slope_finite": sum(r["slope_finite"] for r in rows)
        == reference["slope"]["finite_point_centres"] == 199_853,
        "slope_missing": sum(r["slope_missing"] for r in rows)
        == reference["slope"]["missing_point_centres"] == 839,
        "matrix": [
            [sum(r["threshold_matrix"][i][j] for r in rows)
             for j in range(4)] for i in range(4)
        ] == total_matrix == reference["physical_threshold_sensitivity"][
            "matching_point_centre_counts_in_row_column_order"
        ],
        "LRIS_deltas": lris is None or sum(
            r["delta_point_centres_vs_LRIS"] for r in rows
        ) == 330,
    }
    if not all(checks.values()):
        raise ValueError(f"NWIC district aggregation failed QA: {checks}")
    report = {
        "classification": "NIWE_NWIC_14_DISTRICT_DESCRIPTIVE_POINT_PARTITION_NOT_CAPACITY",
        "NWIC_source_zip_sha256": ZIP_SHA256,
        "NWIC_member_sha256": MEMBER_SHA256,
        "private_niwe_clip_sha256": CLIP_SHA256,
        "private_DSM_slope_sha256": PINNED_GLO90_SLOPE_SHA256,
        "point_centres": EXPECTED,
        "uniquely_assigned": EXPECTED,
        "unassigned": 0,
        "ambiguous": 0,
        "slope_finite": 199_853,
        "slope_missing": 839,
        "districts": rows,
        "checks": checks,
        "source_reuse_rights_verified": False,
        "legal_land_exclusions_verified": False,
        "eligible_area_km2": None,
        "feasible_capacity_MW": None,
        "hourly_generation_validated": False,
        "model_admitted": False,
        "point_rows_and_polygon_coordinates_written": False,
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n",
                   encoding="utf8")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--nwic-district-zip", type=Path, required=True)
    parser.add_argument("--niwe-clip", type=Path, required=True)
    parser.add_argument("--slope-degrees", type=Path, required=True)
    parser.add_argument("--statewide-reference", type=Path, required=True)
    parser.add_argument("--historic-lris-aggregate", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    result = run(
        args.nwic_district_zip, args.niwe_clip, args.slope_degrees,
        args.out, args.statewide_reference, args.historic_lris_aggregate,
    )
    print(json.dumps({
        "districts": len(result["districts"]),
        "uniquely_assigned": result["uniquely_assigned"],
        "unassigned": result["unassigned"],
        "slope_finite": result["slope_finite"],
        "checks": result["checks"],
        "model_admitted": False,
    }, indent=2))
