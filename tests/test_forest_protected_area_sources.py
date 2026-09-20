"""Forest/protected-area source discovery must fail closed without source geometry."""

from __future__ import annotations

import importlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
m = importlib.import_module("audit_forest_protected_area_sources")


def test_file_kind_does_not_promote_pdf_map_to_vector():
    assert m._file_kind("https://forest.kerala.gov.in/a/map.pdf") == "document"
    assert m._file_kind("https://forest.kerala.gov.in/a/data.geojson") == "vector_candidate"
    assert m._file_kind("https://forest.kerala.gov.in/a/data.zip") == "vector_candidate"
    assert m._file_kind("https://forest.kerala.gov.in/a/page/") is None


def test_only_department_hosts_are_official_for_probe():
    assert m._same_official_host("https://forest.kerala.gov.in/a")
    assert m._same_official_host("https://www.forest.kerala.gov.in/a")
    assert not m._same_official_host("https://example.com/forest.geojson")


def test_protected_area_counts_parse_only_explicit_department_prose():
    text = (
        "Protected area network includes 6 National Parks, 18 wildlife sanctuaries, "
        "2 tiger reserves and 1 community reserve."
    )
    assert m._extract_pa_counts(text) == {
        "national_parks": 6,
        "wildlife_sanctuaries": 18,
        "tiger_reserves": 2,
        "community_reserves": 1,
    }


def test_missing_counts_stay_unknown():
    assert all(v is None for v in m._extract_pa_counts("Protected areas of Kerala").values())
