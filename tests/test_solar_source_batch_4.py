"""Guard the fourth solar-source batch and day/total distinction."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
QA = ROOT / "data/evidence/solar/solar_batch_4_2026_09_21_avg_daily_geotiff_qa.json"
MANIFEST = ROOT / "data/evidence/solar/solar_batch_2026_09_21_originals_manifest.json"
PREVIOUS = ROOT / "data/evidence/solar/solar_batch_3_2026_09_21_source_qa.json"


def test_avg_daily_archives_sha_and_crc_pinned() -> None:
    qa = json.loads(QA.read_text(encoding="utf-8"))
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    by_name = {x["name"]: x for x in manifest["assets"]}
    assert len(by_name) == 17
    assert qa["zip_count"] == 3
    assert qa["tiff_count"] == 19
    assert len(qa["original_archives"]) == 3
    for archive in qa["original_archives"]:
        assert archive["zip_crc"] == "PASS_all_members"
        assert archive["bytes"] == by_name[archive["name"]]["bytes"]
        assert archive["sha256"] == by_name[archive["name"]]["sha256"]
        assert re.fullmatch(r"[0-9a-f]{64}", archive["sha256"])
        for tif in archive["tiffs"]:
            assert tif["bytes"] > 0
            assert re.fullmatch(r"[0-9a-f]{64}", tif["sha256"])


def test_monthly_avg_daily_is_not_prior_monthly_totals() -> None:
    qa = json.loads(QA.read_text(encoding="utf-8"))
    assert [x["name"] for x in qa["original_archives"][0]["tiffs"]] == [
        f"PVOUT_{month:02d}.tif" for month in range(1, 13)
    ]
    assert "without stating per-day denominator" in qa["publisher_XML_ambiguity"]
    assert qa["solar_reference_years"] == "1999-2018"
    assert qa["temperature_reference_years"] == "1994-2018"
    assert qa["raw_binary_in_git_or_release"] is False
    assert qa["model_ready"] is False


def test_opta_and_temp_byte_duplicate_previous_annual_tiffs() -> None:
    qa = json.loads(QA.read_text(encoding="utf-8"))
    previous = json.loads(PREVIOUS.read_text(encoding="utf-8"))
    current_by_name = {
        file["name"]: file
        for archive in qa["original_archives"]
        for file in archive["tiffs"]
    }
    prior_by_name = {
        file["name"]: file
        for archive in previous["archives"]
        for file in archive["data_files"]
    }
    assert qa["byte_duplicate_with_batch3"] == ["OPTA.tif", "TEMP.tif"]
    for name in qa["byte_duplicate_with_batch3"]:
        assert current_by_name[name]["sha256"] == prior_by_name[name]["sha256"]
        assert current_by_name[name]["bytes"] == prior_by_name[name]["bytes"]
        assert current_by_name[name]["duplicate_from_batch3"] is True


def test_gis_layout_no_implied_kerala_or_uniform_grid() -> None:
    qa = json.loads(QA.read_text(encoding="utf-8"))
    r = qa["rasters"]
    assert r["all_crs"] == "EPSG:4326"
    assert r["all_bounds_lonlat"] == [66, 6, 98, 38]
    assert r["monthly_pvout"]["count"] == 12
    assert r["yearly_gHI_DNI_DIF_GTI"]["resolution_arcsec"] == 9
    assert r["yearly_PVOUT"]["resolution_arcsec"] == 30
    assert r["optimum_tilt"]["resolution_arcsec"] == 120
    assert r["sanity_window_NOT_Kerala"] == [74, 8, 78, 13]
