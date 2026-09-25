"""Run the Full-PyPSA 2030 proxy capacity-expansion counterfactual v0.8."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from kerala2040.full_pypsa_proxy_expansion import run_proxy_expansion_suite

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--profile",
        type=Path,
        default=ROOT
        / "results/models/full_pypsa/era5_renewables_v0_6/statewide_equal_weight_profile.parquet",
    )
    parser.add_argument("--hours", type=int, default=8760)
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "results/models/full_pypsa/proxy_expansion_v0_8/summary.json",
    )
    parser.add_argument(
        "--acknowledge-proxy",
        action="store_true",
        help="Required: confirms this is not a validated least-cost capacity plan.",
    )
    args = parser.parse_args()
    if not args.acknowledge_proxy:
        raise SystemExit("Refusing to run v0.8 without --acknowledge-proxy")

    summary = run_proxy_expansion_suite(
        ROOT,
        profile_path=args.profile,
        hours=args.hours,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
