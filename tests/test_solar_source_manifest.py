"""Guard the exact original-source solar batch manifest against accidental drift."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data/evidence/solar/solar_batch_2026_09_21_originals_manifest.json"


def test_solar_source_batch_manifest_is_complete_and_unambiguously_pinned() -> None:
    d = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert d["schema_version"] == 1
    assert d["release_tag"] == "solar-source-2026-09-21"
    assert d["release_uploaded"] is False  # Update only on verified remote upload.
    assets = d["assets"]
    assert len(assets) == 17
    assert len({item["name"] for item in assets}) == len(assets)
    for asset in assets:
        assert Path(asset["name"]).name == asset["name"]
        assert asset["bytes"] > 0
        assert re.fullmatch(r"[0-9a-f]{64}", asset["sha256"])
    assert any(a["name"].endswith("derived 1(1).zip") for a in assets)
    assert any(a["name"].endswith("derived 2(1).zip") for a in assets)
    for name in (
        "global-PV-RASTER-DATA-LAYERS--GlobalSol masks(1).zip",
        "monthlyIndia_GISdata_LTAy_YearlyMonthlyTotals_GlobalSolarAtla(1).zip",
        "New folder(1).zip",
        "New folder (2)(1).zip",
    ):
        assert name in {asset["name"] for asset in assets}
    for name in (
        "monthlyIndia_GISdata_LTAy_AvgDailyTotals_GlobalSolarAtlas-v2_GEOTIFF(1).zip",
        "India_GISdata_LTAy_AvgDailyTotals_GlobalSolarAtlas-v2_GEOTIFF2(1).zip",
        "India_GISdata_LTAy_AvgDailyTotals_GlobalSolarAtlas-v2_GEOTIFF.zip",
    ):
        assert name in {asset["name"] for asset in assets}
    assert d["latest_batch_qa"] == (
        "data/evidence/solar/solar_batch_4_2026_09_21_avg_daily_geotiff_qa.json"
    )
    members = d["solar_zip_members"]
    assert len(members) == 18
    assert len({m[0] for m in members}) == len(members)
    for name, size, checksum, attribution in members:
        assert name and size > 0 and attribution
        assert re.fullmatch(r"[0-9a-f]{64}", checksum)


def test_station_observation_counts_are_not_interpreted_as_statewide() -> None:
    d = json.loads(MANIFEST.read_text(encoding="utf-8"))
    qa = d["telemetry_FY2024_25_preview"]
    solar = qa["solar"]
    wind = qa["wind"]
    assert solar["fy_rows"] == sum(solar["fy_stations"].values()) == 6007
    assert wind["fy_rows"] == sum(wind["fy_stations"].values()) == 10946
    assert solar["unit"] == "W/m2"
    assert wind["unit"] == "km/h"
    assert solar["fy_rows"] < solar["total_rows"]
    assert wind["fy_rows"] < wind["total_rows"]
