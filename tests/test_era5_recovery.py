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
                  bytes.fromhex("43444605"), bytes.fromhex("894844460d0a1a0a")):
        data.write_bytes(magic + b"0" * 5000)
        assert module.valid_netcdf(data) is True
        assert len(module.sha256(data)) == 64


def test_oversized_quarter_recovers_with_verified_monthly_bytes(tmp_path, monkeypatch) -> None:
    import json
    import sys
    from types import SimpleNamespace

    class MockCDS:
        def __init__(self) -> None:
            self.calls = []

        def retrieve(self, dataset, request, target):
            assert dataset == module.DATASET
            self.calls.append(tuple(request["month"]))
            if len(request["month"]) > 1:
                raise RuntimeError("HTTP 403: cost limits exceeded; your request is too large")
            Path(target).write_bytes(bytes.fromhex("894844460d0a1a0a") + b"0" * 5000)

    provider = MockCDS()
    monkeypatch.setenv("CDSAPI_KEY", "synthetic-test-key-not-a-real-secret")
    monkeypatch.setitem(sys.modules, "cdsapi", SimpleNamespace(Client=lambda **kwargs: provider))
    manifest = tmp_path / "attempt.json"
    monkeypatch.setattr(sys, "argv", [
        "ingest_era5_points.py", "--points", "kochi", "--periods",
        "2024-04_to_2024-06", "--max-requests", "1",
        "--raw-dir", str(tmp_path / "raw"), "--manifest", str(manifest),
    ])
    assert module.main() == 0
    result = json.loads(manifest.read_text())
    assert result["classification"] == (
        "reanalysis_retrieval_attempt_not_validated_resource_model"
    )
    assert result["windows_completed"] == 1
    assert result["source_requests_sent"] == 4
    assert result["files_succeeded"] == 3
    assert result["files_expected"] == 20  # Full new plan, not observed source count
    assert result["files_not_attempted"] == 19
    assert result["failures"] == []
    assert len(result["oversized_window_fallbacks"]) == 1
    assert provider.calls == [
        ("04", "05", "06"), ("04",), ("05",), ("06",)
    ]
    assert {row["period"] for row in result["files"]} == {
        "2024-04", "2024-05", "2024-06"
    }
    for item in result["files"]:
        assert Path(item["path"]).is_file()
        assert len(item["sha256"]) == 64


def test_incomplete_monthly_fallback_never_returns_success(tmp_path, monkeypatch) -> None:
    import json
    import sys
    from types import SimpleNamespace

    class MockCDS:
        def retrieve(self, dataset, request, target):
            months = request["month"]
            if len(months) > 1:
                raise RuntimeError("cost limits exceeded")
            if months == ["05"]:
                Path(target).write_bytes(b"<html>" * 1000)
                return
            Path(target).write_bytes(bytes.fromhex("43444601") + b"0" * 5000)

    monkeypatch.setenv("CDSAPI_KEY", "synthetic-test-key-not-a-real-secret")
    monkeypatch.setitem(sys.modules, "cdsapi", SimpleNamespace(
        Client=lambda **kwargs: MockCDS()
    ))
    manifest = tmp_path / "attempt.json"
    monkeypatch.setattr(sys, "argv", [
        "ingest_era5_points.py", "--points", "kochi", "--periods",
        "2024-04_to_2024-06", "--max-requests", "1",
        "--raw-dir", str(tmp_path / "raw"), "--manifest", str(manifest),
    ])
    assert module.main() == 2
    result = json.loads(manifest.read_text())
    assert result["windows_completed"] == 0
    assert result["files_succeeded"] == 2
    assert len(result["failures"]) == 1
    assert result["failures"][0]["period"] == "2024-05"
    assert not (tmp_path / "raw/era5_kochi_2024-05.nc").exists()


def test_rejected_cds_zip_is_preserved_with_hash_and_format(tmp_path, monkeypatch) -> None:
    import json
    import sys
    from types import SimpleNamespace

    response = bytes.fromhex("504b0304") + b"not-a-netcdf" * 500

    class MockCDS:
        def retrieve(self, dataset, request, target):
            Path(target).write_bytes(response)

    monkeypatch.setenv("CDSAPI_KEY", "synthetic-test-key-not-a-real-secret")
    monkeypatch.setitem(sys.modules, "cdsapi", SimpleNamespace(Client=lambda **kw: MockCDS()))
    manifest = tmp_path / "attempt.json"
    monkeypatch.setattr(sys, "argv", [
        "ingest_era5_points.py", "--points", "kochi", "--periods",
        "2024-04_to_2024-06", "--max-requests", "1",
        "--raw-dir", str(tmp_path / "raw"), "--manifest", str(manifest),
    ])
    assert module.main() == 2
    result = json.loads(manifest.read_text())
    assert result["files_succeeded"] == 0
    failure = result["failures"][0]
    assert failure["response_format_guess"] == "zip"
    assert failure["response_prefix_hex"].startswith("504b0304")
    assert failure["response_bytes"] == len(response)
    rejected = Path(failure["rejected_path"])
    assert rejected.suffix == ".zip"
    assert rejected.read_bytes() == response
    assert failure["response_sha256"] == module.sha256(rejected)
    assert not (tmp_path / "raw/era5_kochi_2024-04_to_2024-06.nc").exists()
