"""Run boundary-interface allocation robustness for KSEBL network bottlenecks."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

import pandas as pd

from kerala2040.kseb_network_chronological_screen import run_screening

ROOT = Path(__file__).resolve().parents[1]
CLASSIFICATION = (
    "KSEBL_NETWORK_BOTTLENECK_ROBUSTNESS_V1_0_"
    "BOUNDARY_ALLOCATION_SENSITIVITY_NOT_OPERATIONAL_VALIDATION"
)


def _as_bool(value: Any) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "y"}


def _slug(value: str) -> str:
    out = re.sub(r"[^A-Za-z0-9]+", "_", value).strip("_").lower()
    return out or "interface"


def _aggregate_lines(
    case_paths: dict[str, Path],
) -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    for case_id, path in case_paths.items():
        frame = pd.read_csv(path / "line_loading_summary.csv")
        frame = frame[frame["primary_congestion_claim_eligible"].map(_as_bool)].copy()
        frame["case_id"] = case_id
        frame["overloaded"] = frame["hours_over_100pct"].astype(float) > 0
        frames.append(frame)
    all_rows = pd.concat(frames, ignore_index=True)
    case_count = len(case_paths)
    records: list[dict[str, Any]] = []
    for line_id, group in all_rows.groupby("line_id", sort=True):
        first = group.iloc[0]
        source_backed = _as_bool(
            first["rating_uses_ksebl_conductor_current_reference"]
        )
        overload_count = int(group["overloaded"].sum())
        if source_backed:
            classification = (
                "ROBUST_SOURCE_BACKED_SCREENING_BOTTLENECK"
                if overload_count == case_count
                else (
                    "INTERFACE_ALLOCATION_SENSITIVE_SOURCE_BACKED"
                    if overload_count > 0
                    else "SOURCE_BACKED_NOT_OVERLOADED_IN_ROBUSTNESS_ENVELOPE"
                )
            )
        else:
            classification = (
                "ROBUST_FALLBACK_RATING_SCREENING_SIGNAL"
                if overload_count == case_count
                else (
                    "FALLBACK_RATING_INTERFACE_SENSITIVE"
                    if overload_count > 0
                    else "FALLBACK_RATING_NOT_OVERLOADED_IN_ROBUSTNESS_ENVELOPE"
                )
            )
        records.append(
            {
                "line_id": line_id,
                "name": first.get("name", ""),
                "feeder_code": first.get("feeder_code", ""),
                "voltage_kv": int(float(first["voltage_kv"])),
                "bus0": first["bus0"],
                "bus1": first["bus1"],
                "screening_s_nom_mva": float(first["screening_s_nom_mva"]),
                "rating_basis": first.get("rating_basis", ""),
                "rating_uses_ksebl_conductor_current_reference": source_backed,
                "case_count": case_count,
                "overload_case_count": overload_count,
                "overloaded_all_cases": overload_count == case_count,
                "overloaded_any_case": overload_count > 0,
                "min_case_max_loading_pu": float(group["max_loading_pu"].min()),
                "max_case_max_loading_pu": float(group["max_loading_pu"].max()),
                "median_case_max_loading_pu": float(group["max_loading_pu"].median()),
                "min_case_hours_over_100pct": int(
                    group["hours_over_100pct"].astype(float).min()
                ),
                "max_case_hours_over_100pct": int(
                    group["hours_over_100pct"].astype(float).max()
                ),
                "robustness_classification": classification,
            }
        )
    result = pd.DataFrame(records)
    return result.sort_values(
        [
            "overloaded_all_cases",
            "rating_uses_ksebl_conductor_current_reference",
            "min_case_max_loading_pu",
            "max_case_max_loading_pu",
            "line_id",
        ],
        ascending=[False, False, False, False, True],
    )


def _aggregate_transformers(
    case_paths: dict[str, Path],
) -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    for case_id, path in case_paths.items():
        frame = pd.read_csv(path / "transformer_loading_summary.csv")
        frame = frame[
            frame["independent_capacity_bottleneck_claim_eligible"].map(_as_bool)
        ].copy()
        frame["case_id"] = case_id
        frame["overloaded"] = frame["hours_over_100pct"].fillna(0).astype(float) > 0
        frames.append(frame)
    all_rows = pd.concat(frames, ignore_index=True)
    case_count = len(case_paths)
    records: list[dict[str, Any]] = []
    for tx_id, group in all_rows.groupby("transformer_link_id", sort=True):
        first = group.iloc[0]
        overload_count = int(group["overloaded"].sum())
        records.append(
            {
                "transformer_link_id": tx_id,
                "location": first.get("location", ""),
                "bus0": first["bus0"],
                "bus1": first["bus1"],
                "v0_kv": int(float(first["v0_kv"])),
                "v1_kv": int(float(first["v1_kv"])),
                "source_backed_capacity_mva": float(first["dc_base_s_nom_mva"]),
                "capacity_basis": first.get("capacity_basis", ""),
                "case_count": case_count,
                "overload_case_count": overload_count,
                "overloaded_all_cases": overload_count == case_count,
                "overloaded_any_case": overload_count > 0,
                "min_case_max_loading_pu": float(group["max_loading_pu"].min()),
                "max_case_max_loading_pu": float(group["max_loading_pu"].max()),
                "median_case_max_loading_pu": float(group["max_loading_pu"].median()),
                "min_case_hours_over_100pct": int(
                    group["hours_over_100pct"].fillna(0).astype(float).min()
                ),
                "max_case_hours_over_100pct": int(
                    group["hours_over_100pct"].fillna(0).astype(float).max()
                ),
                "robustness_classification": (
                    "ROBUST_INDEPENDENT_PSS_BACKED_TRANSFORMER_BOTTLENECK"
                    if overload_count == case_count
                    else (
                        "INTERFACE_ALLOCATION_SENSITIVE_PSS_BACKED_TRANSFORMER"
                        if overload_count > 0
                        else "PSS_BACKED_TRANSFORMER_NOT_OVERLOADED_IN_ENVELOPE"
                    )
                ),
            }
        )
    result = pd.DataFrame(records)
    return result.sort_values(
        [
            "overloaded_all_cases",
            "min_case_max_loading_pu",
            "max_case_max_loading_pu",
            "transformer_link_id",
        ],
        ascending=[False, False, False, True],
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--hours", type=int, default=8760)
    parser.add_argument(
        "--baseline",
        type=Path,
        default=ROOT / "results/network/network_chronological_screening_v1_0",
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
        "--suite",
        type=Path,
        default=ROOT / "configs/kseb_network_chronological_screening_v1_0.yaml",
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
        default=ROOT / "results/network/network_bottleneck_robustness_v1_0",
    )
    parser.add_argument("--acknowledge-screening-only", action="store_true")
    args = parser.parse_args()
    if not args.acknowledge_screening_only:
        parser.error(
            "Pass --acknowledge-screening-only; boundary cases are screening "
            "sensitivities, not measured interface dispatch."
        )

    baseline_summary = json.loads(
        (args.baseline / "summary.json").read_text(encoding="utf-8")
    )
    if baseline_summary["hours"] != args.hours:
        raise ValueError("baseline chronology does not match requested hours")
    interfaces = pd.read_csv(args.baseline / "boundary_interfaces.csv")
    admitted = interfaces[
        interfaces["admitted_for_boundary_allocation"].map(_as_bool)
    ].copy()
    if admitted.empty:
        raise ValueError("baseline has no admitted external interfaces")
    admitted_buses = admitted["bus_id"].astype(str).tolist()

    common = {
        "root": ROOT,
        "suite_path": args.suite,
        "buses_path": args.network_dir / "screening_buses.csv",
        "lines_path": args.network_dir / "screening_lines.csv",
        "transformers_path": args.network_dir / "screening_transformer_links.csv",
        "generators_path": args.generators,
        "spatial_load_path": args.network_dir / "spatial_load_proxy_wide.parquet",
        "load_weights_path": args.network_dir / "load_weights.csv",
        "load_manifest_path": args.load_manifest,
        "daily_path": args.daily,
        "daily_qa_path": args.daily_qa,
        "hours": args.hours,
    }

    args.out.mkdir(parents=True, exist_ok=True)
    case_paths: dict[str, Path] = {"screening_mva": args.baseline}
    case_summaries: dict[str, dict[str, Any]] = {
        "screening_mva": baseline_summary
    }

    equal_dir = args.out / "cases/equal_interface"
    case_summaries["equal_interface"] = run_screening(
        **common,
        out_dir=equal_dir,
        boundary_allocation_mode="equal_interface",
    )
    case_paths["equal_interface"] = equal_dir

    for index, bus_id in enumerate(admitted_buses, start=1):
        case_id = f"single_{index:02d}_{_slug(bus_id)}"
        case_dir = args.out / "cases" / case_id
        case_summaries[case_id] = run_screening(
            **common,
            out_dir=case_dir,
            boundary_allocation_mode="single_interface",
            single_interface_bus=bus_id,
        )
        case_paths[case_id] = case_dir

    line_robustness = _aggregate_lines(case_paths)
    tx_robustness = _aggregate_transformers(case_paths)
    line_robustness.to_csv(args.out / "line_bottleneck_robustness.csv", index=False)
    tx_robustness.to_csv(
        args.out / "transformer_bottleneck_robustness.csv", index=False
    )

    cases = []
    for case_id, summary in case_summaries.items():
        boundary = summary["boundary_allocation"]
        cases.append(
            {
                "case_id": case_id,
                "mode": boundary["mode"],
                "single_interface_bus": boundary["single_interface_bus"],
                "weights": boundary["weights"],
                "primary_lines_over_100pct_any_hour": summary[
                    "line_screening"
                ]["primary_lines_over_100pct_any_hour"],
                "primary_source_backed_lines_over_100pct_any_hour": summary[
                    "line_screening"
                ]["primary_source_backed_rating_lines_over_100pct_any_hour"],
                "independent_transformers_over_100pct_any_hour": summary[
                    "transformer_screening"
                ]["independent_source_backed_transformers_over_100pct_any_hour"],
                "topology_gap_supply_mwh": summary["chronology"][
                    "topology_gap_supply_mwh"
                ],
            }
        )

    robust_source = line_robustness[
        line_robustness["robustness_classification"]
        == "ROBUST_SOURCE_BACKED_SCREENING_BOTTLENECK"
    ]
    sensitive_source = line_robustness[
        line_robustness["robustness_classification"]
        == "INTERFACE_ALLOCATION_SENSITIVE_SOURCE_BACKED"
    ]
    robust_fallback = line_robustness[
        line_robustness["robustness_classification"]
        == "ROBUST_FALLBACK_RATING_SCREENING_SIGNAL"
    ]
    sensitive_fallback = line_robustness[
        line_robustness["robustness_classification"]
        == "FALLBACK_RATING_INTERFACE_SENSITIVE"
    ]
    robust_tx = tx_robustness[
        tx_robustness["robustness_classification"]
        == "ROBUST_INDEPENDENT_PSS_BACKED_TRANSFORMER_BOTTLENECK"
    ]
    sensitive_tx = tx_robustness[
        tx_robustness["robustness_classification"]
        == "INTERFACE_ALLOCATION_SENSITIVE_PSS_BACKED_TRANSFORMER"
    ]

    qa = {
        "classification": CLASSIFICATION,
        "hours_per_case": args.hours,
        "case_count": len(case_paths),
        "expected_case_count": 2 + len(admitted_buses),
        "admitted_interface_count": len(admitted_buses),
        "admitted_interface_buses": admitted_buses,
        "all_cases_topology_closed_without_gap_supply": all(
            abs(float(row["topology_gap_supply_mwh"])) < 1e-8 for row in cases
        ),
        "source_backed_primary_lines_tested": int(
            line_robustness[
                "rating_uses_ksebl_conductor_current_reference"
            ].sum()
        ),
        "robust_source_backed_screening_bottlenecks": len(robust_source),
        "interface_sensitive_source_backed_lines": len(sensitive_source),
        "robust_fallback_rating_screening_signals": len(robust_fallback),
        "interface_sensitive_fallback_rating_lines": len(sensitive_fallback),
        "independent_pss_backed_transformers_tested": len(tx_robustness),
        "robust_independent_pss_backed_transformer_bottlenecks": len(robust_tx),
        "interface_sensitive_pss_backed_transformers": len(sensitive_tx),
        "calibrated_dc_power_flow": False,
        "ac_power_flow": False,
        "measured_interface_dispatch": False,
        "n_minus_1_reliability": False,
        "validated_operational_security": False,
        "cases": cases,
        "interpretation": [
            (
                "Robust means the screening overload persists under the baseline "
                "screening-MVA split, equal interface split, and every one-at-a-time "
                "admitted-interface placement case."
            ),
            (
                "Single-interface cases are deliberately extreme location sensitivities, "
                "not feasible dispatch schedules or interface-capability claims."
            ),
            (
                "Source-backed line ratings use KSEBL conductor/current evidence but are "
                "not operator seasonal or emergency ratings."
            ),
            (
                "This robustness screen does not replace measured interface dispatch, "
                "calibrated branch parameters, AC load flow or N-1 security analysis."
            ),
        ],
    }
    (args.out / "case_summary.json").write_text(
        json.dumps(qa, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(qa, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
