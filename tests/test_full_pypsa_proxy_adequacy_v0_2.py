"""Tests for the full-PyPSA v0.2 proxy adequacy selection and runner."""
from pathlib import Path

import pytest
import yaml

from kerala2040.full_pypsa_proxy_adequacy import (
    load_proxy_adequacy_suite,
    load_v02_selection,
    run_proxy_adequacy_suite,
)

ROOT = Path(__file__).resolve().parents[1]


def test_v02_selection_keeps_research_boundaries_fail_closed():
    selection = load_v02_selection(ROOT / "configs/research_input_selection_v0_2.yaml")
    release = selection["release"]
    assert release["chronological_proxy_screen_ready"] is True
    assert release["chronological_validated_dispatch_ready"] is False
    assert release["stochastic_resource_adequacy_ready"] is False
    assert release["capacity_expansion_ready"] is False
    assert selection["selected"]["demand_scenarios"]["higher"]["peak_only"] is True
    assert (
        selection["selected"]["reliability"]["research_benchmark"]["classification"]
        == "published_CEA_state_RA_benchmark_not_Kerala_statutory_threshold"
    )


def test_proxy_suite_limits_are_explicit_atc_sensitivities():
    suite = load_proxy_adequacy_suite(
        ROOT / "configs/full_pypsa_proxy_adequacy_v0_2.yaml"
    )
    assert [case["import_limit_mw"] for case in suite["cases"]] == [
        6500.0,
        4455.0,
        3564.0,
        2673.0,
    ]
    assert suite["release"]["economic_dispatch"] is False
    assert suite["release"]["capacity_expansion"] is False


def test_solar_crosswalk_fails_closed_on_identity_gap():
    import json

    data = json.loads(
        (
            ROOT
            / "data/evidence/assets/kerala_solar_ge1_identity_crosswalk_2026_03_31.json"
        ).read_text(encoding="utf-8")
    )
    assert data["canonical_cea_boundary"]["total_solar_ge_1mw_mw"] == pytest.approx(
        328.815
    )
    assert (
        data["state_solar"]["firm_named_seed_from_ksebl_2021_22"]["sum_mw"]
        == pytest.approx(14.5)
    )
    assert (
        data["state_solar"]["candidate_arithmetic_diagnostic"][
            "canonical_2026_state_bucket_mw"
        ]
        == pytest.approx(22.715)
    )
    assert data["qa"]["state_identity_complete"] is False
    assert data["qa"]["private_identity_complete"] is False
    assert data["qa"]["safe_for_plant_level_dispatch"] is False


def test_48h_proxy_suite_solves_without_promoting_validation():
    pytest.importorskip("pypsa")
    pytest.importorskip("highspy")
    result = run_proxy_adequacy_suite(ROOT, hours=48)
    assert result["hourly_telemetry_measured"] is False
    assert result["economic_dispatch"] is False
    assert result["capacity_expansion"] is False
    assert result["probabilistic_LOLP_evaluated"] is False
    assert result["cases"][0]["id"] == "replay_control"
    assert result["cases"][0]["unserved_energy_mwh"] < 1e-5
    assert result["cases"][0]["observed_daily_import_replay_max_residual_mu"] < 0.001


def test_config_is_parseable_and_no_reliability_claim_is_hidden():
    selection = yaml.safe_load(
        (ROOT / "configs/research_input_selection_v0_2.yaml").read_text(encoding="utf-8")
    )
    reliability = selection["selected"]["reliability"]
    assert reliability["deterministic_proxy_screen"]["counts_as_LOLP_estimate"] is False
    assert reliability["stochastic_resource_adequacy_ready"] is False
