"""Tests for Full-PyPSA interday hydro flexibility v1.2."""
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from kerala2040.full_pypsa_hydro_flex_v1_1 import solve_hydro_flex_case
from kerala2040.full_pypsa_hydro_interday_v1_2 import (
    load_hydro_interday_v12_suite,
    solve_hydro_interday_case,
)

ROOT = Path(__file__).resolve().parents[1]


def _common_inputs(hours: int) -> dict:
    snapshots = pd.date_range("2025-01-01", periods=hours, freq="h")
    days = hours // 24
    return {
        "residual_after_nonhydro_mw": np.full(hours, 100.0),
        "snapshots": snapshots,
        "daily_hydro_mwh": pd.Series(
            [1200.0] * days,
            index=[
                (pd.Timestamp("2025-01-01") + pd.Timedelta(days=i)).strftime(
                    "%Y-%m-%d"
                )
                for i in range(days)
            ],
        ),
        "solar_profile": np.tile(
            np.r_[np.zeros(6), np.ones(12), np.zeros(6)],
            days,
        ),
        "wind_profile": np.full(hours, 0.4),
        "installed_hydro_mw": 100.0,
        "import_limit_mw": 80.0,
        "import_price_real_inr_per_mwh": 4500.0,
        "caps": {
            "ground_solar_headroom_mw": 200.0,
            "floating_solar_headroom_mw": 100.0,
            "solar_total_headroom_mw": 300.0,
            "wind_headroom_mw": 200.0,
            "bess_power_headroom_mw": 50.0,
        },
        "annualized_costs": {
            "solar_million_inr_per_mw_year": 4.0,
            "wind_million_inr_per_mw_year": 6.0,
            "bess_million_inr_per_mw_year": 8.0,
        },
        "bess_duration_h": 4.0,
        "charge_efficiency": 0.94,
        "discharge_efficiency": 0.94,
        "unserved_tolerance_mwh": 1e-6,
    }


def test_v12_release_is_fail_closed():
    suite = load_hydro_interday_v12_suite(
        ROOT / "configs/full_pypsa_hydro_interday_v1_2.yaml"
    )
    assert suite["release"]["interday_hydro_flexibility_bracket_ready"] is True
    assert suite["release"]["reservoir_model_ready"] is False
    assert suite["release"]["water_balance_model_ready"] is False
    assert suite["release"]["validated_capacity_plan"] is False


def test_v12_one_day_matches_v11_daily_constraint():
    pytest.importorskip("pypsa")
    pytest.importorskip("highspy")
    common = _common_inputs(48)

    v11 = solve_hydro_flex_case(
        **common,
        hydro_available_fraction=0.7,
    )
    v12 = solve_hydro_interday_case(
        **common,
        window_days=1,
        available_hydro_mw=70.0,
    )
    assert v12["stage2_unserved_mwh"] == pytest.approx(
        v11["stage2_unserved_mwh"],
        abs=1e-5,
    )
    assert v12["hydro_generation_mwh"] == pytest.approx(
        v11["hydro_generation_mwh"],
        abs=1e-5,
    )
    assert v12["built"]["solar_combined_mw"] == pytest.approx(
        v11["built"]["solar_combined_mw"],
        abs=1e-5,
    )
    assert v12["max_window_hydro_energy_residual_mwh"] < 1e-4


def test_v12_three_day_window_conserves_energy_and_power():
    pytest.importorskip("pypsa")
    pytest.importorskip("highspy")
    common = _common_inputs(72)
    result = solve_hydro_interday_case(
        **common,
        window_days=3,
        available_hydro_mw=70.0,
    )
    assert result["window_count"] == 1
    assert result["hydro_generation_mwh"] == pytest.approx(3600.0, abs=1e-4)
    assert result["annual_hydro_energy_residual_mwh"] == pytest.approx(
        0.0,
        abs=1e-4,
    )
    assert result["max_window_hydro_energy_residual_mwh"] < 1e-4
    assert result["hydro_peak_mw"] <= 70.0 + 1e-6
