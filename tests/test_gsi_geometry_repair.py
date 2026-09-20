"""Controlled repair comparison must preserve classes and remain non-legal."""

from __future__ import annotations

from shapely.geometry import GeometryCollection, LineString, MultiPolygon, Polygon

from kerala2040.gsi_repair import compare_feature, parts, polygonal


def test_polygonal_drops_non_areal_make_valid_debris():
    value = GeometryCollection([
        Polygon([(0, 0), (2, 0), (2, 2), (0, 2), (0, 0)]),
        LineString([(0, 0), (2, 2)]),
    ])
    result = polygonal(value)
    assert isinstance(result, MultiPolygon)
    assert parts(result) == 1
    assert result.area == 4


def test_two_repairs_of_self_intersection_are_compared_not_assumed_equal():
    source = Polygon([(0, 0), (2, 2), (0, 2), (2, 0), (0, 0)])
    from shapely import make_valid

    mv = polygonal(make_valid(source))
    b0 = polygonal(source.buffer(0))
    result = compare_feature(source, mv, b0)
    assert result["make_valid_valid"]
    assert result["buffer0_valid"]
    assert result["make_valid_parts"] >= 1
    assert result["buffer0_parts"] >= 1
    assert result["repair_symmetric_difference_over_union"] >= 0
