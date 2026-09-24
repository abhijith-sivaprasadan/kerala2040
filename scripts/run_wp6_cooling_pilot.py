"""Generate source-labelled WP6 single-zone cooling/TES pilot output.

uv run python scripts/run_wp6_cooling_pilot.py --output /tmp/wp6-pilot.json
With no --output, write reproducible JSON to stdout.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from kerala2040.flexibility_cooling import build_pilot


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()
    result = json.dumps(build_pilot(), indent=2, allow_nan=False) + "\n"
    if args.output is None:
        print(result, end="")
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(result, encoding="utf-8")
        print(f"Wrote source-labelled illustrative pilot: {args.output}")


if __name__ == "__main__":
    main()
