"""Reproduce the synthetic synchronized WP6 dispatch JSON."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from kerala2040.flexibility_integrated import build_integrated


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("outputs/wp6/wp6-integrated.json"))
    args = parser.parse_args()
    result = build_integrated()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(f"Synthetic synchronized WP6 dispatch: {args.output}")


if __name__ == "__main__":
    main()
