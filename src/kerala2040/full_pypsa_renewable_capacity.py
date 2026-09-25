"""Validate Full-PyPSA renewable capacity-envelope checkpoint v0.7."""
from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

import yaml

CLASSIFICATION = (
    "full_pypsa_renewable_capacity_envelope_v0_7_"
    "source_bounded_research_sensitivity_not_statutory_siting"
)


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_cstep(path: Path) -> dict[tuple[str, str], float]:
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    return {
        (row["resource"], row["metric"]): float(row["value"])
        for row in rows
    }


def load_capacity_envelope(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if data.get("classification") != CLASSIFICATION:
        raise ValueError("v0.7 renewable capacity envelope classification mismatch")
    return data


def validate_capacity_envelope(root: Path, config_path: Path) -> dict[str, Any]:
    data = load_capacity_envelope(config_path)
    sources = data["sources"]

    cstep = _read_cstep(root / sources["cstep_2024"])
    water = _read_json(root / sources["nise_and_niwe_context"])
    assets = _read_json(root / sources["current_capacity"])
    crosswalk = _read_json(root / sources["march_2026_solar_crosswalk"])
    ra = _read_json(root / sources["resource_adequacy"])
    wri = _read_json(root / sources["wri_2025"])
    gate = _read_json(root / sources["fail_closed_gate"])

    tech = data["technology_envelopes"]

    if cstep[("ground_mounted_solar", "usable_potential")] != 2423:
        raise ValueError("CSTEP ground-PV usable potential changed")
    if cstep[("floating_solar", "usable_potential")] != 920:
        raise ValueError("CSTEP floating-PV usable potential changed")
    if cstep[("wind", "potential")] != 2993:
        raise ValueError("CSTEP wind potential changed")

    nise = water["nise_2026"]
    if nise["with_cap_GWp"] != 2.22 or nise["without_cap_GWp"] != 5.73:
        raise ValueError("NISE Kerala floating-PV scenarios changed")
    if water["niwe_2019_120m"]["reported_kerala_scenario_mw"] != 2311:
        raise ValueError("NIWE 2019 Kerala wind scenario changed")

    if wri["extracted_values"]["onshore_wind_potential_mw"] != 2621:
        raise ValueError("WRI/NIWE onshore-wind benchmark changed")
    if wri["extracted_values"]["utility_scale_solar_potential_mw"] != 6110:
        raise ValueError("WRI/DoECC utility-solar benchmark changed")
    if wri["extracted_values"]["rooftop_potential_numeric"] is not None:
        raise ValueError("v0.7 rooftop ceiling must remain source-null")

    snapshot = assets["current_re_snapshot_aug2026"]
    if snapshot["solar_mw"]["rooftop_including_pm_surya_ghar"] != 2259.5:
        raise ValueError("August-2026 rooftop installed floor changed")
    if ra["planned_capacity_totals_mw"]["solar_rooftop_dre"] != 3698:
        raise ValueError("resource-adequacy rooftop-DRE planning additions changed")

    alternate = crosswalk["alternate_same_date_boundary_preserved_from_pr72"]
    if alternate["solar_ground_mounted_mw"] != 340.26:
        raise ValueError("March-2026 MNRE ground-mounted bridge changed")
    canonical_solar = crosswalk["canonical_cea_boundary"]
    canonical_wind = 400.34 - float(canonical_solar["total_solar_ge_1mw_mw"])
    if abs(canonical_wind - 71.525) > 1e-9:
        raise ValueError("canonical March-2026 wind decomposition changed")

    if gate["model_admitted"] is not False:
        raise ValueError("legacy renewable siting gate must remain fail-closed")

    if tech["rooftop_pv"]["technical_ceiling_mw"] is not None:
        raise ValueError("rooftop endogenous ceiling cannot be invented")
    if tech["rooftop_pv"]["endogenous_expansion_admitted"] is not False:
        raise ValueError("rooftop endogenous expansion must remain blocked")

    for name in ("ground_utility_pv", "floating_pv", "onshore_wind"):
        cases = tech[name]["published_total_capacity_scenarios_mw"]
        values = [float(cases[key]["value"]) for key in ("low", "reference", "high")]
        if values != sorted(values):
            raise ValueError(f"{name} scenario envelope is not monotonic")

    ground = tech["ground_utility_pv"]
    existing_ground = float(ground["conservative_existing_floor_mw"]["value"])
    for key in ("low", "reference", "high"):
        expected = (
            float(ground["published_total_capacity_scenarios_mw"][key]["value"])
            - existing_ground
        )
        if abs(float(ground["derived_additional_headroom_mw"][key]) - expected) > 1e-9:
            raise ValueError("ground-PV headroom arithmetic mismatch")

    floating = tech["floating_pv"]
    for key in ("low", "reference", "high"):
        expected = (
            float(floating["published_total_capacity_scenarios_mw"][key]["value"])
            - float(floating["known_existing_floor_mw"])
        )
        if abs(float(floating["derived_additional_headroom_mw"][key]) - expected) > 1e-9:
            raise ValueError("floating-PV headroom arithmetic mismatch")

    wind = tech["onshore_wind"]
    current_wind = float(wind["current_installed_mw"]["value"])
    for key in ("low", "reference", "high"):
        expected = (
            float(wind["published_total_capacity_scenarios_mw"][key]["value"])
            - current_wind
        )
        if abs(float(wind["derived_additional_headroom_mw"][key]) - expected) > 1e-9:
            raise ValueError("wind headroom arithmetic mismatch")

    if abs(float(tech["onshore_wind"]["current_installed_mw"]["value"]) - canonical_wind) > 1e-9:
        raise ValueError("v0.7 wind installed baseline is not March-2026 canonical")

    release = data["release"]
    if release["validated_capacity_expansion_ready"] is not False:
        raise ValueError("v0.7 cannot declare validated expansion readiness")
    if release["statutory_buildable_capacity_ready"] is not False:
        raise ValueError("v0.7 cannot declare statutory buildable capacity")

    return {
        "classification": CLASSIFICATION,
        "source_checks_passed": True,
        "published_capacity_envelope_ready": True,
        "statewide_2030_proxy_capacity_expansion_candidate_limits_ready": True,
        "full_economic_capacity_expansion_ready": False,
        "validated_capacity_expansion_ready": False,
        "statutory_buildable_capacity_ready": False,
        "packaged_research_cases": data["packaged_research_cases"],
        "technology_status": {
            "rooftop_pv": "exogenous_only_no_technical_ceiling",
            "ground_utility_pv": "published_scenario_envelope_with_conservative_headroom",
            "floating_pv": "published_scenario_envelope_with_existing_headroom",
            "onshore_wind": "published_scenario_envelope_with_existing_headroom",
        },
    }
