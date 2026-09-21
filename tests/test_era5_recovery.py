"""Bounded source-acquisition logic; no CDS network or invented ERA5 observations."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "ingest_era5_points", ROOT / "scripts/ingest_era5_points.py"
)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def test_first_quarter_recovery_targets_each_point_once() -> None:
    requests = module.choose_requests(
        list(module.POINTS),
        ["2024-04_to_2024-06"],
        max_requests=5,
    )
    assert len(requests) == 5
    assert {row[0] for row in requests} == set(module.POINTS)
    assert {row[3] for row in requests} == {"2024-04_to_2024-06"}
    assert all(row[4] == "2024" and row[5] == ["04", "05", "06"] for row in requests)
    assert len(module.POINTS) * len(module.PERIODS) == 20


def test_bound_selection_rejects_typos_duplicates_or_unbounded_zero() -> None:
    with pytest.raises(ValueError, match="Unknown"):
        module.choose_requests(["invalid"], ["2024-04_to_2024-06"], 5)
    with pytest.raises(ValueError, match="Unknown"):
        module.choose_requests(["kochi"], ["bad_period"], 5)
    with pytest.raises(ValueError, match="unique"):
        module.choose_requests(["kochi", "kochi"], ["2024-04_to_2024-06"], 5)
    with pytest.raises(ValueError, match="Positive"):
        module.choose_requests(["kochi"], ["2024-04_to_2024-06"], 0)
    selected = module.choose_requests(list(module.POINTS), ["2024-07_to_2024-09"], 2)
    assert len(selected) == 2


def test_netcdf_probe_rejects_empty_truncated_html_and_zip(tmp_path: Path) -> None:
    data = tmp_path / "erasource.nc"
    assert module.valid_netcdf(data) is False
    for bad in (b"", b"<html>" * 1000, b"PK\\x03\\x04" + b"0" * 5000):
        data.write_bytes(bad)
        assert module.valid_netcdf(data) is False
    for magic in (bytes.fromhex("43444601"), bytes.fromhex("43444602"),
                  bytes.fromhex("894844460d0a1a0a")):
        data.write_bytes(magic + b"0" * 5000)
        assert module.valid_netcdf(data) is True
        assert len(module.sha256(data)) == 64
