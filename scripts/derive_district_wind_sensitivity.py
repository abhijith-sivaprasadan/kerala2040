"""Derive source-labelled, district-normalized wind/DSM screening statistics.

Only committed, nonspatial district aggregates are read. Do not infer turbine
sites, km², installed MW, wind generation or legal eligibility from counts.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

CLASS = "NIWE_NWIC_DISTRICT_NORMALIZED_DESCRIPTIVE_WIND_TERRAIN_SENSITIVITY_NOT_SUITABILITY"


def pct(count: int, denominator: int) -> float | None:
    return round(100 * count / denominator, 4) if denominator else None


def build(source: dict) -> dict:
    a = source["point_assignment"]
    limits = source["hypothetical_thresholds"]
    totals = limits["all_districts_point_counts"]
    rows = source["districts"]
    if (len(rows) != 14 or len({r["district"] for r in rows}) != 14
            or a["source_points"] != a["uniquely_assigned"] != 200_692):
        raise ValueError("NWIC source population/partition incomplete")
    if a["unassigned"] or a["ambiguous"] or not a["complete_descriptive_partition"]:
        raise ValueError("Cannot normalize an incomplete NWIC district partition")
    if len(totals) != 4 or any(len(r) != 4 for r in totals):
        raise ValueError("Expected exactly 16 statewide threshold counts")
    if (sum(r["point_centres"] for r in rows) != a["source_points"]
            or sum(r["slope_finite"] for r in rows) != a["slope_finite"]
            or sum(r["slope_missing"] for r in rows) != a["slope_missing"]):
        raise ValueError("District slope or source point totals differ from statewide")
    if any(sum(r["threshold_matrix"][i][j] for r in rows) != totals[i][j]
           for i in range(4) for j in range(4)):
        raise ValueError("The 16 district threshold sums do not reconcile")
    if (source["eligible_area_km2"] is not None or
            source["feasible_capacity_MW"] is not None or
            source["model_admitted"] is not False or
            source["source"]["source_reuse_rights_verified"] is not False):
        raise ValueError("An unadmitted source was promoted to wind capacity")
    districts = []
    for row in rows:
        finite = row["slope_finite"]
        matrix = row["threshold_matrix"]
        if finite <= 0 or row["point_centres"] != finite + row["slope_missing"]:
            raise ValueError("Invalid district slope denominator")
        districts.append({
            "district": row["district"],
            "niwe_point_centres": row["point_centres"],
            "valid_slope_point_centres": finite,
            "missing_slope_point_centres": row["slope_missing"],
            "missing_slope_pct_of_all_centres": pct(row["slope_missing"], row["point_centres"]),
            "median_modelled_150m_speed_m_s": row["wind_speed_median_m_s"],
            "median_DSM_surface_slope_degrees": row["slope_median_degrees"],
            "counts": matrix,
            "percent_of_district_valid_slope_centres": [
                [pct(v, finite) for v in line] for line in matrix
            ],
            "percent_of_statewide_matching_centres": [
                [pct(v, totals[i][j]) for j, v in enumerate(line)]
                for i, line in enumerate(matrix)
            ],
            "retention_relative_to_max20_slope_same_min_speed": [
                [pct(v, line[3]) for v in line] for line in matrix
            ],
        })
    highlight = {row["district"]: row for row in districts}
    result = {
        "classification": CLASS,
        "reviewed_date": "2026-09-23",
        "input_evidence_path": "data/evidence/gis/niwe_nwic_district_wind_terrain_2026_09_22.json",
        "source": source["source"],
        "interpretation": {
            "thresholds": "Hypothetical NIWE 150 m modelled wind >= row minimum and GLO-90 DSM surface slope <= column maximum; not accepted siting criteria",
            "percent_of_district_valid_slope_centres": "count/finite sampled slope NIWE point centres in same NWIC district; denominator excludes missing slope samples",
            "percent_of_statewide_matching_centres": "district count/statewide threshold-matching centres; geographic share of a hypothetical point subset not capacity share",
            "retention_relative_to_max20_slope_same_min_speed": "count at selected slope maximum / count at <=20 degrees for the same wind minimum, only if the <=20 reference count is nonzero; NOT fraction of all windy points; null for empty reference",
            "valid_slope_selection_not_random": "Missing slopes are reported and excluded, not inferred",
            "scope": "No district ranking, eligible area, legal exclusions, physical sites, layout, turbine yield, grid capacity or MW.",
        },
        "thresholds": {
            "minimum_modelled_wind_speed_150m_m_s_inclusive": limits["min_modelled_150m_wind_speed_m_s_inclusive"],
            "maximum_DSM_surface_slope_degrees_inclusive": limits["max_DSM_surface_slope_degrees_inclusive"],
        },
        "statewide": {
            "source_point_centres": a["source_points"],
            "finite_DSM_slope_point_centres": a["slope_finite"],
            "missing_DSM_slope_point_centres": a["slope_missing"],
            "threshold_count_matrix": totals,
            "threshold_pct_of_valid_slope_centres": [
                [pct(v, a["slope_finite"]) for v in line] for line in totals
            ],
        },
        "districts": districts,
        "spotlight_descriptive_example": {
            "wind_min_m_s": 7, "max_DSM_slope_degrees": 10,
            "statewide_matching_point_centres": totals[2][1],
            "statewide_pct_of_valid_slope_centres": pct(totals[2][1], a["slope_finite"]),
            "palakkad_matching_point_centres": highlight["Palakkad"]["counts"][2][1],
            "palakkad_pct_of_district_valid_slope_centres":
                highlight["Palakkad"]["percent_of_district_valid_slope_centres"][2][1],
            "idukki_matching_point_centres": highlight["Idukki"]["counts"][2][1],
            "idukki_pct_of_district_valid_slope_centres":
                highlight["Idukki"]["percent_of_district_valid_slope_centres"][2][1],
        },
        "qa": {
            "district_count": len(districts),
            "source_point_centres_reconciled": True,
            "valid_slope_reconciled": True,
            "missing_slope_reconciled": True,
            "all_16_threshold_cell_counts_reconciled": True,
            "district_boundaries_NWIC_not_LRIS": True,
        },
        "source_reuse_rights_verified": False,
        "eligible_area_km2": None,
        "feasible_capacity_MW": None,
        "hourly_generation_validated": False,
        "model_admitted": False,
    }
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=Path(
        "data/evidence/gis/niwe_nwic_district_wind_terrain_2026_09_22.json"))
    parser.add_argument("--output", type=Path, default=Path(
        "data/evidence/gis/niwe_nwic_district_normalized_wind_terrain_2026_09_23.json"))
    args = parser.parse_args()
    result = build(json.loads(args.input.read_text(encoding="utf8")))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf8")
    print(json.dumps(result["spotlight_descriptive_example"], indent=2))


if __name__ == "__main__":
    main()
