"""Validate and summarize the canonical 31 March 2026 Kerala base system."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import yaml

CLASSIFICATION = "reconciled_structural_base_not_dispatch_ready"


@dataclass(frozen=True)
class BaseSystemSummary:
    base_date: str
    thermal_mw: float
    large_hydro_mw: float
    small_hydro_mw: float
    hydro_total_mw: float
    wind_mw: float
    bio_power_mw: float
    solar_total_mw: float
    rooftop_solar_mw: float
    ground_solar_mw: float
    renewable_total_mw: float
    physical_capacity_total_mw: float
    rooftop_solar_treatment: str
    same_date_technology_capacity_reconciled: bool
    dispatch_ready: bool
    expansion_ready: bool
    blocker_count: int

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _near(a: float, b: float, tol: float = 1e-6) -> bool:
    return abs(float(a) - float(b)) <= tol


def load_base_system(path: Path) -> dict[str, Any]:
    cfg = yaml.safe_load(path.read_text(encoding="utf-8"))
    validate_base_system(cfg)
    return cfg


def validate_base_system(cfg: dict[str, Any]) -> None:
    if cfg.get("classification") != CLASSIFICATION:
        raise ValueError("base-system classification mismatch")
    if cfg.get("base_date") != "2026-03-31":
        raise ValueError("canonical base date must remain 2026-03-31")

    cap = cfg["capacity_boundary_mw"]
    re = cap["renewable_location_based"]
    solar = re["solar"]
    bio = re["bio_power"]

    if not _near(re["large_hydro"] + re["small_hydro"], re["hydro_total"]):
        raise ValueError("hydro categories do not reconcile")
    if not _near(
        solar["ground_mounted"]
        + solar["rooftop_including_pm_surya_ghar"]
        + solar["hybrid_component"]
        + solar["off_grid_or_kusum_component_b"],
        solar["total"],
    ):
        raise ValueError("MNRE solar categories do not reconcile")
    if not _near(
        bio["biomass_non_bagasse"] + bio["waste_to_energy_off_grid"],
        bio["total"],
    ):
        raise ValueError("MNRE bio-power categories do not reconcile")
    if not _near(
        re["hydro_total"] + re["wind"] + bio["total"] + solar["total"],
        re["total"],
    ):
        raise ValueError("MNRE location-based renewable total does not reconcile")
    if not _near(cap["thermal"] + re["total"], cap["physical_capacity_total_mw"]):
        raise ValueError("physical March-2026 capacity total does not reconcile")

    thermal_sum = sum(
        float(row["accounting_mw"]) for row in cfg["named_asset_crosschecks"]["thermal"]
    )
    if not _near(thermal_sum, cap["thermal"]):
        raise ValueError("named/residual thermal rows do not reconcile")

    distributed = cfg["distributed_solar_boundary"]
    if not _near(
        distributed["rooftop_capacity_mw"], solar["rooftop_including_pm_surya_ghar"]
    ):
        raise ValueError("rooftop solar boundary disagrees with MNRE capacity")
    if distributed["rooftop_pypsa_treatment_default"] != "embedded_in_net_grid_demand":
        raise ValueError("rooftop default would change the declared demand boundary")
    if distributed["rooftop_explicit_generator_allowed"] is not False:
        raise ValueError("existing rooftop solar cannot be explicit with net-grid demand")
    if distributed["off_grid_pypsa_treatment_default"] != "excluded_from_grid_dispatch":
        raise ValueError("off-grid solar cannot enter grid dispatch by default")

    overlay = cfg["later_august_2026_renewable_overlay"]
    if overlay["applied_to_base"] is not False:
        raise ValueError("August 2026 overlay must not silently mutate March base")
    if overlay["as_of"] != "2026-08-31":
        raise ValueError("later renewable overlay date changed")

    storage = cfg["storage_boundary"]
    for key in (
        "operational_bess_power_mw",
        "operational_bess_energy_mwh",
        "operational_psp_power_mw",
    ):
        if storage[key] is not None:
            raise ValueError("unverified operational storage inserted into base")

    release = cfg["base_release"]
    if release["same_date_technology_capacity_reconciled"] is not True:
        raise ValueError("same-date technology reconciliation must remain explicit")
    if any(
        release[key] is not False
        for key in (
            "asset_level_fleet_reconciled",
            "chronological_dispatch_ready",
            "capacity_expansion_ready",
            "research_assumption_run_ready",
            "validated_run_ready",
        )
    ):
        raise ValueError("base system promoted beyond available evidence")
    if not cfg.get("blocking_inputs"):
        raise ValueError("base system must retain explicit blockers")


def summarize_base_system(cfg: dict[str, Any]) -> BaseSystemSummary:
    validate_base_system(cfg)
    cap = cfg["capacity_boundary_mw"]
    re = cap["renewable_location_based"]
    solar = re["solar"]
    release = cfg["base_release"]
    return BaseSystemSummary(
        base_date=cfg["base_date"],
        thermal_mw=float(cap["thermal"]),
        large_hydro_mw=float(re["large_hydro"]),
        small_hydro_mw=float(re["small_hydro"]),
        hydro_total_mw=float(re["hydro_total"]),
        wind_mw=float(re["wind"]),
        bio_power_mw=float(re["bio_power"]["total"]),
        solar_total_mw=float(solar["total"]),
        rooftop_solar_mw=float(solar["rooftop_including_pm_surya_ghar"]),
        ground_solar_mw=float(solar["ground_mounted"]),
        renewable_total_mw=float(re["total"]),
        physical_capacity_total_mw=float(cap["physical_capacity_total_mw"]),
        rooftop_solar_treatment=cfg["distributed_solar_boundary"][
            "rooftop_pypsa_treatment_default"
        ],
        same_date_technology_capacity_reconciled=bool(
            release["same_date_technology_capacity_reconciled"]
        ),
        dispatch_ready=bool(release["chronological_dispatch_ready"]),
        expansion_ready=bool(release["capacity_expansion_ready"]),
        blocker_count=len(cfg["blocking_inputs"]),
    )
