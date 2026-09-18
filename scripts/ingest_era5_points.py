"""Retrieve FY2024-25 ERA5 hourly weather at representative Kerala points.

Raw NetCDF files are kept as workflow artifacts rather than committed to git. A compact
manifest is written to data/processed for provenance and web-publication.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from datetime import UTC, datetime
from pathlib import Path
import cdsapi

from kerala2040.sources.era5 import DATASET, PERIODS, POINTS, VARIABLES, request_for

def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def request_for(lat: float, lon: float, year: str, months: list[str]) -> dict[str, Any]:
    # Request a small box around each representative location. ERA5 is 0.25 degrees,
    # so this resolves to the nearest small set of grid cells without claiming statewide
    # spatial coverage.
    pad = 0.13
    return {
        "product_type": ["reanalysis"],
        "variable": VARIABLES,
        "year": [year],
        "month": months,
        "day": DAYS,
        "time": HOURS,
        "data_format": "netcdf",
        "download_format": "unarchived",
        "area": [lat + pad, lon - pad, lat - pad, lon + pad],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw-dir", type=Path, default=Path("data/raw/era5"))
    parser.add_argument(
        "--manifest",
        type=Path,
        default=Path("data/processed/era5_daily_manifest.json"),
    )
    args = parser.parse_args()

    if not os.getenv("CDSAPI_KEY"):
        raise RuntimeError("CDSAPI_KEY is required")
    url = os.getenv("CDSAPI_URL", "https://cds.climate.copernicus.eu/api")
    client = cdsapi.Client(
        url=url,
        key=os.environ["CDSAPI_KEY"],
        quiet=True,
        progress=False,
        timeout=180,
        sleep_max=30,
        retry_max=20,
    )

    args.raw_dir.mkdir(parents=True, exist_ok=True)
    files: list[dict[str, Any]] = []
    failures: list[dict[str, str]] = []

    for point, (lat, lon) in POINTS.items():
        for label, year, months in PERIODS:
            target = args.raw_dir / f"era5_{point}_{label}.nc"
            try:
                client.retrieve(
                    DATASET,
                    request_for(lat, lon, year, months),
                    str(target),
                )
                if not target.exists() or target.stat().st_size == 0:
                    raise RuntimeError("CDS returned no non-empty file")
                files.append(
                    {
                        "point": point,
                        "latitude": lat,
                        "longitude": lon,
                        "period": label,
                        "path": str(target),
                        "bytes": target.stat().st_size,
                        "sha256": sha256(target),
                    }
                )
            except Exception as exc:  # noqa: BLE001 - preserve per-request evidence
                failures.append(
                    {
                        "point": point,
                        "period": label,
                        "error": f"{type(exc).__name__}: {exc}",
                    }
                )

    payload = {
        "retrieved_at_utc": datetime.now(UTC).replace(microsecond=0).isoformat(),
        "classification": "reanalysis_input",
        "dataset": DATASET,
        "dataset_url": "https://cds.climate.copernicus.eu/datasets/reanalysis-era5-single-levels",
        "temporal_resolution": "hourly",
        "model_period": "2024-04-01 to 2025-03-31",
        "variables": VARIABLES,
        "spatial_method": "representative point boxes; not statewide resource-potential mapping",
        "files_succeeded": len(files),
        "files_expected": len(POINTS) * len(PERIODS),
        "files": files,
        "failures": failures,
    }
    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    args.manifest.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(
        json.dumps(
            {
                "files_succeeded": len(files),
                "files_expected": len(POINTS) * len(PERIODS),
                "failures": len(failures),
            },
            indent=2,
        )
    )
    return 0 if files else 2


if __name__ == "__main__":
    raise SystemExit(main())
