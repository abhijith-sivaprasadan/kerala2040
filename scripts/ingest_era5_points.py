"""Retrieve bounded FY2024-25 ERA5 hourly Kerala representative-point chunks.

The public manifest is historical evidence, not a live file cache. This script
writes a *separate* source-attempt manifest and keeps original NetCDF bytes in
a private workflow artifact. No selective run may overwrite a public complete-
year weather record or self-certify generation resource-model readiness.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from kerala2040.sources.era5 import DATASET, PERIODS, POINTS, VARIABLES, request_for

PERIOD_LABELS = {label for label, _, _ in PERIODS}
NETCDF_SIGNATURES = (bytes.fromhex("43444601"), bytes.fromhex("43444602"), bytes.fromhex("894844460d0a1a0a"))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def choose_requests(
    points: list[str], periods: list[str], max_requests: int
) -> list[tuple[str, float, float, str, str, list[str]]]:
    """Reject mistaken point/period filters before spending CDS request budget."""
    if max_requests <= 0 or len(points) != len(set(points)) or len(periods) != len(set(periods)):
        raise ValueError("Positive max requests and unique point/period names are required")
    if not points or not periods or any(name not in POINTS for name in points):
        raise ValueError("Unknown or empty ERA5 point selection")
    if any(period not in PERIOD_LABELS for period in periods):
        raise ValueError("Unknown ERA5 quarter label")
    chosen = []
    for point in points:
        lat, lon = POINTS[point]
        for label, year, months in PERIODS:
            if label in periods:
                chosen.append((point, lat, lon, label, year, months))
    return chosen[:max_requests]


def valid_netcdf(path: Path) -> bool:
    """Minimal file-format guard; time/unit/source admission is a later QA."""
    if not path.is_file() or path.stat().st_size < 4096:
        return False
    with path.open("rb") as handle:
        signature = handle.read(8)
    return any(signature.startswith(magic) for magic in NETCDF_SIGNATURES)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw-dir", type=Path, default=Path("data/raw/era5"))
    parser.add_argument(
        "--manifest", type=Path,
        default=Path("results/acquisition/era5/retrieval_attempt.json"),
    )
    parser.add_argument("--points", nargs="+", choices=list(POINTS), default=list(POINTS))
    parser.add_argument(
        "--periods", nargs="+", choices=sorted(PERIOD_LABELS),
        default=[label for label, _, _ in PERIODS],
    )
    parser.add_argument("--max-requests", type=int, default=len(POINTS) * len(PERIODS))
    args = parser.parse_args()
    requests = choose_requests(args.points, args.periods, args.max_requests)

    # Do not publish an empty or misleading manifest when a secret is missing.
    if not os.getenv("CDSAPI_KEY"):
        raise RuntimeError("CDSAPI_KEY is required; no source retrieval was attempted")

    # CI need not install cdsapi just to test the pure request-selection functions.
    import cdsapi

    client = cdsapi.Client(
        url=os.getenv("CDSAPI_URL", "https://cds.climate.copernicus.eu/api"),
        key=os.environ["CDSAPI_KEY"],
        quiet=True, progress=False, timeout=180, sleep_max=30, retry_max=20,
    )
    args.raw_dir.mkdir(parents=True, exist_ok=True)
    files: list[dict[str, Any]] = []
    failures: list[dict[str, str]] = []

    fallbacks: list[dict[str, str]] = []
    completed_windows = 0
    requests_sent = 0

    for point, lat, lon, label, year, months in requests:
        chunks = [(label, months)]
        fallback_reason = None
        quarter_succeeded = True

        while chunks:
            chunk_label, chunk_months = chunks.pop(0)
            target = args.raw_dir / f"era5_{point}_{chunk_label}.nc"
            try:
                # Never accept a left-over source file for a failed current request.
                target.unlink(missing_ok=True)
                requests_sent += 1
                client.retrieve(DATASET, request_for(lat, lon, year, chunk_months), str(target))
                if not valid_netcdf(target):
                    raise ValueError("CDS output is empty, truncated or not NetCDF/HDF5")
                files.append({
                    "point": point, "latitude": lat, "longitude": lon,
                    "period": chunk_label, "selected_quarter": label,
                    "months": chunk_months, "path": str(target),
                    "bytes": target.stat().st_size, "sha256": sha256(target),
                })
            except Exception as exc:  # noqa: BLE001 - retain per-request evidence
                target.unlink(missing_ok=True)
                reason = f"{type(exc).__name__}: {exc}"
                oversized = ("cost limits exceeded" in reason.lower()
                             or "request is too large" in reason.lower())
                if oversized and len(chunk_months) > 1:
                    fallback_reason = reason
                    fallbacks.append({
                        "point": point, "selected_quarter": label,
                        "failed_window": chunk_label, "error": reason,
                        "action": "split_into_individual_months",
                    })
                    chunks = [
                        (f"{year}-{month}", [month]) for month in chunk_months
                    ] + chunks
                else:
                    quarter_succeeded = False
                    failures.append({
                        "point": point, "period": chunk_label,
                        "selected_quarter": label, "error": reason,
                    })
        if quarter_succeeded:
            completed_windows += 1
        if fallback_reason:
            print(f"ERA5 {point} {label}: three-month CDS request was too large;"
                  " attempted individual months", flush=True)

    expected = len(POINTS) * len(PERIODS)
    payload = {
        "retrieved_at_utc": datetime.now(UTC).replace(microsecond=0).isoformat(),
        "classification": "reanalysis_retrieval_attempt_not_validated_resource_model",
        "dataset": DATASET,
        "dataset_url": "https://cds.climate.copernicus.eu/datasets/reanalysis-era5-single-levels",
        "temporal_resolution": "hourly",
        "model_period": "2024-04-01 to 2025-03-31",
        "variables": VARIABLES,
        "spatial_method": "representative point boxes; not statewide resource-potential mapping",
        "request_plan": "five Kerala points times four FY2024-25 three-month chunks",
        "selection": {"points": args.points, "periods": args.periods,
                      "max_requests": args.max_requests},
        "files_attempted": len(requests),
        "files_succeeded": len(files),
        "windows_completed": completed_windows,
        "source_requests_sent": requests_sent,
        "oversized_window_fallbacks": fallbacks,
        "files_expected": expected,
        "files_not_attempted": expected - len(requests),
        "files": files,
        "failures": failures,
        "scope_warning": (
            "Selective attempts and source-byte hashes do not certify a complete "
            "FY2024-25 weather chronology, Kerala-wide resource map or generation profile. "
            "Do not replace the public ERA5 manifest with this partial attempt."
        ),
    }
    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    args.manifest.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "files_succeeded": len(files), "windows_completed": completed_windows,
        "source_requests_sent": requests_sent, "files_attempted": len(requests),
        "files_expected": expected, "failures": len(failures),
        "manifest": str(args.manifest),
    }, indent=2))
    return 0 if completed_windows == len(requests) else 2


if __name__ == "__main__":
    raise SystemExit(main())
