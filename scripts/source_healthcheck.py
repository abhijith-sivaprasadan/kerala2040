#!/usr/bin/env python
"""Live source health check. Kept separate from deterministic unit tests."""

from __future__ import annotations

import argparse
import json
import os
from datetime import date
from pathlib import Path

from kerala2040.sources.iced import probe_page
from kerala2040.sources.nasa_power import fetch_hourly_point
from kerala2040.sources.ogd import OGDClient
from kerala2040.sources.sldc import fetch_system_statistics


def run() -> dict:
    results: dict[str, dict] = {}

    try:
        latest = fetch_system_statistics()
        metrics = latest["metrics"]
        results["kerala_sldc"] = {
            "status": "ok",
            "report_date": latest["report_date"],
            "internal_generation_mu": metrics["internal_generation_mu"],
            "net_import_mu": metrics["net_import_interface_mu"],
            "consumption_mu": metrics["consumption_mu"],
            "balance_error_mu": latest["balance_error_mu"],
        }
    except Exception as exc:  # noqa: BLE001 - a health probe must report source failures
        results["kerala_sldc"] = {"status": "error", "error": str(exc)}

    try:
        frame, metadata = fetch_hourly_point(
            latitude=9.9312,
            longitude=76.2673,
            start=date(2025, 4, 1),
            end=date(2025, 4, 1),
        )
        results["nasa_power"] = {
            "status": "ok" if len(frame) == 24 else "error",
            "rows": len(frame),
            "non_null_temperature": int(frame["temp_c"].notna().sum()),
            "non_null_irradiance": int(frame["ghi_wh_m2"].notna().sum()),
            "api": metadata.get("api"),
        }
    except Exception as exc:  # noqa: BLE001 - a health probe must report source failures
        results["nasa_power"] = {"status": "error", "error": str(exc)}

    try:
        info = probe_page()
        results["niti_iced"] = {
            "status": "ok",
            "mode": info["mode"],
            "http_status": info["http_status"],
            "download_links_visible_in_html": len(info["download_links"]),
        }
    except Exception as exc:  # noqa: BLE001 - a health probe must report source failures
        results["niti_iced"] = {"status": "error", "error": str(exc)}

    if os.getenv("DATA_GOV_API_KEY") and os.getenv("DATA_GOV_RESOURCE_ID"):
        try:
            with OGDClient() as client:
                frame, metadata = client.fetch_resource(
                    os.environ["DATA_GOV_RESOURCE_ID"], max_records=1
                )
            results["data_gov_in"] = {
                "status": "ok",
                "rows_sampled": len(frame),
                "resource_id": metadata["resource_id"],
            }
        except Exception as exc:  # noqa: BLE001 - report optional-source failures
            results["data_gov_in"] = {"status": "error", "error": str(exc)}
    else:
        results["data_gov_in"] = {
            "status": "skip",
            "reason": "set DATA_GOV_API_KEY and DATA_GOV_RESOURCE_ID to probe",
        }

    return results


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json-output", type=Path)
    parser.add_argument("--strict-core", action="store_true")
    args = parser.parse_args()

    results = run()
    print(json.dumps(results, indent=2, sort_keys=True))
    if args.json_output:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(json.dumps(results, indent=2), encoding="utf-8")

    if args.strict_core:
        core_failed = any(
            results.get(name, {}).get("status") != "ok"
            for name in ("kerala_sldc", "nasa_power")
        )
        return 1 if core_failed else 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
