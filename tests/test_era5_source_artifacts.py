"""Source QA tests use synthetic NetCDFs, never fabricated ERA5 observations."""
from __future__ import annotations

import hashlib
import importlib.util
import io
import json
from pathlib import Path
import zipfile

import h5py
import numpy as np
import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/verify_era5_source_artifacts.py"
spec = importlib.util.spec_from_file_location("verify_era5_source_artifacts", SCRIPT)
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)


def make_artifact(tmp_path: Path, *, corrupt: bool = False) -> Path:
    year, months = 2024, ["04", "05", "06"]
    expected = validator.hourly_window(year, months)
    all_vars = (("instant", ("t2m", "u10", "v10")),
                ("accum", ("ssrd", "tp")))
    files = {}
    for stream, keys in all_vars:
        filename = tmp_path / (stream + ".nc")
        with h5py.File(filename, "w") as nc:
            time = nc.create_dataset("valid_time", data=expected)
            time.attrs["units"] = np.bytes_("seconds since 1970-01-01")
            nc.create_dataset("latitude", data=[10.0])
            nc.create_dataset("longitude", data=[76.25])
            for key in keys:
                values = nc.create_dataset(key, data=np.ones((len(expected), 1, 1)))
                values.attrs["units"] = np.bytes_(validator.UNITS[key])
        files[stream] = filename.read_bytes()
    source_stream = io.BytesIO()
    with zipfile.ZipFile(source_stream, "w") as original:
        for stream, data in files.items():
            original.writestr(stream + ".nc", data)
    raw = source_stream.getvalue()
    rows = []
    for stream, data in files.items():
        rows.append({
            "point": "kochi", "selected_quarter": "2024-04_to_2024-06",
            "period": "2024-04_to_2024-06", "months": months,
            "path": "source_files/quarter__" + stream + ".nc",
            "sha256": hashlib.sha256(data).hexdigest(),
            "bytes": len(data),
            "source_archive_path": "source_files/quarter.zip",
            "source_archive_member": stream + ".nc",
            "source_archive_sha256": hashlib.sha256(raw).hexdigest(),
            "source_archive_bytes": len(raw),
            "latitude": 9.9312, "longitude": 76.2673,
        })
    attempt = {
        "selection": {"points": ["kochi"], "periods": ["2024-04_to_2024-06"]},
        "source_windows_succeeded": 1, "files_attempted": 1,
        "windows_completed": 1, "failures": [], "files": rows,
    }
    path = tmp_path / "synthetic-GitHub-artifact.zip"
    with zipfile.ZipFile(path, "w") as artifact:
        artifact.writestr("retrieval_attempt.json", json.dumps(attempt))
        artifact.writestr("source_files/quarter.zip", raw)
        for stream, data in files.items():
            artifact.writestr(
                "source_files/quarter__" + stream + ".nc",
                (b"corrupted" + data if corrupt and stream == "accum" else data),
            )
    return path


def test_hourly_source_qa_checks_both_streams_and_exact_hours(tmp_path: Path) -> None:
    path = make_artifact(tmp_path)
    result = validator.inspect_artifact(path)
    assert result["point"] == "kochi"
    assert result["quarter"] == "2024-04_to_2024-06"
    assert result["hours"] == 2184
    assert result["grid"] == {"latitude": [10.0], "longitude": [76.25]}
    assert len(result["components"]) == 2
    partial = validator.verify([path])
    assert partial["full_year_source_qc_passed"] is False
    assert partial["point_hours_verified"] == 2184
    with pytest.raises(ValueError, match="Missing full-year"):
        validator.verify([path], require_full_year=True)


def test_tampering_with_netcdffiles_is_rejected(tmp_path: Path) -> None:
    path = make_artifact(tmp_path, corrupt=True)
    with pytest.raises(ValueError, match="hash/size mismatch"):
        validator.inspect_artifact(path)


def test_duplicate_artifact_is_not_full_year(tmp_path: Path) -> None:
    path = make_artifact(tmp_path)
    with pytest.raises(ValueError, match="Duplicate"):
        validator.verify([path, path])
