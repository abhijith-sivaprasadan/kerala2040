"""Retry the exact FY2024-25 missing Kerala SLDC Storage dates."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from requests import Session

from kerala2040.sldc_storage_gap_recovery import probe_storage_dates

MISSING = [
    "2024-08-12",
    "2024-09-06",
    "2024-09-20",
    "2024-10-26",
    "2024-11-17",
    "2024-11-30",
    "2024-12-16",
    "2025-02-19",
    "2025-03-05",
    "2025-03-10",
    "2025-03-17",
]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("results/audit/sldc_storage_gap_recovery_v14"),
    )
    parser.add_argument("--pause-seconds", type=float, default=0.8)
    args = parser.parse_args()

    with Session() as session:
        session.headers.update({
            "User-Agent": (
                "Kerala2040 research source-recovery audit; "
                "https://github.com/abhijith-sivaprasadan/kerala2040"
            )
        })
        report = probe_storage_dates(
            MISSING,
            args.out,
            session,
            pause_seconds=args.pause_seconds,
        )
    print(json.dumps({
        "recovered_storage_candidates": report["recovered_storage_candidates"],
        "not_recovered": report["not_recovered"],
        "known_observed_control_status": report["known_observed_control_status"],
        "out": str(args.out),
    }, indent=2))


if __name__ == "__main__":
    main()
