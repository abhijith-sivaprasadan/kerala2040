"""Aggregate parallel PyPSA-OSeMOSYS v1.3 common-frontier case results."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from kerala2040.pypsa_osemosys_common_frontier import COMMON_CLASS


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    paths = sorted(args.input_dir.glob("*.json"))
    if len(paths) != 12:
        raise SystemExit(f"Expected 12 case JSON files, found {len(paths)}")

    docs = [json.loads(path.read_text(encoding="utf-8")) for path in paths]
    for doc in docs:
        if doc.get("classification") != COMMON_CLASS:
            raise SystemExit("Unexpected common-frontier classification")
        if doc.get("cases_compared") != 1 or len(doc.get("cases", [])) != 1:
            raise SystemExit("Each parallel artifact must contain exactly one case")

    cases = [doc["cases"][0] for doc in docs]
    case_ids = [row["case_id"] for row in cases]
    if len(set(case_ids)) != 12:
        raise SystemExit("Parallel common-frontier artifacts contain duplicate cases")

    maxima: dict[str, float] = {}
    for row in cases:
        for key, value in row["comparison"][
            "differences_osemosys_minus_pypsa"
        ].items():
            maxima[key] = max(maxima.get(key, 0.0), abs(float(value)))

    first = docs[0]
    result = {
        "classification": COMMON_CLASS,
        "prepared_date": first["prepared_date"],
        "hours": first["hours"],
        "days": first["days"],
        "cases_compared": len(cases),
        "all_cases_pass": all(
            row["comparison"]["status"] == "PASS" for row in cases
        ),
        "maximum_absolute_differences": maxima,
        "acceptance": first["acceptance"],
        "source_qa": first["source_qa"],
        "common_contract": first["common_contract"],
        "newer_evidence_not_admitted": first["newer_evidence_not_admitted"],
        "interpretation": first["interpretation"],
        "parallel_case_artifacts": [path.name for path in paths],
        "cases": sorted(cases, key=lambda row: row["case_id"]),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "cases_compared": result["cases_compared"],
                "all_cases_pass": result["all_cases_pass"],
                "maximum_absolute_differences": maxima,
            },
            indent=2,
        )
    )
    if not result["all_cases_pass"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
