"""Bounded live audit of SWAK/DoECC wetland legal and GIS source routes.

Discovery is not confirmation: PDF, brief, draft, portal, gazette candidate
and vector are separate. Nothing here establishes a final statutory polygon.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

PAGES = {
    "swak_home": "https://www.swak.kerala.gov.in/index.php",
    "swak_draft_briefs": (
        "https://www.swak.kerala.gov.in/index.php/"
        "wetland-notification-in-kerala/draft-brief-documents-of-wetlands"
    ),
    "doecc_swak": "https://envt.kerala.gov.in/state-wetland-authority-kerala-swak/",
    "wiams_portal": "https://wiams.kerala.gov.in/",
}
OFFICIAL_HOSTS = {
    "swak.kerala.gov.in",
    "www.swak.kerala.gov.in",
    "envt.kerala.gov.in",
    "wiams.kerala.gov.in",
}
VECTOR_SUFFIXES = (".geojson", ".gpkg", ".shp", ".kml", ".kmz", ".gdb", ".zip")
DOCUMENT_SUFFIXES = (".pdf", ".doc", ".docx")
MAX_HTML_BYTES = 5_000_000
MAX_ANCHORS = 600


def official_url(url: str) -> bool:
    parsed = urlparse(url)
    return parsed.scheme == "https" and parsed.hostname in OFFICIAL_HOSTS


def classify_link(label: str, url: str, page_key: str) -> str:
    """Only candidate classification; keywords NEVER establish final legal status."""
    lower = urlparse(url).path.lower()
    words = f"{label} {lower}".lower()
    if lower.endswith(VECTOR_SUFFIXES):
        return "machine_readable_candidate_UNINSPECTED"
    if page_key == "swak_draft_briefs" or "draft" in words:
        return "draft_or_draft_page_NOT_FINAL"
    if lower.endswith(DOCUMENT_SUFFIXES):
        if any(word in words for word in ("gazette", "notification", "wetland")):
            return "notification_or_brief_DOCUMENT_NEEDS_LEGAL_REVIEW"
        return "other_document_UNREVIEWED"
    if "notification" in words or "wetland" in words:
        return "page_candidate_NEEDS_LEGAL_REVIEW"
    return "other_link"


def anchors(html: bytes, base_url: str, page_key: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    found = {}
    for anchor in soup.select("a[href]")[:MAX_ANCHORS]:
        url = urljoin(base_url, anchor["href"].strip())
        if not official_url(url):
            continue
        label = " ".join(anchor.get_text(" ", strip=True).split())[:250]
        found[url] = {
            "url": url,
            "label": label,
            "candidate_class": classify_link(label, url, page_key),
        }
    return sorted(found.values(), key=lambda item: item["url"])


def probe(session: requests.Session, key: str, url: str) -> dict:
    record: dict = {"page": key, "source_url": url}
    try:
        response = session.get(url, timeout=(15, 40))
        record["http_status"] = response.status_code
        record["final_url"] = response.url
        if not official_url(response.url):
            record["status"] = "BLOCKED_redirect_outside_official_hosts"
            return record
        response.raise_for_status()
        if len(response.content) > MAX_HTML_BYTES:
            record["status"] = "BLOCKED_html_exceeds_size_cap"
            return record
        if "html" not in response.headers.get("content-type", "").lower():
            record["status"] = "BLOCKED_not_html"
            return record
        record.update({
            "status": "HTML_DISCOVERED_NOT_GEOMETRY",
            "html_sha256": hashlib.sha256(response.content).hexdigest(),
            "bytes": len(response.content),
            "links": anchors(response.content, response.url, key),
        })
    except requests.RequestException as exc:
        record["status"] = "BLOCKED_live_source_unavailable"
        record["exception_type"] = type(exc).__name__
    return record


def audit(output: Path, session: requests.Session | None = None) -> dict:
    owns_session = session is None
    if session is None:
        session = requests.Session()
        session.headers.update({
            "User-Agent": "Kerala2040Research/1.0 (+https://github.com/abhijith-sivaprasadan/kerala2040)"
        })
    try:
        records = [probe(session, key, url) for key, url in PAGES.items()]
    finally:
        if owns_session:
            session.close()
    links = [item for record in records for item in record.get("links", [])]
    candidates = [
        item for item in links
        if item["candidate_class"] != "other_link"
    ]
    report = {
        "classification": (
            "live_official_SWAK_DoECC_discovery_NOT_notification_or_geometry_validation"
        ),
        "reviewed_at_utc": datetime.now(UTC).replace(microsecond=0).isoformat(),
        "pages": records,
        "reachable_html_pages": sum(
            row["status"] == "HTML_DISCOVERED_NOT_GEOMETRY" for row in records
        ),
        "official_candidate_links_unverified": candidates,
        "machine_readable_candidates_uninspected": sum(
            item["candidate_class"] == "machine_readable_candidate_UNINSPECTED"
            for item in candidates
        ),
        "draft_briefs_not_promoted_to_final": True,
        "gazette_identity_and_effective_date_verified": False,
        "notification_linked_original_vector_verified": False,
        "waterbody_inventory_original_vector_verified": False,
        "zone_of_influence_original_vector_verified": False,
        "legal_wetland_exclusion_ready": False,
        "floating_pv_water_area_eligible": False,
        "eligible_area_sq_km": None,
        "capacity_ceiling_mw": None,
        "required_request": {
            "custodian": "State Wetland Authority Kerala",
            "layers": [
                "final notified wetland boundaries",
                "final legally applicable zones of influence",
                "draft/proposed wetland boundaries kept separate",
                "waterbody and reservoir inventory geometries",
            ],
            "metadata": [
                "gazette_id", "notification_effective_date",
                "original_crs", "source_revision_date",
                "survey_precision", "licence_and_redistribution_terms",
            ],
        },
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
    print(json.dumps({
        "reachable_pages": report["reachable_html_pages"],
        "candidate_links": len(candidates),
        "machine_readable_candidates_uninspected": report[
            "machine_readable_candidates_uninspected"
        ],
        "legal_overlay_ready": False,
        "output": str(output),
    }))
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output", type=Path,
        default=Path("results/gis/swak_wetland_source_audit.json"),
    )
    args = parser.parse_args()
    audit(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
