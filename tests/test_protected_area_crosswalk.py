"""Protected-area crosswalk cannot certify statutory forest boundaries."""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from crosswalk_kerala_protected_areas import norm  # noqa: E402


def test_official_register_has_25_core_designations_and_no_capacity_claim():
    data = yaml.safe_load(
        (ROOT / "configs/kerala_protected_area_crosswalk_2026.yaml").read_text()
    )
    assert len(data["protected_areas"]) == 25
    assert {x["type"] for x in data["protected_areas"]} == {
        "National Park", "Wildlife Sanctuary", "Community Reserve"
    }
    assert len(data["overlapping_designations"]) == 2
    assert data["model_use"]["protected_area_secondary_geometry_ready"] is False
    assert data["model_use"]["statutory_boundary_verified"] is False
    assert data["model_use"]["reserve_forest_boundary_verified"] is False
    assert data["model_use"]["protected_area_union_sq_km"] is None
    assert data["model_use"]["ecological_capacity_ceiling_ready"] is False


def test_name_normalization_handles_punctuation_only():
    assert norm("Peechi - Vazhani") == norm("Peechi-Vazhani")
    assert norm("Kadalundi - Vallikunnu") == norm("Kadalundi Vallikunnu")
