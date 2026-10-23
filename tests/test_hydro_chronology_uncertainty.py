"""The bounded chronology experiment checks model invariants and source selection."""
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from kerala2040.hydro_chronology_uncertainty import (
    SHAPES,
    choose_observed_peak_energy_week,
    perturb_day,
    solve_one_day,
)

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("kind", SHAPES)
def test_perturbations_preserve_daily_mwh(kind):
    load = np.array([4000 + 500*np.sin(2*np.pi*i/24) for i in range(24)])
    shaped = perturb_day(load, kind)
    assert np.sum(shaped) == pytest.approx(np.sum(load), abs=1e-8)
    assert np.all(shaped > 0)


def test_unknown_shape_is_rejected():
    with pytest.raises(ValueError, match="Unsupported"):
        perturb_day(np.ones(24)*100, "data_trained_percentile")


def test_flexible_hydro_helps_at_fixed_daily_energy_under_hourly_peak():
    load = np.full(24, 65.)
    load[18:22] = 160.
    common = {"nonhydro_mw": 10., "daily_hydro_mwh": 480.,
              "hydro_power_mw": 60., "import_ceiling_mw": 60.}
    flat = solve_one_day(load, flexible=False, **common)
    flex = solve_one_day(load, flexible=True, **common)
    assert flat["modelled_unserved_mwh"] > 0
    assert flex["modelled_unserved_mwh"] + 1e-5 < flat["modelled_unserved_mwh"]
    assert flat["hydro_mwh"] == pytest.approx(480, abs=1e-5)
    assert flex["hydro_mwh"] == pytest.approx(480, abs=1e-5)
    assert flex["hydro_peak_mw"] <= 60.00001


def test_infeasible_daily_hydro_is_rejected():
    with pytest.raises(ValueError, match="infeasible"):
        solve_one_day(np.ones(24)*100, nonhydro_mw=20, daily_hydro_mwh=2000,
                      hydro_power_mw=60, import_ceiling_mw=50, flexible=True)


def test_high_consumption_week_selected_from_real_daily_source():
    p = ROOT / "data/external/sldc_fy2024_25/daily_balance.csv"
    days = choose_observed_peak_energy_week(pd.read_csv(p))
    assert days == ["2024-04-28", "2024-04-29", "2024-04-30",
                    "2024-05-01", "2024-05-02", "2024-05-03", "2024-05-04"]


@pytest.mark.parametrize("flexible", [False, True])
@pytest.mark.parametrize("cap", [45., 60., 90.])
def test_lp_matches_independently_derived_daily_shortage_bound(flexible, cap):
    """Two different implementations: constrained LP vs arithmetic lower bound."""
    load = np.full(24, 65.)
    load[18:22] = 160.
    nonhydro, hydro_mwh, hydro_cap = 10., 480., 60.
    deficit = np.maximum(0., load - nonhydro - cap)
    if flexible:
        expected = max(float(deficit.sum()) - hydro_mwh,
                       float(np.maximum(0., deficit - hydro_cap).sum()), 0.)
    else:
        expected = float(np.maximum(0., deficit - hydro_mwh / 24.).sum())
    solved = solve_one_day(load, nonhydro_mw=nonhydro,
                           daily_hydro_mwh=hydro_mwh,
                           hydro_power_mw=hydro_cap,
                           import_ceiling_mw=cap, flexible=flexible)
    assert solved["modelled_unserved_mwh"] == pytest.approx(expected, abs=1e-5)
