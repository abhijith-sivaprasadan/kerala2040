"""Snapshot FIVE user folders into PRIVATE GitHub release assets, with SHA256 restore.

This handles extracted folders (not necessarily original ZIP bytes). Do not
mistake a re-packaged directory for a byte-identical original provider ZIP.
Source hierarchy is retained; each nested file is SHA256-pinned. Each
archive is split into 768 MiB parts for robust Release uploads.

Windows example (from the public kerala2040 checkout):
  python scripts/archive_renewable_folders_private.py --source-root "$env:USERPROFILE\Downloads" --staging-dir "E:\kerala-staging"
  python scripts/archive_renewable_folders_private.py --staging-dir "E:\kerala-staging" --upload
  python scripts/archive_renewable_folders_private.py --staging-dir "E:\kerala-restore" --verify --reference-manifest "E:\kerala-staging\renewable-five-folders-manifest.json"
Requires gh auth login, PRIVATE archive repo with initialized default branch.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import zipfile
from pathlib import Path

from private_archive_utils import (
    PRIVATE_ARCHIVE,
    create_or_check_release,
    ensure_private,
    restore_exact_asset,
    sha256,
    upload_exact_asset,
)

FOLDERS = (
    "global-pv-potential-study-raster-data-layers-globalsolaratlas",
    "India_GISdata_LTAym_YearlyMonthlyTotals_GlobalSolarAtlas-v2_GEOTIFF",
    "India_GISdata_LTAym_AvgDailyTotals_GlobalSolarAtlas-v2_GEOTIFF",
    "Wind",
    "Solar",
)
TAG = "renewable-five-folder-snapshot-2026-09-22"
MANIFEST_NAME = "renewable-five-folders-manifest.json"
PART_BYTES = 768 * 1024 * 1024
BUFFER = 4 * 1024 * 1024


def folder_files(folder: Path) -> list[Path]:
    if not folder.is_dir() or folder.is_symlink():
        raise FileNotFoundError(f"Missing/unsafe source folder: {folder}")
    entries = []
    for path in folder.rglob("*"):
        if path.is_symlink():
            raise ValueError(f"Refusing symlink in source folder: {path}")
        if path.is_file():
            entries.append(path)
    if not entries:
        raise ValueError(f"Folder contains no files: {folder}")
    return sorted(entries, key=lambda p: p.relative_to(folder).as_posix())


def pack_folder(folder: Path, stage: Path) -> dict:
    """Write deterministic ZIP64 snapshot without loading large files into RAM."""
    archive = stage / f"{folder.name}.snapshot.zip"
    files = folder_files(folder)
    members = []
    with zipfile.ZipFile(
        archive, "w", compression=zipfile.ZIP_DEFLATED,
        compresslevel=3, allowZip64=True,
    ) as output:
        for path in files:
            rel = path.relative_to(folder).as_posix()
            if ".." in path.relative_to(folder).parts:
                raise ValueError(f"Unsafe relative path: {rel}")
            item = zipfile.ZipInfo(f"{folder.name}/{rel}")
            item.date_time = (1980, 1, 1, 0, 0, 0)
            item.compress_type = zipfile.ZIP_DEFLATED
            item._compresslevel = 3
            item.external_attr = 0o644 << 16
            digest = hashlib.sha256()
            size = 0
            with path.open("rb") as source, output.open(
                item, "w", force_zip64=True
            ) as destination:
                for block in iter(lambda: source.read(BUFFER), b""):
                    destination.write(block)
                    digest.update(block)
                    size += len(block)
            members.append({
                "relative_path": rel, "bytes": size,
                "sha256": digest.hexdigest(),
            })
            print(f"HASHED {folder.name}/{rel} ({size} bytes)", flush=True)
    # Independently check that ZIP member CRCs are valid.
    with zipfile.ZipFile(archive) as check:
        if check.testzip() is not None:
            raise ValueError(f"Archive member CRC failed: {archive}")
    packed_size = archive.stat().st_size
    total_hash = sha256(archive)
    return {
        "folder": folder.name,
        "archive_filename": archive.name,
        "archive_bytes": packed_size,
        "archive_sha256": total_hash,
        "file_count": len(members),
        "members": members,
    }


def split_archive(snapshot: dict, stage: Path) -> None:
    original = stage / snapshot["archive_filename"]
    chunks = []
    with original.open("rb") as source:
        index = 1
        while True:
            first = source.read(BUFFER)
            if not first:
                break
            target = stage / f"{original.name}.part{index:04d}"
            digest = hashlib.sha256()
            size = 0
            with target.open("wb") as out:
                block = first
                while block and size < PART_BYTES:
                    out.write(block)
                    digest.update(block)
                    size += len(block)
                    block = source.read(min(BUFFER, PART_BYTES - size))
            chunks.append({
                "name": target.name, "bytes": size, "sha256": digest.hexdigest()
            })
            index += 1
    if not chunks:
        raise ValueError(f"Zero parts from snapshot {original}")
    if sum(p["bytes"] for p in chunks) != snapshot["archive_bytes"]:
        raise ValueError("Chunk total length does not match ZIP")
    snapshot["parts"] = chunks
    print(
        f"PACKED {snapshot['folder']} -> {len(chunks)} upload parts; "
        f"{snapshot['archive_bytes']} ZIP bytes", flush=True,
    )


def prepare(root: Path, stage: Path) -> dict:
    root, stage = root.resolve(), stage.resolve()
    if stage == root or stage.is_relative_to(root):
        raise ValueError("Staging directory must be OUTSIDE the source tree")
    if not root.is_dir():
        raise NotADirectoryError(f"Source root does not exist: {root}")
    stage.mkdir(parents=True, exist_ok=True)
    existing = list(stage.iterdir())
    if existing:
        raise ValueError(
            f"Staging folder must be empty; found {len(existing)} items at {stage}"
        )
    snapshots = []
    for name in FOLDERS:
        path = root / name
        snapshots.append(pack_folder(path, stage))
        split_archive(snapshots[-1], stage)
    result = {
        "schema_version": 1,
        "classification": "PRIVATE_EXTRACTED_FOLDER_SNAPSHOT_NOT_ORIGINAL_PROVIDER_ZIPS",
        "source_root_folder_names": list(FOLDERS),
        "original_17_archives_SHA256_verified_by_this_snapshot": False,
        "public_repo_raw_data_uploaded": False,
        "archive_repo": PRIVATE_ARCHIVE,
        "release_tag": TAG,
        "snapshots": snapshots,
    }
    manifest = stage / MANIFEST_NAME
    manifest.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(f"PREPARED {len(snapshots)} folders: {manifest}")
    return result


def validate_manifest(stage: Path) -> dict:
    manifest = stage / MANIFEST_NAME
    if not manifest.is_file():
        raise FileNotFoundError(
            f"No folder snapshot manifest in {stage}; run preparation first"
        )
    data = json.loads(manifest.read_text(encoding="utf-8"))
    if data["classification"] != (
        "PRIVATE_EXTRACTED_FOLDER_SNAPSHOT_NOT_ORIGINAL_PROVIDER_ZIPS"
    ):
        raise ValueError("Unexpected source archive manifest classification")
    if [s["folder"] for s in data["snapshots"]] != list(FOLDERS):
        raise ValueError("Expected exactly the five named folders in order")
    return data


def verified_archive(stage: Path, snapshot: dict) -> None:
    """Validate full local archive SHA and every original member's SHA."""
    archive = stage / snapshot["archive_filename"]
    if archive.stat().st_size != snapshot["archive_bytes"]:
        raise ValueError(f"Archive byte size mismatch: {archive}")
    if sha256(archive) != snapshot["archive_sha256"]:
        raise ValueError(f"Archive SHA256 mismatch: {archive}")
    with zipfile.ZipFile(archive) as source:
        if len(source.infolist()) != snapshot["file_count"]:
            raise ValueError(f"Archive member count mismatch: {archive}")
        expected = {snapshot["folder"] + "/" + f["relative_path"]: f
                    for f in snapshot["members"]}
        if set(source.namelist()) != set(expected):
            raise ValueError(f"Archive member names differ: {archive}")
        for member in source.infolist():
            record = expected[member.filename]
            digest, size = hashlib.sha256(), 0
            with source.open(member) as stream:
                for block in iter(lambda: stream.read(BUFFER), b""):
                    digest.update(block)
                    size += len(block)
            if size != record["bytes"] or digest.hexdigest() != record["sha256"]:
                raise ValueError(f"Folder file SHA256/size mismatch: {member.filename}")
    print(f"RESTORED and verified ZIP plus ALL file SHAs: {archive.name}")


def reconstruct(stage: Path, snapshot: dict) -> None:
    target = stage / snapshot["archive_filename"]
    if target.is_file():
        verified_archive(stage, snapshot)
        return
    with target.open("wb") as out:
        for item in snapshot["parts"]:
            part = stage / item["name"]
            if part.stat().st_size != item["bytes"] or sha256(part) != item["sha256"]:
                target.unlink(missing_ok=True)
                raise ValueError(f"Private Release part hash failed: {part}")
            with part.open("rb") as inp:
                shutil.copyfileobj(inp, out, length=BUFFER)
    verified_archive(stage, snapshot)


def upload(stage: Path, repo: str) -> None:
    branch = ensure_private(repo)
    data = validate_manifest(stage)
    if data["archive_repo"] != repo:
        raise ValueError("Staged manifest targets a different private repository")
    # Full preflight of all local chunks BEFORE remote write.
    for snapshot in data["snapshots"]:
        reconstruct(stage, snapshot)
        for part in snapshot["parts"]:
            path = stage / part["name"]
            if path.stat().st_size != part["bytes"] or sha256(path) != part["sha256"]:
                raise ValueError(f"Invalid local staging chunk: {path}")
    create_or_check_release(
        repo, TAG, branch, "Kerala2040 PRIVATE five original folder snapshots"
    )
    for snapshot in data["snapshots"]:
        for part in snapshot["parts"]:
            upload_exact_asset(
                repo, TAG, stage / part["name"], part["bytes"], part["sha256"]
            )
    manifest = stage / MANIFEST_NAME
    upload_exact_asset(
        repo, TAG, manifest, manifest.stat().st_size, sha256(manifest)
    )
    print("Uploaded five folder snapshots to PRIVATE Release. Run --verify to test download.")


def verify(stage: Path, repo: str, reference_manifest: Path) -> None:
    ensure_private(repo)
    stage.mkdir(parents=True, exist_ok=True)
    # Manifest is remote, not silently reused from local source folders.
    local_manifest = stage / MANIFEST_NAME
    if local_manifest.exists():
        raise ValueError(
            "Use a NEW/EMPTY restore directory: local manifest could mask "
            "a missing remote archive."
        )
    from private_archive_utils import gh

    gh(
        "release", "download", TAG, "--repo", repo, "--dir", str(stage),
        "--pattern", MANIFEST_NAME, capture=False,
    )
    if not reference_manifest.is_file():
        raise FileNotFoundError(f"Trusted source manifest missing: {reference_manifest}")
    if sha256(local_manifest) != sha256(reference_manifest):
        raise ValueError("Remote manifest differs from LOCAL trusted preparation manifest")
    data = validate_manifest(stage)
    if data["archive_repo"] != repo:
        raise ValueError("Remote manifest references a different repository")
    for snap in data["snapshots"]:
        for part in snap["parts"]:
            restore_exact_asset(
                repo, TAG, part["name"], stage, part["bytes"], part["sha256"]
            )
        reconstruct(stage, snap)
    print("SUCCESS: all five PRIVATE folder snapshots and EVERY nested file SHA256 verified.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--source-root", type=Path)
    mode.add_argument("--upload", action="store_true")
    mode.add_argument("--verify", action="store_true")
    parser.add_argument("--staging-dir", type=Path, required=True)
    parser.add_argument("--archive-repo", default=PRIVATE_ARCHIVE)
    parser.add_argument("--reference-manifest", type=Path)
    args = parser.parse_args()
    if args.source_root is not None:
        prepare(args.source_root, args.staging_dir)
    elif args.upload:
        upload(args.staging_dir.resolve(), args.archive_repo)
    else:
        if args.reference_manifest is None:
            parser.error("--verify requires --reference-manifest from local preparation")
        verify(
            args.staging_dir.resolve(), args.archive_repo,
            args.reference_manifest.resolve(),
        )


if __name__ == "__main__":
    main()
