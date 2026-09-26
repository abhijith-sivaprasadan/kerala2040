"""Tests for Idukki source-reported inflow gate and solver v1.4."""
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from kerala2040.full_pypsa_idukki_inflow_release_v1_4 import (
    assess_private_inflow_gate,
    load_idukki_inflow_v14_suite,
    sha256,
    solve_idukki_reported_inflow_case,
    validate_private_inflow_rows,
)

ROOT = Path(__file__).resolve().parents[1]


def test_v14_public_source_gate_is_fail_closed():
    suite = load_idukki_inflow_v14_suite(
        ROOT / "configs/full_pypsa_idukki_inflow_release_v1_4.yaml"
    )
    gate = assess_private_inflow_gate(None, suite)
    assert gate["status"] == "blocked_private_source_missing"
    assert gate["physical_run_ready"] is False
    assert gate["required_pilot_inflow_days"] == 364
    assert suite["release"]["source_reported_inflow_model_run_ready"] is False
    assert suite["release"]["observed_spill_chronology_ready"] is False


def _write_private_fixture(path: Path, missing_second_day: bool = False) -> None:
    values = [1.0, np.nan if missing_second_day else 2.0]
    pd.DataFrame(
        {
            "date": ["2025-01-01", "2025-01-02"],
            "reservoir": ["IDUKKI", "IDUKKI"],
            "effective_storage_mcm": [5.0, 5.2],
            "inflow_mcm_day": values,
            "source_sha256": ["a", "b"],
        }
    ).to_csv(path, index=False)


def test_private_inflow_validator_requires_complete_source_days(tmp_path):
    source = tmp_path / "reservoir_rows.csv"
    _write_private_fixture(source)
    digest = sha256(source)
    checked = validate_private_inflow_rows(
        source,
        expected_sha256=digest,
        start="2025-01-01",
        dispatch_end="2025-01-02",
        required_columns=[
            "date",
            "reservoir",
            "effective_storage_mcm",
            "inflow_mcm_day",
            "source_sha256",
        ],
    )
    assert checked["complete_for_physical_run"] is True
    assert checked["pilot_days_source_reported_valid"] == 2

    _write_private_fixture(source, missing_second_day=True)
    digest = sha256(source)
    blocked = validate_private_inflow_rows(
        source,
        expected_sha256=digest,
        start="2025-01-01",
        dispatch_end="2025-01-02",
        required_columns=[
            "date",
            "reservoir",
            "effective_storage_mcm",
            "inflow_mcm_day",
            "source_sha256",
        ],
    )
    assert blocked["complete_for_physical_run"] is False
    assert blocked["missing_or_invalid_pilot_dates"] == ["2025-01-02"]


def test_private_inflow_validator_rejects_wrong_hash(tmp_path):
    source = tmp_path / "reservoir_rows.csv"
    _write_private_fixture(source)
    with pytest.raises(ValueError, match="SHA-256"):
        validate_private_inflow_rows(
            source,
            expected_sha256="0" * 64,
            start="2025-01-01",
            dispatch_end="2025-01-02",
            required_columns=["date", "reservoir", "inflow_mcm_day"],
        )


def test_v14_synthetic_reported_inflow_solver_closes_storage():
    pytest.importorskip("pypsa")
    pytest.importorskip("highspy")

    snapshots = pd.date_range("2025-01-01", periods=48, freq="h")
    daily = pd.to_datetime(["2025-01-01", "2025-01-02"])
    result = solve_idukki_reported_inflow_case(
        residual_after_nonhydro_mw=np.full(48, 20.0),
        snapshots=snapshots,
        other_hydro_daily_mwh=pd.Series(
            [0.0, 0.0],
            index=["2025-01-01", "2025-01-02"],
        ),
        other_hydro_power_mw=10.0,
        idukki_power_mw=20.0,
        idukki_full_storage_mcm=10.0,
        idukki_initial_storage_mcm=5.0,
        idukki_terminal_storage_mcm=5.0,
        idukki_energy_equivalent_mwh_per_mcm=100.0,
        reported_inflow_mcm_day=pd.Series([2.0, 2.0], index=daily),
        solar_profile=np.zeros(48),
        wind_profile=np.zeros(48),
        import_limit_mw=20.0,
        import_price_real_inr_per_mwh=4500.0,
        caps={
            "ground_solar_headroom_mw": 0.0,
            "floating_solar_headroom_mw": 0.0,
            "solar_total_headroom_mw": 0.0,
            "wind_headroom_mw": 0.0,
            "bess_power_headroom_mw": 0.0,
        },
        annualized_costs={
            "solar_million_inr_per_mw_year": 4.0,
            "wind_million_inr_per_mw_year": 6.0,
            "bess_million_inr_per_mw_year": 8.0,
        },
        bess_duration_h=4.0,
        charge_efficiency=0.94,
        discharge_efficiency=0.94,
        unserved_tolerance_mwh=1e-6,
    )
    assert result["idukki_storage_terminal_mcm"] == pytest.approx(5.0, abs=1e-5)
    assert result["idukki_storage_min_mcm"] >= -1e-6
    assert result["idukki_storage_max_mcm"] <= 10.0 + 1e-6
    assert result["idukki_generation_peak_mw"] <= 20.0 + 1e-6
    assert np.isfinite(result["idukki_non_turbine_release_mcm"])
    assert result["idukki_non_turbine_release_mcm"] >= -1e-9
    assert result["solver"]["stage3"] == ["ok", "optimal"]
