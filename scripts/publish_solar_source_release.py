"""Archive solar ZIPs/PDFs into a SEPARATE PRIVATE GitHub repository.

Replaces unsafe public-release workflow. The destination MUST be private.
Private archival remains subject to applicable source usage/access terms.

Create private archive repository with an initial README, authenticate with
GitHub CLI on your computer, and place all 17 original files in one folder.

  python scripts/publish_solar_source_release.py --source-dir "E:/Solar"
  python scripts/restore_solar_source_release.py --dest "E:/Solar-restore-test"
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from private_archive_utils import (
    PRIVATE_ARCHIVE,
    assert_original,
    create_or_check_release,
    ensure_private,
    upload_exact_asset,
)

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data/evidence/solar/solar_batch_2026_09_21_originals_manifest.json"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", required=True, type=Path)
    parser.add_argument("--archive-repo", default=PRIVATE_ARCHIVE)
    args = parser.parse_args()

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    source_dir = args.source_dir.resolve()
    assets = manifest["assets"]
    if not source_dir.is_dir():
        parser.error(f"Originals folder not found: {source_dir}")
    if len(assets) != 17:
        parser.error(f"Expected 17 original solar-batch files, got {len(assets)}")
    # Verify private destination and ALL local originals BEFORE remote write.
    branch = ensure_private(args.archive_repo)
    for item in assets:
        if Path(item["name"]).name != item["name"]:
            raise ValueError(f"Unsafe source filename: {item['name']}")
        assert_original(source_dir / item["name"], item["bytes"], item["sha256"])
        print(f"VERIFIED local original: {item['name']}")
    tag = manifest["release_tag"]
    create_or_check_release(
        args.archive_repo, tag, branch,
        "Kerala2040 PRIVATE original solar data — 2026-09-21",
    )
    for item in assets:
        upload_exact_asset(
            args.archive_repo, tag, source_dir / item["name"],
            item["bytes"], item["sha256"],
        )
    print(
        "All 17 original solar files present by remote size in a PRIVATE repo. "
        "Run restore_solar_source_release.py to verify remote bytes by SHA256."
    )
    print(
        f"PRIVATE link (authorized collaborators only): "
        f"https://github.com/{args.archive_repo}/releases/tag/{tag}"
    )


if __name__ == "__main__":
    main()
