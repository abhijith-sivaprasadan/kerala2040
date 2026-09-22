"""Audit the already-clipped NIWE 150 m Kerala resource; optionally compare DSM slope.

This is a DESCRIPTIVE resource/terrain diagnostic, not a legal siting screen,
turbine yield, available area, model input or capacity calculation.
No original NIWE rows or raster pixels are published by this script.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

PINNED_CLIP_SHA256 = "364808dd40751bd5f3e131e86127dbdab73168d1830a682002de5a4c6fdd0dee"
PINNED_GLO90_SLOPE_SHA256 = "72551921c99eb563abe37c9502d4e4c592c3be667f31459296c90e48be9436f7"
EXPECTED_KERALA_ROWS = 200_692
FIELDS = (
    "Longitude (E)", "Latitude (N)", "Wind Speed (m/s)",
    "Weibull A (m/s)", "Weibull k", "Air Density (kg/m3)",
    "Wind Power Density (W/sq.m)",
)
SPEED_EDGES = (0, 3, 4, 5, 6, 7, 8, 10, float("inf"))
POWER_EDGES = (0, 50, 100, 200, 300, 500, 800, float("inf"))
SLOPE_EDGES = (0, 5, 10, 15, 20, 30, 45, 90.000001)
KERALA_BOUNDS = (74.86433401590513, 8.292707436852217,
                 77.41224235944739, 12.795602379977375)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(4 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def histogram(values: np.ndarray, edges: tuple[float, ...]) -> list[dict]:
    counts, _ = np.histogram(values, bins=np.asarray(edges))
    result = []
    for left, right, n in zip(edges[:-1], edges[1:], counts, strict=True):
        result.append({
            "minimum_inclusive": left,
            "maximum_exclusive": right if np.isfinite(right) else None,
            "point_centres": int(n),
        })
    return result


def stats(values: np.ndarray) -> dict:
    return {
        "minimum": float(np.min(values)),
        "p05": float(np.percentile(values, 5)),
        "median": float(np.median(values)),
        "p95": float(np.percentile(values, 95)),
        "maximum": float(np.max(values)),
    }


def threshold_diagnostics(speed: np.ndarray, slope: np.ndarray) -> list[dict]:
    """Sensitivity counts among centres with finite slope, never eligible sites."""
    if speed.shape != slope.shape:
        raise ValueError("Wind speed and slope sample lengths differ")
    valid = np.isfinite(slope)
    denominator = int(valid.sum())
    rows = []
    for minimum_speed in (5.0, 6.0, 7.0, 8.0):
        for maximum_slope in (5.0, 10.0, 15.0, 20.0):
            count = int(np.count_nonzero(
                valid & (speed >= minimum_speed) & (slope <= maximum_slope)
            ))
            rows.append({
                "minimum_150m_wind_speed_m_s_inclusive": minimum_speed,
                "maximum_DSM_surface_slope_degrees_inclusive": maximum_slope,
                "matching_point_centres": count,
                "percentage_of_slope_available_point_centres": (
                    round(100 * count / denominator, 3) if denominator else None
                ),
            })
    return rows


def render_private_maps(frame: pd.DataFrame, slope: np.ndarray | None,
                        out_dir: Path) -> dict:
    """Draw private descriptive point maps, never GIS exclusions or MW estimates."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    out_dir.mkdir(parents=True, exist_ok=True)
    lon = frame[FIELDS[0]].to_numpy(dtype="float64")
    lat = frame[FIELDS[1]].to_numpy(dtype="float64")
    definitions = [
        ("NIWE_150m_kerala_wind_speed_PRIVATE.png", "Wind Speed (m/s)", "m/s"),
        ("NIWE_150m_kerala_wind_density_PRIVATE.png",
         "Wind Power Density (W/sq.m)", "W/m²"),
    ]
    if slope is not None:
        if slope.shape != lon.shape:
            raise ValueError("Slope and wind point counts differ")
        definitions.append(("NIWE_150m_kerala_DSM_slope_PRIVATE.png", None, "degrees"))

    output = {}
    for name, field, unit in definitions:
        values = slope if field is None else frame[field].to_numpy(dtype="float64")
        assert values is not None
        finite = np.isfinite(values)
        fig, ax = plt.subplots(figsize=(7, 9))
        try:
            scatter = ax.scatter(
                lon[finite], lat[finite], c=values[finite], s=0.9,
                linewidths=0, rasterized=True,
            )
            ax.set_aspect("equal")
            ax.set_xlabel("Longitude (°E)")
            ax.set_ylabel("Latitude (°N)")
            ax.set_title("Kerala NWIC-clipped NIWE point centres: " + unit +
                         " · Descriptive only · NOT eligible area or capacity")
            fig.colorbar(scatter, ax=ax, label=unit, shrink=0.65)
            destination = out_dir / name
            fig.savefig(destination, dpi=160, bbox_inches="tight")
            output[name] = {"sha256": sha256(destination),
                            "mapped_finite_point_centres": int(finite.sum())}
        finally:
            plt.close(fig)
    return {"derived_maps_local_private_only": True,
            "public_redistribution_rights_verified": False,
            "files": output}


def read_clip(path: Path, expected_rows: int) -> pd.DataFrame:
    frame = pd.read_csv(path, compression="infer")
    if tuple(frame.columns) != FIELDS:
        raise ValueError(f"NIWE source columns/order differ: {tuple(frame.columns)!r}")
    if len(frame) != expected_rows:
        raise ValueError(f"Expected {expected_rows} clipped rows, got {len(frame)}")
    for name in FIELDS:
        frame[name] = pd.to_numeric(frame[name], errors="raise")
    numeric = frame.loc[:, FIELDS].to_numpy(dtype="float64")
    if not np.isfinite(numeric).all():
        raise ValueError("Non-finite NIWE coordinates or resource values")
    w, s, e, n = KERALA_BOUNDS
    if not (frame[FIELDS[0]].between(w, e).all()
            and frame[FIELDS[1]].between(s, n).all()):
        raise ValueError("Point outside Kerala boundary envelope; wrong source clip?")
    if frame.duplicated(subset=FIELDS[:2]).any():
        raise ValueError("Duplicate NIWE point coordinates")
    if (frame["Wind Speed (m/s)"] <= 0).any():
        raise ValueError("Non-positive source wind speed")
    if (frame["Weibull A (m/s)"] <= 0).any() or (frame["Weibull k"] <= 0).any():
        raise ValueError("Non-positive Weibull parameter")
    if (frame["Air Density (kg/m3)"] <= 0).any():
        raise ValueError("Non-positive source air density")
    if (frame["Wind Power Density (W/sq.m)"] < 0).any():
        raise ValueError("Negative wind power density")
    return frame


def sample_slope(slope_path: Path, frame: pd.DataFrame) -> np.ndarray:
    """Sample a user-supplied degree-slope raster, preserving missing coverage."""
    import rasterio
    from pyproj import Transformer

    with rasterio.open(slope_path) as src:
        if src.crs is None or src.count != 1:
            raise ValueError("Slope raster must have a CRS and exactly one band")
        if src.width < 1 or src.height < 1:
            raise ValueError("Empty slope raster")
        transform = Transformer.from_crs("EPSG:4326", src.crs, always_xy=True)
        xs, ys = transform.transform(
            frame[FIELDS[0]].to_numpy(), frame[FIELDS[1]].to_numpy()
        )
        # Read the pinned 90 m DSM slope grid once, then index all points.
        # Rasterio.sample incurs per-point window IO and is prohibitively slow
        # for the ~200,000 Kerala NIWE point centres.
        inverse = ~src.transform
        cols = np.floor(inverse.a * xs + inverse.b * ys + inverse.c).astype("int64")
        rows = np.floor(inverse.d * xs + inverse.e * ys + inverse.f).astype("int64")
        in_grid = (
            (cols >= 0) & (cols < src.width) &
            (rows >= 0) & (rows < src.height)
        )
        samples = np.full(len(frame), np.nan, dtype="float64")
        grid = src.read(1, masked=True)
        samples[in_grid] = np.ma.filled(
            grid[rows[in_grid], cols[in_grid]], np.nan
        )
    samples[~np.isfinite(samples)] = np.nan
    if np.any((samples[np.isfinite(samples)] < 0)
              | (samples[np.isfinite(samples)] > 90)):
        raise ValueError("Slope values outside 0..90 degrees: verify units and raster")
    return samples


def analyze(
    clip: Path, *, expected_rows: int = EXPECTED_KERALA_ROWS,
    allow_repacked_clip: bool = False, slope: Path | None = None,
    allow_unpinned_slope: bool = False,
) -> dict:
    source_hash = sha256(clip)
    hash_match = source_hash == PINNED_CLIP_SHA256
    if not hash_match and not allow_repacked_clip:
        raise ValueError(
            "Clip SHA256 differs from the documented 2026-09-22 compressed "
            "clip. Pass --allow-repacked-clip only after independent source QA."
        )
    frame = read_clip(clip, expected_rows)
    speed = frame["Wind Speed (m/s)"].to_numpy(dtype="float64")
    power = frame["Wind Power Density (W/sq.m)"].to_numpy(dtype="float64")
    result = {
        "classification": "NIWE_150M_KERALA_DESCRIPTIVE_RESOURCE_TERRAIN_NOT_CAPACITY",
        "source": "NIWE original 150 m seven-column national CSV; exact NWIC Kerala clip",
        "clip_sha256": source_hash,
        "matches_documented_2026_09_22_compressed_clip": hash_match,
        "non_pinned_clip_explicitly_allowed": not hash_match and allow_repacked_clip,
        "point_centres": len(frame),
        "source_height_m_agl": 150,
        "source_nominal_horizontal_grid_m": 500,
        "source_crs_independently_verified_by_this_run": False,
        "wind_speed_m_s": stats(speed),
        "wind_speed_classes_m_s": histogram(speed, SPEED_EDGES),
        "wind_power_density_w_m2": stats(power),
        "wind_power_density_classes_w_m2": histogram(power, POWER_EDGES),
        "weibull_a_m_s": stats(frame["Weibull A (m/s)"].to_numpy()),
        "weibull_k": stats(frame["Weibull k"].to_numpy()),
        "air_density_kg_m3": stats(frame["Air Density (kg/m3)"].to_numpy()),
        "terrain": None,
        "legal_eligibility_verified": False,
        "hourly_generation_validated": False,
        "candidate_area_km2": None,
        "feasible_capacity_MW": None,
        "model_admitted": False,
    }
    if slope is not None:
        slope_hash = sha256(slope)
        matches_pinned_slope = slope_hash == PINNED_GLO90_SLOPE_SHA256
        if not matches_pinned_slope and not allow_unpinned_slope:
            raise ValueError(
                "Slope SHA256 differs from recovered 2026-09-20 GLO-90 "
                "slope TIFF. Use --allow-unpinned-slope ONLY after independent "
                "CRS, slope-unit and provenance QA."
            )
        degree = sample_slope(slope, frame)
        finite = np.isfinite(degree)
        joint = np.histogram2d(
            speed[finite], degree[finite], bins=[SPEED_EDGES, SLOPE_EDGES],
        )[0].astype(int).tolist()
        result["terrain"] = {
            "raster_sha256": slope_hash,
            "matches_verified_2026_09_20_GLO90_slope_tiff": matches_pinned_slope,
            "non_pinned_slope_explicitly_allowed": (
                not matches_pinned_slope and allow_unpinned_slope
            ),
            "assumed_unit": "degrees; caller must independently verify source units",
            "surface_type": "source-defined; GLO-90 DSM is not a bare-earth DTM",
            "available_point_centres": int(finite.sum()),
            "missing_point_centres": int((~finite).sum()),
            "slope_degrees": stats(degree[finite]) if finite.any() else None,
            "slope_classes_degrees": histogram(degree[finite], SLOPE_EDGES),
            "joint_speed_by_slope_point_counts": joint,
            "joint_speed_edges_m_s": list(SPEED_EDGES[:-1]) + [None],
            "joint_slope_edges_degrees": list(SLOPE_EDGES),
            "wind_speed_slope_threshold_sensitivity": threshold_diagnostics(
                speed, degree
            ),
            "threshold_sensitivity_interpretation": (
                "Physical descriptive combinations only: not forest/wetland "
                "rights, wind turbine yield, viable area, layout or legal eligibility."
            ),
            "not_a_technology_specific_setback_or_legal_screen": True,
        }
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--niwe-clip", type=Path, required=True,
                        help="Existing NIWE_150m_Kerala_NWIC_point_centres.csv.gz")
    parser.add_argument("--out", type=Path, required=True,
                        help="Local PRIVATE or public-safe aggregate JSON; no raw rows")
    parser.add_argument("--slope-degrees", type=Path,
                        help="Optional independent CRS-aware raster; verify units first")
    parser.add_argument("--allow-unpinned-slope", action="store_true",
                        help="Use another degree-slope raster ONLY after independent QA")
    parser.add_argument("--map-dir", type=Path,
                        help="Optional LOCAL PRIVATE PNG point maps; check NIWE licence "
                             "before public redistribution")
    parser.add_argument("--allow-repacked-clip", action="store_true",
                        help="Explicitly accept non-pinned compressed bytes")
    args = parser.parse_args()
    if args.out.resolve() == args.niwe_clip.resolve():
        parser.error("Do not overwrite source clip")
    if args.map_dir and args.map_dir.resolve() == args.niwe_clip.parent.resolve():
        parser.error("Choose a separate private map directory, not the source directory")
    report = analyze(
        args.niwe_clip, allow_repacked_clip=args.allow_repacked_clip,
        slope=args.slope_degrees, allow_unpinned_slope=args.allow_unpinned_slope,
    )
    if args.map_dir is not None:
        # The analysis verifies the compressed hash and row count before map rendering.
        frame = read_clip(args.niwe_clip, report["point_centres"])
        degree = sample_slope(args.slope_degrees, frame) if args.slope_degrees else None
        report["private_maps"] = render_private_maps(frame, degree, args.map_dir)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n",
                        encoding="utf-8")
    print(f"NIWE resource QA: {report['point_centres']} point centres; "
          f"terrain supplied: {args.slope_degrees is not None}; model admitted: false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
