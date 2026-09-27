"""Acquire public Kerala transmission-network sources without credentials.

The main high-value source is KSEBL Power System Engineering's public qgis2web
grid map (v3.2, 31-03-2026). The script discovers the map's public layer JS files,
archives the raw files, converts qgis2web GeoJSON variables to ordinary GeoJSON,
extracts public SLD links, and archives selected official public reports.

It deliberately does NOT log into SOS or TrAMS and does not attempt to bypass
access controls.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = ROOT / "configs/public_network_acquisition_v0_1.json"
DEFAULT_OUT = ROOT / "results/acquisition/network_public_v0_1"
USER_AGENT = "Kerala2040-public-network-acquisition/0.1 (+https://github.com/abhijith-sivaprasadan/kerala2040)"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def fetch(url: str, *, attempts: int = 3, timeout: int = 60) -> tuple[bytes, dict[str, Any]]:
    last: Exception | None = None
    for attempt in range(1, attempts + 1):
        try:
            request = urllib.request.Request(
                url,
                headers={
                    "User-Agent": USER_AGENT,
                    "Accept": "*/*",
                },
            )
            with urllib.request.urlopen(request, timeout=timeout) as response:
                data = response.read()
                return data, {
                    "requested_url": url,
                    "final_url": response.geturl(),
                    "status": int(getattr(response, "status", 200)),
                    "content_type": response.headers.get("Content-Type"),
                    "content_length": len(data),
                    "sha256": sha256_bytes(data),
                }
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as exc:
            last = exc
            if attempt < attempts:
                time.sleep(1.5 * attempt)
    raise RuntimeError(f"failed to download {url}: {last}")


def save_download(url: str, path: Path) -> dict[str, Any]:
    data, meta = fetch(url)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    meta["path"] = str(path)
    return meta


def load_config(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("classification") != "PUBLIC_WEB_NETWORK_ACQUISITION_MANIFEST_NO_AUTH_BYPASS":
        raise ValueError("public network acquisition classification mismatch")
    if data["release_gate"]["sos_or_trams_auth_bypass_permitted"] is not False:
        raise ValueError("manifest must keep SOS/TrAMS auth bypass disabled")
    return data


def discover_layer_urls(index_html: str, base_url: str) -> list[str]:
    raw = re.findall(
        r"""<script[^>]+src=["']([^"']+/layers/[^"']+\.js)["']""",
        index_html,
        flags=re.IGNORECASE,
    )
    urls: list[str] = []
    for item in raw:
        url = urllib.parse.urljoin(base_url, item)
        if url not in urls:
            urls.append(url)
    return urls


def qgis_js_to_geojson(text: str) -> dict[str, Any]:
    match = re.search(r"^\s*var\s+[A-Za-z0-9_]+\s*=\s*(\{.*\})\s*;?\s*$", text, re.DOTALL)
    if not match:
        raise ValueError("layer JS does not match qgis2web var = {...} format")
    obj = json.loads(match.group(1))
    if obj.get("type") != "FeatureCollection" or not isinstance(obj.get("features"), list):
        raise ValueError("qgis2web layer is not a FeatureCollection")
    return obj


def extract_sld_links(feature_collection: dict[str, Any], layer_base: str) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    seen: set[str] = set()
    for feature in feature_collection["features"]:
        props = feature.get("properties") or {}
        sld = props.get("SLD")
        if not isinstance(sld, str):
            continue
        href = re.search(r"""href\s*=\s*["']?([^"' >]+)""", sld, re.IGNORECASE)
        if not href:
            continue
        url = urllib.parse.urljoin(layer_base, href.group(1))
        if url in seen:
            continue
        seen.add(url)
        out.append(
            {
                "url": url,
                "location": str(props.get("Location") or ""),
                "code": str(props.get("Code") or ""),
                "class": str(props.get("Class") or ""),
                "status": str(props.get("Status") or ""),
                "owner": str(props.get("Owner") or ""),
                "type": str(props.get("Type") or ""),
            }
        )
    return out


def geometry_bounds(obj: Any, xs: list[float], ys: list[float]) -> None:
    if isinstance(obj, (list, tuple)):
        if len(obj) >= 2 and all(isinstance(value, (int, float)) for value in obj[:2]):
            xs.append(float(obj[0]))
            ys.append(float(obj[1]))
        else:
            for child in obj:
                geometry_bounds(child, xs, ys)


def layer_qa(fc: dict[str, Any]) -> dict[str, Any]:
    xs: list[float] = []
    ys: list[float] = []
    geometry_types: dict[str, int] = {}
    for feature in fc["features"]:
        geometry = feature.get("geometry") or {}
        kind = str(geometry.get("type") or "null")
        geometry_types[kind] = geometry_types.get(kind, 0) + 1
        geometry_bounds(geometry.get("coordinates"), xs, ys)
    return {
        "feature_count": len(fc["features"]),
        "geometry_types": geometry_types,
        "bounds": None
        if not xs
        else {
            "min_lon": min(xs),
            "min_lat": min(ys),
            "max_lon": max(xs),
            "max_lat": max(ys),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument(
        "--download-sld",
        action="store_true",
        help="Also download all public SLD PDFs referenced by the KSEBL map.",
    )
    args = parser.parse_args()

    config = load_config(args.config)
    out = args.out
    raw_dir = out / "raw"
    geojson_dir = out / "geojson"
    sld_dir = out / "sld"
    for path in (raw_dir, geojson_dir):
        path.mkdir(parents=True, exist_ok=True)

    source_map = {row["id"]: row for row in config["sources"]}
    acquisition_log: list[dict[str, Any]] = []

    # Public KSEBL grid map.
    index_source = source_map["kseb_grid_map_index"]
    index_data, index_meta = fetch(index_source["url"])
    (raw_dir / "kseb_grid_map_index.html").write_bytes(index_data)
    index_meta.update({"source_id": index_source["id"], "path": str(raw_dir / "kseb_grid_map_index.html")})
    acquisition_log.append(index_meta)

    index_html = index_data.decode("utf-8", errors="replace")
    layer_urls = discover_layer_urls(index_html, index_source["url"])
    names = [Path(urllib.parse.urlparse(url).path).name for url in layer_urls]
    expected = config["qgis_layer_files_expected"]
    missing = sorted(set(expected) - set(names))
    extra = sorted(set(names) - set(expected))
    if missing:
        raise RuntimeError(f"public KSEBL grid map is missing expected layer files: {missing}")

    layer_summary: dict[str, Any] = {}
    all_sld: list[dict[str, str]] = []
    layer_base = urllib.parse.urljoin(index_source["url"], "./")
    for url in layer_urls:
        name = Path(urllib.parse.urlparse(url).path).name
        data, meta = fetch(url)
        raw_path = raw_dir / "layers" / name
        raw_path.parent.mkdir(parents=True, exist_ok=True)
        raw_path.write_bytes(data)
        meta.update({"source_id": "kseb_grid_map_index", "path": str(raw_path)})
        acquisition_log.append(meta)

        text = data.decode("utf-8", errors="strict")
        fc = qgis_js_to_geojson(text)
        geojson_name = name.removesuffix(".js") + ".geojson"
        geojson_path = geojson_dir / geojson_name
        geojson_path.write_text(
            json.dumps(fc, ensure_ascii=False, separators=(",", ":")) + "\n",
            encoding="utf-8",
        )
        qa = layer_qa(fc)
        qa["raw_sha256"] = meta["sha256"]
        qa["geojson_sha256"] = sha256_bytes(geojson_path.read_bytes())
        layer_summary[name] = qa
        all_sld.extend(extract_sld_links(fc, layer_base))

    # Deduplicate SLD links by URL.
    unique_sld: dict[str, dict[str, str]] = {row["url"]: row for row in all_sld}
    sld_rows = sorted(unique_sld.values(), key=lambda row: (row["class"], row["location"], row["url"]))
    (out / "public_sld_inventory.json").write_text(
        json.dumps(sld_rows, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    sld_downloads: list[dict[str, Any]] = []
    if args.download_sld:
        sld_dir.mkdir(parents=True, exist_ok=True)
        for row in sld_rows:
            filename = Path(urllib.parse.urlparse(row["url"]).path).name
            if not filename:
                continue
            try:
                meta = save_download(row["url"], sld_dir / filename)
                meta["source_id"] = "kseb_grid_map_public_sld"
                sld_downloads.append(meta)
            except RuntimeError as exc:
                sld_downloads.append({"url": row["url"], "error": str(exc)})

    # Other public source documents/pages. Login-gated sources are recorded but never fetched.
    for source in config["sources"]:
        if source["id"] == "kseb_grid_map_index":
            continue
        if source["acquisition"] != "auto":
            acquisition_log.append(
                {
                    "source_id": source["id"],
                    "url": source["url"],
                    "status": "SKIPPED_LOGIN_GATED",
                }
            )
            continue
        suffix = ".pdf" if source["source_type"] == "public_pdf" else ".html"
        target = raw_dir / f"{source['id']}{suffix}"
        meta = save_download(source["url"], target)
        meta["source_id"] = source["id"]
        acquisition_log.append(meta)

    summary = {
        "classification": "PUBLIC_NETWORK_ACQUISITION_V0_1_EXECUTED",
        "prepared_date": config["prepared_date"],
        "kseb_grid_map_title_expected": "KERALA POWER SYSTEM NETWORK - Version. 3.2 (As on 31/03/2026)",
        "layer_files_discovered": len(layer_urls),
        "expected_layer_files": len(expected),
        "missing_expected_layers": missing,
        "unexpected_layers": extra,
        "layers": layer_summary,
        "public_sld_links_discovered": len(sld_rows),
        "public_sld_download_requested": bool(args.download_sld),
        "public_sld_download_results": sld_downloads,
        "acquisition_log": acquisition_log,
        "release_gate": config["release_gate"],
        "interpretation": [
            "Public qgis2web grid geometry is suitable for asset/topology reconstruction.",
            "Map feature status is source-reported map status and must be reconciled against dated capacity/accounting sources before model admission.",
            "Individual interstate line capacities are not additive to statewide ATC/TTC.",
            "SOS and TrAMS remain credential-gated; this workflow does not automate authentication or bypass access controls.",
            "Substation/load operating chronology remains unresolved until a public endpoint or legitimately accessible export is found.",
        ],
    }
    (out / "acquisition_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print(json.dumps(
        {
            "layer_files_discovered": len(layer_urls),
            "public_sld_links_discovered": len(sld_rows),
            "output": str(out),
            "missing_expected_layers": missing,
        },
        indent=2,
    ))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
