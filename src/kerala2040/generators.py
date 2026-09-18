"""Canonical generator/capacity inventory helpers."""

from __future__ import annotations

import re

import pandas as pd


_YEAR_RE = re.compile(r"(19|20)\d{2}")


def _commissioning_year(label: str | None) -> int | None:
    if not label:
        return None
    match = _YEAR_RE.search(str(label))
    return int(match.group(0)) if match else None


def generator_database(
    project_payload: dict[str, object],
    observed_capacity: dict[str, object],
) -> tuple[pd.DataFrame, dict[str, object]]:
    """Normalise KSEB project records and compare them with official aggregate capacity."""
    records: list[dict[str, object]] = []
    for item in project_payload.get("projects", []):
        records.append(
            {
                "plant": item.get("name"),
                "technology": item.get("technology"),
                "district": item.get("district"),
                "capacity_mw": item.get("capacity_mw"),
                "status": item.get("status"),
                "commissioning_year": _commissioning_year(item.get("milestone_date_label")),
                "owner": None,
                "historical_generation_mu": None,
                "source": "KSEB Project Management System public portal",
                "source_classification": "official_project_portal_record",
                "owner_status": "not_exposed_by_current_portal_export",
                "generation_status": "plant_level_history_not_in_current_evidence",
            }
        )

    frame = pd.DataFrame(records)
    completed = frame.loc[frame["status"].eq("Completed")].copy()
    completed_by_tech = (
        completed.groupby("technology", dropna=False)["capacity_mw"]
        .sum(min_count=1)
        .dropna()
        .to_dict()
    )
    official_mix = observed_capacity["electricity"]["capacity_mix_mw"]
    summary = {
        "classification": "derived",
        "source_type": "canonical_inventory_seed",
        "source": "KSEB Project Management System public portal + Kerala State Planning Board/KSEBL Economic Review 2025",
        "project_records": len(frame),
        "completed_records": len(completed),
        "portal_data_as_of_label": project_payload.get("tracker", {}).get("data_as_of_label"),
        "completed_portal_capacity_by_technology_mw": {
            str(key): float(value) for key, value in completed_by_tech.items()
        },
        "official_fy2024_25_capacity_mix_mw": official_mix,
        "official_total_installed_capacity_mw": float(
            observed_capacity["electricity"]["installed_capacity_mw"]
        ),
        "limitations": [
            "The KSEB project portal is not a complete current ownership register.",
            "Owner is left null rather than inferred from plant names.",
            "Plant-level historical generation is not available in the current evidence bundle.",
            "Portal completed-project totals must not replace Economic Review aggregate capacity.",
        ],
    }
    return frame, summary
