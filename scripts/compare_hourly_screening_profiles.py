"""Compare old fixed-shape and ERA5-sensitive PyPSA baseline dispatch artifacts."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd


def _series_metrics(values: pd.Series) -> dict:
    x = pd.to_numeric(values, errors="raise").to_numpy(dtype=float)
    ramps = np.diff(x)
    return {
        "mean_mw": float(np.mean(x)),
        "p95_mw": float(np.quantile(x, 0.95)),
        "peak_mw": float(np.max(x)),
        "minimum_mw": float(np.min(x)),
        "std_mw": float(np.std(x)),
        "max_abs_1h_ramp_mw": float(np.max(np.abs(ramps))) if len(ramps) else 0.0,
        "p95_abs_1h_ramp_mw": float(np.quantile(np.abs(ramps), 0.95)) if len(ramps) else 0.0,
    }


def _dispatch(path: Path) -> tuple[pd.DataFrame, dict]:
    frame = pd.read_csv(path / "dispatch_screening.csv")
    summary = json.loads((path / "summary.json").read_text(encoding="utf-8"))
    times = pd.to_datetime(frame.timestamp_ist, utc=True).dt.tz_convert("Asia/Kolkata")
    if len(frame) != 8760 or times.duplicated().any():
        raise ValueError(f"{path}: expected unique 8,760-hour chronology")
    frame = frame.assign(hour_local=times.dt.hour)
    return frame, summary


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--old", type=Path, required=True)
    p.add_argument("--era5", type=Path, required=True)
    p.add_argument("--shape-summary", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    a = p.parse_args()

    old, old_summary = _dispatch(a.old)
    era5, era5_summary = _dispatch(a.era5)
    shape = json.loads(a.shape_summary.read_text(encoding="utf-8"))
    if not np.allclose(old.daily_energy_imputed, era5.daily_energy_imputed):
        raise ValueError("Missing-day masks differ between profile runs")
    if abs(old.load_proxy_mw.sum() - era5.load_proxy_mw.sum()) > 1e-4:
        raise ValueError("Annual proxy energies differ")
    if old_summary["unserved_mwh_modelled"] > 1e-5 or era5_summary["unserved_mwh_modelled"] > 1e-5:
        raise ValueError("Baseline comparison has unserved load")

    report = {
        "classification": "PROXY_SHAPE_COMPARISON_NOT_MEASURED_HOURLY_VALIDATION",
        "period": "FY2024-25",
        "hours": 8760,
        "profiles": {
            "old_fixed_two_peak": {
                "load": _series_metrics(old.load_proxy_mw),
                "imports": _series_metrics(old.screened_import_mw),
                "evening_18_23_peak_import_mw": float(
                    old.loc[old.hour_local.between(18, 23), "screened_import_mw"].max()
                ),
                "observed_daily_import_replay_max_residual_mu": old_summary.get(
                    "observed_daily_import_replay_max_residual_mu"
                ),
                "unserved_mwh": old_summary["unserved_mwh_modelled"],
            },
            "era5_sensitive": {
                "load": _series_metrics(era5.load_proxy_mw),
                "imports": _series_metrics(era5.screened_import_mw),
                "evening_18_23_peak_import_mw": float(
                    era5.loc[era5.hour_local.between(18, 23), "screened_import_mw"].max()
                ),
                "observed_daily_import_replay_max_residual_mu": era5_summary.get(
                    "observed_daily_import_replay_max_residual_mu"
                ),
                "unserved_mwh": era5_summary["unserved_mwh_modelled"],
            },
        },
        "selected_intraday_extrema_holdout": shape[
            "validation_against_selected_intraday_consumption_extrema"
        ],
        "cea_duration_bins": {
            "old": shape["cea_duration_bins_old_fixed_profile"],
            "era5_sensitive": shape["cea_duration_bins_era5_sensitive_profile"],
        },
        "peak_reference": {
            "cea_mw": shape["cea_reference_peak_mw"],
            "old_fixed_mw": shape["old_fixed_profile_peak_mw"],
            "era5_sensitive_mw": shape["era5_sensitive_profile_peak_mw"],
        },
        "invariants": {
            "same_annual_proxy_energy": True,
            "same_missing_day_mask": True,
            "354_observed_daily_energy_totals_preserved": True,
            "11_missing_daily_totals_model_only_interpolated": True,
            "measured_hourly_telemetry_used": False,
        },
    }
    old_peak = report["profiles"]["old_fixed_two_peak"]["imports"]["peak_mw"]
    new_peak = report["profiles"]["era5_sensitive"]["imports"]["peak_mw"]
    report["change"] = {
        "peak_import_mw": new_peak - old_peak,
        "peak_import_pct": 100.0 * (new_peak - old_peak) / old_peak,
        "max_abs_import_ramp_mw": (
            report["profiles"]["era5_sensitive"]["imports"]["max_abs_1h_ramp_mw"]
            - report["profiles"]["old_fixed_two_peak"]["imports"]["max_abs_1h_ramp_mw"]
        ),
    }
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "old_peak_import_mw": old_peak,
        "era5_peak_import_mw": new_peak,
        "peak_import_change_pct": report["change"]["peak_import_pct"],
        "holdout_rmse_change_pct": report["selected_intraday_extrema_holdout"][
            "era5_curve_rmse_change_vs_old_pct"
        ],
        "output": str(a.out),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
