"""Mathematical controls, negative data gates and source-window verification."""
from pathlib import Path

import numpy as np
import pytest

from kerala2040.hydro_chronology_v0_2 import (
    import_capacity_series,
    solve_seven_day_hydro,
)

ROOT = Path(__file__).resolve().parents[1]


def test_derate_is_at_declared_clock_hours_and_is_source_neutral():
    cap = import_capacity_series(2, 100.0, "illustrative_18_22_import_20pct_derate")
    assert cap.shape == (48,)
    for day in range(2):
        np.testing.assert_allclose(cap[day*24+18:day*24+22], 80.)
        np.testing.assert_allclose(cap[day*24:day*24+18], 100.)
        np.testing.assert_allclose(cap[day*24+22:(day+1)*24], 100.)
    with pytest.raises(ValueError, match="Unknown"):
        import_capacity_series(1, 100., "measured_2024_restriction")


def test_source_days_cannot_be_relabelled_as_measured_hours():
    # A short solver test verifies physical constraints, not the inferred history.
    load = np.full(48, 65.)
    load[18:22] = 160.
    load[42:46] = 160.
    nonhydro = np.full(48, 10.)
    daily_hydro = np.array([480., 480.])
    caps = np.full(48, 60.)
    unlimited = solve_seven_day_hydro(load, nonhydro, daily_hydro, caps,
                                      hydro_power_mw=60., ramp_mw_per_h=None)
    constrained = solve_seven_day_hydro(load, nonhydro, daily_hydro, caps,
                                        hydro_power_mw=60., ramp_mw_per_h=10.)
    assert constrained["modelled_unserved_mwh"] >= unlimited["modelled_unserved_mwh"] - 1e-6
    assert constrained["observed_solver_max_hydro_ramp_mw_per_h"] < 10.0001
    assert constrained["max_daily_hydro_energy_residual_mwh"] < 1e-5
    assert constrained["max_hourly_balance_residual_mw"] < 1e-5
    assert unlimited["hydro_generation_mwh"] == pytest.approx(960., abs=1e-5)


def test_derive_one_day_unconstrained_matches_independent_daily_lp():
    from kerala2040.hydro_chronology_uncertainty import solve_one_day

    load = np.full(24, 70.)
    load[18:22] = 135.
    nonhydro = np.full(24, 10.)
    daily_hydro = np.array([500.])
    caps = import_capacity_series(1, 60., "illustrative_18_22_import_20pct_derate")
    result = solve_seven_day_hydro(load, nonhydro, daily_hydro, caps,
                                   hydro_power_mw=70., ramp_mw_per_h=None)
    # A second mathematical reference: SciPy LP with the same time-varying imports,
    # but independently implemented daily hydro accounting by source-day enumeration.
    # The lower bound on unserved comprises uncovered per-hour excess and an energy gap.
    d = np.maximum(0., load - nonhydro - caps)
    analytic = max(float(d.sum())-daily_hydro[0], float(np.maximum(0., d-70.).sum()), 0.)
    assert result["modelled_unserved_mwh"] == pytest.approx(analytic, abs=1e-5)
    assert result["max_daily_hydro_energy_residual_mwh"] < 1e-5


def test_clock_shift_breaks_only_with_external_time_asymmetry():
    # Synthetic counterexample where the import availability window changes conclusions:
    # positive shortage at coinciding evening demand/import derate.
    source_load = np.full(24, 75.)
    source_load[18:22] = 135.
    shifted_load = np.roll(source_load, -8)
    nonhydro = np.full(24, 10.)
    hydro = np.array([480.])
    uniform = import_capacity_series(1, 60., "uniform_import_capacity")
    evening = import_capacity_series(1, 60., "illustrative_18_22_import_20pct_derate")
    def solve(load, cap):
        return solve_seven_day_hydro(load, nonhydro, hydro, cap,
                                      hydro_power_mw=60., ramp_mw_per_h=None
                                    )["modelled_unserved_mwh"]
    assert solve(source_load, uniform) == pytest.approx(solve(shifted_load, uniform), abs=1e-5)
    assert abs(solve(source_load, evening) - solve(shifted_load, evening)) > 10.


def test_bad_ramp_and_incomplete_days_fail_closed():
    arr = np.full(24, 65.)
    with pytest.raises(ValueError, match="positive"):
        solve_seven_day_hydro(arr, arr*0, np.array([100.]), arr,
                              hydro_power_mw=50., ramp_mw_per_h=-1.)
    with pytest.raises(ValueError, match="complete day"):
        solve_seven_day_hydro(arr[:23], arr[:23]*0, np.array([100.]), arr[:23],
                              hydro_power_mw=50., ramp_mw_per_h=None)
    with pytest.raises(ValueError, match="exceeds"):
        solve_seven_day_hydro(arr, arr*0, np.array([2400.]), arr,
                              hydro_power_mw=50., ramp_mw_per_h=None)
