"""Synthetic regression checks; not Kerala evidence."""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from scripts.audit_kerala_niwe_resource import (
    FIELDS,
    analyze,
    histogram,
    read_clip,
)


def sample_clip(tmp_path):
    path = tmp_path / "clip.csv.gz"
    pd.DataFrame([
        [76.1, 10.1, 3.5, 4.0, 2.0, 1.0, 50.0],
        [76.2, 10.2, 7.5, 8.4, 2.2, 1.1, 410.0],
        [76.3, 10.3, 10.5, 11.8, 2.5, 1.0, 850.0],
    ], columns=FIELDS).to_csv(path, index=False)
    return path


def test_binning_edges():
    bins = histogram(np.array([0., 3., 4., 9., 10.]),
                     (0., 3., 4., 10., float("inf")))
    assert [b["point_centres"] for b in bins] == [1, 1, 2, 1]
    assert bins[-1]["maximum_exclusive"] is None


def test_pinned_hash_and_descriptive_result(tmp_path):
    path = sample_clip(tmp_path)
    with pytest.raises(ValueError, match="SHA256"):
        analyze(path, expected_rows=3)
    report = analyze(path, expected_rows=3, allow_repacked_clip=True)
    assert report["point_centres"] == 3
    assert report["wind_speed_m_s"]["median"] == 7.5
    assert report["feasible_capacity_MW"] is None
    assert report["model_admitted"] is False


def test_invalid_or_duplicate_coordinates(tmp_path):
    path = sample_clip(tmp_path)
    frame = pd.read_csv(path)
    frame.loc[0, "Longitude (E)"] = 100.0
    frame.to_csv(path, index=False)
    with pytest.raises(ValueError, match="outside Kerala"):
        read_clip(path, 3)
    frame.loc[0, "Longitude (E)"] = frame.loc[1, "Longitude (E)"]
    frame.loc[0, "Latitude (N)"] = frame.loc[1, "Latitude (N)"]
    frame.to_csv(path, index=False)
    with pytest.raises(ValueError, match="Duplicate"):
        read_clip(path, 3)
