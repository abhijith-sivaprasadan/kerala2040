import json
from pathlib import Path
import pandas as pd
import pytest
import yaml

from kerala2040.generators import generator_database


def test_generator_database_does_not_infer_owner():
    projects = {
        "tracker": {"data_as_of_label": "old"},
        "projects": [
            {
                "name": "Example HEP",
                "technology": "Hydro",
                "status": "Completed",
                "capacity_mw": 10.0,
                "district": "Idukki",
                "milestone_date_label": "12, Feb 2001",
            }
        ],
    }
    observed = {
        "electricity": {
            "installed_capacity_mw": 100.0,
            "capacity_mix_mw": {
                "hydel": 50.0,
                "thermal": 20.0,
                "solar": 25.0,
                "wind": 5.0,
            },
        }
    }
    frame, summary = generator_database(projects, observed)

    assert frame.loc[0, "commissioning_year"] == 2001
    assert frame.loc[0, "owner"] is None
    assert summary["official_total_installed_capacity_mw"] == 100.0

ROOT = Path(__file__).resolve().parents[1]


def _real_inputs():
    projects = json.loads((ROOT / "public/kseb-projects.json").read_text(encoding="utf-8"))
    observed = yaml.safe_load(
        (ROOT / "configs/observed_2024_25.yaml").read_text(encoding="utf-8")
    )
    crosscheck = yaml.safe_load(
        (ROOT / "configs/generator_reconciliation_2024_25.yaml").read_text(
            encoding="utf-8"
        )
    )
    return projects, observed, crosscheck


def test_fy2024_25_official_commissioning_crosscheck_preserves_portal():
    projects, observed, crosscheck = _real_inputs()
    frame, summary = generator_database(projects, observed, crosscheck)
    assert len(frame) == 70
    assert summary["uncaptured_portal_items"] == 17
    assert summary["official_fy2024_25_commissioned_plant_count"] == 2
    assert summary["official_fy2024_25_commissioned_additions_mw"] == 100
    assert summary["completed_portal_capacity_is_verified_fleet"] is False
    assert summary["full_station_register_verified"] is False
    assert summary["plant_level_fy_generation_verified"] is False
    for name, mw in (("Thottiyar HEP", 40), ("Pallivasal Extension Scheme", 60)):
        row = frame.loc[frame["plant"].eq(name)].iloc[0]
        assert row["status"] == "Ongoing"  # Unaltered stale portal claim.
        assert row["reconciled_commissioned_mw"] == mw
        assert row["owner"] == "KSEBL"
        assert row["commissioning_evidence_status"] == (
            "independently_crosschecked_fy2024_25"
        )
        assert pd.isna(row["commissioning_year"])


def test_name_kw_and_raw_mw_conflicts_are_never_silently_repaired():
    projects, observed, crosscheck = _real_inputs()
    frame, summary = generator_database(projects, observed, crosscheck)
    cases = (
        ("Poringalkuthu Left Bank Project - Micro Screw Generator 1x11kW", 11, .011),
        ("Agali -Chaliyur-96kW", .96, .096),
    )
    for name, portal_mw, name_mw in cases:
        row = frame.loc[frame["plant"].eq(name)].iloc[0]
        assert row["capacity_mw"] == portal_mw
        assert row["unit_label_capacity_mw"] == pytest.approx(name_mw)
        assert bool(row["unit_label_conflicts_with_portal_mw"])
        assert pd.isna(row["reconciled_commissioned_mw"])
    assert summary["name_unit_portal_mw_conflict_count"] >= 2
    zero = frame.loc[frame["plant"].str.startswith("Sabarigiri Augmentation")].iloc[0]
    assert zero["capacity_mw"] == 0
    assert pd.isna(zero["reconciled_commissioned_mw"])


def test_crosscheck_rejects_unit_sums_outside_fy_and_bad_total():
    projects, observed, crosscheck = _real_inputs()
    import copy
    wrong = copy.deepcopy(crosscheck)
    wrong["official_commissioned_during_fy"][0]["units"][0]["capacity_mw"] = 9
    with pytest.raises(ValueError, match="do not sum"):
        generator_database(projects, observed, wrong)
    wrong = copy.deepcopy(crosscheck)
    wrong["official_commissioned_during_fy"][0]["units"][0][
        "commissioning_date"
    ] = "2025-04-01"
    with pytest.raises(ValueError, match="outside FY"):
        generator_database(projects, observed, wrong)
    wrong = copy.deepcopy(crosscheck)
    wrong["official_totals"]["all_kerala_installed_mw"] = 5000
    with pytest.raises(ValueError, match="statewide capacity"):
        generator_database(projects, observed, wrong)


def test_crosscheck_does_not_turn_planned_future_project_into_a_commissioned_asset():
    projects, observed, crosscheck = _real_inputs()
    frame, _ = generator_database(projects, observed, crosscheck)
    row = frame.loc[frame["plant"].eq("Mankulam HEP Stage I")].iloc[0]
    assert pd.isna(row["commissioning_year"])
    assert pd.isna(row["reconciled_commissioned_mw"])
    assert row["owner"] is None
    assert row["status"] == "Ongoing"
