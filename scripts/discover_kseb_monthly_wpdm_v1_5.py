"""Discover and download official KSEB monthly reservoir files from WPDM.

This tool is fail-closed. It never guesses WordPress Download Manager package
IDs or filenames. It binds a download candidate to an inventory month only
when the page HTML itself exposes a package/download locator near that item's
official title, and it requires 12 unique bindings before bulk download.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urljoin, urlparse

import requests
from bs4 import BeautifulSoup, Tag

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INDEX = "https://dams.kseb.in/?p=329"
DEFAULT_INVENTORY = (
    ROOT
    / "data/evidence/hydro/"
    "kseb_monthly_reservoir_inventory_fy2024_25_2026_09_26.json"
)
OFFICIAL_HOST = "dams.kseb.in"

WPDM_QUERY_RE = re.compile(r"(?:[?&]|\\b)wpdmdl=(\\d+)", re.IGNORECASE)
SHORTCODE_RE = re.compile(
    r"\\[wpdm_package[^\\]]*\\bid=[\"']?(\\d+)", re.IGNORECASE
)
ATTR_ID_RE = re.compile(
    r"(?:package[_-]?id|download[_-]?id|wpdm[_-]?id)[^0-9]{0,8}(\\d+)",
    re.IGNORECASE,
)
DOWNLOAD_PATH_RE = re.compile(r"/download/[^\\s\"'<>]+", re.IGNORECASE)


def normalize(text: str) -> str:
    text = re.sub(r"[^a-z0-9]+", " ", text.lower())
    return " ".join(text.split())


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_inventory(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    months = data.get("months", [])
    if len(months) != 12:
        raise ValueError("Expected exactly 12 official FY2024-25 inventory rows")
    return data


def _candidate_from_url(raw: str, base_url: str) -> dict[str, Any] | None:
    raw = raw.strip()
    if not raw:
        return None
    url = urljoin(base_url, raw)
    parsed = urlparse(url)
    if parsed.hostname and parsed.hostname.lower() != OFFICIAL_HOST:
        return None

    query = parse_qs(parsed.query)
    package_ids = query.get("wpdmdl", [])
    package_id = package_ids[0] if package_ids else None
    if package_id and package_id.isdigit():
        return {
            "url": url,
            "package_id": int(package_id),
            "kind": "wpdmdl_query",
        }
    if DOWNLOAD_PATH_RE.search(parsed.path):
        return {"url": url, "package_id": None, "kind": "download_path"}
    return None


def _scan_fragment(fragment: Tag, base_url: str) -> list[dict[str, Any]]:
    found: dict[tuple[str, str], dict[str, Any]] = {}

    for tag in fragment.find_all(True):
        for attr, value in tag.attrs.items():
            values = value if isinstance(value, list) else [value]
            for item in values:
                raw = str(item)
                candidate = _candidate_from_url(raw, base_url)
                if candidate:
                    key = (candidate["kind"], candidate["url"])
                    found[key] = {
                        **candidate,
                        "evidence": f"attribute:{tag.name}.{attr}",
                    }
                for match in ATTR_ID_RE.finditer(raw):
                    pid = int(match.group(1))
                    url = urljoin(base_url, f"/?wpdmdl={pid}")
                    found[("package_id_attribute", url)] = {
                        "url": url,
                        "package_id": pid,
                        "kind": "package_id_attribute",
                        "evidence": f"attribute:{tag.name}.{attr}",
                    }

        if tag.name == "a" and tag.get("href"):
            candidate = _candidate_from_url(str(tag["href"]), base_url)
            if candidate:
                found[(candidate["kind"], candidate["url"])] = {
                    **candidate,
                    "evidence": "anchor_href",
                }

    raw_html = str(fragment)
    for match in WPDM_QUERY_RE.finditer(raw_html):
        pid = int(match.group(1))
        url = urljoin(base_url, f"/?wpdmdl={pid}")
        found[("wpdmdl_raw_html", url)] = {
            "url": url,
            "package_id": pid,
            "kind": "wpdmdl_raw_html",
            "evidence": "raw_html",
        }
    for match in SHORTCODE_RE.finditer(raw_html):
        pid = int(match.group(1))
        url = urljoin(base_url, f"/?wpdmdl={pid}")
        found[("wpdm_shortcode", url)] = {
            "url": url,
            "package_id": pid,
            "kind": "wpdm_shortcode",
            "evidence": "shortcode",
        }

    return list(found.values())


def _title_score(text: str, title: str) -> float:
    a = set(normalize(text).split())
    b = set(normalize(title).split())
    if not b:
        return 0.0
    return len(a & b) / len(b)


def discover_bindings(
    html: str,
    *,
    inventory: dict[str, Any],
    base_url: str = DEFAULT_INDEX,
) -> dict[str, Any]:
    soup = BeautifulSoup(html, "html.parser")
    bindings: list[dict[str, Any]] = []

    for row in inventory["months"]:
        title = row["title"]
        title_norm = normalize(title)
        text_nodes = [
            node
            for node in soup.find_all(string=True)
            if title_norm in normalize(str(node))
            or _title_score(str(node), title) >= 0.8
        ]

        fragments: list[tuple[int, Tag]] = []
        for node in text_nodes:
            parent = node.parent
            depth = 0
            while isinstance(parent, Tag) and depth <= 7:
                score = _title_score(parent.get_text(" ", strip=True), title)
                if score >= 0.8:
                    fragments.append((depth, parent))
                parent = parent.parent
                depth += 1

        candidates: list[dict[str, Any]] = []
        for depth, fragment in sorted(fragments, key=lambda item: item[0]):
            for candidate in _scan_fragment(fragment, base_url):
                candidates.append(
                    {
                        **candidate,
                        "dom_ancestor_depth": depth,
                    }
                )
            if candidates:
                break

        unique: dict[str, dict[str, Any]] = {}
        for candidate in candidates:
            unique[candidate["url"]] = candidate
        candidates = list(unique.values())

        if len(candidates) == 1:
            status = "bound_unique_html_candidate"
            selected = candidates[0]
        elif not candidates:
            status = "unresolved_no_exposed_candidate"
            selected = None
        else:
            status = "unresolved_multiple_candidates"
            selected = None

        bindings.append(
            {
                "month": row["month"],
                "title": title,
                "status": status,
                "selected": selected,
                "candidates": candidates,
            }
        )

    selected_urls = [
        item["selected"]["url"]
        for item in bindings
        if item["selected"] is not None
    ]
    complete = (
        len(selected_urls) == 12
        and len(set(selected_urls)) == 12
        and all(item["selected"] is not None for item in bindings)
    )

    return {
        "classification": "KSEB_WPDM_MONTHLY_DOWNLOAD_DISCOVERY_V1_5",
        "index_url": base_url,
        "months_expected": 12,
        "months_uniquely_bound": len(selected_urls),
        "all_12_unique_downloads_bound": complete,
        "bindings": bindings,
    }


def fetch_html(url: str, timeout: float) -> str:
    response = requests.get(
        url,
        timeout=timeout,
        headers={"User-Agent": "kerala2040-research/1.5"},
    )
    response.raise_for_status()
    return response.text


def download_bound_files(
    result: dict[str, Any],
    *,
    output_dir: Path,
    timeout: float,
) -> list[dict[str, Any]]:
    if not result["all_12_unique_downloads_bound"]:
        raise ValueError("Refusing bulk download before all 12 months are uniquely bound")
    output_dir.mkdir(parents=True, exist_ok=True)

    records = []
    for binding in result["bindings"]:
        url = binding["selected"]["url"]
        response = requests.get(
            url,
            timeout=timeout,
            allow_redirects=True,
            headers={"User-Agent": "kerala2040-research/1.5"},
        )
        response.raise_for_status()
        data = response.content
        if not data:
            raise ValueError(f"Empty download for {binding['month']}: {url}")

        disposition = response.headers.get("content-disposition", "")
        source_name = "source.bin"
        for part in disposition.split(";"):
            key, sep, value = part.strip().partition("=")
            if sep and key.lower() in {"filename", "filename*"}:
                value = value.strip().strip("\\\"'")
                if "''" in value:
                    value = value.split("''", 1)[1]
                if value:
                    source_name = Path(value).name
                break
        path = output_dir / f"{binding['month']}_{source_name}"
        path.write_bytes(data)
        records.append(
            {
                "month": binding["month"],
                "download_url": url,
                "final_url": response.url,
                "http_content_type": response.headers.get("content-type"),
                "http_content_disposition": disposition or None,
                "filename": path.name,
                "bytes": len(data),
                "sha256": sha256_bytes(data),
            }
        )
    return records


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--inventory", type=Path, default=DEFAULT_INVENTORY)
    parser.add_argument("--index-url", default=DEFAULT_INDEX)
    parser.add_argument("--html-file", type=Path)
    parser.add_argument("--timeout", type=float, default=30.0)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--download-dir", type=Path)
    args = parser.parse_args()

    inventory = load_inventory(args.inventory)
    html = (
        args.html_file.read_text(encoding="utf-8")
        if args.html_file
        else fetch_html(args.index_url, args.timeout)
    )
    result = discover_bindings(
        html,
        inventory=inventory,
        base_url=args.index_url,
    )
    if args.download_dir:
        result["downloads"] = download_bound_files(
            result,
            output_dir=args.download_dir,
            timeout=args.timeout,
        )

    output = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(output, encoding="utf-8")
    print(output, end="")


if __name__ == "__main__":
    main()
