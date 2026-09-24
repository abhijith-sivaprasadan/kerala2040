"""Kerala 2023 official energy emissions belong to a distinct time and scope."""
import json
from copy import deepcopy
from pathlib import Path

import pytest

from kerala2040.energy_ghg_bridge import (
    load_energy_ghg_bridge,
    validate_energy_ghg_bridge,
)

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "data/evidence/total_energy/kerala_ghg_sector_bridge_2026_09_24.json"


def test_official_2023_ghg_is_a_distinct_inventory_not_fy2024_25_tfec():
    d = load_energy_ghg_bridge()
    assert validate_energy_ghg_bridge(d)["categories"] == 3
    assert d["period"] == "calendar_2023"
    assert d["unit"] == "MtCO2e"
    assert d["energy_sector_2023_mtco2e"] == 20.64
    assert [(s["id"], s["mtco2e"]) for s in d["categories"]] == [
        ("transport", 13.59), ("residential", 3.2), ("industrial", 1.89)
    ]
    assert d["historic_source_vintage_conflict"]["old_report_energy_mtco2e"] == 16.96
    assert d["historic_source_vintage_conflict"]["current_portal_energy_mtco2e"] == 17.09
    assert d["no_assumed_energy_2024_25_mtoe"] is None
    assert d["no_assumed_2024_25_sectoral_emissions_mtco2e"] is None
    assert d["no_externally_verified_2023_fuel_by_sector_matrix"] is None
    assert d["no_raw_seeap_workbook"] is True
    assert all(
        row["allowed_join"] is False
        for row in d["crosswalk"] if row["measure"] != "Official Kerala energy GHG"
    )


@pytest.mark.parametrize(
    ("key", "value"),
    [
        ("period", "FY2024-25"),
        ("energy_sector_2023_mtco2e", 28),
        ("categories", []),
        ("no_assumed_energy_2024_25_mtoe", 20.64),
        ("no_assumed_2024_25_sectoral_emissions_mtco2e", 20.64),
        ("no_co2_per_tonne_pol_ratio", 5.5),
        ("no_raw_seeap_workbook", False),
    ],
)
def test_source_bridge_rejects_invalid_sector_and_current_total(key, value):
    d = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    bad = deepcopy(d)
    bad[key] = value
    with pytest.raises(ValueError):
        validate_energy_ghg_bridge(bad)


def test_original_heating_reference_cannot_be_called_net_calorific_value():
    d = load_energy_ghg_bridge()
    d["historical_seeap_gcv"]["basis"] = "NET CALORIFIC VALUE"
    with pytest.raises(ValueError, match="Gross and net"):
        validate_energy_ghg_bridge(d)


def test_ghg_chapter_and_independently_dated_chart_present():
    chapter = (
        ROOT / "docs/KERALA_TOTAL_ENERGY_ATLAS_SECTOR_GHG_METHODS_2026_09_24.md"
    ).read_text(encoding="utf-8")
    html = (ROOT / "docs/index.html").read_text(encoding="utf-8")
    assert "20.64 MtCO₂e" in chapter
    assert "16.96" in chapter and "17.09" in chapter
    assert "gross calorific values" in chapter.lower()
    assert 'id="totalEnergyGHGChart"' in html
    assert 'id="totalEnergyGHGStatus"' in html
