"""Admit a dated historical final-energy extraction without fabricating current totals."""
from __future__ import annotations

import json
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REGISTER = ROOT / "data/evidence/total_energy/kerala_total_energy_source_register_2026_09_24.json"
CLASSIFICATION = (
    "HISTORICAL_KERALA_FINAL_ENERGY_AND_H1_PETROLEUM_SALES_"
    "NOT_CURRENT_COMPLETE_ENERGY_BALANCE"
)
FY = ("2014-15", "2015-16", "2016-17", "2017-18", "2018-19", "2019-20")
TFEC = ("9.18", "9.35", "9.61", "10.17", "10.33", "10.78")
PPAC = {
    "LPG": "579",
    "Motor spirit (petrol)": "937",
    "Superior kerosene oil": "3.41",
    "High-speed diesel": "1169.5",
    "Aviation turbine fuel": "283.7",
}


def validate_total_energy_source_register(value: dict) -> dict:
    if value.get("classification") != CLASSIFICATION:
        raise ValueError("Final-energy provenance classification changed")
    emc = value["emc_final_energy"]
    years = emc["observed_years"]
    if tuple(row["fy"] for row in years) != FY:
        raise ValueError("Incorrect EMC fiscal end-year interpretation")
    if tuple(str(Decimal(str(row["value_mtoe"]))) for row in years) != TFEC:
        raise ValueError("EMC six-year figure labels changed")
    if emc["baseline_fy"] != "2019-20" or Decimal(str(emc["baseline_total_mtoe"])) != Decimal("10.78"):
        raise ValueError("EMC published baseline changed")
    shares = {row["fuel"]: row["pct"] for row in emc["rounded_mix_pct"]}
    if shares != {
        "Oil": 64, "Electricity (utilities)": 19,
        "Coal (imported)": 16, "Gas": 1, "Coal (non-power)": 0
    }:
        raise ValueError("Publisher's rounded fuel share graphic changed")
    if sum(shares.values()) != 100 or emc["mix_reconstruction_allowed"] is not False:
        raise ValueError("Fuel mix cannot be reconstructed as precise measured Mtoe")
    if emc["coal_captive_pct"] is not None:
        raise ValueError("Unreported coal share manufactured")
    disagreement = emc["internal_discrepancy"]
    if disagreement.get("figure_3_fy2015_mtoe") != 9.18 or disagreement.get("section_3_prose_fy2015_mtoe") != 9.81 or disagreement.get("status") != "unresolved_publisher_internal_disagreement":
        raise ValueError("EMC figure/prose source discrepancy was concealed")
    ppac = value["ppac_provisional_half_year_2024_25"]
    if (ppac["start_date"], ppac["end_date"]) != ("2024-04-01", "2024-09-30"):
        raise ValueError("PPAC half-year period changed")
    if ppac["no_annualisation"] is not True or ppac["publisher_pdf_visual_validation"] is not False:
        raise ValueError("Provisional PPAC sales were promoted to verified annual demand")
    if {row["product"]: str(Decimal(str(row["tmt"]))) for row in ppac["items"]} != PPAC:
        raise ValueError("Indexed original PPAC product values changed")
    if not all(row is None for row in value["quantities_deliberately_null"].values()):
        raise ValueError("Current all-energy result was manufactured")
    if value["sources"]["emc_seeap"]["publisher"] != "Energy Management Centre Kerala / CII":
        raise ValueError("EMC publisher changed")
    if value["sources"]["ppac_h1_fy2024_25"]["status"] != "provisional":
        raise ValueError("PPAC status changed")
    return {
        "emc_historical_years": len(years),
        "ppac_provisional_selected_products": len(ppac["items"]),
        "current_final_energy_balance_ready": False,
    }


def load_total_energy_source_register(path: Path = REGISTER) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    validate_total_energy_source_register(value)
    return value
