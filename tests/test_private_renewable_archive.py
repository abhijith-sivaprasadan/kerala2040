"""Private research-source archive must fail closed on public repo or stale flags."""
from __future__ import annotations

import json
import runpy
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
MANIFEST = ROOT / "data/evidence/solar/solar_batch_2026_09_21_originals_manifest.json"


def test_public_repo_is_rejected_before_any_gh_call() -> None:
    utils = runpy.run_path(str(SCRIPTS / "private_archive_utils.py"))
    with pytest.raises(ValueError, match="public Kerala2040"):
        utils["ensure_private"]("abhijith-sivaprasadan/kerala2040")
    with pytest.raises(ValueError, match="public Kerala2040"):
        utils["ensure_private"]("")


def test_manifest_does_not_claim_private_repo_or_uploaded_data() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert manifest["release_uploaded"] is False
    assert manifest["release_url"] is None
    assert manifest["archive_repo_created_and_private_verified"] is True
    assert manifest["archive_repo_proposed"] == (
        "abhijith-sivaprasadan/kerala2040-source-archive"
    )
    assert "PRIVATE" in manifest["storage_policy"]


@pytest.mark.parametrize(
    "script,stale_flag",
    [
        ("publish_solar_source_release.py", "--publish"),
        ("publish_solar_source_release.py", "--confirm-public-redistribution"),
        ("publish_niwe_original_release.py", "--confirm-public-redistribution"),
    ],
)
def test_old_public_upload_flags_are_removed(script: str, stale_flag: str) -> None:
    result = subprocess.run(
        [sys.executable, str(SCRIPTS / script), stale_flag],
        capture_output=True,
        text=True,
        check=False,
        cwd=ROOT,
    )
    assert result.returncode != 0
    assert "unrecognized arguments" in result.stderr or "required" in result.stderr


def test_restore_solar_defaults_to_private_repository() -> None:
    restore = (SCRIPTS / "restore_solar_source_release.py").read_text()
    assert "ensure_private(args.archive_repo)" in restore
    assert 'default=PRIVATE_ARCHIVE' in restore
    assert '"abhijith-sivaprasadan/kerala2040"' not in restore
