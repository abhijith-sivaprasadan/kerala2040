#!/usr/bin/env python
"""Probe registered source endpoints and write a lightweight availability audit."""

from __future__ import annotations

import argparse
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests
import yaml

PREFERRED_URL_KEYS = (
    "probe_url",
    "system_statistics_url",
    "tracker",
    "hazard_maps",
    "open_data",
    "economic_review_2025",
    "catalog",
    "home",
    "endpoint",
    "file_api",
)


def choose_url(source: dict[str, Any]) -> str | None:
    for key in PREFERRED_URL_KEYS:
        value = source.get(key)
        if isinstance(value, str) and value.startswith("http"):
            return value
    return None


def probe(url: str, timeout: float) -> dict[str, Any]:
    started = time.perf_counter()
    try:
        response = requests.get(
            url,
            timeout=(8, timeout),
            allow_redirects=True,
            stream=True,
            headers={"User-Agent": "Kerala2040Research/1.0 (+https://github.com/abhijith-sivaprasadan/kerala2040)"},
        )
        elapsed = round((time.perf_counter() - started) * 1000)
        status = response.status_code
        response.close()
        if 200 <= status < 400:
            state = "reachable"
        elif status in {401, 403, 405, 429}:
            state = "reachable_restricted"
        else:
            state = "http_error"
        return {
            "status": state,
            "http_status": status,
            "elapsed_ms": elapsed,
            "final_url": response.url,
        }
    except requests.RequestException as exc:
        elapsed = round((time.perf_counter() - started) * 1000)
        return {
            "status": "unreachable",
            "elapsed_ms": elapsed,
            "error": f"{type(exc).__name__}: {exc}",
        }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=Path("configs/sources.yaml"))
    parser.add_argument("--output", type=Path, default=Path("results/source_audit.json"))
    parser.add_argument("--timeout", type=float, default=15.0)
    args = parser.parse_args()

    config = yaml.safe_load(args.config.read_text(encoding="utf-8")) or {}
    results: dict[str, Any] = {
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "classification": "connectivity_probe_not_data_validation",
        "sources": {},
    }

    for source_id, source in config.get("sources", {}).items():
        url = choose_url(source)
        entry = {
            "priority": source.get("priority"),
            "organisation": source.get("organisation"),
            "acquisition": source.get("acquisition"),
            "probe_url": url,
        }
        if url:
            entry.update(probe(url, args.timeout))
        else:
            entry["status"] = "no_probe_url"
        results["sources"][source_id] = entry

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(json.dumps(results, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
