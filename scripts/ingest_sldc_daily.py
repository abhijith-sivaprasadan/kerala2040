#!/usr/bin/env python
"""Download a date range of Kerala SLDC daily public statistics."""

from __future__ import annotations

import argparse
import json
import time
from datetime import date, timedelta
from pathlib import Path

from kerala2040.provenance import build_manifest, write_manifest
from kerala2040.sources.http import build_session
from kerala2040.sources.sldc import daily_frame, fetch_system_statistics


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", required=True, type=date.fromisoformat)
    parser.add_argument("--end", required=True, type=date.fromisoformat)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/processed/sldc_daily.parquet"),
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
                records.append(fetch_system_statistics(current, session=session))
            except Exception as exc:  # noqa: BLE001 - preserve date-level acquisition failures
                failures.append({"date": current.isoformat(), "error": str(exc)})
            current += timedelta(days=1)
            if current <= args.end and args.delay_seconds > 0:
                time.sleep(args.delay_seconds)

    frame = daily_frame(records)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    frame.to_parquet(args.output, index=False)
    failure_path = args.output.with_suffix(".failures.json")
    failure_path.write_text(json.dumps(failures, indent=2), encoding="utf-8")

    sources = [record["provenance"] for record in records]
    manifest = build_manifest(
        command="scripts/ingest_sldc_daily.py",
        parameters={
            "start": args.start.isoformat(),
            "end": args.end.isoformat(),
            "delay_seconds": args.delay_seconds,
            "failures": len(failures),
        },
        sources=sources,
        outputs=[str(args.output), str(failure_path)],
    )
    manifest_path = args.output.with_suffix(".manifest.json")
    write_manifest(manifest_path, manifest)
    print(f"wrote {len(frame)} rows -> {args.output}")
    print(f"failures: {len(failures)}")
    print(f"manifest -> {manifest_path}")
    return 0 if (args.allow_gaps or not failures) else 2


if __name__ == "__main__":
    raise SystemExit(main())
