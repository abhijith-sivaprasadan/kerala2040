"""Extract Idukki rows directly from official KSEB Dam Safety pages."""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import requests

from kerala2040.kseb_dam_safety_official_v1_5 import (
    KSEBSourceError,
    discover_dated_post_links,
    parse_kseb_reservoir_page,
    utc_now_iso,
)

DEFAULT_INDEX = "https://dams.kseb.in/?page_id=45"


def fetch(url: str, timeout: float) -> str:
    response = requests.get(
        url,
        timeout=timeout,
        headers={
            "User-Agent": (
                "kerala2040-research/1.5 "
                "(official KSEB Dam Safety source extraction)"
            )
        },
    )
    response.raise_for_status()
    return response.text


def flatten(record: dict) -> dict:
    flat = {
        "date": record["date"],
        "dam": record["dam"],
        "source_url": record["source_url"],
        "schema_fingerprint_sha256": record["schema"]["fingerprint_sha256"],
        "schema_column_count": record["schema"]["column_count"],
    }
    flat.update(record["metrics"])
    return flat


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", action="append", default=[])
    parser.add_argument("--url-file", type=Path)
    parser.add_argument("--index-url", default=None)
    parser.add_argument("--start")
    parser.add_argument("--end")
    parser.add_argument("--timeout", type=float, default=30.0)
    parser.add_argument("--out-json", type=Path)
    parser.add_argument("--out-csv", type=Path)
    args = parser.parse_args()

    urls = list(args.url)
    if args.url_file:
        urls.extend(
            line.strip()
            for line in args.url_file.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.lstrip().startswith("#")
        )

    if args.index_url:
        index_html = fetch(args.index_url, args.timeout)
        discovered = discover_dated_post_links(
            index_html,
            base_url=args.index_url,
        )
        for item in discovered:
            if args.start and item["date"] < args.start:
                continue
            if args.end and item["date"] > args.end:
                continue
            urls.append(item["url"])

    urls = list(dict.fromkeys(urls))
    if not urls:
        raise SystemExit(
            "No official KSEB page URLs supplied or discovered. "
            f"Use --url, --url-file, or --index-url {DEFAULT_INDEX!r}."
        )

    records = []
    errors = []
    for url in urls:
        try:
            html = fetch(url, args.timeout)
            records.append(parse_kseb_reservoir_page(html, source_url=url))
        except (requests.RequestException, KSEBSourceError) as exc:
            errors.append({"source_url": url, "error": str(exc)})

    records.sort(key=lambda x: x["date"])
    result = {
        "classification": "OFFICIAL_KSEB_IDUKKI_EXTRACTION_V1_5",
        "retrieved_at": utc_now_iso(),
        "records": records,
        "errors": errors,
        "record_count": len(records),
        "error_count": len(errors),
    }

    if args.out_json:
        args.out_json.parent.mkdir(parents=True, exist_ok=True)
        args.out_json.write_text(
            json.dumps(result, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

    if args.out_csv:
        rows = [flatten(record) for record in records]
        keys = sorted({key for row in rows for key in row})
        args.out_csv.parent.mkdir(parents=True, exist_ok=True)
        with args.out_csv.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=keys)
            writer.writeheader()
            writer.writerows(rows)

    print(json.dumps(result, indent=2, sort_keys=True))
    if errors:
        raise SystemExit(
            f"Official KSEB extraction rejected {len(errors)} page(s); "
            "see errors above."
        )


if __name__ == "__main__":
    main()
