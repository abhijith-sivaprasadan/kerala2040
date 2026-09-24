"""WP8 public finance-source checks; not a priced Kerala2040 scenario model."""
from __future__ import annotations

from decimal import Decimal
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RECORD = ROOT / "data/evidence/finance/wp8_finance_source_ledger_2026_09_24.json"
CLASSIFICATION = "WP8_FINANCE_PUBLIC_SOURCE_LEDGER_NOT_KERALA_2040_FINANCING_PLAN"


def _dec(x: object) -> Decimal:
    return Decimal(str(x))


def validate_finance_ledger(record: dict) -> dict:
    """Refuse cross-boundary promotion, stale source and fabricated project numbers."""
    if record["classification"] != CLASSIFICATION:
        raise ValueError("WP8 source classification changed")
    plan = record["planning_fy2025_26"]
    plan_sources = record["sources"]["annual_plan_2025_26"]
    if plan_sources["reporting_status"] != "budget_proposal_not_spending":
        raise ValueError("Budget plan incorrectly promoted as expenditure")
    if plan["provisional_visual_qa"] is not True:
        raise ValueError("Publisher PDF table needs a separately verified visual review")
    by_agency = {r["entity"]: _dec(r["value"]) for r in plan["energy_agency_outlay_inr_lakh"]}
    components = {r["category"]: _dec(r["value"])
                  for r in plan["ksebl_proposed_outlay_components_inr_lakh"]}
    if set(by_agency) != {"KSEBL", "ANERT", "Electrical Inspectorate", "EMC"}:
        raise ValueError("Incomplete agency source table")
    if len(components) != 3:
        raise ValueError("KSEBL finance category is incomplete")
    if sum(by_agency.values()) != _dec(plan["reported_total_inr_lakh"]):
        raise ValueError("Energy plan subtotal does not close")
    if sum(components.values()) != by_agency["KSEBL"]:
        raise ValueError("KSEBL own/external/State Plan subtotal does not close")
    if components["KSEBL own-fund schemes"] != Decimal(104218):
        raise ValueError("KSEBL own-fund cannot be booked as Kerala budget expenditure")
    audit = record["fiscal_fy2024_25"]
    if audit["scope"].startswith("statewide") is False:
        raise ValueError("Statewide audit was relabelled sector investment")
    if _dec(audit["original_finance_accounts"]["fiscal_deficit_inr_crore"]) != Decimal("48248.14"):
        raise ValueError("Wrong Finance Accounts deficit")
    if _dec(audit["post_audit"]["fiscal_deficit_inr_crore"]) != Decimal("48510.20"):
        raise ValueError("Wrong post-audit deficit")
    if _dec(audit["outstanding_guarantees_inr_crore"]) != Decimal("74297.58"):
        raise ValueError("Wrong statewide contingent liabilities")
    if len(record["accounting_boundaries"]) != 6 or len(record["financing_cases"]) != 6:
        raise ValueError("Missing payer or financing case")
    model = record["model_template"]
    for name in ("project_capex_inr", "lifecycle_cost_npv_inr",
                 "kerala_exchequer_npv_inr", "ksebl_cash_need_inr",
                 "union_support_inr", "private_capital_inr",
                 "consumer_bill_effect_inr", "scenario_winner"):
        if model[name] is not None:
            raise ValueError(f"An unvalidated finance outcome was promoted: {name}")
    return {
        "proposed_energy_plan_inr_lakh": sum(by_agency.values()),
        "proposed_ksebl_inr_lakh": sum(components.values()),
        "audited_fiscal_context_only": True,
        "model_finance_ready": False,
    }


def load_finance_ledger(path: Path = RECORD) -> dict:
    record = json.loads(path.read_text(encoding="utf-8"))
    validate_finance_ledger(record)
    return record
