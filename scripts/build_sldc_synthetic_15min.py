"""Observed-daily-anchored synthetic quarter-hour demand, with honest gap flags.

No intraday measurements or calendar-day recurrence are inferred from daily MU.
Standard-library-only deterministic generator. Missing dates use a local
interpolation *candidate*, never a reported observation. No annual claim
without an explicit observed/estimated split.
"""
from __future__ import annotations

import csv
import json
import math
import random
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from statistics import mean, median

SOURCE = Path("data/external/sldc_fy2024_25/daily_balance.csv")
CLASSIFICATION = "SYNTHETIC_15MIN_DAILY_SLDC_ANCHORED_NOT_OBSERVED_INTERVAL_LOAD"
METHODS = ("flat", "morning_evening", "evening_stress")
UTC = timezone.utc
IST = timezone(timedelta(hours=5, minutes=30))


def read_daily(path: Path = SOURCE) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    dates = [date.fromisoformat(r["date"]) for r in rows]
    if len(dates) != len(set(dates)):
        raise ValueError("Duplicate SLDC dates")
    if not dates or dates != [dates[0] + timedelta(days=i) for i in range(len(dates))]:
        raise ValueError("Incomplete or unsorted daily calendar")
    for row in rows:
        if row["status"] == "observed":
            if row["classification"] != "official_observed_reference":
                raise ValueError("Unexpected observation classification")
            energy = float(row["consumption_mu"])
            if not math.isfinite(energy) or energy <= 0 or not row["source_sha256"]:
                raise ValueError("Invalid observed energy or missing source hash")
        elif row["status"] != "missing":
            raise ValueError("Unexpected daily source status")
    return rows


def local_gap_estimate(rows: list[dict], index: int, excluded: set[int] | None = None) -> float | None:
    """Interpolate bounding observed days within seven days, never silently extrapolate."""
    excluded = excluded or set()
    bounds = []
    for step in (-1, 1):
        match = None
        for distance in range(1, 8):
            j = index + step * distance
            if 0 <= j < len(rows) and j not in excluded and rows[j]["status"] == "observed":
                match = (distance, float(rows[j]["consumption_mu"]))
                break
        bounds.append(match)
    if any(x is None for x in bounds):
        return None
    (left_days, left_mu), (right_days, right_mu) = bounds
    return (right_days * left_mu + left_days * right_mu) / (left_days + right_days)


def benchmark(rows: list[dict]) -> dict:
    """Leave-one-observed-date-out; identical held-out dates for all candidates."""
    errors = {"interpolation": [], "local_median": []}
    for i, row in enumerate(rows):
        if row["status"] != "observed":
            continue
        actual = float(row["consumption_mu"])
        nearby = [
            float(rows[j]["consumption_mu"])
            for j in range(max(0, i - 7), min(len(rows), i + 8))
            if j != i and rows[j]["status"] == "observed"
        ]
        predictions = {
            "interpolation": local_gap_estimate(rows, i, {i}),
            "local_median": median(nearby) if len(nearby) >= 4 else None,
        }
        for method, predicted in predictions.items():
            if predicted is not None:
                errors[method].append(predicted - actual)
    return {
        method: {
            "held_out_observed_days": len(values),
            "mae_mu": mean(abs(e) for e in values) if values else None,
            "bias_mu": mean(values) if values else None,
        }
        for method, values in errors.items()
    }


def shape(day: date, method: str, seed: int = 0) -> list[float]:
    if method not in METHODS:
        raise ValueError("Unknown synthetic shape")
    rng = random.Random(f"{seed}:{day.isoformat()}:{method}")
    weights = []
    for slot in range(96):
        hour = slot / 4
        morning = math.exp(-0.5 * ((hour - 9) / 2.6) ** 2)
        evening = math.exp(-0.5 * ((hour - 19.25) / 2.2) ** 2)
        if method == "flat":
            value = 1.0
        elif method == "morning_evening":
            value = 0.77 + 0.19 * morning + 0.43 * evening
        else:
            value = 0.65 + 0.15 * morning + 0.8 * evening
        # Bounded, temporally correlated illustrative variation; not fitted to Kerala.
        weights.append(value * (1 + 0.015 * rng.uniform(-1, 1)))
    return weights


def generate(rows: list[dict], *, seed: int = 2040, estimate_missing: bool = True) -> tuple[list[dict], list[dict], dict]:
    daily, intervals = [], []
    for i, row in enumerate(rows):
        observed = row["status"] == "observed"
        energy = float(row["consumption_mu"]) if observed else (
            local_gap_estimate(rows, i) if estimate_missing else None
        )
        status = "observed_daily_anchor" if observed else (
            "estimated_daily_anchor" if energy is not None else "unavailable_daily_anchor"
        )
        daily.append({
            "date": row["date"], "anchor_status": status,
            "daily_energy_mu": energy,
            "observed_daily_energy_mu": float(row["consumption_mu"]) if observed else None,
            "source_sha256": row["source_sha256"] if observed else None,
            "daily_estimator": None if observed else ("local_interpolation_candidate" if energy is not None else None),
        })
        if energy is None:
            continue
        day = date.fromisoformat(row["date"])
        for method in METHODS:
            weights = shape(day, method, seed)
            denominator = sum(weights)
            # Each interval is 0.25 h; daily MU -> 1000 MWh.
            powers = [4000 * energy * w / denominator for w in weights]
            if abs(sum(powers) / 4000 - energy) > 1e-9:
                raise AssertionError("Daily energy reconciliation failed")
            for slot, mw in enumerate(powers):
                local = datetime(day.year, day.month, day.day, tzinfo=IST) + timedelta(minutes=15 * slot)
                intervals.append({
                    "timestamp_ist": local.isoformat(),
                    "timestamp_utc": local.astimezone(UTC).isoformat(),
                    "date_ist": row["date"], "scenario_id": method, "seed": seed,
                    "interval_hours": 0.25, "demand_mw": round(mw, 9),
                    "daily_anchor_mu": energy, "daily_anchor_status": status,
                    "classification": CLASSIFICATION,
                })
    observed = [d["daily_energy_mu"] for d in daily if d["anchor_status"] == "observed_daily_anchor"]
    estimated = [d["daily_energy_mu"] for d in daily if d["anchor_status"] == "estimated_daily_anchor"]
    report = {
        "classification": CLASSIFICATION, "interval_minutes": 15,
        "source": str(SOURCE), "seed": seed, "scenarios": list(METHODS),
        "observed_days": len(observed), "estimated_days": len(estimated),
        "unavailable_days": len(daily) - len(observed) - len(estimated),
        "observed_days_energy_mu": sum(observed),
        "estimated_missing_days_energy_mu": sum(estimated),
        "reconstructed_full_period_mu": sum(observed) + sum(estimated) if len(observed) + len(estimated) == len(daily) else None,
        "benchmark": benchmark(rows),
        "limitations": [
            "All 15-minute profiles are illustrative and not observed Kerala telemetry.",
            "Missing-day local interpolation is a candidate, not a validated historical same-date estimator.",
            "The source package contains one FY; no cross-year date recurrence is estimated.",
            "Daily estimates have no calibrated uncertainty interval; do not use as validated annual totals.",
            "Shape variability, peak, ramp and scenario probabilities are not calibrated.",
        ],
    }
    return daily, intervals, report


def write(rows: list[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        raise ValueError("No rows to write")
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=SOURCE)
    parser.add_argument("--out-dir", type=Path, default=Path("outputs/sldc_synthetic_15min"))
    parser.add_argument("--seed", type=int, default=2040)
    parser.add_argument("--no-estimate-missing", action="store_true")
    args = parser.parse_args()
    daily, intervals, report = generate(
        read_daily(args.input), seed=args.seed, estimate_missing=not args.no_estimate_missing
    )
    write(daily, args.out_dir / "daily_anchors.csv")
    write(intervals, args.out_dir / "synthetic_15min.csv")
    (args.out_dir / "qa.json").write_text(
        json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
