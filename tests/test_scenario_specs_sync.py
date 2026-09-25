"""Keep the three S0-S5 representations synchronized."""
import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def test_structural_and_public_scenario_specs_agree():
    structural = yaml.safe_load(
        (ROOT / "configs/scenario_dimensions.yaml").read_text(encoding="utf-8")
    )
    descriptive = yaml.safe_load(
        (ROOT / "configs/scenarios_2040.yaml").read_text(encoding="utf-8")
    )
    public = json.loads(
        (ROOT / "public/scenarios.json").read_text(encoding="utf-8")
    )

    assert structural["model_years"] == descriptive["model_years"] == [2030, 2035, 2040]
    expected_ids = list(structural["scenarios"])
    assert expected_ids == list(descriptive["scenarios"])
    assert expected_ids == [row["id"] for row in public["scenarios"]]
    assert [row["code"] for row in public["scenarios"]] == [
        "S0", "S1", "S2", "S3", "S4", "S5"
    ]

    public_by_id = {row["id"]: row for row in public["scenarios"]}
    for scenario_id in expected_ids:
        structural_case = structural["scenarios"][scenario_id]
        descriptive_case = descriptive["scenarios"][scenario_id]
        public_case = public_by_id[scenario_id]
        assert structural_case["ecological_constraint"] == descriptive_case["ecology_constraint"]
        assert structural_case["ecological_constraint"] == public_case["ecology_constraint"]
        assert structural_case["demand_flexibility"] == descriptive_case["demand_flexibility"]
        assert structural_case["demand_flexibility"] == public_case["demand_flexibility"]
        assert public_case["type"] is None


def test_s2_is_legal_minimum_not_spatial_suitability():
    structural = yaml.safe_load(
        (ROOT / "configs/scenario_dimensions.yaml").read_text(encoding="utf-8")
    )
    assert structural["scenarios"]["S2_solar_storage"]["ecological_constraint"] == "legal_minimum"


def test_s5_remains_unsolved_public_specification():
    public = json.loads(
        (ROOT / "public/scenarios.json").read_text(encoding="utf-8")
    )
    s5 = next(row for row in public["scenarios"] if row["code"] == "S5")
    assert s5["name"] == "Fiscal Conservative"
    assert s5["type"] is None
