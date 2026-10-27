#!/usr/bin/env python3
"""Static consistency checks for the publication literature evidence matrix.

No DOI network lookup or claim of full-text validity is made. Reproducible local
schema checks alone cannot certify the science or substitute human review.
"""
from __future__ import annotations

import csv
import re
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
CSV_PATH = HERE / "EVIDENCE_MATRIX.csv"
REVIEW_PATH = HERE / "CRITICAL_LITERATURE_REVIEW_V0_1.md"
PROTOCOL_PATH = HERE / "REVIEW_PROTOCOL_AND_SEARCH_LOG.md"
REQUIRED = [
    "id", "theme", "authors", "year", "title", "doi", "source_type",
    "access_level", "relevance", "source_contribution",
    "kerala2040_design_implication",
]
DOI_RE = re.compile(r"^10\.\d{4,9}/\S+$", re.I)
ID_RE = re.compile(r"^[A-Z]\d{2}$")
CITED_ID = re.compile(r"\[([A-Z]\d{2})\]")


def validate(path: Path = CSV_PATH, review_path: Path = REVIEW_PATH) -> dict:
    with path.open(newline="", encoding="utf-8-sig") as fp:
        reader = csv.DictReader(fp)
        if reader.fieldnames != REQUIRED:
            raise ValueError(f"Matrix headers differ from expected schema: {reader.fieldnames}")
        rows = list(reader)
    if not rows:
        raise ValueError("Matrix contains no source records")
    unique_ids = set()
    doi_keys = set()
    peer_count = 0
    unknown_authors = []
    access_types = Counter()
    for index, row in enumerate(rows, start=2):
        ref_id = row["id"].strip()
        if not ID_RE.fullmatch(ref_id):
            raise ValueError(f"Row {index}: invalid stable source identifier {ref_id!r}")
        if ref_id in unique_ids:
            raise ValueError(f"Row {index}: duplicate identifier {ref_id}")
        unique_ids.add(ref_id)
        for field in ("theme", "title", "source_type", "access_level", "source_contribution", "kerala2040_design_implication"):
            if not row[field].strip():
                raise ValueError(f"Row {index}: missing essential {field}")
        if row["authors"] == "authors_to_verify":
            unknown_authors.append(ref_id)
        doi = row["doi"].strip().lower()
        if doi:
            if not DOI_RE.match(doi) or " " in doi:
                raise ValueError(f"Row {index}: malformed DOI {doi!r}")
            if doi in doi_keys:
                raise ValueError(f"Row {index}: duplicate DOI {doi}")
            doi_keys.add(doi)
        if row["source_type"].startswith("peer_reviewed"):
            peer_count += 1
            if not doi:
                raise ValueError(f"Row {index}: scholarly reference missing DOI; verify and fill, or mark bibliographic status")
        access_types[row["access_level"]] += 1

    review = review_path.read_text(encoding="utf-8")
    for ref_id in set(CITED_ID.findall(review)):
        if ref_id not in unique_ids:
            raise ValueError(f"Literature review cites missing matrix reference {ref_id}")
    if not PROTOCOL_PATH.exists():
        raise ValueError("Review protocol/search log missing")
    return {
        "curated_entries": len(rows),
        "peer_reviewed_type_entries": peer_count,
        "distinct_dois": len(doi_keys),
        "bibliographic_author_checks_pending": unknown_authors,
        "access_level_distribution": dict(access_types),
        "note": "Static schema/integrity only. Not external DOI validation, full-text appraisal or PRISMA compliance.",
    }


if __name__ == "__main__":
    try:
        import json
        print(json.dumps(validate(), indent=2, sort_keys=True))
    except (OSError, ValueError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        sys.exit(1)
