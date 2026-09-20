"""Probe real public DEM and KSDMA data without making an eligibility assertion.

Opt-in; official source downloads go to a workflow artifact, not research
committed evidence. No access token, login bypass, or fabricated missing data.
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

from kerala2040.gis_three_workstreams import check_raster, check_shapefile_zip

KSDMA = "https://sdma.kerala.gov.in/hazard-maps/"
TILE = "Copernicus_DSM_COG_30_N09_00_E076_00_DEM"
COP_90 = f"https://copernicus-dem-90m.s3.amazonaws.com/{TILE}/{TILE}.tif"
HEADERS = {"User-Agent": "Kerala2040Research/1.0 (+https://github.com/abhijith-sivaprasadan/kerala2040)"}


def _download(session: requests.Session, url: str, dest: Path, limit_mb: int) -> dict:
    dest.parent.mkdir(parents=True, exist_ok=True)
    part = dest.with_suffix(dest.suffix + ".part")
    limit = limit_mb * 1024 * 1024
    total = 0
    digest = hashlib.sha256()
    try:
        with session.get(url, timeout=(15, 90), stream=True) as response:
            response.raise_for_status()
            declared = int(response.headers.get("Content-Length", "0") or "0")
            if declared > limit:
                raise ValueError(f"declared download {declared} exceeds {limit} bytes")
            with part.open("wb") as out:
                for chunk in response.iter_content(1024 * 1024):
                    if not chunk:
                        continue
                    total += len(chunk)
                    if total > limit:
                        raise ValueError(f"download exceeded {limit} bytes")
                    digest.update(chunk)
                    out.write(chunk)
        part.replace(dest)
    except Exception:
        part.unlink(missing_ok=True)
        raise
    return {"download_url": url, "bytes": total, "sha256": digest.hexdigest(), "path": str(dest)}


def probe(output: Path, download_dir: Path, *, max_mb: int = 65) -> dict:
    output.parent.mkdir(parents=True, exist_ok=True)
    result: dict = {
        "retrieved_at_utc": datetime.now(UTC).replace(microsecond=0).isoformat(),
        "classification": "uncommitted_public_source_probe_not_kerala_ecological_model_data",
        "catalogue_only_is_not_data_acquisition": True,
        "copernicus_glo90_pilot": {"status": "not_attempted"},
        "ksdma_gsi_2022": {"status": "not_attempted"},
        "forest": {"status": "official_geometry_not_publicly_acquired"},
        "wetlands": {"status": "notified_original_polygon_not_acquired"},
        "statewide_dem_coverage_verified": False,
        "statewide_gsi_2022_coverage_verified": False,
        "ecological_capacity_ceiling_ready": False,
    }
    with requests.Session() as session:
        session.headers.update(HEADERS)
        try:
            path = download_dir / "copernicus" / (TILE + ".tif")
            download = _download(session, COP_90, path, max_mb)
            result["copernicus_glo90_pilot"] = {
                "status": "original_public_tile_downloaded_preliminary_raster_QA",
                **download,
                "raster_qa": check_raster(path),
            }
        except Exception as exc:  # noqa: BLE001 - probe failure is audit evidence
            result["copernicus_glo90_pilot"] = {
                "status": "probe_failed_not_acquired", "error": f"{type(exc).__name__}: {exc}",
            }
        try:
            response = session.get(KSDMA, timeout=(15, 60))
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            candidates = []
            all_links = []
            for link in soup.find_all("a", href=True):
                target = urljoin(response.url, link["href"])
                u = urlparse(target)
                label = " ".join(link.get_text(" ", strip=True).split())
                if any(v in (label + " " + target).lower() for v in (
                    "idukki", "thiruvananthapuram", "landslide", "gsi", "shapefile", ".zip"
                )):
                    all_links.append({"label": label, "url": target})
                if u.scheme != "https" or u.hostname != "sdma.kerala.gov.in":
                    continue
                nearby = " ".join(
                    (link.parent.parent.get_text(" ", strip=True) if link.parent.parent else "")
                    .lower().split()
                )
                if u.path.lower().endswith(".zip") and (
                    "landslide" in target.lower()
                    or "landslide" in nearby
                    or "gsi" in nearby
                ):
                    candidates.append({"label": link.get_text(" ", strip=True), "url": target})
            candidates = list({row["url"]: row for row in candidates}.values())
            result["ksdma_gsi_2022"] = {
                "status": "public_website_archive_candidates_not_validated_district_coverage",
                "source_url": KSDMA,
                "candidate_archives": candidates[:80],
                "relevant_anchor_preview": all_links[:80],
                "candidate_count": len(candidates),
                "warning": (
                    "Automated link context may include other landslide vintages. "
                    "Do not equate candidate count with verified GSI2022 districts."
                ),
            }
            if candidates:
                chosen = candidates[0]
                filename = urlparse(chosen["url"]).path.split("/")[-1]
                if filename and all(x not in filename for x in ("/", "\\", "..")):
                    path = download_dir / "ksdma" / filename
                    downloaded = _download(session, chosen["url"], path, max_mb)
                    result["ksdma_gsi_2022"]["pilot"] = {
                        **downloaded, "zip_qa": check_shapefile_zip(path),
                        "gsi_2022_provenance_confirmed": False,
                    }
        except Exception as exc:  # noqa: BLE001 - probe failure recorded, no false pass
            result["ksdma_gsi_2022"]["error"] = f"{type(exc).__name__}: {exc}"
            result["ksdma_gsi_2022"]["status"] = "probe_failed_or_partial_NOT_verified_GSI2022"
    output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("results/gis/public_source_probe.json"))
    parser.add_argument("--download-dir", type=Path, default=Path("results/gis/pilot_raw"))
    parser.add_argument("--max-mb", type=int, default=65)
    args = parser.parse_args()
    print(json.dumps(probe(args.output, args.download_dir, max_mb=args.max_mb), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
