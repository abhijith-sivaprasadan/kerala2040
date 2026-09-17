from pathlib import Path

from kerala2040.config import load_yaml


def test_baseline_config_loads() -> None:
    config = load_yaml(Path("configs/baseline.yaml"))
    assert config["project"]["target_year"] == 2040
    assert config["baseline"]["snapshots"] == 8760
    assert config["model"]["solver"] == "highs"
