"""Validate and package one self-contained dashboard, without live API credentials."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import shutil
from datetime import datetime, timedelta
from itertools import pairwise
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
    if "hourly_load_proxy_summary" in files:
        proxy = read(files["hourly_load_proxy_summary"])
        if proxy != site.get("hourly_load_proxy"):
            raise ValueError("Proxy summary and manifest disagree")
        if proxy.get("classification") != "proxy_reconstruction_not_measured_telemetry":
            raise ValueError("Hourly proxy must be explicitly classified as reconstruction")
        if "hourly_load_proxy" in files:
            product = read(files["hourly_load_proxy"])
            hourly = product["records"]
            if product.get("classification") != proxy["classification"]:
                raise ValueError("Hourly series classification disagrees with summary")
            times = [datetime.fromisoformat(row["timestamp"]) for row in hourly]
            if len(hourly) != proxy["hours"] or len(hourly) != 8760:
                raise ValueError("Hourly proxy must contain the complete FY2024-25 chronology")
            if times[0].isoformat() != "2024-04-01T00:00:00+05:30" or any(
                right - left != timedelta(hours=1) for left, right in pairwise(times)
            ):
                raise ValueError("Hourly proxy timestamps must be consecutive IST intervals")
            if any(not math.isfinite(row["load_mw"]) or row["load_mw"] <= 0 for row in hourly):
                raise ValueError("Hourly proxy contains invalid load values")
            if abs(sum(row["load_mw"] for row in hourly) / 1000 - proxy["annual_energy_mu"]) > 1e-6:
                raise ValueError("Hourly series energy disagrees with proxy summary")
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
    # Immutable filenames prevent a new HTML page from running an old cached app.
    html = (output / "index.html").read_text(encoding="utf-8")
    for name in ("app.js", "styles.css", "platform.css"):
        asset = root / "docs/assets" / name
        digest = hashlib.sha256(asset.read_bytes()).hexdigest()[:12]
        versioned = f"{asset.stem}.{digest}{asset.suffix}"
        shutil.copy2(asset, output / "assets" / versioned)
        html = html.replace(f"assets/{name}", f"assets/{versioned}")
    (output / "index.html").write_text(html, encoding="utf-8")
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
