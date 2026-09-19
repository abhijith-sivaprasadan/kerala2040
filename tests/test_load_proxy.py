import numpy as np
import pandas as pd
import pytest

from kerala2040.load_proxy import (
    build_hourly_proxy,
    complete_daily_energy,
    duration_counts,
    fit_proxy_shape,
)


def _daily_frame() -> pd.DataFrame:
    dates = pd.date_range("2024-04-01", "2025-03-31", freq="D")
    return pd.DataFrame({"date": dates, "consumption_mu": np.full(len(dates), 86.4)})


def test_complete_daily_energy_flags_and_interpolates_gap() -> None:
    daily = _daily_frame().drop(index=10).reset_index(drop=True)
    completed = complete_daily_energy(daily)
    assert len(completed) == 365
    assert completed["daily_energy_imputed"].sum() == 1
    missing = completed.loc[completed["daily_energy_imputed"]].iloc[0]
    assert missing["date"] == pd.Timestamp("2024-04-11")
    assert missing["consumption_mu"] == 86.4


@pytest.mark.parametrize("index", [0, 364])
def test_proxy_rejects_unbounded_missing_days(index: int) -> None:
    with pytest.raises(ValueError, match="leading/trailing gaps"):
        complete_daily_energy(_daily_frame().drop(index=index))


@pytest.mark.parametrize("value", [np.inf, -1, 0])
def test_proxy_rejects_invalid_observations(value: float) -> None:
    daily = _daily_frame()
    daily.loc[10, "consumption_mu"] = value
    with pytest.raises(ValueError, match="finite and positive"):
        complete_daily_energy(daily)


def test_hourly_proxy_conserves_each_days_energy() -> None:
    daily = complete_daily_energy(_daily_frame())
    hourly = build_hourly_proxy(
        daily,
        afternoon_amplitude=0.2,
        night_amplitude=0.3,
    )
    assert len(hourly) == 8760
    recovered = (
        hourly.assign(date=hourly["timestamp"].dt.tz_localize(None).dt.normalize())
        .groupby("date")["load_mw"]
        .sum()
        / 1000.0
    )
    assert np.allclose(recovered.to_numpy(), daily["consumption_mu"].to_numpy())
    assert set(hourly["classification"]) == {"proxy_reconstruction"}


def test_fit_proxy_shape_returns_valid_candidate() -> None:
    daily = complete_daily_energy(_daily_frame())
    bins = [
        {"min_mw": 2000, "max_mw": 3000, "hours": 100},
        {"min_mw": 3000, "max_mw": 4000, "hours": 8000},
        {"min_mw": 4000, "max_mw": 5000, "hours": 660},
    ]
    fit = fit_proxy_shape(daily, bins=bins, target_peak_mw=4500)
    hourly = build_hourly_proxy(
        daily,
        afternoon_amplitude=fit.afternoon_amplitude,
        night_amplitude=fit.night_amplitude,
    )
    assert fit.objective >= 0
    assert len(fit.duration_counts) == len(bins)
    assert duration_counts(hourly["load_mw"], bins) == fit.duration_counts
    assert np.isfinite(hourly["load_mw"]).all()
