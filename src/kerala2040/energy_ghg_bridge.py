"""Source-boundary validator for 2023 official Kerala sectoral GHG evidence.

This is NOT a converter from PPAC sales to FY2024-25 final energy.
"""

from __future__ import annotations

import json
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RECORD = ROOT / "data/evidence/total_energy/kerala_ghg_sector_bridge_2026_09_24.json"
CLASSIFICATION = "KERALA_GHG_2023_OFFICIAL_SECTOR_EMISSIONS_NOT_FINAL_ENERGY_OR_2024_25"


def validate_energy_ghg_bridge(data: dict) -> dict:
    if data.get("classification") != CLASSIFICATION:
        raise ValueError("Kerala emissions bridge classification changed")
    if data["period"] != "calendar_2023" or data["unit"] != "MtCO2e":
        raise ValueError("Calendar-year emissions confused with fiscal energy")
    if Decimal(str(data["energy_sector_2023_mtco2e"])) != Decimal("20.64"):
        raise ValueError("2023 official sector estimate changed")
    categories = data["categories"]
    expected = (
        ("transport", "13.59", "65.87"),
        ("residential", "3.2", "15.48"),
        ("industrial", "1.89", "9.16"),
    )
    actual = tuple(
        (
            r["id"], str(Decimal(str(r["mtco2e"]))),
            str(Decimal(str(r["share_of_energy_pct"])))
        )
        for r in categories
    )
    if actual != expected:
        raise ValueError("DoECC source sector category or denominator changed")
    if sum(Decimal(str(r["mtco2e"])) for r in categories) >= Decimal("20.64"):
        raise ValueError("Three categories must not claim full GHG coverage")
    source = data["historic_source_vintage_conflict"]
    if (
        source["calendar_year"] != 2020
        or Decimal(str(source["old_report_energy_mtco2e"])) != Decimal("16.96")
        or Decimal(str(source["current_portal_energy_mtco2e"])) != Decimal("17.09")
        or source["status"] != "non_identical_inventory_vintages; no merged trend; reconcile methodology and data revisions with DoECC"
    ):
        raise ValueError("Historical inventory version conflict suppressed")
    if data["historical_seeap_gcv"]["basis"].startswith(
        "GROSS CALORIFIC VALUE"
    ) is False:
        raise ValueError("Gross and net heating value boundaries were conflated")
    factors = {
        row["product"]: row["kcal_per_kg"]
        for row in data["historical_seeap_gcv"]["values"]
    }
    if factors != {
        "LPG": 11318,
        "Motor gasoline": 10717,
        "Gas/diesel oil": 10357,
        "Fuel oil": 9866,
        "Kerosene": 10467,
        "Kerosene type jet fuel": 10667,
        "Naphtha": 10767,
    }:
        raise ValueError("Historic gross energy-content reference changed")
    if (
        data["no_assumed_energy_2024_25_mtoe"] is not None
        or data["no_assumed_2024_25_sectoral_emissions_mtco2e"] is not None
        or data["no_co2_per_tonne_pol_ratio"] is not None
        or data["no_current_kerala_import_share"] is not None
        or data["no_externally_verified_2023_fuel_by_sector_matrix"] is not None
        or data["no_raw_seeap_workbook"] is not True
    ):
        raise ValueError("Unsupported fuel-energy, import, or sector result released")
    return {
        "calendar_2023_official_emissions": True,
        "categories": len(categories),
        "current_all_energy_balance_ready": False,
    }


def load_energy_ghg_bridge(path: Path = RECORD) -> dict:
    record = json.loads(path.read_text(encoding="utf-8"))
    validate_energy_ghg_bridge(record)
    return record
