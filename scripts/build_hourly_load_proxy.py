"""Build the FY2024-25 Kerala hourly load proxy used for chronological model calibration."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd
import yaml

from kerala2040.load_proxy import (
    build_hourly_proxy,
    complete_daily_energy,
    fit_proxy_shape,
    proxy_summary,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--daily",
        type=Path,
        default=Path("data/processed/sldc_daily.parquet"),
        help="Measured/derived SLDC daily balance parquet.",
    )
    parser.add_argument(
        "--cea-config",
        type=Path,
        default=Path("configs/cea_resource_adequacy_2025.yaml"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/processed/hourly_load_proxy.parquet"),
    )
    parser.add_argument(
        "--summary",
        type=Path,
        default=Path("results/baseline/hourly_load_proxy_summary.json"),
    )
    args = parser.parse_args()

    daily_raw = pd.read_parquet(args.daily)
    daily = complete_daily_energy(daily_raw)
    cea = yaml.safe_load(args.cea_config.read_text(encoding="utf-8"))
    hourly_reference = cea["hourly_demand_2024_25"]
    bins = hourly_reference["frequency_bins"]
    annual_energy_mu = float(cea["actual_2024_25"]["electrical_energy_requirement_mu"])
    peak_mw = float(cea["actual_2024_25"]["peak_demand_mw"])

    fit = fit_proxy_shape(daily, bins=bins, target_peak_mw=peak_mw)
    hourly = build_hourly_proxy(
        daily,
        afternoon_amplitude=fit.afternoon_amplitude,
        night_amplitude=fit.night_amplitude,
    )
    summary = proxy_summary(
        daily,
        hourly,
        fit,
        bins=bins,
        cea_annual_energy_mu=annual_energy_mu,
        cea_peak_mw=peak_mw,
    )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    hourly.to_parquet(args.output, index=False)
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
