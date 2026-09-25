"""Recover verified ERA5 artifacts and build Full-PyPSA v0.6 screening profiles."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from kerala2040.era5_renewable_profiles import (
    build_era5_screening_profiles,
    load_profile_suite,
    recover_full_year_weather,
)

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("artifact_root", type=Path)
    parser.add_argument(
        "--config",
        type=Path,
        default=ROOT / "configs/full_pypsa_era5_renewable_profiles_v0_6.yaml",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=ROOT / "results/models/full_pypsa/era5_renewables_v0_6",
    )
    args = parser.parse_args()

    suite = load_profile_suite(args.config)
    weather, weather_summary = recover_full_year_weather(args.artifact_root)
    point_profiles, statewide, profile_summary = build_era5_screening_profiles(weather, suite)

    args.out_dir.mkdir(parents=True, exist_ok=True)
    weather.to_parquet(args.out_dir / "weather_points.parquet", index=False)
    point_profiles.to_parquet(args.out_dir / "point_profiles.parquet", index=False)
    statewide.to_parquet(args.out_dir / "statewide_equal_weight_profile.parquet", index=False)
    summary = {
        "weather": weather_summary,
        "profiles": profile_summary,
    }
    (args.out_dir / "summary.json").write_text(
        json.dumps(summary, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
