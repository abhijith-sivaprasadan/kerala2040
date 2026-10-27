#!/usr/bin/env python3
"""Verify local scholarly PDF downloads and make a metadata-only QA manifest.

A PDF signature is not enough. Validate structure using pypdf, count pages,
extract first-page text and check whether title/DOI evidence is visible.
No PDF content is exported to GitHub Actions artifacts or stdout.
This is document provenance QA, not scientific paper appraisal.
"""
from __future__ import annotations

import argparse
import csv
from difflib import SequenceMatcher
from pathlib import Path
import re

def filename_for(row: dict[str,str]) -> str:
    return f"{row['id']}_{re.sub(r'[^a-zA-Z0-9._-]+', '_', row['doi'])[:90]}.pdf"

def normalize(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", s.casefold()).strip()

def check_one(row: dict[str,str], folder: Path) -> dict[str,str]:
    result = {k: row.get(k, "") for k in
              ("id", "doi", "title", "candidate_pdf_url", "pdf_status",
               "pdf_sha256", "pdf_bytes")}
    result.update({"structural_pdf_status": "not_available",
                   "pdf_pages": "", "doi_in_first_two_pages": "",
                   "title_token_coverage_first_page": "",
                   "manual_identity_check_required": "yes",
                   "validation_detail": ""})
    if row.get("pdf_status") != "saved_pdf_signature_verified":
        return result
    path = folder / filename_for(row)
    if not path.is_file():
        result.update(structural_pdf_status="missing_local_file",
                      validation_detail="Recorded PDF not present in private runner directory")
        return result
    try:
        from pypdf import PdfReader
        reader = PdfReader(str(path), strict=True)
        count = len(reader.pages)
        if count < 1:
            raise ValueError("Empty PDF")
        first = (reader.pages[0].extract_text() or "")[:25000]
        second = (reader.pages[1].extract_text() or "")[:25000] if count>1 else ""
        alltext = normalize(first + " " + second)
        doi = row["doi"].casefold().replace("https://doi.org/", "").strip()
        doi_present = doi in (first + "\n" + second).casefold().replace("\n", "")
        # PDF text layout can reorder words; token coverage is a *screen*, not
        # an identity guarantee. Poor extraction is not proof the PDF is wrong.
        title_tokens = set(normalize(row["title"]).split())
        first_tokens = set(normalize(first).split())
        coverage = len(title_tokens & first_tokens) / max(len(title_tokens),1)
        result["pdf_pages"] = str(count)
        result["doi_in_first_two_pages"] = str(bool(doi_present)).lower()
        result["title_token_coverage_first_page"] = f"{coverage:.3f}"
        result["structural_pdf_status"] = "valid_readable_pdf"
        result["validation_detail"] = (
            "Candidate identity requires human verification"
            if coverage < .65 and not doi_present
            else "Bibliographic text is consistent with target; manual identity/edition verification still required"
        )
    except Exception as e:
        # Catch pypdf's PdfReadError, PDF malformation, encrypted or scanned
        # limitations. Do not print extracted article text in logs.
        result["structural_pdf_status"] = "pdf_parse_failed"
        result["validation_detail"] = f"{type(e).__name__}: {str(e)[:110]}"
    return result

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    root = Path(__file__).resolve().parent
    parser.add_argument("--manifest",type=Path,default=root/"oa_discovery_results.csv")
    parser.add_argument("--pdf-dir",type=Path,default=root/"downloaded")
    parser.add_argument("--out",type=Path,default=root/"pdf_validation_results.csv")
    args=parser.parse_args()
    with args.manifest.open(newline="",encoding="utf-8") as f:
        rows=list(csv.DictReader(f))
    results=[check_one(row,args.pdf_dir) for row in rows]
    args.out.parent.mkdir(parents=True,exist_ok=True)
    with args.out.open("w",newline="",encoding="utf-8") as f:
        writer=csv.DictWriter(f,fieldnames=list(results[0].keys()) if results else [
            "id","doi","title","candidate_pdf_url","pdf_status","pdf_sha256",
            "pdf_bytes","structural_pdf_status","pdf_pages",
            "doi_in_first_two_pages","title_token_coverage_first_page",
            "manual_identity_check_required","validation_detail"])
        writer.writeheader()
        writer.writerows(results)
    from collections import Counter
    print(f"Checked {len(rows)} sources: {dict(Counter(x['structural_pdf_status'] for x in results))}")
    print(f"Metadata-only validation register: {args.out}. Do not publish fetched third-party PDF content.")

if __name__=="__main__":
    main()
