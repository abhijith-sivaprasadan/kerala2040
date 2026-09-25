"""Validate the partial-exact 31 March 2026 Kerala fleet reconciliation."""
from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path
from typing import Any

CLASSIFICATION = (
    "PARTIAL_EXACT_AGGREGATE_FLEET_RECONCILIATION_WITH_EXPLICIT_RESIDUALS_"
    "NOT_DISPATCH_READY"
)


@dataclass(frozen=True)
class FleetSummary:
    base_date: str
    physical_capacity_mw: float
    thermal_mw: float
    hydro_mw: float
    wind_mw: float
    solar_grid_and_rooftop_mw: float
    bio_power_mw: float
    hydro_residual_mw: float
    wind_residual_mw: float
    ground_solar_residual_mw: float
    exact_aggregate_fleet_reconciled: bool
    station_level_complete: bool
    dispatch_ready: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _near(a: float, b: float, tol: float = 1e-6) -> bool:
    return abs(float(a) - float(b)) <= tol


def load_fleet(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    validate_fleet(data)
    return data


def validate_fleet(data: dict[str, Any]) -> None:
    if data.get("classification") != CLASSIFICATION:
        raise ValueError("fleet classification mismatch")
    if data.get("base_date") != "2026-03-31":
        raise ValueError("fleet base date changed")

    totals = data["exact_technology_totals_mw"]
    expected_total = (
        totals["thermal"]
        + totals["large_hydro"]
        + totals["small_hydro"]
        + totals["wind"]
        + totals["bio_power"]
        + totals["solar_ground_mounted"]
        + totals["solar_rooftop"]
        + totals["solar_off_grid_or_kusum_b"]
        + totals["solar_hybrid"]
    )
    if not _near(expected_total, totals["total_physical"]):
        raise ValueError("fleet technology totals do not reconcile")

    thermal = data["thermal"]
    if not _near(sum(float(row["capacity_mw"]) for row in thermal), totals["thermal"]):
        raise ValueError("thermal rows do not reconcile")
    excluded_ids = {row["id"] for row in data["excluded_or_historical"]}
    if not {"bses_kochi", "kasaragod_power_thermal"} <= excluded_ids:
        raise ValueError("historical thermal assets were not explicitly excluded")
    if any(row["id"] in excluded_ids for row in thermal):
        raise ValueError("excluded historical thermal asset appears in current fleet")

    hydro = data["hydro_reconciliation"]
    if not _near(hydro["large_hydro"]["exact_mw"], totals["large_hydro"]):
        raise ValueError("large-hydro exact total changed")
    if not _near(hydro["small_hydro"]["exact_mw"], totals["small_hydro"]):
        raise ValueError("small-hydro exact total changed")
    for key in ("large_hydro", "small_hydro", "total"):
        row = hydro[key]
        if not _near(row["station_seed_mw"] + row["residual_unresolved_mw"], row["exact_mw"]):
            raise ValueError(f"{key} station seed and residual do not reconcile")
    if not _near(
        hydro["large_hydro"]["residual_unresolved_mw"]
        + hydro["small_hydro"]["residual_unresolved_mw"],
        hydro["total"]["residual_unresolved_mw"],
    ):
        raise ValueError("hydro residual subtotals do not reconcile")

    wind = data["wind"]
    if not _near(wind["named_seed_mw"] + wind["residual_unresolved_mw"], wind["exact_mw"]):
        raise ValueError("wind named seed and residual do not reconcile")
    if not _near(wind["exact_mw"], totals["wind"]):
        raise ValueError("wind total disagrees with base technology total")

    solar = data["solar"]
    ground = solar["ground_mounted"]
    if not _near(
        ground["named_seed_mw"] + ground["residual_unresolved_mw"], ground["exact_mw"]
    ):
        raise ValueError("ground solar named seed and residual do not reconcile")
    if not _near(ground["exact_mw"], totals["solar_ground_mounted"]):
        raise ValueError("ground solar total disagrees with base technology total")
    if solar["rooftop"]["explicit_dispatch_generator"] is not False:
        raise ValueError("rooftop solar cannot be explicit with net-grid demand")
    if solar["rooftop"]["representation"] != "embedded_in_net_grid_demand":
        raise ValueError("rooftop solar representation changed")
    if solar["off_grid_or_kusum_b"]["representation"] != "excluded_from_grid_dispatch":
        raise ValueError("off-grid solar entered grid dispatch")

    kasargod = [
        row for row in ground["named_seed"] if row["id"] == "kasaragod_solar_park"
    ]
    if len(kasargod) != 1 or not _near(kasargod[0]["capacity_mw"], 100.0):
        raise ValueError("Kasaragod park subtotal changed or was duplicated")

    release = data["release"]
    if release["exact_aggregate_fleet_reconciled"] is not True:
        raise ValueError("aggregate fleet reconciliation must remain explicit")
    if release["station_level_fleet_complete"] is not False:
        raise ValueError("station-level fleet was promoted without closing residuals")
    if release["unit_level_fleet_complete"] is not False:
        raise ValueError("unit-level fleet was promoted without unit evidence")
    if release["dispatch_ready"] is not False:
        raise ValueError("fleet was promoted to dispatch-ready")
    if release["capacity_expansion_ready"] is not False:
        raise ValueError("fleet was promoted to capacity-expansion-ready")

    if not any(
        float(value) > 0
        for value in (
            hydro["total"]["residual_unresolved_mw"],
            wind["residual_unresolved_mw"],
            ground["residual_unresolved_mw"],
        )
    ):
        raise ValueError("station-level residuals disappeared without evidence")


def summarize_fleet(data: dict[str, Any]) -> FleetSummary:
    validate_fleet(data)
    totals = data["exact_technology_totals_mw"]
    hydro = data["hydro_reconciliation"]
    wind = data["wind"]
    ground = data["solar"]["ground_mounted"]
    return FleetSummary(
        base_date=data["base_date"],
        physical_capacity_mw=float(totals["total_physical"]),
        thermal_mw=float(totals["thermal"]),
        hydro_mw=float(totals["large_hydro"] + totals["small_hydro"]),
        wind_mw=float(totals["wind"]),
        solar_grid_and_rooftop_mw=float(
            totals["solar_ground_mounted"]
            + totals["solar_rooftop"]
            + totals["solar_off_grid_or_kusum_b"]
            + totals["solar_hybrid"]
        ),
        bio_power_mw=float(totals["bio_power"]),
        hydro_residual_mw=float(hydro["total"]["residual_unresolved_mw"]),
        wind_residual_mw=float(wind["residual_unresolved_mw"]),
        ground_solar_residual_mw=float(ground["residual_unresolved_mw"]),
        exact_aggregate_fleet_reconciled=bool(
            data["release"]["exact_aggregate_fleet_reconciled"]
        ),
        station_level_complete=bool(data["release"]["station_level_fleet_complete"]),
        dispatch_ready=bool(data["release"]["dispatch_ready"]),
    )
