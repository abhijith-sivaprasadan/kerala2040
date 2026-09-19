"""Attempt the eleven source-identified missing SLDC historical Generation reports."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from kerala2040.sldc_gap_recovery import probe_from_committed_qa
from kerala2040.sources.http import build_session


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("results/acquisition/sldc_missing_dates"),
    )
    parser.add_argument("--pause", type=float, default=0.8)
    args = parser.parse_args()
    if args.pause < 0:
        parser.error("--pause must not be negative")
    with build_session() as session:
        result = probe_from_committed_qa(
            args.root, args.output, session, pause_seconds=args.pause
        )
    print(
        json.dumps(
            {
                "classification": result["classification"],
                "generation_candidates": result["recovered_generation_candidates"],
                "not_recovered": result["not_recovered"],
                "dates": [
                    {
                        "date": row["requested_date"],
                        "status": row["status"],
                        "attempts": [
                            {
                                "endpoint": attempt["endpoint"],
                                "result": attempt["result"],
                                "returned_report_date": attempt.get(
                                    "returned_report_date"
                                ),
                                "http_status": attempt.get("http_status"),
                                "detail": attempt.get("detail"),
                            }
                            for attempt in row["attempts"]
                        ],
                    }
                    for row in result["records"]
                ],
                "audit_gate_closed": result["audit_gate_closed"],
                "known_observed_control_status": result["known_observed_control_status"],
                "interpretation": result["interpretation"],
                "report": str(args.output / "attempts.json"),
            },
            indent=2,
        )
    )
    # Non-recovery is a documented source acquisition outcome, not a CI failure.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
