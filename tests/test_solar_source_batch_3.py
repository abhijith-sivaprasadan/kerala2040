"""Protect the third solar source batch and avoid advancing model gates on raw files."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
QA = ROOT / "data/evidence/solar/solar_batch_3_2026_09_21_source_qa.json"
MANIFEST = ROOT / "data/evidence/solar/solar_batch_2026_09_21_originals_manifest.json"


def test_third_batch_sha_and_member_structure() -> None:
    qa = json.loads(QA.read_text(encoding="utf-8"))
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    originals = {x["name"]: x for x in manifest["assets"]}
    assert len(originals) == 14
    assert len(qa["archives"]) == 4
    assert sum(len(a["data_files"]) for a in qa["archives"]) == 29
    for archive in qa["archives"]:
        assert archive["zip_crc"] == "PASS_all_members"
        assert archive["non_directory_members"] >= len(archive["data_files"])
        asset = originals[archive["name"]]
        assert archive["bytes"] == asset["bytes"]
        assert archive["sha256"] == asset["sha256"]
        assert re.fullmatch(r"[0-9a-f]{64}", archive["sha256"])
        for file in archive["data_files"]:
            assert file["bytes"] > 0
            assert re.fullmatch(r"[0-9a-f]{64}", file["sha256"])


def test_monthly_pvout_twelve_and_split_annual_seven() -> None:
    qa = json.loads(QA.read_text(encoding="utf-8"))
    monthly = qa["archives"][1]["data_files"]
    annual = qa["archives"][2]["data_files"] + qa["archives"][3]["data_files"]
    assert [x["name"] for x in monthly] == [
        f"PVOUT_{month:02d}.tif" for month in range(1, 13)
    ]
    assert {x["name"] for x in annual} == {
        "DIF.tif", "GHI.tif", "OPTA.tif", "TEMP.tif",
        "DNI.tif", "GTI.tif", "PVOUT.tif",
    }
    assert qa["raster_properties"]["india_monthly_pvout"]["source_units"].startswith(
        "kWh/kWp per calendar month"
    )
    assert qa["sources"]["india_gsa_tiff"]["temp_reference_years"] == "1994-2018"
    assert qa["interpretation"]["model_readiness"] is False
    assert qa["interpretation"]["reproducible_remote_binary_storage"] is False


def test_mask_original_readme_and_screening_status() -> None:
    qa = json.loads(QA.read_text(encoding="utf-8"))
    masks = qa["archives"][0]
    assert len(masks["data_files"]) == 10
    assert masks["readme"]["bytes"] == 1697
    original_readme = (
        ROOT / "references/source_originals/global_pv_potential_by_country_2020_MASKS_README.txt"
    )
    assert hashlib.sha256(original_readme.read_bytes()).hexdigest() == masks["readme"][
        "sha256"
    ]
    assert qa["raster_properties"]["mask_composites"]["shape"] == [15000, 43200]
    assert qa["raster_properties"]["mask_components"]["shape"] == [21600, 43200]
