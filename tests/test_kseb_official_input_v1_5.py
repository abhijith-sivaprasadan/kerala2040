import json
from pathlib import Path

import pandas as pd

import kerala2040.kseb_official_input_v1_5 as module
from kerala2040.kseb_monthly_bundle_v1_5 import EXPECTED_MONTHS


def _records_for_month(month: str):
    start = pd.Timestamp(f"{month}-01")
    end = start + pd.offsets.MonthEnd(0)
    records = []
    for day in pd.date_range(start, end, freq="D"):
        value = 600.0 + (day - pd.Timestamp("2024-04-01")).days * 0.1
        records.append(
            {
                "date": day.strftime("%Y-%m-%d"),
                "reservoir": "IDUKKI",
                "source_month": month,
                "source_file": f"{month}.xlsx",
                "source_sha256": f"sha-{month}",
                "source_sheet": day.strftime("%d.%m.%y"),
                "metrics": {
                    "live_storage_mcm": value,
                    "inflow_mcm": 1.0,
                    "average_inflow_cumecs": 10.0,
                },
            }
        )
    return records


def test_365_day_gate_and_anchor_reconciliation(tmp_path: Path, monkeypatch):
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    for month in EXPECTED_MONTHS:
        (bundle / f"{month}.xlsx").write_bytes(b"placeholder")

    all_records = {
        month: _records_for_month(month) for month in EXPECTED_MONTHS
    }

    def fake_parse(path: Path, *, source_month: str):
        return {
            "source_file": path.name,
            "source_sha256": f"sha-{source_month}",
            "record_count": len(all_records[source_month]),
            "ignored_sheets": [],
            "records": all_records[source_month],
        }

    monkeypatch.setattr(module, "parse_workbook", fake_parse)

    evidence_dir = (
        tmp_path / "data" / "evidence" / "hydro"
    )
    evidence_dir.mkdir(parents=True)
    dates = {}
    frame = pd.DataFrame(
        [
            {
                "date": record["date"],
                **record["metrics"],
            }
            for records in all_records.values()
            for record in records
        ]
    ).set_index(pd.to_datetime(
        [
            record["date"]
            for records in all_records.values()
            for record in records
        ]
    ))
    for day in [
        "2024-04-01",
        "2024-04-02",
        "2024-04-09",
        "2024-04-11",
        "2024-05-04",
        "2024-11-30",
    ]:
        dates[day] = {
            "live_storage_mcm": float(frame.loc[pd.Timestamp(day), "live_storage_mcm"]),
            "inflow_cumecs": 10.0,
        }
    (evidence_dir / "idukki_v1_5_official_daily_gap_anchors_2026_09_26.json").write_text(
        json.dumps({"dates": dates}),
        encoding="utf-8",
    )

    result = module.build_model_input(tmp_path, bundle)
    assert result["physical_run_ready"] is True
    assert result["required_calendar_days"] == 365
    assert result["required_dispatch_days"] == 364
    assert result["extracted_unique_days"] == 365
    assert len(result["dispatch_inflow_mcm_day"]) == 364
    assert result["anchor_reconciliation"]["all_anchors_passed"] is True


def test_missing_day_blocks_gate(tmp_path: Path, monkeypatch):
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    for month in EXPECTED_MONTHS:
        (bundle / f"{month}.xlsx").write_bytes(b"placeholder")

    def fake_parse(path: Path, *, source_month: str):
        records = _records_for_month(source_month)
        if source_month == "2024-04":
            records = records[1:]
        return {
            "source_file": path.name,
            "source_sha256": f"sha-{source_month}",
            "record_count": len(records),
            "ignored_sheets": [],
            "records": records,
        }

    monkeypatch.setattr(module, "parse_workbook", fake_parse)
    extracted = module.extract_official_series(bundle)
    assert extracted["complete_365_day_storage_and_inflow"] is False
    assert "2024-04-01" in extracted["missing_dates"]
