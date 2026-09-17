"""Small provenance helpers used by all data connectors."""

from __future__ import annotations

import hashlib
import json
import platform
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from kerala2040 import __version__


def utc_now_iso() -> str:
    """Return an RFC3339-ish UTC timestamp without local-time ambiguity."""
    return datetime.now(UTC).isoformat()


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def git_sha() -> str | None:
    """Best-effort current git SHA; returns None outside a git checkout."""
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], text=True, stderr=subprocess.DEVNULL
        ).strip()
    except (OSError, subprocess.SubprocessError):
        return None


def build_manifest(
    *,
    command: str,
    sources: list[dict[str, Any]],
    parameters: dict[str, Any] | None = None,
    outputs: list[str] | None = None,
) -> dict[str, Any]:
    """Build a machine-readable run manifest."""
    return {
        "schema_version": 1,
        "project": "kerala2040",
        "project_version": __version__,
        "generated_at_utc": utc_now_iso(),
        "git_sha": git_sha(),
        "python": platform.python_version(),
        "command": command,
        "parameters": parameters or {},
        "sources": sources,
        "outputs": outputs or [],
    }


def write_manifest(path: str | Path, manifest: dict[str, Any]) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    return target
