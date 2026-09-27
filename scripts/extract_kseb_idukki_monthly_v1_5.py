"""Extract and gate the official FY2024-25 KSEB Idukki monthly series."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from kerala2040.kseb_official_input_v1_5 import build_model_input


def _serializable(result: dict) -> dict:
    out = {key: value for key, value in result.items() if key not in {"frame", "dispatch_inflow_mcm_day"}}
    series = result.get("dispatch_inflow_mcm_day")
    if series is not None:
        out["dispatch_inflow_mcm_day"] = {
            index.strftime("%Y-%m-%d"): float(value)
            for index, value in series.items()
        }
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--bundle-dir", type=Path, required=True)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()

    result = build_model_input(args.root, args.bundle_dir)
    rendered = json.dumps(_serializable(result), indent=2, sort_keys=True) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    if not result["physical_run_ready"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
