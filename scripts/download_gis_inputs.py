"""Download directly accessible GIS inputs without claiming they are model-ready."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from urllib.parse import urlparse

import requests
import yaml


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _safe_direct_url(url: str) -> bool:
    parsed = urlparse(url)
    return parsed.scheme == "https" and bool(parsed.netloc)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=Path("configs/gis_inputs.yaml"))
    parser.add_argument(
        "--manifest",
        type=Path,
        default=Path("results/gis/gis_download_manifest.json"),
    )
    parser.add_argument("--timeout", type=float, default=120.0)
    parser.add_argument("--max-mb", type=float, default=750.0)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    config = yaml.safe_load(args.config.read_text(encoding="utf-8"))
    max_bytes = int(args.max_mb * 1024 * 1024)
    records = []

    session = requests.Session()
    session.headers.update({"User-Agent": "Kerala2040Research/1.0"})
    try:
        for layer_id, item in config["layers"].items():
            url = item.get("url")
            path = Path(item["raw_path"])
            record = {
                "layer_id": layer_id,
                "classification": "unresolved",
                "source_type": "official_gis_source",
                "source": item["source"],
                "url": url or item.get("landing_page"),
                "role": item["role"],
                "path": str(path),
                "status": None,
            }

            if not url:
                record["status"] = "manual_or_gated_acquisition_required"
                records.append(record)
                continue
            if not _safe_direct_url(str(url)):
                record["status"] = "invalid_or_unsupported_url"
                records.append(record)
                continue

            if path.exists() and path.is_file() and not args.force:
                record.update(
                    {
                        "classification": "official_observed_reference",
                        "status": "already_present",
                        "bytes": path.stat().st_size,
                        "sha256": _sha256(path),
                    }
                )
                records.append(record)
                continue

            path.parent.mkdir(parents=True, exist_ok=True)
            temp = path.with_suffix(path.suffix + ".part")
            try:
                with session.get(str(url), stream=True, timeout=args.timeout) as response:
                    response.raise_for_status()
                    expected = int(response.headers.get("Content-Length", "0") or 0)
                    if expected and expected > max_bytes:
                        raise ValueError(
                            f"content-length {expected} exceeds max {max_bytes} bytes"
                        )
                    size = 0
                    with temp.open("wb") as handle:
                        for chunk in response.iter_content(chunk_size=1024 * 1024):
                            if not chunk:
                                continue
                            size += len(chunk)
                            if size > max_bytes:
                                raise ValueError(
                                    f"download exceeded max {max_bytes} bytes"
                                )
                            handle.write(chunk)
                temp.replace(path)
                record.update(
                    {
                        "classification": "official_observed_reference",
                        "status": "downloaded_not_yet_model_ready",
                        "bytes": path.stat().st_size,
                        "sha256": _sha256(path),
                        "content_type": response.headers.get("Content-Type"),
                    }
                )
            except Exception as exc:  # noqa: BLE001 - retain per-layer acquisition evidence
                if temp.exists():
                    temp.unlink()
                record.update(
                    {
                        "status": "download_failed",
                        "error": f"{type(exc).__name__}: {exc}",
                    }
                )
            records.append(record)
    finally:
        session.close()

    result = {
        "classification": "derived_from_measured",
        "source_type": "gis_acquisition_manifest",
        "source": "Configured official GIS sources in configs/gis_inputs.yaml",
        "model_ready": False,
        "note": (
            "Downloaded files remain raw evidence. They are not model-ready until CRS, "
            "vintage, licence/access conditions and processing rules are validated."
        ),
        "records": records,
    }
    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    args.manifest.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
