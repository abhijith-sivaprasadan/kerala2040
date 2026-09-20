"""Synthetic topology defect shows repairs are separate from authoritative GSI source."""

from __future__ import annotations

import pytest

pytest.importorskip("shapely")

from shapely import is_valid, make_valid
from shapely.geometry import Polygon

from kerala2040.gsi_geometry_repair import _polygons


def test_ring_crossing_make_valid_preserves_polygonal_parts():
    original = Polygon([(0, 0), (2, 2), (0, 2), (2, 0), (0, 0)])
    assert not is_valid(original)
    candidate = make_valid(original, method="linework")
    parts = _polygons(candidate)
    assert len(parts) == 2
    assert all(is_valid(part) for part in parts)
    assert sum(part.area for part in parts) > 0
