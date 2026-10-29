#!/usr/bin/env python3
"""Offline structural audit of the Kerala2040 literature programme.

This validates machine-readable metadata; it NEVER certifies DOI publisher
resolution, study relevance, peer-review, full-text access or scientific results.

Usage:
    python research/literature/audit_master_catalogue.py
    python research/literature/audit_master_catalogue.py --json
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DOI = re.compile(r"^10\.\d{4,9}/\S+$", re.IGNORECASE)
PAPERS = ROOT / "MASTER_PAPERS_R01_R23.csv"
ROADMAP = ROOT / "ROUND_ROADMAP_R01_R23.csv"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def check() -> tuple[dict, list[str]]:
    issues: list[str] = []
    if not PAPERS.is_file() or not ROADMAP.is_file():
        return {}, ["Missing master papers or roadmap file"]

    records = read_csv(PAPERS)
    rounds = read_csv(ROADMAP)
    by_round = Counter()
    by_doi: dict[str, list[dict]] = defaultdict(list)

    roadmap_ids = []
    for record in rounds:
        try:
            round_id = int(record["round"])
        except (ValueError, KeyError):
            issues.append(f"Invalid roadmap round: {record!r}")
            continue
        roadmap_ids.append(round_id)
        try:
            n = int(record["papers_in_catalogue"])
        except (ValueError, KeyError):
            issues.append(f"Invalid roadmap count for R{round_id}")
            continue
        if not 20 <= n <= 40:
            issues.append(f"R{round_id}: expected count outside 20..40")

    if sorted(roadmap_ids) != list(range(1, 24)):
        issues.append("Roadmap must have exactly R1..R23 once each")

    for index, row in enumerate(records, start=2):
        try:
            r = int(row["round"])
        except (ValueError, KeyError):
            issues.append(f"Master row {index}: invalid round")
            continue
        by_round[r] += 1
        if not (row.get("title") or "").strip():
            issues.append(f"Master row {index}: blank title")
        doi = (row.get("doi") or "").strip()
        if doi:
            if not DOI.fullmatch(doi):
                issues.append(f"Master row {index}: malformed DOI {doi}")
            if (row.get("doi_url") or "").lower() != ("https://doi.org/" + doi).lower():
                issues.append(f"Master row {index}: DOI resolver mismatch {doi}")
            by_doi[doi.lower()].append(row)
        elif r != 2:
            issues.append(f"Master row {index}: DOI missing outside R2")

    roadmap_map = {int(r["round"]): int(r["papers_in_catalogue"])
                   for r in rounds if r.get("round", "").isdigit()
                   and r.get("papers_in_catalogue", "").isdigit()}
    for r in range(1, 24):
        observed = by_round[r]
        if not 20 <= observed <= 40:
            issues.append(f"R{r}: {observed} candidates outside 20..40")
        if roadmap_map.get(r) != observed:
            issues.append(f"R{r}: roadmap count and master count differ")

    duplicate_doi = {
        doi: sorted(set(int(x["round"]) for x in items))
        for doi, items in by_doi.items() if len(items) > 1
    }
    missing = sum(1 for x in records if not x.get("doi", "").strip())
    report = {
        "round_count": len(roadmap_ids),
        "candidate_rows": len(records),
        "papers_per_round": dict(sorted(by_round.items())),
        "doi_entries": sum(len(x) for x in by_doi.values()),
        "unique_dois": len(by_doi),
        "missing_dois": missing,
        "cross_round_or_duplicate_dois": duplicate_doi,
        "metadata_authentication": "NOT_VALIDATED_BY_THIS_SCRIPT",
        "human_relevance_screen": "REQUIRED",
        "full_text_appraisal": "NOT_INFERRED",
        "issues": issues,
    }
    return report, issues


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true", help="Machine JSON output")
    args = parser.parse_args()
    report, issues = check()
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(f"Rounds: {report.get('round_count', 0)}")
        print(f"Candidates: {report.get('candidate_rows', 0)}")
        print(f"DOI entries / unique: {report.get('doi_entries', 0)} / "
              f"{report.get('unique_dois', 0)}")
        print(f"Missing DOI: {report.get('missing_dois', 0)}")
        print(f"Structural issues: {len(issues)}")
        for issue in issues:
            print(" - " + issue, file=sys.stderr)
        print("This is metadata integrity only: relevance and source evidence remain open.")
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
