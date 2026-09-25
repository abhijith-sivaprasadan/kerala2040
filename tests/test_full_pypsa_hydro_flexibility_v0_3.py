"""Tests for the v0.3 intraday hydro-flexibility bracket."""
from pathlib import Path

import pytest

from kerala2040.full_pypsa_hydro_flexibility import (
    load_hydro_flexibility_config,
    run_hydro_flexibility_bracket,
)

ROOT = Path(__file__).resolve().parents[1]


def test_hydro_flexibility_config_is_explicitly_an_upper_bound():
    config = load_hydro_flexibility_config(
        ROOT / "configs/full_pypsa_hydro_flexibility_v0_3.yaml"
    )
    mode = config["hydro_modes"]["daily_energy_redispatch_upper_bound"]
    assert mode["classification"] == "optimistic_intraday_hydro_flexibility_bound"
    assert "reservoir storage state and rule curves" in mode["explicitly_not_modelled"]
    assert config["release"]["validated_hydro_dispatch_ready"] is False
    assert config["release"]["capacity_expansion_ready"] is False


def test_48h_hydro_redispatch_conserves_daily_energy_and_never_worsens_shortage():
    pytest.importorskip("pypsa")
    pytest.importorskip("highspy")
    result = run_hydro_flexibility_bracket(ROOT, hours=48)
    flat = {case["id"]: case for case in result["flat_daily_average"]}
    for flexible in result["daily_energy_redispatch_upper_bound"]:
        assert flexible["max_daily_hydro_energy_residual_mwh"] < 1e-3
        assert flexible["max_abs_hourly_balance_residual_mw"] < 1e-3
        assert flexible["hydro_peak_capacity_fraction"] <= 1 + 1e-9
        assert flexible["unserved_energy_mwh"] <= (
            flat[flexible["id"]]["unserved_energy_mwh"] + 1e-5
        )
    assert result["release"]["validated_hydro_dispatch"] is False
    assert result["release"]["reservoir_model"] is False
