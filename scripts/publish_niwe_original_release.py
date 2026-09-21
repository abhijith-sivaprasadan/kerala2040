"""Store original NIWE Wind.zip in a SEPARATE PRIVATE GitHub repository.

No public redistribution flag or public Release is supported. Private source
archival is still subject to NIWE's download/use terms; never grant archive
access to others without verifying permission.

  python scripts/publish_niwe_original_release.py --wind-zip "E:/Wind.zip"
  python scripts/publish_niwe_original_release.py --verify --dest "E:/wind-restore"
"""
from __future__ import annotations

import argparse
import hashlib
import io
import zipfile
from pathlib import Path

from private_archive_utils import (
    PRIVATE_ARCHIVE,
    assert_original,
    create_or_check_release,
    ensure_private,
    restore_exact_asset,
    upload_exact_asset,
)

WIND_SHA = "54196bfa8dfa27295db7f71f100ac63c0b4a77d1dace4da2ae5f9ee2c869d849"
WIND_BYTES = 422482328
INNER_SHA = "f166450c3ea591b5b346f9cd27899b10b6f18ce9cf441c98388c6f0e98d44b38"
TAG = "niwe-wind-original-2026-09-21"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--wind-zip", type=Path, help="Upload original Wind.zip")
    mode.add_argument("--verify", action="store_true", help="Restore and verify SHA256")
    parser.add_argument("--dest", type=Path, help="Restore into this new/empty folder")
    parser.add_argument("--archive-repo", default=PRIVATE_ARCHIVE)
    args = parser.parse_args()

    branch = ensure_private(args.archive_repo)
    if args.verify:
        if args.dest is None:
            parser.error("--verify requires --dest")
        restore_exact_asset(
            args.archive_repo, TAG, "Wind.zip", args.dest.resolve(),
            WIND_BYTES, WIND_SHA,
        )
        print("PRIVATE NIWE original restore verified by SHA256")
        return

    assert args.wind_zip is not None
    original = args.wind_zip.resolve()
    if original.name != "Wind.zip":
        parser.error("The pinned original must be named Wind.zip")
    assert_original(original, WIND_BYTES, WIND_SHA)
    with zipfile.ZipFile(original) as outer:
        inner = outer.read("Wind/150m_Map_Data_A_to_G.zip")
    if hashlib.sha256(inner).hexdigest() != INNER_SHA:
        parser.error("NIWE internal original ZIP SHA256 mismatch")
    with zipfile.ZipFile(io.BytesIO(inner)) as archive:
        bad = archive.testzip()
    if bad is not None:
        parser.error(f"NIWE member integrity failed: {bad}")
    create_or_check_release(
        args.archive_repo, TAG, branch,
        "Kerala2040 PRIVATE original NIWE 150 m wind data",
    )
    upload_exact_asset(
        args.archive_repo, TAG, original, WIND_BYTES, WIND_SHA,
    )
    print("NIWE original PRIVATE archive size checked; run --verify to check restored bytes.")
    print(
        f"PRIVATE link: "
        f"https://github.com/{args.archive_repo}/releases/tag/{TAG}"
    )


if __name__ == "__main__":
    main()
