"""Tests for explicit 2040 reference energy and provenance boundaries."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import yaml

from kerala2040.chronological_screen import (
    ScreeningAssumptions,
    build_hourly_screening_network,
    dispatch_summary,
    prepare_inputs,
    solve_hourly_screening,
)
from kerala2040.planning_2040 import demand_references, scale_reference_load

ROOT = Path(__file__).resolve().parents[1]


def inputs():
    cstep = pd.read_csv(
        ROOT / "data/external/cstep_2024/demand_projection_fy2023_fy2040.csv"
    )
    refs = yaml.safe_load(
        (ROOT / "configs/published_2040_references.yaml").read_text()
    )
    cases = demand_references(cstep, refs)
    proxy = json.loads((ROOT / "public/hourly-load-proxy.json").read_text())
    qa = json.loads(
        (ROOT / "data/external/sldc_fy2024_25/qa_report.json").read_text()
    )
    daily = pd.read_csv(ROOT / "data/external/sldc_fy2024_25/daily_balance.csv")
    historical, meta = prepare_inputs(
        proxy, daily, expected_missing_dates=qa["missing_dates"]
    )
    return historical, meta, cases


def test_published_demands_are_distinct_and_reconciled():
    _, _, cases = inputs()
    assert cases["cstep_2024_bau"]["target_mu"] == 45519
    assert cases["cn50_2026_bau"]["target_mu"] == 65980
    assert cases["cn50_2026_transition"]["target_mu"] == 88560
    assert all(c["classification"] == "published_external_scenario" for c in cases.values())
    assert all("different" in c["scope_warning"] for c in cases.values())


def test_2040_annual_energy_preserves_original_proxy_and_missing_days():
    historical, meta, cases = inputs()
    source = historical.load_mw.copy()
    scaled, provenance = scale_reference_load(
        historical, meta, cases["cstep_2024_bau"]
    )
    assert len(scaled) == 8760
    assert np.allclose(source, historical.load_mw)
    assert np.isclose(scaled.load_mw.sum(), 45_519_000, rtol=0, atol=1e-5)
    assert scaled.daily_energy_imputed.sum() == 11 * 24
    assert provenance["measured_hourly_telemetry_used"] is False
    assert provenance["cost_optimal_2040_result"] is False
    assert provenance["shape_year"].startswith("FY2024-25")
    assert provenance["classification"].startswith("scenario_screening_using_proxy")
    assert provenance["historical_shape_energy_mwh_proxy"] > 30_666_256.9


def test_unlabelled_demand_and_partial_year_fail_closed():
    historical, meta, cases = inputs()
    with pytest.raises(ValueError, match="8760"):
        scale_reference_load(historical.iloc[:48], meta, cases["cstep_2024_bau"])
    case = {**cases["cstep_2024_bau"], "classification": "measured"}
    with pytest.raises(ValueError, match="published"):
        scale_reference_load(historical, meta, case)
    bad_meta = {**meta, "load_classification": "measured"}
    with pytest.raises(ValueError, match="reconstructed"):
        scale_reference_load(historical, bad_meta, cases["cstep_2024_bau"])


def test_pypsa_solves_2040_reference_screen_without_claiming_validated_forecast():
    pytest.importorskip("pypsa")
    pytest.importorskip("highspy")
    historical, meta, cases = inputs()
    scaled, provenance = scale_reference_load(
        historical, meta, cases["cstep_2024_bau"]
    )
    sample = scaled.iloc[:48].copy()
    settings = ScreeningAssumptions(import_limit_mw=6500)
    net = build_hourly_screening_network(
        sample, provenance, settings, installed_hydro_mw=2284.42,
        installed_nonhydro_mw=4412.14 - 2284.42,
    )
    status, condition = solve_hourly_screening(net)
    summary = dispatch_summary(net, sample, status, condition)
    assert status == "ok" and condition == "optimal"
    assert summary["cost_optimal_2040_result"] is False
    assert summary["measured_hourly_telemetry_used"] is False
    assert summary["max_abs_hourly_balance_residual_mw"] < 1e-3
    assert summary["load_mwh_proxy"] > historical.load_mw.iloc[:48].sum()
    assert summary["full_year_2040_reference_mwh"] == 45_519_000
