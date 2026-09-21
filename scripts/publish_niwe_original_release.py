"""Publish verified NIWE Wind.zip to same repo Release assets after rights review.

NIWE original raw wind atlas has publisher research-use restrictions; a public
GitHub Release is NOT implicitly permitted. This script intentionally refuses
upload without the user's explicit redistribution-rights confirmation.

Example:
 python scripts/publish_niwe_original_release.py --wind-zip "E:/Data/Wind.zip" \
   --confirm-public-redistribution
Creates only a DRAFT release; inspect before publishing.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import zipfile
from pathlib import Path

WIND_SHA = "54196bfa8dfa27295db7f71f100ac63c0b4a77d1dace4da2ae5f9ee2c869d849"
WIND_BYTES = 422482328
INNER_SHA = "f166450c3ea591b5b346f9cd27899b10b6f18ce9cf441c98388c6f0e98d44b38"
TAG = "niwe-wind-original-2026-09-21"
REPO = "abhijith-sivaprasadan/kerala2040"


def hash_file(path: Path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(2 ** 20), b""):
            h.update(block)
    return h.hexdigest()


def run(*args: str):
    return subprocess.run(["gh", *args], check=True, capture_output=True, text=True)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--wind-zip", type=Path, required=True)
    p.add_argument("--confirm-public-redistribution", action="store_true")
    a = p.parse_args()
    if not a.confirm_public_redistribution:
        p.error("Confirm NIWE's applicable PUBLIC REDISTRIBUTION rights first.")
    if not shutil.which("gh"):
        p.error("Install GitHub CLI and authenticate with gh auth login")
    f = a.wind_zip.resolve()
    if f.stat().st_size != WIND_BYTES or hash_file(f) != WIND_SHA:
        p.error("Original Wind.zip differs from pinned source (size or SHA256)")
    with zipfile.ZipFile(f) as outer:
        inner = outer.read("Wind/150m_Map_Data_A_to_G.zip")
    if hashlib.sha256(inner).hexdigest() != INNER_SHA:
        p.error("NIWE internal original ZIP does not match evidence")
    try:
        prior = json.loads(
            run("release", "view", TAG, "-R", REPO, "--json", "isDraft").stdout
        )
        if not prior["isDraft"]:
            p.error("Release already public: no overwrite allowed")
    except subprocess.CalledProcessError:
        run(
            "release", "create", TAG, "-R", REPO, "--target", "main",
            "--draft", "--title", "NIWE original 150m wind data source",
            "--notes", (
                "Original NIWE Wind.zip; source usage/redistribution requires "
                "publisher permission. Original SHA256: " + WIND_SHA
            ),
        )
    run("release", "upload", TAG, str(f), "-R", REPO, "--clobber")
    state = json.loads(
        run("release", "view", TAG, "-R", REPO, "--json", "isDraft,assets").stdout
    )
    matching = [
        x for x in state["assets"]
        if x["name"] == f.name and x["size"] == WIND_BYTES
    ]
    if not state["isDraft"] or len(matching) != 1:
        p.error("Remote asset size or draft status failed")
    print("Verified DRAFT NIWE archive; do not publish without NIWE permission.")
    print(f"https://github.com/{REPO}/releases/tag/{TAG}")


if __name__ == "__main__":
    main()
