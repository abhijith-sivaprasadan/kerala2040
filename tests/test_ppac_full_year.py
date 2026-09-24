"""Full-fiscal-year PPAC fuel sales do not become a final-energy balance."""
import json
from copy import deepcopy
from pathlib import Path

import pytest

from kerala2040.ppac_full_year import load_ppac_sales, validate_ppac_sales

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "data/evidence/total_energy/ppac_full_fy_kerala_source_audit_2026_09_24.json"


def test_full_fy_sales_not_current_final_energy_or_reconciled_mtoe():
    d = load_ppac_sales()
    assert validate_ppac_sales(d)["annual_rows"] == 6
    r = d["annual_kerala_rows"]
    assert r[0]["all_pol_tmt"] == 6533.5
    assert r[-1]["all_pol_tmt"] == 6939.7
    assert r[-1]["ms_tmt"] == 1879.4
    assert r[-1]["hsd_tmt"] == 2419.3
    assert r[0]["hsd_tmt"] is None
    assert r[-1]["all_pol_tier"] == "secondary_transcription_unverified_at_primary"
    assert d["qa"]["all_pol_includes_subcategory_ms_hsd"] is True
    assert all(v is None for v in d["unsupported_current_results"].values())
    assert d["emc_data_request"]["not_obtained"] is True


@pytest.mark.parametrize(
    ("path", "value"),
    [
        (("qa", "primary_fy2024_25_pdf_image_verified"), True),
        (("qa", "no_annualisation_of_h1"), False),
        (("qa", "all_pol_includes_subcategory_ms_hsd"), False),
        (("annual_kerala_rows", 5, "all_pol_tmt"), 9999),
        (("annual_kerala_rows", 0, "hsd_tmt"), 10),
        (("unsupported_current_results", "fy2024_25_kerala_total_final_energy_mtoe"), 17),
        (("emc_data_request", "not_obtained"), False),
    ],
)
def test_no_source_promotion_or_reinterpretation(path, value):
    d = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    copy = deepcopy(d)
    current = copy
    for key in path[:-1]:
        current = current[key]
    current[path[-1]] = value
    with pytest.raises(ValueError):
        validate_ppac_sales(copy)


def test_public_source_report_and_browser_mounts():
    doc = (ROOT / "docs/PPAC_KERALA_FULL_YEAR_SALES_SOURCE_AUDIT_2026_09_24.md").read_text(
        encoding="utf-8"
    )
    html = (ROOT / "docs/index.html").read_text(encoding="utf-8")
    assert "6,939.7" in doc
    assert "6,533.5" in doc
    assert "secondary" in doc.lower()
    assert "EMC" in doc
    assert 'id="totalEnergyAnnualPPACChart"' in html
    assert 'id="totalEnergyPPACProductsChart"' in html
