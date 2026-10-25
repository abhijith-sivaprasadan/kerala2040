"""Reconcile the frozen monthly daily-demand ML observations without fitting models.

This is arithmetic checking of a previously published experiment, NOT an
independent rerun, a forecast, a significance test or new causal evidence.
"""

from __future__ import annotations

import math
import statistics


def _close(actual: float, expected: float, what: str) -> None:
    if not math.isfinite(actual) or not math.isfinite(expected):
        raise ValueError(f"Nonfinite {what}")
    if not math.isclose(actual, expected, abs_tol=1e-7, rel_tol=1e-10):
        raise ValueError(f"Reconciliation failed for {what}")


def audit_frozen_ml_record(record: dict) -> dict:
    if record.get("classification") != "experimental_daily_observed_demand_ml_robustness_v0_2":
        raise ValueError("Unexpected evidence type")
    target = record["target"]
    if (
        target.get("reconstructed_hourly_proxy_used_as_target") is not False
        or target.get("source_observed_rows") != 354
        or target.get("matched_observed_rows") != 353
    ):
        raise ValueError("Target provenance or completeness mismatch")
    design = record["rolling_design"]
    folds = design["folds"]
    rows = record["fold_weather_rmse_reduction_pct"]
    if len(folds) != 7 or len(rows) != 7 or [r["fold"] for r in rows] != folds:
        raise ValueError("Expected the exact seven ordered, unique monthly holdouts")
    if len(set(folds)) != 7:
        raise ValueError("Duplicate fold")

    output = {}
    for model in ("lightgbm", "xgboost"):
        values = [float(row[model]) for row in rows]
        if any(not math.isfinite(v) for v in values):
            raise ValueError("Nonfinite fold reduction")
        summary = record["rolling_summary"][model]
        n_wins = sum(v > 0 for v in values)
        _close(summary["weather_rmse_wins"], n_wins, model + " wins")
        _close(summary["fold_count"], len(values), model + " fold count")
        _close(summary["weather_rmse_win_rate"], n_wins / len(values), model + " win rate")
        for key, derived in (
            ("median_weather_rmse_reduction_pct", statistics.median(values)),
            ("mean_weather_rmse_reduction_pct", statistics.mean(values)),
            ("best_weather_rmse_reduction_pct", max(values)),
            ("worst_weather_rmse_reduction_pct", min(values)),
        ):
            _close(summary[key], derived, model + " " + key)
        baseline = float(summary["pooled_calendar_only"]["rmse_mu"])
        weather = float(summary["pooled_weather"]["rmse_mu"])
        if not 0 < baseline or not 0 < weather:
            raise ValueError("Pooled RMSE must be positive")
        output[model] = {
            "winning_folds": n_wins,
            "n_folds": len(values),
            "pooled_rmse_reduction_pct": 100.0 * (baseline - weather) / baseline,
            "worst_month": folds[values.index(min(values))],
            "worst_month_reduction_pct": min(values),
            "leave_one_fold_out_wins_min": n_wins - (1 if n_wins else 0),
            "leave_one_fold_out_wins_max": min(n_wins, len(values) - 1),
        }

    variants = record["xgboost_feature_group_ablation"]["variants"]
    by_name = {v["variant"]: v for v in variants}
    if len(by_name) != len(variants) or "calendar_only" not in by_name:
        raise ValueError("Ablation variants missing or duplicated")
    base_rmse = float(by_name["calendar_only"]["holdout_rmse_mu"])
    for name, variant in by_name.items():
        rmse = float(variant["holdout_rmse_mu"])
        if base_rmse <= 0 or rmse <= 0:
            raise ValueError("Invalid ablation RMSE")
        _close(
            variant["rmse_reduction_vs_calendar_pct"],
            100.0 * (base_rmse - rmse) / base_rmse,
            name + " ablation reduction",
        )
    return {
        "status": "PASS_FROZEN_RESULT_ARITHMETIC_ONLY",
        "target": "Observed SLDC daily consumption, not reconstructed hourly demand",
        "years_tested": "one financial year only",
        "same_day_reanalysis_not_forecast": True,
        "models": output,
        "scope": (
            "A recheck of committed published monthly statistics; no independent "
            "model rerun, calibrated confidence interval or multi-year generalisation."
        ),
    }
