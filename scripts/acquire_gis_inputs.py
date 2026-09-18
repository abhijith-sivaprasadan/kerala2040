"""Acquire only directly downloadable official GIS inputs and record exact provenance."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import requests
import yaml


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _download(url: str, output: Path, *, timeout: float = 120.0) -> dict[str, Any]:
    output.parent.mkdir(parents=True, exist_ok=True)
    with requests.get(url, timeout=timeout, stream=True) as response:
        response.raise_for_status()
        with output.open("wb") as handle:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    handle.write(chunk)
        return {
            "http_status": response.status_code,
            "content_type": response.headers.get("Content-Type"),
            "content_length_header": response.headers.get("Content-Length"),
            "final_url": response.url,
        }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=Path("configs/gis_inputs.yaml"))
    parser.add_argument(
        "--output", type=Path, default=Path("results/gis/gis_download_manifest.json")
    )
    parser.add_argument("--refresh", action="store_true")
    args = parser.parse_args()

    config = yaml.safe_load(args.config.read_text(encoding="utf-8"))
    records: list[dict[str, Any]] = []

    for layer_id, item in config["layers"].items():
        direct_url = item.get("url")
        target = Path(item["raw_path"])
        record: dict[str, Any] = {
            "layer_id": layer_id,
            "classification": "unresolved",
            "source": item["source"],
            "source_url": direct_url or item.get("landing_page"),
            "configured_status": item["acquisition_status"],
            "raw_path": str(target),
        }

        if not direct_url:
            record["acquisition_result"] = "not_attempted_no_direct_download"
            records.append(record)
            continue

        parsed = urlparse(direct_url)
        if parsed.scheme not in {"http", "https"}:
            record["acquisition_result"] = "invalid_direct_url"
            records.append(record)
            continue

        try:
            if target.exists() and not args.refresh:
                response_meta: dict[str, Any] = {"reused_existing_file": True}
            else:
                response_meta = _download(direct_url, target)
            record.update(response_meta)
            record.update(
                {
                    "classification": "official_observed_reference",
                    "acquisition_result": "downloaded",
                    "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
                    "bytes": target.stat().st_size,
                    "sha256": sha256_file(target),
                    "model_ready": False,
                    "model_ready_note": (
                        "Acquired official raw input only; CRS, vintage, licence and "
                        "processing rules still require validation."
                    ),
                }
            )
        except Exception as exc:  # noqa: BLE001 - preserve layer-level failure evidence
            record["acquisition_result"] = "failed"
            record["error"] = f"{type(exc).__name__}: {exc}"
        records.append(record)

    successful = [record for record in records if record["acquisition_result"] == "downloaded"]
    result = {
        "classification": "derived_from_measured",
        "source": "Official agencies identified per GIS layer",
        "records": records,
        "downloaded_count": len(successful),
        "layer_count": len(records),
        "model_ready": False,
        "model_ready_note": "Acquisition is not equivalent to a processed GIS exclusion model.",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
