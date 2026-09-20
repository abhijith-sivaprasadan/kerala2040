"""Geometry-repair primitives for invalid GSI susceptibility polygons."""

from __future__ import annotations

from typing import Any

from shapely.geometry import GeometryCollection, MultiPolygon, Polygon


def polygonal(value):
    """Keep only areal repair output; line/point debris is never silently modelled."""
    if value is None or value.is_empty:
        return MultiPolygon([])
    if isinstance(value, Polygon):
        return MultiPolygon([value])
    if isinstance(value, MultiPolygon):
        return value
    if isinstance(value, GeometryCollection):
        polygons = []
        for item in value.geoms:
            if isinstance(item, Polygon):
                polygons.append(item)
            elif isinstance(item, MultiPolygon):
                polygons.extend(item.geoms)
        return MultiPolygon(polygons)
    return MultiPolygon([])


def parts(value) -> int:
    if value is None or value.is_empty:
        return 0
    if isinstance(value, Polygon):
        return 1
    if isinstance(value, MultiPolygon):
        return len(value.geoms)
    return 0


def ratio(a: float, b: float) -> float | None:
    return None if b == 0 else a / b


def compare_feature(source, make_valid_geometry, buffer0_geometry) -> dict[str, Any]:
    """Quantify two repairs; source-area ratio is diagnostic because source is invalid."""
    source_area = float(source.area)
    mv_area = float(make_valid_geometry.area)
    b0_area = float(buffer0_geometry.area)
    area_scale = max(mv_area, b0_area)
    area_disagreement = (
        0.0 if area_scale == 0 else abs(mv_area - b0_area) / area_scale
    )
    mv_centroid = make_valid_geometry.centroid
    b0_centroid = buffer0_geometry.centroid
    centroid_shift = float(mv_centroid.distance(b0_centroid))
    mv_bounds = make_valid_geometry.bounds
    b0_bounds = buffer0_geometry.bounds
    bounds_max_abs_delta = max(
        abs(float(a) - float(b)) for a, b in zip(mv_bounds, b0_bounds, strict=True)
    )
    return {
        "source_computational_area_m2_invalid_geometry": source_area,
        "make_valid_area_m2": mv_area,
        "buffer0_area_m2": b0_area,
        "make_valid_vs_source_area_ratio": ratio(mv_area, source_area),
        "buffer0_vs_source_area_ratio": ratio(b0_area, source_area),
        "make_valid_vs_buffer0_area_ratio": ratio(mv_area, b0_area),
        "repair_relative_area_disagreement": area_disagreement,
        "repair_centroid_shift_m": centroid_shift,
        "repair_bounds_max_abs_delta_m": bounds_max_abs_delta,
        "make_valid_parts": parts(make_valid_geometry),
        "buffer0_parts": parts(buffer0_geometry),
        "part_count_difference": parts(make_valid_geometry) - parts(buffer0_geometry),
        "make_valid_valid": bool(make_valid_geometry.is_valid),
        "buffer0_valid": bool(buffer0_geometry.is_valid),
        "make_valid_empty": bool(make_valid_geometry.is_empty),
        "buffer0_empty": bool(buffer0_geometry.is_empty),
    }
