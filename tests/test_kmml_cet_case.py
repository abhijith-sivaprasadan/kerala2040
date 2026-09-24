"""KMML source-boundary test: no financial/energy recovery is manufactured from old slides."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "data/evidence/industry/kmml_source_bounded_case_2026_09_24.json"


def test_kmml_process_ledger_is_source_bounded():
    case = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    scope = case["scientific_scope"]
    assert case["selected_case"] == "KMML"
    assert case["classification"].endswith("NOT_RECOVERY_FORECAST")
    assert len(case["units"]) == 9
    assert len(case["streams"]) == 10
    ids = {unit["id"] for unit in case["units"]}
    assert ids == {"MS", "IBP", "ARP", "U200", "U300", "U400", "TSP", "ETP", "UTIL"}
    assert {row["id"] for row in case["streams"]} == {
        "iron_oxide", "arp_acid", "ibp_spent_liquor", "u200_impurity",
        "chlorine_cycle", "pigment_fines", "backwash_water", "etp_sludge",
        "heat", "sponge_mgcl2",
    }
    assert all(row["unit"] in ids for row in case["streams"])
    assert all(start in ids and end in ids for start, end, _ in case["links"])
    assert all(not unit["quantified"] for unit in case["units"])
    assert all(
        row["annual_tonnes"] is None
        and row["annual_mwh"] is None
        and row["avoided_co2_t"] is None
        for row in case["streams"]
    )
    assert scope["measured_mass_energy_water_balance_complete"] is False
    assert scope["measured_recovery_credits_available"] is False
    assert scope["kmml_case_release_gate_passed"] is False
    assert case["published_numeric_recovery_by_Kerala2040"] is None
    assert case["ready_for_numerical_2040_industry_scenario"] is False
    assert case["verified_regulatory_classification"] is None
    assert case["measured_fy2024_25_site_energy"] is None


def test_kmml_keep_historical_trial_streams_distinct():
    case = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    previous = case["dated_evidence"]["fy2022_23"]
    assert previous["iron_oxide_sponge_iron_trial_mt"] == 10
    assert previous["filter_backwash_m3_per_day_approx"] == 300
    assert previous["tio2_fines_overflow_g_per_l"] == [1, 2]
    assert "unit" in previous["iron_oxide_stock_phrase"]
    streams = {row["id"]: row for row in case["streams"]}
    assert streams["pigment_fines"]["unit"] == "U400"
    assert streams["backwash_water"]["unit"] == "UTIL"
    assert "FY2022_23" in streams["pigment_fines"]["status"]
    assert "FY2022_23" in streams["backwash_water"]["status"]
    assert streams["etp_sludge"]["unit"] != streams["iron_oxide"]["unit"]
    assert case["sources"]["annual_2022_23"]["url"].startswith(
        "https://www.kmml.com/"
    )


def test_kmml_public_chapter_and_industry_map_remain_present():
    chapter = (ROOT / "docs/KMML_CIRCULAR_INDUSTRY_CASE_2026_09_24.md").read_text(
        encoding="utf-8"
    )
    page = (ROOT / "docs/index.html").read_text(encoding="utf-8")
    assert "filter backwash" in chapter.lower()
    assert "not 10 MT/year" in chapter
    assert "do not multiply the two" in chapter
    assert "FY2024–25" in chapter
    assert 'id="kmmlFlow"' in page
    assert 'id="kmmlStreams"' in page
