"""Regression tests for reproducible repair-comparison, not model admission."""

from __future__ import annotations

import pytest

from shapely.geometry import Polygon

from scripts.compare_gsi_2022_repairs import (
    CLASSES,
    METHODS,
    class_overlap,
    compare_feature,
    polygonal,
)


def test_self_intersection_requires_explicit_candidate_comparison():
    bowtie = Polygon([(0, 0), (2, 2), (0, 2), (2, 0), (0, 0)])
    assert not bowtie.is_valid
    observed, variants = compare_feature(
        bowtie, "synthetic_only", "High", "synthetic_sha", 0
    )
    assert set(observed["candidates"]) == set(METHODS)
    assert all(
        observed["candidates"][method]["geometry_is_valid"]
        for method in METHODS
    )
    assert all(
        observed["candidates"][method]["area_m2"] > 0
        for method in METHODS
    )
    assert observed["candidate_automatically_admitted"] is False
    assert observed["source_geometry_is_valid"] is False
    assert variants["linework"].area >= variants["buffer0"].area
    assert observed["pairwise_comparison"]["linework_vs_buffer0"][
        "symmetric_difference_m2"
    ] > 0


def test_polygon_extraction_counts_discarded_linear_parts():
    from shapely.geometry import GeometryCollection, LineString

    geom, discarded = polygonal(
        GeometryCollection([
            Polygon([(0, 0), (0, 1), (1, 0), (0, 0)]),
            LineString([(2, 2), (3, 3)]),
        ])
    )
    assert geom.is_valid
    assert not geom.is_empty
    assert discarded == 1


def test_class_overlap_is_measured_not_assumed_absent():
    classes = {
        "Low": Polygon([(0, 0), (0, 2), (2, 2), (2, 0)]),
        "Moderate": Polygon([(1, 1), (1, 3), (3, 3), (3, 1)]),
        "High": Polygon([(5, 5), (5, 6), (6, 6), (6, 5)]),
    }
    assert set(classes) == CLASSES
    result = class_overlap(classes)
    assert result["Low_and_Moderate"]["overlap_m2"] == pytest.approx(1)
    assert result["High_and_Low"]["overlap_m2"] == 0
