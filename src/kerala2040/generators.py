"""Source-scoped project inventory with explicit official commissioning crosschecks.

A project-listing entry is never automatically an operating station or a measured
annual generator. Only independently documented FY2024-25 unit additions are
labelled crosschecked. Raw portal fields are retained for dispute resolution.
"""

from __future__ import annotations

import re
from datetime import date

import pandas as pd

_YEAR_RE = re.compile(r"(?:19|20)\\d{2}")
_KW_IN_NAME = re.compile(r"(?<!\\d)(\\d+(?:\\.\\d+)?)\\s*kW\\b", re.IGNORECASE)
CAPACITY_TOLERANCE_MW = 0.001


def _commissioning_year(label: str | None) -> int | None:
    if not label:
        return None
    match = _YEAR_RE.search(str(label))
    return int(match.group(0)) if match else None


def _named_kw_mw(name: str) -> float | None:
    """Convert an explicitly named kW generator; not arbitrary text/portal MW."""
    matches = _KW_IN_NAME.findall(name)
    if len(matches) != 1:
        return None
    return float(matches[0]) / 1000


def _official_events(
    project_payload: dict,
    observed_capacity: dict,
    reconciliation: dict | None,
) -> tuple[dict[str, dict], dict]:
    if not reconciliation:
        return {}, {}
    if reconciliation.get("classification") != (
        "official_crosscheck_of_project_portal_not_complete_operating_fleet"
    ):
        raise ValueError("Unexpected generator crosscheck classification")
    date.fromisoformat(reconciliation["snapshot_date"])
    totals = reconciliation["official_totals"]
    if abs(
        float(totals["all_kerala_installed_mw"])
        - float(observed_capacity["electricity"]["installed_capacity_mw"])
    ) > 0.01:
        raise ValueError("Generator crosscheck disagrees with Kerala statewide capacity")
    if abs(
        float(totals["all_kerala_hydel_mw"])
        - float(observed_capacity["electricity"]["capacity_mix_mw"]["hydel"])
    ) > 0.01:
        raise ValueError("Generator crosscheck disagrees with statewide hydel capacity")
    sources = reconciliation["primary_sources"]
    portal_names = [row.get("name") for row in project_payload["projects"]]
    if len(portal_names) != len(set(portal_names)):
        raise ValueError("Duplicate portal names require manual alias mapping")
    events: dict[str, dict] = {}
    for event in reconciliation["official_commissioned_during_fy"]:
        name = event["portal_name"]
        if name in events or name not in portal_names:
            raise ValueError(f"Official event missing from or duplicated in portal: {name}")
        if not event.get("sources") or len(set(event["sources"])) < 2:
            raise ValueError(f"Commissioning needs at least two identified sources: {name}")
        for key in event["sources"]:
            if key not in sources or not sources[key].get("url"):
                raise ValueError(f"Commissioning source missing URL: {key}")
        units = event["units"]
        if not units or len({unit["unit"] for unit in units}) != len(units):
            raise ValueError(f"Missing or duplicated generating units: {name}")
        if abs(sum(float(u["capacity_mw"]) for u in units)
               - float(event["commissioned_mw"])) > CAPACITY_TOLERANCE_MW:
            raise ValueError(f"Commissioned unit MW do not sum to plant MW: {name}")
        for unit in units:
            when = date.fromisoformat(unit["commissioning_date"])
            if not date(2024, 4, 1) <= when <= date(2025, 3, 31):
                raise ValueError(f"Commissioning date outside FY2024-25: {name}")
            if float(unit["capacity_mw"]) <= 0:
                raise ValueError(f"Invalid unit capacity: {name}")
        matches = [row for row in project_payload["projects"] if row["name"] == name]
        if len(matches) != 1 or matches[0]["technology"] != event["technology"]:
            raise ValueError(f"Official event technology/portal mismatch: {name}")
        if (
            matches[0]["capacity_mw"] is not None
            and abs(float(matches[0]["capacity_mw"])
                    - float(event["commissioned_mw"])) > CAPACITY_TOLERANCE_MW
        ):
            raise ValueError(f"Portal vs official event MW mismatch: {name}")
        events[name] = event
    return events, totals


def generator_database(
    project_payload: dict[str, object],
    observed_capacity: dict[str, object],
    reconciliation: dict | None = None,
) -> tuple[pd.DataFrame, dict[str, object]]:
    """Keep raw portal rows; certify only specifically evidenced FY additions."""
    events, totals = _official_events(project_payload, observed_capacity, reconciliation)
    records: list[dict[str, object]] = []
    for item in project_payload.get("projects", []):
        name = str(item.get("name") or "")
        portal_capacity = item.get("capacity_mw")
        named_mw = _named_kw_mw(name)
        conflict = bool(
            named_mw is not None and portal_capacity is not None
            and abs(named_mw - float(portal_capacity)) > CAPACITY_TOLERANCE_MW
        )
        event = events.get(name)
        records.append(
            {
                "plant": name,
                "technology": item.get("technology"),
                "district": item.get("district"),
                "capacity_mw": portal_capacity,  # Preserve original portal value!
                "status": item.get("status"),  # Preserve original portal status!
                "portal_milestone": item.get("milestone"),
                "portal_date_label": item.get("milestone_date_label"),
                "commissioning_year": (
                    _commissioning_year(item.get("milestone_date_label"))
                    if item.get("milestone") == "commissioned_on" else None
                ),
                "unit_label_capacity_mw": named_mw,
                "unit_label_conflicts_with_portal_mw": conflict,
                "reconciled_commissioned_mw": (
                    float(event["commissioned_mw"]) if event else None
                ),
                "reconciled_commissioning_dates": (
                    ";".join(u["commissioning_date"] for u in event["units"])
                    if event else None
                ),
                "commissioning_evidence_status": (
                    "independently_crosschecked_fy2024_25"
                    if event else "portal_only_not_independently_crosschecked"
                ),
                "owner": event["owner"] if event else None,
                "historical_generation_mu": None,
                "source": "KSEB Project Management System public portal",
                "source_classification": "official_project_portal_record",
                "source_url": project_payload.get(
                    "explorer_url", "https://pms.kseb.in/explore-projects"
                ),
                "official_commissioning_source_ids": (
                    ";".join(event["sources"]) if event else None
                ),
                "owner_status": (
                    "official_fy2024_25_source_crosscheck"
                    if event else "not_exposed_by_current_portal_export"
                ),
                "generation_status": "plant_level_history_not_in_current_evidence",
                "availability_status": "outage_derating_not_verified",
            }
        )

    frame = pd.DataFrame(records)
    completed = frame.loc[frame["status"].eq("Completed")].copy()
    completed_by_tech = (
        completed.groupby("technology", dropna=False)["capacity_mw"]
        .sum(min_count=1).dropna().to_dict()
    )
    official_mix = observed_capacity["electricity"]["capacity_mix_mw"]
    official_additions_mw = sum(float(e["commissioned_mw"]) for e in events.values())
    summary = {
        "classification": "project_portal_seed_with_bounded_official_crosschecks",
        "source_type": "provisional_generator_register_not_operating_fleet",
        "source": "KSEB project explorer and documented KSEBL/CEA commissioning references",
        "source_urls": [
            "https://pms.kseb.in/explore-projects",
            observed_capacity["sources"]["economic_review_2025_volume_1"]["url"]
        ] if "sources" in observed_capacity else ["https://pms.kseb.in/explore-projects"],
        "project_records": len(frame),
        "portal_reported_total": project_payload.get("portal_reported_total"),
        "uncaptured_portal_items": (
            int(project_payload["portal_reported_total"]) - len(frame)
            if project_payload.get("portal_reported_total") is not None else None
        ),
        "completed_records": len(completed),
        "portal_data_as_of_label": project_payload.get("tracker", {}).get("data_as_of_label"),
        "completed_portal_capacity_by_technology_mw": {
            str(key): float(value) for key, value in completed_by_tech.items()
        },
        "completed_portal_capacity_is_verified_fleet": False,
        "official_fy2024_25_commissioned_plant_count": len(events),
        "official_fy2024_25_commissioned_additions_mw": official_additions_mw,
        "independently_crosschecked_portal_names": sorted(events),
        "name_unit_portal_mw_conflicts": frame.loc[
            frame["unit_label_conflicts_with_portal_mw"], "plant"
        ].tolist(),
        "name_unit_portal_mw_conflict_count": int(
            frame["unit_label_conflicts_with_portal_mw"].sum()
        ),
        "official_fy2024_25_capacity_mix_mw": official_mix,
        "official_total_installed_capacity_mw": float(
            observed_capacity["electricity"]["installed_capacity_mw"]
        ),
        "official_ksebl_owned_totals": totals,
        "full_station_register_verified": False,
        "plant_level_fy_generation_verified": False,
        "plant_level_availability_verified": False,
        "limitations": [
            "A portal 'Completed' status does not prove operation at the FY boundary.",
            "A planned commissioning date is not an actual commissioning date.",
            "Only specifically crosschecked FY2024-25 unit additions have verified event MW.",
            "Name-embedded kW contradicting portal MW is flagged, never silently converted.",
            "A zero-MW initiative is not automatically a generating unit.",
            "Owner is null except where separately evidenced; retired/outaged capacity unresolved.",
            "Plant-level generation and outage/derating information are still missing.",
            "Portalled rows/technology totals cannot replace all-owner or KSEBL-only totals.",
        ],
    }
    return frame, summary
