"""WP8 finance public-record boundary tests."""
from copy import deepcopy
from decimal import Decimal
import json
from pathlib import Path

import pytest

from kerala2040.wp8_finance import load_finance_ledger, validate_finance_ledger

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "data/evidence/finance/wp8_finance_source_ledger_2026_09_24.json"


def test_wp8_finance_ledger_reconciles_and_preserves_reporting_scopes():
    data = load_finance_ledger()
    checked = validate_finance_ledger(data)
    plan = data["planning_fy2025_26"]
    assert checked["proposed_energy_plan_inr_lakh"] == Decimal(115676)
    assert checked["proposed_ksebl_inr_lakh"] == Decimal(108880)
    assert checked["audited_fiscal_context_only"]
    assert checked["model_finance_ready"] is False
    assert sum(r["value"] for r in plan["energy_agency_outlay_inr_lakh"]) == 115676
    assert sum(r["value"] for r in plan["ksebl_proposed_outlay_components_inr_lakh"]) == 108880
    assert data["sources"]["annual_plan_2025_26"]["reporting_status"] == "budget_proposal_not_spending"
    assert data["fiscal_fy2024_25"]["scope"].startswith("statewide")
    assert len(data["financing_cases"]) == len(data["accounting_boundaries"]) == 6
    assert data["model_template"]["project_capex_inr"] is None
    assert data["model_template"]["financing_shares_pct"] is None
    assert data["model_template"]["scenario_winner"] is None


@pytest.mark.parametrize(
    ("path", "value"),
    [
        (("planning_fy2025_26", "provisional_visual_qa"), False),
        (("planning_fy2025_26", "reported_total_inr_lakh"), 115677),
        (("model_template", "project_capex_inr"), 100),
        (("model_template", "kerala_exchequer_npv_inr"), 50),
        (("fiscal_fy2024_25", "outstanding_guarantees_inr_crore"), 0),
        (("sources", "annual_plan_2025_26", "reporting_status"), "actual_expenditure"),
    ],
)
def test_finance_fails_closed_on_evidence_promotion(path, value):
    data = json.loads(LEDGER.read_text(encoding="utf-8"))
    mutated = deepcopy(data)
    obj = mutated
    for key in path[:-1]:
        obj = obj[key]
    obj[path[-1]] = value
    with pytest.raises(ValueError):
        validate_finance_ledger(mutated)


def test_finance_source_study_and_web_sections_present():
    chapter = (ROOT / "docs/WP8_FINANCE_FEDERAL_VALUE_CAPTURE_2026_09_24.md").read_text(
        encoding="utf-8"
    )
    html = (ROOT / "docs/index.html").read_text(encoding="utf-8")
    assert "WHO PAYS" in chapter
    assert "budget proposal" in chapter.lower()
    assert "48,510.20" in chapter
    for part in ("financeHeading", "financeStatus", "financeAgency",
                 "financeKSEB", "financeCAG", "financeCases"):
        assert f'id="{part}"' in html
