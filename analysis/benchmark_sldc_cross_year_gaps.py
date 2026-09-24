"""Private-data cross-year SLDC daily gap benchmark; aggregate results only.

Input: locally retrieved curated/sldc_2019_2026/daily_system.csv.
No detailed third-party SLDC records are written by this script.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path
from statistics import mean, median


def load(path: Path) -> dict[date, float]:
    result = {}
    with path.open(newline="", encoding="utf-8-sig") as stream:
        for row in csv.DictReader(stream):
            day = date.fromisoformat(row["date"])
            if day in result:
                raise ValueError("Duplicate source date")
            if row["energy_balance_qualified"] != "True" or not row["consumption_qualified_mu"]:
                continue
            value = float(row["consumption_qualified_mu"])
            if not math.isfinite(value) or value <= 0:
                raise ValueError("Invalid qualified consumption")
            result[day] = value
    return result


def nearby(data: dict[date, float], day: date, window: int = 7) -> list[float]:
    return [
        data[day + timedelta(days=offset)]
        for offset in range(-window, window + 1)
        if offset and day + timedelta(days=offset) in data
    ]


def interpolate(data: dict[date, float], day: date, window: int = 7) -> float | None:
    bounds = []
    for direction in (-1, 1):
        match = next(
            ((n, data[day + timedelta(days=direction * n)])
             for n in range(1, window + 1)
             if day + timedelta(days=direction * n) in data),
            None,
        )
        if match is None:
            return None
        bounds.append(match)
    (a, left), (b, right) = bounds
    return (b * left + a * right) / (a + b)


def historical_factor(
    data: dict[date, float], day: date, *,
    min_years: int = 3, window: int = 7,
) -> tuple[float | None, int]:
    """Same Gregorian date, normalized by *that other year's* nearby demand.

    Excludes target year entirely. Does not infer a holiday/weekday effect.
    """
    factors = []
    for year in sorted({d.year for d in data} - {day.year}):
        try:
            other = day.replace(year=year)
        except ValueError:  # 29 February has no analogue in most years
            continue
        if other not in data:
            continue
        context = nearby(data, other, window)
        if len(context) < 6:
            continue
        baseline = median(context)
        if baseline > 0:
            factors.append(data[other] / baseline)
    return (median(factors), len(factors)) if len(factors) >= min_years else (None, len(factors))


def predict(\n    data: dict[date, float], day: date, min_years: int = 3, *,\n    historical_training: dict[date, float] | None = None,\n) -> dict:
    """Target date MUST be masked by caller; all baselines are target-year local."""
    if day in data:
        raise ValueError("Target must be masked before prediction")
    context = nearby(data, day)
    baseline = median(context) if len(context) >= 4 else None
    linear = interpolate(data, day)
    # The training pool can exclude the *entire* held-out year.\n    factor, years = historical_factor(\n        data if historical_training is None else historical_training,\n        day, min_years=min_years,\n    )
    return {
        "interpolation": linear,
        "local_median": baseline,\n        "weekday_local": weekday_baseline,\n        "historical_weekday_adjusted": (weekday_baseline * factor\n                                        if weekday_baseline is not None and factor is not None else None),
        "historical_adjusted": baseline * factor if baseline is not None and factor is not None else None,
        "historical_analogue_years": years,
    }


def benchmark(data: dict[date, float], *, min_years: int = 3) -> dict:
    errors = defaultdict(list)\n    residuals_by_year = defaultdict(lambda: defaultdict(list))
    paired = defaultdict(list)
    by_year = defaultdict(lambda: defaultdict(list))
    for day, actual in sorted(data.items()):
        # Mask whole target date; other years may be used only as independent analogues.
        masked = dict(data)
        del masked[day]
        training = {d: value for d, value in masked.items() if d.year != day.year}\n        candidates = predict(masked, day, min_years=min_years, historical_training=training)
        for method in ("interpolation", "local_median", "weekday_local", "historical_adjusted",\n                       "historical_weekday_adjusted"):
            estimate = candidates[method]
            if estimate is not None:
                err = estimate - actual
                errors[method].append(err)
                by_year[str(day.year)][method].append(err)\n                residuals_by_year[day.year][method].append(err)
        if candidates["interpolation"] is not None and candidates["historical_adjusted"] is not None:
            paired["interpolation"].append(candidates["interpolation"] - actual)
            paired["historical_adjusted"].append(candidates["historical_adjusted"] - actual)

    def stats(values: list[float]) -> dict:
        return {
            "n": len(values),
            "mae_mu": round(mean(abs(x) for x in values), 5) if values else None,
            "bias_mu": round(mean(values), 5) if values else None,
            "rmse_mu": round(math.sqrt(mean(x * x for x in values)), 5) if values else None,
        }

    return {
        "classification": "CROSS_YEAR_SLDC_DAILY_GAP_BENCHMARK_NOT_INTERVAL_TELEMETRY",
        "qualified_observed_days": len(data),
        "min_other_year_analogues": min_years,
        "methods_all_eligible": {k: stats(v) for k, v in errors.items()},
        "paired_interpolation_vs_historical": {k: stats(v) for k, v in paired.items()},
        "yearwise": {year: {k: stats(v) for k, v in methods.items()}
                     for year, methods in sorted(by_year.items())},
        "limitations": [
            "Historical analogue training excludes entire target calendar year; local interpolation and target-year baseline retain observed neighbouring days.",\n            "This is not leave-one-year-out evaluation of a model that uses no target-year observations.",
            "Other-year same-date ratios confound weekday, festivals and weather.",
            "Error-band coverage is marginal and retrospective; not a calibrated conditional interval for actual missing gaps.",\n            "No verified movable-festival calendar or weather controls; weekday matching is not festival control.",
            "Method comparison must use paired cases, not unequal eligible-date counts.",
            "Input daily source rows remain private; this report contains aggregates only.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--out", type=Path, default=Path("outputs/sldc_cross_year_gap_qa.json"))
    parser.add_argument("--min-years", type=int, default=3)
    args = parser.parse_args()
    if args.min_years < 2:
        parser.error("--min-years must be at least 2")
    data = load(args.input)
    result = benchmark(data, min_years=args.min_years)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
