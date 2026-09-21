"""Fail-closed renewable model-admission gate. Never copy proxies into PyPSA.

This is additional to existing project-wide gates, not a replacement.
Exit 2 until independent observed generation validation, legal GIS siting,
grid deliverability and source archival/permission are documented.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAPACITY = ROOT / "data/evidence/solar/solar_wind_feasible_capacity_gates_2026_09_22.json"
SOURCES = ROOT / "data/evidence/solar/solar_batch_2026_09_21_originals_manifest.json"
RESULT = ROOT / "results/solar_wind/renewable_model_admission_qa.json"


def evaluate(capacity: dict, sources: dict, validation: dict | None = None):
    validation = validation or {}
    tests = {
        "original_solar_release_verified": bool(sources.get("release_uploaded")),
        "independently_measured_solar_generation_or_irradiance_validation": bool(
            validation.get("solar_observed_validated")
        ),
        "independently_measured_wind_generation_or_height_mapped_validation": bool(
            validation.get("wind_observed_validated")
        ),
        "native_Kerala_resource_and_technology_site_masks_QA": bool(
            validation.get("Kerala_spatial_screen_validated")
        ),
        "legal_land_and_ecology_permissions": bool(
            validation.get("legal_siting_screen_validated")
        ),
        "verified_grid_headroom_and_firm_transfer": bool(
            validation.get("grid_constraints_validated")
        ),
        "technology_specific_manufacturer_power_models": bool(
            validation.get("technology_models_validated")
        ),
        "measured_demand_and_2040_system_gates": bool(
            validation.get("existing_project_release_gates_passed")
        ),
    }
    for row in capacity["technologies"].values():
        if row.get("feasible_GWp_range") is not None:
            tests["eligible_solar_capacity_not_yet_admitted"] = False
        if row.get("feasible_MW_range") is not None:
            tests["eligible_wind_capacity_not_yet_admitted"] = False
    return {
        "classification": "renewable_model_admission_FAIL_CLOSED",
        "checks": tests,
        "all_checks_pass": all(tests.values()),
        "model_admitted": False,
        "proxies_allowed_as_verified_generation": False,
    }


def main():
    capacity = json.loads(CAPACITY.read_text(encoding="utf8"))
    sources = json.loads(SOURCES.read_text(encoding="utf8"))
    result = evaluate(capacity, sources)
    RESULT.parent.mkdir(parents=True, exist_ok=True)
    RESULT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf8")
    print(json.dumps(result, indent=2))
    return 0 if result["all_checks_pass"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
