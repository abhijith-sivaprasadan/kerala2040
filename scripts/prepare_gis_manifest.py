"""Inventory locally acquired GIS inputs and preserve hashes/provenance."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import yaml


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=Path("configs/gis_inputs.yaml"))
    parser.add_argument(
        "--output", type=Path, default=Path("results/gis/gis_input_manifest.json")
    )
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()

    config = yaml.safe_load(args.config.read_text(encoding="utf-8"))
    records = []
    for layer_id, item in config["layers"].items():
        path = Path(item["raw_path"])
        exists = path.exists()
        record = {
            "layer_id": layer_id,
            "source": item["source"],
            "url": item.get("url") or item.get("landing_page"),
            "role": item["role"],
            "expected_format": item["expected_format"],
            "raw_path": str(path),
            "configured_status": item["acquisition_status"],
            "local_exists": exists,
            "local_type": "directory" if exists and path.is_dir() else "file" if exists else None,
            "sha256": sha256_file(path) if exists and path.is_file() else None,
            "bytes": path.stat().st_size if exists and path.is_file() else None,
        }
        records.append(record)

    missing = [record["layer_id"] for record in records if not record["local_exists"]]
    result = {
        "classification": "gis_local_acquisition_manifest",
        "target_crs": config["processing_contract"]["target_crs"],
        "records": records,
        "available_count": len(records) - len(missing),
        "missing_count": len(missing),
        "missing_layers": missing,
        "model_ready": False,
        "model_ready_reason": (
            "Raw presence alone is insufficient; CRS, vintage, licence and processing "
            "metadata must also be validated before capacity ceilings are generated."
        ),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 2 if args.strict and missing else 0


if __name__ == "__main__":
    raise SystemExit(main())
