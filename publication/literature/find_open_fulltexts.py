#!/usr/bin/env python3
"""Resolve legal OA links for Kerala2040's DOI evidence matrix.

The discovery output is metadata, NOT proof that a paper was downloaded, licensed
for redistribution, read, appraised or independently peer reviewed.

Standard library only; Python >=3.10. The program only downloads with --download.
OpenAlex keys are read from OPENALEX_API_KEY; Unpaywall requires the user's own
UNPAYWALL_EMAIL. Never hard-code keys or email in repository source.
"""
from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode, urlparse
from urllib.request import Request, urlopen

FIELDS = [
    "id", "doi", "title", "relevance", "provider", "query_status",
    "is_oa", "oa_status", "candidate_pdf_url", "landing_page_url",
    "source_host_type", "pdf_status", "pdf_sha256", "pdf_bytes",
    "checked_utc", "detail",
]
USER_AGENT = "Kerala2040-Literature-OA/0.1 (metadata and public PDF discovery)"
MAX_PDF_BYTES = 35 * 1024 * 1024


def read_matrix(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as f:
        records = list(csv.DictReader(f))
    if not records or not all("id" in row and "doi" in row for row in records):
        raise ValueError("Invalid evidence matrix: expected id and doi columns")
    return [r for r in records if r.get("doi", "").strip()]


def request_json(url: str, *, api_key: str = "", retries: int = 2) -> dict:
    headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    for attempt in range(retries + 1):
        try:
            with urlopen(Request(url, headers=headers), timeout=35) as response:
                return json.load(response)
        except HTTPError as e:
            if e.code == 404:
                raise LookupError("record_not_found") from e
            if e.code not in (429, 500, 502, 503, 504) or attempt == retries:
                raise RuntimeError(f"HTTP {e.code} from literature lookup") from e
        except (URLError, TimeoutError) as e:
            if attempt == retries:
                raise RuntimeError(f"Network/timeout error: {type(e).__name__}") from e
        time.sleep(min(2 ** (attempt + 1), 10))
    raise RuntimeError("lookup_exhausted")


def is_https_url(s: object) -> bool:
    if not isinstance(s, str):
        return False
    p = urlparse(s)
    return p.scheme == "https" and bool(p.netloc) and not p.username and not p.password


def valid_url(s: object) -> str:
    return s if is_https_url(s) else ""


def openalex_lookup(doi: str, key: str) -> dict:
    # URI-encode the DOI as a literal ID without allowing query-string injection.
    encoded = quote("https://doi.org/" + doi, safe=":/")
    url = "https://api.openalex.org/works/" + encoded
    work = request_json(url, api_key=key)
    if not isinstance(work, dict):
        raise ValueError("OpenAlex did not return a work object")
    oa = work.get("open_access") or {}
    locations = [
        work.get("best_oa_location") or {},
        *(work.get("locations") or []),
    ]
    accessible = [
        loc for loc in locations if isinstance(loc, dict) and
        valid_url(loc.get("pdf_url"))
    ]
    best = accessible[0] if accessible and oa.get("is_oa") else {}
    preferred = work.get("best_oa_location") or work.get("primary_location") or {}
    return {
        "provider": "openalex",
        "is_oa": str(bool(oa.get("is_oa"))).lower(),
        "oa_status": str(oa.get("oa_status") or ""),
        "candidate_pdf_url": valid_url(best.get("pdf_url")),
        "landing_page_url": valid_url(best.get("landing_page_url")) or
            valid_url(preferred.get("landing_page_url")),
        "source_host_type": str((best.get("source") or {}).get("type") or ""),
    }


def unpaywall_lookup(doi: str, email: str) -> dict:
    if not email or "@" not in email:
        raise ValueError("Unpaywall requires your real email via UNPAYWALL_EMAIL")
    url = ("https://api.unpaywall.org/v2/" + quote(doi, safe="/") +
           "?" + urlencode({"email": email}))
    result = request_json(url)
    if not isinstance(result, dict):
        raise ValueError("Unpaywall did not return a DOI record")
    best = result.get("best_oa_location") or {}
    alternate = next(
        (loc for loc in (result.get("oa_locations") or [])
         if valid_url(loc.get("url_for_pdf"))),
        {},
    )
    selected = best if valid_url(best.get("url_for_pdf")) else alternate
    return {
        "provider": "unpaywall",
        "is_oa": str(bool(result.get("is_oa"))).lower(),
        "oa_status": str(result.get("oa_status") or ""),
        "candidate_pdf_url": valid_url(selected.get("url_for_pdf")),
        "landing_page_url": valid_url(best.get("url_for_landing_page")) or
            valid_url(result.get("doi_url")),
        "source_host_type": str(selected.get("host_type") or ""),
    }


def resolve(doi: str, provider: str, key: str, email: str) -> dict:
    failures: list[str] = []
    choices = (["openalex", "unpaywall"] if provider == "both" else [provider])
    saved: dict = {}
    for choice in choices:
        try:
            found = (openalex_lookup(doi, key) if choice == "openalex" else
                     unpaywall_lookup(doi, email))
        except (LookupError, RuntimeError, ValueError) as e:
            failures.append(f"{choice}:{str(e)[:100]}")
            continue
        if found.get("candidate_pdf_url"):
            return {**found, "query_status": "oa_pdf_candidate", "detail": ""}
        if not saved:
            saved = found
    if saved:
        return {**saved, "query_status": "no_direct_oa_pdf",
                "detail": "; ".join(failures)}
    return {"provider": provider, "query_status": "lookup_failed",
            "detail": "; ".join(failures)}


def save_pdf(candidate: str, path: Path, max_bytes: int) -> tuple[str, str, int, str]:
    if not is_https_url(candidate):
        return ("rejected_unsafe_url", "", 0, "Only HTTPS public links permitted")
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".pdf.partial")
    try:
        with urlopen(Request(candidate, headers={"User-Agent": USER_AGENT,
                                                  "Accept": "application/pdf"}),
                     timeout=60) as response:
            if not is_https_url(response.geturl()):
                raise ValueError("Redirected away from HTTPS")
            first = response.read(8)
            if not first.startswith(b"%PDF-"):
                raise ValueError("Response is not a PDF (possibly a landing/login page)")
            h = hashlib.sha256()
            total = len(first)
            h.update(first)
            with tmp.open("wb") as out:
                out.write(first)
                while True:
                    block = response.read(128 * 1024)
                    if not block:
                        break
                    total += len(block)
                    if total > max_bytes:
                        raise ValueError("PDF exceeds max configured size")
                    h.update(block)
                    out.write(block)
        os.replace(tmp, path)
        return ("saved_pdf_signature_verified", h.hexdigest(), total, "")
    except (HTTPError, URLError, TimeoutError, OSError, ValueError) as error:
        if tmp.exists():
            tmp.unlink()
        # No request URL or user email in logs, as those may contain private data.
        return ("download_failed", "", 0, f"{type(error).__name__}: {str(error)[:140]}")


def run(argv: list[str] | None = None) -> int:
    here = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--matrix", type=Path, default=here / "EVIDENCE_MATRIX.csv")
    parser.add_argument("--out", type=Path, default=here / "oa_discovery_results.csv")
    parser.add_argument("--provider", choices=["openalex", "unpaywall", "both"],
                        default="openalex")
    parser.add_argument("--limit", type=int, default=0,
                        help="First N DOI records, 0=all")
    parser.add_argument("--download", action="store_true",
                        help="Explicit opt-in to fetch public PDF candidates; not publication rights")
    parser.add_argument("--pdf-dir", type=Path, default=here / "downloaded")
    parser.add_argument("--max-mb", type=int, default=35)
    parser.add_argument("--interval", type=float, default=1.0)
    args = parser.parse_args(argv)
    key = os.environ.get("OPENALEX_API_KEY", "")
    email = os.environ.get("UNPAYWALL_EMAIL", "")
    if args.provider in ("unpaywall", "both") and not email:
        parser.error("Set UNPAYWALL_EMAIL to your own email for Unpaywall lookups")
    if args.max_mb < 1 or args.interval < 0:
        parser.error("--max-mb must be >= 1 and --interval >= 0")
    records = read_matrix(args.matrix)
    if args.limit > 0:
        records = records[:args.limit]
    checked = datetime.now(timezone.utc).isoformat(timespec="seconds")
    results = []
    for index, record in enumerate(records, 1):
        doi = record["doi"].strip()
        item = {k: "" for k in FIELDS}
        item.update({"id": record["id"], "doi": doi,
                     "title": record["title"], "relevance": record.get("relevance", ""),
                     "checked_utc": checked,
                     "pdf_status": "not_requested"})
        item.update(resolve(doi, args.provider, key, email))
        candidate = item.get("candidate_pdf_url", "")
        if args.download:
            if candidate:
                filename = f"{record['id']}_{re.sub(r'[^a-zA-Z0-9._-]+', '_', doi)[:90]}.pdf"
                status, digest, size, error = save_pdf(
                    candidate, args.pdf_dir / filename,
                    min(MAX_PDF_BYTES, args.max_mb * 1024 * 1024))
                item["pdf_status"] = status
                item["pdf_sha256"] = digest
                item["pdf_bytes"] = size or ""
                if error:
                    item["detail"] = (item.get("detail", "") + "; " + error).strip("; ")
            else:
                item["pdf_status"] = "no_oa_pdf_candidate"
        results.append(item)
        print(f"[{index}/{len(records)}] {record['id']} "
              f"{item['query_status']} | {item['pdf_status']}", file=sys.stderr)
        if index < len(records):
            time.sleep(args.interval)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", newline="", encoding="utf-8") as output:
        writer = csv.DictWriter(output, fieldnames=FIELDS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(results)
    print(f"Wrote {len(results)} records to {args.out}")
    print("Candidate URLs are not certified download, full-text reading or redistribution rights.")
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
