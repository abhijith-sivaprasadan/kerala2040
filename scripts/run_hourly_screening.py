"""Solve explicitly labelled hourly PyPSA screening from FY2024-25 SLDC evidence.

Default is a 48-hour smoke test. Full 8760-hour solves are opt-in. The historical
354-day observed PyPSA replay remains scripts/build_historical_model.py.
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


def _make_figures(hourly: pd.DataFrame, network, output: Path) -> None:
    output.mkdir(parents=True, exist_ok=True)
    p = network.generators_t.p
    plot = hourly.head(min(72, len(hourly)))
    n = len(plot)
    x = pd.DatetimeIndex(plot.snapshot_ist_naive)
    fig, ax = plt.subplots(figsize=(11, 4.5))
    ax.plot(x, plot.load_mw, label="Reconstructed load (not measured)", linewidth=1.6)
    ax.plot(x, p.screened_import.iloc[:n], label="Screened import (modelled)", linewidth=1.3)
    ax.plot(x, p.fixed_daily_hydro.iloc[:n], label="Hydro (observed daily average)", linewidth=1.2)
    if "added_solar_sensitivity" in p:
        ax.plot(x, p.added_solar_sensitivity.iloc[:n], label="Added PV (modelled)")
    ax.set_ylabel("MW")
    ax.set_title("Kerala 2040 | illustrative hourly PyPSA screening, FY2024–25")
    ax.legend(loc="upper right", fontsize=8)
    ax.grid(alpha=0.2)
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(output / "screening_dispatch.png", dpi=180)
    plt.close(fig)

    energy = {
        "Hydro (daily-average replay)": float(p.fixed_daily_hydro.sum()),
        "Other internal (daily-average replay)": float(p.fixed_daily_nonhydro.sum()),
        "Screened imports": float(p.screened_import.sum()),
        "Unserved (modelled)": float(p.unserved_load.sum()),
    }
    if "added_solar_sensitivity" in p:
        energy["Added PV (modelled)"] = float(p.added_solar_sensitivity.sum())
    fig, ax = plt.subplots(figsize=(9, 4))
    ax.barh(list(energy), [v / 1000 for v in energy.values()])
    ax.set_xlabel("GWh within modelled window")
    ax.set_title("Source-energy accounting — proxy-based sensitivity, not observed hourly")
    fig.tight_layout()
    fig.savefig(output / "screening_energy.png", dpi=180)
    plt.close(fig)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--acknowledge-proxy", action="store_true", help="Required: reconstructed hours are NOT telemetry")
    parser.add_argument("--hours", type=int, default=48, help="Consecutive hours from FY start; 8760 for full year")
    parser.add_argument("--proxy", type=Path, default=Path("public/hourly-load-proxy.json"))
    parser.add_argument("--daily", type=Path, default=Path("data/external/sldc_fy2024_25/daily_balance.csv"))
    parser.add_argument("--qa", type=Path, default=Path("data/external/sldc_fy2024_25/qa_report.json"))
    parser.add_argument("--observed", type=Path, default=Path("public/observed-reference.json"))
    parser.add_argument("--assumptions", type=Path, default=Path("configs/pypsa_screening_example.yaml"))
    parser.add_argument("--solar-profile", type=Path, default=Path("data/processed/renewable_availability_proxy.parquet"))
    parser.add_argument("--output", type=Path, default=Path("results/models/hourly_proxy_screening"))
    parser.add_argument("--export-network", action="store_true", help="Export netCDF; may be large at 8760 hours")
    args = parser.parse_args()
    if not args.acknowledge_proxy:
        parser.error("Pass --acknowledge-proxy; this is NOT measured hourly Kerala telemetry")
    if not 1 <= args.hours <= 8760 or args.hours % 24:
        parser.error("--hours must be a whole number of days, between 24 and 8760")
    proxy = json.loads(args.proxy.read_text(encoding="utf-8"))
    qa = json.loads(args.qa.read_text(encoding="utf-8"))
    observed = json.loads(args.observed.read_text(encoding="utf-8"))
    settings = yaml.safe_load(args.assumptions.read_text(encoding="utf-8"))
    if settings.get("classification") != "scenario_assumption_not_kerala_capacity_or_cost":
        raise ValueError("Refusing missing or mislabeled screening assumptions")
    assumptions = ScreeningAssumptions(**{
        key: settings[key] for key in ScreeningAssumptions.__dataclass_fields__
    })
    hourly, metadata = prepare_inputs(
        proxy, pd.read_csv(args.daily), expected_missing_dates=qa["missing_dates"]
    )
    if qa["observed_days"] != metadata["observed_days"]:
        raise ValueError("Observed-day count differs from QA report")
    if abs(qa["observed_days_totals_mu"]["consumption_mu"] -
           metadata["observed_days_energy_mu"]["consumption_mu"]) > 0.001:
        raise ValueError("QA totals disagree with model observations")
    metadata["source_archive_sha256"] = qa["source_archive_sha256"]
    metadata["input_qa"] = "verified 354-day SLDC daily accounting; no hourly calibration"
    metadata["modeled_window_hours"] = args.hours
    if args.hours != 8760:
        metadata["window_note"] = "Short chronological sensitivity, NOT annual system totals"
    hourly = hourly.iloc[:args.hours].copy()
    solar = pd.read_parquet(args.solar_profile) if assumptions.additional_solar_mw else None
    capacities = observed["electricity"]["capacity_mix_mw"]
    network = build_hourly_screening_network(
        hourly, metadata, assumptions,
        installed_hydro_mw=float(capacities["hydel"]),
        installed_nonhydro_mw=float(observed["electricity"]["installed_capacity_mw"] - capacities["hydel"]),
        solar=solar,
    )
    status, condition = solve_hourly_screening(network)
    summary = dispatch_summary(network, hourly, status, condition)
    p = network.generators_t.p
    dispatch = pd.DataFrame({
        "timestamp_ist": pd.DatetimeIndex(hourly.snapshot_ist_naive).strftime("%Y-%m-%dT%H:%M:%S+05:30"),
        "classification": "scenario_screening_using_proxy_not_measured_hourly_dispatch",
        "daily_energy_imputed": hourly.daily_energy_imputed.to_numpy(),
        "generation_daily_imputed": hourly.generation_daily_imputed.to_numpy(),
        "load_proxy_mw": hourly.load_mw.to_numpy(),
        "hydro_daily_average_mw": p.fixed_daily_hydro.to_numpy(),
        "nonhydro_daily_average_mw": p.fixed_daily_nonhydro.to_numpy(),
        "screened_import_mw": p.screened_import.to_numpy(),
        "unserved_mw": p.unserved_load.to_numpy(),
    })
    if "added_solar_sensitivity" in p:
        dispatch["added_solar_mw"] = p.added_solar_sensitivity.to_numpy()
    if "added_bess_sensitivity" in network.storage_units.index:
        dispatch["bess_net_discharge_mw"] = network.storage_units_t.p[
            "added_bess_sensitivity"
        ].to_numpy()
    if not assumptions.additional_solar_mw and not assumptions.battery_power_mw:
        # No *independent* hourly accuracy claim. This checks only conservation
        # of the measured daily source energy through the reconstructed hours.
        observed_import = dispatch.assign(date=hourly.date.to_numpy()).groupby("date").screened_import_mw.sum() / 1000
        reference = hourly.groupby("date").observed_import_mu.first().dropna()
        deviation = (observed_import.loc[reference.index] - reference).abs()
        summary["observed_daily_import_replay_max_residual_mu"] = float(deviation.max())
        if deviation.max() > 0.001 or summary["unserved_mwh_modelled"] > 1e-5:
            raise RuntimeError("No-additions baseline fails daily energy replay; inspect assumed import bound")
    args.output.mkdir(parents=True, exist_ok=True)
    dispatch.to_csv(args.output / "dispatch_screening.csv", index=False)
    (args.output / "summary.json").write_text(
        json.dumps(summary, indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )
    _make_figures(hourly, network, args.output / "figures")
    if args.export_network:
        network.export_to_netcdf(args.output / "hourly_screening.nc")
    print(json.dumps({
        "status": status, "condition": condition, "hours": args.hours,
        "hourly_telemetry": "NOT measured", "output": str(args.output),
        "unserved_mwh": summary["unserved_mwh_modelled"],
        "max_balance_residual_mw": summary["max_abs_hourly_balance_residual_mw"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
