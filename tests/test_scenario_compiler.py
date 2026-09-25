"""Tests for the full PyPSA structural scenario compiler."""
from pathlib import Path

import pytest

from kerala2040.scenario_compiler import (
    MODEL_YEARS,
    STRESSES,
    ScenarioRequest,
    compile_matrix,
    compile_scenario,
    load_framework,
)

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def framework():
    return load_framework(ROOT / "configs/scenario_dimensions.yaml")


def test_all_six_scenarios_compile_for_three_model_years(framework):
    compiled = compile_matrix(framework)
    assert len(compiled) == 18
    assert {x.model_year for x in compiled} == set(MODEL_YEARS)
    assert {x.scenario for x in compiled} == set(framework["scenarios"])
    assert all(x.status == "UNSOLVED_SPECIFICATION" for x in compiled)


def test_s5_requires_public_finance_and_integrated_inputs(framework):
    case = compile_scenario(
        framework,
        ScenarioRequest("S5_fiscal_conservative", 2040),
    )
    assert case.levers["fiscal_constraint"] == "explicit_public_cap"
    assert "public_finance" in case.required_inputs
    assert "battery_cost_performance" in case.required_inputs
    assert "processed_ecology_gis" in case.required_inputs
    assert "ev_charging" in case.required_inputs


def test_s0_does_not_invent_fixed_storage_or_ev_requirements(framework):
    case = compile_scenario(framework, ScenarioRequest("S0_business_as_usual", 2030))
    assert "battery_cost_performance" not in case.required_inputs
    assert "pumped_storage_constraints" not in case.required_inputs
    assert "ev_charging" not in case.required_inputs
    assert "interstate_transfer_limit" in case.required_inputs
    assert "reliability_criterion" in case.required_inputs


@pytest.mark.parametrize("stress", STRESSES)
def test_every_stress_adds_a_distinct_blocker(framework, stress):
    base = compile_scenario(framework, ScenarioRequest("S3_integrated_sovereignty", 2040))
    stressed = compile_scenario(
        framework, ScenarioRequest("S3_integrated_sovereignty", 2040, stress=stress)
    )
    assert set(stressed.required_inputs) > set(base.required_inputs)


def test_admission_is_fail_closed_until_every_requirement_exists(framework):
    unresolved = compile_scenario(
        framework, ScenarioRequest("S2_solar_storage", 2040), admitted_inputs=set()
    )
    assert unresolved.blockers
    admitted = set(unresolved.required_inputs)
    ready = compile_scenario(
        framework, ScenarioRequest("S2_solar_storage", 2040), admitted_inputs=admitted
    )
    assert ready.blockers == ()
    assert ready.status == "READY_TO_BUILD_NETWORK"
    assert ready.classification == "scenario_structure_not_optimised_result"


def test_invalid_requests_are_rejected(framework):
    with pytest.raises(ValueError, match="model_year"):
        compile_scenario(framework, ScenarioRequest("S0_business_as_usual", 2037))
    with pytest.raises(ValueError, match="Unknown stress"):
        compile_scenario(
            framework, ScenarioRequest("S0_business_as_usual", 2040, stress="magic")
        )
