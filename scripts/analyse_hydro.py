"""Build empirical Kerala hydro/storage/import diagnostics and figures."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from kerala2040.hydro import (
    build_hydro_daily,
    build_reservoir_level_diagnostics,
    summarise_hydro,
)


def _figures(
    frame: pd.DataFrame,
    output_dir: Path,
    reservoir_levels: pd.DataFrame | None = None,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(10, 4.8))
    ax.plot(frame["date"], frame["storage_pct_energy_weighted"])
    ax.set_ylabel("Energy-weighted storage (%)")
    ax.set_title("Kerala reservoir storage state")
    fig.tight_layout()
    fig.savefig(output_dir / "reservoir_storage_vs_date.png", dpi=180)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(10, 4.8))
    ax.plot(frame["date"], frame["generation_capability_gross_mu"])
    ax.set_ylabel("Gross generation capability (MU)")
    ax.set_title("Reported reservoir energy-equivalent storage")
    fig.tight_layout()
    fig.savefig(output_dir / "reservoir_energy_equivalent_vs_date.png", dpi=180)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.scatter(frame["storage_pct_energy_weighted"], frame["hydel_total_mu"], s=14)
    ax.set_xlabel("Energy-weighted storage (%)")
    ax.set_ylabel("Daily hydro generation (MU)")
    ax.set_title("Hydro generation vs reservoir storage")
    fig.tight_layout()
    fig.savefig(output_dir / "hydro_vs_storage.png", dpi=180)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.scatter(frame["inflow_mu"], frame["hydel_total_mu"], s=14)
    ax.set_xlabel("Reported reservoir inflow (MU equivalent)")
    ax.set_ylabel("Daily hydro generation (MU)")
    ax.set_title("Hydro generation vs reservoir inflow")
    fig.tight_layout()
    fig.savefig(output_dir / "hydro_vs_inflow.png", dpi=180)
    plt.close(fig)

    if "precip_mm_day_mean" in frame and frame["precip_mm_day_mean"].notna().any():
        fig, ax = plt.subplots(figsize=(7, 5))
        ax.scatter(frame["precip_mm_day_mean"], frame["hydel_total_mu"], s=14)
        ax.set_xlabel("Representative-point precipitation (mm/day)")
        ax.set_ylabel("Daily hydro generation (MU)")
        ax.set_title("Hydro generation vs representative precipitation")
        fig.tight_layout()
        fig.savefig(output_dir / "hydro_vs_precipitation.png", dpi=180)
        plt.close(fig)

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.scatter(frame["hydel_total_mu"], frame["net_import_interface_mu"], s=14)
    ax.set_xlabel("Daily hydro generation (MU)")
    ax.set_ylabel("Daily net interface imports (MU)")
    ax.set_title("Interstate imports vs hydro generation")
    fig.tight_layout()
    fig.savefig(output_dir / "imports_vs_hydro.png", dpi=180)
    plt.close(fig)

    if reservoir_levels is not None and not reservoir_levels.empty:
        valid = reservoir_levels[
            ["normalised_level", "hydel_total_mu"]
        ].dropna()
        if not valid.empty:
            fig, ax = plt.subplots(figsize=(7, 5))
            ax.scatter(valid["normalised_level"], valid["hydel_total_mu"], s=10)
            ax.set_xlabel("Reported reservoir level, normalized MDDL→FRL")
            ax.set_ylabel("System daily hydro generation (MU)")
            ax.set_title("System hydro vs reported reservoir levels — context only")
            fig.tight_layout()
            fig.savefig(output_dir / "hydro_vs_normalised_reservoir_level.png", dpi=180)
            plt.close(fig)

    grouped = frame.groupby("season", observed=True)["hydel_total_mu"].mean().sort_index()
    fig, ax = plt.subplots(figsize=(7, 4.8))
    ax.bar(grouped.index, grouped.values)
    ax.set_ylabel("Mean daily hydro generation (MU)")
    ax.set_title("Observed hydro generation by diagnostic season")
    ax.tick_params(axis="x", rotation=20)
    fig.tight_layout()
    fig.savefig(output_dir / "hydro_by_season.png", dpi=180)
    plt.close(fig)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--daily", type=Path, default=Path("data/processed/sldc_daily.parquet"))
    parser.add_argument(
        "--storage", type=Path, default=Path("data/processed/sldc_storage_daily.parquet")
    )
    parser.add_argument(
        "--weather", type=Path, default=Path("data/processed/weather_points.parquet")
    )
    parser.add_argument(
        "--reservoirs",
        type=Path,
        default=Path("data/processed/sldc_storage_reservoirs.parquet"),
    )
    parser.add_argument("--output-dir", type=Path, default=Path("results/hydro"))
    parser.add_argument("--figure-dir", type=Path, default=Path("figures/hydro"))
    args = parser.parse_args()

    weather = pd.read_parquet(args.weather) if args.weather.exists() else None
    frame = build_hydro_daily(
        pd.read_parquet(args.daily),
        pd.read_parquet(args.storage),
        weather,
    )
    summary = summarise_hydro(frame)
    reservoir_levels = None
    if args.reservoirs.exists():
        reservoir_levels, reservoir_summary = build_reservoir_level_diagnostics(
            frame,
            pd.read_parquet(args.reservoirs),
        )
        summary["reservoir_level_diagnostics"] = reservoir_summary

    args.output_dir.mkdir(parents=True, exist_ok=True)
    frame.to_parquet(args.output_dir / "hydro_daily.parquet", index=False)
    if reservoir_levels is not None:
        reservoir_levels.to_parquet(
            args.output_dir / "reservoir_level_diagnostics.parquet",
            index=False,
        )
    (args.output_dir / "summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    _figures(frame, args.figure_dir, reservoir_levels)
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
