"""Reproducible *observed-daily* SLDC figures; do not confuse with proxy PyPSA plots."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

STATIONS = ["Idukki", "Sabarigiri", "Kuttiadi", "Idamalayar"]
INTERFACES = ["400KV MDKA", "400KV PKKD", "400KV KOCHI+KOTTAYAM", "400KV KOZHKOD"]


def build_figures(root: Path, output: Path) -> dict:
    base = root / "data/external/sldc_fy2024_25"
    qa = json.loads((base / "qa_report.json").read_text(encoding="utf-8"))
    daily = pd.read_csv(base / "daily_balance.csv")
    station = pd.read_csv(base / "hydro_station_daily.csv")
    interfaces = pd.read_csv(base / "import_interface_daily.csv")
    reservoirs = pd.read_csv(base / "reservoir_daily.csv")
    if len(daily) != 365 or int((daily.status == "observed").sum()) != qa["observed_days"]:
        raise ValueError("Daily evidence coverage does not match source QA")
    if sorted(daily.loc[daily.status != "observed", "date"].tolist()) != qa["missing_dates"]:
        raise ValueError("Expected 11 missing dates; do not fill observational plots")
    for source in (station, interfaces, reservoirs):
        if not source.classification.eq("official_observed_reference").all():
            raise ValueError("Source classifications have changed")
    if int(station.shape[0]) != qa["normalized_row_counts"]["hydro_station"]:
        raise ValueError("Station extraction does not match QA")
    output.mkdir(parents=True, exist_ok=True)
    paths = []

    # Use per-observed-day means to avoid bias from months with missing reports.
    daily["month"] = daily.date.str[:7]
    monthly = daily.loc[daily.status == "observed"].groupby("month").agg(
        hydro_mu_day=("hydro_mu", "mean"),
        imports_mu_day=("net_import_mu", "mean"),
        consumption_mu_day=("consumption_mu", "mean"),
        observed_days=("date", "size"),
    )
    fig, ax = plt.subplots(figsize=(11, 4.7))
    for name, key in (
        ("Consumption", "consumption_mu_day"),
        ("Net imports", "imports_mu_day"),
        ("Hydro", "hydro_mu_day"),
    ):
        ax.plot(monthly.index, monthly[key], marker="o", label=name)
    ax.set_ylabel("MU / observed day")
    ax.set_title("Kerala SLDC FY2024–25: observed daily system energy")
    ax.tick_params(axis="x", rotation=55)
    ax.grid(alpha=0.2)
    ax.legend()
    fig.tight_layout()
    fig.savefig(output / "observed_daily_balance.png", dpi=180)
    plt.close(fig)
    paths.append("observed_daily_balance.png")

    # Explicit named plants only; exclude SLDC group/IPP subtotals to avoid duplication.
    selected = station[station.station_name_as_reported.isin(STATIONS)].copy()
    selected["month"] = selected.date.str[:7]
    plant = selected.pivot_table(
        index="month", columns="station_name_as_reported", values="generation_mu", aggfunc="sum"
    ).reindex(monthly.index)
    fig, ax = plt.subplots(figsize=(11, 4.7))
    for name in STATIONS:
        if name in plant:
            ax.plot(plant.index, plant[name], marker="o", label=name)
    ax.set_ylabel("MU / observed reporting dates")
    ax.set_title("Selected named hydro stations: reported monthly generation")
    ax.tick_params(axis="x", rotation=55)
    ax.grid(alpha=0.2)
    ax.legend()
    fig.tight_layout()
    fig.savefig(output / "observed_hydro_stations.png", dpi=180)
    plt.close(fig)
    paths.append("observed_hydro_stations.png")

    selected = interfaces[interfaces.interface_name_as_reported.isin(INTERFACES)].copy()
    selected["month"] = selected.date.str[:7]
    inter = selected.pivot_table(
        index="month", columns="interface_name_as_reported", values="import_mu", aggfunc="sum"
    ).reindex(monthly.index)
    fig, ax = plt.subplots(figsize=(11, 4.7))
    for name in INTERFACES:
        if name in inter:
            ax.plot(inter.index, inter[name], marker="o", label=name)
    ax.set_ylabel("MU / observed reporting dates")
    ax.set_title("Selected grouped import interfaces: reported monthly energy (not MW capacity)")
    ax.tick_params(axis="x", rotation=55)
    ax.grid(alpha=0.2)
    ax.legend()
    fig.tight_layout()
    fig.savefig(output / "observed_import_interfaces.png", dpi=180)
    plt.close(fig)
    paths.append("observed_import_interfaces.png")

    idukki = reservoirs.loc[reservoirs.reservoir_name_as_reported == "IDUKKI"].copy()
    idukki = idukki.sort_values("date")
    fig, ax = plt.subplots(figsize=(11, 4.7))
    ax.plot(pd.to_datetime(idukki.date), idukki.storage_percent)
    ax.set_ylabel("Reported storage (%)")
    ax.set_title("Idukki: SLDC reported reservoir storage (not dispatchable energy)")
    ax.grid(alpha=0.2)
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(output / "observed_idukki_storage.png", dpi=180)
    plt.close(fig)
    paths.append("observed_idukki_storage.png")

    summary = {
        "classification": "derived_from_measured_daily_not_hourly",
        "source_url": "https://sldckerala.com/index.php?id=1",
        "source_archive_sha256": qa["source_archive_sha256"],
        "observed_days": qa["observed_days"],
        "missing_dates": qa["missing_dates"],
        "figure_paths": paths,
        "monthly_coverage": monthly.observed_days.to_dict(),
        "limitations": [
            "No unobserved dates have been inserted into the plots.",
            "Monthly source totals omit missing days; first figure uses observed-day means.",
            "Grouped import-interface energy is not a transmission rating.",
            "Reservoir storage percentage is not a hydro plant state of charge.",
            "Named station figures exclude group-total rows and do not represent all hydro.",
        ],
    }
    (output / "evidence_manifest.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--output", type=Path, default=Path("results/figures/sldc_observed_fy2024_25"))
    args = parser.parse_args()
    summary = build_figures(args.root, args.output)
    print(json.dumps({"figures": summary["figure_paths"], "output": str(args.output)}, indent=2))


if __name__ == "__main__":
    main()
