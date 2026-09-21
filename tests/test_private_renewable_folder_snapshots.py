"""Test five-folder snapshots without GitHub or downloading any third-party bytes."""
from __future__ import annotations

import json
import runpy
import subprocess
import sys
import zipfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/archive_renewable_folders_private.py"
FOLDERS = (
    "global-pv-potential-study-raster-data-layers-globalsolaratlas",
    "India_GISdata_LTAym_YearlyMonthlyTotals_GlobalSolarAtlas-v2_GEOTIFF",
    "India_GISdata_LTAym_AvgDailyTotals_GlobalSolarAtlas-v2_GEOTIFF",
    "Wind",
    "Solar",
)


def make_folders(root: Path) -> None:
    for index, name in enumerate(FOLDERS):
        directory = root / name / "nested"
        directory.mkdir(parents=True)
        (directory / f"{index:02d}.txt").write_bytes(
            ("binary source " + name).encode("utf8")
        )


def test_exact_five_folder_prepare_and_local_restore(tmp_path: Path) -> None:
    source, stage = tmp_path / "Downloads", tmp_path / "stage"
    make_folders(source)
    p = subprocess.run(
        [sys.executable, str(SCRIPT), "--source-root", str(source),
         "--staging-dir", str(stage)],
        check=False, text=True, capture_output=True,
    )
    assert p.returncode == 0, p.stdout + p.stderr
    manifest = json.loads(
        (stage / "renewable-five-folders-manifest.json").read_text()
    )
    assert manifest["classification"].endswith("NOT_ORIGINAL_PROVIDER_ZIPS")
    assert manifest["original_17_archives_SHA256_verified_by_this_snapshot"] is False
    assert [row["folder"] for row in manifest["snapshots"]] == list(FOLDERS)
    assert len(manifest["snapshots"]) == 5
    for snap in manifest["snapshots"]:
        assert snap["file_count"] == 1
        assert sum(part["bytes"] for part in snap["parts"]) == snap["archive_bytes"]
        with zipfile.ZipFile(stage / snap["archive_filename"]) as archive:
            assert archive.testzip() is None
            assert archive.namelist() == [
                snap["folder"] + "/nested/" + snap["members"][0]["relative_path"].split("/")[-1]
            ]
    # Reassemble one ZIP from verified part(s), then check every file checksum.
    sys.path.insert(0, str(ROOT / "scripts"))
    try:
        module = runpy.run_path(str(SCRIPT))
    finally:
        sys.path.remove(str(ROOT / "scripts"))
    snap = manifest["snapshots"][0]
    (stage / snap["archive_filename"]).unlink()
    module["reconstruct"](stage, snap)
    assert (stage / snap["archive_filename"]).exists()


def test_refuse_staging_inside_original_downloads(tmp_path: Path) -> None:
    source = tmp_path / "Downloads"
    make_folders(source)
    p = subprocess.run(
        [sys.executable, str(SCRIPT), "--source-root", str(source),
         "--staging-dir", str(source / "archive-stage")],
        check=False, text=True, capture_output=True,
    )
    assert p.returncode != 0
    assert "OUTSIDE the source tree" in (p.stdout + p.stderr)


def test_missing_one_folder_fails_without_github(tmp_path: Path) -> None:
    source = tmp_path / "Downloads"
    make_folders(source)
    import shutil

    shutil.rmtree(source / FOLDERS[-1])
    p = subprocess.run(
        [sys.executable, str(SCRIPT), "--source-root", str(source),
         "--staging-dir", str(tmp_path / "stage")],
        check=False, text=True, capture_output=True,
    )
    assert p.returncode != 0
    assert "Missing/unsafe source folder" in (p.stdout + p.stderr)


def test_verify_requires_local_trusted_manifest(tmp_path: Path) -> None:
    p = subprocess.run(
        [sys.executable, str(SCRIPT), "--verify",
         "--staging-dir", str(tmp_path / "new-stage")],
        check=False, text=True, capture_output=True,
    )
    assert p.returncode != 0
    assert "--reference-manifest" in p.stderr


def test_symlink_is_refused(tmp_path: Path) -> None:
    source = tmp_path / "Downloads"
    make_folders(source)
    external = tmp_path / "secret.txt"
    external.write_text("secret")
    link = source / FOLDERS[0] / "nested" / "link"
    try:
        link.symlink_to(external)
    except (OSError, NotImplementedError):
        pytest.skip("Creating symlinks is not supported")
    sys.path.insert(0, str(ROOT / "scripts"))
    try:
        module = runpy.run_path(str(SCRIPT))
    finally:
        sys.path.remove(str(ROOT / "scripts"))
    with pytest.raises(ValueError, match="Refusing symlink"):
        module["folder_files"](source / FOLDERS[0])
