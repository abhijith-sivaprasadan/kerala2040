"""Checksum-gated upload of ONLY NIWE's original 150 m ZIP to a repo Release.

DO NOT upload the user's whole mixed Wind.zip: it contains unrelated studies.
Public redistribution must be authorised by NIWE's actual download terms.

Example:
 python scripts/publish_niwe_source_release.py --source-wind "E:/Wind.zip" \
   --confirm-public-redistribution --publish
"""
from __future__ import annotations

import argparse
import hashlib
import io
import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path

EXPECTED = "f166450c3ea591b5b346f9cd27899b10b6f18ce9cf441c98388c6f0e98d44b38"
BYTES = 251971340
TAG = "niwe-150m-original-2026-09-22"
NAME = "150m_Map_Data_A_to_G.zip"


def digest(path: Path) -> str:
    sha = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(4 * 1024 * 1024), b""):
            sha.update(block)
    return sha.hexdigest()


def gh(*args: str, capture: bool = False) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["gh", *args], check=False, text=True,
        stdout=subprocess.PIPE if capture else None,
        stderr=subprocess.PIPE if capture else None,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-wind", type=Path, required=True)
    parser.add_argument("--repo", default="abhijith-sivaprasadan/kerala2040")
    parser.add_argument("--confirm-public-redistribution", action="store_true")
    parser.add_argument("--publish", action="store_true")
    args = parser.parse_args()
    if not args.confirm_public_redistribution:
        parser.error("Review NIWE's written public-redistribution terms first.")
    if not shutil.which("gh") or gh("auth", "status").returncode:
        parser.error("Install gh and run gh auth login before uploading.")
    with tempfile.TemporaryDirectory() as temp:
        target = Path(temp) / NAME
        with zipfile.ZipFile(args.source_wind) as uploaded:
            if NAME in uploaded.namelist():
                target.write_bytes(args.source_wind.read_bytes())
            else:
                target.write_bytes(uploaded.read("Wind/" + NAME))
        if target.stat().st_size != BYTES or digest(target) != EXPECTED:
            parser.error("Source is not the verified original NIWE 150m archive.")
        with zipfile.ZipFile(target) as original:
            if original.testzip() is not None:
                parser.error("Original NIWE ZIP CRC failure.")
            if "150m_Map_Data_A_to_G.csv" not in original.namelist():
                parser.error("Missing national original CSV.")
        print("ORIGINAL NIWE ZIP SHA256 + CRC VERIFIED", flush=True)
        existing = gh(
            "release", "view", TAG, "--repo", args.repo, "--json", "isDraft",
            capture=True,
        )
        if existing.returncode:
            created = gh(
                "release", "create", TAG, "--repo", args.repo,
                "--target", "main", "--draft",
                "--title", "NIWE original national 150 m wind atlas",
                "--notes", (
                    "Verified original NIWE national 150 m source ZIP; 500m model "
                    "grid. Publisher: NIWE; source: "
                    "https://niwe.res.in/Open_data_Set/open_wind_dataset/11/ ; "
                    "SHA256 f166450c3ea591b5b346f9cd27899b10b6f18ce9cf441c98388c6f0e98d44b38. "
                    "Not model-ready wind generation or installable capacity."
                ),
            )
            if created.returncode:
                parser.error("Could not create draft source release.")
        elif '"isDraft":true' not in existing.stdout.replace(" ", ""):
            parser.error("Existing NIWE release is public; refusing overwrite.")
        if gh(
            "release", "upload", TAG, str(target), "--repo", args.repo,
            "--clobber",
        ).returncode:
            parser.error("GitHub NIWE upload failed; draft retained.")
        verify = Path(temp) / "remote"
        verify.mkdir()
        if gh(
            "release", "download", TAG, "--repo", args.repo,
            "--pattern", NAME, "--dir", str(verify),
        ).returncode or digest(verify / NAME) != EXPECTED:
            parser.error("Remote download SHA mismatch; draft retained.")
        print("ORIGINAL NIWE SOURCE STORED AND REMOTE SHA256 VERIFIED", flush=True)
        if args.publish:
            if gh(
                "release", "edit", TAG, "--repo", args.repo, "--draft=false",
            ).returncode:
                parser.error("NIWE release uploaded but not published.")
            print(f"https://github.com/{args.repo}/releases/tag/{TAG}")


if __name__ == "__main__":
    main()
