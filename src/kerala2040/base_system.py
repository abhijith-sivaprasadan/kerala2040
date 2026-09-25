"""Validate and summarize the canonical 31 March 2026 Kerala base system."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

CLASSIFICATION = "reconciled_structural_base_not_dispatch_ready"


@dataclass(frozen=True)
class BaseSystemSummary:
    base_date: str
    cea_main_capacity_mw: float
    solar_lt_1mw_mw: float
    physical_arithmetic_capacity_mw: float
    thermal_mw: float
    hydro_mw: float
    renewable_ge_1mw_mw: float
    distributed_solar_treatment: str
    structural_capacity_reconciled: bool
    dispatch_ready: bool
    expansion_ready: bool
    blocker_count: int

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()


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
    main = cap["cea_main_table"]
    if not _near(
        main["thermal"] + main["hydro"] + main["renewable_wind_and_solar_ge_1mw"],
        main["total"],
    ):
        raise ValueError("CEA main capacity table does not reconcile")

    solar_lt = cap["solar_below_1mw_reported_separately"]
    if not _near(
        solar_lt["state"] + solar_lt["private"] + solar_lt["central"],
        solar_lt["total"],
    ):
        raise ValueError("sub-1-MW solar ownership does not reconcile")

    if not _near(
        main["total"] + solar_lt["total"],
        cap["physical_arithmetic_total_including_reported_sub_1mw_solar"],
    ):
        raise ValueError("combined physical capacity arithmetic does not reconcile")

    ownership = cfg["ownership_boundary_mw"]
    for owner, row in ownership.items():
        if not _near(
            row["thermal"] + row["hydro"] + row["renewable_wind_and_solar_ge_1mw"],
            row["main_table_total"],
        ):
            raise ValueError(f"{owner} main-table capacity does not reconcile")

    if not _near(sum(row["main_table_total"] for row in ownership.values()), main["total"]):
        raise ValueError("ownership main-table totals do not reconcile to CEA total")
    for technology, key in (
        ("thermal", "thermal"),
        ("hydro", "hydro"),
        ("renewable_wind_and_solar_ge_1mw", "renewable_wind_and_solar_ge_1mw"),
    ):
        if not _near(sum(row[key] for row in ownership.values()), main[technology]):
            raise ValueError(f"ownership {technology} does not reconcile")
    if not _near(sum(row["solar_lt_1mw"] for row in ownership.values()), solar_lt["total"]):
        raise ValueError("ownership sub-1-MW solar does not reconcile")

    assets = cfg["named_asset_crosschecks"]
    thermal_sum = sum(float(row["accounting_mw"]) for row in assets["thermal"])
    if not _near(thermal_sum, main["thermal"]):
        raise ValueError("named/residual thermal rows do not reconcile")
    re_sum = sum(float(row["accounting_mw"]) for row in assets["renewable_ge_1mw"])
    if not _near(re_sum, main["renewable_wind_and_solar_ge_1mw"]):
        raise ValueError("named/residual >=1 MW renewable rows do not reconcile")

    distributed = cfg["distributed_solar_boundary"]
    if distributed["pypsa_treatment_default"] != "embedded_in_net_grid_demand":
        raise ValueError("distributed-solar default would change the declared demand boundary")
    if distributed["explicit_generator_allowed"] is not False:
        raise ValueError("existing sub-1-MW solar cannot be explicit with net-grid demand")

    overlay = cfg["later_august_2026_renewable_overlay"]
    if overlay["applied_to_base"] is not False:
        raise ValueError("August 2026 overlay must not silently mutate March base")

    storage = cfg["storage_boundary"]
    for key in (
        "operational_bess_power_mw",
        "operational_bess_energy_mwh",
        "operational_psp_power_mw",
    ):
        if storage[key] is not None:
            raise ValueError("unverified operational storage inserted into base")

    release = cfg["base_release"]
    if release["structural_capacity_reconciled"] is not True:
        raise ValueError("base must expose completed structural capacity reconciliation")
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
    main = cap["cea_main_table"]
    release = cfg["base_release"]
    return BaseSystemSummary(
        base_date=cfg["base_date"],
        cea_main_capacity_mw=float(main["total"]),
        solar_lt_1mw_mw=float(cap["solar_below_1mw_reported_separately"]["total"]),
        physical_arithmetic_capacity_mw=float(
            cap["physical_arithmetic_total_including_reported_sub_1mw_solar"]
        ),
        thermal_mw=float(main["thermal"]),
        hydro_mw=float(main["hydro"]),
        renewable_ge_1mw_mw=float(main["renewable_wind_and_solar_ge_1mw"]),
        distributed_solar_treatment=cfg["distributed_solar_boundary"][
            "pypsa_treatment_default"
        ],
        structural_capacity_reconciled=bool(release["structural_capacity_reconciled"]),
        dispatch_ready=bool(release["chronological_dispatch_ready"]),
        expansion_ready=bool(release["capacity_expansion_ready"]),
        blocker_count=len(cfg["blocking_inputs"]),
    )
