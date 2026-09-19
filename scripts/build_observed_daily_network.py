"""Build the FY2024-25 observed-detail Kerala PyPSA replay network.

This is a 354-observed-day evidence replay. It does not reconstruct missing days,
hourly load, hydro dispatch, reservoir operation, or transfer capability.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from kerala2040.observed_daily_network import (
    build_observed_detail_network,
    observed_detail_summary,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--daily",
        type=Path,
        default=Path("data/external/sldc_fy2024_25/daily_balance.csv"),
    )
    parser.add_argument(
        "--hydro",
        type=Path,
        default=Path("data/external/sldc_fy2024_25/hydro_station_daily.csv"),
    )
    parser.add_argument(
        "--imports",
        type=Path,
        default=Path("data/external/sldc_fy2024_25/import_interface_daily.csv"),
    )
    parser.add_argument(
        "--qa",
        type=Path,
        default=Path("data/external/sldc_fy2024_25/qa_report.json"),
    )
    parser.add_argument(
        "--network-output",
        type=Path,
        default=Path("results/models/observed_daily_detail/kerala_fy2024_25_observed_detail.nc"),
    )
    parser.add_argument(
        "--summary-output",
        type=Path,
        default=Path("results/models/observed_daily_detail/summary.json"),
    )
    args = parser.parse_args()

    daily = pd.read_csv(args.daily)
    hydro = pd.read_csv(args.hydro)
    imports = pd.read_csv(args.imports)
    qa = json.loads(args.qa.read_text(encoding="utf-8"))

    network = build_observed_detail_network(daily, hydro, imports, qa=qa)
    summary = observed_detail_summary(network)

    expected_days = int(qa["observed_days"])
    if len(network.snapshots) != expected_days:
        raise RuntimeError(
            f"network contains {len(network.snapshots)} observed days; QA expects {expected_days}"
        )
    if abs(summary["balance_error_mwh"]) > 0.2:
        raise RuntimeError(
            f"observed-detail replay does not close: {summary['balance_error_mwh']:.6f} MWh"
        )

    args.network_output.parent.mkdir(parents=True, exist_ok=True)
    network.export_to_netcdf(args.network_output)
    args.summary_output.parent.mkdir(parents=True, exist_ok=True)
    args.summary_output.write_text(
        json.dumps(summary, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )

    print(
        json.dumps(
            {
                "classification": summary["classification"],
                "model_role": summary["model_role"],
                "observed_days": summary["observed_days"],
                "load_twh": summary["load_mwh"] / 1_000_000,
                "balance_error_mwh": summary["balance_error_mwh"],
                "network_output": str(args.network_output),
                "summary_output": str(args.summary_output),
                "hourly_telemetry": "NOT USED",
                "reservoir_dispatch_constraints": "NOT YET VERIFIED",
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
