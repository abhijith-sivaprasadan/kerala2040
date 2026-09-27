"""Run KSEBL public-network chronological screening v1.0."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from kerala2040.kseb_network_chronological_screen import run_screening

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--hours", type=int, default=8760)
    parser.add_argument(
        "--suite",
        type=Path,
        default=ROOT / "configs/kseb_network_chronological_screening_v1_0.yaml",
    )
    parser.add_argument(
        "--network-dir",
        type=Path,
        default=ROOT / "results/network/public_transport_screening_v0_1",
    )
    parser.add_argument(
        "--generators",
        type=Path,
        default=ROOT / "results/network/public_multibus_skeleton_v0_1/model_generators.csv",
    )
    parser.add_argument(
        "--load-manifest",
        type=Path,
        default=ROOT
        / "data/evidence/demand/hourly_load_proxy_era5_weather_sensitive_v2/manifest.json",
    )
    parser.add_argument(
        "--daily",
        type=Path,
        default=ROOT / "data/external/sldc_fy2024_25/daily_balance.csv",
    )
    parser.add_argument(
        "--daily-qa",
        type=Path,
        default=ROOT / "data/external/sldc_fy2024_25/qa_report.json",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=ROOT / "results/network/network_chronological_screening_v1_0",
    )
    parser.add_argument(
        "--acknowledge-screening-only",
        action="store_true",
        help="Required: parameters and hourly spatial dispatch are screening proxies.",
    )
    args = parser.parse_args()
    if not args.acknowledge_screening_only:
        parser.error(
            "Pass --acknowledge-screening-only; this is not a calibrated KSEBL load flow"
        )

    result = run_screening(
        ROOT,
        suite_path=args.suite,
        buses_path=args.network_dir / "screening_buses.csv",
        lines_path=args.network_dir / "screening_lines.csv",
        transformers_path=args.network_dir / "screening_transformer_links.csv",
        generators_path=args.generators,
        spatial_load_path=args.network_dir / "spatial_load_proxy_wide.parquet",
        load_weights_path=args.network_dir / "load_weights.csv",
        load_manifest_path=args.load_manifest,
        daily_path=args.daily,
        daily_qa_path=args.daily_qa,
        out_dir=args.out,
        hours=args.hours,
    )
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
