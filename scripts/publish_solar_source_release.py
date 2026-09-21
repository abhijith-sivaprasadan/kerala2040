"""Publish the original solar source batch as GitHub Release assets, not Git blobs.

Use ONLY after checking that every asset may be redistributed from a PUBLIC
repository. This includes the mixed Solar.zip archive and third-party PDFs.
All originals and their SHA256 values must match the committed source manifest.
The release stays draft unless --publish is supplied.

Example:
  python scripts/publish_solar_source_release.py --source-dir "E:/Solar" \\
      --confirm-public-redistribution --publish
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


def run_gh(*args: str, capture: bool = False) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["gh", *args],
        text=True,
        stdout=subprocess.PIPE if capture else None,
        stderr=subprocess.PIPE if capture else None,
        check=False,
    )


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(4 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", type=Path, required=True)
    parser.add_argument("--repo", default="abhijith-sivaprasadan/kerala2040")
    parser.add_argument("--confirm-public-redistribution", action="store_true")
    parser.add_argument("--publish", action="store_true")
    args = parser.parse_args()
    if not args.confirm_public_redistribution:
        parser.error("Check all source licences, then pass --confirm-public-redistribution.")
    if not shutil.which("gh"):
        parser.error("GitHub CLI is required: https://cli.github.com/")
    if run_gh("auth", "status").returncode:
        parser.error("Run gh auth login first.")
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    source = args.source_dir.resolve()
    originals: list[Path] = []
    for asset in manifest["assets"]:
        file = source / asset["name"]
        if not file.is_file() or file.stat().st_size != asset["bytes"]:
            parser.error(f"Original missing or wrong size: {file}")
        if file_sha256(file) != asset["sha256"]:
            parser.error(f"SHA256 mismatch: {file}")
        originals.append(file)
        print(f"VERIFIED original: {asset['name']}", flush=True)

    tag = manifest["release_tag"]
    existing = run_gh(
        "release", "view", tag, "--repo", args.repo, "--json", "isDraft,assets",
        capture=True,
    )
    if existing.returncode:
        created = run_gh(
            "release", "create", tag, "--repo", args.repo, "--target", "main",
            "--title", "Kerala2040: original solar sources 2026-09-21",
            "--notes", (
                "Original solar/wind provider uploads. Read provenance, publisher "
                "attribution, units and SHA256 in "
                "data/evidence/solar/solar_batch_2026_09_21_originals_manifest.json. "
                "No model admission is implied."
            ),
            "--draft",
        )
        if created.returncode:
            parser.error("Could not create draft release; check repo permission.")
    elif not json.loads(existing.stdout)["isDraft"]:
        parser.error("Release is already public; refusing to overwrite assets.")

    for file in originals:
        uploaded = run_gh(
            "release", "upload", tag, str(file), "--repo", args.repo, "--clobber"
        )
        if uploaded.returncode:
            parser.error(f"Failed to upload {file.name}; draft retained for retry.")
    remote = run_gh(
        "release", "view", tag, "--repo", args.repo, "--json", "isDraft,assets",
        capture=True,
    )
    if remote.returncode:
        parser.error("Cannot verify uploaded assets.")
    release = json.loads(remote.stdout)
    by_name = {item["name"]: item["size"] for item in release["assets"]}
    if any(by_name.get(item["name"]) != item["bytes"] for item in manifest["assets"]):
        parser.error("Remote release asset missing or different size; draft retained.")
    print(f"VERIFIED GitHub release: {len(originals)} assets of expected size, tag {tag}")
    if args.publish:
        done = run_gh("release", "edit", tag, "--repo", args.repo, "--draft=false")
        if done.returncode:
            parser.error("Source assets uploaded, but release remains draft.")
        print(f"PUBLISHED: https://github.com/{args.repo}/releases/tag/{tag}")
    else:
        print("DRAFT only; publish after rights review with gh release edit "
              f"{tag} --repo {args.repo} --draft=false")


if __name__ == "__main__":
    main()
