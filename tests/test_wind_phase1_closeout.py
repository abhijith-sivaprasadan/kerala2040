"""Wind phase 1: unit-scale reproducibility and no capacity laundering."""
from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/derive_district_wind_sensitivity.py"
SPEC = importlib.util.spec_from_file_location("derive_district_wind_sensitivity", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
SOURCE = ROOT / "data/evidence/gis/niwe_nwic_district_wind_terrain_2026_09_22.json"
RESULT = ROOT / "data/evidence/gis/niwe_nwic_district_normalized_wind_terrain_2026_09_23.json"


def source() -> dict:
    return json.loads(SOURCE.read_text(encoding="utf8"))


def test_public_normalized_closeout_is_exactly_reproducible():
    derived = MODULE.build(source())
    committed = json.loads(RESULT.read_text(encoding="utf8"))
    assert derived == committed
    assert derived["qa"]["all_16_threshold_cell_counts_reconciled"] is True
    assert len(derived["districts"]) == 14
    assert derived["statewide"]["source_point_centres"] == 200_692
    assert derived["statewide"]["finite_DSM_slope_point_centres"] == 199_853
    assert derived["statewide"]["missing_DSM_slope_point_centres"] == 839
    case = derived["spotlight_descriptive_example"]
    assert case["statewide_matching_point_centres"] == 8_637
    assert case["palakkad_matching_point_centres"] == 6_330
    assert case["idukki_matching_point_centres"] == 1_804
    assert case["palakkad_pct_of_district_valid_slope_centres"] == 27.4978
    assert case["idukki_pct_of_district_valid_slope_centres"] == 8.0795
    assert derived["eligible_area_km2"] is None
    assert derived["feasible_capacity_MW"] is None
    assert derived["model_admitted"] is False


def test_zero_reference_ratio_is_missing_not_zero():
    result = MODULE.build(source())
    alappuzha = next(d for d in result["districts"] if d["district"] == "Alappuzha")
    assert alappuzha["counts"][2] == [0, 0, 0, 0]
    assert alappuzha["retention_relative_to_max20_slope_same_min_speed"][2] == [
        None, None, None, None
    ]


@pytest.mark.parametrize("fault", ["count", "missing", "matrix", "mw", "source_rights"])
def test_fail_closed_if_aggregates_or_model_flags_change(fault):
    data = copy.deepcopy(source())
    if fault == "count":
        data["point_assignment"]["source_points"] -= 1
    elif fault == "missing":
        data["districts"][0]["slope_missing"] += 1
    elif fault == "matrix":
        data["districts"][0]["threshold_matrix"][2][1] += 1
    elif fault == "mw":
        data["feasible_capacity_MW"] = 100
    elif fault == "source_rights":
        data["source"]["source_reuse_rights_verified"] = True
    with pytest.raises(ValueError):
        MODULE.build(data)


def test_svg_poster_figures_do_not_embed_original_geometry_or_eligibility():
    for filename in [
        "wind-district-normalized-20260923.svg",
        "wind-terrain-sensitivity-20260923.svg",
    ]:
        figure = (ROOT / "docs/assets" / filename).read_text(encoding="utf8")
        assert figure.startswith("<svg")
        assert "<title" in figure and "<desc" in figure
        assert "NOT legal" in figure or "Not eligible" in figure or "Not legal" in figure
        assert "geometry" not in figure.lower()
        assert "200,692" not in figure or "NOT" in figure
