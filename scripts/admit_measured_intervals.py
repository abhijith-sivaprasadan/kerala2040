"""Check a PRIVATE candidate FY2024-25 measured interval export (no gate promotion).

Input CSV is never copied, uploaded, committed, or published by this command.
QA output is a local report containing source identity and daily derived summaries.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from kerala2040.interval_admission import IntervalAdmissionError, inspect_interval_candidate


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv", type=Path, required=True,
                        help="Source-supplied normalized CSV; KEEP PRIVATE")
    parser.add_argument("--source-manifest", type=Path, required=True,
                        help="Explicit original source, metering scope, revision and SHA")
    parser.add_argument("--report", type=Path,
                        default=Path("data/processed/interval_candidate_qa.json"))
    args = parser.parse_args()
    if not args.csv.is_file() or not args.source_manifest.is_file():
        parser.error("both source CSV and manifest must be existing local files")
    if args.report.resolve() in {args.csv.resolve(), args.source_manifest.resolve()}:
        parser.error("report may not overwrite the input or its manifest")
    try:
        report = inspect_interval_candidate(args.csv, args.source_manifest)
    except (IntervalAdmissionError, ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"admitted": False, "scientific_gate_passed": False,
                          "reason": str(exc)}, indent=2))
        return 2
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n",
                           encoding="utf-8")
    print(json.dumps({"structurally_checked": True,
                      "scientific_gate_passed": False,
                      "model_ready": False,
                      "source_sha256": report["source_sha256"],
                      "observed_intervals": report["observed_intervals"],
                      "report": str(args.report)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
