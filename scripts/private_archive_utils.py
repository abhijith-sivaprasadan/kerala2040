"""Private GitHub source-archive safety and integrity utilities.

NEVER upload third-party original datasets to the public Kerala2040 repository.
The separate archive must exist and be PRIVATE on GitHub before any upload or
download. Private access does not override publisher terms or sharing rights.
"""
from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
from pathlib import Path

MAIN_REPO = "abhijith-sivaprasadan/kerala2040"
PRIVATE_ARCHIVE = "abhijith-sivaprasadan/kerala2040-source-archive"


def sha256(path: Path) -> str:
    result = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(4 * 1024 * 1024), b""):
            result.update(chunk)
    return result.hexdigest()


def gh(*args: str, capture: bool = True) -> str:
    if not shutil.which("gh"):
        raise RuntimeError("GitHub CLI (gh) is required; install then run gh auth login.")
    completed = subprocess.run(
        ["gh", *args],
        check=True,
        text=True,
        stdout=subprocess.PIPE if capture else None,
        stderr=subprocess.PIPE if capture else None,
    )
    return completed.stdout if capture else ""


def ensure_private(repo: str) -> str:
    """Fail BEFORE uploading anything when destination is missing or public."""
    if not repo or repo == MAIN_REPO:
        raise ValueError("Do not upload raw sources to the public Kerala2040 repository")
    details = json.loads(
        gh("repo", "view", repo, "--json", "isPrivate,defaultBranchRef")
    )
    if details.get("isPrivate") is not True:
        raise ValueError(f"Refusing source archive upload/download: {repo} is NOT PRIVATE")
    default_branch = (details.get("defaultBranchRef") or {}).get("name")
    if not default_branch:
        raise ValueError(
            "Private archive repo needs an initial commit/README before Releases"
        )
    return default_branch


def assert_original(path: Path, bytes_expected: int, hash_expected: str) -> None:
    if not path.is_file():
        raise FileNotFoundError(f"Original source not found: {path}")
    if path.stat().st_size != bytes_expected:
        raise ValueError(f"Original byte-size mismatch: {path}")
    if sha256(path) != hash_expected:
        raise ValueError(f"Original SHA256 mismatch: {path}")



def find_originals_in_folders(
    root: Path, assets: list[dict],
) -> dict[str, Path]:
    """Find all exact original files recursively; compare actual bytes and SHA.

    A ZIP made from an extracted folder is NOT the byte-identical original ZIP,
    and it cannot satisfy an original ZIP's pinned SHA256.
    """
    if not root.is_dir():
        raise NotADirectoryError(f"Source folder not found: {root}")
    expected = {a["name"]: a for a in assets}
    if len(expected) != len(assets) or any(
        Path(n).name != n for n in expected
    ):
        raise ValueError("Manifest has duplicate or unsafe original filenames")
    found: dict[str, list[Path]] = {name: [] for name in expected}
    for candidate in root.rglob("*"):
        if candidate.name in expected and candidate.is_file() and not candidate.is_symlink():
            found[candidate.name].append(candidate)
    result: dict[str, Path] = {}
    problems = []
    for name, item in expected.items():
        candidates = sorted(found[name], key=lambda p: (len(p.parts), str(p)))
        if not candidates:
            problems.append(
                f"MISSING original {name}; extracted folders cannot recreate "
                "the original ZIP's exact SHA256"
            )
            continue
        size_matches = [p for p in candidates if p.stat().st_size == item["bytes"]]
        if not size_matches:
            problems.append(
                f"SIZE mismatch for {name}: {len(candidates)} namesake(s), "
                f"expected {item['bytes']} bytes"
            )
            continue
        valid = [p for p in size_matches if sha256(p) == item["sha256"]]
        if not valid:
            problems.append(
                f"SHA256 mismatch for {name}: {len(size_matches)} size-matching file(s)"
            )
            continue
        # Identical copies are harmless; preserve the shallowest exact original.
        result[name] = valid[0]
        print(f"VERIFIED original: {result[name]}", flush=True)
    if problems:
        raise ValueError(
            "No files were uploaded. Recursive preflight failed:\n"
            + "\n".join(problems)
        )
    return result

def view_release(repo: str, tag: str) -> dict | None:
    """Distinguish a missing tag from a denied request where possible."""
    import subprocess as _subprocess

    if not shutil.which("gh"):
        raise RuntimeError("GitHub CLI is not installed")
    completed = _subprocess.run(
        ["gh", "release", "view", tag, "--repo", repo,
         "--json", "assets,isDraft"],
        text=True, capture_output=True, check=False,
    )
    if completed.returncode == 0:
        return json.loads(completed.stdout)
    message = (completed.stderr + completed.stdout).lower()
    if "release not found" in message or "not found" in message:
        return None
    raise RuntimeError(
        "Cannot check existing private source release: "
        + (completed.stderr.strip() or completed.stdout.strip())[:300]
    )


def create_or_check_release(repo: str, tag: str, branch: str, title: str) -> None:
    current = view_release(repo, tag)
    if current is None:
        gh(
            "release", "create", tag, "--repo", repo, "--target", branch,
            "--title", title,
            "--notes", (
                "PRIVATE access only. Original research source archives. "
                "Publisher terms still apply; do not mirror publicly. "
                "Source identity is pinned by SHA256 in public Kerala2040 metadata."
            ),
            capture=False,
        )


def upload_exact_asset(
    repo: str, tag: str, source: Path, expected_bytes: int, expected_hash: str,
) -> None:
    assert_original(source, expected_bytes, expected_hash)
    current = view_release(repo, tag)
    if current is None:
        raise RuntimeError("Create private release before uploading source assets")
    matching = [a for a in current["assets"] if a["name"] == source.name]
    if matching:
        if len(matching) != 1 or matching[0]["size"] != expected_bytes:
            raise ValueError(
                f"An existing remote asset has different byte size: {source.name}. "
                "Never silently overwrite private source archives."
            )
        print(f"Remote asset already present by name/size: {source.name}")
        return
    gh(
        "release", "upload", tag, str(source), "--repo", repo,
        capture=False,
    )
    again = view_release(repo, tag)
    matches = [a for a in again["assets"] if a["name"] == source.name]
    if len(matches) != 1 or matches[0]["size"] != expected_bytes:
        raise RuntimeError(f"Private Release asset upload not verified: {source.name}")
    print(f"Uploaded {source.name}; remote size verified; SHA download test still required")


def restore_exact_asset(
    repo: str, tag: str, name: str, dest: Path, expected_bytes: int,
    expected_hash: str,
) -> None:
    dest.mkdir(parents=True, exist_ok=True)
    target = dest / name
    if target.is_file():
        assert_original(target, expected_bytes, expected_hash)
        print(f"VERIFIED cached original: {name}")
        return
    gh(
        "release", "download", tag, "--repo", repo, "--dir", str(dest),
        "--pattern", name, capture=False,
    )
    try:
        assert_original(target, expected_bytes, expected_hash)
    except (OSError, ValueError):
        target.unlink(missing_ok=True)
        raise
    print(f"VERIFIED RESTORED original SHA256: {name}")
