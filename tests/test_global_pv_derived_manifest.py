"""Invariants for the user-supplied 2020 global PV-derived original layers."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
QA = ROOT / "data/evidence/solar/global_pv_derived_source_qa_2026_09_21.json"
BATCH = ROOT / "data/evidence/solar/solar_batch_2026_09_21_originals_manifest.json"


def test_global_pv_derived_archives_are_cross_pinned() -> None:
    qa = json.loads(QA.read_text(encoding="utf-8"))
    batch = json.loads(BATCH.read_text(encoding="utf-8"))
    assets = {x["name"]: x for x in batch["assets"]}
    assert len(qa["archives"]) == 2
    assert qa["storage"]["raw_bytes_in_github"] is False
    assert batch["release_uploaded"] is False
    assert qa["storage"]["release_tag"] == batch["release_tag"]
    assert qa["source_vintage"].startswith("2020 ")
    for archive in qa["archives"]:
        assert archive["zip_crc"] == "PASS_all_members"
        assert archive["file_count"] == len(archive["members"])
        assert archive["name"] in assets
        assert archive["sha256"] == assets[archive["name"]]["sha256"]
        assert archive["bytes"] == assets[archive["name"]]["bytes"]
        for member in archive["members"]:
            assert member["bytes"] > 0
            assert re.fullmatch(r"[0-9a-f]{64}", member["sha256"])


def test_study_rasters_do_not_claim_kerala_or_model_readiness() -> None:
    qa = json.loads(QA.read_text(encoding="utf-8"))
    rasters = qa["raster_qa"]
    assert rasters["all_files_epsg"] == 4326
    assert rasters["all_files_shape"] == [13800, 43200]
    assert rasters["all_files_bounds_lonlat"] == [-180, -55, 180, 60]
    window = rasters["south_india_sanity_window"]
    assert window["bounds_lonlat"] == [74, 8, 78, 13]
    assert window["pixel_count_per_layer"] == 288000
    assert "NOT" in window["WARNING"]
    assert len(window["layers"]) == 4
    for layer in window["layers"]:
        assert 0 < layer["finite"] < window["pixel_count_per_layer"]
        assert layer["min"] <= layer["median"] <= layer["max"]
    assert "not" in qa["interpretation"]["model_use"].lower() or "pending" in qa["interpretation"]["model_use"].lower()
