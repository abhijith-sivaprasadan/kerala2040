#!/usr/bin/env python
"""Create auditable daily-baseline summaries and figures."""

from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path

import matplotlib
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from kerala2040.analysis import add_daily_indicators, summarise_daily_baseline


def _plot(data: pd.DataFrame, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(10, 4.8))
    ax.plot(data["date"], data["consumption_mu"], label="Consumption")
    ax.plot(data["date"], data["internal_generation_mu"], label="Internal generation")
    ax.plot(data["date"], data["net_import_interface_mu"], label="Net imports")
    ax.set_ylabel("Daily energy (MU)")
    ax.set_title("Kerala daily electricity balance")
    ax.legend()
    fig.tight_layout()
    fig.savefig(output_dir / "daily_energy_balance.png", dpi=180)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(10, 4.8))
    ax.plot(data["date"], 100.0 * data["import_share"])
    ax.set_ylabel("Net imports / consumption (%)")
    ax.set_title("Daily interstate import dependence")
    fig.tight_layout()
    fig.savefig(output_dir / "daily_import_share.png", dpi=180)
    plt.close(fig)

    duration = data["import_share"].dropna().sort_values(ascending=False).reset_index(drop=True)
    fig, ax = plt.subplots(figsize=(7.5, 4.8))
    ax.plot(range(1, len(duration) + 1), 100.0 * duration)
    ax.set_xlabel("Ranked day")
    ax.set_ylabel("Net imports / consumption (%)")
    ax.set_title("Daily import-dependence duration curve")
    fig.tight_layout()
    fig.savefig(output_dir / "import_share_duration_curve.png", dpi=180)
    plt.close(fig)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=Path("data/processed/sldc_daily.parquet"))
    parser.add_argument(
        "--storage", type=Path, default=Path("data/processed/sldc_storage_daily.parquet")
    )
    parser.add_argument("--start", type=date.fromisoformat, default=date(2024, 4, 1))
    parser.add_argument("--end", type=date.fromisoformat, default=date(2025, 3, 31))
    parser.add_argument("--minimum-coverage", type=float, default=0.95)
    parser.add_argument("--balance-tolerance-mu", type=float, default=0.05)
    parser.add_argument("--output-dir", type=Path, default=Path("results/baseline"))
    parser.add_argument("--figure-dir", type=Path, default=Path("figures/baseline"))
    parser.add_argument("--fail-on-gate", action="store_true")
    args = parser.parse_args()

    data = add_daily_indicators(pd.read_parquet(args.input))
    summary = summarise_daily_baseline(
        data,
        expected_start=args.start,
        expected_end=args.end,
        minimum_coverage=args.minimum_coverage,
        balance_tolerance_mu=args.balance_tolerance_mu,
    )

    if args.storage.exists():
        storage = pd.read_parquet(args.storage).copy()
        storage["date"] = pd.to_datetime(storage["date"]).dt.normalize()
        data = data.merge(storage, on="date", how="left", suffixes=("", "_storage"))
        available = data["storage_pct_energy_weighted"].dropna()
        summary["storage_days"] = available.size
        if not available.empty:
            summary["storage_pct_energy_weighted_min"] = float(available.min())
            summary["storage_pct_energy_weighted_median"] = float(available.median())
            summary["storage_pct_energy_weighted_max"] = float(available.max())

    args.output_dir.mkdir(parents=True, exist_ok=True)
    data.to_parquet(args.output_dir / "daily_indicators.parquet", index=False)
    (args.output_dir / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8"
    )
    _plot(data, args.figure_dir)
    print(json.dumps(summary, indent=2, sort_keys=True))
    if args.fail_on_gate and not summary["calibration_gate_pass"]:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
