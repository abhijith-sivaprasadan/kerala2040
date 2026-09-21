"""Restore SHA256-pinned originals from the separate PRIVATE solar data archive.

Requires authenticated GitHub CLI. The destination repository MUST be private.
No raw originals are downloaded from the public Kerala2040 repository.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from private_archive_utils import (
    PRIVATE_ARCHIVE,
    ensure_private,
    restore_exact_asset,
)

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data/evidence/solar/solar_batch_2026_09_21_originals_manifest.json"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dest",
        type=Path,
        default=ROOT / "data/external/raw/solar/source_2026_09_21",
    )
    parser.add_argument("--archive-repo", default=PRIVATE_ARCHIVE)
    args = parser.parse_args()

    ensure_private(args.archive_repo)
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    for item in data["assets"]:
        restore_exact_asset(
            args.archive_repo, data["release_tag"],
            item["name"], args.dest.resolve(),
            item["bytes"], item["sha256"],
        )
    print(
        f"All {len(data['assets'])} original files restored from PRIVATE "
        f"archive and SHA256-verified. This is source storage, not model admission."
    )


if __name__ == "__main__":
    main()
