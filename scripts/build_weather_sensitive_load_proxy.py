"""Build and validate the FY2024-25 ERA5-sensitive hourly Kerala load proxy.

Outputs are research artifacts, not measured telemetry:
- weather_sensitive_hourly_load.json: PyPSA-compatible 8,760-hour proxy
- weather_sensitive_hourly_load.csv.gz: compact tabular chronology
- summary.json: chronological holdout + CEA validation diagnostics
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd
import yaml

from kerala2040.weather_sensitive_load import create_proxy_and_summary


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--daily",
        type=Path,
        default=Path("data/external/sldc_fy2024_25/daily_balance.csv"),
    )
    p.add_argument(
        "--extrema",
        type=Path,
        default=Path("data/external/sldc_fy2024_25/selected_intraday_extrema.csv"),
    )
    p.add_argument(
        "--era5-daily",
        type=Path,
        default=Path("data/evidence/weather/era5_kerala_state_daily_all24_fy2024_25.csv"),
    )
    p.add_argument(
        "--cea-config",
        type=Path,
        default=Path("configs/cea_resource_adequacy_2025.yaml"),
    )
    p.add_argument(
        "--output",
        type=Path,
        default=Path("results/models/weather_sensitive_hourly_load"),
    )
    args = p.parse_args()

    daily = pd.read_csv(args.daily)
    extrema = pd.read_csv(args.extrema)
    weather = pd.read_csv(args.era5_daily)
    cea = yaml.safe_load(args.cea_config.read_text(encoding="utf-8"))
    bins = cea["hourly_demand_2024_25"]["frequency_bins"]
    peak = float(cea["actual_2024_25"]["peak_demand_mw"])

    proxy, hourly, summary = create_proxy_and_summary(
        daily,
        weather,
        extrema,
        bins=bins,
        cea_peak_mw=peak,
    )
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "weather_sensitive_hourly_load.json").write_text(
        json.dumps(proxy, separators=(",", ":"), allow_nan=False) + "\n",
        encoding="utf-8",
    )
    hourly.to_csv(
        args.output / "weather_sensitive_hourly_load.csv.gz",
        index=False,
        compression="gzip",
        float_format="%.7f",
    )
    (args.output / "summary.json").write_text(
        json.dumps(summary, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "classification": summary["classification"],
        "hours": summary["hours"],
        "measured_days": summary["daily_observations_measured"],
        "interpolated_days": summary["daily_observations_interpolated"],
        "holdout": summary["validation_against_selected_intraday_consumption_extrema"]["overall"],
        "era5_curve_rmse_change_vs_old_pct": summary[
            "validation_against_selected_intraday_consumption_extrema"
        ]["era5_curve_rmse_change_vs_old_pct"],
        "old_peak_mw": summary["old_fixed_profile_peak_mw"],
        "era5_peak_mw": summary["era5_sensitive_profile_peak_mw"],
        "output": str(args.output),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
