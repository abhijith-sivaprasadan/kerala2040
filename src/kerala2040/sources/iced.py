"""NITI ICED discovery adapter.

ICED is treated as a discovery/download layer in v1.0. We do not invent an
undocumented API. Key values used in the model should be traced to primary
official sources when possible.
"""

from __future__ import annotations

from typing import Any
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from requests import Session

from kerala2040.provenance import utc_now_iso
from kerala2040.sources.http import build_session, checked

HOME = "https://www.iced.niti.gov.in/"


def probe_page(
    url: str = HOME,
    *,
    session: Session | None = None,
    timeout: float = 45.0,
) -> dict[str, Any]:
    own_session = session is None
    session = session or build_session()
    try:
        response = checked(session.get(url, timeout=timeout))
        soup = BeautifulSoup(response.text, "lxml")
        downloads = []
        for anchor in soup.find_all("a", href=True):
            href = str(anchor["href"])
            text = " ".join(anchor.get_text(" ", strip=True).split())
            lower = href.lower()
            if lower.endswith((".csv", ".xls", ".xlsx", ".zip")) or "download" in text.lower():
                downloads.append({"text": text, "url": urljoin(response.url, href)})
        return {
            "source_id": "niti_iced_discovery",
            "url": response.url,
            "http_status": response.status_code,
            "retrieved_at_utc": utc_now_iso(),
            "download_links": downloads,
            "mode": "discovery_only",
        }
    finally:
        if own_session:
            session.close()
