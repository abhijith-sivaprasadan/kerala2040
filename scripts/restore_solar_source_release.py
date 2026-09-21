"""Restore the checksum-pinned solar source batch from this repository's release.

Prerequisites: GitHub CLI (gh) authenticated and source release uploaded.
Never treat successful retrieval as model admission; see the source manifest.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data/evidence/solar/solar_batch_2026_09_21_originals_manifest.json"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(4 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dest",
        type=Path,
        default=ROOT / "data/external/raw/solar/source_2026_09_21",
        help="Local destination for release source archives (ignored by git)",
    )
    parser.add_argument(
        "--repo", default="abhijith-sivaprasadan/kerala2040"
    )
    args = parser.parse_args()
    if not shutil.which("gh"):
        raise SystemExit("GitHub CLI (gh) is required: https://cli.github.com/")
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    dest = args.dest.resolve()
    dest.mkdir(parents=True, exist_ok=True)
    for asset in data["assets"]:
        path = dest / asset["name"]
        if path.is_file():
            if path.stat().st_size == asset["bytes"] and sha256_file(path) == asset["sha256"]:
                print(f"VERIFIED cached original: {asset['name']}")
                continue
            raise SystemExit(f"Existing file fails manifest SHA/size; remove or move: {path}")
        subprocess.run(
            [
                "gh", "release", "download", data["release_tag"],
                "--repo", args.repo, "--dir", str(dest),
                "--pattern", asset["name"],
            ],
            check=True,
        )
        if not path.is_file() or path.stat().st_size != asset["bytes"]:
            raise SystemExit(f"Missing/wrong size release original: {path}")
        if sha256_file(path) != asset["sha256"]:
            path.unlink()
            raise SystemExit(f"SHA256 mismatch; discarded downloaded file: {asset['name']}")
        print(f"VERIFIED downloaded original: {asset['name']}")
    print(f"All {len(data['assets'])} originals verified in {dest}")


if __name__ == "__main__":
    main()
