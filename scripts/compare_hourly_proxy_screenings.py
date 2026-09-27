"""Compare legacy and ERA5-sensitive 8,760-hour PyPSA screening outputs.

This is a chronology comparison, not an hourly validation or a 2040 investment result.
Both runs must use the same daily SLDC energy accounting and screening assumptions.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd


def _load_run(path: Path) -> tuple[dict, pd.DataFrame]:
    summary = json.loads((path / "summary.json").read_text(encoding="utf-8"))
    dispatch = pd.read_csv(path / "dispatch_screening.csv")
    needed = {
        "timestamp_ist",
        "load_proxy_mw",
        "screened_import_mw",
        "unserved_mw",
    }
    missing = needed - set(dispatch)
    if missing:
        raise ValueError(f"{path}: dispatch missing {sorted(missing)}")
    if len(dispatch) != 8760:
        raise ValueError(f"{path}: expected 8760 dispatch rows")
    for col in ("load_proxy_mw", "screened_import_mw", "unserved_mw"):
        dispatch[col] = pd.to_numeric(dispatch[col], errors="coerce")
        if not np.isfinite(dispatch[col]).all():
            raise ValueError(f"{path}: non-finite {col}")
    if summary.get("solver_status") != "ok" or summary.get("solver_condition") != "optimal":
        raise ValueError(f"{path}: PyPSA run was not optimal")
    if float(summary.get("unserved_mwh_modelled", 1.0)) > 1e-5:
        raise ValueError(f"{path}: baseline has modelled unserved energy")
    if float(summary.get("observed_daily_import_replay_max_residual_mu", 1.0)) > 0.001:
        raise ValueError(f"{path}: daily import replay no longer closes")
    return summary, dispatch


def _metrics(summary: dict, dispatch: pd.DataFrame) -> dict:
    load = dispatch["load_proxy_mw"].to_numpy(dtype=float)
    imports = dispatch["screened_import_mw"].to_numpy(dtype=float)
    ramp = np.diff(load)
    return {
        "profile_variant": summary.get("load_profile_variant", "unknown"),
        "hours": len(dispatch),
        "load_energy_gwh": float(load.sum() / 1000.0),
        "load_peak_mw": float(load.max()),
        "load_p95_mw": float(np.quantile(load, 0.95)),
        "load_min_mw": float(load.min()),
        "max_absolute_1h_load_ramp_mw": float(np.max(np.abs(ramp))),
        "hours_load_ge_5000_mw": int(np.sum(load >= 5000.0)),
        "screened_import_energy_gwh": float(imports.sum() / 1000.0),
        "screened_import_peak_mw": float(imports.max()),
        "screened_import_p95_mw": float(np.quantile(imports, 0.95)),
        "unserved_mwh": float(summary["unserved_mwh_modelled"]),
        "max_power_balance_residual_mw": float(
            summary["max_abs_hourly_balance_residual_mw"]
        ),
        "observed_daily_import_replay_max_residual_mu": float(
            summary["observed_daily_import_replay_max_residual_mu"]
        ),
    }


def compare(legacy_dir: Path, weather_dir: Path, out: Path) -> dict:
    legacy_summary, legacy_dispatch = _load_run(legacy_dir)
    weather_summary, weather_dispatch = _load_run(weather_dir)
    if legacy_dispatch["timestamp_ist"].tolist() != weather_dispatch["timestamp_ist"].tolist():
        raise ValueError("Legacy/weather runs do not share identical timestamps")

    legacy = _metrics(legacy_summary, legacy_dispatch)
    weather = _metrics(weather_summary, weather_dispatch)

    if "era5_weather_sensitive" not in str(weather["profile_variant"]):
        raise ValueError("Weather run is not the ERA5-sensitive proxy")
    if weather["profile_variant"] == legacy["profile_variant"]:
        raise ValueError("Comparison accidentally used the same proxy twice")

    # Same daily energy + same daily-average generation replay should preserve
    # annual energy accounting. The chronology, peaks and ramps may differ.
    if abs(weather["load_energy_gwh"] - legacy["load_energy_gwh"]) > 1e-5:
        raise ValueError("Proxy variants no longer conserve the same FY energy")
    if abs(
        weather["screened_import_energy_gwh"] - legacy["screened_import_energy_gwh"]
    ) > 1e-5:
        raise ValueError("Proxy variants changed annual import energy accounting")

    delta_keys = (
        "load_peak_mw",
        "load_p95_mw",
        "load_min_mw",
        "max_absolute_1h_load_ramp_mw",
        "hours_load_ge_5000_mw",
        "screened_import_peak_mw",
        "screened_import_p95_mw",
    )
    result = {
        "classification": (
            "same_energy_chronology_comparison_not_measured_hourly_validation_or_2040_result"
        ),
        "period": "FY2024-25",
        "hours": 8760,
        "legacy": legacy,
        "era5_weather_sensitive": weather,
        "delta_weather_minus_legacy": {
            key: float(weather[key] - legacy[key]) for key in delta_keys
        },
        "invariants": {
            "same_hourly_timestamps": True,
            "same_total_load_energy": True,
            "same_total_screened_import_energy": True,
            "both_optimal": True,
            "both_zero_unserved_with_current_screening_bound": True,
            "both_replay_observed_daily_import_energy_within_0_001_mu": True,
        },
        "interpretation": [
            "Differences quantify how the reconstructed chronology changes peaks, ramps and hourly import stress while daily source energy is held fixed.",
            "Neither chronology is measured state hourly telemetry.",
            "The 6500 MW import bound remains an illustrative screening assumption, not Kerala ATC/TTC.",
            "This comparison does not validate reservoir dispatch or produce a 2040 investment recommendation.",
        ],
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--legacy", type=Path, required=True)
    parser.add_argument("--weather", type=Path, required=True)
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("results/models/hourly_proxy_comparison/summary.json"),
    )
    args = parser.parse_args()
    result = compare(args.legacy, args.weather, args.out)
    print(json.dumps(result, indent=2, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
