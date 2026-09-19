"""Guard proxy-vs-observed boundaries even without a local solver installation."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from kerala2040.chronological_screen import (
    ScreeningAssumptions,
    align_solar_profile,
    build_hourly_screening_network,
    dispatch_summary,
    prepare_inputs,
    solve_hourly_screening,
)

ROOT = Path(__file__).resolve().parents[1]


def inputs():
    qa = json.loads((ROOT / "data/external/sldc_fy2024_25/qa_report.json").read_text())
    proxy = json.loads((ROOT / "public/hourly-load-proxy.json").read_text())
    daily = pd.read_csv(ROOT / "data/external/sldc_fy2024_25/daily_balance.csv")
    return proxy, daily, qa


def test_prepare_preserves_measured_days_and_model_only_missing_dates():
    proxy, daily, qa = inputs()
    hours, meta = prepare_inputs(proxy, daily, expected_missing_dates=qa["missing_dates"])
    assert len(hours) == 8760
    assert meta["observed_days"] == 354 and meta["imputed_days"] == 11
    assert hours.daily_energy_imputed.sum() == 11 * 24
    assert hours.generation_daily_imputed.sum() == 11 * 24
    assert abs(meta["observed_days_energy_mu"]["consumption_mu"] - 30666.2569) < 1e-4
    first = hours.iloc[:24]
    assert abs(first.hydro_fixed_mw.sum() / 1000 - 19.479) < 1e-6
    assert abs(first.load_mw.sum() / 1000 - 104.8262) < 1e-6
    assert not first.daily_energy_imputed.any()
    assert pd.isna(hours.loc[hours.date == "2024-08-12", "observed_import_mu"]).all()


def test_proxy_and_daily_edits_are_rejected():
    proxy, daily, qa = inputs()
    proxy["classification"] = "measured"
    with pytest.raises(ValueError, match="not-measured"):
        prepare_inputs(proxy, daily, expected_missing_dates=qa["missing_dates"])
    proxy, daily, qa = inputs()
    daily.loc[daily.date == "2024-08-12", "consumption_mu"] = 90.0
    with pytest.raises(ValueError, match="remain null"):
        prepare_inputs(proxy, daily, expected_missing_dates=qa["missing_dates"])
    proxy, daily, qa = inputs()
    proxy["records"][0]["load_mw"] += 25
    with pytest.raises(ValueError, match="conserve measured"):
        prepare_inputs(proxy, daily, expected_missing_dates=qa["missing_dates"])


def test_solar_resource_refuses_missing_hours_and_mislabel():
    snaps = pd.date_range("2024-04-01", periods=2, freq="h")
    df = pd.DataFrame({
        "timestamp_ist": ["2024-04-01T00:00:00+05:30"],
        "solar_p_max_pu": [0.3], "classification": ["modelled_resource_profile"],
    })
    with pytest.raises(ValueError, match="missing hours"):
        align_solar_profile(df, snaps)
    df.loc[1] = ["2024-04-01T01:00:00+05:30", 0.4, "measured"]
    with pytest.raises(ValueError, match="modelled resource"):
        align_solar_profile(df, snaps)


def test_screening_assumptions_fail_closed():
    with pytest.raises(ValueError, match="positive"):
        ScreeningAssumptions(import_limit_mw=0).validate()
    with pytest.raises(ValueError, match="penalty"):
        ScreeningAssumptions(import_limit_mw=6500, objective_unserved_per_mwh=0.5).validate()
    with pytest.raises(ValueError, match="Invalid battery"):
        ScreeningAssumptions(import_limit_mw=6500, battery_round_trip_efficiency=1.5).validate()


def test_highs_short_window_solution_and_daily_energy_replay():
    pytest.importorskip("pypsa")
    pytest.importorskip("highspy")
    proxy, daily, qa = inputs()
    hours, meta = prepare_inputs(proxy, daily, expected_missing_dates=qa["missing_dates"])
    hours = hours.iloc[:48].copy()
    settings = ScreeningAssumptions(import_limit_mw=6500)
    network = build_hourly_screening_network(
        hours, meta, settings, installed_hydro_mw=2284.42,
        installed_nonhydro_mw=4412.14 - 2284.42,
    )
    status, condition = solve_hourly_screening(network)
    summary = dispatch_summary(network, hours, status, condition)
    assert summary["measured_hourly_telemetry_used"] is False
    assert summary["cost_optimal_2040_result"] is False
    assert summary["unserved_mwh_modelled"] < 1e-6
    assert summary["max_abs_hourly_balance_residual_mw"] < 1e-3
    imports = network.generators_t.p.screened_import.to_numpy().reshape(2, 24).sum(axis=1) / 1000
    assert np.allclose(imports, [83.3343, 83.4503], atol=1e-4)


def test_additional_solar_requires_explicit_modelled_profile():
    pytest.importorskip("pypsa")
    proxy, daily, qa = inputs()
    hours, meta = prepare_inputs(proxy, daily, expected_missing_dates=qa["missing_dates"])
    with pytest.raises(ValueError, match="requires"):
        build_hourly_screening_network(
            hours.iloc[:24], meta, ScreeningAssumptions(import_limit_mw=6500, additional_solar_mw=100),
            installed_hydro_mw=2284.42, installed_nonhydro_mw=2127.72,
        )
