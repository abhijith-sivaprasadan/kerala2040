"""Audit official Kerala forest/protected-area legal source routes.

This is a source/legal registry and public-download probe. It does not infer
polygon boundaries from maps, PDFs, text descriptions, OpenStreetMap, WDPA,
Google/Bhuvan imagery or hand digitisation.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import re
import zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

BASE = "https://forest.kerala.gov.in/"
PA_PAGE = urljoin(BASE, "en/preserving-natures-heritage/")
WLS_PAGE = urljoin(BASE, "en/wildlife-sanctuaries/")
MANAGEMENT_PAGE = urljoin(BASE, "en/management-plans/")
KSDI = "https://eitd.kerala.gov.in/en/kerala-state-spatial-data-infrastructure/"
AR_REPORT = "https://forest.kerala.gov.in/images/abc/AR_Book_2022.pdf"
RESERVE_CATEGORY = urljoin(BASE, "category/reserve-notification-ml/")
AUTHOR_PAGE = urljoin(BASE, "en/author/secusrkfrst/page/{page}/")
HEADERS = {
    "User-Agent": (
        "Kerala2040Research/1.0 "
        "(+https://github.com/abhijith-sivaprasadan/kerala2040)"
    )
}
VECTOR_EXT = (".geojson", ".json", ".gpkg", ".shp", ".kml", ".kmz", ".gdb", ".zip")
DOCUMENT_EXT = (".pdf", ".doc", ".docx")
PAGE_HINT = re.compile(r"(reserve|territorial|wildlife|sanctuary|national.?park|tiger)", re.IGNORECASE)


def _get(session: requests.Session, url: str) -> requests.Response:
    response = session.get(url, timeout=(15, 75), headers=HEADERS)
    response.raise_for_status()
    return response


def _anchors(response: requests.Response) -> list[dict[str, str]]:
    soup = BeautifulSoup(response.text, "html.parser")
    rows = []
    seen = set()
    for a in soup.find_all("a", href=True):
        href = urljoin(response.url, a["href"])
        label = " ".join(a.get_text(" ", strip=True).split())
        key = (label, href)
        if key in seen:
            continue
        seen.add(key)
        rows.append({"label": label, "url": href})
    return rows


def _same_official_host(url: str) -> bool:
    host = (urlparse(url).hostname or "").lower()
    return host in {"forest.kerala.gov.in", "www.forest.kerala.gov.in"}


def _file_kind(url: str) -> str | None:
    path = urlparse(url).path.lower()
    if path.endswith(VECTOR_EXT):
        return "vector_candidate"
    if path.endswith(DOCUMENT_EXT):
        return "document"
    return None


def _page_text(response: requests.Response) -> str:
    return " ".join(BeautifulSoup(response.text, "html.parser").stripped_strings)


def _extract_pa_counts(text: str) -> dict[str, int | None]:
    # Official public prose currently states six NPs, eighteen sanctuaries,
    # two tiger reserves and one community reserve. Parse rather than hard-code pass.
    patterns = {
        "national_parks": r"\b6\s+national\s+parks?\b",
        "wildlife_sanctuaries": r"\b18\s+(?:wildlife\s+)?sanctuaries\b",
        "tiger_reserves": r"\b2\s+tiger\s+reserves?\b",
        "community_reserves": r"\b1\s+community\s+reserve\b",
    }
    return {key: (int(re.search(r"\d+", re.search(pat, text, re.IGNORECASE).group()).group())
                  if re.search(pat, text, re.IGNORECASE) else None)
            for key, pat in patterns.items()}


def _page_sha(response: requests.Response) -> str:
    return hashlib.sha256(response.content).hexdigest()


def _inspect_zip_candidate(session: requests.Session, row: dict[str, str]) -> dict:
    """Inspect official ZIP members without promoting archive label to GIS data."""
    url = row["url"]
    try:
        response = session.get(url, timeout=(15, 120), headers=HEADERS, stream=True)
        response.raise_for_status()
        declared = int(response.headers.get("Content-Length", "0") or 0)
        if declared > 250_000_000:
            return {**row, "status": "not_inspected_declared_over_250MB", "bytes": declared}
        chunks = []
        total = 0
        digest = hashlib.sha256()
        for chunk in response.iter_content(1024 * 1024):
            if not chunk:
                continue
            total += len(chunk)
            if total > 250_000_000:
                return {**row, "status": "not_inspected_stream_over_250MB", "bytes": total}
            digest.update(chunk)
            chunks.append(chunk)
        payload = b"".join(chunks)
        with zipfile.ZipFile(io.BytesIO(payload)) as archive:
            names = archive.namelist()
            suffixes = sorted({Path(name).suffix.lower() for name in names if Path(name).suffix})
            stems: dict[str, set[str]] = {}
            for name in names:
                p = Path(name)
                stems.setdefault(str(p.with_suffix("")).casefold(), set()).add(p.suffix.lower())
            shapefile_groups = [
                stem for stem, exts in stems.items()
                if {".shp", ".shx", ".dbf", ".prj"} <= exts
            ]
            direct_geo = [
                name for name in names
                if Path(name).suffix.lower() in {".geojson", ".gpkg", ".kml", ".kmz"}
            ]
            return {
                **row,
                "status": "zip_members_inspected",
                "bytes": total,
                "sha256": digest.hexdigest(),
                "member_count": len(names),
                "member_suffixes": suffixes,
                "complete_shapefile_groups": shapefile_groups,
                "direct_geospatial_members": direct_geo,
                "contains_machine_readable_geometry": bool(shapefile_groups or direct_geo),
            }
    except (requests.RequestException, zipfile.BadZipFile, OSError) as exc:
        return {**row, "status": "zip_inspection_failed", "error": f"{type(exc).__name__}: {exc}"}


def run(output: Path) -> dict:
    session = requests.Session()
    official_pages = {}
    discovered_pages = {}
    all_file_links: dict[str, dict] = {}
    failures = []
    try:
        for key, url in {
            "protected_area_network": PA_PAGE,
            "wildlife_sanctuaries": WLS_PAGE,
            "management_plans": MANAGEMENT_PAGE,
            "reserve_notification_category": RESERVE_CATEGORY,
        }.items():
            try:
                response = _get(session, url)
                official_pages[key] = {
                    "url": response.url,
                    "http_status": response.status_code,
                    "sha256_of_html_response": _page_sha(response),
                    "text_chars": len(_page_text(response)),
                }
                for row in _anchors(response):
                    kind = _file_kind(row["url"])
                    if kind and _same_official_host(row["url"]):
                        all_file_links[row["url"]] = {
                            **row, "kind": kind, "discovered_from": response.url,
                        }
            except requests.RequestException as exc:  # source failure is evidence, not a pass
                failures.append({"url": url, "error": f"{type(exc).__name__}: {exc}"})

        # Official site author archive exposes reserve/division pages not linked
        # cleanly from one English index. Keep this crawl strictly bounded.
        for page in range(1, 13):
            url = AUTHOR_PAGE.format(page=page)
            try:
                response = _get(session, url)
            except requests.RequestException as exc:
                failures.append({"url": url, "error": f"{type(exc).__name__}: {exc}"})
                continue
            for row in _anchors(response):
                if not _same_official_host(row["url"]):
                    continue
                if PAGE_HINT.search(row["label"] + " " + row["url"]):
                    discovered_pages[row["url"]] = {
                        "label": row["label"], "discovered_from": response.url
                    }

        # Visit only official reserve/protected-area candidate pages. Use bounded
        # concurrency because the department site is page-oriented and can be slow.
        targets = list(discovered_pages.items())[:120]

        def fetch_candidate(url: str) -> tuple[str, requests.Response | None, str | None]:
            try:
                response = requests.get(url, timeout=(10, 35), headers=HEADERS)
                response.raise_for_status()
                return url, response, None
            except requests.RequestException as exc:
                return url, None, f"{type(exc).__name__}: {exc}"

        with ThreadPoolExecutor(max_workers=8) as pool:
            futures = [pool.submit(fetch_candidate, url) for url, _ in targets]
            for future in as_completed(futures):
                url, response, error = future.result()
                meta = discovered_pages[url]
                if error is not None:
                    meta["error"] = error
                    continue
                assert response is not None
                meta.update({
                    "http_status": response.status_code,
                    "sha256_of_html_response": _page_sha(response),
                })
                for row in _anchors(response):
                    kind = _file_kind(row["url"])
                    if kind and _same_official_host(row["url"]):
                        all_file_links[row["url"]] = {
                            **row, "kind": kind, "discovered_from": response.url,
                        }

        pa_counts = {}
        if "protected_area_network" in official_pages:
            response = _get(session, official_pages["protected_area_network"]["url"])
            pa_counts = _extract_pa_counts(_page_text(response))

        vectors = [
            row for row in all_file_links.values()
            if row["kind"] == "vector_candidate"
        ]
        # A ZIP is only a candidate until its members are inspected.
        direct_nonzip_vector = [
            row for row in vectors
            if not urlparse(row["url"]).path.lower().endswith(".zip")
        ]
        zip_candidates = [
            row for row in vectors
            if urlparse(row["url"]).path.lower().endswith(".zip")
        ]
        with ThreadPoolExecutor(max_workers=4) as pool:
            inspected_zip_candidates = list(pool.map(
                lambda row: _inspect_zip_candidate(session, row), zip_candidates
            ))
        verified_geometry_archives = [
            row for row in inspected_zip_candidates
            if row.get("contains_machine_readable_geometry") is True
        ]
        result = {
            "classification": (
                "official_Kerala_Forest_source_and_notification_discovery_"
                "NO_authoritative_public_machine_readable_geometry_admitted"
            ),
            "reviewed_at_utc": datetime.now(UTC).replace(microsecond=0).isoformat(),
            "official_department": "Kerala Forest and Wildlife Department",
            "ksdi": KSDI,
            "department_gis_report": AR_REPORT,
            "official_pages": official_pages,
            "protected_area_network_counts_from_department_page": pa_counts,
            "discovered_official_candidate_pages_count": len(discovered_pages),
            "discovered_official_candidate_pages": [
                {"url": url, **meta}
                for url, meta in sorted(discovered_pages.items())
            ],
            "official_download_links_discovered_count": len(all_file_links),
            "official_download_links": sorted(
                all_file_links.values(), key=lambda row: row["url"]
            ),
            "machine_readable_vector_candidates": vectors,
            "direct_nonzip_machine_readable_vector_candidates": direct_nonzip_vector,
            "inspected_official_zip_candidates": inspected_zip_candidates,
            "verified_archives_containing_machine_readable_geometry": verified_geometry_archives,
            "verified_geometry_archive_count": len(verified_geometry_archives),
            "public_authoritative_forest_polygon_verified": False,
            "public_authoritative_protected_area_polygon_verified": False,
            "notification_to_polygon_linkage_verified": False,
            "current_revision_date_for_statewide_geometry_verified": False,
            "redistribution_licence_for_statewide_geometry_verified": False,
            "forest_cover_treated_as_legal_forest": False,
            "pdf_or_rendered_map_digitised_as_geometry": False,
            "external_non_custodian_geometry_admitted": False,
            "legal_exclusion_overlay_ready": False,
            "eligible_area_sq_km": None,
            "capacity_ceiling_mw": None,
            "source_failures": failures,
            "request_needed": {
                "format": "GPKG/GeoJSON or complete SHP components",
                "layers": [
                    "Reserve Forest",
                    "Proposed Reserve",
                    "Vested Forest",
                    "EFL",
                    "Protected Areas by legal category",
                    "final Eco-Sensitive Zones separately",
                ],
                "metadata": [
                    "gazette_or_notification_id",
                    "effective_date",
                    "legal_category",
                    "original_crs",
                    "revision_date",
                    "boundary_accuracy_or_survey_basis",
                    "licence_or_research_and_public_derivative_permission",
                ],
            },
        }
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
        return result
    finally:
        session.close()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output", type=Path,
        default=Path("results/gis/forest_protected_area_source_audit.json"),
    )
    args = parser.parse_args()
    result = run(args.output)
    print(json.dumps({
        "classification": result["classification"],
        "candidate_pages": result["discovered_official_candidate_pages_count"],
        "download_links": result["official_download_links_discovered_count"],
        "vector_candidates": len(result["machine_readable_vector_candidates"]),
        "direct_nonzip_vectors": len(
            result["direct_nonzip_machine_readable_vector_candidates"]
        ),
        "verified_geometry_archives": result["verified_geometry_archive_count"],
        "pa_counts": result["protected_area_network_counts_from_department_page"],
        "legal_exclusion_overlay_ready": result["legal_exclusion_overlay_ready"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
