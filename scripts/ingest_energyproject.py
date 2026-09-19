"""Capture public national chart inputs, keeping them separate from Kerala telemetry.

Only the default/latest month's interval products are requested. Historical interval
navigation marked sign-in-only in the source UI is not traversed.
"""
from __future__ import annotations

import argparse
import calendar
import hashlib
import json
import math
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path

import requests

BASE = "https://www.energyproject.in/data/"
FIELDS = ("demand", "thermal", "solar", "wind", "hydro", "gas", "nuclear",
          "storage_gen", "storage_demand", "others")


def average_profile(days: list[dict], fields: tuple[str, ...]) -> list[dict]:
    values = defaultdict(lambda: defaultdict(list))
    dates = set()
    expected = {f"{h:02d}:{m:02d}" for h in range(24) for m in (0, 15, 30, 45)}
    for day in days:
        if day["date"] in dates:
            raise ValueError("Duplicate interval-product date")
        dates.add(day["date"])
        series = day["series"]
        if day["interval_min"] != 15 or len(series) != 96 or {r["t"] for r in series} != expected:
            raise ValueError(f"Incomplete quarter-hour day: {day['date']}")
        for row in series:
            for field in fields:
                value = row.get(field)
                if value is not None:
                    if not isinstance(value, (int, float)) or not math.isfinite(value):
                        raise ValueError(f"Invalid {field} observation")
                    values[row["t"]][field].append(value)
    return [{"time": time, **{field: sum(v) / len(v) for field, v in by_field.items()},
             "sample_counts": {field: len(v) for field, v in by_field.items()}}
            for time, by_field in sorted(values.items())]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("data/processed/energyproject_context.json"))
    parser.add_argument("--raw-dir", type=Path, default=Path("data/raw/energyproject"))
    args = parser.parse_args()
    args.raw_dir.mkdir(parents=True, exist_ok=True)
    sources = []
    with requests.Session() as session:
        def get(path):
            response = session.get(BASE + path, timeout=45)
            response.raise_for_status()
            data = response.json()
            (args.raw_dir / path.replace("/", "-" )).write_bytes(response.content)
            sources.append({"url": BASE + path, "sha256": hashlib.sha256(response.content).hexdigest()})
            return data

        monthly = get("grid/monthly_summary.json")
        latest = max(monthly, key=lambda r: r["month"])
        month = latest["month"]
        datetime.strptime(month, "%Y-%m").replace(tzinfo=UTC)
        generation = get(f"grid/timeseries/{month}.json")
        market = get(f"dam/{month}.json")
        if any(not r["date"].startswith(month + "-") for r in generation + market):
            raise ValueError("Interval data does not match selected month")
    profiles = average_profile(generation, FIELDS)
    market_profiles = average_profile(market, ("mcp",))
    prices = [{"time": r["time"], "price_inr_per_kwh": r.get("mcp") / 1000
               if r.get("mcp") is not None else None,
               "sample_days": r["sample_counts"].get("mcp", 0)} for r in market_profiles]
    year, month_number = map(int, month.split("-"))
    payload = {
        "classification": "secondary_national_context_not_kerala_telemetry",
        "geography": "India", "publisher": "Energy Project",
        "source_page": "https://www.energyproject.in/grid",
        "upstream_sources_as_attributed": ["NLDC", "IEX", "CEA"],
        "retrieved_at_utc": datetime.now(UTC).isoformat(), "sources": sources,
        "month": month, "month_complete": len(generation) == calendar.monthrange(year, month_number)[1],
        "generation_days": len(generation), "market_days": len(market),
        "generation_date_range": [min(r["date"] for r in generation), max(r["date"] for r in generation)],
        "market_date_range": [min(r["date"] for r in market), max(r["date"] for r in market)],
        "profile_unit": "MW", "interval_minutes": 15,
        "time_basis": "Source clock labels; timezone not declared in downloaded JSON",
        "generation_average_day": profiles, "market_average_day": prices,
        "limitations": [
            "National averages are not Kerala demand, generation or interstate interchange.",
            "Profiles average available days by time label; they are not an ordered full-year chronology.",
            "Storage discharge is shown separately and is not automatically classified as clean generation.",
            "National market clearing price is not a Kerala delivered tariff or contracted procurement cost.",
            "Upstream extraction methods and redistribution licence are not documented in these JSON files.",
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({k: payload[k] for k in ("month", "generation_days", "market_days", "classification")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
