"""Validate and package one self-contained dashboard, without live API credentials."""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path


def validate_bundle(public: Path) -> dict:
    def read(name: str):
        path = (public / name).resolve()
        if path.parent != public.resolve() or path.suffix != ".json":
            raise ValueError(f"Invalid bundle filename: {name}")
        return json.loads(path.read_text(encoding="utf-8"))

    site = read("site-data.json")
    metadata = site["metadata"]
    files = metadata["files"]
    for name in files.values():
        read(name)
    if read("metadata.json") != metadata:
        raise ValueError("Manifest and metadata disagree")
    if metadata["status"]["sldc_daily"]["available"]:
        rows = read(files["daily_balance"])["records"]
        dates = [row["date"] for row in rows]
        if not rows or len(dates) != len(set(dates)) or dates != sorted(dates):
            raise ValueError("Daily evidence must contain unique, sorted dates")
        baseline = site.get("baseline")
        if baseline:
            if baseline["rows"] != len(rows):
                raise ValueError("Baseline and daily series come from different snapshots")
            total = sum(row["consumption_mu"] for row in rows) / 1000
            if abs(total - baseline["consumption_twh"]) > 0.000001:
                raise ValueError("Baseline energy does not match daily evidence")
    return site


def build_site(root: Path, output: Path) -> None:
    root, output = root.resolve(), output.resolve()
    if output == root or output == root / "docs" or output == root / "public":
        raise ValueError("Build into a separate directory, not a source directory")
    validate_bundle(root / "public")
    output.mkdir(parents=True, exist_ok=True)
    for name in ("index.html", "manifest.webmanifest", "robots.txt"):
        shutil.copy2(root / "docs" / name, output / name)
    shutil.copytree(root / "docs/assets", output / "assets", dirs_exist_ok=True)
    shutil.copytree(root / "public", output / "data", dirs_exist_ok=True)
    (output / ".nojekyll").touch()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output", type=Path, default=Path("_site"))
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.check:
        validate_bundle(args.root / "public")
        print("Public bundle is internally consistent")
    else:
        build_site(args.root, args.output)
        print(f"Dashboard ready: {args.output.resolve()}")
