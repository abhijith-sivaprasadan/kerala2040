import pytest

from kerala2040.kseb_idukki_water_balance_v1_5 import water_balance_qa


def rec(day, storage, inflow=None, outflow=None, inflow_c=None, outflow_c=None):
    metrics = {"live_storage_mcm": storage}
    if inflow is not None:
        metrics["inflow_mcm"] = inflow
        metrics["total_outflow_mcm"] = outflow
    if inflow_c is not None:
        metrics["inflow_cumecs"] = inflow_c
        metrics["total_outflow_cumecs"] = outflow_c
    return {"date": day, "metrics": metrics}


def test_direct_mcm_report_date_balance():
    records = [
        rec("2026-07-01", 100.0, 1.0, 1.0),
        rec("2026-07-02", 101.8, 3.0, 1.0),
        rec("2026-07-03", 103.6, 3.0, 1.0),
        rec("2026-07-04", 105.4, 3.0, 1.0),
    ]
    result = water_balance_qa(records)
    assert result["residual_summary"]["median_mcm"] == pytest.approx(-0.2)
    assert result["representation_counts"]["direct_mcm"] == 3


def test_cumecs_conversion():
    # 10 cumecs net = 0.864 MCM/day.
    records = [
        rec("2020-11-01", 100.0, inflow_c=20.0, outflow_c=10.0),
        rec("2020-11-02", 100.7, inflow_c=20.0, outflow_c=10.0),
        rec("2020-11-03", 101.4, inflow_c=20.0, outflow_c=10.0),
        rec("2020-11-04", 102.1, inflow_c=20.0, outflow_c=10.0),
    ]
    result = water_balance_qa(records)
    assert result["residual_summary"]["median_mcm"] == pytest.approx(-0.164)
    assert result["representation_counts"]["cumecs_daily_volume_assumption"] == 3


def test_large_source_typo_is_flagged_not_corrected():
    records = [
        rec("2026-07-01", 100.0, 3.0, 1.0),
        rec("2026-07-02", 101.8, 3.0, 1.0),
        rec("2026-07-03", 103.6, 3.0, 1.0),
        rec("2026-07-04", 105.4, 3.0, 1994.0),
        rec("2026-07-05", 107.2, 3.0, 1.0),
    ]
    result = water_balance_qa(records)
    assert result["source_anomaly_count"] == 1
    assert result["source_anomaly_candidates"][0]["date"] == "2026-07-04"
    assert result["automatic_source_corrections_applied"] is False
    assert result["ready_for_model_input"] is False
