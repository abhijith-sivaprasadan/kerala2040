"""QA for the March-2026 CEA/MNRE renewable boundary crosswalk."""
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def crosswalk():
    return json.loads(
        (ROOT / "data/evidence/assets/kerala_re_crosswalk_2026_03_31.json").read_text(
            encoding="utf-8"
        )
    )


def test_cea_renewable_ownership_boundary_reconciles(crosswalk):
    own = crosswalk["cea_main_boundary"]["ownership_mw"]
    assert own["state"] + own["private"] + own["central"] == pytest.approx(400.34)
    assert own["total"] == pytest.approx(400.34)


def test_wind_plus_derived_solar_reconciles_to_cea_boundary(crosswalk):
    wind = crosswalk["admitted_wind_crosswalk_mw"]
    solar = crosswalk["derived_solar_ge_1mw_mw"]
    assert wind["arithmetic_total"] == pytest.approx(71.525)
    assert solar["arithmetic_total_solar_ge_1mw"] == pytest.approx(328.815)
    assert wind["arithmetic_total"] + solar["arithmetic_total_solar_ge_1mw"] == pytest.approx(
        400.34
    )


def test_solar_ownership_residuals_are_transparent(crosswalk):
    solar = crosswalk["derived_solar_ge_1mw_mw"]
    assert solar["state"]["derived_solar_mw"] == pytest.approx(22.715)
    assert solar["private"]["derived_solar_mw"] == pytest.approx(214.10)
    assert solar["central"]["derived_solar_mw"] == pytest.approx(92.00)
    assert solar["central"]["identified_asset"] == "NTPC Kayamkulam Floating Solar"


def test_mnre_population_is_not_used_as_cea_threshold_crosswalk(crosswalk):
    mnre = crosswalk["mnre_same_date_crosscheck"]
    assert mnre["solar"]["total_mw"] == pytest.approx(2215.59)
    assert "not the same population" in mnre["source_boundary_warning"]
    assert crosswalk["model_admission"]["dispatch_ready"] is False
