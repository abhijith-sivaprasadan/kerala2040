#!/usr/bin/env python
"""Ingest official Grid-India Daily PSP state rows."""

from __future__ import annotations

import argparse
import json
import time
from datetime import date
from pathlib import Path

import pandas as pd
import requests

from kerala2040.sources.grid_india import (
    discover_daily_psp_files,
    download_report,
    legacy_report_entries,
    parse_mop_e_state,
)
from kerala2040.sources.http import build_session


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", required=True, type=date.fromisoformat)
    parser.add_argument("--end", required=True, type=date.fromisoformat)
    parser.add_argument("--state", default="Kerala")
    parser.add_argument("--output", type=Path, default=Path("data/processed/grid_india_psp.parquet"))
    parser.add_argument("--delay-seconds", type=float, default=0.25)
    parser.add_argument("--legacy-direct", action="store_true")
    parser.add_argument("--allow-insecure-tls-fallback", action="store_true")
    args = parser.parse_args()

    with build_session() as session:
        if args.legacy_direct:
            selected = legacy_report_entries(args.start, args.end)
        else:
            try:
                selected = discover_daily_psp_files(
                    args.start,
                    args.end,
                    session=session,
                    verify_tls=True,
                )
            except requests.exceptions.RequestException:
                if not args.allow_insecure_tls_fallback:
                    raise
                selected = discover_daily_psp_files(
                    args.start,
                    args.end,
                    session=session,
                    verify_tls=False,
                )

        rows = []
        failures = []
        for entry in selected:
            try:
                try:
                    content, provenance = download_report(entry, session=session, verify_tls=True)
                except requests.exceptions.RequestException:
                    if not args.allow_insecure_tls_fallback:
                        raise
                    content, provenance = download_report(entry, session=session, verify_tls=False)
                row = parse_mop_e_state(
                    content,
                    state=args.state,
                    filename=str(provenance["file_path"]),
                )
                rows.append({"date": pd.Timestamp(entry["report_date"]), **row, **provenance})
            except Exception as exc:  # noqa: BLE001 - retain per-report failure instead of losing batch
                failures.append(
                    {
                        "date": entry.get("report_date"),
                        "file_path": entry.get("FilePath") or entry.get("Title_"),
                        "error": str(exc),
                    }
                )
            if args.delay_seconds > 0:
                time.sleep(args.delay_seconds)

    frame = pd.DataFrame(rows)
    if not frame.empty:
        frame = frame.sort_values("date").reset_index(drop=True)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    frame.to_parquet(args.output, index=False)
    failure_path = args.output.with_suffix(".failures.json")
    failure_path.write_text(json.dumps(failures, indent=2), encoding="utf-8")
    print(f"Grid-India files selected: {len(selected)}; parsed: {len(frame)}; failures: {len(failures)}")
    return 0 if not frame.empty else 2


if __name__ == "__main__":
    raise SystemExit(main())
