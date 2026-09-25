"""Tests for the v0.4 SLDC-reported hydro peak envelope."""
from pathlib import Path

import pandas as pd
import pytest

from kerala2040.full_pypsa_hydro_reported_peak import (
    derive_reported_station_peak_envelope,
    load_reported_peak_envelope_config,
    run_reported_peak_envelope,
)

ROOT = Path(__file__).resolve().parents[1]


def test_reported_peak_config_never_claims_simultaneous_capability():
    config = load_reported_peak_envelope_config(
        ROOT / "configs/full_pypsa_hydro_reported_peak_v0_4.yaml"
    )
    release = config["release"]
    assert release["research_reported_peak_envelope_ready"] is True
    assert release["measured_simultaneous_hydro_capability"] is False
    assert release["validated_hydro_dispatch_ready"] is False
    assert release["capacity_expansion_ready"] is False


def test_station_peak_envelope_matches_admitted_sldc_coverage():
    station = pd.read_csv(
        ROOT / "data/external/sldc_fy2024_25/hydro_station_daily.csv"
    )
    qa = pd.read_json(
        ROOT / "data/external/sldc_fy2024_25/qa_report.json",
        typ="series",
    )
    full_dates = pd.date_range("2024-04-01", "2025-03-31", freq="D")
    envelope, summary = derive_reported_station_peak_envelope(
        station,
        full_dates,
        expected_missing_dates=list(qa["missing_dates"]),
    )
    assert summary["station_rows"] == 5779
    assert summary["station_names"] == 17
    assert summary["observed_days"] == 354
    assert summary["interpolated_missing_days"] == 11
    assert summary["reported_peak_rows_fraction"] == pytest.approx(
        0.9027513411,
        abs=1e-9,
    )
    assert summary["reported_peak_energy_fraction_median"] == pytest.approx(
        0.9943691822,
        abs=1e-9,
    )
    assert summary["observed_envelope_mw_median"] == pytest.approx(
        1616.85,
        abs=1e-6,
    )
    assert envelope["reported_peak_envelope_mw"].notna().all()


def test_48h_three_way_unserved_energy_bracket_is_monotonic():
    pytest.importorskip("pypsa")
    pytest.importorskip("highspy")
    result = run_reported_peak_envelope(ROOT, hours=48)
    flat = {case["id"]: case for case in result["flat_daily_average"]}
    middle = {
        case["id"]: case for case in result["reported_station_peak_envelope"]
    }
    upper = {
        case["id"]: case
        for case in result["installed_capacity_redispatch_upper_bound"]
    }
    for case_id in flat:
        assert upper[case_id]["unserved_energy_mwh"] <= (
            middle[case_id]["unserved_energy_mwh"] + 1e-5
        )
        assert middle[case_id]["unserved_energy_mwh"] <= (
            flat[case_id]["unserved_energy_mwh"] + 1e-5
        )
        assert middle[case_id]["max_daily_hydro_energy_residual_mwh"] < 1e-3
    assert result["release"]["validated_hydro_dispatch"] is False
