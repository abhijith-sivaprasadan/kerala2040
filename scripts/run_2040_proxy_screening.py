"""Run an illustrative 2040-demand PyPSA screen on a 2024-25 shape year.

No source record or live website data is changed by this script.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import yaml

from kerala2040.chronological_screen import (
    ScreeningAssumptions,
    build_hourly_screening_network,
    dispatch_summary,
    prepare_inputs,
    solve_hourly_screening,
)
from kerala2040.planning_2040 import demand_references, scale_reference_load


def make_figures(hourly: pd.DataFrame, network, output: Path, benchmark: str) -> None:
    output.mkdir(parents=True, exist_ok=True)
    p = network.generators_t.p
    first = hourly.head(min(72, len(hourly)))
    x = pd.DatetimeIndex(first.snapshot_ist_naive)
    fig, ax = plt.subplots(figsize=(11, 4.6))
    ax.plot(x, first.load_mw, label="2040 reference demand on reconstructed shape")
    ax.plot(x, p.screened_import.iloc[: len(first)], label="Modelled imports")
    ax.plot(x, p.fixed_daily_hydro.iloc[: len(first)], label="Frozen FY2024-25 hydro")
    if "added_solar_sensitivity" in p:
        ax.plot(x, p.added_solar_sensitivity.iloc[: len(first)], label="Additional solar")
    if "unserved_load" in p:
        ax.plot(x, p.unserved_load.iloc[: len(first)], label="Unserved demand")
    ax.set_ylabel("MW")
    ax.set_title(f"2040 {benchmark} screening | NOT forecast hourly demand")
    ax.legend(loc="upper right", fontsize=8)
    ax.grid(alpha=0.2)
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(output / "2040_proxy_dispatch.png", dpi=180)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.plot(
        sorted(hourly.load_mw, reverse=True),
        label="Published annual demand scaled to proxy shape",
    )
    ax.plot(
        sorted(hourly.historical_load_proxy_mw, reverse=True),
        label="FY2024-25 reconstructed shape (original)",
    )
    ax.set_xlabel("Hours in solved window, ranked by load")
    ax.set_ylabel("MW")
    ax.set_title("Demand-duration sensitivity | not measured hourly load")
    ax.legend(fontsize=8)
    ax.grid(alpha=0.2)
    fig.tight_layout()
    fig.savefig(output / "2040_proxy_load_duration.png", dpi=180)
    plt.close(fig)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--acknowledge-proxy", action="store_true")
    parser.add_argument("--hours", type=int, default=48)
    parser.add_argument(
        "--benchmark",
        choices=("cstep_2024_bau", "cn50_2026_bau", "cn50_2026_transition"),
        default="cstep_2024_bau",
    )
    parser.add_argument(
        "--assumptions", type=Path,
        default=Path("configs/pypsa_screening_example.yaml"),
    )
    parser.add_argument(
        "--solar-profile", type=Path,
        default=Path("data/processed/renewable_availability_proxy.parquet"),
    )
    parser.add_argument(
        "--output", type=Path, default=Path("results/models/2040_proxy_screening"),
    )
    args = parser.parse_args()
    if not args.acknowledge_proxy:
        parser.error("Pass --acknowledge-proxy: the 2040 load is NOT measured hourly")
    if not 24 <= args.hours <= 8760 or args.hours % 24:
        parser.error("--hours must be a multiple of 24 from 24 to 8760")
    root = Path(".")
    proxy = json.loads((root / "public/hourly-load-proxy.json").read_text())
    qa = json.loads(
        (root / "data/external/sldc_fy2024_25/qa_report.json").read_text()
    )
    daily = pd.read_csv(root / "data/external/sldc_fy2024_25/daily_balance.csv")
    observed = json.loads((root / "public/observed-reference.json").read_text())
    references = yaml.safe_load(
        (root / "configs/published_2040_references.yaml").read_text()
    )
    cstep = pd.read_csv(
        root / "data/external/cstep_2024/demand_projection_fy2023_fy2040.csv"
    )
    cases = demand_references(cstep, references)
    historical, source_meta = prepare_inputs(
        proxy, daily, expected_missing_dates=qa["missing_dates"]
    )
    if source_meta["observed_days"] != qa["observed_days"]:
        raise ValueError("SLDC QA observations disagree")
    hourly, meta = scale_reference_load(historical, source_meta, cases[args.benchmark])
    meta["source_archive_sha256"] = qa["source_archive_sha256"]
    meta["benchmark_id"] = args.benchmark
    meta["window_hours"] = args.hours
    meta["full_annual_demand_only_if_hours_8760"] = True
    meta["note"] = (
        "Frozen 2024-25 daily source energy and illustrative 2040 demand. "
        "No cost-optimal expansion, hourly validation, or verified transfer capacity."
    )
    settings = yaml.safe_load(args.assumptions.read_text())
    if settings.get("classification") != "scenario_assumption_not_kerala_capacity_or_cost":
        raise ValueError("Refusing unlabelled PyPSA screening assumptions")
    assumptions = ScreeningAssumptions(
        **{key: settings[key] for key in ScreeningAssumptions.__dataclass_fields__}
    )
    hourly = hourly.iloc[: args.hours].copy()
    solar = (
        pd.read_parquet(args.solar_profile) if assumptions.additional_solar_mw else None
    )
    hydro_mw = float(observed["electricity"]["capacity_mix_mw"]["hydel"])
    nonhydro_mw = float(observed["electricity"]["installed_capacity_mw"]) - hydro_mw
    network = build_hourly_screening_network(
        hourly, meta, assumptions, installed_hydro_mw=hydro_mw,
        installed_nonhydro_mw=nonhydro_mw, solar=solar,
    )
    status, condition = solve_hourly_screening(network)
    summary = dispatch_summary(network, hourly, status, condition)
    summary["scenario_classification"] = (
        "published_2040_demand_on_proxy_2024_25_weather_and_generation"
    )
    summary["fully_validated_2040_model"] = False
    summary["inr_costs_computed"] = False
    summary["whole_year_solved"] = args.hours == 8760
    p = network.generators_t.p
    dispatch = pd.DataFrame({
        "timestamp_ist_shape_year": pd.DatetimeIndex(
            hourly.snapshot_ist_naive
        ).strftime("%Y-%m-%dT%H:%M:%S+05:30"),
        "classification": "2040_scenario_proxy_not_measured_or_hourly_forecast",
        "historical_daily_imputed": hourly.daily_energy_imputed.to_numpy(),
        "2040_demand_proxy_mw": hourly.load_mw.to_numpy(),
        "2024_25_load_shape_proxy_mw": hourly.historical_load_proxy_mw.to_numpy(),
        "frozen_2024_25_hydro_mw": p.fixed_daily_hydro.to_numpy(),
        "frozen_2024_25_nonhydro_mw": p.fixed_daily_nonhydro.to_numpy(),
        "screened_import_mw": p.screened_import.to_numpy(),
        "unserved_mw": p.unserved_load.to_numpy(),
    })
    if "added_solar_sensitivity" in p:
        dispatch["added_solar_mw"] = p.added_solar_sensitivity.to_numpy()
    if "added_bess_sensitivity" in network.storage_units.index:
        dispatch["bess_net_discharge_mw"] = network.storage_units_t.p[
            "added_bess_sensitivity"
        ].to_numpy()
    args.output.mkdir(parents=True, exist_ok=True)
    dispatch.to_csv(args.output / "dispatch.csv", index=False)
    (args.output / "summary.json").write_text(
        json.dumps(summary, indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )
    pd.DataFrame.from_dict(cases, orient="index").rename_axis("benchmark").to_csv(
        args.output / "published_2040_demand_references.csv"
    )
    make_figures(hourly, network, args.output / "figures", args.benchmark)
    print(json.dumps({
        "status": status, "condition": condition, "benchmark": args.benchmark,
        "hours": args.hours, "full_year_reference_mwh": meta["full_year_2040_reference_mwh"],
        "solved_window_load_mwh": summary["load_mwh_proxy"],
        "unserved_mwh": summary["unserved_mwh_modelled"],
        "output": str(args.output),
        "validated_hourly_or_cost_optimal": False,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
