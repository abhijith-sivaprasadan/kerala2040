"""Fail-closed PPAC all-FY petroleum sales, not a final energy balance."""
from __future__ import annotations

import json
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RECORD = ROOT / "data/evidence/total_energy/ppac_full_fy_kerala_source_audit_2026_09_24.json"
CLASSIFICATION = "PPAC_KERALA_ANNUAL_OIL_COMPANY_SALES_NOT_FINAL_ENERGY_OR_SECTOR_ALLOCATION"
FYS = ("2019-20", "2020-21", "2021-22", "2022-23", "2023-24", "2024-25")
ALL_POL = ("6533.5", "5461.3", "5901.7", "6879.1", "6891.7", "6939.7")
MOTOR_SPIRIT = ("1558.8", "1371.1", "1495.8", "1747.6", "1791.5", "1879.4")
HSD = (None, "1922.7", "2101.1", "2485.6", "2413.3", "2419.3")


def validate_ppac_sales(data: dict) -> dict:
    if data.get("classification") != CLASSIFICATION:
        raise ValueError("PPAC sales reporting boundary changed")
    rows = data["annual_kerala_rows"]
    if tuple(row["fy"] for row in rows) != FYS:
        raise ValueError("Six PPAC fiscal-year labels changed")
    for key, expected in (
        ("all_pol_tmt", ALL_POL), ("ms_tmt", MOTOR_SPIRIT), ("hsd_tmt", HSD)
    ):
        actual = tuple(
            None if row[key] is None else str(Decimal(str(row[key])))
            for row in rows
        )
        if actual != expected:
            raise ValueError(f"PPAC source year/product values changed: {key}")
    qa = data["qa"]
    if (
        qa["primary_fy2024_25_pdf_image_verified"] is not False
        or qa["all_rows_full_fiscal_year"] is not True
        or qa["all_pol_includes_subcategory_ms_hsd"] is not True
        or qa["no_annualisation_of_h1"] is not True
        or qa["no_mass_to_energy_without_source_factors"] is not True
        or qa["revenue_cost_or_kerala_import_claim_ready"] is not False
    ):
        raise ValueError("PPAC source admission or additive energy rule breached")
    if (
        rows[-1]["all_pol_tier"] != "secondary_transcription_unverified_at_primary"
        or data["source_register"]["fy2024_25_secondary_transcription"][
            "status"
        ] != "secondary_transcription_unverified_at_primary"
        or data["source_register"]["ppac_fy2024_25_primary_unretrieved"][
            "original_page_image_verified"
        ] is not False
    ):
        raise ValueError("FY2024-25 mirrored PPAC table promoted without primary QA")
    if rows[0]["hsd_tmt"] is not None:
        raise ValueError("Original FY2019-20 diesel missing cell must stay null")
    if (
        data["vintage_disagreements"][0]["earlier_all_pol_tmt"] != 6882.6
        or data["vintage_disagreements"][0]["later_all_pol_tmt"] != 6879.1
    ):
        raise ValueError("Revised publisher historical total concealed")
    if data["emc_data_request"]["not_obtained"] is not True:
        raise ValueError("EMC workbook claim not verified")
    if not all(x is None for x in data["unsupported_current_results"].values()):
        raise ValueError("PPAC product sales illegally promoted to current final energy")
    return {
        "annual_rows": len(rows),
        "full_year_2024_25_original_image_verified": False,
        "kerala_current_final_energy_ready": False,
    }


def load_ppac_sales(path: Path = RECORD) -> dict:
    record = json.loads(path.read_text(encoding="utf-8"))
    validate_ppac_sales(record)
    return record
