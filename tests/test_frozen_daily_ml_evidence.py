"""Published summaries are tested against frozen month-level evidence."""

import copy
import json
from pathlib import Path

import pytest

from kerala2040.fold_evidence import audit_frozen_ml_record

RECORD = (
    Path(__file__).resolve().parents[1]
    / "data/evidence/daily_demand_ml_robustness_v0_2_2026_10_06.json"
)


def source():
    return json.loads(RECORD.read_text(encoding="utf-8"))


def test_frozen_monthly_results_reconcile():
    report = audit_frozen_ml_record(source())
    assert report["status"] == "PASS_FROZEN_RESULT_ARITHMETIC_ONLY"
    assert report["models"]["xgboost"]["winning_folds"] == 6
    assert report["models"]["lightgbm"]["winning_folds"] == 5
    assert abs(report["models"]["xgboost"]["pooled_rmse_reduction_pct"] - 37.13) < 0.02


def test_tampered_win_count_fails():
    record = copy.deepcopy(source())
    record["rolling_summary"]["xgboost"]["weather_rmse_wins"] = 7
    with pytest.raises(ValueError, match="wins"):
        audit_frozen_ml_record(record)


def test_tampered_fold_fails():
    record = copy.deepcopy(source())
    record["fold_weather_rmse_reduction_pct"][0]["xgboost"] = 100
    with pytest.raises(ValueError, match="Reconciliation failed"):
        audit_frozen_ml_record(record)


def test_missing_month_fails():
    record = copy.deepcopy(source())
    record["fold_weather_rmse_reduction_pct"].pop()
    with pytest.raises(ValueError, match="seven ordered"):
        audit_frozen_ml_record(record)


def test_synthetic_target_cannot_be_promoted():
    record = copy.deepcopy(source())
    record["target"]["reconstructed_hourly_proxy_used_as_target"] = True
    with pytest.raises(ValueError, match="Target provenance"):
        audit_frozen_ml_record(record)
