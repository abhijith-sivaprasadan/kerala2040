"""Kerala total-energy atlas: source, period and non-reconstruction gates."""
import json
from copy import deepcopy
from decimal import Decimal
from pathlib import Path

import pytest

from kerala2040.total_energy_atlas import (
    load_total_energy_source_register,
    validate_total_energy_source_register,
)

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/evidence/total_energy/kerala_total_energy_source_register_2026_09_24.json"


def test_historical_emc_chart_years_and_share_are_fiscal_and_not_rebuilt():
    d = load_total_energy_source_register()
    qa = validate_total_energy_source_register(d)
    assert qa == {
        "emc_historical_years": 6,
        "ppac_provisional_selected_products": 5,
        "current_final_energy_balance_ready": False,
    }
    emc = d["emc_final_energy"]
    assert [r["fy"] for r in emc["observed_years"]] == [
        "2014-15", "2015-16", "2016-17",
        "2017-18", "2018-19", "2019-20",
    ]
    assert Decimal(str(emc["baseline_total_mtoe"])) == Decimal("10.78")
    assert emc["mix_reconstruction_allowed"] is False
    assert emc["coal_captive_pct"] is None
    assert emc["internal_discrepancy"]["figure_3_fy2015_mtoe"] == 9.18
    assert emc["internal_discrepancy"]["section_3_prose_fy2015_mtoe"] == 9.81
    assert d["emc_2019_20_electricity_sector_share_context"]["classification"].endswith(
        "NOT_sector_shares_of_total_final_energy"
    )


def test_ppac_is_distinct_six_month_provisional_sales_not_fuel_energy():
    d = load_total_energy_source_register()
    ppac = d["ppac_provisional_half_year_2024_25"]
    assert (ppac["start_date"], ppac["end_date"]) == ("2024-04-01", "2024-09-30")
    assert ppac["no_annualisation"]
    assert ppac["publisher_pdf_visual_validation"] is False
    assert d["sources"]["ppac_h1_fy2024_25"]["status"] == "provisional"
    assert "NOT all petroleum" in ppac["scope"]
    assert all(v is None for v in d["quantities_deliberately_null"].values())
    assert all(r["tmt"] >= 0 for r in ppac["items"])


@pytest.mark.parametrize(
    ("path", "changed"),
    [
        (("emc_final_energy", "baseline_total_mtoe"), 15.0),
        (("emc_final_energy", "mix_reconstruction_allowed"), True),
        (("emc_final_energy", "internal_discrepancy"), {}),
        (("ppac_provisional_half_year_2024_25", "end_date"), "2025-03-31"),
        (("ppac_provisional_half_year_2024_25", "no_annualisation"), False),
        (("ppac_provisional_half_year_2024_25", "publisher_pdf_visual_validation"), True),
        (("quantities_deliberately_null", "kerala_total_final_energy_fy2024_25_mtoe"), 17.98),
    ],
)
def test_source_register_refuses_synthetic_current_energy(path, changed):
    d = json.loads(SOURCE.read_text(encoding="utf-8"))
    copy = deepcopy(d)
    item = copy
    for key in path[:-1]:
        item = item[key]
    item[path[-1]] = changed
    with pytest.raises(ValueError):
        validate_total_energy_source_register(copy)


def test_three_source_separated_interactive_homepage_mounts():
    html = (ROOT / "docs/index.html").read_text(encoding="utf-8")
    study = (ROOT / "docs/KERALA_TOTAL_ENERGY_ATLAS_BASELINE_2026_09_24.md").read_text(
        encoding="utf-8"
    )
    for mount in (
        "totalEnergyStatus", "totalEnergyHistoryChart", "totalEnergyMixChart",
        "totalEnergyPPACChart",
    ):
        assert f'id="{mount}"' in html
    assert "10.78 Mtoe" in study
    assert "FY2019–20" in study
    assert "not annual" in study.lower()
    assert "PPAC" in study
