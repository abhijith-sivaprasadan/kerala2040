"""Tests for source-bounded renewable capacity envelope v0.7."""
from pathlib import Path

from kerala2040.full_pypsa_renewable_capacity import (
    load_capacity_envelope,
    validate_capacity_envelope,
)

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs/full_pypsa_renewable_capacity_v0_7.yaml"


def test_v07_capacity_envelope_validates_sources_and_arithmetic():
    summary = validate_capacity_envelope(ROOT, CONFIG)
    assert summary["source_checks_passed"] is True
    assert summary["statewide_2030_capacity_expansion_sensitivity_ready"] is True
    assert summary["validated_capacity_expansion_ready"] is False
    assert summary["statutory_buildable_capacity_ready"] is False


def test_v07_rooftop_remains_exogenous_without_invented_ceiling():
    data = load_capacity_envelope(CONFIG)
    rooftop = data["technology_envelopes"]["rooftop_pv"]
    assert rooftop["technical_ceiling_mw"] is None
    assert rooftop["endogenous_expansion_admitted"] is False


def test_v07_packaged_cases_are_monotonic():
    data = load_capacity_envelope(CONFIG)
    cases = data["packaged_research_cases"]
    for technology in (
        "ground_utility_pv_total_mw",
        "floating_pv_total_mw",
        "onshore_wind_total_mw",
    ):
        values = [float(cases[name][technology]) for name in ("low", "reference", "high")]
        assert values == sorted(values)
