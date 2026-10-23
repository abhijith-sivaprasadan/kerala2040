"""Independently audit observed SLDC daily totals against the hourly MODELLED proxy.

Python standard library only. This audit verifies daily energy accounting, NOT intraday
physical correctness or forecast skill. Missing SLDC days are never treated as observations.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DAILY = "data/external/sldc_fy2024_25/daily_balance.csv"
QA = "data/external/sldc_fy2024_25/qa_report.json"
PROXY = "public/hourly-load-proxy.json"
TOLERANCE_MU = 1e-4


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def audit(root: Path = ROOT) -> dict:
    raw = {p: (root / p).read_bytes() for p in (DAILY, QA, PROXY)}
    qa = json.loads(raw[QA])
    proxy = json.loads(raw[PROXY])
    daily = list(csv.DictReader(raw[DAILY].decode("utf-8-sig").splitlines()))
    if proxy.get("classification") != "proxy_reconstruction_not_measured_telemetry":
        raise ValueError("Wrong proxy evidence class; refusing to imply measured hourly load")
    if proxy.get("timezone") != "Asia/Kolkata" or proxy.get("interval") != "1h":
        raise ValueError("Unexpected timezone or temporal resolution")
    if len(daily) != 365 or len({x["date"] for x in daily}) != 365:
        raise ValueError("Expected 365 distinct SLDC dates")
    if [r["date"] for r in daily] != [(date(2024, 4, 1) + timedelta(days=i)).isoformat() for i in range(365)]:
        raise ValueError("Daily dates not contiguous FY2024–25")
    missing = sorted(r["date"] for r in daily if r["status"] != "observed")
    observed = [r for r in daily if r["status"] == "observed"]
    if missing != sorted(qa["missing_dates"]) or len(observed) != qa["observed_days"] or len(missing) != 11:
        raise ValueError("Missing-day provenance differs from original QA")
    for row in daily:
        for key in ("hydro_mu", "internal_generation_mu", "net_import_mu", "consumption_mu"):
            if row["status"] == "observed":
                if not row[key] or not math.isfinite(float(row[key])):
                    raise ValueError("Invalid observed source numerical value")
            elif row[key].strip():
                raise ValueError("Missing-source day has incorrectly acquired an observed value")
    rows = proxy.get("records", [])
    if len(rows) != 8760:
        raise ValueError("Expected 8760 reconstructed hourly records")
    sums = defaultdict(float)
    counts = defaultdict(int)
    flags = defaultdict(set)
    timestamps = set()
    last_time = None
    from datetime import datetime, timezone
    for row in rows:
        if row.get("classification") != "proxy_reconstruction":
            raise ValueError("Hourly record mislabelled as observed")
        stamp = datetime.fromisoformat(row["timestamp"])
        if stamp.tzinfo is None or stamp.utcoffset().total_seconds() != 19800:
            raise ValueError("Hourly timestamps must be India-local (+05:30)")
        instant = stamp.astimezone(timezone.utc)
        if instant in timestamps or (last_time is not None and (instant - last_time).total_seconds() != 3600):
            raise ValueError("Non-contiguous or duplicate hourly timestamp")
        last_time = instant
        timestamps.add(instant)
        day = stamp.date().isoformat()
        v = float(row["load_mw"])
        if not math.isfinite(v) or v <= 0:
            raise ValueError("Non-finite or nonpositive proxy demand")
        sums[day] += v / 1000  # hourly MW × 1h -> MWh -> MU (million kWh)
        counts[day] += 1
        flags[day].add(row.get("daily_energy_imputed"))
    if sorted(counts) != [r["date"] for r in daily] or any(v != 24 for v in counts.values()):
        raise ValueError("Proxy day/hour coverage disagrees with SLDC days")
    residuals = []
    for row in daily:
        day = row["date"]
        imputed = row["status"] != "observed"
        if flags[day] != {imputed}:
            raise ValueError("Model-only/observed-day flag disagreement")
        if not imputed:
            discrepancy = sums[day] - float(row["consumption_mu"])
            if abs(discrepancy) > TOLERANCE_MU:
                raise ValueError(f"Observed daily-energy conservation fails for {day}: {discrepancy:.8f} MU")
            residuals.append(abs(discrepancy))
    observed_consumption = sum(float(r["consumption_mu"]) for r in observed)
    if abs(observed_consumption - float(qa["observed_days_totals_mu"]["consumption_mu"])) > TOLERANCE_MU:
        raise ValueError("Observed source totals differ from the original QA")
    return {
        "audit": "kerala2040.observed_daily_energy_vs_proxy.v1",
        "evidence": "354 observed daily totals and 8760 MODELLED hourly data; NOT hour-level validation",
        "source_sha256": {p: digest(content) for p, content in raw.items()},
        "observed_days": len(observed), "missing_source_days": len(missing),
        "missing_dates": missing, "reconstructed_hours": len(rows),
        "observed_source_consumption_mu": round(observed_consumption, 4),
        "max_abs_observed_day_energy_residual_mu": max(residuals),
        "result": "PASS_INVARIANT_NOT_PHYSICAL_VALIDATION",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = audit()
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(encoded, encoding="utf-8")
    print(encoded, end="")


if __name__ == "__main__":
    main()
