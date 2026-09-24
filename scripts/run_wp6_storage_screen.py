"""Publish a reproducible synthetic BESS/PSP comparison (not Kerala capacity)."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from kerala2040.flexibility_storage import build_screen


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output", type=Path, default=Path("outputs/wp6/wp6-storage.json"))
    args = p.parse_args()
    result = build_screen()
    args.output.parent.mkdir(exist_ok=True, parents=True)
    args.output.write_text(
        json.dumps(result, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    print(f"Synthetic WP6 BESS/PSP screen: {args.output}")


if __name__ == "__main__":
    main()
