"""Build self-contained WP6 synthetic EV/industry datasets without outside sources."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from kerala2040.flexibility_dispatch import build_demonstration


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--kind", choices=("ev", "industry", "both"), default="both")
    p.add_argument("--out-dir", type=Path, default=Path("outputs/wp6"))
    args = p.parse_args()
    args.out_dir.mkdir(exist_ok=True, parents=True)
    for kind in (("ev", "industry") if args.kind == "both" else (args.kind,)):
        path = args.out_dir / f"wp6-{kind}.json"
        path.write_text(
            json.dumps(build_demonstration(kind), indent=2, allow_nan=False) + "\n",
            encoding="utf-8",
        )
        print(f"Illustrative {kind} output: {path}")


if __name__ == "__main__":
    main()
