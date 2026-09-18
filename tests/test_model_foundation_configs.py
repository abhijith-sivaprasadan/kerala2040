from pathlib import Path

import yaml


def _load(path: str):
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))


def test_scenario_framework_has_no_numeric_capacity_answers():
    config = _load("configs/scenario_dimensions.yaml")
    assert config["classification"] == "scenario_assumption"
    assert config["source"] == "Kerala 2040 research design"
    for scenario in config["scenarios"].values():
        for value in scenario.values():
            assert not isinstance(value, (int, float))


def test_final_techno_economic_grid_is_unresolved():
    config = _load("configs/techno_economics.yaml")
    assert config["classification"] == "external_study_result"
    for source in config["sources"].values():
        assert source["publisher"]
        assert source["url"]
        assert source["evidence"]
    grid = config["model_input_grid"]["technologies"]

    assert grid["solar_pv"]["capex_inr_per_kw"][2025] is None
    assert grid["wind_onshore"]["capex_inr_per_kw"][2040] is None
    assert grid["bess"]["capex_energy_inr_per_kwh"][2030] is None
    assert config["system_finance"]["discount_rate_pct"] is None


def test_gis_manifest_does_not_claim_catalogue_as_model_ready():
    config = _load("configs/gis_inputs.yaml")
    assert config["classification"] == "catalogue_only"
    for layer in config["layers"].values():
        assert "source" in layer
        assert "role" in layer
        assert layer["acquisition_status"] != "model_ready"
