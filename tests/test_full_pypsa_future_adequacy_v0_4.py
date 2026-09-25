"""Tests for the v0.4 future-demand adequacy counterfactual."""
from pathlib import Path

import pandas as pd
import pytest

from kerala2040.full_pypsa_future_adequacy import (
    load_future_adequacy_suite,
    morph_load_to_energy_and_peak,
    run_future_adequacy_suite,
)

ROOT = Path(__file__).resolve().parents[1]


def test_future_suite_keeps_capacity_planning_fail_closed():
    suite = load_future_adequacy_suite(
        ROOT / "configs/full_pypsa_future_adequacy_v0_4.yaml"
    )
    assert suite["release"]["research_counterfactual_screen"] is True
    assert suite["release"]["economic_dispatch"] is False
    assert suite["release"]["capacity_expansion"] is False
    assert suite["release"]["scenario_recommendation"] is False


def test_affine_morph_hits_energy_and_peak_exactly():
    base = pd.Series([3000.0] * 8759 + [6000.0])
    transformed, meta = morph_load_to_energy_and_peak(
        base,
        annual_energy_mu=35000.0,
        peak_mw=7000.0,
    )
    assert transformed.sum() / 1000 == pytest.approx(35000.0, abs=1e-6)
    assert transformed.max() == pytest.approx(7000.0, abs=1e-6)
    assert meta["scale"] > 0
    assert transformed.min() > 0


def test_48h_future_suite_solves_without_promoting_forecast_claims():
    pytest.importorskip("pypsa")
    pytest.importorskip("highspy")
    result = run_future_adequacy_suite(ROOT, hours=48)
    assert result["future_hourly_demand_measured"] is False
    assert result["future_generation_forecast"] is False
    assert result["economic_dispatch"] is False
    assert result["capacity_expansion"] is False
    assert len(result["cases"]) == 15
    assert all(case["solver_status"] == "ok" for case in result["cases"])
