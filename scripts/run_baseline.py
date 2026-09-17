#!/usr/bin/env python

from pathlib import Path

from kerala2040.config import load_yaml
from kerala2040.model import solve_smoke_network


def main() -> None:
    config_path = Path("configs/baseline.yaml")
    config = load_yaml(config_path)
    network, status, condition = solve_smoke_network(hours=24)
    print(f"Loaded project: {config['project']['name']}")
    print(f"Smoke solve: status={status}, condition={condition}")
    print(f"Snapshots: {len(network.snapshots)}")
    print("NOTE: this is only an infrastructure smoke test, not a Kerala result.")


if __name__ == "__main__":
    main()
