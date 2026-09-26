"""Audit synthetic quarter-hour scenarios and report shape sensitivity without grid claims.

Input is the generator's synthetic_15min.csv. Outputs aggregate diagnostics only.
This is not capacity expansion, dispatch optimisation or calibrated Kerala telemetry.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
from collections import defaultdict
from pathlib import Path
from statistics import mean


def audit(path: Path) -> dict:
    groups = defaultdict(list)
    with path.open(newline="", encoding="utf-8") as stream:
        for row in csv.DictReader(stream):
            if row["classification"] != (
                "SYNTHETIC_15MIN_DAILY_SLDC_ANCHORED_NOT_OBSERVED_INTERVAL_LOAD"
            ):
                raise ValueError("Unexpected source classification")
            key = (row["date_ist"], row["scenario_id"])
            power = float(row["demand_mw"])
            if not math.isfinite(power) or power <= 0:
                raise ValueError("Invalid quarter-hour power")
            groups[key].append((row["timestamp_ist"], power, float(row["daily_anchor_mu"])))
    by_scenario = defaultdict(list)
    daily = defaultdict(dict)
    for (day, scenario), slots in sorted(groups.items()):
        if len(slots) != 96 or len({t for t, _, _ in slots}) != 96:
            raise ValueError("Expected 96 unique quarter-hour intervals per day and scenario")
        if [t for t, _, _ in slots] != sorted(t for t, _, _ in slots):
            raise ValueError("Intervals must be chronologically sorted")
        anchor = slots[0][2]
        if any(abs(a - anchor) > 1e-10 for _, _, a in slots):
            raise ValueError("Daily anchor changed within day")
        powers = [mw for _, mw, _ in slots]
        if abs(sum(powers) / 4000 - anchor) > 1e-8:
            raise ValueError("Daily energy does not reconcile")
        record = {
            "peak_mw": max(powers),
            "max_quarter_hour_ramp_mw": max(
                abs(right - left) for left, right in zip(powers, powers[1:])
            ),
            "load_factor": mean(powers) / max(powers),
        }
        by_scenario[scenario].append(record)
        daily[day][scenario] = anchor
    scenarios = sorted(by_scenario)
    if not scenarios or any(set(values) != set(scenarios) for values in daily.values()):
        raise ValueError("Scenario/day coverage differs")
    if any(max(values.values()) - min(values.values()) > 1e-8 for values in daily.values()):
        raise ValueError("Daily scenario anchors disagree")
    return {
        "classification": "SYNTHETIC_SHAPE_SENSITIVITY_NOT_OBSERVED_KERALA_DISPATCH",
        "days": len(daily), "scenarios": scenarios,
        "per_scenario": {
            scenario: {
                "days": len(records),
                "maximum_modelled_peak_mw": max(r["peak_mw"] for r in records),
                "maximum_modelled_15min_ramp_mw": max(
                    r["max_quarter_hour_ramp_mw"] for r in records
                ),
                "mean_daily_load_factor": mean(r["load_factor"] for r in records),
            }
            for scenario, records in sorted(by_scenario.items())
        },
        "limits": [
            "These are assumed load-shape sensitivities, not measured Kerala peak or ramp.",
            "No generation, storage, cost, transmission or optimisation constraints are included.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    report = audit(args.input)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
