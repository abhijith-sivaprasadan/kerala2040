"""Tests for the PyPSA-OSeMOSYS v1.3 common-frontier contract."""
from pathlib import Path

import numpy as np
import pytest

from kerala2040.pypsa_osemosys_common_frontier import (
    COMMON_CLASS,
    _demand_mapping,
    load_common_frontier_suite,
)

ROOT = Path(__file__).resolve().parents[1]


def test_common_frontier_contract_is_guarded():
    suite = load_common_frontier_suite(
        ROOT / "configs/pypsa_osemosys_common_frontier_v1_3c.yaml"
    )
    assert suite["classification"] == COMMON_CLASS
    assert suite["common_contract"]["expected_cases"] == 12
    assert suite["release"]["observed_catchment_inflow_model"] is False
    assert suite["release"]["validated_capacity_plan"] is False
    assert suite["release"]["network_spatial_constraints_internalized"] is False
    assert suite["common_contract"]["network_planning_evidence"] == "configs/network_planning_evidence_v1_0.yaml"


def test_demand_mapping_preserves_negative_residual_as_fixed_source():
    annual, profile, source = _demand_mapping(
        np.array([10.0, -2.0, 20.0, 0.0]),
        ["a", "b", "c", "d"],
    )
    assert annual == pytest.approx(30.0)
    assert sum(profile.values()) == pytest.approx(1.0)
    assert profile["a"] == pytest.approx(1.0 / 3.0)
    assert source.tolist() == pytest.approx([0.0, 2.0, 0.0, 0.0])
