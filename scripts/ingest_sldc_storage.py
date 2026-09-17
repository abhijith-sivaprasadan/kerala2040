#!/usr/bin/env python
"""Download a range of Kerala SLDC reservoir-storage reports."""

from __future__ import annotations

import argparse
import json
import time
from datetime import date, timedelta
from pathlib import Path

from kerala2040.provenance import build_manifest, write_manifest
from kerala2040.sources.http import build_session
from kerala2040.sources.sldc_storage import fetch_storage, storage_frames


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", required=True, type=date.fromisoformat)
    parser.add_argument("--end", required=True, type=date.fromisoformat)
    parser.add_argument(
        "--output", type=Path, default=Path("data/processed/sldc_storage_daily.parquet")
    )
    parser.add_argument(
        "--reservoir-output",
        type=Path,
        default=Path("data/processed/sldc_storage_reservoirs.parquet"),
    )
    parser.add_argument("--delay-seconds", type=float, default=0.8)
    parser.add_argument("--allow-gaps", action="store_true")
    args = parser.parse_args()

    if args.end < args.start:
        raise ValueError("end must be on or after start")
    records = []
    failures = []
    current = args.start
    with build_session() as session:
        while current <= args.end:
            try:
                records.append(fetch_storage(current, session=session))
            except Exception as exc:  # noqa: BLE001 - preserve date-level acquisition failures
                failures.append({"date": current.isoformat(), "error": str(exc)})
            current += timedelta(days=1)
            if current <= args.end and args.delay_seconds > 0:
                time.sleep(args.delay_seconds)

    daily, reservoirs = storage_frames(records)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    daily.to_parquet(args.output, index=False)
    args.reservoir_output.parent.mkdir(parents=True, exist_ok=True)
    reservoirs.to_parquet(args.reservoir_output, index=False)
    failure_path = args.output.with_suffix(".failures.json")
    failure_path.write_text(json.dumps(failures, indent=2), encoding="utf-8")

    manifest = build_manifest(
        command="scripts/ingest_sldc_storage.py",
        parameters={
            "start": args.start.isoformat(),
            "end": args.end.isoformat(),
            "delay_seconds": args.delay_seconds,
            "failures": len(failures),
        },
        sources=[record["provenance"] for record in records],
        outputs=[str(args.output), str(args.reservoir_output), str(failure_path)],
    )
    write_manifest(args.output.with_suffix(".manifest.json"), manifest)
    print(f"wrote {len(daily)} daily rows and {len(reservoirs)} reservoir rows")
    print(f"failures: {len(failures)}")
    return 0 if (args.allow_gaps or not failures) else 2


if __name__ == "__main__":
    raise SystemExit(main())
