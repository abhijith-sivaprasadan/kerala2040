#!/usr/bin/env python
"""Build a download manifest for official KSDMA hazard-map layers."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

URL = "https://sdma.kerala.gov.in/hazard-maps/"
KEYWORDS = ("flood", "landslide", "coastal", "hazard", "raster", "shape", "kml", "drought")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("data/processed/ksdma_hazard_manifest.json"))
    args = parser.parse_args()

    response = requests.get(
        URL,
        timeout=45,
        headers={"User-Agent": "Kerala2040Research/1.0 (+https://github.com/abhijith-sivaprasadan/kerala2040)"},
    )
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    records = []
    seen = set()

    for anchor in soup.find_all("a", href=True):
        href = urljoin(response.url, anchor["href"])
        label = " ".join(anchor.get_text(" ", strip=True).split())
        haystack = f"{label} {href}".lower()
        if not any(word in haystack for word in KEYWORDS):
            continue
        if href in seen:
            continue
        seen.add(href)
        records.append({"label": label or href.rsplit("/", 1)[-1], "url": href})

    payload = {
        "retrieved_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "classification": "official_hazard_download_catalog",
        "source_url": URL,
        "records": records,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps({"hazard_links": len(records)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
