"""FY2024-25 Kerala installed-generation capacity census.

This module reconciles a source-bounded bottom-up station/portfolio register to
the official Kerala/KSEBL installed-capacity anchors at 31 March 2025.

Installed MW is not treated as hourly available MW. Distributed solar remains
in explicit aggregate buckets where no public asset-by-asset register is
available.
"""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

import pandas as pd

CLASSIFICATION = (
    "fy2024_25_capacity_accounting_census_reconciled_with_"
    "distributed_aggregate_buckets"
)
CATEGORY_TOLERANCE_MW = 0.011
SECTOR_TOLERANCE_MW = 0.011
TECHNOLOGY_TOLERANCE_MW = 0.011
DETAILED_TOTAL_TOLERANCE_MW = 0.020


def load_generator_census(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("classification") != CLASSIFICATION:
        raise ValueError("generator-census classification mismatch")
    if data.get("snapshot_date") != "2025-03-31":
        raise ValueError("generator-census snapshot boundary changed")
    return data


def _asset_frame(data: dict[str, Any]) -> pd.DataFrame:
    assets = data.get("assets") or []
    if not assets:
        raise ValueError("generator census contains no assets")
    frame = pd.DataFrame(assets)
    required = {
        "asset_id",
        "plant",
        "technology",
        "ownership_sector",
        "commercial_class",
        "capacity_mw",
        "capacity_basis",
        "status_as_of_2025_03_31",
        "included_in_official_state_total",
        "official_category",
        "source_tier",
        "source_id",
        "model_admission",
    }
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"generator census missing fields: {sorted(missing)}")
    if frame["asset_id"].duplicated().any():
        dupes = frame.loc[frame["asset_id"].duplicated(), "asset_id"].tolist()
        raise ValueError(f"duplicate generator asset IDs: {dupes}")
    frame["capacity_mw"] = pd.to_numeric(frame["capacity_mw"], errors="raise")
    if (frame["capacity_mw"] <= 0).any():
        raise ValueError("included generator capacities must be positive")
    if not frame["included_in_official_state_total"].astype(bool).all():
        raise ValueError("historical exclusions belong outside the included asset table")
    if not frame["status_as_of_2025_03_31"].eq("installed").all():
        raise ValueError("included asset table contains a non-installed row")
    allowed_technology = {"hydro", "thermal", "wind", "solar"}
    if not set(frame["technology"]).issubset(allowed_technology):
        raise ValueError("unexpected generator technology")
    allowed_sector = {"state", "central", "private"}
    if not set(frame["ownership_sector"]).issubset(allowed_sector):
        raise ValueError("unexpected ownership sector")
    return frame


def _sum_map(frame: pd.DataFrame, column: str) -> dict[str, float]:
    return {
        str(key): float(value)
        for key, value in frame.groupby(column, dropna=False)["capacity_mw"].sum().items()
    }


def _diff_map(
    detailed: dict[str, float],
    official: dict[str, float],
) -> dict[str, float]:
    return {
        key: float(detailed.get(key, 0.0) - float(value))
        for key, value in official.items()
    }


def _assert_within(
    differences: dict[str, float],
    tolerance: float,
    label: str,
) -> None:
    bad = {
        key: value
        for key, value in differences.items()
        if abs(float(value)) > float(tolerance) + 1e-12
    }
    if bad:
        raise ValueError(f"{label} reconciliation exceeds tolerance: {bad}")


def reconcile_generator_census(
    data: dict[str, Any],
) -> tuple[pd.DataFrame, dict[str, Any]]:
    frame = _asset_frame(data)

    official_categories = {
        str(key): float(value)
        for key, value in data["official_category_anchors_mw"].items()
    }
    categories = _sum_map(frame, "official_category")
    category_diff = _diff_map(categories, official_categories)
    extra_categories = set(categories) - set(official_categories)
    if extra_categories:
        raise ValueError(
            f"detailed assets use categories without official anchors: "
            f"{sorted(extra_categories)}"
        )
    missing_categories = set(official_categories) - set(categories)
    if missing_categories:
        raise ValueError(
            f"official categories have no detailed assets: {sorted(missing_categories)}"
        )
    _assert_within(category_diff, CATEGORY_TOLERANCE_MW, "category")

    sectors = _sum_map(frame, "ownership_sector")
    official_sectors = {
        str(key): float(value)
        for key, value in data["official_sector_anchors_mw"].items()
    }
    sector_diff = _diff_map(sectors, official_sectors)
    _assert_within(sector_diff, SECTOR_TOLERANCE_MW, "sector")

    technologies = _sum_map(frame, "technology")
    official_technologies = {
        str(key): float(value)
        for key, value in data["official_headline"]["technology_mix_mw"].items()
    }
    technology_diff = _diff_map(technologies, official_technologies)
    _assert_within(
        technology_diff,
        TECHNOLOGY_TOLERANCE_MW,
        "technology",
    )

    detailed_total = float(frame["capacity_mw"].sum())
    reported_total = float(data["official_headline"]["reported_total_mw"])
    category_anchor_sum = float(sum(official_categories.values()))
    sector_anchor_sum = float(sum(official_sectors.values()))

    if abs(category_anchor_sum - 4412.15) > 1e-9:
        raise ValueError("official category arithmetic no longer equals 4412.15 MW")
    if abs(reported_total - 4412.14) > 1e-9:
        raise ValueError("official reported headline total changed")
    if abs(detailed_total - reported_total) > DETAILED_TOTAL_TOLERANCE_MW:
        raise ValueError(
            "bottom-up detailed total is too far from the official headline: "
            f"{detailed_total:.6f} vs {reported_total:.6f}"
        )

    hydro = frame.loc[
        frame["official_category"].eq("Hydel: KSEB")
    ]
    if len(hydro) != 44:
        raise ValueError(f"KSEBL hydro station count is {len(hydro)}, expected 44")
    if abs(float(hydro["capacity_mw"].sum()) - 2196.361) > 1e-9:
        raise ValueError("44-station KSEBL hydro arithmetic changed")

    solar_other = float(
        frame.loc[
            frame["official_category"].eq("Solar other than KSEBL"),
            "capacity_mw",
        ].sum()
    )
    if abs(solar_other - 1264.24) > 1e-9:
        raise ValueError("detailed non-KSEBL non-IPP solar arithmetic changed")

    distributed = frame.loc[
        frame["capacity_basis"].isin(["distributed_aggregate", "aggregate_bucket"])
    ]
    individual = frame.loc[
        ~frame["capacity_basis"].isin(["distributed_aggregate", "aggregate_bucket"])
    ]

    exclusions = data.get("historical_exclusions") or []
    exclusion_ids = [item["asset_id"] for item in exclusions]
    if len(exclusion_ids) != len(set(exclusion_ids)):
        raise ValueError("duplicate historical exclusion IDs")
    if any(item.get("included_in_official_state_total") is not False for item in exclusions):
        raise ValueError("historical exclusion accidentally included in official total")

    release = data["release_gate"]
    if release["capacity_accounting_reconciled"] is not True:
        raise ValueError("capacity-accounting release flag is false")
    for key in (
        "every_physical_rooftop_asset_individually_enumerated",
        "plant_level_hourly_availability_verified",
        "unit_outage_derating_verified",
        "station_generation_reconciled",
        "dispatch_model_ready_from_installed_capacity_alone",
    ):
        if release[key] is not False:
            raise ValueError(f"release gate incorrectly closes {key}")

    summary = {
        "classification": CLASSIFICATION,
        "snapshot_date": data["snapshot_date"],
        "capacity_accounting_reconciled": True,
        "included_register_rows": int(len(frame)),
        "station_or_farm_rows": int(len(individual)),
        "aggregate_or_distributed_rows": int(len(distributed)),
        "historical_exclusion_rows": int(len(exclusions)),
        "bottom_up_detailed_total_mw": detailed_total,
        "official_reported_total_mw": reported_total,
        "bottom_up_minus_reported_total_mw": detailed_total - reported_total,
        "official_category_anchor_sum_mw": category_anchor_sum,
        "official_category_sum_minus_reported_total_mw": (
            category_anchor_sum - reported_total
        ),
        "official_sector_anchor_sum_mw": sector_anchor_sum,
        "category_capacity_mw": categories,
        "official_category_anchor_mw": official_categories,
        "category_residual_mw": category_diff,
        "technology_capacity_mw": technologies,
        "official_technology_anchor_mw": official_technologies,
        "technology_residual_mw": technology_diff,
        "sector_capacity_mw": sectors,
        "official_sector_anchor_mw": official_sectors,
        "sector_residual_mw": sector_diff,
        "ksebl_hydro_station_count": int(len(hydro)),
        "ksebl_hydro_detailed_mw": float(hydro["capacity_mw"].sum()),
        "capacity_basis_counts": dict(Counter(frame["capacity_basis"])),
        "model_admission_counts": dict(Counter(frame["model_admission"])),
        "historical_exclusions": exclusions,
        "source_ids": sorted(data["sources"]),
        "source_discrepancy_note": (
            "The official Appendix 11.2.4 category rows sum to 4412.15 MW "
            "while its printed total is 4412.14 MW. The detailed technical "
            "decomposition sums to 4412.156 MW because it retains more precise "
            "station/farm values and a 1264.24 MW non-KSEBL solar decomposition. "
            "No balancing/fudge row is inserted."
        ),
        "release_gate": release,
    }
    return frame, summary


def build_generator_census(
    source_path: Path,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    return reconcile_generator_census(load_generator_census(source_path))
