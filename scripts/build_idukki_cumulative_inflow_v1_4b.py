"""Build private v1.4b Idukki cumulative-inflow sensitivity scenarios."""
from __future__ import annotations

import argparse
from pathlib import Path

from kerala2040.idukki_cumulative_inflow_v1_4b import (
    build_source_informed_inflow_scenarios,
    load_v14b_suite,
    write_public_qa,
)

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--private-reservoir-rows", type=Path, required=True)
    parser.add_argument("--private-output-dir", type=Path, required=True)
    parser.add_argument("--public-qa", type=Path)
    args = parser.parse_args()

    suite = load_v14b_suite(
        ROOT / "configs/full_pypsa_idukki_cumulative_inflow_v1_4b.yaml"
    )
    result = build_source_informed_inflow_scenarios(
        args.private_reservoir_rows,
        suite,
        private_output_dir=args.private_output_dir,
    )
    if args.public_qa:
        write_public_qa(result, args.public_qa)

    print("classification:", result["classification"])
    print("pilot:", result["pilot"])
    print("blank convention:", result["archive_blank_convention"])
    print("unresolved bracket:", result["unresolved_date_bracket"])
    for scenario_id, values in result["scenarios"].items():
        print(scenario_id, values)


if __name__ == "__main__":
    main()
